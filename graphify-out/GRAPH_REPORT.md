# Graph Report - grloop  (2026-11-15)

## Corpus Check
- 39 files · ~27,846 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 10 file(s) not represented in the graph (top: (none) 7, .example 1, .webmanifest 1)

## Summary
- 411 nodes · 918 edges · 24 communities (20 shown, 4 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 37 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7d422721`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- server.js
- app.js
- dashboard/package.json
- common.py
- session.js
- gv.py
- gear3.py
- with
- hit.py
- gb.py
- android
- desktop
- build-apps.yml
- jobs
- Sky
- desktop/package.json
- android/package.json
- steps
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
  code/gear3.py → code/common.py
- `run()` --calls--> `Writer`  [EXTRACTED]
  code/gv.py → code/common.py

## Import Cycles
- None detected.

## Communities (24 total, 4 thin omitted)

### Community 0 - "server.js"
Cohesion: 0.08
Nodes (55): batch(), client, { createClient }, delKV(), fs, getKV(), guard(), init() (+47 more)

### Community 1 - "app.js"
Cohesion: 0.13
Nodes (39): addDays(), api(), app, appShell(), axes(), bestTimes(), C, charts (+31 more)

### Community 2 - "dashboard/package.json"
Cohesion: 0.12
Nodes (19): dependencies, chart.js@^4.4.0, dotenv@^18.0.10, express@^5.0.0, @libsql/client@^0.18.0, description, engines, node (+11 more)

### Community 3 - "common.py"
Cohesion: 0.06
Nodes (69): draw(), rot(), run(), step(), draw(), rot(), run(), step() (+61 more)

### Community 4 - "session.js"
Cohesion: 0.23
Nodes (14): authed(), clearOAuth(), cookies(), crypto, devSecret, getOAuth(), isLoggedIn(), login() (+6 more)

### Community 5 - "gv.py"
Cohesion: 0.35
Nodes (9): arm_state(), draw(), gear_hit(), obb(), rot(), run(), seg_hit(), step() (+1 more)

### Community 6 - "gear3.py"
Cohesion: 0.44
Nodes (8): ang(), arc_collide(), ballcol(), draw(), draw_arm(), pt_collide(), run(), step()

### Community 7 - "with"
Cohesion: 0.22
Nodes (9): with, distribution, files, java-version, merge-multiple, name, node-version, path (+1 more)

### Community 8 - "hit.py"
Cohesion: 0.38
Nodes (8): ballcol(), corners(), draw(), obb(), obstacles(), rot(), run(), step()

### Community 9 - "gb.py"
Cohesion: 0.42
Nodes (7): bloop(), draw(), make_audio_gb(), run(), scol(), shimmer(), step()

### Community 10 - "android"
Cohesion: 0.29
Nodes (7): defaults, needs, runs-on, run, defaults, android, working-directory

### Community 11 - "desktop"
Cohesion: 0.29
Nodes (7): needs, runs-on, strategy, desktop, os, fail-fast, matrix

### Community 12 - "build-apps.yml"
Cohesion: 0.33
Nodes (5): env, APP_URL, name, permissions, contents

### Community 13 - "jobs"
Cohesion: 0.33
Nodes (6): runs-on, jobs, check, release, needs, runs-on

### Community 22 - "desktop/package.json"
Cohesion: 0.06
Nodes (31): { app, BrowserWindow, shell, ipcMain }, APP_URL, path, pending, author, build, appId, files (+23 more)

### Community 23 - "android/package.json"
Cohesion: 0.14
Nodes (17): dependencies, @capacitor/android@^8.6.2, @capacitor/app@^8.1.2, @capacitor/browser@^8.0.5, @capacitor/cli@^8.6.2, @capacitor/core@^8.6.2, description, name (+9 more)

### Community 24 - "steps"
Cohesion: 0.23
Nodes (12): steps, steps, steps, CSC_IDENTITY_AUTO_DISCOVERY, steps, continue-on-error, env, name (+4 more)

### Community 27 - "dr.py"
Cohesion: 0.54
Nodes (7): adf(), draw(), rot(), run(), step(), th1(), th2()

### Community 28 - "build-apps.yml"
Cohesion: 0.25
Nodes (8): description, required, app_url, on, push, workflow_dispatch, tags, inputs

### Community 65 - "vercel.json"
Cohesion: 0.33
Nodes (5): maxDuration, functions, api/index.js, regions, rewrites

## Knowledge Gaps
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `q()` connect `server.js` to `app.js`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Should `server.js` be split into smaller, more focused modules?**
  _Cohesion score 0.07878787878787878 - nodes in this community are weakly interconnected._
- **Why does `videosView()` connect `app.js` to `server.js`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._
- **Should `dashboard/package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.12105263157894737 - nodes in this community are weakly interconnected._
- **Should `common.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06486254295532647 - nodes in this community are weakly interconnected._
- **Should `desktop/package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.057057057057057055 - nodes in this community are weakly interconnected._