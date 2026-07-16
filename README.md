# Basic Map maker w/mcp server

The goal is allow an agent to dynamically generate and update maps following users request

## Components

### Map Engine

- Allows for the addition/removal of blocks within a pre-established 3d space
- Maintain a grid with the allocated blocks

### Rendering Engine

- Displays a 3d space divided by uniform blocks

### Mcp API

- Get current state of the plane
- Update areas
- Fetch available pre-made structures

## Demo 1

### Viewer

![Demo1_image](demo.png)

### Prompt used

```
Using the mapmaker tools, create a map of size 120 and build a fortified river city:
Terrain & layout

Ground platform covering the full 120x120 floor at y=0
A "river" running the full length of the map: a 6-block-wide strip where the ground is raised by 1 block (y=1), crossing the city roughly through the middle but offset from center, so the city has a larger district and a smaller district

Fortifications

Perimeter walls 3 blocks thick, 10 high, inset 3 blocks from the edges
Eight cylindrical towers along the walls: one at each corner (radius 4, height 16) and one at the midpoint of each side (radius 3, height 14)
Two bridge structures crossing the river: solid causeways 5 blocks wide, raised 4 blocks above the ground, each with a small guard post (hollow box) at both ends

The citadel (in the larger district)

A raised foundation 24x24, 3 blocks high
On it, a hollow great hall 20x14, 10 blocks high
A cylindrical grand tower at one corner of the citadel, radius 5, height 26 — the tallest structure in the city
A defensive inner wall around the citadel, 1 block thick, 5 high, with a few blocks of gap on the side facing the river

The districts

Larger district: a 3x3 grid of houses (hollow boxes, varied sizes 5–8 wide, 4–6 tall) with street gaps between them
Smaller district: 4 warehouses (hollow boxes ~10x6x8) arranged in a row parallel to the river
A market: a cluster of small solid platforms (3x1x3) near one bridge

Plan the coordinate layout before placing anything: list each structure with its bounding coordinates, check nothing overlaps and everything fits, then build. Use map_summary periodically to sanity-check. Coordinates are 0-indexed, y is up. When finished, report total blocks and describe the skyline from the river.
```

## Demo 2

### Viewer

![Demo2_image](demo2.png)

### Prompt Used

```
Using the mapmaker tools, create a map of size 120 and build a fortified river city. A river winds through it — not a straight channel, something with bends and varying width, the way real rivers cut through terrain. The city grew around the river: older, denser construction near the water, grander structures on higher ground, defenses where the geography demands them rather than in a neat square.
You have fill, hollow_box, and cylinder — but don't think of structures as single primitives. A convincing shape is usually many small overlapping operations: a winding river is dozens of short offset segments, a hill is stacked shrinking layers, a ruined wall is fills with irregular tops. Fidelity comes from composition, not from the primitive.
Plan the character of the city first — its geography, its districts, its story — then build it. Take as many operations as the vision needs. Coordinates are 0-indexed, y is up, 120³ space. When done, describe what a traveler arriving by the river would see.
```
