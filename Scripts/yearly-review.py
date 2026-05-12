#!/usr/bin/env python3
"""Yearly review — conversational reflection assistant for Lyndsey."""

import subprocess
import sys
import os
import re
from datetime import date

JOURNAL_DIR = "/Users/lyndsey/Library/Mobile Documents/iCloud~md~obsidian/Documents/Lyndsey/📓Journal"
CLAUDE = "/opt/homebrew/bin/claude"
MODEL = "claude-sonnet-4-6"

QUESTIONS = [
    {
        "label": "last_year_goals",
        "marker": "Goals from last year",
        "ask": "Which goals from last year did you accomplish — and which didn't happen?",
        "has_why": True,
        "context": (
            "Be honest about the full picture — wins and misses. For what didn't happen, "
            "was it avoidance, shifting priorities, life circumstances, or goals that no longer fit who you are?"
        ),
    },
    {
        "label": "next_year_goals",
        "marker": "Goals for next year",
        "ask": "What are your goals for next year?",
        "has_why": False,
        "context": (
            "Year goals should be meaningful and worth sustaining through four quarters. "
            "Are they connected to what genuinely matters — not just what sounds ambitious? "
            "Do you have quarterly milestones or atomic habits to carry them forward?"
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


def get_year_context(year: int) -> str:
    """Read quarterly review notes from this year, falling back to monthly reviews."""
    entries = []

    # Try quarterly review notes first
    for q in range(1, 5):
        quarterly_file = os.path.join(JOURNAL_DIR, f"{year}-Q{q}.md")
        if os.path.exists(quarterly_file):
            with open(quarterly_file, "r") as f:
                content = f.read()
            answers = re.findall(r"^- (.+)$", content, re.MULTILINE)
            if answers:
                entries.append(f"Q{q}: " + "; ".join(answers[:3]))

    # Fall back to monthly review notes
    if not entries:
        for m in range(1, 13):
            monthly_file = os.path.join(JOURNAL_DIR, f"{year}-M{m:02d}.md")
            if os.path.exists(monthly_file):
                with open(monthly_file, "r") as f:
                    content = f.read()
                month_name = date(year, m, 1).strftime("%b")
                answers = re.findall(r"^- (.+)$", content, re.MULTILINE)
                if answers:
                    entries.append(f"{month_name}: " + "; ".join(answers[:2]))

    return "\n".join(entries)


def get_yearly_file(year: int) -> str:
    return os.path.join(JOURNAL_DIR, f"{year}-Year.md")


def create_yearly_note(filepath: str, year: int) -> None:
    content = f"""# Year Review — {year}

## Goals

### Goals from last year

### Goals for next year

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


def ask_with_followup(question_data: dict, year_context: str) -> str | None:
    print(f"\n{question_data['ask']}")
    answer = read_answer()
    if not answer:
        return None

    for _ in range(2):
        context_answer = answer.replace("\n", ". ")
        if question_data["has_why"]:
            followup_prompt = (
                f"You are a thoughtful yearly review companion for Lyndsey.\n"
                f"Background: {question_data['context']}\n"
                f"This year's context: {year_context or 'none available'}\n"
                f"Question: {question_data['ask']}\n"
                f"Lyndsey's answer so far: \"{context_answer}\"\n\n"
                f"Push back if the answer doesn't reflect honestly on WHY goals were or weren't reached — "
                f"the real patterns, not just circumstances. "
                f"Ask ONE short follow-up question (under 12 words) that probes deeper. "
                f"If the answer is already sufficiently reflective, respond with exactly: DONE"
            )
        else:
            followup_prompt = (
                f"You are a thoughtful yearly review companion for Lyndsey.\n"
                f"Background: {question_data['context']}\n"
                f"Question: {question_data['ask']}\n"
                f"Lyndsey answered: \"{context_answer}\"\n\n"
                f"If the goals are vague or disconnected from what genuinely matters, "
                f"ask ONE short follow-up (under 12 words) that grounds them. "
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
    year = today.year
    yearly_file = get_yearly_file(year)

    if not os.path.exists(yearly_file):
        create_yearly_note(yearly_file, year)

    unanswered = get_unanswered_questions(yearly_file)
    if not unanswered:
        print(f"Year review for {year} is already complete.")
        input("Press Enter to close.")
        sys.exit(0)

    already_answered = len(QUESTIONS) - len(unanswered)
    year_context = get_year_context(year)

    print(f"\nYear Review — {year}")
    print("─" * 40)
    if already_answered:
        print(f"Resuming — {already_answered} of {len(QUESTIONS)} questions already answered.")
    if year_context:
        lines = year_context.split("\n")
        print(f"\nThis year:")
        for l in lines[:4]:
            print(f"  {l[:120]}")
        if len(lines) > 4:
            print(f"  ... ({len(lines) - 4} more entries)")
    print("\nPress Enter to skip any question. Type multiple lines — blank line to finish.\n")

    answers = {}
    for q in unanswered:
        answer = ask_with_followup(q, year_context)
        if answer:
            answers[q["label"]] = answer

    if answers:
        print("\nWriting to yearly note...")
        write_answers(yearly_file, answers)
        print(f"\nDone — {len(answers)} of {len(unanswered)} questions answered. ✓")
        print(f"Note: {os.path.basename(yearly_file)}")
    else:
        print("\nNo answers recorded.")

    input("\nPress Enter to close.")


if __name__ == "__main__":
    main()
