---
license: mit
pretty_name: LEAD Alpamayo PAI (large v4)
tags:
- autonomous-driving
- carla
- alpamayo
- physical-ai-av
- trajectory-prediction
- navigation
size_categories:
- 10K<n<100K
---

# LEAD Alpamayo PAI: large v4 (balanced manoeuvre mix)

CARLA 0.9.16 expert driving from [LEAD](https://huggingface.co/datasets/ln2697/lead-123d),
re-collected with the four NVIDIA Alpamayo 1.5 input cameras added, and converted to the
NVIDIA PhysicalAI-AV (PAI) on-disk format. It is read unchanged by
[alpamayo-recipes](https://github.com/NVlabs/alpamayo-recipes) Alpamayo 1.5 nav SFT
(`PAIDatasetWithNav`). Built with [lead2alpa](https://github.com/Silicon-Melter/lead2alpa).

A single CARLA pass recorded LEAD's own sensors, the Alpamayo cameras and a Bench2Drive rig
(for a separate HiP-AD project; not included here) at once. Collection is complete: it ran
2026-09-25 through 2026-10-05, ending when the planned route list was exhausted at 574 GB on
disk, and this release converts every log it produced -- the same recordings as
[`..._large_v3`](https://huggingface.co/datasets/earth37815/lead-alpamayo-pai_large_v3).

**v4 is a re-curation, not a new collection: it fixes the manoeuvre mix.** The nav command is
balanced the way a nav-conditioned model wants it -- half the samples straight, the other half
split evenly over the four lateral commands -- and samples are drawn every 0.4 s instead of
every 1 s, which is what makes that mix large enough to train on.

| | train | val |
| --- | --- | --- |
| routes / clips | 601 / 1,694 | 45 / 146 |
| nav samples | **16,040** | **1,720** |
| straight | 8,020 | 860 |
| junction left / right | 2,005 / 2,005 | 215 / 215 |
| swerve left / right | 2,005 / 2,005 | 215 / 215 |
| stationary samples | 1.7% | 0.5% |
| all 0.4 s samples before curation (`*_all.json`) | 42,836 | 3,736 |

Exactly **50.0 % straight and 12.5 % in each of the four lateral classes**, in both splits.
646 routes contribute samples, out of the 843 drives the collector finished. Of the other 197,
73 were skipped outright (a disqualifying infraction, an incomplete route, or a CARLA physics
glitch -- `curation_skipped_logs.json`), 1 errored as too short to sample at all
(`conversion_errors.json`), and the remaining 123 had every clip filtered out for being under
17.5 s or covering under 5 m. 11 towns (Town01-07, Town10HD, Town12, Town13, Town15),
41 scenario types with curated samples.

## The five manoeuvre classes

`nav_maneuver` is one of `STRAIGHT`, `TURN_LEFT`, `TURN_RIGHT`, `SWERVE_LEFT`, `SWERVE_RIGHT`.
Only `nav_text` reaches the model:

| class | `nav_text` |
| --- | --- |
| `STRAIGHT` | `Continue straight` |
| `TURN_LEFT` / `TURN_RIGHT` | `Turn left in 11m` / `Turn right in 11m` |
| `SWERVE_LEFT` / `SWERVE_RIGHT` | `Change lane left in 11m` / `Change lane right in 11m` |

NVIDIA's reference nav annotations (`nav_demo_samples.json`: 17 `TURN_LEFT`, 3 `TURN_RIGHT`)
contain no lateral class and no straight class, so the `Continue straight` and `Change lane`
wordings are this dataset's own.

**A turn is a junction turn.** Whether a manoeuvre happens at a junction is decided by the map,
not by the scenario's name: the py123d maps shipped with LEAD carry `MapLayer.INTERSECTION`
surfaces, and a manoeuvre whose apex is not inside one is not a turn.

**A swerve is a mapped lane departure.** Route shape cannot tell a lane change from a bend in
the road -- on a driven path a 3.5 m / 30 m lane change, a gentle S-bend and 0.3 m of
lane-keeping wobble are all "swing out and return", and a two-degree error in the estimated
approach heading grows into a false 1.75 m of lateral offset over 40 m. So a swerve is instead
a step to a lane that is **not a successor** of the current one, outside a junction, with its
direction taken from the two lanes' centerlines. An obstacle bypass therefore yields two
labelled manoeuvres: the swerve out and the merge back, each with its own direction.

## The mix, and why v3's was wrong

v3 came out **22 % straight, 15 % / 15 % junction turns, 36 % / 12 % swerves**: lane changes and
bypasses together outweighed straight driving three to one, which is not how anything drives.
That was a curation bug, not a property of the recordings. Curation balanced junction turns 1:1
and then capped straight at `1.0 x junction turns`, while a swerve had **no quota at all** -- so
the cap ignored swerves on both sides. Straight was pinned to 1.0 x (699 + 699) = 1,398 samples
although **6,981 verified straight samples existed**, and every verified swerve went in whole:

| class (v3 train) | verified and available | kept by v3 |
| --- | --- | --- |
| STRAIGHT | 6,981 | 1,398 |
| TURN_LEFT | 2,078 | 932 |
| TURN_RIGHT | 932 | 932 |
| SWERVE_LEFT | 2,720 | 2,401 |
| SWERVE_RIGHT | 803 | 777 |

v4 gives a swerve the same standing as a junction turn: **all four lateral classes at one count,
straight at 50 %**. Nothing about the drives, labels or verification changed -- only which
samples the annotation files select.

**The scarce class is `SWERVE_RIGHT`, and v4 uses all of it.** In right-hand traffic a bypass
leaves to the left, and the merge back is the shorter leg that more often fails the driven-path
check, so right swerves are the bottleneck; `TURN_RIGHT` is second. Equal classes therefore size
the whole set from `SWERVE_RIGHT`, which is why v4 samples every **0.4 s** instead of every 1 s:
at a 1 s stride this mix tops out at 7,112 samples, because the right-swerve pool is exhausted.
0.4 s is the finest stride at which two neighbouring samples still share no camera frames (the
4-image stack spans t0 - 0.3 s ... t0).

Be clear about what the stride buys: **sample count, not scene diversity.** It is the same
1,840 clips from the same 843 drives as v3, and neighbouring samples still share most of
their 6.4 s future. What differs between them is the phase of the manoeuvre and the distance in
`nav_text`. Hold out by route, never by sample (the splits here already are: no route appears in
both).

### Per scenario

| scenario | straight | junction L | junction R | swerve L | swerve R | total |
| --- | --- | --- | --- | --- | --- | --- |
| ConstructionObstacleTwoWays | 626 | 65 | 239 | 598 | 328 | 1856 |
| VehicleTurningRoute | 351 | 382 | 614 | 0 | 0 | 1347 |
| noScenarios | 730 | 82 | 156 | 180 | 88 | 1236 |
| ConstructionObstacle | 473 | 8 | 41 | 240 | 353 | 1115 |
| Accident | 476 | 0 | 10 | 188 | 254 | 928 |
| HighwayExit | 323 | 0 | 0 | 0 | 489 | 812 |
| AccidentTwoWays | 224 | 0 | 79 | 331 | 115 | 749 |
| ControlLoss | 618 | 0 | 97 | 19 | 5 | 739 |
| DynamicObjectCrossing | 519 | 33 | 114 | 12 | 0 | 678 |
| ParkedObstacle | 185 | 35 | 4 | 202 | 140 | 566 |
| RedLightWithoutLeadVehicle | 139 | 329 | 0 | 0 | 0 | 468 |
| PedestrianCrossing | 180 | 54 | 219 | 0 | 0 | 453 |
| HardBreakRoute | 364 | 10 | 34 | 6 | 27 | 441 |
| HighwayCutIn | 346 | 0 | 0 | 0 | 89 | 435 |
| MergerIntoSlowTraffic | 260 | 0 | 0 | 31 | 120 | 411 |
| OppositeVehicleRunningRedLight | 306 | 28 | 0 | 0 | 30 | 364 |
| HazardAtSideLane | 207 | 0 | 0 | 49 | 59 | 315 |
| BlockedIntersection | 313 | 0 | 0 | 0 | 0 | 313 |
| VehicleTurningRoutePedestrian | 78 | 228 | 0 | 0 | 0 | 306 |
| PriorityAtJunction | 246 | 0 | 30 | 7 | 0 | 283 |
| InterurbanAdvancedActorFlow | 83 | 192 | 0 | 1 | 0 | 276 |
| OppositeVehicleTakingPriority | 275 | 0 | 0 | 0 | 0 | 275 |
| HazardAtSideLaneTwoWays | 107 | 0 | 74 | 61 | 20 | 262 |
| NonSignalizedJunctionRightTurn | 0 | 0 | 250 | 0 | 0 | 250 |
| MergerIntoSlowTrafficV2 | 173 | 0 | 0 | 0 | 76 | 249 |
| ParkedObstacleTwoWays | 26 | 48 | 10 | 134 | 21 | 239 |
| SignalizedJunctionLeftTurn | 73 | 155 | 0 | 6 | 0 | 234 |
| NonSignalizedJunctionLeftTurn | 9 | 218 | 0 | 0 | 0 | 227 |
| InterurbanActorFlow | 77 | 144 | 0 | 0 | 0 | 221 |
| ParkingCutIn | 161 | 0 | 41 | 0 | 0 | 202 |
| T_Junction | 193 | 0 | 0 | 0 | 0 | 193 |
| StaticCutIn | 172 | 10 | 0 | 1 | 0 | 183 |
| VehicleOpensDoorTwoWays | 22 | 0 | 75 | 73 | 6 | 176 |
| NonSignalizedJunctionLeftTurnEnterFlow | 50 | 113 | 7 | 0 | 0 | 170 |
| EnterActorFlowV2 | 118 | 0 | 0 | 40 | 0 | 158 |
| ParkingCrossingPedestrian | 143 | 0 | 9 | 0 | 0 | 152 |
| EnterActorFlow | 106 | 0 | 0 | 41 | 0 | 147 |
| InvadingTurn | 111 | 10 | 0 | 0 | 0 | 121 |
| SignalizedJunctionRightTurn | 8 | 0 | 78 | 0 | 0 | 86 |
| SignalizedJunctionLeftTurnEnterFlow | 9 | 76 | 0 | 0 | 0 | 85 |
| CrossingBicycleFlow | 0 | 0 | 39 | 0 | 0 | 39 |
| **total (41 scenarios)** | **8880** | **2220** | **2220** | **2220** | **2220** | **17760** |

## Curation

Applied in this order, per split, in a hash order so it is reproducible:

1. **Clean expert drives only** -- the collector's result JSON must show a finished route with no
   infraction, and the ego must not hit a CARLA physics glitch (`ego_physics_issue`: falling
   through the map or flipping).
2. **Driven-path-verified labels only** (`turn_check == "ok"`). A junction turn must hold its new
   heading past 30 deg both 20 m and 40 m beyond the apex. A swerve must deviate from the
   **median road heading over +/-40 m around the apex** in the commanded direction -- a reference
   taken just before the apex does not work, because the two legs of a bypass are often only
   25 m apart. A label whose apex lies beyond the driven path is `unjudged` and dropped; a
   straight that turns more than 60 deg within the 6.4 s future is `contradicted` and dropped.
3. **The mix**: the four lateral classes at one count, set by the scarcest of them, and straight
   at 50 % of the result. Each class is drawn round-robin over clips, so it covers as many
   scenes as it can rather than stacking neighbouring `t0` of the same clip.
4. **Stationary kept under 10 %** (ego moves < 0.5 m over the whole 6.4 s future); it lands at
   1.7% here, against 10.0 % in v3, because moving samples fill the quotas first.

The val split is drawn by route, not by sample: routes join val in hash order while they still
help a turn direction reach `--val-fraction` (0.10 here) of its verified total, with one route
per scenario first for coverage. It holds 45 routes / 146 clips, 9.7 % of the samples.

`annotations_{train,val}_all.json` hold every 0.4 s sample before curation, with `turn_check`,
`stationary`, `future_path_m`, `speed_mps`, `scenario` and `hazard` per sample, so you can
re-curate differently -- a different mix needs no reconversion.
`metadata/nav_dense.parquet` carries a label at every 10 Hz t0 (for re-keying chain-of-causation
keyframes), not just the training samples.

## What changed since `lead-alpamayo-pai_large_v3`

- **The mix** (above): 50 % straight and four equal lateral classes, instead of 22 % straight and
  a 3:1 left-heavy swerve majority.
- **Sample stride 1 s -> 0.4 s**, which is what makes the balanced mix 2.5x larger
  (17,760 vs 7,066 samples) rather than smaller.
- **Same recordings, same labels, same verification.** The clips, cameras, egomotion,
  `turn_check` rules and the 20 s clip timeline are identical.
- v3 stays published, unchanged, so its numbers remain reproducible. Prefer v4 for training; use
  v3 only to reproduce v3.

## Verification

Every snapshot is checked through the recipe's own loader (`PAIDatasetWithNav`), not just by
reading files: trajectories are compared against the raw LEAD logs, and the clip timeline
contract is re-derived.

- max trajectory error vs raw LEAD **0.00 cm** (history and future, both splits);
- clip timeline contract: **1,840 clips, 4 cameras, 17.5-20.0 s, 0 failures**;
- manoeuvre direction agreement **28/28** judged, on 150 samples stratified 30 per class.

Two caveats on that last line, both of them limits of the *spot-check*, not of the labels (every
kept label is verified at conversion time by `nav.check_swerve` against the median road heading,
which is curvature-robust and covers all 17,760 samples):

- the offset is measured in the fixed t0 frame, so a road bending 11° over 129 m produces more
  offset than a lane change does; swerves on a bend are reported *not judged* (16 of them here)
  rather than judged wrongly;
- a 6.4 s future can contain the manoeuvre *after* the commanded one — at 48 m of path, one
  sample swings +1.6 m left at 10 m as commanded and then −3.2 m right at 36 m — so the check
  reads the first lateral excursion past 1 m, not the largest.

## Known limits

- **Simulation.** CARLA 0.9.16, a privileged expert, 11 maps. No real-world images.
- **Nav text is synthesised** from the route polyline, not from a navigation service, and the
  `Change lane` wording is this dataset's own invention (see above).
- **Neighbouring samples are correlated.** 0.4 s apart inside a 20 s clip: disjoint images, but
  heavily overlapping futures. Treat the route, not the sample, as the independent unit.
- **`SWERVE_RIGHT` is used in full**, so this release cannot be made larger at this mix without
  new collection; the other four classes have reserve left in `*_all.json`.
- **No chain-of-causation labels.** `clip_ids_autolabel.txt` lists the clips long enough for
  NVIDIA's CoC auto-labeler; merging its output is supported by `lead2alpa-merge-coc`.
- Earlier releases `lead-alpamayo-pai_test`, `_medium`, `_large`, `_large_v2` and `_large_v3` are
  kept as they were and are **not** updated by this one.

## Licence

MIT, for the LEAD/CARLA recordings and everything derived from them in this repository. No
Bench2Drive-derived files are included.
