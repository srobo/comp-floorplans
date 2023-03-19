#!/usr/bin/env python3

import os
from pathlib import Path

TEAMS_DOC = 'https://docs.google.com/spreadsheets/d/1ADDD-7LmkiChD4_lqH-k6sRnLCwpC8_rydY6PY8qQQo/edit#gid=753416033'

DIR = Path(__file__).parent
MAP_FILE = DIR / Path('map.svg')
OUTPUT_FILE = DIR / Path('map-with-teams.svg')


def eof_name() -> str:
    if os.name == 'nt':
        return 'Ctrl+Z'
    return 'Ctrl+D'


print(f"Paste the entire TLA column of {TEAMS_DOC} then press {eof_name()}")

lines = []
while True:
    try:
        lines.append(input(""))
    except EOFError:
        break

if ['TLA'] == lines[:1]:
    lines.pop(0)

if not lines:
    exit("No teams found")

content = MAP_FILE.read_text()

for idx, name in enumerate(lines, start=1):
    name = name.strip()

    if name in ('', '#N/A'):
        name = '—'

    content = content.replace(f'>{idx}<', f'>{name}<')

OUTPUT_FILE.write_text(content)
