#!/usr/bin/env python3
"""Make a safe, read-only copy of a My B.F.E. herd file to work on.

    python3 snapshot.py                 # finds the herd file, prints the copy's path
    python3 snapshot.py path/to/bfe.db  # a herd file somewhere else

The copy is made with SQLite's own backup, so it is consistent even while
My B.F.E. is running and writing. Everything an assistant does happens on the
copy: the real herd file is opened read-only and never written.
Python 3.8+ standard library only.
"""
import os, sqlite3, sys, tempfile, time
from pathlib import Path


def candidates():
    if os.environ.get("BFE_DB"):
        yield Path(os.environ["BFE_DB"])
    if sys.platform == "win32":
        yield Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "My BFE" / "bfe.db"
    elif sys.platform == "darwin":
        yield Path.home() / "Library" / "Application Support" / "My BFE" / "bfe.db"
    else:
        yield Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "my-bfe" / "bfe.db"


def find(arg=None):
    for p in ([Path(arg)] if arg else candidates()):
        if p.is_file():
            return p
    return None


def snapshot(src_path):
    out = Path(tempfile.gettempdir()) / f"mybfe-snapshot-{time.strftime('%Y%m%d-%H%M%S')}.db"
    src = sqlite3.connect(f"file:{src_path.resolve().as_posix()}?mode=ro", uri=True)
    dst = sqlite3.connect(out)
    with dst:
        src.backup(dst)
    src.close(); dst.close()
    return out


if __name__ == "__main__":
    p = find(sys.argv[1] if len(sys.argv) > 1 else None)
    if not p:
        sys.exit("No My B.F.E. herd file found. Pass its path: python3 snapshot.py /path/to/bfe.db")
    print(snapshot(p))
