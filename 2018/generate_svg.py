#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import yaml
import json
import sys
import re
import os

spec = {}

def printLayers(root, show=[], hide=[], ns={'svg': 'http://www.w3.org/2000/svg','inkscape': 'http://www.inkscape.org/namespaces/inkscape'}, prefix="", autoshow=False):
  if prefix:
    prefix += '/'
  for child in root.findall('./svg:g[@inkscape:groupmode="layer"]', ns):
    label = prefix + child.get(f'{{{ns["inkscape"]}}}label',"")
    if autoshow:
      if label in hide:
        child.set('style','display:none')
        print('Hide: ' + label)
      else:
        child.attrib.pop('style',None)
        print('Show: ' + label)
    else:
      if label in hide:
        child.set('style','display:none')
        print('Hide: ' + label)
      elif label in show or 'ALL' in show:
        child.attrib.pop('style',None)
        print('Show: ' + label)
        printLayers(child, show, hide, ns, prefix=label, autoshow=True)
      else:
        child.set('style','display:none')
        print('Hide: ' + label)

if len(sys.argv) != 2:
  print('Usage: ' + sys.argv[0] + " <specification-file>")
  exit(1)

try:
  with open('layouts/' + sys.argv[1],'r') as file:
    spec = json.load(file) # load json specification
    print('Using json')
except json.JSONDecodeError:
  with open('layouts/' + sys.argv[1],'r') as file:
    print('Using yaml')
    spec = yaml.load(file) # load yaml specification

with open('templates/' + spec['image'],'r') as file:
  ns = dict([ node for _, node in ET.iterparse(file,events=['start-ns'])])

for prefix in ns:
  ET.register_namespace(prefix,ns[prefix])

root_tree = ET.parse('templates/' + spec['image']) # load svg
root = root_tree.getroot()


try: # set title and version
  root.find('.//svg:text[svg:tspan="{{title}}"]', ns)[0].text = spec.get('title',spec['image'])
  root.find('.//svg:text[svg:tspan="{{version}}"]', ns)[0].text = "Version: " + spec.get('version','0.1')
  root.find('.//svg:text[svg:tspan="{{scale}}" ]', ns)[0].text = "Scale 1:" + str(spec.get('scale',1))
except (IndexError,AttributeError,TypeError):
  pass

with open('team_names.txt','r') as file:
  team_names = yaml.load(file)

TLA = root.find('svg:g[@inkscape:label="TLA"]',ns) # add team names
if TLA:
  for team in TLA.findall('.//svg:text/svg:tspan',ns):
    team_no = re.search(r'@T_(\d+)',team.text)
    if team_no:
      team.text = team_names.get(int(team_no[1]),'')

# set scale
old_width = root.get('width')[:-2]
old_height = root.get('height')[:-2]
root.set('width',str(float(old_width)/spec.get('scale',1)) + "cm")
root.set('height',str(float(old_height)/spec.get('scale',1)) + "cm")

printLayers(root,spec.get('show',['ALL']),spec.get('hide',[]),ns=ns) # display only selected layers or ALL

for embedded in spec.get('embed',[]): # add nested svgs (including key)
  print(embedded['image'] + ':')
  embedded_root = ET.parse('templates/' + embedded['image']).getroot() # load svg
  
  TLA = root.find('svg:g[@inkscape:label="TLA"]',ns) # add team names
  if TLA:
    for team in TLA.findall('.//svg:text/svg:tspan',ns):
      team_no = re.search(r'@T_(\d+)',team.text)
      if team_no:
        team.text = team_names.get(int(team_no[1]),'')
  
  printLayers(embedded_root,embedded.get('show',['ALL']),embedded.get('hide',[]),ns=ns) # display only selected layers or ALL
  
  # add scaled at marker
  embed_parent = root.find('.//svg:rect[@id="{}"]/..'.format(embedded['marker']), ns) # search for marker in id
  if embed_parent is None:
    print('Failed to insert ' + embedded['image'] + ' at ' + embedded['marker'])
    continue # exit(2)
  embed_child = embed_parent.find('./svg:rect[@id="{}"]'.format(embedded['marker']), ns)
  embed_index = list(embed_parent).index(embed_child)
  embedded_root.set('x',embed_child.get('x')) # set x, y, height & width from marker
  embedded_root.set('y',embed_child.get('y'))
  embedded_root.set('width',embed_child.get('width'))
  embedded_root.set('height',embed_child.get('height'))
  embed_parent[embed_index] = embedded_root # replace element with svg

if not os.path.exists('output'):
    os.mkdir('output')

root_tree.write('output/' + re.sub(r'\s+','_',spec.get('title','output')) + '.svg',xml_declaration=True,encoding='UTF-8') # save to output
