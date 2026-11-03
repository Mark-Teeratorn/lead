# Extracted Per-Route Data: Flooded-1600 & Flooded-6400

This document extracts the complete closed-loop evaluation records for both **Hazard-Flooded** models across all 44 canonical Bench2Drive routes without running any new simulation tests.

### Summary
- **Flooded-1600**: Mean DS = 45.77, Mean RC = 77.4%, Total Crashes = 49
- **Flooded-6400**: Mean DS = 49.04, Mean RC = 77.8%, Total Crashes = 57

### Complete 44-Route Table

| Route ID | Scenario Name | Flooded-1600 DS | Flooded-1600 RC | Crashes (1.6k) | Flooded-6400 DS | Flooded-6400 RC | Crashes (6.4k) | Delta DS (6.4k - 1.6k) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1711** | ParkingCutIn_1 | 100.0 | 100.0% | 0 | 100.0 | 100.0% | 0 | +0.0 |
| **1773** | ParkedObstacle_1 | 13.0 | 100.0% | 4 | 36.0 | 100.0% | 2 | +23.0 |
| **1790** | HazardAtSideLane_1 | 2.8 | 100.0% | 7 | 4.7 | 100.0% | 6 | +1.9 |
| **1825** | ConstructionObstacleTwoWays_1 | 12.6 | 34.9% | 2 | 3.5 | 27.3% | 4 | -9.0 |
| **1852** | AccidentTwoWays_1 | 60.0 | 100.0% | 1 | 36.0 | 100.0% | 2 | -24.0 |
| **1956** | ParkingExit_1 | 1.9 | 3.1% | 1 | 1.9 | 3.1% | 1 | +0.0 |
| **2050** | SignalizedJunctionRightTurn_1 | 7.7 | 30.6% | 0 | 100.0 | 100.0% | 0 | +92.3 |
| **2082** | OppositeVehicleRunningRedLight_1 | 38.5 | 39.9% | 0 | 53.6 | 56.2% | 0 | +15.1 |
| **2084** | NonSignalizedJunctionLeftTurn_1 | 60.0 | 100.0% | 1 | 17.1 | 47.5% | 2 | -42.9 |
| **2115** | NonSignalizedJunctionRightTurn_1 | 58.5 | 100.0% | 1 | 32.1 | 100.0% | 2 | -26.5 |
| **2127** | OppositeVehicleTakingPriority_1 | 12.6 | 73.9% | 1 | 54.6 | 54.6% | 0 | +42.1 |
| **2144** | VehicleTurningRoute_1 | 33.7 | 56.2% | 1 | 34.1 | 100.0% | 2 | +0.3 |
| **2164** | VehicleTurningRoutePedestrian_1 | 50.3 | 50.3% | 0 | 40.2 | 50.3% | 0 | -10.1 |
| **2201** | EnterActorFlow_1 | 42.0 | 100.0% | 1 | 32.1 | 45.9% | 0 | -9.9 |
| **2204** | BlockedIntersection_1 | 16.8 | 77.6% | 3 | 45.7 | 45.7% | 0 | +28.9 |
| **2283** | MergerIntoSlowTraffic_1 | 93.6 | 93.6% | 0 | 98.6 | 98.6% | 0 | +5.0 |
| **2286** | HighwayCutIn_1 | 100.0 | 100.0% | 0 | 36.0 | 100.0% | 2 | -64.0 |
| **2390** | VanillaNonSignalizedTurn_1 | 31.4 | 31.4% | 0 | 41.1 | 42.5% | 0 | +9.8 |
| **2416** | VanillaNonSignalizedTurnEncounterStopsign_1 | 80.0 | 100.0% | 0 | 100.0 | 100.0% | 0 | +20.0 |
| **2513** | ConstructionObstacle_1 | 13.0 | 100.0% | 4 | 21.6 | 100.0% | 3 | +8.6 |
| **2534** | Accident_1 | 36.0 | 100.0% | 2 | 7.8 | 100.0% | 5 | -28.2 |
| **2664** | ParkedObstacleTwoWays_1 | 94.7 | 100.0% | 0 | 97.0 | 100.0% | 0 | +2.3 |
| **2709** | StaticCutIn_1 | 21.6 | 100.0% | 3 | 21.6 | 100.0% | 3 | +0.0 |
| **2790** | InvadingTurn_1 | 36.0 | 100.0% | 2 | 60.0 | 100.0% | 1 | +24.0 |
| **3086** | CrossingBicycleFlow_1 | 43.7 | 43.7% | 0 | 43.7 | 43.7% | 0 | +0.0 |
| **3144** | VanillaSignalizedTurnEncounterRedLight_1 | 12.9 | 32.1% | 1 | 70.0 | 100.0% | 0 | +57.1 |
| **3248** | ParkingCrossingPedestrian_1 | 100.0 | 100.0% | 0 | 60.0 | 100.0% | 1 | -40.0 |
| **3364** | YieldToEmergencyVehicle_1 | 42.0 | 100.0% | 1 | 70.0 | 100.0% | 0 | +28.0 |
| **3436** | HazardAtSideLaneTwoWays_1 | 1.0 | 6.1% | 1 | 1.5 | 50.0% | 7 | +0.5 |
| **3464** | VehicleOpensDoorTwoWays_1 | 58.2 | 100.0% | 1 | 60.0 | 100.0% | 1 | +1.8 |
| **3540** | HardBreakRoute_1 | 17.3 | 100.0% | 3 | 2.8 | 88.0% | 6 | -14.6 |
| **3561** | ControlLoss_1 | 56.8 | 100.0% | 1 | 100.0 | 100.0% | 0 | +43.2 |
| **3936** | SignalizedJunctionLeftTurn_1 | 39.6 | 39.6% | 0 | 27.7 | 46.2% | 1 | -11.9 |
| **14194** | PedestrianCrossing_1 | 25.2 | 42.1% | 1 | 18.0 | 50.0% | 2 | -7.2 |
| **14842** | VanillaSignalizedTurnEncounterGreenLight_1 | 14.1 | 20.2% | 0 | 20.2 | 20.2% | 0 | +6.1 |
| **17563** | SequentialLaneChange_1 | 60.0 | 100.0% | 1 | 21.6 | 100.0% | 3 | -38.4 |
| **17752** | DynamicObjectCrossing_1 | 56.4 | 100.0% | 1 | 90.9 | 100.0% | 0 | +34.6 |
| **23687** | HighwayExit_1 | 54.7 | 100.0% | 1 | 100.0 | 100.0% | 0 | +45.3 |
| **23695** | InterurbanAdvancedActorFlow_1 | 96.1 | 100.0% | 0 | 94.8 | 100.0% | 0 | -1.3 |
| **23771** | MergerIntoSlowTrafficV2_1 | 100.0 | 100.0% | 0 | 100.0 | 100.0% | 0 | +0.0 |
| **23901** | InterurbanActorFlow_1 | 51.3 | 100.0% | 1 | 49.8 | 100.0% | 1 | -1.5 |
| **26458** | T_Junction_1 | 10.9 | 32.4% | 1 | 52.2 | 52.2% | 0 | +41.3 |
| **28087** | NonSignalizedJunctionLeftTurnEnterFlow_1 | 100.0 | 100.0% | 0 | 56.1 | 56.1% | 0 | -43.9 |
| **28099** | SignalizedJunctionLeftTurnEnterFlow_1 | 56.8 | 100.0% | 1 | 43.0 | 43.0% | 0 | -13.8 |
