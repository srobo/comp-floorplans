#!/usr/bin/env python3

import re
import json
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from contextlib import suppress

import yaml


def register_xml_namespaces(xml_file):
    with open(xml_file, 'r') as file:
        ns = dict([node for _, node in ET.iterparse(file, events=['start-ns'])])

    for prefix in ns:
        ET.register_namespace(prefix, ns[prefix])

    return ns


def load_config(conf_file):
    try:
        with open(conf_file, 'r') as file:
            conf = json.load(file)  # load json specification
    except json.JSONDecodeError:
        print(f"Failed to read {conf_file} as JSON, trying YAML")
        with open(conf_file, 'r') as file:
            conf = yaml.safe_load(file)  # load yaml specification

    return conf


def print_layers(
    root, show=[], hide=[],
    ns={
        'svg': 'http://www.w3.org/2000/svg',
        'inkscape': 'http://www.inkscape.org/namespaces/inkscape'
    },
    prefix="", autoshow=False
):
    if prefix:
        prefix += '/'

    for child in root.findall('./svg:g[@inkscape:groupmode="layer"]', ns):
        label = prefix + child.get(f'{{{ns["inkscape"]}}}label', "")

        if autoshow:
            if label in hide:
                child.set('style', 'display:none')
                print(f'Hide: {label}')
            else:
                child.attrib.pop('style', None)
                print(f'Show: {label}')
        else:
            if label in hide:
                child.set('style', 'display:none')
                print(f'Hide: {label}')
            elif label in show or 'ALL' in show:
                child.attrib.pop('style', None)
                print(f'Show: {label}')
                child = print_layers(child, show, hide, ns, prefix=label, autoshow=True)
            else:
                child.set('style', 'display:none')
                print(f'Hide: {label}')

    return root


def set_titles(root, title, version, scale, ns):
    with suppress(IndexError, AttributeError, TypeError):
        root.find('.//svg:text[svg:tspan="{{title}}"]', ns)[0].text = title
    with suppress(IndexError, AttributeError, TypeError):
        root.find('.//svg:text[svg:tspan="{{version}}"]', ns)[0].text = f"Version: {version}"
    with suppress(IndexError, AttributeError, TypeError):
        root.find('.//svg:text[svg:tspan="{{scale}}" ]', ns)[0].text = f"Scale 1:{scale:.0f}"

    return root


def insert_tlas(svg_root, teams, ns):
    TLA = svg_root.find('svg:g[@inkscape:label="TLA"]', ns)  # add team names
    if TLA:
        for team in TLA.findall('.//svg:text/svg:tspan', ns):
            team_no = re.search(r'@T_(\d+)', team.text)
            if team_no is not None:
                team.text = teams.get(int(team_no[1]), '')

    return svg_root


def embed_svg(embedded, root, ns, template_dir, team_names=None):
    print(f"Embedding {embedded['image']}")
    embedded_root = ET.parse(Path(template_dir) / embedded['image']).getroot()  # load svg

    if team_names is not None:
        embedded_root = insert_tlas(embedded_root, team_names, ns)

    # display only selected layers or ALL
    embedded_root = print_layers(
        embedded_root,
        embedded.get('show', ['ALL']),
        embedded.get('hide', []),
        ns=ns,
    )

    embed_marker = embedded['marker']
    # get container that we will be inserting into
    embed_parent = root.find(f'.//svg:rect[@id="{embed_marker}"]/..', ns)
    if embed_parent is None:
        print(f"Failed to find the marker {embed_marker}")
        return

    # get the element that will be replaced by the embed
    embed_child = embed_parent.find(f'./svg:rect[@id="{embed_marker}"]', ns)
    if embed_child is None:
        print(f"Failed to find the marker {embed_marker}")
        return

    embed_index = list(embed_parent).index(embed_child)

    for field in ['x', 'y', 'width', 'height']:  # set x, y, height & width from the placeholder
        embedded_root.set(field, embed_child.get(field))

    embed_parent[embed_index] = embedded_root  # replace element with svg
    print(f"Embedded {embedded['image']}")
    return root


def generate_svg(spec_path, template_dir, out_dir, base_scale, teams_file=None):
    team_names = None
    spec = load_config(spec_path)

    svg_file = Path(template_dir) / spec['image']
    ns = register_xml_namespaces(svg_file)

    root_tree = ET.parse(svg_file)  # load svg
    root = root_tree.getroot()

    root = set_titles(
        root,
        spec.get('title', spec['image']),
        spec.get('version', 0.1),
        spec.get('scale', 1) * base_scale,
        ns,
    )

    if teams_file:
        team_names = load_config(teams_file)
        root = insert_tlas(root, team_names, ns)

    # set scale
    try:
        old_width = float(root.get('width')[:-2])
        old_height = float(root.get('height')[:-2])
    except TypeError:
        print("Invalid SVG")

    scale = spec.get('scale', 1)
    root.set('width', str(old_width / scale) + "cm")
    root.set('height', str(old_height / scale) + "cm")

    # display only selected layers or ALL
    print_layers(root, spec.get('show', ['ALL']), spec.get('hide', []), ns=ns)

    for embedded in spec.get('embed', []):  # add nested svgs (including key)
        root = embed_svg(embedded, root, ns, template_dir, team_names)

    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True)

    out_file = spec.get('title', 'output').replace(' ', '_') + '.svg'
    root_tree.write(out_dir / out_file, xml_declaration=True, encoding='UTF-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('specs', type=Path, nargs=argparse.OPTIONAL, default=Path('layouts/'), help=(
        "Folder or file containing the YAML/JSON that defines what output SVG's are created, "
        "defaults to '%(default)s'"
    ))
    parser.add_argument('-s', '--base-scale', type=int, default=100, help=(
        "The initial 1:X scale that the template files are at, defaults to %(default)s"
    ))
    parser.add_argument('-t', '--templates', type=Path, default=Path('templates/'), help=(
        "Folder containing the template SVG's, defaults to '%(default)s'"
    ))
    parser.add_argument('--teams', type=Path, default=Path('team_names.yaml'), help=(
        "The YAML/JSON file containing a mapping of number to TLA, "
        "defaults to '%(default)s'"
    ))
    parser.add_argument('-o', '--output', type=Path, default=Path('output/'), help=(
        "Folder to store the output SVG's, defaults to '%(default)s'"
    ))

    args = parser.parse_args()

    if args.specs.is_file():
        generate_svg(args.specs, args.templates, args.output, args.base_scale, teams_file=args.teams)
    elif args.specs.is_dir():
        for spec in args.specs.iterdir():
            if not spec.is_file():
                continue

            print(f"Processing spec file {spec}")
            generate_svg(spec, args.templates, args.output, args.base_scale, teams_file=args.teams)
    else:
        print("The specification is neither a file nor directory")


if __name__ == "__main__":
    main()
