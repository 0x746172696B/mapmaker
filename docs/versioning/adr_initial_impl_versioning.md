# ADR: Initial implementation of map versioning

- Status: Draft
- Date: 2026-07-17

## Context

Today every map lives in memory in `MapEngine._maps` and is persisted by the MCP
server's `_persist()` to `state/maps.json` as `{map_id: {size, blocks}}`. Every
mutating tool call (`fill`, `hollow_box`, `cylinder`, `batch_ops`) applies
immediately and silently overwrites the previous state of the map.

Consequences of that:

- an agent that makes a bad build step cannot undo it; it must manually erase
  or rebuild,
- there is no record of how a map evolved or why,
- maps have no description, so with several maps in the state file nothing
  tells you (or an agent) which map is which.

## Requirements

1. Applying an action stores a new **version** with a description of the change.
2. `rollback` restores a map to a previous version.
3. `list_map_versions` returns the available versions with their descriptions.
4. A map has a **description** of its content.
5. The MCP layer can list maps and switch which map is "active" (worked on by
   default).

## Decision

### 1. Version history lives on `Map`

Each `Map` owns its own history; `MapEngine` only orchestrates. A version is:

```python
@dataclass(frozen=True)
class MapVersion:
    number: int          # 1, 2, 3... monotonically increasing
    description: str     # what changed
    blocks: dict[Coord, Block]  # snapshot of the sparse block dict
```

Snapshots are shallow copies of `_blocks`. `Coord`, `Block`, `HexColor` are
immutable, so copying the dict is enough and shared `Block` instances are safe.
Cost is O(active blocks) per version.

### 2. Snapshot on every mutating engine call

`MapEngine.do()` appends a version after successfully applying an action, using
a generated description (e.g. `"fill #FF0000 (0,0,0)->(5,5,5)"`). `batch_ops`
produces **one** version per batch (snapshot after the whole batch, or after
the last successful op on partial failure), not one per operation, otherwise a
large build floods the history.

### 3. Rollback is non-destructive

`rollback(map_id, version)` restores that snapshot as the current blocks and
appends it as a **new** version (`"rollback to version N"`). History is never
truncated, so you can roll forward again after a bad rollback.

### 4. New API surface

`MapEngine` / `Map`:

- `Map.description: str`: set at creation, updatable.
- `MapEngine.create_map(size, description)`: description becomes required
  from the MCP tool so agents always label maps.
- `MapEngine.rollback(map_id, version_number)`
- `MapEngine.list_map_versions(map_id) -> list[tuple[int, str]]`

MCP tools (new):

- `list_maps()`: ids + descriptions + sizes.
- `list_map_versions(map_id)`
- `rollback(map_id, version)`
- `set_active_map(map_id)` / active-map default (see below).

### 5. Active map lives in the MCP server, not the engine

"Active map" is a client-session convenience: existing tools keep their
explicit `map_id` parameter, but it becomes optional and defaults to the
active map. The engine stays ignorant of it; it is UI/protocol state, not
domain state.

> **Known tradeoff:** the MCP server is a single process, so the active map is
> effectively global. Two clients connected to the same server would fight over
> it. We accept this because mapmaker is currently a single-user, local tool.
> If multi-client becomes real, active-map must move to per-session state or be
> dropped in favor of always-explicit `map_id`.

### 6. Persistence schema v2

`state/maps.json` gains versions and descriptions:

```json
{
  "<map_id>": {
    "size": 20,
    "description": "medieval castle",
    "versions": [
      {"number": 1, "description": "initial", "blocks": [...]}
    ],
    "current": [...blocks...]
  }
}
```

Migration: on load, an entry without `versions` (v1 format) is imported as a
single version `1` with description `"imported"`. `Map.from_state` is the
touchpoint.

## Alternatives considered

- **Action log + replay** instead of block snapshots: cheaper to store, but
  rollback cost grows with history length and replay must stay perfectly
  deterministic across code changes. Snapshots are dumber and safer for a
  first implementation.
- **Explicit checkpoint tool** (agent decides when to version) instead of
  auto-snapshot per `do()`: fewer versions, but the whole point is protecting
  against steps the agent did *not* anticipate going wrong. Auto-snapshot wins;
  batch-level granularity keeps volume sane.
- **Engine-level version store** (`MapEngine` holds `dict[map_id, history]`):
  splits a map's data across two owners and complicates persistence. Rejected.

## Consequences

- Memory and state-file size grow linearly with history × active blocks. If
  this hurts, add a history cap (keep last N versions), noted as follow-up,
  not built now.
- Every mutating MCP call already rewrites the whole state file; with versions
  the file gets bigger and this O(everything) write gets slower. Acceptable at
  current scale.
- `create_map` signature changes (description). Tests and the demo agent
  config need updating.
