#!/usr/bin/env python3
"""Weekly review — conversational reflection assistant for Lyndsey."""

import subprocess
import sys
import os
import re
from datetime import date, timedelta

JOURNAL_DIR = "/Users/lyndsey/Library/Mobile Documents/iCloud~md~obsidian/Documents/Lyndsey/📓Journal"
CLAUDE = "/opt/homebrew/bin/claude"
MODEL = "claude-sonnet-4-6"

WORK_ATTITUDES_SUMMARY = (
    "Embrace: decisiveness, clear boundaries, clarity of intent, record work done, "
    "write clear proposals, gather metrics, meet with stakeholders, monitor impact, "
    "respect others' contributions, thoughtful pace, prioritize personal energy, "
    "protect deep work, assertive kindness, celebrate progress. "
    "Reject: working >40 hrs unnecessarily, panic without data, doing everything instead of delegating, "
    "dismissing others' opinions, gossip or negative speculation, deciding on the last voice heard, "
    "over-explaining 'no', letting meetings fill all time, treating work as personal fulfillment."
)

QUESTIONS = [
    {
        "label": "needs",
        "marker": "What do I need?",
        "ask": "What do you need this coming week?",
        "has_why": False,
        "context": (
            "Personal needs: rest, recovery time, support from Ana, clarity on a project, "
            "deep work time, or social connection. Physical needs count too — sleep, exercise, nutrition."
        ),
    },
    {
        "label": "big_rocks",
        "marker": "All big rocks for the week completed?",
        "ask": "Did you complete all your big rocks this week?",
        "has_why": True,
        "context": (
            "Big rocks are the most important priorities — not just tasks completed, "
            "but whether the things that truly mattered got done. "
            "If not, what specifically got in the way? Avoidance, interruption, or unclear priorities?"
        ),
    },
    {
        "label": "went_well",
        "marker": "What went well?",
        "ask": "What went well this week?",
        "has_why": True,
        "context": (
            "Look across work, health, relationships, and personal growth. "
            "Lyndsey tends to undercount wins — mentoring, exercise, navigating hard conversations, "
            "and steady progress on long-term work all count."
        ),
    },
    {
        "label": "adjust",
        "marker": "What should be adjusted?",
        "ask": "What should be adjusted going forward?",
        "has_why": True,
        "context": (
            "Adjustments to behavior, routine, approach, or environment. "
            "Not self-criticism — calibration. What pattern would yield better results next week?"
        ),
    },
    {
        "label": "stop",
        "marker": "What should I stop doing?",
        "ask": "What should you stop doing?",
        "has_why": True,
        "context": (
            "Habits or patterns that drain energy or cause harm: "
            "over-explaining, doom scrolling, taking on others' problems, saying yes reflexively, "
            "staying on Slack/email after hours."
        ),
    },
    {
        "label": "start",
        "marker": "What should I start doing?",
        "ask": "What should you start doing?",
        "has_why": False,
        "context": (
            "New habits, practices, or approaches to try. "
            "Should be concrete and small enough to actually begin this week."
        ),
    },
    {
        "label": "attitudes",
        "marker": "Work Attitudes check",
        "ask": "Any work attitude patterns worth noting from this week?",
        "has_why": False,
        "context": WORK_ATTITUDES_SUMMARY,
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
    """Read a multi-line answer. Blank line finishes input."""
    lines = []
    while True:
        prefix = "  " if lines else "> "
        line = input(prefix)
        if not line.strip():
            break
        lines.append(line.strip())
    return "\n".join(lines)


def iso_week_info(d: date) -> tuple[int, int, date, date]:
    iso = d.isocalendar()
    week_start = d - timedelta(days=d.weekday())
    week_end = week_start + timedelta(days=6)
    return iso.year, iso.week, week_start, week_end


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
            parts.append("Highlights: " + "; ".join(lines[:3]))

    review_match = re.search(r"## Review what happened.*", content, re.DOTALL)
    if review_match:
        answers = re.findall(r"^  - (.+)$", review_match.group(0), re.MULTILINE)
        if answers:
            parts.append("Notes: " + "; ".join(answers[:2]))

    return " | ".join(parts)


def get_week_context(week_start: date) -> str:
    entries = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        if day > date.today():
            break
        filepath = os.path.join(JOURNAL_DIR, f"{day.strftime('%Y-%m-%d')}.md")
        if not os.path.exists(filepath):
            continue
        with open(filepath, "r") as f:
            content = f.read()
        summary = extract_day_summary(content)
        if summary:
            entries.append(f"{day.strftime('%A %b %-d')}: {summary}")
    return "\n".join(entries)


def create_weekly_note(filepath: str, week_start: date, week_end: date, week_num: int) -> None:
    start_str = week_start.strftime("%b %-d")
    end_str = week_end.strftime("%b %-d, %Y")
    content = f"""# Week {week_num} Review — {start_str}–{end_str}

## Reflections

##### What do I need?

##### All big rocks for the week completed?

##### What went well?

##### What should be adjusted?

##### What should I stop doing?

##### What should I start doing?

##### Work Attitudes check

## Action Items
- Create tasks for Ana's concerns, interests, or problems expressed this week
- Create tasks to resolve events from last week
- Create tasks to prepare for events in the upcoming week
- Create tasks from last week's incomplete tasks
- Create tasks from last week's journal notes
- Follow up on things waiting for
- Move projects closer to completion
- Attend to issues in environment
- Add major highlights from the past week, month, quarter, or year to current journal
- Review someday list

## After Review
- Categorize tasks in Inbox
- Schedule tasks with definite deadlines
"""
    with open(filepath, "w") as f:
        f.write(content)


def get_unanswered_questions(filepath: str) -> list[dict]:
    if not os.path.exists(filepath):
        return QUESTIONS
    with open(filepath, "r") as f:
        content = f.read()
    return [q for q in QUESTIONS if f"##### {q['marker']}\n\n" in content]


def write_answers(filepath: str, answers: dict) -> None:
    with open(filepath, "r") as f:
        content = f.read()

    for q in QUESTIONS:
        answer = answers.get(q["label"])
        if not answer:
            continue
        lines = [l for l in answer.split("\n") if l.strip()]
        sub_bullets = "\n".join(f"- {l}" for l in lines)
        marker = f"##### {q['marker']}\n\n"
        if marker in content:
            content = content.replace(marker, f"##### {q['marker']}\n{sub_bullets}\n\n", 1)

    with open(filepath, "w") as f:
        f.write(content)


def ask_with_followup(question_data: dict, week_context: str) -> str | None:
    print(f"\n{question_data['ask']}")
    answer = read_answer()

    if not answer:
        return None

    for _ in range(2):
        context_answer = answer.replace("\n", ". ")

        if question_data["has_why"]:
            followup_prompt = (
                f"You are a thoughtful weekly review companion for Lyndsey.\n"
                f"Background: {question_data['context']}\n"
                f"This week's journal context: {week_context or 'none available'}\n"
                f"Question: {question_data['ask']}\n"
                f"Lyndsey's answer so far: \"{context_answer}\"\n\n"
                f"Push back if the answer doesn't explain WHY — the emotion, root cause, or motivation. "
                f"Ask ONE short follow-up question (under 12 words) that probes deeper. "
                f"You may hint at a possible angle to spark reflection. "
                f"If the answer is already sufficiently reflective, respond with exactly: DONE"
            )
        else:
            followup_prompt = (
                f"You are a brief weekly review companion for Lyndsey.\n"
                f"Background: {question_data['context']}\n"
                f"This week's journal context: {week_context or 'none available'}\n"
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
    iso_year, week_num, week_start, week_end = iso_week_info(today)

    weekly_file = os.path.join(JOURNAL_DIR, f"{iso_year}-W{week_num:02d}.md")

    if not os.path.exists(weekly_file):
        create_weekly_note(weekly_file, week_start, week_end, week_num)

    unanswered = get_unanswered_questions(weekly_file)

    if not unanswered:
        print(f"Weekly review for Week {week_num} is already complete.")
        input("Press Enter to close.")
        sys.exit(0)

    already_answered = len(QUESTIONS) - len(unanswered)
    week_context = get_week_context(week_start)

    print(f"\nWeekly Review — Week {week_num} ({week_start.strftime('%b %-d')}–{week_end.strftime('%b %-d')})")
    print("─" * 40)
    if already_answered:
        print(f"Resuming — {already_answered} of {len(QUESTIONS)} questions already answered.")
    if week_context:
        lines = week_context.split("\n")
        print(f"\nThis week:")
        for l in lines[:4]:
            print(f"  {l}")
        if len(lines) > 4:
            print(f"  ... ({len(lines) - 4} more days)")
    print("\nPress Enter to skip any question. Type multiple lines — blank line to finish.\n")

    answers = {}
    for q in unanswered:
        if q["label"] == "attitudes":
            print("\nWork Attitudes Reference:")
            print("  Embrace: decisiveness, clear boundaries, clarity of intent,")
            print("           protect deep work, assertive kindness, celebrate progress.")
            print("  Reject:  overwork, panic without data, gossip, dismissing others,")
            print("           meetings filling all time, work as personal fulfillment.")
        answer = ask_with_followup(q, week_context)
        if answer:
            answers[q["label"]] = answer

    if answers:
        print("\nWriting to weekly note...")
        write_answers(weekly_file, answers)
        print(f"\nDone — {len(answers)} of {len(unanswered)} questions answered. ✓")
        print(f"Note: {os.path.basename(weekly_file)}")
    else:
        print("\nNo answers recorded.")

    input("\nPress Enter to close.")


if __name__ == "__main__":
    main()
