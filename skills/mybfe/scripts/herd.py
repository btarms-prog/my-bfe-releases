#!/usr/bin/env python3
"""One row per animal, as My B.F.E. itself would describe it -- from a snapshot.

    python3 herd.py SNAPSHOT.db            # CSV to the screen
    python3 herd.py SNAPSHOT.db --json     # JSON
    python3 herd.py SNAPSHOT.db --all      # include pedigree-only ancestors

Applies the app's rules so an assistant does not have to re-derive them:
an entry replaced or undone by a later one (its entry_id in another entry's
`supersedes`) does not count; for a fact that can change (a name, sex, purpose)
the most recently RECORDED entry wins; for a measurement (weight, height,
condition) the one that HAPPENED most recently wins. Read-only.
Python 3.8+ standard library only.
"""
import csv, datetime, json, sqlite3, sys


def rows(path, include_external=False):
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    gone = {r[0] for r in con.execute("SELECT supersedes FROM entries WHERE supersedes IS NOT NULL")}
    by = {}
    for r in con.execute("SELECT * FROM entries WHERE subject_id != 'OP001' ORDER BY recorded_at, seq"):
        if r["entry_id"] in gone or r["kind"] == "correction":
            continue
        d = json.loads(r["data"] or "{}")
        if d.get("removed"):
            continue
        by.setdefault(r["subject_id"], []).append((r, d))
    names = {}
    for sid, es in by.items():
        for r, d in es:
            if r["kind"] == "naming":
                names[sid] = d.get("name")

    def last_recorded(es, kind):
        xs = [x for x in es if x[0]["kind"] == kind]
        return xs[-1] if xs else (None, {})

    def last_happened(es, kind):
        xs = [x for x in es if x[0]["kind"] == kind]
        xs.sort(key=lambda x: (x[0]["occurred_on"] or "", x[0]["seq"]))
        return xs[-1] if xs else (None, {})

    births = {sid: d for sid, es in by.items() for r, d in es if r["kind"] == "birth"}
    born_on = {sid: r["occurred_on"] for sid, es in by.items() for r, d in es if r["kind"] == "birth"}

    def display(sid, depth=0):
        """The app's name for an animal: its own name, or "<dam>'s <year> calf"."""
        if names.get(sid):
            return names[sid]
        dam = (births.get(sid) or {}).get("dam")
        if dam and depth < 10:
            dn = display(dam, depth + 1)
            return f"{dn}{chr(39) if dn.upper().endswith('S') else chr(39) + 's'} {(born_on.get(sid) or '')[:4]} calf".strip()
        return sid

    today = datetime.date.today()
    out = []
    for s in con.execute("SELECT * FROM subjects WHERE id != 'OP001' ORDER BY id"):
        if s["scope"] != "ours" and not include_external:
            continue
        es = by.get(s["id"], [])
        b, bd = last_recorded(es, "birth")
        dob = b["occurred_on"] if b else None
        age = None
        if dob:
            try:
                days = (today - datetime.date.fromisoformat(dob)).days
                age = f"{days // 365}y {days % 365 // 30}m" if days >= 365 else f"{days // 30}m"
            except ValueError:
                pass
        w, wd = last_happened(es, "weight")
        h, hd = last_happened(es, "height")
        c, cd = last_happened(es, "bcs")
        hl, hld = last_happened(es, "health")
        pc, pcd = last_happened(es, "preg_check")
        c3, c3d = last_happened(es, "c3_assessment")
        status = "died" if last_recorded(es, "death")[0] else "sold" if last_recorded(es, "sale")[0] else "here"
        out.append({
            "id": s["id"], "name": display(s["id"]), "named": bool(names.get(s["id"])), "module": s["module"],
            "scope": s["scope"], "status": status,
            "sex": last_recorded(es, "sex")[1].get("sex"),
            "born": dob, "born_precision": b["occurred_precision"] if b else None, "age": age,
            "dam": display(bd["dam"]) if bd.get("dam") else None, "sire": display(bd["sire"]) if bd.get("sire") else None,
            "purpose": last_recorded(es, "purpose")[1].get("purpose"),
            "castration_plan": last_recorded(es, "castration_plan")[1].get("plan"),
            "castrated_on": (last_recorded(es, "castration")[0] or {"occurred_on": None})["occurred_on"],
            "weight_lb": wd.get("lb"), "weighed_on": w["occurred_on"] if w else None, "weigh_method": wd.get("method"),
            "height_in": hd.get("inches"), "measured_on": h["occurred_on"] if h else None,
            "bcs": cd.get("score"), "bcs_scale": cd.get("scale"), "scored_on": c["occurred_on"] if c else None,
            "health_records": sum(1 for r, _ in es if r["kind"] == "health"),
            "last_health": f"{hld.get('type')} {hl['occurred_on'] or ''}".strip() if hl else None,
            "last_preg_check": f"{pcd.get('result')} {pc['occurred_on'] or ''}".strip() if pc else None,
            "last_c3_score": c3d.get("score") if c3 else None,
            "notes": sum(1 for r, _ in es if r["kind"] == "note"),
        })
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python3 herd.py SNAPSHOT.db [--json] [--all]")
    data = rows(sys.argv[1], include_external="--all" in sys.argv)
    if "--json" in sys.argv:
        print(json.dumps(data, indent=1))
    elif data:
        w = csv.DictWriter(sys.stdout, fieldnames=list(data[0].keys()))
        w.writeheader(); w.writerows(data)
