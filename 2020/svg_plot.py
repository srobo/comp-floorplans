#!/usr/bin/env python3

# MIT License

# Copyright (c) 2020 William Barber

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

version = 1.2

import xml.etree.ElementTree as ET
import os
import re
from math import sin, cos, radians, atan2, degrees
import argparse

parser = argparse.ArgumentParser(description="create SVG paths from the command line") 
# key_map
parser.add_argument('-i','--input',help='The file to read in a previous SVG from')
parser.add_argument('-o','--output',help='The file to store the output svg in, this is required',required=True)
parser.add_argument('-s','--scale',help='Set the scale value used for distances in commands')
parser.add_argument('-l','--layer',help='Layer to place the path on, delimited by /')
parser.add_argument('-S','--svg-scale',type=float, default=0.005, # 1cm on diagram is 1m real life if not scaled
  help='Point values are equal to meters, this sets the conversion for the output vector size')
parser.add_argument('-x',type=float,help='x-coordinate to start at, specify with -y to apply. In svg coordinates')
parser.add_argument('-y',type=float,help='y-coordinate to start at, specify with -x to apply. In svg coordinates')
parser.add_argument('-a','--append',type=str,dest="path",help='ID of path to append')
parser.add_argument('--log',type=str,help='Log file for executed commands')
parser.add_argument('args', nargs='*', help='A list of commands to run non-interactively')
parser.add_argument('--version', action='version', version='%(prog)s {}'.format(version))
arg_list = parser.parse_args()

key_map = {
  'north': 'w',
  'east': 'd',
  'south': 's',
  'west': 'a',
  'undo': 'z',
  'quit': 'q',
  'help': 'h?',
  'save': 'e',
  'print': 'p',
  'move': 'm', # only single char here
  'curve': 'c',
  'angle': 'r' # only single char here
}
end_pos=[0,0]

# produced vector is 1 point per m, this sets the relationship between viewbox and height/width
output_scale=arg_list.svg_scale

def valid_num(num: str) -> bool:
  try:
    float(num)
  except ValueError:
    return False
  return True

def cmd_list():
  print(' {}<n>  add upward segment of length n'.format(key_map['north'][0]))
  print(' {}<n>  add rightward segment of length n'.format(key_map['east'][0]))
  print(' {}<n>  add downward segment of length n'.format(key_map['south'][0]))
  print(' {}<n>  add leftward segment of length n'.format(key_map['west'][0]))
  print(' <m>{}<n>  add a segment of length n at angle m'.format(key_map['angle'][0]))
  print(' <m>{}<n>  move at angle m for length n '.format(key_map['move'][0]))
  print(' {}<n>,<m> add curve of radius n and relative angle m'.format(key_map['curve'][0]))
  print(' {}     print the current location in svg coordinates'.format(key_map['print'][0]))
  print(' {}     undo last segment'.format(key_map['undo'][0]))
  print(' {}     show help message'.format(key_map['help'][0]))
  print(' {}     save'.format(key_map['save'][0]))
  print(' {}     save and quit'.format(key_map['quit'][0]))

def calc_path_data(path):
  pos = [0,0]
  last_move = [0,0]
  angle = 0
  segments = re.findall(r'[A-Za-z][0-9.,\s-]*',path)
  for segment in segments:
    params = re.split(r'[\s,]',segment)
    try:
      if segment[0] == 'M':
        pos = [float(params[1]),float(params[2])]
        last_move = pos
        angle = 0
      if segment[0] == 'm':
        pos[0] += float(params[1])
        pos[1] += float(params[2])
        last_move = pos
        angle = 0
      if segment[0] == 'L':
        angle = degrees(-90-atan2(-(float(params[2])-pos[1]),float(params[1])-pos[0]))
        pos = [float(params[1]),float(params[2])]
      if segment[0] == 'l':
        angle = degrees(-90-atan2(float(params[2]),float(params[1])))
        pos[0] += float(params[1])
        pos[1] += float(params[2])
      if segment[0] == 'H':
        angle = 90 if (float(params[1])-pos[0]) >=0 else -90
        pos[0] = float(params[1])
      if segment[0] == 'h':
        angle = 90 if float(params[1]) >=0 else -90
        pos[0] += float(params[1])
      if segment[0] == 'V':
        pos[1] = float(params[1])
        angle = 180 if (float(params[1])-pos[1]) >=0 else 0
      if segment[0] == 'v':
        pos[1] += float(params[1])
        angle = 180 if float(params[1]) >=0 else 0
      if segment[0] in [ 'C','S','Q','T','A' ]:
        pos_str = params[-2:]
        pos = [float(pos_str[0]),float(pos_str[1])]
        angle = 0
      if segment[0] in [ 'c','s','q','t','a' ]:
        pos[0] += float(params[1])
        pos[1] += float(params[2])
        angle = 0
      if segment[0] in [ 'Z','z' ]:
        angle = degrees(-90-atan2(last_move[1]-pos[1],last_move[0]-pos[0]))
        pos = last_move
    except IndexError:
      pass
  return pos, angle

def process_command(root: ET.Element, new_path: ET.Element,cmd: str, scale: float, log=None) -> bool:
  global end_pos

  if len(cmd) == 0:
    return True
  elif not cmd[0].isalpha(): # first char isn't a letter
    if key_map['angle'][0] in cmd:
      args = cmd.split(key_map['angle'][0]) # split on char
    elif key_map['move'][0] in cmd:
      args = cmd.split(key_map['move'][0]) # split on char
    # arg 1 = degrees, arg 2 = length
    if len(args) == 2 and valid_num(args[0]) and valid_num(args[1]):
      args = [float(x) for x in args]
      # calc end pos from direction, length, last pos
      change_x = scale * args[1] * sin(radians(args[0]))
      change_y = scale * args[1] * cos(radians(args[0]))
      end_pos = [end_pos[0] + change_x, end_pos[1] - change_y ]
      if key_map['angle'][0] in cmd:
        new_path.attrib['d'] += "L {0[0]} {0[1]} ".format(end_pos) # append path
      elif key_map['move'][0] in cmd:
        new_path.attrib['d'] += "M {0[0]} {0[1]} ".format(end_pos) # append path
    else:
      print('invalid command')
      return True
  elif cmd[0] in key_map['quit']:
    if log:
      log.write(cmd+'\n')
    return False
  elif cmd[0] in key_map['undo']:
    try: # remove last segment of path
      new_path.attrib['d'] = re.match(r'(.*)([MLHVCSQTAZmlhvcsqtaz][ 0-9.,-]*)$',new_path.attrib['d'])[1]
      end_pos =  calc_path_data(new_path.attrib['d'])[0] # reset last pos
    except TypeError:
      print('Nothing to undo, start position cannot be changed')
      if input('Would you like to exit without saving?').lower() in ['y','yes']:
        os.remove(tmp_name) # remove tmp file
        exit(0)
  elif cmd[0] in key_map['help']:
    cmd_list()
  elif cmd[0] in key_map['print']:
    print('{}, {}'.format(end_pos[0],end_pos[1]))
  elif cmd[0] in key_map['save']:
    ET.ElementTree(root).write(svg_name,xml_declaration=True,encoding='UTF-8') # save svg
    if log:
      log.write(cmd+'\n')
    return True
  elif cmd[0] in key_map['curve']:
    # 1=radius, 2=rel angle (+ is right, - is left)
    args = cmd[1:].split(',')
    if len(args) == 2 and valid_num(args[0]) and valid_num(args[1]):
      args = [float(x) for x in args]
      # calculate path angle
      angle = calc_path_data(new_path.attrib['d'])[1]

      change_x_ctl = scale * args[0] * sin(radians(angle))
      change_y_ctl = scale * args[0] * cos(radians(angle))
      pos_ctl = [end_pos[0] + change_x_ctl, end_pos[1] - change_y_ctl ]

      change_x_fin = scale * args[0] * sin(radians(angle+args[1]))
      change_y_fin = scale * args[0] * cos(radians(angle+args[1]))
      pos_fin = [pos_ctl[0] + change_x_fin, pos_ctl[1] - change_y_fin ]

      new_path.attrib['d'] += "Q {0[0]} {0[1]} {1[0]} {1[1]} ".format(pos_ctl,pos_fin) # append path
      end_pos = pos_fin
    else:
      print('invalid command')
      return True
  else:
    try:
      length = float(cmd[1:])*scale # rest of string = length
    except ValueError:
      print('invalid command')
      return True
    if cmd[0] in key_map['north']: # convert char into direction
      end_pos[1] -= length # calc end pos from direction, length, last pos
      new_path.attrib['d'] += "V {} ".format(end_pos[1]) # append path
    elif cmd[0] in key_map['east']:
      end_pos[0] += length # calc end pos from direction, length, last pos
      new_path.attrib['d'] += "H {} ".format(end_pos[0]) # append path
    elif cmd[0] in key_map['south']:
      end_pos[1] += length # calc end pos from direction, length, last pos
      new_path.attrib['d'] += "V {} ".format(end_pos[1]) # append path
    elif cmd[0] in key_map['west']:
      end_pos[0] -= length # calc end pos from direction, length, last pos
      new_path.attrib['d'] += "H {} ".format(end_pos[0]) # append path
    else:
      print('invalid command')
      return True
  viewbox = [ float(x) for x in root.attrib['viewBox'].split()] # keep path inside viewBox
  if end_pos[0] <= viewbox[0]:
    viewbox[2] +=  viewbox[0]-(end_pos[0]-1)
    viewbox[0] = end_pos[0]-1
  if end_pos[1] <= viewbox[1]:
    viewbox[3] += viewbox[1]-(end_pos[1]-1)
    viewbox[1] = end_pos[1]-1
  if end_pos[0] >= viewbox[2]: viewbox[2] = end_pos[0]+1-viewbox[0]
  if end_pos[1] >= viewbox[3]: viewbox[3] = end_pos[1]+1-viewbox[1]
  root.attrib['viewBox'] = ' '.join([ str(x) for x in viewbox])
  # update size values
  root.attrib['height'] = '{}cm'.format((viewbox[3]-viewbox[1])*100*output_scale)
  root.attrib['width'] = '{}cm'.format((viewbox[2]-viewbox[0])*100*output_scale)
  if log:
    log.write(cmd+'\n')
  return True

if arg_list.input:
  with open(arg_list.input,'r') as file:
    ns = dict([ node for _, node in ET.iterparse(file,events=['start-ns'])])
  for prefix in ns:
    ET.register_namespace(prefix,ns[prefix])
  ET.register_namespace('','http://www.w3.org/2000/svg')
  root = ET.parse(arg_list.input).getroot() # load svg
else:
  base_svg = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <svg
      xmlns:svg="http://www.w3.org/2000/svg"
      xmlns="http://www.w3.org/2000/svg"
      xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
      width="1cm"
      height="1cm"
      viewBox="0 0 10 10">
    </svg>
  """
  ns = {
    '': 'http://www.w3.org/2000/svg',
    'svg': 'http://www.w3.org/2000/svg',
    'inkscape': 'http://www.inkscape.org/namespaces/inkscape'
  }
  for prefix in ns:
    ET.register_namespace(prefix,ns[prefix])
  ET.register_namespace('','http://www.w3.org/2000/svg')
  root = ET.fromstring(base_svg) # generate base svg

svg_name = arg_list.output # set svg name
tmp_name = 'svg_tmp'+'.html' # gen temp svg name

if not arg_list.args:
  preview_wrapper = '<!DOCTYPE html><html><meta http-equiv="refresh" content="2"/><style>svg {display:block; position:fixed;top:0; left:0; width:100%; height:100%;}</style></html>'
  preview_vector = ET.fromstring(preview_wrapper) # wrap in html autoload tags
  preview_vector.append(root)
  ET.ElementTree(preview_vector).write(tmp_name,method='html') # output to temp file
  print('live preview available at {}, please open this file in a browser'.format(tmp_name)) # open in browser
  ## non-portable, tends to steal focus
  # import webbrowser
  # webbrowser.open('file://'+os.getcwd()+'/'+tmp_name,new=2,autoraise=False)

log = None
try:
  if arg_list.scale:
    scale_segments = arg_list.scale.split('/')
    if valid_num(arg_list.scale):
      dist_scale = float(arg_list.scale)
      units_scale = 1
    elif len(scale_segments) == 2 and valid_num(scale_segments[0]) and valid_num(scale_segments[1]):
      dist_scale = float(scale_segments[0])
      units_scale = float(scale_segments[1])
    else:
      print('Invalid scale format')
      if not arg_list.args:
        os.remove(tmp_name) # remove tmp file
      exit(1)

  else:
    units_scale = float(input('Set the measured distance for scale: ')) # get scale units
    dist_scale = float(input('Set the actual distance for scale: ')) # get scale distance
  scale = dist_scale/units_scale

  if arg_list.layer:
    layer_path = arg_list.layer
  else:
    layer_path = input('Enter layer path, use / as the delimiter: ') # get layer
  layer_root = root
  for layer_frag in layer_path.split('/'): # locate layer in tree or add it
    if layer_frag == '': continue
    next_layer = layer_root.find('./g[@inkscape:groupmode="layer"][@inkscape:label="{}"]'.format(layer_frag), ns)
    if next_layer is None:
      new_layer = ET.SubElement(layer_root, 'g', {'{http://www.inkscape.org/namespaces/inkscape}groupmode': "layer",
      "{http://www.inkscape.org/namespaces/inkscape}label": layer_frag, 'style': "display:inline"}) # add layer
      layer_root = new_layer
    else:
      layer_root = next_layer
  if arg_list.path:
    active_path = layer_root.find('./path[@id="{}"]'.format(arg_list.path), ns)
    if active_path is None:
      if arg_list.x and arg_list.y:
        end_pos=[arg_list.x, arg_list.y]
      else:
        start_pos = input('Enter start position (x,y): ') # get start pos
        end_pos = start_pos.split(',')
      if len(end_pos) == 2 and valid_num(end_pos[0]): # and valid_num(end_pos[1]):
        end_pos = [float(x) for x in end_pos]
      else:
        print('Invalid coordinates')
        exit(2)
      new_path = ET.SubElement(layer_root, 'path',{
        'style': "fill:none;stroke:#000000;stroke-width:0.5;stroke-linecap:butt;stroke-linejoin:butt;",
        'd': "M {0[0]},{0[1]} ".format(end_pos)
      }) # start path
      if arg_list.path:
        new_path.attrib['{http://www.inkscape.org/namespaces/inkscape}label'] = arg_list.path
    else:
      new_path = active_path
      active_path.attrib['d'] += ' '
      end_pos = calc_path_data(active_path.attrib['d'])[0]
  layer_root.append(ET.Comment('Scaling values used {}/{} Scale factor = {}'.format(dist_scale,units_scale,scale)))
  if arg_list.log:
    log = open(arg_list.log,'a')
  if arg_list.args:
    for cmd in arg_list.args:
      if not process_command(root, new_path, cmd, scale, log):
        break
  else:
    print('type h for help')
    while 1:
      cmd = input('cmd> ') # read in next direction and length
      if not process_command(root, new_path, cmd, scale, log):
        break
      preview_vector = ET.fromstring(preview_wrapper) # wrap in html autoload tags
      preview_vector.append(root)
      ET.ElementTree(preview_vector).write(tmp_name,method='html') # output to temp file
  if log:
    log.close()
except KeyboardInterrupt:
  if log:
    log.close()
  ans = input('Would you like to save before exiting? (y/n)').lower()
  if ans in ['n','no']:
    os.remove(tmp_name) # remove tmp file
    exit(0)
ET.ElementTree(root).write(svg_name,xml_declaration=True,encoding='UTF-8') # save svg
if not arg_list.args:
  os.remove(tmp_name) # remove tmp file