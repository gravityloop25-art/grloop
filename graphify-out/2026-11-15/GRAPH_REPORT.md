# Graph Report - grloop  (2026-11-15)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 408 nodes · 912 edges · 18 communities (15 shown, 3 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 37 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `eaba0540`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- server.js
- app.js
- dashboard/package.json
- common.py
- session.js
- gv.py
- hit.py
- gb.py
- wl.py
- Sky
- desktop/package.json
- android/package.json
- with
- dr.py
- build-apps.yml
- make-config.js
- vercel.json

## God Nodes (most connected - your core abstractions)
1. `make_audio()` - 27 edges
2. `Writer` - 22 edges
3. `compose()` - 21 edges
4. `mux()` - 20 edges
5. `font()` - 19 edges
6. `lerp()` - 16 edges
7. `renderPlan()` - 15 edges
8. `getKV()` - 13 edges
9. `openVideo()` - 11 edges
10. `with` - 11 edges

## Surprising Connections (you probably didn't know these)
- `videosView()` --indirect_call--> `q()`  [INFERRED]
  dashboard/public/app.js → dashboard/db.js
- `run()` --calls--> `Writer`  [EXTRACTED]
  code/dr.py → code/common.py
- `run()` --calls--> `Writer`  [EXTRACTED]
  code/gb.py → code/common.py
- `run()` --calls--> `Writer`  [EXTRACTED]
  code/gv.py → code/common.py
- `run()` --calls--> `Writer`  [EXTRACTED]
  code/hit.py → code/common.py

## Import Cycles
- None detected.

## Communities (18 total, 3 thin omitted)

### Community 0 - "server.js"
Cohesion: 0.08
Nodes (54): batch(), client, { createClient }, delKV(), fs, getKV(), init(), path (+46 more)

### Community 1 - "app.js"
Cohesion: 0.13
Nodes (39): addDays(), api(), app, appShell(), axes(), bestTimes(), C, charts (+31 more)

### Community 2 - "dashboard/package.json"
Cohesion: 0.12
Nodes (19): dependencies, chart.js@^4.4.0, dotenv@^18.0.10, express@^5.0.0, @libsql/client@^0.18.0, description, engines, node (+11 more)

### Community 3 - "common.py"
Cohesion: 0.06
Nodes (71): draw(), rot(), run(), step(), draw(), rot(), run(), step() (+63 more)

### Community 4 - "session.js"
Cohesion: 0.27
Nodes (13): clearOAuth(), cookies(), crypto, devSecret, getOAuth(), isLoggedIn(), login(), logout() (+5 more)

### Community 5 - "gv.py"
Cohesion: 0.35
Nodes (9): arm_state(), draw(), gear_hit(), obb(), rot(), run(), seg_hit(), step() (+1 more)

### Community 8 - "hit.py"
Cohesion: 0.38
Nodes (8): ballcol(), corners(), draw(), obb(), obstacles(), rot(), run(), step()

### Community 9 - "gb.py"
Cohesion: 0.42
Nodes (7): bloop(), draw(), make_audio_gb(), run(), scol(), shimmer(), step()

### Community 10 - "wl.py"
Cohesion: 0.57
Nodes (6): colr(), draw(), run(), scr(), splash(), wave_step()

### Community 22 - "desktop/package.json"
Cohesion: 0.06
Nodes (31): { app, BrowserWindow, shell, ipcMain }, APP_URL, path, pending, author, build, appId, files (+23 more)

### Community 23 - "android/package.json"
Cohesion: 0.14
Nodes (17): dependencies, @capacitor/android@^8.6.2, @capacitor/app@^8.1.2, @capacitor/browser@^8.0.5, @capacitor/cli@^8.6.2, @capacitor/core@^8.6.2, description, name (+9 more)

### Community 24 - "with"
Cohesion: 0.06
Nodes (41): defaults, needs, runs-on, steps, runs-on, steps, run, defaults (+33 more)

### Community 27 - "dr.py"
Cohesion: 0.54
Nodes (7): adf(), draw(), rot(), run(), step(), th1(), th2()

### Community 28 - "build-apps.yml"
Cohesion: 0.14
Nodes (13): description, required, env, APP_URL, app_url, name, on, push (+5 more)

### Community 65 - "vercel.json"
Cohesion: 0.33
Nodes (5): maxDuration, functions, api/index.js, regions, rewrites

## Knowledge Gaps
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `q()` connect `server.js` to `app.js`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Should `server.js` be split into smaller, more focused modules?**
  _Cohesion score 0.07878787878787878 - nodes in this community are weakly interconnected._
- **Why does `videosView()` connect `app.js` to `server.js`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._
- **Should `dashboard/package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.12105263157894737 - nodes in this community are weakly interconnected._
- **Should `common.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06079207920792079 - nodes in this community are weakly interconnected._
- **Should `desktop/package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.05873015873015873 - nodes in this community are weakly interconnected._