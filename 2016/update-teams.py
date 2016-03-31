#!/usr/bin/env python

"""
Update the teams.txt based on a teams.json from srweb.

When adding teams, those who were on the ground floor last year are
moved to the top floor. Other teams keep their relative position in
the list, though this means they may still move if teams are added
above them.
"""

from __future__ import print_function

import json
import os.path
import sys

GROUND_FLOOR_CAPACITY = 22

USAGE = "Usage: update-teams.py TEAMS_JSON"

if len(sys.argv) != 2:
    exit(USAGE)

if sys.argv[1] in ('-h', '--help'):
    exit(USAGE + "\n" + __doc__)

teams_json = sys.argv[1]
mydir = os.path.dirname(__file__)
ground_floor_last_year_txt = os.path.join(mydir, 'gfly.txt')
teams_txt = os.path.join(mydir, 'teams.txt')

with open(teams_json, 'r') as tjf:
    teams = json.load(tjf)
    tlas = teams.keys()

with open(teams_txt, 'r') as ttf:
    current_teams = ttf.read().split()

with open(ground_floor_last_year_txt, 'r') as gflytf:
    gfly_tlas = gflytf.read().split()

def tla_key(tla):
    global gfly_tlas, current_teams

    try:
        curr_idx = current_teams.index(tla)
    except:
        # new teams go on the end
        curr_idx = len(current_teams)

    return (tla in gfly_tlas, curr_idx)

tlas.sort(key = tla_key)

with open(teams_txt, 'w') as ttf:
    print("# Ground Floor\n", file=ttf)
    print("\n".join(tlas[:GROUND_FLOOR_CAPACITY]), file=ttf)
    print("\n# Second Floor\n", file=ttf)
    print("\n".join(tlas[GROUND_FLOOR_CAPACITY:]), file=ttf)
