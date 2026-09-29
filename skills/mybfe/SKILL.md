---
name: mybfe
description: Answer questions about a My B.F.E. herd in plain language — from its own records, read-only. Use when someone asks about their cattle or horses as recorded in My B.F.E. (homestead herd software) — weights and gains, body condition, health and wormer history, feedings and feed use, pregnancies and due dates, temperament (C3 / BIF), family lines, who was sold or died, anything worth charting or summarising. Triggers: "My B.F.E.", "MyBFE", "my herd", bfe.db, "how much has … gained", "who's due", "when did we last worm", "which cows are thin".
---

# My B.F.E. — asking the herd

My B.F.E. keeps a homestead's animals in one SQLite file, `bfe.db`. This skill
lets you (any AI assistant that can run Python, or read a CSV) answer questions
about it in plain language: *"who's gained the most since spring?"*, *"when did
we last worm the heifers?"*, *"which cows are due in the next month?"*.

## The rules that come first

1. **Never write to the herd file.** Not one row, not even to "fix" something.
   The app is the only thing that writes to it, and its records are the only
   copy of years of history. Work on a snapshot (below). If the person wants
   something recorded or corrected, tell them how to do it in the app.
2. **Work on a snapshot, always.** `scripts/snapshot.py` makes a consistent,
   read-only copy — safe even while the app is running — and prints its path.
3. **Never show PINs, sign-in data or other people's contact details.** `person`
   entries hold hashed PINs; `contact` entries hold phone numbers and emails.
   Leave them out of answers unless the person asks about their own details.
4. **Unknown is an answer.** Many facts are genuinely unknown (a bought cow's
   birth date, an unweighed calf). Say so; do not guess or fill in.
   Dates can be *estimated* — say "about" when `occurred_precision` is
   `estimated`.
5. **Show your working in one line.** "Up 140 lb (760 → 900) from 12 Apr to
   29 Sep, tape both times." People check numbers against their animals.

## Getting started

```bash
python3 scripts/snapshot.py              # finds the herd file; prints the snapshot's path
python3 scripts/herd.py SNAPSHOT --json  # one row per animal, the app's own rules applied
```

`snapshot.py` looks for the herd file where My B.F.E. keeps it:

| Computer | Herd file |
|---|---|
| Windows | `%LOCALAPPDATA%\My BFE\bfe.db` |
| Mac | `~/Library/Application Support/My BFE/bfe.db` |
| Linux | `~/.local/share/my-bfe/bfe.db` |
| Run from the code (developers) | `bfe.db` beside the code |

Pass a path to use another file: `python3 scripts/snapshot.py /path/to/bfe.db`.

Start from `herd.py` for anything about animals as they are now (name, age,
latest weight, condition, status, parents). Go to SQL on the snapshot for
history, trends and anything `herd.py` does not carry.

## How the records work (read before writing SQL)

Nothing is ever overwritten. Everything that happens is an **entry**, and what
is true now is worked out from the entries.

**`subjects`** — one row per animal, plus the place itself.

| column | meaning |
|---|---|
| `id` | `A001`, `A002`… an animal. **`OP001` is the place** (its settings, people, feedings). IDs carry no meaning. |
| `module` | `cattle`, `equine` (a place may have renamed modules, e.g. `cattle-2`) |
| `scope` | `ours` = the place's own animals; `external` = pedigree-only ancestors (never lived here) |

**`entries`** — the history.

| column | meaning |
|---|---|
| `entry_id` | stable id |
| `subject_id` | the animal (or `OP001`) |
| `kind` | what sort of entry (table below) |
| `occurred_on` | the day it **happened** (`YYYY-MM-DD`), may be null |
| `occurred_precision` | `exact`, `estimated` or `unknown` |
| `recorded_at` | when it was **written down** — often later than it happened |
| `recorded_by` | the records key of the person who recorded it (map to a name through the latest `person` entries' `user` → `name`; never show their PIN) |
| `data` | JSON — the fields for that kind |
| `supersedes` | the `entry_id` this entry corrects or undoes |

**Which entry counts:**
- An entry whose `entry_id` appears in another entry's `supersedes` has been
  **replaced or undone — ignore it.** `correction` entries are the undo
  markers themselves; ignore them too.
- An entry whose `data` has `"removed": true` is a removal — ignore it and what
  it supersedes.
- **Facts that change** (name, sex, purpose, a setting): the most recently
  *recorded* entry wins — `ORDER BY recorded_at DESC, seq DESC`.
- **Measurements** (weight, height, condition): the one that *happened* most
  recently is "the latest" — `ORDER BY occurred_on DESC, seq DESC`. A weight
  recorded today about last spring is last spring's weight.
- **Status:** a `death` entry → died; else a `sale` → sold; else here.

Useful SQL shapes (SQLite has JSON built in):

```sql
-- entries that still count
WITH live AS (
  SELECT * FROM entries e
  WHERE kind != 'correction'
    AND entry_id NOT IN (SELECT supersedes FROM entries WHERE supersedes IS NOT NULL)
    AND COALESCE(json_extract(data,'$.removed'), 0) = 0)

-- every weight for one animal, oldest first
SELECT occurred_on, json_extract(data,'$.lb') lb, json_extract(data,'$.method') how
FROM live WHERE subject_id='A002' AND kind='weight' ORDER BY occurred_on, seq;
```

## Kinds of entry

On an animal:

| kind | data | notes |
|---|---|---|
| `naming` | `name` | names are usually capitals |
| `sex` | `sex` | `male`, `female`, `unknown` |
| `birth` | `dam`, `sire` (subject ids) | `occurred_on` = birth date; family lines follow dam/sire |
| `acquisition` | `from`, `price` | bought in |
| `origin` | `where` | |
| `purpose` | `purpose` | e.g. Permanent, To Sell |
| `use` | `use` | what it is kept for |
| `breed_declared` | `mix` (breed → share), `basis`, `certainty` | |
| `registry`, `registry_note` | `registered_name`, `code`, `herd_no`, `text` | |
| `weight` | `lb`, `method` (`scale`, `tape`, `visual estimate`), `note` | pounds |
| `height` | `inches`, `method` | horses: hands = inches ÷ 4 |
| `bcs` | `score`, `scale` (`1-9`, or `1-9 (Henneke)` for horses) | body condition, 1–9. Cattle: 1 emaciated … 5 moderate … 9 obese. Horses use the Henneke 1–9 |
| `health` | `type` (Deworming, Vaccination, Vet visit, Treatment, Injury, Other), `product` or `witness`, `route`, `detail`, `batch` | `batch` groups one job done to several animals |
| `note` | `text` | |
| `castration_plan` | `plan` | |
| `castration` | `method`, `source` | done |
| `preg_check` | `result` (`bred`, `open`, `unsure`), `stage_days`, `how`, `by` (who checked, as typed), `note` | |
| `bred` | `sire`, `how`, `note` | a known breeding date |
| `preg_loss` | | a pregnancy lost |
| `temperament` | `scale` (`bif`, or `companion` = the C3 Temperament Scale), `score`, `where` | **BIF docility 1–6** (1 docile … 6 very aggressive); **C3 Temperament Scale 1–9** (1 seeks people … 9 dangerous) |
| `c3_assessment` | `score`, `why`, `results`, `assessor`, `familiar`, `where`, `fed`, `company`, `flag`, `note`, `version` | one C3 protocol assessment |
| `c3_approval` | `score`, `median`, `counted`, `action` | the owner's approved final C3 score |
| `c3_incident` | `what`, `by` | a charge or push |
| `can_do` | `item`, `done` | handling milestones |
| `sale` | `to`, `price`, `what` | |
| `death` | `what` | |

On the place (`OP001`):

| kind | data | notes |
|---|---|---|
| `feeding` | `module`, `feed`, `feed_key`, `amount_lb`, `bales`, `bale` (`round`/`square`), `bale_lb`, `hay_method`, `waste_pct`, `lot`, `note` | what actually went out, per feeding |
| `hay_lot`, `feed_lot` | `id`, `feed_key`, `bales`/`bags`, `price`, `price_unit`, `bought_on`, `from`, `test`/`tag` | purchases |
| `settings` | per `module`: `feeds` (ticked feeds), `tier`, `hay`, `standard`, … | the feed plan's settings |
| `module` | `key`, `label`, `animal_type`, `use`, switches | the place's modules |
| `operation` | `name` | the place's name |
| `breeding_season` | bull in/out dates, females | |
| `person`, `contact`, `home_layout`, `herd_columns`, `filters`, `name_style`, `setup`, `backup_target`, `days_out`, `celebrate` | | app plumbing — rarely useful; **never show `person` PINs or others' `contact`** |

Gestation used by the app: cattle 283 days (279–287), horses 338 days
(320–370). A due date = breeding date + gestation.

## Good answers

- Lead with the answer, then one line of working, then anything unknown.
- Name animals by name (the `name` column in `herd.py`; unnamed calves are
  "DAM's YEAR calf").
- A chart or a small table is welcome when the question is a trend — produce it
  however your tools allow (a CSV the person can open, a simple chart).
- Money, weights and dates in the person's own terms: pounds, dollars, "12 Apr".
- If the question needs something the records do not hold, say what would need
  recording in the app to answer it next time.
