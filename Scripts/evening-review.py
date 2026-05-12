#!/usr/bin/env python3
"""Evening journal review — conversational assistant for Lyndsey."""

import subprocess
import sys
import os
import re
from datetime import date

JOURNAL_DIR = "/Users/lyndsey/Library/Mobile Documents/iCloud~md~obsidian/Documents/Lyndsey/📓Journal"
CLAUDE = "/opt/homebrew/bin/claude"
MODEL = "claude-sonnet-4-6"

# Each question carries only the context relevant to it — kept light.
QUESTIONS = [
    {
        "label": "wins",
        "checklist": 'Journal the "wins" for today',
        "ask": "Wins for today?",
        "context": (
            "Lyndsey tends to undercount wins. Technical problem-solving, mentoring moments, "
            "and exercise count even when they feel routine."
        ),
    },
    {
        "label": "tedious",
        "checklist": "Journal tedious or repetitious tasks you performed",
        "ask": "Tedious or repetitious tasks today?",
        "context": (
            "Admin work is heavy: condo board, banking, medical coordination for Ana, car issues. "
            "These all count as tedious tasks."
        ),
    },
    {
        "label": "enjoyed",
        "checklist": "What did you enjoy today? Why?",
        "ask": "What did you enjoy today, and why?",
        "context": (
            "Consistent energisers: gym and exercise, mentoring others, unexpected social connection, "
            "technical wins, tender moments with Ana."
        ),
    },
    {
        "label": "disliked",
        "checklist": "What did you dislike today? Why?",
        "ask": "What did you dislike today, and why?",
        "context": (
            "Common patterns: doom scrolling when bored, anger responses that missed the mark, "
            "physical pain interfering with plans, feeling unfocused."
        ),
    },
    {
        "label": "offenses",
        "checklist": "Journal any responses to offenses to loved ones.",
        "ask": "Any responses to offenses with loved ones to note?",
        "context": (
            "Anger spikes and sharp words with Ana are worth capturing honestly — "
            "both what happened and how Lyndsey responded."
        ),
    },
    {
        "label": "ana_emotional",
        "checklist": "Captured what Ana has told you and the emotional aspects?",
        "ask": "What did Ana share with you today, emotionally?",
        "context": (
            "Ana's family (Susana, Pablo, siblings), her health, and her daily mood matter. "
            "The emotional subtext is often as important as the facts."
        ),
    },
    {
        "label": "ana_interesting",
        "checklist": "Anything interesting to tell Ana?",
        "ask": "Anything interesting to share with Ana?",
        "context": "Something from work, a learning moment, or an observation that might spark a good conversation.",
    },
    {
        "label": "ana_matters",
        "checklist": "❤️ Did something that matters to Ana?",
        "ask": "Did you do something that matters to Ana today? ❤️",
        "context": (
            "Small acts count: initiated affection, asked about her day, "
            "followed up on something she mentioned, did something together."
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


def get_highlights(content: str) -> str:
    match = re.search(r"## Highlights\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
    if not match:
        return ""
    raw = match.group(1)
    raw = re.sub(r"<%.*?%>", "", raw)  # strip Templater markers
    lines = [l for l in raw.splitlines() if l.strip().lstrip("* ").strip()]
    return "\n".join(lines).strip()


def read_answer() -> str:
    """Read a multi-line answer. Blank line finishes input."""
    lines = []
    while True:
        prefix = "  " if lines else "> "
        line = input(prefix)
        if not line.strip():
            break
        lines.append(line.strip())
    return "\n".join(lines)


def ask_with_followup(question_data: dict, highlights: str) -> str | None:
    print(f"\n{question_data['ask']}")
    answer = read_answer()

    if not answer:
        return None

    has_why = "why" in question_data['ask'].lower()

    for _ in range(2):
        context_answer = answer.replace("\n", ". ")

        if has_why:
            followup_prompt = (
                f"You are a thoughtful evening journal companion for Lyndsey.\n"
                f"Background: {question_data['context']}\n"
                f"Today's highlights: {highlights or 'none recorded'}\n"
                f"Question: {question_data['ask']}\n"
                f"Lyndsey's answer so far: \"{context_answer}\"\n\n"
                f"This question asks 'why' — the emotional reason, feeling, or motivation behind it. "
                f"If the answer only describes what happened without addressing feelings or meaning, "
                f"push back with ONE short follow-up question (under 12 words) that probes the emotional "
                f"or motivational dimension. You may hint at a possible angle to spark reflection "
                f"(e.g. 'Was it the sense of control, or something else?'). "
                f"If the answer already addresses the 'why' sufficiently, respond with exactly: DONE"
            )
        else:
            followup_prompt = (
                f"You are a brief evening journal companion for Lyndsey.\n"
                f"Background: {question_data['context']}\n"
                f"Today's highlights: {highlights or 'none recorded'}\n"
                f"Question asked: {question_data['ask']}\n"
                f"Lyndsey answered: \"{context_answer}\"\n\n"
                f"If the answer is vague or under 6 words, respond with ONE short follow-up question (under 12 words) to draw out more. "
                f"If the answer is sufficient, respond with exactly: DONE"
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


def already_completed(content: str) -> bool:
    review_match = re.search(r"## Review what happened.*", content, re.DOTALL)
    if not review_match:
        return False
    return bool(re.search(r"^- .+\n  - ", review_match.group(0), re.MULTILINE))


def write_answers(journal_file: str, answers: dict) -> None:
    with open(journal_file, "r") as f:
        content = f.read()

    for q in QUESTIONS:
        answer = answers.get(q["label"])
        if not answer:
            continue
        pattern = re.escape(f"- {q['checklist']}")
        lines = [l for l in answer.split("\n") if l.strip()]
        sub_bullets = "\n  - ".join(lines)
        replacement = f"- {q['checklist']}\n  - {sub_bullets}"
        content = re.sub(pattern, replacement, content, count=1)

    with open(journal_file, "w") as f:
        f.write(content)


def main() -> None:
    today = date.today().strftime("%Y-%m-%d")
    journal_file = os.path.join(JOURNAL_DIR, f"{today}.md")

    if not os.path.exists(journal_file):
        print(f"No journal file found for {today}.")
        input("Press Enter to close.")
        sys.exit(1)

    with open(journal_file, "r") as f:
        content = f.read()

    if already_completed(content):
        print("Evening review already done for today.")
        input("Press Enter to close.")
        sys.exit(0)

    highlights = get_highlights(content)

    print(f"\nEvening Review — {today}")
    print("─" * 40)
    if highlights:
        preview = highlights[:150] + ("..." if len(highlights) > 150 else "")
        print(f"Highlights: {preview}")
    print("\nPress Enter to skip any question. Type multiple lines — blank line to finish.\n")

    answers = {}
    for q in QUESTIONS:
        answer = ask_with_followup(q, highlights)
        if answer:
            answers[q["label"]] = answer

    if answers:
        print("\nWriting to journal...")
        write_answers(journal_file, answers)
        print(f"\nDone — {len(answers)} of {len(QUESTIONS)} questions answered. ✓")
    else:
        print("\nNo answers recorded.")

    input("\nPress Enter to close.")


if __name__ == "__main__":
    main()
