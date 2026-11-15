# Graph Report - grloop  (2026-11-15)

## Corpus Check
- 40 files · ~30,786 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 6, .example 1, .webmanifest 1)

## Summary
- 1168 nodes · 2785 edges · 68 communities (56 shown, 12 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 116 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `25768a3d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- server.js
- app.js
- package.json
- font
- Na
- gv.py
- js
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
- random
- Sky
- desktop/package.json
- android/package.json
- steps
- with
- chart.umd.js
- dr.py
- app_url
- android
- desktop
- build-apps.yml
- jobs
- make-config.js
- _n
- sn
- tn
- Jt
- xt
- .update
- n
- Ss
- ua
- .notifyPlugins
- l
- e
- .register
- ._computeLabelItems
- draw
- oo
- s
- Ho
- .draw
- .buildOrUpdateControllers
- a
- co
- bo
- hs
- Rn
- update
- .getPixelForDecimal
- So
- je
- u
- .getLabelTimestamps
- vercel.json
- .getLabels

## God Nodes (most connected - your core abstractions)
1. `tn` - 131 edges
2. `js` - 58 edges
3. `s()` - 44 edges
4. `_n` - 34 edges
5. `n()` - 31 edges
6. `o()` - 28 edges
7. `Na` - 28 edges
8. `make_audio()` - 27 edges
9. `l()` - 26 edges
10. `a()` - 25 edges

## Surprising Connections (you probably didn't know these)
- `videosView()` --indirect_call--> `q()`  [INFERRED]
  dashboard/public/app.js → dashboard/public/vendor/chart.umd.js
- `draw()` --calls--> `compose()`  [EXTRACTED]
  code/bk.py → code/common.py
- `draw()` --calls--> `font()`  [EXTRACTED]
  code/bk.py → code/common.py
- `draw()` --calls--> `lerp()`  [EXTRACTED]
  code/bk.py → code/common.py
- `run()` --calls--> `make_audio()`  [EXTRACTED]
  code/bk.py → code/common.py

## Import Cycles
- None detected.

## Communities (68 total, 12 thin omitted)

### Community 0 - "server.js"
Cohesion: 0.06
Nodes (67): batch(), client, { createClient }, delKV(), fs, getKV(), init(), path (+59 more)

### Community 1 - "app.js"
Cohesion: 0.13
Nodes (39): addDays(), api(), app, appShell(), axes(), bestTimes(), C, charts (+31 more)

### Community 2 - "package.json"
Cohesion: 0.12
Nodes (19): dependencies, chart.js@^4.4.0, dotenv@^18.0.10, express@^5.0.0, @libsql/client@^0.18.0, description, engines, node (+11 more)

### Community 3 - "font"
Cohesion: 0.38
Nodes (9): font(), ang(), arc_collide(), ballcol(), draw(), draw_arm(), pt_collide(), run() (+1 more)

### Community 4 - "Na"
Cohesion: 0.05
Nodes (21): afterInit(), Ba(), Ca(), Ee(), f(), generateLabels(), ki(), Le() (+13 more)

### Community 5 - "gv.py"
Cohesion: 0.35
Nodes (9): arm_state(), draw(), gear_hit(), obb(), rot(), run(), seg_hit(), step() (+1 more)

### Community 6 - "js"
Cohesion: 0.05
Nodes (16): Bn(), _calculateBarValuePixels(), getLabelAndValue(), getMaxOverflow(), initialize(), js, g(), Ls() (+8 more)

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
Cohesion: 0.29
Nodes (11): lerp(), draw(), run(), step(), tcol(), colr(), draw(), run() (+3 more)

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
Cohesion: 0.53
Nodes (4): draw(), rot(), run(), step()

### Community 15 - "cd.py"
Cohesion: 0.67
Nodes (5): draw(), rot(), run(), step(), theta()

### Community 16 - "ls.py"
Cohesion: 0.67
Nodes (5): draw(), mcol(), rad(), run(), step()

### Community 17 - "plinko.py"
Cohesion: 0.33
Nodes (5): ballcol(), draw(), run(), spawn(), step()

### Community 18 - "rb.py"
Cohesion: 0.39
Nodes (6): compose(), bcol(), draw(), rot(), run(), step()

### Community 19 - "compose"
Cohesion: 0.48
Nodes (5): mux(), bar(), draw(), run(), step()

### Community 20 - "random"
Cohesion: 0.31
Nodes (6): draw(), run(), step(), draw(), run(), step()

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

### Community 26 - "chart.umd.js"
Cohesion: 0.05
Nodes (17): at(), beforeLayout(), buildLookupTable(), ea(), getDecimalForValue(), getValueForPixel(), Go(), initOffsets() (+9 more)

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

### Community 34 - "_n"
Cohesion: 0.10
Nodes (4): fn(), gn(), _n, xn()

### Community 35 - "sn"
Cohesion: 0.11
Nodes (4): an(), on, rn(), sn

### Community 37 - "Jt"
Cohesion: 0.10
Nodes (9): It(), jt(), Jt, kt(), mt(), qt(), _t(), wt() (+1 more)

### Community 38 - "xt"
Cohesion: 0.12
Nodes (3): As, Ts, xt

### Community 39 - ".update"
Cohesion: 0.13
Nodes (4): d(), dt(), Pn(), Sn()

### Community 40 - "n"
Cohesion: 0.13
Nodes (18): b(), cn(), eo(), g(), Gs(), hn(), ln(), m() (+10 more)

### Community 41 - "Ss"
Cohesion: 0.12
Nodes (14): Be(), bs(), ct(), Fs(), ge(), ks(), ms(), pe() (+6 more)

### Community 42 - "ua"
Cohesion: 0.13
Nodes (15): beforeDatasetDraw(), beforeDatasetsDraw(), beforeDraw(), ca, da(), fa(), ga(), ha() (+7 more)

### Community 44 - "l"
Cohesion: 0.14
Nodes (18): aa(), afterDatasetsUpdate(), _calculateBarIndexPixels(), _getAxis(), _getAxisCount(), getFirstScaleIdForIndexAxis(), _getRuler(), _getStackCount() (+10 more)

### Community 45 - "e"
Cohesion: 0.16
Nodes (18): Bt(), dn(), e(), fe(), Ft(), gi(), Gt(), K() (+10 more)

### Community 46 - ".register"
Cohesion: 0.18
Nodes (5): ce(), de, en, he(), te()

### Community 48 - "draw"
Cohesion: 0.15
Nodes (16): ai(), dataset(), draw(), _e(), fo(), hi(), index(), nearest() (+8 more)

### Community 49 - "oo"
Cohesion: 0.13
Nodes (8): Bi(), Ci(), et(), Fi(), io(), no(), oo, zi()

### Community 50 - "s"
Cohesion: 0.15
Nodes (15): De(), getPixelForTick(), getPixelForValue(), ho(), _i(), ii(), ji(), label() (+7 more)

### Community 51 - "Ho"
Cohesion: 0.21
Nodes (3): Bo(), Ho, nt()

### Community 54 - "a"
Cohesion: 0.24
Nodes (4): a(), determineDataLimits(), Di(), l()

### Community 55 - "co"
Cohesion: 0.18
Nodes (11): ao(), co(), Do(), getCenterPoint(), inRange(), inXRange(), inYRange(), Oo() (+3 more)

### Community 56 - "bo"
Cohesion: 0.20
Nodes (4): bo, H(), j(), xo()

### Community 59 - "update"
Cohesion: 0.20
Nodes (10): addElements(), as(), es(), is(), ns(), os(), rs(), ss() (+2 more)

### Community 61 - "So"
Cohesion: 0.20
Nodes (4): configure(), ne(), numeric(), So

### Community 62 - "je"
Cohesion: 0.29
Nodes (6): ei(), je(), qe(), ti(), Ye(), yn()

### Community 64 - ".getLabelTimestamps"
Cohesion: 0.38
Nodes (3): _generate(), _getTimestampsForTable(), Vo()

### Community 65 - "vercel.json"
Cohesion: 0.33
Nodes (5): maxDuration, functions, api/index.js, regions, rewrites

### Community 66 - ".getLabels"
Cohesion: 0.40
Nodes (3): buildTicks(), init(), mo()

## Knowledge Gaps
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `tn` connect `tn` to `.getLabels`, `sn`, `xt`, `.update`, `n`, `ua`, `.notifyPlugins`, `._computeLabelItems`, `s`, `.draw`, `.buildOrUpdateControllers`, `a`, `co`, `bo`, `chart.umd.js`, `.getPixelForDecimal`, `So`, `u`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `s()` (e.g. with `ao()` and `co()`) actually correct?**
  _`s()` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Should `server.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06392405063291139 - nodes in this community are weakly interconnected._
- **Why does `q()` connect `draw` to `app.js`, `chart.umd.js`, `s`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `n()` (e.g. with `chart.umd.js` and `l()`) actually correct?**
  _`n()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._
- **Why does `videosView()` connect `app.js` to `draw`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._