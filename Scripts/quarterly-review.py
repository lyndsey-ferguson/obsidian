#!/usr/bin/env python3
"""Quarterly review — conversational reflection assistant for Lyndsey."""

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
        "label": "last_quarter_goals",
        "marker": "Goals from last quarter",
        "ask": "Which goals from last quarter did you accomplish — and which didn't happen?",
        "has_why": True,
        "context": (
            "Celebrate accomplishments honestly. For goals not reached, probe the real reason: "
            "avoidance, wrong priorities, life getting in the way, or goals that no longer fit."
        ),
    },
    {
        "label": "next_quarter_goals",
        "marker": "Goals for next quarter",
        "ask": "What are your goals for next quarter?",
        "has_why": False,
        "context": (
            "Goals should connect to the year's priorities. "
            "Are they specific and achievable? Do you have atomic habits or milestones to support them? "
            "Quarters start Jan 1, Apr 1, Jul 1, Oct 1."
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


def get_quarter(d: date) -> int:
    return (d.month - 1) // 3 + 1


def get_quarter_range(year: int, quarter: int) -> tuple[date, date]:
    start_month = (quarter - 1) * 3 + 1
    end_month = start_month + 2
    end_day = calendar.monthrange(year, end_month)[1]
    return date(year, start_month, 1), date(year, end_month, end_day)


def get_quarter_context(year: int, quarter: int) -> str:
    """Read monthly review notes from this quarter, falling back to weekly reviews."""
    q_start, q_end = get_quarter_range(year, quarter)
    today = date.today()
    entries = []

    # Try monthly review notes first
    for m in range(q_start.month, q_end.month + 1):
        monthly_file = os.path.join(JOURNAL_DIR, f"{year}-M{m:02d}.md")
        if os.path.exists(monthly_file):
            with open(monthly_file, "r") as f:
                content = f.read()
            month_name = date(year, m, 1).strftime("%B")
            answers = re.findall(r"^- (.+)$", content, re.MULTILINE)
            if answers:
                entries.append(f"{month_name}: " + "; ".join(answers[:3]))

    # Fall back to weekly review notes if no monthly notes
    if not entries:
        d = q_start
        while d <= min(q_end, today):
            iso = d.isocalendar()
            weekly_file = os.path.join(JOURNAL_DIR, f"{iso.year}-W{iso.week:02d}.md")
            if os.path.exists(weekly_file):
                with open(weekly_file, "r") as f:
                    content = f.read()
                answers = re.findall(r"^- (.+)$", content, re.MULTILINE)
                if answers:
                    entries.append(f"W{iso.week:02d}: " + "; ".join(answers[:2]))
            d += timedelta(weeks=1)

    return "\n".join(entries)


def get_quarterly_file(year: int, quarter: int) -> str:
    return os.path.join(JOURNAL_DIR, f"{year}-Q{quarter}.md")


def create_quarterly_note(filepath: str, year: int, quarter: int) -> None:
    q_start, q_end = get_quarter_range(year, quarter)
    label = f"Q{quarter} {year} ({q_start.strftime('%b')}–{q_end.strftime('%b')})"
    content = f"""# Quarter Review — {label}

## Goals

### Goals from last quarter

### Goals for next quarter

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


def ask_with_followup(question_data: dict, quarter_context: str) -> str | None:
    print(f"\n{question_data['ask']}")
    answer = read_answer()
    if not answer:
        return None

    for _ in range(2):
        context_answer = answer.replace("\n", ". ")
        if question_data["has_why"]:
            followup_prompt = (
                f"You are a thoughtful quarterly review companion for Lyndsey.\n"
                f"Background: {question_data['context']}\n"
                f"This quarter's context: {quarter_context or 'none available'}\n"
                f"Question: {question_data['ask']}\n"
                f"Lyndsey's answer so far: \"{context_answer}\"\n\n"
                f"Push back if the answer doesn't explain WHY goals were or weren't reached. "
                f"Ask ONE short follow-up question (under 12 words) that probes the real reason. "
                f"If the answer is already sufficiently reflective, respond with exactly: DONE"
            )
        else:
            followup_prompt = (
                f"You are a brief quarterly review companion for Lyndsey.\n"
                f"Background: {question_data['context']}\n"
                f"Question: {question_data['ask']}\n"
                f"Lyndsey answered: \"{context_answer}\"\n\n"
                f"If the goals are vague or lack specificity, ask ONE short follow-up (under 12 words). "
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
    quarter = get_quarter(today)
    quarterly_file = get_quarterly_file(year, quarter)

    if not os.path.exists(quarterly_file):
        create_quarterly_note(quarterly_file, year, quarter)

    unanswered = get_unanswered_questions(quarterly_file)
    if not unanswered:
        print(f"Quarterly review for Q{quarter} {year} is already complete.")
        input("Press Enter to close.")
        sys.exit(0)

    already_answered = len(QUESTIONS) - len(unanswered)
    quarter_context = get_quarter_context(year, quarter)
    q_start, q_end = get_quarter_range(year, quarter)

    print(f"\nQuarterly Review — Q{quarter} {year} ({q_start.strftime('%b %-d')}–{q_end.strftime('%b %-d')})")
    print("─" * 40)
    if already_answered:
        print(f"Resuming — {already_answered} of {len(QUESTIONS)} questions already answered.")
    if quarter_context:
        lines = quarter_context.split("\n")
        print(f"\nThis quarter:")
        for l in lines[:4]:
            print(f"  {l[:120]}")
        if len(lines) > 4:
            print(f"  ... ({len(lines) - 4} more entries)")
    print("\nPress Enter to skip any question. Type multiple lines — blank line to finish.\n")

    answers = {}
    for q in unanswered:
        answer = ask_with_followup(q, quarter_context)
        if answer:
            answers[q["label"]] = answer

    if answers:
        print("\nWriting to quarterly note...")
        write_answers(quarterly_file, answers)
        print(f"\nDone — {len(answers)} of {len(unanswered)} questions answered. ✓")
        print(f"Note: {os.path.basename(quarterly_file)}")
    else:
        print("\nNo answers recorded.")

    input("\nPress Enter to close.")


if __name__ == "__main__":
    main()
