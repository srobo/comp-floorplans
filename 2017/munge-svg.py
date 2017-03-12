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
    parser.add_argument("--output", default="-",
                        help="Output file. Use - for stdout")
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

class SVGMunger(object):
    def __init__(self, teams, layers):
        self.teams = teams
        self.layers = layers

    def munge(self, src, dst):
        template = src.read()
        replaced = re.sub(r'@T_(\d+)', lambda x: self.get_team(x), template)
        dst.write(replaced)

    def get_team(self, match):
        num = int(match.group(1))
        try:
            return self.teams[num]
        except IndexError:
            print("Failed to get team with index '{0}'.".format(num), file=sys.stderr)
            return ''

if __name__ == "__main__":
    args = get_args()

    munger = SVGMunger(get_teams(args.teams), args.show_layers)
    with open(args.svg, 'r') as src:
        dst = sys.stdout if args.output == "-" else open(args.output, 'w')
        munger.munge(src, dst)
        dst.close()

