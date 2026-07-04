#!/usr/bin/env python3
"""
mail_to_obsidian.py
Polls Mail.app every 10 minutes (via launchd).

receipts_* mailboxes (any account)
  → 🧾 Receipts/YYYY-MM-DD Subject.md, then deleted from Mail.
  → ZIPS Cleaners emails also create a Reminders item for 10 AM today.

4707 Condo Board + subfolders (Gmail)
  → 🏣 Condo Board/YYYY-MM-DD Thread Subject.md (grouped by thread), then deleted from Mail.

Live copy: ~/.claude/scripts/mail_to_obsidian.py
Backup:    ~/Developer/obsidian/Scripts/mail_to_obsidian.py
"""

import email as _email
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
GMAIL_ACCOUNT = "Google"             # exact account name in Mail.app sidebar
BOARD_MAILBOX = "4707 Condo Board"   # exact mailbox name in Mail.app
ZIPS_SENDER   = "noreply4@321zips.com"

VAULT        = "/Users/lyndsey/Library/Mobile Documents/iCloud~md~obsidian/Documents/Lyndsey"
RECEIPTS_DIR = Path(VAULT) / "🧾 Receipts"
BOARD_DIR    = Path(VAULT) / "🏣 Condo Board"
# ─────────────────────────────────────────────────────────────────────────────

# ASCII control chars as field/record separators — never appear in email metadata
FS = "\x1c"
RS = "\x1e"


def run_osascript(script: str) -> str:
    result = subprocess.run(
        ["osascript", "-"],
        input=script,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 and result.stderr:
        print(result.stderr.strip(), file=sys.stderr)
    return result.stdout.strip()


def read_temp_body(counter: str) -> str:
    path = f"/tmp/mail_obsidian_{counter}.txt"
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8", errors="replace") as f:
        body = f.read()
    os.remove(path)
    return body


def normalize_subject(subject: str) -> str:
    """Strip Re:/Fwd: prefixes repeatedly until none remain."""
    pattern = re.compile(r"^(Re|Fwd|FW|RE|FWD|AW|Aw):\s*", re.IGNORECASE)
    prev = None
    while prev != subject:
        prev = subject
        subject = pattern.sub("", subject).strip()
    return subject


def safe_filename(text: str, max_len: int = 60) -> str:
    return re.sub(r'[/:*?"<>|\\]', "", text)[:max_len].strip()


def esc(s: str) -> str:
    """Escape a value for embedding in an AppleScript double-quoted string."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


# ── Receipts ──────────────────────────────────────────────────────────────────

# Iterates every receipts_* top-level mailbox across all accounts.
# Writes each message body to /tmp/mail_obsidian_N.txt; returns FS/RS-delimited metadata.
_RECEIPTS_FETCH = """
tell application "Mail"
    set FS to ASCII character 28
    set RS to ASCII character 30
    set out to ""
    set counter to 0
    repeat with acct in accounts
        repeat with mb in mailboxes of acct
            if (name of mb) begins with "receipts_" then
                repeat with msg in (messages of mb)
                    try
                        set counter to counter + 1
                        set msgId to message id of msg
                        set {year:yr, month:mo, day:da} to date received of msg
                        set moInt to mo as integer
                        set ds to (yr as string) & "-" & text -2 thru -1 of ("0" & moInt) & "-" & text -2 thru -1 of ("0" & da)
                        set bodyPath to "/tmp/mail_obsidian_" & counter & ".txt"
                        set msgBody to source of msg
                        if msgBody is "" then set msgBody to content of msg
                        try
                            set fRef to open for access POSIX file bodyPath with write permission
                            write msgBody to fRef as string
                            close access fRef
                        on error
                            try
                                close access POSIX file bodyPath
                            end try
                        end try
                        set out to out & msgId & FS & (subject of msg) & FS & (sender of msg) & FS & ds & FS & (name of acct) & FS & (name of mb) & FS & counter & RS
                    on error
                    end try
                end repeat
            end if
        end repeat
    end repeat
    return out
end tell
"""


def get_receipt_messages() -> list[dict]:
    raw = run_osascript(_RECEIPTS_FETCH)
    messages = []
    for block in raw.split(RS):
        block = block.strip()
        if not block:
            continue
        parts = block.split(FS, 6)
        if len(parts) < 7:
            continue
        msg_id, subject, sender, date_str, account, mailbox, counter = parts
        try:
            msg_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            msg_date = datetime.now()
        messages.append({
            "id":      msg_id,
            "subject": subject,
            "sender":  sender,
            "date":    msg_date,
            "account": account,
            "mailbox": mailbox,
            "body":    read_temp_body(counter),
        })
    return messages


def extract_html_body(raw: str) -> str:
    """Extract HTML from raw MIME source. Falls back to plain text in <pre>."""
    try:
        msg = _email.message_from_string(raw)
        html, text = None, None
        for part in msg.walk():
            ct = part.get_content_type()
            charset = part.get_content_charset() or "utf-8"
            payload = part.get_payload(decode=True)
            if payload is None:
                continue
            decoded = payload.decode(charset, errors="replace")
            if ct == "text/html" and html is None:
                html = decoded
            elif ct == "text/plain" and text is None:
                text = decoded
        if html:
            return html
        if text:
            return f"<html><body><pre style='white-space:pre-wrap;font-family:sans-serif'>{text}</pre></body></html>"
    except Exception:
        pass
    return f"<html><body><pre style='white-space:pre-wrap'>{raw[:10000]}</pre></body></html>"


def extract_text_body(raw: str) -> str:
    """Extract plain text from raw MIME source, with correct charset decoding."""
    try:
        msg = _email.message_from_string(raw)
        for part in msg.walk():
            if part.get_content_type() != "text/plain":
                continue
            payload = part.get_payload(decode=True)
            if payload is None:
                continue
            charset = part.get_content_charset() or "utf-8"
            try:
                return payload.decode(charset).strip()
            except (LookupError, UnicodeDecodeError):
                return payload.decode("utf-8", errors="replace").strip()
    except Exception:
        pass
    return raw.strip()


def write_receipt(msg: dict) -> Path | None:
    filename = f"{msg['date'].strftime('%Y-%m-%d')} {safe_filename(msg['subject'])}.html"
    filepath = RECEIPTS_DIR / filename
    try:
        filepath.write_text(extract_html_body(msg["body"]), encoding="utf-8")
        if filepath.exists() and filepath.stat().st_size > 0:
            return filepath
    except Exception as e:
        print(f"Error writing {filepath}: {e}", file=sys.stderr)
    return None


def create_zips_reminder() -> None:
    run_osascript("""
tell application "Reminders"
    set pickupDate to current date
    set time of pickupDate to 36000
    make new reminder at end of default list with properties {name:"Pick up dry cleaning — ZIPS", due date:pickupDate}
end tell
""")


def delete_all_in_mailbox(account: str, mailbox: str) -> bool:
    script = f"""
tell application "Mail"
    try
        set mb to mailbox "{esc(mailbox)}" of account "{esc(account)}"
        delete every message of mb
        return "ok"
    on error e
        return "error:" & e
    end try
end tell
"""
    return run_osascript(script) == "ok"


def process_receipts() -> None:
    messages = get_receipt_messages()
    if not messages:
        return

    # Group by (account, mailbox) so we can bulk-delete per mailbox after writing
    by_mailbox: dict[tuple, list[dict]] = {}
    for msg in messages:
        by_mailbox.setdefault((msg["account"], msg["mailbox"]), []).append(msg)

    for (account, mailbox), msgs in by_mailbox.items():
        written = 0
        for msg in msgs:
            filepath = write_receipt(msg)
            if not filepath:
                continue
            written += 1
            if ZIPS_SENDER in msg["sender"] and msg["date"] >= datetime.now() - timedelta(days=7):
                create_zips_reminder()

        if written == len(msgs):
            if not delete_all_in_mailbox(account, mailbox):
                print(f"Warning: bulk delete failed for {account}/{mailbox}", file=sys.stderr)
        elif written > 0:
            print(f"Warning: only {written}/{len(msgs)} written for {account}/{mailbox} — skipping delete", file=sys.stderr)


# ── Board Emails ──────────────────────────────────────────────────────────────

# Iterates 4707 Condo Board and its direct subfolders in Google.
# Bodies written to /tmp/mail_obsidian_N.txt; returns FS/RS-delimited metadata.
_BOARD_FETCH = """
tell application "Mail"
    set FS to ASCII character 28
    set RS to ASCII character 30
    set out to ""
    set counter to 0
    try
        set boardBx to mailbox "__BOARD_MAILBOX__" of account "__GMAIL_ACCOUNT__"
    on error e
        return "ERROR:" & e
    end try
    set allBoxes to {boardBx}
    repeat with subBx in (mailboxes of boardBx)
        set end of allBoxes to subBx
    end repeat
    repeat with bx in allBoxes
        repeat with msg in (messages of bx)
            try
                set counter to counter + 1
                set msgId to message id of msg
                set {year:yr, month:mo, day:da, hours:hr, minutes:mn} to date received of msg
                set moInt to mo as integer
                set ds to (yr as string) & "-" & text -2 thru -1 of ("0" & moInt) & "-" & text -2 thru -1 of ("0" & da) & " " & text -2 thru -1 of ("0" & hr) & ":" & text -2 thru -1 of ("0" & mn)
                set bodyPath to "/tmp/mail_obsidian_" & counter & ".txt"
                set msgBody to source of msg
                if msgBody is "" then set msgBody to content of msg
                try
                    set fRef to open for access POSIX file bodyPath with write permission
                    write msgBody to fRef as string
                    close access fRef
                on error
                    try
                        close access POSIX file bodyPath
                    end try
                end try
                set out to out & msgId & FS & (subject of msg) & FS & (sender of msg) & FS & ds & FS & counter & RS
            on error
            end try
        end repeat
    end repeat
    return out
end tell
""".replace("__BOARD_MAILBOX__", BOARD_MAILBOX).replace("__GMAIL_ACCOUNT__", GMAIL_ACCOUNT)


def get_board_messages() -> list[dict]:
    raw = run_osascript(_BOARD_FETCH)
    if raw.startswith("ERROR:"):
        print(raw, file=sys.stderr)
        return []
    messages = []
    for block in raw.split(RS):
        block = block.strip()
        if not block:
            continue
        parts = block.split(FS, 4)
        if len(parts) < 5:
            continue
        msg_id, subject, sender, date_str, counter = parts
        try:
            msg_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        except ValueError:
            msg_date = datetime.now()
        messages.append({
            "id":      msg_id,
            "subject": subject,
            "sender":  sender,
            "date":    msg_date,
            "body":    extract_text_body(read_temp_body(counter)),
        })
    return messages


def write_board_thread(filepath: Path, thread_subject: str, messages: list[dict]) -> bool:
    try:
        sorted_msgs = sorted(messages, key=lambda m: m["date"])
        if filepath.exists():
            with open(filepath, "a", encoding="utf-8") as f:
                for msg in sorted_msgs:
                    f.write(f"\n## {msg['sender']} — {msg['date'].strftime('%Y-%m-%d %H:%M')}\n\n{msg['body']}\n\n---\n")
        else:
            first_date = sorted_msgs[0]["date"].strftime("%Y-%m-%d")
            lines = ["---", f'thread: "{thread_subject}"', f"first_email: {first_date}", "---", ""]
            for msg in sorted_msgs:
                lines += [f"## {msg['sender']} — {msg['date'].strftime('%Y-%m-%d %H:%M')}", "", msg["body"], "", "---", ""]
            filepath.write_text("\n".join(lines), encoding="utf-8")
        return filepath.exists() and filepath.stat().st_size > 0
    except Exception as e:
        print(f"Error writing {filepath}: {e}", file=sys.stderr)
        return False


def delete_all_board_messages() -> bool:
    script = f"""
tell application "Mail"
    try
        set boardBx to mailbox "{esc(BOARD_MAILBOX)}" of account "{esc(GMAIL_ACCOUNT)}"
        delete every message of boardBx
        repeat with subBx in (mailboxes of boardBx)
            delete every message of subBx
        end repeat
        return "ok"
    on error e
        return "error:" & e
    end try
end tell
"""
    return run_osascript(script) == "ok"


def process_board_emails() -> None:
    messages = get_board_messages()
    if not messages:
        return

    threads: dict[str, list[dict]] = {}
    for msg in messages:
        threads.setdefault(normalize_subject(msg["subject"]), []).append(msg)

    written = 0
    for thread_subject, thread_msgs in threads.items():
        first_date = min(m["date"] for m in thread_msgs).strftime("%Y-%m-%d")
        filepath = BOARD_DIR / f"{first_date} {safe_filename(thread_subject)}.md"
        if write_board_thread(filepath, thread_subject, thread_msgs):
            written += len(thread_msgs)

    if written == len(messages):
        if not delete_all_board_messages():
            print("Warning: bulk delete failed for board mailbox", file=sys.stderr)
    elif written > 0:
        print(f"Warning: only {written}/{len(messages)} board messages written — skipping delete", file=sys.stderr)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    BOARD_DIR.mkdir(parents=True, exist_ok=True)
    process_receipts()
    process_board_emails()


if __name__ == "__main__":
    main()
