# Graph Report - grloop  (2026-11-15)

## Corpus Check
- 37 files · ~27,202 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 5, .example 1, .webmanifest 1)

## Summary
- 385 nodes · 852 edges · 34 communities (32 shown, 2 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 23 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3eb74543`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- server.js
- app.js
- package.json
- font
- math
- gv.py
- demo.js
- common.py
- hit.py
- gb.py
- wl.py
- mux
- gearpl.py
- tu.py
- pil
- cd.py
- ls.py
- plinko.py
- rb.py
- compose
- math
- Sky
- desktop/package.json
- android/package.json
- steps
- with
- pil
- dr.py
- app_url
- android
- desktop
- build-apps.yml
- jobs
- make-config.js

## God Nodes (most connected - your core abstractions)
1. `make_audio()` - 27 edges
2. `Writer` - 22 edges
3. `compose()` - 21 edges
4. `mux()` - 20 edges
5. `font()` - 19 edges
6. `lerp()` - 16 edges
7. `renderPlan()` - 15 edges
8. `with` - 11 edges
9. `openVideo()` - 11 edges
10. `getKV()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `draw()` --calls--> `compose()`  [EXTRACTED]
  code/bk.py → code/common.py
- `draw()` --calls--> `font()`  [EXTRACTED]
  code/bk.py → code/common.py
- `draw()` --calls--> `lerp()`  [EXTRACTED]
  code/bk.py → code/common.py
- `run()` --calls--> `make_audio()`  [EXTRACTED]
  code/bk.py → code/common.py
- `run()` --calls--> `mux()`  [EXTRACTED]
  code/bk.py → code/common.py

## Import Cycles
- None detected.

## Communities (34 total, 2 thin omitted)

### Community 0 - "server.js"
Cohesion: 0.10
Nodes (45): Database, db, delKV(), fs, getKV(), path, setKV(), ApiError (+37 more)

### Community 1 - "app.js"
Cohesion: 0.15
Nodes (35): addDays(), api(), app, appShell(), axes(), bestTimes(), C, charts (+27 more)

### Community 2 - "package.json"
Cohesion: 0.11
Nodes (21): dependencies, better-sqlite3@^13.2.0, chart.js@^4.4.0, dotenv@^18.0.10, express@^5.0.0, express-session@^1.18.0, description, engines (+13 more)

### Community 3 - "font"
Cohesion: 0.42
Nodes (8): font(), ang(), arc_collide(), draw(), draw_arm(), pt_collide(), run(), step()

### Community 4 - "math"
Cohesion: 0.60
Nodes (3): draw(), run(), step()

### Community 5 - "gv.py"
Cohesion: 0.35
Nodes (9): arm_state(), draw(), gear_hit(), obb(), rot(), run(), seg_hit(), step() (+1 more)

### Community 6 - "demo.js"
Cohesion: 0.18
Nodes (7): ch, fs, insD, insP, insV, names, now

### Community 7 - "common.py"
Cohesion: 0.47
Nodes (5): click(), finale(), make_audio(), pop(), tone()

### Community 8 - "hit.py"
Cohesion: 0.38
Nodes (8): ballcol(), corners(), draw(), obb(), obstacles(), rot(), run(), step()

### Community 9 - "gb.py"
Cohesion: 0.42
Nodes (7): bloop(), draw(), make_audio_gb(), run(), scol(), shimmer(), step()

### Community 10 - "wl.py"
Cohesion: 0.57
Nodes (6): colr(), draw(), run(), scr(), splash(), wave_step()

### Community 11 - "mux"
Cohesion: 0.33
Nodes (5): dang(), draw(), run(), step(), Writer

### Community 12 - "gearpl.py"
Cohesion: 0.52
Nodes (6): ballcol(), draw(), run(), spawn(), step(), update_gears()

### Community 13 - "tu.py"
Cohesion: 0.48
Nodes (5): arm_hit(), draw(), rot(), run(), step()

### Community 14 - "pil"
Cohesion: 0.36
Nodes (4): draw(), rot(), run(), step()

### Community 15 - "cd.py"
Cohesion: 0.67
Nodes (5): draw(), rot(), run(), step(), theta()

### Community 16 - "ls.py"
Cohesion: 0.67
Nodes (5): draw(), mcol(), rad(), run(), step()

### Community 17 - "plinko.py"
Cohesion: 0.60
Nodes (5): ballcol(), draw(), run(), spawn(), step()

### Community 18 - "rb.py"
Cohesion: 0.39
Nodes (6): mux(), bcol(), draw(), rot(), run(), step()

### Community 19 - "compose"
Cohesion: 0.48
Nodes (5): compose(), bar(), draw(), run(), step()

### Community 20 - "math"
Cohesion: 0.60
Nodes (3): draw(), run(), step()

### Community 22 - "desktop/package.json"
Cohesion: 0.06
Nodes (31): { app, BrowserWindow, shell, ipcMain }, APP_URL, path, pending, author, build, appId, files (+23 more)

### Community 23 - "android/package.json"
Cohesion: 0.14
Nodes (17): dependencies, @capacitor/android@^8.6.2, @capacitor/app@^8.1.2, @capacitor/browser@^8.0.5, @capacitor/cli@^8.6.2, @capacitor/core@^8.6.2, description, name (+9 more)

### Community 24 - "steps"
Cohesion: 0.23
Nodes (12): steps, steps, steps, CSC_IDENTITY_AUTO_DISCOVERY, steps, continue-on-error, env, name (+4 more)

### Community 25 - "with"
Cohesion: 0.22
Nodes (9): with, distribution, files, java-version, merge-multiple, name, node-version, path (+1 more)

### Community 26 - "pil"
Cohesion: 0.39
Nodes (6): lerp(), ballcol(), draw(), run(), step(), tcol()

### Community 27 - "dr.py"
Cohesion: 0.54
Nodes (7): adf(), draw(), rot(), run(), step(), th1(), th2()

### Community 28 - "app_url"
Cohesion: 0.25
Nodes (8): description, required, app_url, on, push, workflow_dispatch, tags, inputs

### Community 29 - "android"
Cohesion: 0.29
Nodes (7): defaults, needs, runs-on, run, defaults, android, working-directory

### Community 30 - "desktop"
Cohesion: 0.29
Nodes (7): needs, runs-on, strategy, desktop, os, fail-fast, matrix

### Community 31 - "build-apps.yml"
Cohesion: 0.33
Nodes (5): env, APP_URL, name, permissions, contents

### Community 32 - "jobs"
Cohesion: 0.33
Nodes (6): runs-on, jobs, check, release, needs, runs-on

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `make_audio()` connect `common.py` to `font`, `math`, `gv.py`, `hit.py`, `wl.py`, `mux`, `gearpl.py`, `tu.py`, `pil`, `cd.py`, `ls.py`, `plinko.py`, `rb.py`, `compose`, `math`, `pil`, `dr.py`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Should `server.js` be split into smaller, more focused modules?**
  _Cohesion score 0.09643605870020965 - nodes in this community are weakly interconnected._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.1492063492063492 - nodes in this community are weakly interconnected._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.11255411255411256 - nodes in this community are weakly interconnected._
- **Should `desktop/package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.057057057057057055 - nodes in this community are weakly interconnected._
- **Should `android/package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.1437908496732026 - nodes in this community are weakly interconnected._