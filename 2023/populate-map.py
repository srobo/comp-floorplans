#!/usr/bin/env python3
import re
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

from generate_svg import load_config, register_xml_namespaces


def insert_tla_list(svg_root, teams, ns):
    # Sort teams so the list is alphabetical by TLA
    teams_alphabetical = sorted(teams.items(), key=lambda x: x[1])
    teams_alphabetical = (
        (idx, tla) for idx, tla in teams_alphabetical
        if tla != '—'  # remove unused pits, represented with an em dash
    )
    team_dict = dict(enumerate(teams_alphabetical, start=1))

    TLA = svg_root.find('svg:g[@inkscape:label="TLA"]', ns)  # add team names
    if TLA:
        for team in TLA.findall('.//svg:text/svg:tspan', ns):
            if team.text is None:
                continue
            team_no = re.search(r'@t_(\d+)', team.text)
            if team_no is not None:
                tla_data = team_dict.get(int(team_no[1]))
                team.text = f"{tla_data[1]}:" if tla_data is not None else ""
            else:
                idx_no = re.search(r'@I_(\d+)', team.text)
                if idx_no is not None:
                    tla_data = team_dict.get(int(idx_no[1]))
                    team.text = str(tla_data[0]) if tla_data is not None else ""

    return svg_root


def generate_map_svg(svg_file, out_file, teams_file=None):
    ns = register_xml_namespaces(svg_file)

    root_tree = ET.parse(svg_file)  # load svg
    root = root_tree.getroot()

    if teams_file:
        team_names = load_config(teams_file)
        insert_tla_list(root, team_names, ns)

    root_tree.write(Path(out_file), xml_declaration=True, encoding='UTF-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--map', type=Path, default=Path('templates/map.svg'), help=(
        "The template map SVG, defaults to '%(default)s'"
    ))
    parser.add_argument('--teams', type=Path, default=Path('team_names.yaml'), help=(
        "The YAML/JSON file containing a mapping of number to TLA"
    ))
    parser.add_argument('-o', '--output', type=Path, default=Path('output/map-with-teams.svg'), help=(
        "Filepath of the output SVG, defaults to '%(default)s'"
    ))

    args = parser.parse_args()

    generate_map_svg(args.map, args.output, teams_file=args.teams)


if __name__ == "__main__":
    main()
