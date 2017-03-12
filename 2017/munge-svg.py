#!/usr/bin/env python

from __future__ import print_function

import re
import sys
import argparse
import lxml.etree as ET

def get_args():
    parser = argparse.ArgumentParser("Munge an SVG into a useful form",
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                    fromfile_prefix_chars='@')
    parser.add_argument("svg", help="Input SVG to be munged")
    parser.add_argument("--teams", default="teams.txt",
                        help="List of teams to map onto pits")
    parser.add_argument("--show-layers", nargs="+", default=["ALL"],
                        help="Show only these layers. 'ALL' is special and shows all layers")
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
        template = self.select_layers(src.read())
        replaced = re.sub(r'@T_(\d+)', lambda x: self.get_team(x), template)
        dst.write(replaced)

    def select_layers(self, svg):
        root = ET.fromstring(svg)
        for layer in root.findall(".//svg:g[@inkscape:label]", root.nsmap):
            label_attrib = "{{{0}}}label".format(root.nsmap["inkscape"])
            if "ALL" in self.layers or layer.attrib[label_attrib] in self.layers:
                layer.attrib["style"] = "display:inline"
            else:
                layer.attrib["style"] = "display:none"
        return ET.tostring(root)

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
