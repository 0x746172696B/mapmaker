# Map maker

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
