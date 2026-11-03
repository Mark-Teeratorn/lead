# 44-Route Benchmark Evaluation & Post-44 Controller Optimization Plan

## 1. Active Evaluation: Full 44 Canonical Scenarios Run
- **Target Model**: `checkpoint-20050` (Curated 6,400 Large Model)
- **Tag**: `model_v4_final`
- **Output Directory**: `outputs/local_evaluation/model_v4_final_<route_id>/`
- **Runner Script**: [`scripts/common/run_full_44_eval.sh`](file:///home/aimslab/lead/scripts/common/run_full_44_eval.sh)
- **Live Progress Log**: [`outputs/full_44_eval_progress.log`](file:///home/aimslab/lead/outputs/full_44_eval_progress.log)
- **Active Controller Baseline Configuration**:
  - `alpha_steer = 1.0` (Zero-latency steering responsiveness everywhere)
  - Standstill breakout torque (`raw_throttle >= 0.35` when path extent >= 2.5m)
  - 30 cm lateral deviation lookahead trigger (`lookahead_m = 2.8m - 4.5m`)
  - Initial stall rollout guard: 1.8m (`step < 25`)

---

## 2. Post-44 Controller Optimization Candidates (Roadmap)

Following our strict test-and-revert protocol, once the unified 44-route scorecard is generated, the following controller candidates will be evaluated in isolation on specific low-scoring failure routes:

| Candidate | Mechanism | Target Failure Modes | Candidate Target Routes | Hypothesis |
| :--- | :--- | :--- | :--- | :--- |
| **Candidate A: Full Steering Lock (`max_steering = 1.0`)** | Increase `max_steering` from `0.8` to `1.0` in `VehiclePIDController` | Understeer on sharp 90-degree intersection turns & T-junctions | Route 26458 (`T_Junction`), Route 2416 (`Stopsign Turn`) | Eliminates the artificial 20% turning angle limitation, preventing wide turn lane deviations. |
| **Candidate B: Zero-Lag Emergency Braking** | Decouple pedal smoothing: keep `alpha_throttle = 0.25`, but set `alpha_brake = 1.0` when `raw_brake > 0.3` | Tailgating collisions & cut-in accidents caused by 0.5s - 0.8s brake buildup lag | Route 2709 (`StaticCutIn`), Route 3364 (`YieldToEmergencyVehicle`) | Provides instant stopping torque when the vision model requests an emergency stop. |
| **Candidate C: Dynamic Evasion Speed Capping** | Limit target speed to 18-20 km/h during high lateral deviations (`max_lat_dev > 0.30`) | Lateral tire slip causing ego vehicle rear-corner grazes during obstacle bypass | Route 1790 (`HazardAtSideLane`), Route 2513 (`ConstructionObstacle`) | Maximizes tire lateral adhesion and path-tracking accuracy in tight corridors. |

---

## 3. Strict Decision Criteria
1. Evaluate candidate only on the selected benchmark failure route.
2. If Driving Score improves and no new infractions occur: **Keep and document**.
3. If Driving Score regresses or matches baseline: **Revert immediately**.
