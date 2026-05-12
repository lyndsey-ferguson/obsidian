#!/usr/bin/env python3
"""Monthly review — conversational reflection assistant for Lyndsey."""

import subprocess
import sys
import os
import re
import calendar
from datetime import date, timedelta

JOURNAL_DIR = "/Users/lyndsey/Library/Mobile Documents/iCloud~md~obsidian/Documents/Lyndsey/📓Journal"
CLAUDE = "/opt/homebrew/bin/claude"
MODEL = "claude-sonnet-4-6"

QUESTIONS = [
    {
        "label": "improved",
        "marker": "What has improved?",
        "ask": "What has improved this month?",
        "has_why": True,
        "context": (
            "Look for genuine progress in health, relationships, work habits, emotional regulation, "
            "or personal growth. Even small gains count — they often signal a turning point."
        ),
    },
    {
        "label": "drains",
        "marker": "What still drains me?",
        "ask": "What still drains you?",
        "has_why": True,
        "context": (
            "Recurring energy drains: certain tasks, relationships, environments, or mental habits. "
            "If something has drained you for multiple months, that pattern is worth naming."
        ),
    },
    {
        "label": "more_of",
        "marker": "What do I want more of?",
        "ask": "What do you want more of in your life right now?",
        "has_why": True,
        "context": (
            "Not just activities — states of being. More calm, depth in conversation, "
            "creative work, physical vitality, presence with Ana."
        ),
    },
    {
        "label": "last_month_goals",
        "marker": "Goals from last month",
        "ask": "Which goals from last month did you accomplish — and which didn't happen?",
        "has_why": True,
        "context": (
            "Celebrate what was accomplished. For goals not reached, probe honestly: "
            "avoidance, circumstance, or were the goals wrong to begin with?"
        ),
    },
    {
        "label": "next_month_goals",
        "marker": "Goals for next month",
        "ask": "What are your goals for next month?",
        "has_why": False,
        "context": (
            "Goals should connect to the quarter's priorities. "
            "Are they specific enough to act on? Do you have atomic habits or milestones to support them?"
        ),
    },
]


def call_claude(prompt: str) -> str:
    try:
        result = subprocess.run(
            [CLAUDE, "-p", prompt, "--model", MODEL],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, Exception):
        return "DONE"


def read_answer() -> str:
    lines = []
    while True:
        prefix = "  " if lines else "> "
        line = input(prefix)
        if not line.strip():
            break
        lines.append(line.strip())
    return "\n".join(lines)


def extract_day_summary(content: str) -> str:
    parts = []
    highlights_match = re.search(r"## Highlights\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
    if highlights_match:
        raw = highlights_match.group(1)
        raw = re.sub(r"```.*?```", "", raw, flags=re.DOTALL)
        raw = re.sub(r"!\[\[.*?\]\]", "", raw)
        raw = re.sub(r"<%.*?%>", "", raw)
        lines = [l.strip().lstrip("* ").strip() for l in raw.splitlines()]
        lines = [l for l in lines if l and not l.startswith("|")]
        if lines:
            parts.append("; ".join(lines[:2]))
    review_match = re.search(r"## Review what happened.*", content, re.DOTALL)
    if review_match:
        answers = re.findall(r"^  - (.+)$", review_match.group(0), re.MULTILINE)
        if answers:
            parts.append("Notes: " + "; ".join(answers[:2]))
    return " | ".join(parts)


def get_month_context(year: int, month: int) -> str:
    entries = []
    today = date.today()
    num_days = calendar.monthrange(year, month)[1]
    for day in range(1, num_days + 1):
        d = date(year, month, day)
        if d > today:
            break
        filepath = os.path.join(JOURNAL_DIR, f"{d.strftime('%Y-%m-%d')}.md")
        if not os.path.exists(filepath):
            continue
        with open(filepath, "r") as f:
            content = f.read()
        summary = extract_day_summary(content)
        if summary:
            entries.append(f"{d.strftime('%b %-d')}: {summary}")
    return "\n".join(entries)


def get_monthly_file(year: int, month: int) -> str:
    return os.path.join(JOURNAL_DIR, f"{year}-M{month:02d}.md")


def create_monthly_note(filepath: str, year: int, month: int) -> None:
    month_name = date(year, month, 1).strftime("%B %Y")
    content = f"""# Monthly Review — {month_name}

## Reflections

### What has improved?

### What still drains me?

### What do I want more of?

## Goals

### Goals from last month

### Goals for next month

"""
    with open(filepath, "w") as f:
        f.write(content)


def get_unanswered_questions(filepath: str) -> list[dict]:
    if not os.path.exists(filepath):
        return QUESTIONS
    with open(filepath, "r") as f:
        content = f.read()
    return [q for q in QUESTIONS if f"### {q['marker']}\n\n" in content]


def write_answers(filepath: str, answers: dict) -> None:
    with open(filepath, "r") as f:
        content = f.read()
    for q in QUESTIONS:
        answer = answers.get(q["label"])
        if not answer:
            continue
        lines = [l for l in answer.split("\n") if l.strip()]
        sub_bullets = "\n".join(f"- {l}" for l in lines)
        marker = f"### {q['marker']}\n\n"
        if marker in content:
            content = content.replace(marker, f"### {q['marker']}\n{sub_bullets}\n\n", 1)
    with open(filepath, "w") as f:
        f.write(content)


def ask_with_followup(question_data: dict, month_context: str) -> str | None:
    print(f"\n{question_data['ask']}")
    answer = read_answer()
    if not answer:
        return None

    for _ in range(2):
        context_answer = answer.replace("\n", ". ")
        if question_data["has_why"]:
            followup_prompt = (
                f"You are a thoughtful monthly review companion for Lyndsey.\n"
                f"Background: {question_data['context']}\n"
                f"This month's context: {month_context or 'none available'}\n"
                f"Question: {question_data['ask']}\n"
                f"Lyndsey's answer so far: \"{context_answer}\"\n\n"
                f"Push back if the answer doesn't explain WHY — the emotion, root cause, or motivation. "
                f"Ask ONE short follow-up question (under 12 words) that probes deeper. "
                f"You may hint at a possible angle to spark reflection. "
                f"If the answer is already sufficiently reflective, respond with exactly: DONE"
            )
        else:
            followup_prompt = (
                f"You are a brief monthly review companion for Lyndsey.\n"
                f"Background: {question_data['context']}\n"
                f"Question: {question_data['ask']}\n"
                f"Lyndsey answered: \"{context_answer}\"\n\n"
                f"If the answer is vague or under 6 words, ask ONE short follow-up (under 12 words). "
                f"If sufficient, respond with exactly: DONE"
            )
        followup = call_claude(followup_prompt)
        if not followup or followup.upper() == "DONE" or "?" not in followup:
            break
        print(f"\n{followup}")
        extra = read_answer()
        if not extra:
            break
        answer = f"{answer}\n{extra}"

    return answer


def main() -> None:
    today = date.today()
    year, month = today.year, today.month
    monthly_file = get_monthly_file(year, month)

    if not os.path.exists(monthly_file):
        create_monthly_note(monthly_file, year, month)

    unanswered = get_unanswered_questions(monthly_file)
    if not unanswered:
        print(f"Monthly review for {today.strftime('%B %Y')} is already complete.")
        input("Press Enter to close.")
        sys.exit(0)

    already_answered = len(QUESTIONS) - len(unanswered)
    month_context = get_month_context(year, month)

    print(f"\nMonthly Review — {today.strftime('%B %Y')}")
    print("─" * 40)
    if already_answered:
        print(f"Resuming — {already_answered} of {len(QUESTIONS)} questions already answered.")
    if month_context:
        lines = month_context.split("\n")
        print(f"\nThis month ({len(lines)} journal entries):")
        for l in lines[:3]:
            print(f"  {l[:120]}")
        if len(lines) > 3:
            print(f"  ... ({len(lines) - 3} more days)")
    print("\nPress Enter to skip any question. Type multiple lines — blank line to finish.\n")

    answers = {}
    for q in unanswered:
        answer = ask_with_followup(q, month_context)
        if answer:
            answers[q["label"]] = answer

    if answers:
        print("\nWriting to monthly note...")
        write_answers(monthly_file, answers)
        print(f"\nDone — {len(answers)} of {len(unanswered)} questions answered. ✓")
        print(f"Note: {os.path.basename(monthly_file)}")
    else:
        print("\nNo answers recorded.")

    input("\nPress Enter to close.")


if __name__ == "__main__":
    main()
