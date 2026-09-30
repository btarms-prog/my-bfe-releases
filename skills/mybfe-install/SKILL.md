---
name: mybfe-install
description: Install, test and troubleshoot My B.F.E. (homestead herd software) — on Windows, and in a Windows 11 test virtual machine on Ubuntu. Use when someone is installing My B.F.E., setting up a Windows VM to test it, it will not start or open, Windows blocks the installer (SmartScreen, "Windows protected your PC", Smart App Control), first-time setup goes wrong, the phone cannot reach it (Tailscale), updating, or uninstalling. Triggers: "install My B.F.E.", MyBFE-Setup, "won't open", 127.0.0.1:8088, server.log, virt-manager, Windows 11 VM, Tailscale serve.
---

# Installing My B.F.E. — and finding out why it did not work

My B.F.E. is a homestead herd app that runs on the owner's own computer and is
used in a web browser. The phone reaches it through Tailscale. This skill helps
a person install it, set up a Windows test machine for it, and troubleshoot.

**How to help:** go one step at a time and wait for the person to say it worked.
Say what they should see before they do it. Most people following this are not
technical — explain *why* in one line, never paste a wall of commands. When
something fails, ask for the exact words on screen or the log (below) before
guessing. Steps marked *(not in the vendor's docs)* are practical experience,
not documentation — say so if they do not match what the person sees.

**Never touch the records.** Reinstalling, updating and uninstalling all leave
the herd file alone by design. Never delete, move or edit `bfe.db`; if it looks
broken, stop and make a copy of it first.

## Where everything is (Windows)

| What | Where |
|---|---|
| The program | `%LOCALAPPDATA%\Programs\My BFE` (its own Python is inside, in `python\`) |
| **The records** | `%LOCALAPPDATA%\My BFE\bfe.db` — kept on update and on uninstall |
| The app's log | `%LOCALAPPDATA%\My BFE\server.log` |
| Shortcuts | Start menu and (if chosen) desktop: *My B.F.E.*; and one in the Startup folder so it starts with the computer |
| The window | From 0.9.2 it opens in **a window of its own** (Edge's app mode — no address bar), else Chrome, else a normal browser tab. Underneath it is `http://127.0.0.1:8088`, this computer only — any browser can open that address too |

`%LOCALAPPDATA%` is usually `C:\Users\<name>\AppData\Local`. Paste it into File
Explorer's address bar to go there.

Installing needs no administrator. The installer is about 12.5 MB.

## Installing

1. Download the newest installer from
   **https://github.com/btarms-prog/my-bfe-releases/releases** —
   `MyBFE-Setup-<version>.exe`. **Edge may warn** that the file is not commonly
   downloaded; choose to keep it (the menu on the download, then **Keep**).
2. Run it. It is not signed yet, so Windows warns first:
   - **"Windows protected your PC"** (SmartScreen). Microsoft: for an unsigned
     app the "User must choose "Run anyway" before the app can run." The **Run
     anyway** button appears after clicking **More info** *(the More info step
     is not in Microsoft's docs)*.
   - **Smart App Control** (Windows 11 only) could block it outright, with no
     way past for this one app — Microsoft: "There is currently no way to
     bypass Smart App Control protection for individual apps." **Not yet
     confirmed either way:** on 2026-09-30 it seemed not to block 0.9.0 when
     switched ON, but it was later found back in *Evaluation* — so whether it
     was really on is uncertain. Its decisions rest on Microsoft's cloud
     reputation, so check it on every new version: note the setting before and
     after. See *Blocked by Smart App Control* below.
3. Choose whether to put an icon on the desktop, then **Install**, then leave
   **Open My B.F.E. now** ticked and **Finish**. It opens in its own window (0.9.2 on; earlier versions use a browser tab).
4. **First-time setup** walks through: the owner (name and a 4–6 digit PIN),
   the place and its animals, feeding, backups, and the phone. Everything after
   the owner can be skipped and done later in Settings.

## Troubleshooting on Windows

**Nothing opens, or the browser says it can't reach the page.**
1. Open **My B.F.E.** from the Start menu (it starts the app if it is not
   running, then opens the browser). Wait 20 seconds, reload.
2. Still nothing: open `%LOCALAPPDATA%\My BFE\server.log` in Notepad and read the
   last 20 lines. A Python "Traceback" names the problem — report its last line.
3. Something else may be using port 8088. In Command Prompt:
   `netstat -ano | findstr :8088` — a line ending in LISTENING shows the
   process id; Task Manager → Details shows which program it is.

**Start / stop it by hand** (Command Prompt):
```
cd /d "%LOCALAPPDATA%\Programs\My BFE"
python\python.exe -m bfe.launch            & rem start if needed, open the browser
python\python.exe -m bfe.launch --stop     & rem stop it
```

**Reinstall** — safe: run the installer again. It stops the running app,
replaces the program, and starts it again. The records are untouched.

**Uninstall** — Settings → Apps → *My B.F.E.* → Uninstall. **The records stay**
in `%LOCALAPPDATA%\My BFE`, so reinstalling later picks them back up. To remove
them too, delete that folder by hand — only after a backup.

**No new version found, when there is one:**
1. In the browser, open `http://127.0.0.1:8088/api/update?force=1` (signed in
   as an owner) and read it: `latest` is the newest version it could find,
   `error` says why it could not look.
2. Check the app's own secure connection from the program folder in Command
   Prompt — it should print `200`:
   ```
   cd /d "%LOCALAPPDATA%\Programs\My BFE"
   python\python.exe -c "from bfe import net; print(net.urlopen('https://api.github.com/repos/btarms-prog/my-bfe-releases/releases/latest').status)"
   ```
   `CERTIFICATE_VERIFY_FAILED` means a version before 0.9.3 (it could not check
   certificates on a fresh Windows) — install 0.9.3 or newer by hand.
   `HTTP Error 403: rate limit exceeded` is GitHub's hourly limit; from 0.9.3
   the app then reads the releases page instead.
3. The reason for any failed check is also in `server.log`
   (`update check failed: …`).

**Versions 0.9.0–0.9.2 cannot update themselves** — install 0.9.3 or newer by
hand once, over the top; the records are kept.

**Updates** — owners see *"A new version of My B.F.E. is ready"* across the
top, with **Update**. It downloads the new installer, checks it against the
releases page's checksum, installs quietly, and the page comes back by itself
in a minute or so. Settings (bottom) shows the version and *Check for a new
version*. Every past version stays on the releases page; to go back, make a
backup, then run the older installer.

### Blocked by Smart App Control

Where to see it (Microsoft): Windows Security → **App & browser control** →
**Smart App Control settings**. Microsoft says it "can only be enabled on a
clean install", that "unknown, unsigned code are blocked by default", and that
in *evaluation* mode it watches first and may turn itself off.
- **On a test virtual machine:** it is fine to switch it **Off** to carry on —
  but first **write down that it blocked the installer**; that finding decides
  whether My B.F.E. needs a signed installer.
- **On someone's real computer:** do not advise switching a security feature
  off. Stop and tell the owner of My B.F.E. — it means the installer needs
  signing.

## The phone (Tailscale)

The phone needs Tailscale on this computer and on the phone, both signed in to
the same account; first-time setup's Phone step (or Settings → Phone) checks
each part and shows a QR code. If it is stuck:
- **Tailscale not found / not signed in** — install from
  https://tailscale.com/download, open it, sign in. Command Prompt check:
  `"C:\Program Files\Tailscale\tailscale.exe" status`
- **"Secure address" not ticked** — Tailscale's docs: open the DNS page of the
  admin console (https://console.tailscale.com/admin/dns), "Enable MagicDNS if
  not already enabled", then "Under **HTTPS Certificates**, select **Enable
  HTTPS**", and acknowledge that machine names go on a public certificate log.
- **Serving** — the app runs this itself. To check:
  `"C:\Program Files\Tailscale\tailscale.exe" serve status`. Tailscale: with
  `--bg` it "runs persistently in the background" and resumes after a reboot.
  No administrator is needed to serve a port.
- **iPhone** (Tailscale's docs): "Download Tailscale from the App Store",
  "Launch the app, select **Get Started**, accept the prompts to install a VPN
  configuration", "Select **Log in**". Then scan the QR code, open it in Safari,
  Share → **Add to Home Screen**. After Airplane Mode, check the Tailscale app
  says Connected.

## A Windows 11 test machine on Ubuntu

For testing the installer without a Windows PC. The host needs virtualization
switched on (`grep -cE '(vmx|svm)' /proc/cpuinfo` > 0), 8 GB+ RAM (16 is
comfortable) and **about 70 GB free** (`df -h /`). A nearly full disk makes
Ubuntu itself misbehave — do not start below ~70 GB.

**1. Windows 11 itself** — either of Microsoft's own downloads:
- **The ordinary Windows 11 ISO** (used for the 2026-09-30 test — no form):
  https://www.microsoft.com/software-download/windows11 → *Download Windows 11
  Disk Image (ISO) for x64 devices*. During setup choose **I don't have a
  product key**; it installs unactivated, which is fine for testing.
- **Windows 11 Enterprise evaluation**:
  https://www.microsoft.com/en-us/evalcenter/evaluate-windows-11-enterprise —
  "90-day evaluation"; "A product key is not required" — but its download page
  asks for business details in a sign-up form first.

(Microsoft's ready-made developer VMs are no longer offered.)

Windows 11 needs (Microsoft's spec page): 2+ cores, "4 gigabytes (GB)" RAM,
"64 GB or larger storage", "UEFI, Secure Boot capable", "Trusted Platform
Module (TPM) version 2.0". A virtual machine provides the TPM and Secure Boot
in software.

**2. The virtual machine software** — virt-manager, from Ubuntu's own
repositories (Ubuntu 24.04 ships 4.1, which turns on a TPM by default when the
machine uses UEFI — as long as `swtpm` is installed):
```bash
sudo apt install qemu-kvm libvirt-daemon-system virt-manager ovmf swtpm-tools
sudo adduser $USER libvirt      # Ubuntu's docs; then log out and back in
```
(Ubuntu's docs give the first three packages; `ovmf` is the UEFI firmware and
`swtpm-tools` the software TPM — both in Ubuntu's repositories.)

**3. Create it** in *Virtual Machine Manager* *(these clicks are not in any
vendor's docs — check each screen against them)*:
1. **File → New Virtual Machine → Local install media**, choose the ISO. It
   should detect **Microsoft Windows 11**.
2. Memory **6144** MB and **4** CPUs (on an 8-thread, 16 GB host); disk **64 GB**.
3. Tick **Customize configuration before install**, then **Finish**.
4. **Overview → Firmware**: a **UEFI** choice; if there is a list, pick the one
   with `secboot` or `ms` in its name (Secure Boot). Check there is a **TPM**
   device, version **2.0** — if not, **Add Hardware → TPM**, Emulated, 2.0.
5. **Begin Installation**. Click into the window and press a key as soon as
   it says "Press any key to boot from CD or DVD" — it only waits a few
   seconds. **Missed it and landed in a blue firmware menu?** Choose **Boot
   Manager → UEFI QEMU DVD-ROM**, then tap the spacebar straight away *(what
   worked on 2026-09-30; not in any vendor's docs)*.
6. Windows setup may insist on a Microsoft account. Microsoft's evaluation page
   says Enterprise needs one; no Microsoft document describes a way round it.
   Use one, or a throwaway one.

Networking works out of the box (libvirt's default NAT network), so inside the
VM just open Edge, go to the releases page and download the installer.

**4. Save a clean checkpoint** — once Windows is installed and **fully shut
down**, before installing My B.F.E., copy the machine's three parts so every
new version can be tested on a fresh Windows. (Copying files rather than
virt-manager snapshots, which were not reliable with UEFI + TPM on Ubuntu
24.04 — what worked on 2026-09-30, not vendor documentation.) For a VM named
`win11-bfe`:
```bash
sudo mkdir -p /var/lib/libvirt/clean-win11/swtpm
sudo cp --sparse=always /var/lib/libvirt/images/win11-bfe.qcow2 /var/lib/libvirt/clean-win11/
sudo cp /var/lib/libvirt/qemu/nvram/win11-bfe_VARS.fd /var/lib/libvirt/clean-win11/
sudo cp -a /var/lib/libvirt/swtpm/. /var/lib/libvirt/clean-win11/swtpm/
```
To go back to it, with the VM shut off:
```bash
sudo cp --sparse=always /var/lib/libvirt/clean-win11/win11-bfe.qcow2 /var/lib/libvirt/images/
sudo cp /var/lib/libvirt/clean-win11/win11-bfe_VARS.fd /var/lib/libvirt/qemu/nvram/
sudo cp -a /var/lib/libvirt/clean-win11/swtpm/. /var/lib/libvirt/swtpm/
```

**5. The test, each release** — from the clean checkpoint: download from the
releases page (note any **Edge** download warning and SmartScreen screen);
switch **Smart App Control ON** for the worst case (Windows Security → App &
browser control) and record whether it blocks; install; it opens in its own
window (no address bar; note its taskbar icon, and anything Edge shows on its
first run); first-time setup;
close the browser and reopen from the Start menu; restart Windows (it should
start by itself); reinstall over the top (records kept); one-click update
from the previous version; the phone through Tailscale; uninstall (the
records must stay in `%LOCALAPPDATA%\My BFE`).

**6. Clean up afterwards** — the disk image is the big part. In Virtual
Machine Manager: select the VM → **Delete**, and tick **Delete associated
storage files**. Then `df -h /` to confirm the space came back.

## When helping from another machine

If the person is on a different computer from the one with the problem, ask
them to paste back, in order: what they clicked, the exact message on screen,
then (Windows) the last 20 lines of `server.log` and the output of
`python\python.exe -m bfe.launch` run from the program folder, or (Ubuntu host)
`df -h /; virsh -c qemu:///system list --all`.
