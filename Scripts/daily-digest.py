#!/usr/bin/env python3
"""
Daily digest — runs when today's journal is created.
Fetches top Reddit/HN articles, summarizes them, creates fleeting notes,
finds vault connections, and appends a digest section to today's journal.
"""

import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from datetime import date, datetime
from pathlib import Path

VAULT        = "/Users/lyndsey/Library/Mobile Documents/iCloud~md~obsidian/Documents/Lyndsey"
JOURNAL_DIR  = f"{VAULT}/📓Journal"
NOTES_DIR    = f"{VAULT}/📌 Permanent Notes"
REF_DIR      = f"{VAULT}/📖 Reference Notes"
CLAUDE       = "/opt/homebrew/bin/claude"
MODEL        = "claude-sonnet-4-6"
LOCK_FILE    = Path.home() / ".claude/scripts/.daily-digest.lock"

# Subreddits selected from vault topic analysis
SUBREDDITS = [
    # DevOps / cloud / infrastructure
    "devops", "kubernetes", "aws", "terraform", "golang",
    # Software engineering / architecture
    "programming", "systemdesign",
    # AI / ML
    "MachineLearning", "LocalLLaMA",
    # Personal development
    "getdisciplined", "Stoicism", "ObsidianMD",
    # Health
    "fitness", "sleep",
    # Creative / hobbies
    "worldbuilding", "rpg",
]

REDDIT_PER_SUB  = 3    # top posts to fetch per subreddit
REDDIT_MIN_SCORE = 50  # ignore posts below this score
HN_FETCH        = 20   # top HN stories to consider
MAX_SELECTED    = 8    # articles to summarize and include

USER_PROFILE = """
Senior software engineer / technical lead. Interests:
- DevOps, CI/CD, Kubernetes, AWS, infrastructure as code, Go, Python
- Distributed systems, system design, microservices
- AI/ML, LLMs, AI governance and ethics
- Personal development: Stoicism, atomic habits, systems thinking
- Health: strength training, HRV, sleep optimization, breathing
- Fantasy fiction, world-building, tabletop RPG design
- Obsidian/Zettelkasten knowledge management
- Leadership, career growth, communication
"""


# ── Utilities ──────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def call_claude(prompt: str, timeout: int = 120) -> str:
    try:
        result = subprocess.run(
            [CLAUDE, "-p", prompt, "--model", MODEL],
            capture_output=True, text=True, timeout=timeout,
        )
        return result.stdout.strip()
    except Exception as e:
        log(f"Claude error: {e}")
        return ""


def fetch_json(url: str) -> dict | list | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "LyndseyDailyDigest/1.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            return json.loads(resp.read())
    except Exception as e:
        log(f"  fetch failed ({url[:60]}): {e}")
        return None


# ── Article fetching ────────────────────────────────────────────────────────

def fetch_reddit() -> list[dict]:
    posts = []
    for sub in SUBREDDITS:
        data = fetch_json(
            f"https://www.reddit.com/r/{sub}/top.json?t=day&limit={REDDIT_PER_SUB}"
        )
        if not data:
            continue
        time.sleep(0.6)  # polite rate limit
        for child in data.get("data", {}).get("children", []):
            p = child["data"]
            if p.get("score", 0) < REDDIT_MIN_SCORE:
                continue
            posts.append({
                "source": f"r/{sub}",
                "title": p.get("title", ""),
                "url":   p.get("url") or f"https://reddit.com{p.get('permalink','')}",
                "score": p.get("score", 0),
                "blurb": p.get("selftext", "")[:300].strip(),
            })
    return posts


def fetch_hn() -> list[dict]:
    ids = fetch_json("https://hacker-news.firebaseio.com/v0/topstories.json")
    if not ids:
        return []
    stories = []
    for sid in ids[:HN_FETCH]:
        item = fetch_json(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json")
        if item and item.get("type") == "story" and item.get("url"):
            stories.append({
                "source": "HN",
                "title":  item.get("title", ""),
                "url":    item.get("url", ""),
                "score":  item.get("score", 0),
                "blurb":  "",
            })
        time.sleep(0.1)
    return stories


# ── Claude processing ───────────────────────────────────────────────────────

def select_and_summarize(articles: list[dict]) -> list[dict]:
    url_map = {a["title"]: a["url"] for a in articles}

    listing = "\n".join(
        f"{i+1}. [{a['source']}] {a['title']} (score {a['score']})"
        + (f"\n   {a['blurb']}" if a["blurb"] else "")
        for i, a in enumerate(articles)
    )
    prompt = f"""You are preparing a daily digest for a user with this profile:
{USER_PROFILE}

Here are today's articles from Reddit and Hacker News:
{listing}

Select the {MAX_SELECTED} most relevant and interesting ones for this user.
For each, write a 2-sentence summary and 3 concise bullet takeaways.
Use the exact title string from the list above — do not paraphrase it.

Format your response using this exact structure, one block per article:

===ARTICLE===
TITLE: <exact title from the list>
SOURCE: <source>
SUMMARY: <two sentences>
- <takeaway 1>
- <takeaway 2>
- <takeaway 3>

Repeat the ===ARTICLE=== block for each selected article. No other text."""

    raw = call_claude(prompt, timeout=120)
    selected = []
    for block in raw.split("===ARTICLE==="):
        block = block.strip()
        if not block:
            continue
        title_m   = re.search(r"^TITLE:\s*(.+)$",   block, re.MULTILINE)
        source_m  = re.search(r"^SOURCE:\s*(.+)$",  block, re.MULTILINE)
        summary_m = re.search(r"^SUMMARY:\s*(.+)$", block, re.MULTILINE)
        takeaways = re.findall(r"^-\s*(.+)$",        block, re.MULTILINE)
        if not title_m:
            continue
        title = title_m.group(1).strip()
        # Restore URL from original fetch data
        url = url_map.get(title, "")
        if not url:
            for orig_title, orig_url in url_map.items():
                if title[:50] in orig_title or orig_title[:50] in title:
                    url = orig_url
                    break
        selected.append({
            "title":     title,
            "source":    source_m.group(1).strip()  if source_m  else "",
            "url":       url,
            "summary":   summary_m.group(1).strip() if summary_m else "",
            "takeaways": takeaways[:3],
        })
    return selected


def find_connections(articles: list[dict], note_titles: list[str]) -> list[dict]:
    if not articles or not note_titles:
        return []

    themes = "\n".join(f"- {a['title']}: {a['summary']}" for a in articles)
    titles = "\n".join(f"- {t}" for t in note_titles[:120])

    prompt = f"""You are finding connections between today's article themes and an Obsidian vault.

Today's themes:
{themes}

Vault note titles:
{titles}

Identify 3–5 vault notes that genuinely connect to today's themes.
For each, give a one-sentence reason.

Format your response as one connection per line, exactly like this:
NOTE: <exact note title> | REASON: <one sentence>

No other text."""

    raw = call_claude(prompt, timeout=60)
    connections = []
    for line in raw.splitlines():
        m = re.match(r"NOTE:\s*(.+?)\s*\|\s*REASON:\s*(.+)", line.strip())
        if m:
            connections.append({"note": m.group(1).strip(), "reason": m.group(2).strip()})
    return connections


# ── Vault & journal I/O ─────────────────────────────────────────────────────

def get_note_titles() -> list[str]:
    titles = []
    for folder in [NOTES_DIR, REF_DIR]:
        if not os.path.isdir(folder):
            continue
        for fname in os.listdir(folder):
            if fname.endswith(".md") and not fname.startswith("."):
                titles.append(fname[:-3])
    return sorted(titles)



def already_processed(journal_file: str) -> bool:
    if not os.path.exists(journal_file):
        return False
    with open(journal_file, "r") as f:
        return "## Daily Digest" in f.read()


def append_digest(journal_file: str, articles: list[dict], connections: list[dict]) -> None:
    today_str = date.today().strftime("%B %-d, %Y")

    article_blocks = []
    for a in articles:
        bullets = "\n".join(f"  - {t}" for t in a.get("takeaways", []))
        article_blocks.append(
            f"**[{a['title']}]({a['url']})** *({a['source']})*\n{a['summary']}\n{bullets}"
        )

    conn_lines = "\n".join(
        f"- **[[{c['note']}]]** — {c['reason']}" for c in connections
    ) or "- None identified today"

    digest = f"## Daily Digest — {today_str}\n\n### 🔗 Articles\n\n"
    digest += "\n\n---\n\n".join(article_blocks)
    digest += f"\n\n### 🕸️ Vault Connections\n\n{conn_lines}\n\n---\n\n"

    with open(journal_file, "r") as f:
        content = f.read()

    # Strip the startup placeholder wherever it landed, then prepend digest
    placeholder = f"\n## Daily Digest — {today_str}\n\n*(fetching…)*\n"
    content = content.replace(placeholder, "", 1)

    with open(journal_file, "w") as f:
        f.write(digest + content)


# ── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    today = date.today().strftime("%Y-%m-%d")
    journal_file = os.path.join(JOURNAL_DIR, f"{today}.md")

    if not os.path.exists(journal_file):
        log(f"No journal for {today}, nothing to do.")
        sys.exit(0)

    if already_processed(journal_file):
        log("Digest already present in today's journal.")
        sys.exit(0)

    # Debounce: skip if another instance ran within the last 5 minutes
    if LOCK_FILE.exists() and (time.time() - LOCK_FILE.stat().st_mtime) < 300:
        log("Recent lock file found, skipping.")
        sys.exit(0)

    LOCK_FILE.touch()

    # Claim the digest slot immediately so any concurrent run sees it and exits
    with open(journal_file, "a") as f:
        f.write(f"\n## Daily Digest — {date.today().strftime('%B %-d, %Y')}\n\n*(fetching…)*\n")

    try:
        log("Fetching Reddit posts...")
        reddit = fetch_reddit()
        log(f"  {len(reddit)} qualifying posts")

        log("Fetching HN stories...")
        hn = fetch_hn()
        log(f"  {len(hn)} stories")

        all_articles = reddit + hn
        if not all_articles:
            log("No articles fetched.")
            sys.exit(0)

        log(f"Selecting and summarizing top {MAX_SELECTED}...")
        selected = select_and_summarize(all_articles)
        log(f"  {len(selected)} articles selected")

        log("Finding vault connections...")
        note_titles = get_note_titles()
        connections = find_connections(selected, note_titles)
        log(f"  {len(connections)} connections found")

        log("Appending digest to journal...")
        append_digest(journal_file, selected, connections)
        log("Done.")

    finally:
        LOCK_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
