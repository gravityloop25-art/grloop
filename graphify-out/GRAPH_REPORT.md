# Graph Report - grloop  (2026-11-15)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 269 nodes · 718 edges · 23 communities (21 shown, 2 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 22 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `92d39df9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22

## God Nodes (most connected - your core abstractions)
1. `make_audio()` - 27 edges
2. `Writer` - 22 edges
3. `compose()` - 21 edges
4. `mux()` - 20 edges
5. `font()` - 19 edges
6. `lerp()` - 16 edges
7. `renderPlan()` - 15 edges
8. `openVideo()` - 11 edges
9. `getKV()` - 10 edges
10. `overview()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `run()` --calls--> `Writer`  [EXTRACTED]
  code/bk.py → code/common.py
- `run()` --calls--> `Writer`  [EXTRACTED]
  code/cd.py → code/common.py
- `run()` --calls--> `Writer`  [EXTRACTED]
  code/ce.py → code/common.py
- `run()` --calls--> `Writer`  [EXTRACTED]
  code/dr.py → code/common.py
- `run()` --calls--> `Writer`  [EXTRACTED]
  code/fk.py → code/common.py

## Import Cycles
- None detected.

## Communities (23 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.10
Nodes (44): Database, db, delKV(), fs, getKV(), path, setKV(), ApiError (+36 more)

### Community 1 - "Community 1"
Cohesion: 0.15
Nodes (34): addDays(), api(), app, axes(), bestTimes(), C, charts, COLS (+26 more)

### Community 2 - "Community 2"
Cohesion: 0.11
Nodes (21): dependencies, better-sqlite3@^13.2.0, chart.js@^4.4.0, dotenv@^18.0.10, express@^5.0.0, express-session@^1.18.0, description, engines (+13 more)

### Community 3 - "Community 3"
Cohesion: 0.19
Nodes (18): font(), lerp(), ang(), arc_collide(), ballcol(), draw(), draw_arm(), pt_collide() (+10 more)

### Community 4 - "Community 4"
Cohesion: 0.27
Nodes (6): mux(), run(), step(), draw(), run(), step()

### Community 5 - "Community 5"
Cohesion: 0.35
Nodes (9): arm_state(), draw(), gear_hit(), obb(), rot(), run(), seg_hit(), step() (+1 more)

### Community 6 - "Community 6"
Cohesion: 0.18
Nodes (7): ch, fs, insD, insP, insV, names, now

### Community 7 - "Community 7"
Cohesion: 0.47
Nodes (5): click(), finale(), make_audio(), pop(), tone()

### Community 8 - "Community 8"
Cohesion: 0.38
Nodes (8): ballcol(), corners(), draw(), obb(), obstacles(), rot(), run(), step()

### Community 9 - "Community 9"
Cohesion: 0.42
Nodes (7): bloop(), draw(), make_audio_gb(), run(), scol(), shimmer(), step()

### Community 10 - "Community 10"
Cohesion: 0.54
Nodes (7): adf(), draw(), rot(), run(), step(), th1(), th2()

### Community 11 - "Community 11"
Cohesion: 0.48
Nodes (5): dang(), draw(), run(), step(), compose()

### Community 12 - "Community 12"
Cohesion: 0.52
Nodes (6): ballcol(), draw(), run(), spawn(), step(), update_gears()

### Community 13 - "Community 13"
Cohesion: 0.48
Nodes (5): arm_hit(), draw(), rot(), run(), step()

### Community 14 - "Community 14"
Cohesion: 0.53
Nodes (4): draw(), rot(), run(), step()

### Community 15 - "Community 15"
Cohesion: 0.67
Nodes (5): draw(), rot(), run(), step(), theta()

### Community 16 - "Community 16"
Cohesion: 0.67
Nodes (5): draw(), mcol(), rad(), run(), step()

### Community 17 - "Community 17"
Cohesion: 0.60
Nodes (5): ballcol(), draw(), run(), spawn(), step()

### Community 18 - "Community 18"
Cohesion: 0.60
Nodes (5): bcol(), draw(), rot(), run(), step()

### Community 19 - "Community 19"
Cohesion: 0.80
Nodes (4): bar(), draw(), run(), step()

### Community 20 - "Community 20"
Cohesion: 0.60
Nodes (3): draw(), run(), step()

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `make_audio()` connect `Community 7` to `Community 3`, `Community 4`, `Community 5`, `Community 8`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 14`, `Community 15`, `Community 16`, `Community 17`, `Community 18`, `Community 19`, `Community 20`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.09796806966618288 - nodes in this community are weakly interconnected._
- **Why does `Writer` connect `Community 22` to `Community 3`, `Community 4`, `Community 5`, `Community 7`, `Community 8`, `Community 9`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 14`, `Community 15`, `Community 16`, `Community 17`, `Community 18`, `Community 19`, `Community 20`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.11255411255411256 - nodes in this community are weakly interconnected._
- **Why does `compose()` connect `Community 11` to `Community 3`, `Community 4`, `Community 5`, `Community 7`, `Community 8`, `Community 9`, `Community 10`, `Community 12`, `Community 13`, `Community 14`, `Community 15`, `Community 16`, `Community 17`, `Community 18`, `Community 19`, `Community 20`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._