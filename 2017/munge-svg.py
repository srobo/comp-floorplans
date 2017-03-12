#!/usr/bin/env python

from __future__ import print_function

import re
import sys
import argparse

def get_args():
    parser = argparse.ArgumentParser("Munge an SVG into a useful form",
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("svg", help="Input SVG to be munged")
    parser.add_argument("--teams", default="teams.txt",
                        help="List of teams to map onto pits")
    parser.add_argument("--show-layers", nargs="+", default=["Layout"],
                        help="Show only these layers")
    return parser.parse_args()

def get_teams(file_name):
    with open(file_name) as teams_file:
        lines = teams_file.readlines()
        teams = []
        for l in lines:
            val = l.split('#', 1)[0].strip()
            if val:
                teams.append(val)
        return teams

args = get_args()
source_name = args.svg
target_name = source_name + '-with-teams.svg'

with open(source_name, 'r') as src:
    template = src.read()

teams = get_teams(args.teams)

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
