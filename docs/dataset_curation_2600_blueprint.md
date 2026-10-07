# Dataset Curation Blueprint: Scaling to 2,600 Curated Samples

This document defines the curation specifications, directional balance, and exact scenario allocation to scale the Action Expert training dataset from **1,384 to 2,600 samples**. 

The goal of this curation blueprint is to eliminate data starvation on critical maneuvers (such as narrow construction detours, signalized red lights, and ramp curves) and elevate the Bench2Drive Driving Score (DS) from **72.2 to 95+**.

---

## 1. Directional Maneuver Distribution

In uncurated driving datasets, straight driving dominates (>65%), causing models to develop a severe "straight bias" (blowing through turns or failing to initiate detours). The 2,600-sample dataset enforces a balanced directional split:

| Maneuver | Option A: Proven 2:1:1 Ratio (Consistent with 1,384 Set) | Option B: 4:3:3 Ratio (Optimized for Detour & Turn Agility) | Purpose |
| :--- | :---: | :---: | :--- |
| **STRAIGHT** | **50.0% (1,300 samples)** | **40.0% (1,040 samples)** | Basic lane keeping, cruising, and in-lane emergency stops |
| **TURN_LEFT** | **25.0% (650 samples)** | **30.0% (780 samples)** | Unprotected junction turns, lane merges, and left obstacle nudges |
| **TURN_RIGHT** | **25.0% (650 samples)** | **30.0% (780 samples)** | Signalized/uncontrolled right turns, shoulder returns, off-ramps |
| **Total** | **100.0% (2,600 samples)** | **100.0% (2,600 samples)** | |

> **Note on Detour Labeling:** When bypassing obstacles (`ConstructionObstacle`, `ParkedObstacle`), the initial steering phase around the obstacle is classified under **`TURN_LEFT`** and the return merge back into the lane is classified under **`TURN_RIGHT`**. Under Option A, this naturally balances the policy.

---

## 2. High-Level Category Scaling (1,384 $\to$ 2,600)

| Category Type | 1,384 Count | 1,384 % | **2,600 Count** | **2,600 %** | Strategic Adjustment Rationale |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **A. Turning & Junction Maneuvers** | 401 | 28.97% | **750** | **28.85%** | Fills missing right turns and strengthens uncontrolled junction yielding |
| **B. Obstacle Bypass & Avoidance** | 364 | 26.30% | **750** | **28.85%** | **Heavily boosted (+106%)** to eliminate the Route 2513 bottleneck |
| **C. General Driving & Vehicle Control** | 234 | 16.91% | **340** | **13.08%** | Downweights repetitive highway cruising to prevent straight-bias |
| **D. Pedestrians & Vulnerable Road Users** | 164 | 11.85% | **280** | **10.77%** | Teaches strict in-lane braking (fixes Route 14194 swerving) |
| **E. Highway, Merging & Cut-ins** | 135 | 9.75% | **280** | **10.77%** | Boosts Highway Exit (was starved at only 6 samples!) |
| **F. Traffic Light & Intersection Rules** | 86 | 6.21% | **200** | **7.69%** | Enforces hard stops behind the stop bar (fixes Route 3144 red light) |
| **Total** | **1,384** | **100.00%** | **2,600** | **100.00%** | |

---

## 3. Granular Scenario Breakdown (All 39 Scenarios)

### Category A: Turning & Junction Maneuvers (750 samples, 28.85%)
* `VehicleTurningRoute`: **320** *(Standard route-guided intersection turns)*
* `NonSignalizedJunctionRightTurn`: **90** *(Uncontrolled junction right turns, up from 61)*
* `NonSignalizedJunctionLeftTurn`: **70** *(Uncontrolled junction left turns, up from 20)*
* `NonSignalizedJunctionLeftTurnEnterFlow`: **60** *(Yielding and merging into moving traffic, up from 35)*
* **`SignalizedJunctionRightTurn`**: **50** 🚨 *(CRITICAL FIX: Was 0 / completely missing in the 1,384 set!)*
* `SignalizedJunctionLeftTurn`: **50** *(Protected/unprotected traffic light turns, up from 23)*
* `SignalizedJunctionLeftTurnEnterFlow`: **35** *(Protected green left turns into flow, up from 12)*
* `PriorityAtJunction`: **30** *(Yielding to priority cross-traffic, up from 8)*
* `BlockedIntersection`: **25** *(Stopping before gridlocked intersection boxes, up from 8)*
* `T_Junction`: **20** *(T-junction turning navigation, up from 9)*

---

### Category B: Obstacle Bypass & Avoidance (750 samples, 28.85%)
* **`ConstructionObstacle`**: **180** 🚨 *(CRITICAL FIX: Was starved at only 39 samples. 4.6× increase to stop grazing parked cars on Route 2513)*
* `ConstructionObstacleTwoWays`: **180** *(Cones/barriers pushing into opposing oncoming lane, up from 71)*
* `AccidentTwoWays`: **130** *(Two-way road crash scene bypass, up from 80)*
* `Accident`: **100** *(Single-lane crash scene bypass, up from 60)*
* `ParkedObstacle`: **70** *(Passing a parked car on single-lane road, up from 41)*
* `HazardAtSideLane`: **40** *(Shoulder obstacle navigation, up from 26)*
* `HazardAtSideLaneTwoWays`: **40** *(Shoulder hazard on two-way road, up from 34)*
* `ParkedObstacleTwoWays`: **30** *(Passing parked car into opposing traffic, up from 13)*

---

### Category C: General Driving & Vehicle Control (340 samples, 13.08%)
* `noScenarios` *(Clean cruising & lane keeping)*: **200** *(Intentionally capped from 150 to keep dataset rich in active maneuvers)*
* `ControlLoss`: **100** *(Recovery from traction loss, skidding, and wet asphalt, up from 73)*
* `HardBreakRoute`: **40** *(High-G emergency stop execution, up from 11)*

---

### Category D: Pedestrians & Vulnerable Road Users (280 samples, 10.77%)
* `DynamicObjectCrossing`: **110** *(Animals, bikes, or unexpected moving obstacles, up from 70)*
* **`PedestrianCrossing`**: **90** *(Teaches stopping in-lane without swerving over lane boundaries, up from 40)*
* `VehicleTurningRoutePedestrian`: **60** *(Yielding to crosswalk pedestrians while turning, up from 43)*
* `ParkingCrossingPedestrian`: **20** *(Pedestrians stepping out between parked cars, up from 11)*

---

### Category E: Highway, Merging & Cut-ins (280 samples, 10.77%)
* `InterurbanAdvancedActorFlow`: **60** *(Dense multi-vehicle high-speed traffic, up from 36)*
* **`HighwayExit`**: **50** 🚨 *(CRITICAL FIX: Was only 6 samples! Smooths exit ramp deceleration and prevents solid line clips)*
* `HighwayCutIn`: **35** *(Evasive speed adjustment when vehicle cuts into lane, up from 16)*
* `MergerIntoSlowTraffic`: **30** *(On-ramp merge into slow queue, up from 14)*
* `InterurbanActorFlow`: **30** *(Standard highway cruising, up from 17)*
* `StaticCutIn` & `ParkingCutIn`: **30** *(Vehicles pulling out from parking spaces, up from 19)*
* `VehicleOpensDoorTwoWays`: **25** *(Parked car suddenly swinging door open, up from 10)*
* `MergerIntoSlowTrafficV2`: **20** *(Secondary merge variant, up from 4)*

---

### Category F: Traffic Light & Intersection Rules (200 samples, 7.69%)
* **`RedLightWithoutLeadVehicle`**: **120** 🚨 *(CRITICAL FIX: Was 57. Teaches hard stop-line holding to prevent the instant 30-point red light penalty on Route 3144)*
* `OppositeVehicleRunningRedLight`: **45** *(Defensive stopping when cross traffic runs a red light, up from 18)*
* `OppositeVehicleTakingPriority`: **35** *(Yielding to oncoming traffic with right-of-way, up from 11)*

---

## 4. Root Cause Analysis (RCA) Fix Mapping

| Canonical Route | Scenario Name | Previous DS | Previous Bottleneck | Curation Fix | Projected New DS |
| :--- | :--- | :---: | :--- | :--- | :---: |
| **Route 2513** | `ConstructionObstacle` | **3.0** | Grazed 6 parked cars on shoulder due to 39-sample data starvation | Bumped from **39 $\to$ 180** samples with explicit lateral margin buffer | **95.0 (+92.0)** |
| **Route 3144** | `VanillaSignalizedTurnEncounterRedLight` | **70.0** | Inched past stop line while turning on red (-30% penalty) | Bumped `RedLightWithoutLeadVehicle` from **57 $\to$ 120** with stop-bar hold | **100.0 (+30.0)** |
| **Route 14194** | `PedestrianCrossing` | **90.7** | Swerved 7m outside lane while giving berth to pedestrian | Bumped from **40 $\to$ 90** samples enforcing strict **in-lane braking** | **100.0 (+9.3)** |
| **Route 23687** | `HighwayExit` | **97.4** | Clipped 3.9m over solid line on ramp curve | Bumped from **6 $\to$ 50** samples covering curved off-ramps | **100.0 (+2.6)** |
| **Route 2790** | `InvadingTurn` | **100.0** | Flawless | Maintained strong defensive turning representation | **100.0 (0.0)** |
| **Average** | **5 Canonical Abilities** | **72.2** | Compounding penalties on narrow detours & red lights | Targeted sample injection across all 4 starved categories | **99.0 (+26.8)** |

---

## 5. Curation Filtering Rules & Quality Gates

When your curation script selects the 2,600 samples from the master dataset (`annotations_train_all.json`):

1. **Zero-Infraction Filtering:**
   Only admit demonstrations where the expert achieved `score_composed == 100.0` and zero collisions. Discard any recording where the expert vehicle came within $< 0.4\text{m}$ of a static object.
2. **Deceleration Gate for Red Lights & Pedestrians:**
   Ensure each sample selected for Categories D and F contains at least 15–20 consecutive frames where ego velocity is $< 0.5\text{ km/h}$ behind the stop line.
3. **Hard Straight-Line Cap:**
   Cease collecting `Follow lane` / `noScenarios` once the straight bucket reaches its quota (1,040 to 1,300 samples) to prevent policy corruption.
4. **Town & Weather Diversity:**
   Ensure samples are distributed across Town01, Town03, Town04, Town06, and Town12, avoiding over-concentration in any single CARLA map.
