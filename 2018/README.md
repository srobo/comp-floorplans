# Notes for 2018

The templates here are intended to be 1:1 scale diagram of all the areas used in SUSU, they are believed to be within 5% accurate.
Locations highlighted in red on one of the venue related layers require measurements to be taken to assure their size.

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


#### Key Layers:
- General
- Network
- Power
- Areas
- Shepherding


## Generation Script:
#### Folder structure:
```
team_names.txt
templates/
  Lv4.svg
  Lv3.svg
  Lv2.svg
  Cube.svg
  key.svg
  layout.svg
layouts/
  shepherding.json
output/
  Shepherding.svg
```

#### Code structure:
```
read in specification
load svg
set title and version
add team names
display only selected layers or ALL
add key
  add at marker (with scale)?
add other nested svgs
  add at marker (with scale)?
  add team names
  display only selected layers or ALL
save to output
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
  marker: "%%KEY%%"
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
  "embed": {
    "marker": "%%KEY%%",
    "image": "key.svg",
    "show":[ "ALL" ],
    "hide": [ "shepherding" ]
  }
}
```
