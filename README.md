# The Passport Page of a Country That Isn't There

[![make.fun bounty](https://img.shields.io/badge/make.fun-bounty-7c3aed)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Entry for the [make.fun bounty "The Passport Page of a Country That Isn't There"](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318) ($50, 20 places paid).

Play code: `makefun-slipper-jam-mitten`

## What it does

`main.py` draws, entirely in code with Pillow, a 1024×1024 passport spread
for the invented country **The Free State of Aerthys** — a lighthouse nation
that does not exist:

- **Left page — data page:** holder MARA SELIN VOSS, passport
  AE-2026-0117, issued 12 FEB 2024, valid to 12 FEB 2034, with a drawn
  portrait (silhouette against a lighthouse sky, no real person's photo)
  and a machine-readable zone with ICAO check digits.
- **Right page — visas and endorsements:** a visitor-visa sticker showing
  the Lighthouse Levy (paid, 40 AUR) and its condition — the bearer shall
  tend one lamp — plus arrival and departure stamps from neighbouring
  countries (Kestrel Republic, Vostra, Isle of Echoes), all dated after
  the passport was issued, and the observation that the holder is a
  certified lamp-keeper, grade II.

No external assets, no network, no randomness: running the program twice
produces the same PNG bytes.

## Run it

```sh
python3 main.py   # writes /output/entry.png (1024x1024, < 1 MiB)
```

Requires Pillow (`pip install pillow`).
