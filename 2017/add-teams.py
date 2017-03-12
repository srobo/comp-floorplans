#!/usr/bin/env python

from __future__ import print_function

import re
import sys

def get_teams(file_name):
    with open(file_name) as teams_file:
        lines = teams_file.readlines()
        teams = []
        for l in lines:
            val = l.split('#', 1)[0].strip()
            if val:
                teams.append(val)
        return teams

if len(sys.argv) != 2:
    exit("Usage: add-teams.py SVG_FILE")

source_name = sys.argv[1]
target_name = source_name + '-with-teams.svg'

with open(source_name, 'r') as src:
    template = src.read()

teams = get_teams('teams.txt')

def get_team(match):
    global teams
    num = int(match.group(1))
    try:
        return teams[num]
    except IndexError:
        print("Failed to get team with index '{0}'.".format(num), file=sys.stderr)
        return ''

replaced = re.sub(r'@T_(\d+)', get_team, template)

with open(target_name, 'w') as tgt:
    tgt.write(replaced)
