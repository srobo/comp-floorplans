# Notes for 2019

The templates here are intended to be 100:1 scale diagrams of the areas used at Reading Union, they are believed to be within 5% accurate.

The raw layout diagrams containing all the layers are in the `templates/` directory.
The yaml/json files in the `layouts/` directory specify visible layers, scaling and labels to apply to the produced output images.



## Layers
#### Floorplan layers:
- Notes *(Additional notes)*
- Dimensions
  - VenueDimensions *(Dimensions relating to venue floorplan)*
  - AreaDimensions *(Dimensions relating to area placement and layout)*
- TLA *(Team names)*
- Network
  - Displays *(SRcomp info monitors)*
  - VenueNetwork *(Venue installed networking)*
  - NetworkEquipment *(Additional cables, switches, routers and access points)*
- Power
  - VenuePower *(Venue power outlets)*
  - PowerEquipment *(Required power locations)*
- Areas
  - AreaTables *(Position of designated tables)*
  - AreaZones *(Marked out zones)*
- Shepherding *(Shepherd specific highlighting)*
- General
  - GeneralLabels *(global drawing labels)*
  - VenueFloorplan *(venue floorplans)*
  - Exits *(Fire exits and lanes)*

#### Key Layers:
- General
- Network
- Power
- Areas
- Shepherding

## Generation script

This script helps with drawing building diagrams parametrically since most building have straight walls at right-angles.

#### Requires:
- python 3

#### Usage
Run `python svg_plot --help` for the command-line options,
specifically `-o` is needed to specify the output file-name.
The `-i` option can be used to begin with a pre-existing svg file.
Most of the other options are set interactively if not specified.
The scale option allows setting a scale of the input units so that when measuring lengths on a printed diagram the millimetre value is automatically converted into it's represented amount of meters.

Once the program is started and the initial options are complete a live-preview of the drawing can be seen by opening the `svg_tmp.html` file, which will have been created in the current directory. 

The prompt is then used to input straight horizontal or vertical lines using the configured letter and a length, i.e. `w12` for a vertical line of 12 units. Use `h` to get a list and description of the configured commands.

## Build script
__This script is still being written__

The script that will take each layout file and create a file in the `output/` directory with the required layers and scaling as well as adding a key and scale bar.

#### Requires:
- python \>3.6
- PyYaml

```bash
pip3 install --user -U -r requirements.txt
```

#### YAML Layer Specification
```yaml
image: "cube.svg"
title: "Cube Layout"
show: 
  - ALL
hide:
  - shepherding
embed:
-
  marker: "KEY__"
  image: "key.svg"
  show: 
    - ALL
  hide:
    - shepherding
```

#### JSON Layer Specification
```json
{
  "image": "cube.svg",
  "title": "Cube Layout",
  "show": [
    "All"
  ],
  "hide": [
    "shepherding"
  ],
  "embed": [{
    "marker": "KEY__",
    "image": "key.svg",
    "show":[ "ALL" ],
    "hide": [ "shepherding" ]
  }]
}
```
