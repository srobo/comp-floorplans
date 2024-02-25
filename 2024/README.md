# Notes for 2024

The templates here are intended to be 100:1 scale diagram of all the areas used in SUSU, they are believed to be within 5% accurate.
Locations highlighted in red on one of the venue related layers require measurements to be taken to assure their size.

#### Requires:
- Python 3.6+
- PyYaml

```bash
pip3 install --user -U -r requirements.txt
```

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
