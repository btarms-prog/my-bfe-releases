# My B.F.E. — downloads

**My B.F.E.** (Baby Farm Experiment) is homestead herd software: cattle and
horses, their weights, condition, health, feeding, breeding and temperament.
It runs on your own computer — your records never leave it — and your phone
reaches it privately through Tailscale, with no signal needed in the pasture.

This repository holds **the installers and release notes only.**

## Download

**[Latest version → Releases](https://github.com/btarms-prog/my-bfe-releases/releases)**
— download `MyBFE-Setup-<version>.exe` (Windows 10/11). Mac and Linux later.

### Windows will warn you first

The installer is not signed yet, so the first time you run it:

- **Edge** may say the download isn't commonly downloaded — choose to **Keep** it.
- **"Windows protected your PC"** — click **More info**, then **Run anyway**.
- **Smart App Control** (some new Windows 11 PCs) could block it. It did not
  block 0.9.0, even switched fully on; if it ever does, please tell us — it
  means the installer needs signing.

It installs for you only (no administrator), in about a minute, and opens in
your web browser. First-time setup walks you through the rest.

## Your records

Your records live in their own folder on your computer
(`%LOCALAPPDATA%\My BFE`), apart from the program. **Updating and uninstalling
never touch them.** Set up backups in first-time setup (Google Drive, a USB
drive, or both) — your computer is the only other copy.

## Versions

Every version stays on the [Releases](https://github.com/btarms-prog/my-bfe-releases/releases)
page, each with its own installer and checksum. The app tells an owner when a
new one is ready and installs it with one click. **To go back** to an earlier
version: make a backup, then run that version's installer.

## Skills for AI assistants

The `skills/` folder holds two skills in the open *Agent Skills* format
(a `SKILL.md` per folder), usable by Claude, Codex and other assistants that
read it:

| Skill | What it does |
|---|---|
| [`mybfe`](skills/mybfe/SKILL.md) | Ask your herd questions in plain language — gains, condition, health history, due dates, feed use — from your own records, **read-only** (it works on a copy and never changes your records). |
| [`mybfe-install`](skills/mybfe-install/SKILL.md) | Help installing, updating and troubleshooting My B.F.E., including setting up a Windows 11 test machine. |

To add them:

- **Claude Code** — copy each folder into `~/.claude/skills/`:
  ```bash
  git clone https://github.com/btarms-prog/my-bfe-releases.git
  mkdir -p ~/.claude/skills && cp -r my-bfe-releases/skills/* ~/.claude/skills/
  ```
- **Codex** — the same, into `~/.codex/skills/`.
- **Any other assistant** — give it the `SKILL.md` (and the `scripts/` folder
  for `mybfe`, which needs Python 3.8 or newer).
