# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npm test                                           # run all tests
npm test -- --testPathPattern=getRandomRuleOfLife  # run a single test file
```

## Architecture

This repo has two distinct types of scripts that coexist in `Scripts/`:

### Obsidian JS scripts (`Scripts/*.js`)
These run **inside Obsidian** via the Templater plugin as user scripts. They rely on the `app` global (Obsidian's vault API) at runtime — there is no import or require for it. The two current scripts are:
- `getRandomRuleOfLife.js` — called from the Journal Entry Template to display a random rule from `⭐️Lyndsey's Rules for Life.md`
- `getRandomCountOfCalloutsWithGivenTypes.js` — finds vault files containing specific callout types

**Testing**: `testHelpers.ts` is a Jest `setupFiles` entry that installs a global `app` mock, replacing `vault.cachedRead` with a local `fs.readFile` and `vault.getFiles` with a directory scan. This lets tests run against `TestFixtures/` files without Obsidian. Tests live in `Scripts/__tests__/`.

### Python automation scripts (`Scripts/*.py`)
Standalone CLI scripts that run outside Obsidian, invoked from Terminal (triggered by buttons in Obsidian notes via `osascript`, or by launchd). They use the `claude` CLI at `/opt/homebrew/bin/claude` for AI calls. The live copies that actually run are in `~/.claude/scripts/` — the copies here are backups.

- `evening-review.py` — interactive evening journal Q&A, writes answers into today's journal
- `weekly-review.py` — weekly reflection, creates `📓Journal/YYYY-WXX.md`
- `monthly-review.py` — monthly reflection, creates `📓Journal/YYYY-MXX.md`
- `quarterly-review.py` — quarterly reflection, creates `📓Journal/YYYY-QX.md`
- `yearly-review.py` — yearly reflection, creates `📓Journal/YYYY-Year.md`
- `daily-digest.py` — fetches Reddit/HN articles, summarizes via Claude, prepends a digest to today's journal

`com.lyndsey.daily-digest.plist` is the launchd agent (installed at `~/Library/LaunchAgents/`) that fires `daily-digest.py` via `WatchPaths` whenever the journal directory changes.

### Vault paths
All scripts target the live Obsidian vault at:
`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Lyndsey/`

The `templates/daily.md` in this repo is a legacy reference copy; the live templates are in the vault under `📌 Permanent Notes/Z Templates/`.
