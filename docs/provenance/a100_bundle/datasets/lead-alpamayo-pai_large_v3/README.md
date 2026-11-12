---
license: mit
pretty_name: LEAD Alpamayo PAI (large v3)
tags:
- autonomous-driving
- carla
- alpamayo
- physical-ai-av
- trajectory-prediction
- navigation
size_categories:
- 1K<n<10K
---

# LEAD Alpamayo PAI: large v3 (five-way manoeuvre labels, complete collection)

CARLA 0.9.16 expert driving from [LEAD](https://huggingface.co/datasets/ln2697/lead-123d),
re-collected with the four NVIDIA Alpamayo 1.5 input cameras added, and converted to the
NVIDIA PhysicalAI-AV (PAI) on-disk format. It is read unchanged by
[alpamayo-recipes](https://github.com/NVlabs/alpamayo-recipes) Alpamayo 1.5 nav SFT
(`PAIDatasetWithNav`). Built with [lead2alpa](https://github.com/Silicon-Melter/lead2alpa).

A single CARLA pass recorded LEAD's own sensors, the Alpamayo cameras and a Bench2Drive rig
(for a separate HiP-AD project; not included here) at once. **Collection is complete**: it ran
2026-09-25 through 2026-10-05, ending when the planned route list was exhausted at 574 GB on
disk, and this snapshot converts every log it produced.

**The headline change from v2 is the label set.** v2 had three classes, and its "turns"
silently included lane changes and obstacle bypasses. v3 separates them: junction turns are
turns, lateral manoeuvres are their own class, and the two are never mixed.

| | train | val |
| --- | --- | --- |
| routes / clips | 601 / 1,694 | 45 / 146 |
| nav samples | **6,440** | **626** |
| straight | 1,398 | 160 |
| junction left / right | 932 / 932 | 102 / 102 |
| swerve left / right | 2,401 / 777 | 176 / 86 |
| stationary samples | 10.0 % | 9.9 % |
| all 1 s samples before curation (`*_all.json`) | 16,977 | 1,483 |

646 curated routes out of 843 LEAD logs the collector finished (77 %); 73 logs were dropped for
infractions, incompleteness, an ego-physics glitch or being too short to sample, and 1 errored
(see `curation_skipped_logs.json` and `conversion_errors.json`). 11 towns (Town01-07, Town10HD,
Town12, Town13, Town15), 41 scenario types with curated samples.

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
the road — on a driven path a 3.5 m / 30 m lane change, a gentle S-bend and 0.3 m of
lane-keeping wobble are all "swing out and return", and a two-degree error in the estimated
approach heading grows into a false 1.75 m of lateral offset over 40 m. So a swerve is instead
a step to a lane that is **not a successor** of the current one, outside a junction, with its
direction taken from the two lanes' centerlines. An obstacle bypass therefore yields two
labelled manoeuvres: the swerve out and the merge back, each with its own direction.

### Balance

Junction turns are balanced **exactly 1:1** (932/932 train, 102/102 val) and the straight cap is
sized off them, which lands the junction-only split at **42.9 / 28.6 / 28.6 %**
(straight / left / right) in train.

Swerves are deliberately **not** quota'd and are left-heavy, **2,577 : 863 (3.0:1)** over both
splits. In right-hand traffic a bypass leaves to the left and the merge back is the shorter leg,
which more often fails the driven-path check. If you need lateral balance, subsample
`SWERVE_LEFT`; do not rebalance by discarding junction turns.

### Per scenario

| scenario | straight | junction L | junction R | swerve L | swerve R | total |
| --- | --- | --- | --- | --- | --- | --- |
| ConstructionObstacleTwoWays | 120 | 37 | 159 | 709 | 135 | 1160 |
| AccidentTwoWays | 41 | 0 | 44 | 427 | 44 | 556 |
| ConstructionObstacle | 87 | 2 | 29 | 289 | 131 | 538 |
| noScenarios | 141 | 38 | 60 | 229 | 34 | 502 |
| VehicleTurningRoute | 47 | 180 | 254 | 0 | 0 | 481 |
| Accident | 82 | 0 | 4 | 215 | 88 | 389 |
| ParkedObstacle | 29 | 4 | 1 | 208 | 54 | 296 |
| HighwayExit | 46 | 0 | 0 | 0 | 199 | 245 |
| RedLightWithoutLeadVehicle | 20 | 182 | 0 | 0 | 0 | 202 |
| DynamicObjectCrossing | 107 | 21 | 49 | 15 | 0 | 192 |
| ParkedObstacleTwoWays | 2 | 18 | 4 | 161 | 6 | 191 |
| ControlLoss | 124 | 0 | 40 | 22 | 1 | 187 |
| PedestrianCrossing | 26 | 46 | 107 | 0 | 0 | 179 |
| VehicleTurningRoutePedestrian | 10 | 120 | 0 | 0 | 0 | 130 |
| MergerIntoSlowTraffic | 56 | 0 | 0 | 21 | 48 | 125 |
| HazardAtSideLaneTwoWays | 20 | 0 | 30 | 67 | 8 | 125 |
| VehicleOpensDoorTwoWays | 2 | 0 | 46 | 72 | 2 | 122 |
| HazardAtSideLane | 30 | 0 | 0 | 59 | 25 | 114 |
| HighwayCutIn | 75 | 0 | 0 | 0 | 35 | 110 |
| NonSignalizedJunctionRightTurn | 0 | 0 | 101 | 0 | 0 | 101 |
| InterurbanAdvancedActorFlow | 12 | 79 | 0 | 0 | 0 | 91 |
| NonSignalizedJunctionLeftTurn | 1 | 85 | 0 | 0 | 0 | 86 |
| SignalizedJunctionLeftTurn | 8 | 66 | 0 | 7 | 0 | 81 |
| HardBreakRoute | 48 | 2 | 13 | 6 | 10 | 79 |
| PriorityAtJunction | 52 | 0 | 12 | 12 | 0 | 76 |
| OppositeVehicleRunningRedLight | 52 | 7 | 0 | 0 | 12 | 71 |
| NonSignalizedJunctionLeftTurnEnterFlow | 12 | 48 | 2 | 0 | 0 | 62 |
| MergerIntoSlowTrafficV2 | 28 | 0 | 0 | 0 | 31 | 59 |
| InterurbanActorFlow | 6 | 51 | 0 | 0 | 0 | 57 |
| OppositeVehicleTakingPriority | 57 | 0 | 0 | 0 | 0 | 57 |
| ParkingCutIn | 25 | 0 | 30 | 0 | 0 | 55 |
| EnterActorFlowV2 | 24 | 0 | 0 | 30 | 0 | 54 |
| EnterActorFlow | 16 | 0 | 0 | 28 | 0 | 44 |
| SignalizedJunctionLeftTurnEnterFlow | 0 | 41 | 0 | 0 | 0 | 41 |
| BlockedIntersection | 37 | 0 | 0 | 0 | 0 | 37 |
| ParkingCrossingPedestrian | 34 | 0 | 3 | 0 | 0 | 37 |
| StaticCutIn | 34 | 1 | 0 | 0 | 0 | 35 |
| SignalizedJunctionRightTurn | 1 | 0 | 31 | 0 | 0 | 32 |
| T_Junction | 27 | 0 | 0 | 0 | 0 | 27 |
| InvadingTurn | 19 | 6 | 0 | 0 | 0 | 25 |
| CrossingBicycleFlow | 0 | 0 | 15 | 0 | 0 | 15 |
| **total (41 scenarios)** | **1558** | **1034** | **1034** | **2577** | **863** | **7066** |
## Curation

Applied in this order, per split, in a hash order so it is reproducible:

1. **Clean expert drives only** — the collector's result JSON must show a finished route with no
   infraction, and the ego must not hit a CARLA physics glitch (`ego_physics_issue`: falling
   through the map or flipping).
2. **Driven-path-verified labels only** (`turn_check == "ok"`). A junction turn must hold its new
   heading past 30° both 20 m and 40 m beyond the apex. A swerve must deviate from the **median
   road heading over ±40 m around the apex** in the commanded direction — a reference taken just
   before the apex does not work, because the two legs of a bypass are often only 25 m apart. A
   label whose apex lies beyond the driven path is `unjudged` and dropped; a straight that turns
   more than 60° within the 6.4 s future is `contradicted` and dropped.
3. **Exact 1:1 junction turns**, straight capped against them, swerves kept as they are.
4. **Stationary capped at 10 %** (ego moves < 0.5 m over the whole 6.4 s future).

`annotations_{train,val}_all.json` hold every 1 s sample before curation, with
`turn_check`, `stationary`, `future_path_m`, `speed_mps`, `scenario` and `hazard` per sample, so
you can re-curate differently. `metadata/nav_dense.parquet` carries a label at every 10 Hz t0
(for re-keying chain-of-causation keyframes), not just the 1 s training samples.

## What changed since `lead-alpamayo-pai_large_v2`

- **Five manoeuvre classes instead of three** (above). About 12 % of v2's verified "turns" were
  lane changes or bypasses; they are now `SWERVE_*`. v2's turn counts are therefore **not**
  comparable with v3's: its 1,067/1,067 junction turns become 932/932 here even though the
  dataset grew, because the mislabelled ones moved out.
- **Samples 2,627 → 7,066** (routes 441 → 646). Part is the extra collection; most is that
  verified swerves are now kept instead of being dropped as contradicted turns or labelled
  straight.
- **Collection is finished.** v2 was a mid-collection snapshot (stopped by hand at 418 GB); this
  covers the whole planned route list, including a 224-route pass targeted at the scenarios the
  earlier set under-covered.
- Unchanged: the PAI layout, the camera rig, the 20 s clip timeline, the trajectory contract and
  the clean-drive / stationary rules.

## Verification

Every snapshot is checked through the recipe's own loader (`PAIDatasetWithNav`), not just by
reading files: trajectories are compared against the raw LEAD logs, and the clip timeline
contract is re-derived.

- max trajectory error vs raw LEAD **0.00 cm** (history and future, both splits);
- clip timeline contract: **1,840 clips, 4 cameras, 17.5-20.0 s, 0 failures**;
- manoeuvre direction agreement on the sampled subset: all judged samples agree.

A caveat on that last line: a swerve's direction is only checked where the road is straight. The
check measures lateral offset in the fixed t0 frame, and a road bending 11° over 129 m produces
more offset than the lane change itself, so swerves on a bend are reported as *not judged*
rather than judged wrongly.

## Known limits

- **Simulation.** CARLA 0.9.16, a privileged expert, 11 maps. No real-world images.
- **Nav text is synthesised** from the route polyline, not from a navigation service, and the
  `Change lane` wording is this dataset's own invention (see above).
- **Swerve direction is left-heavy** 3:1 by design.
- **No chain-of-causation labels.** `clip_ids_autolabel.txt` lists the 1,840 clips long enough
  for NVIDIA's CoC auto-labeler; merging its output is supported by `lead2alpa-merge-coc`.
- Earlier releases `lead-alpamayo-pai_test`, `_medium`, `_large` and `_large_v2` are kept as they
  were and are **not** updated by this one.

## Licence

MIT, for the LEAD/CARLA recordings and everything derived from them in this repository. No
Bench2Drive-derived files are included.
