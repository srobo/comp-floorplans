#!/usr/bin/env python3

import os
from pathlib import Path

import yaml

DIR = Path(__file__).parent

MAP_FILE = DIR / 'map.svg'
TEAMS_FILE = DIR / 'team_names.yaml'

OUTPUT_FILE = DIR / 'output/map-with-teams.svg'

with TEAMS_FILE.open() as f:
    teams: dict[str, str] = yaml.safe_load(f)

content = MAP_FILE.read_text()

for idx, name in teams.items():
    name = name.strip()

    if not name:
        name = '—'

    content = content.replace(f'>{idx}<', f'>{name}<')

OUTPUT_FILE.parent.mkdir(exist_ok=True, parents=True)
OUTPUT_FILE.write_text(content)
