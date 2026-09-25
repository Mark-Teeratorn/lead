#!/usr/bin/env python3
"""Alpamayo Bridge Agent for CARLA Bench2Drive / Fail2Drive.

Connects to the FlashDrive Alpamayo-1.5 model server over IPC, passes multi-view
camera streams and ego vehicle state, and tracks returned waypoints with PID controllers.
"""

import json
import math
import os
import pickle
import socket
import struct
import sys
from collections import deque
from dataclasses import dataclass
from typing import Any

import carla
import numpy as np


@dataclass(frozen=True)
class RawTargetWaypoint:
    """Minimal waypoint-like target for CARLA VehiclePIDController (Carlamayo style)."""
    transform: carla.Transform

# NumPy 2.x -> NumPy 1.x pickle compatibility shim.
# FlashDrive server runs on Python 3.12 with NumPy 2.x (which pickles objects as numpy._core),
# while Bench2Drive / CARLA runs on Python 3.10 with NumPy 1.x (which only has numpy.core).
if not hasattr(np, "_core"):
    import numpy.core as _c
    sys.modules["numpy._core"] = _c
    sys.modules["numpy._core.multiarray"] = _c.multiarray
    if hasattr(_c, "_multiarray_umath"):
        sys.modules["numpy._core._multiarray_umath"] = _c._multiarray_umath
    if hasattr(_c, "umath"):
        sys.modules["numpy._core.umath"] = _c.umath
    if hasattr(_c, "numerictypes"):
        sys.modules["numpy._core.numerictypes"] = _c.numerictypes

# Ensure CARLA 0.9.15 egg is accessible if running under 0.9.15
EGG_0915 = "/home/aimslab/lead/3rd_party/CARLA/fail2drive_0915/PythonAPI/carla/dist/carla-0.9.15-py3.10-linux-x86_64.egg"
if os.path.exists(EGG_0915) and EGG_0915 not in sys.path:
    sys.path.insert(0, EGG_0915)

from leaderboard.autoagents.autonomous_agent import AutonomousAgent, Track

DEFAULT_SOCKET_PATH = "/tmp/alpamayo_flashdrive.sock"
DEFAULT_TCP_PORT = 5555


def send_msg(sock: socket.socket, data: Any) -> None:
    payload = pickle.dumps(data, protocol=5)
    sock.sendall(struct.pack("!I", len(payload)) + payload)


def recv_msg(sock: socket.socket) -> Any:
    raw_len = sock.recv(4)
    if not raw_len:
        return None
    msg_len = struct.unpack("!I", raw_len)[0]
    chunks = []
    bytes_recd = 0
    while bytes_recd < msg_len:
        chunk = sock.recv(min(msg_len - bytes_recd, 65536))
        if not chunk:
            raise ConnectionError("Socket closed while reading payload")
        chunks.append(chunk)
        bytes_recd += len(chunk)
    return pickle.loads(b"".join(chunks))


def get_entry_point():
    return "AlpamayoBridgeAgent"


class AlpamayoBridgeAgent(AutonomousAgent):
    """Bridge Agent communicating with external Python 3.12 FlashDrive server."""

    def setup(self, path_to_conf_file: str) -> None:
        self.track = Track.SENSORS
        self.step_idx = 0
        self.num_cam_frames = 4
        self.history_traj_len = 16  # Alpamayo 1.5 expects 16 steps (48 tokens)
        self.pose_history = deque(maxlen=60)  # (timestamp, carla.Transform) for ~3s at 20 Hz
        self.history_frames = deque(maxlen=self.num_cam_frames)

        # Trajectory logging
        self._save_path = os.environ.get("SAVE_PATH", None)
        self._traj_log_file = None
        if self._save_path:
            os.makedirs(self._save_path, exist_ok=True)
            self._traj_log_file = open(
                os.path.join(self._save_path, "predicted_trajectories.jsonl"), "a"
            )

        # CARLA debug drawing (spectator view)
        self._debug_draw = os.environ.get("ALPAMAYO_DEBUG_DRAW", "1") == "1"

        # Official CARLA VehiclePIDController (Carlamayo architecture)
        self.pid_controller = None

        # Control smoothing (Carlamayo exponential filter, alpha = 0.25)
        self.control_smooth_alpha = 0.25
        self.prev_steer = 0.0
        self.prev_throttle = 0.0
        self.prev_brake = 0.0

        # IPC connection
        self.sock = None
        self._connect_to_server()

    def _connect_to_server(self) -> None:
        """Connect to FlashDrive server over UNIX socket or TCP."""
        if os.path.exists(DEFAULT_SOCKET_PATH):
            try:
                s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                s.connect(DEFAULT_SOCKET_PATH)
                self.sock = s
                print(f"[AlpamayoBridgeAgent] Connected to model server via UNIX socket {DEFAULT_SOCKET_PATH}")
                # Test handshake
                send_msg(self.sock, {"cmd": "ping"})
                res = recv_msg(self.sock)
                if res and res.get("status") == "pong":
                    print("[AlpamayoBridgeAgent] Handshake successful.")
                return
            except Exception as e:
                print(f"[AlpamayoBridgeAgent] UNIX socket connection failed ({e}), trying TCP...")

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("127.0.0.1", DEFAULT_TCP_PORT))
            self.sock = s
            print(f"[AlpamayoBridgeAgent] Connected to model server via TCP 127.0.0.1:{DEFAULT_TCP_PORT}")
            send_msg(self.sock, {"cmd": "ping"})
            res = recv_msg(self.sock)
            if res and res.get("status") == "pong":
                print("[AlpamayoBridgeAgent] Handshake successful.")
        except Exception as e:
            print(f"[AlpamayoBridgeAgent] Warning: could not connect to model server: {e}")
            self.sock = None

    def sensors(self):
        """Configure multi-view camera suite for Alpamayo 1.5.

        Matches Carlamayo's FOUR_CAMERA_RIG:
        - Camera 0: cross-left  (120° FOV, yaw=-60°)
        - Camera 1: front-wide  (120° FOV, yaw=0°)
        - Camera 2: cross-right (120° FOV, yaw=60°)
        - Camera 6: front-tele  (30° FOV, yaw=0°)
        All at z=2.4, 1920x1080 resolution.
        """
        return [
            # Camera 0: cross-left 120° FOV
            {
                "type": "sensor.camera.rgb",
                "x": 1.0,
                "y": -0.5,
                "z": 2.4,
                "roll": 0.0,
                "pitch": 0.0,
                "yaw": -60.0,
                "width": 1920,
                "height": 1080,
                "fov": 120,
                "id": "cross_left",
            },
            # Camera 1: front-wide 120° FOV
            {
                "type": "sensor.camera.rgb",
                "x": 1.5,
                "y": 0.0,
                "z": 2.4,
                "roll": 0.0,
                "pitch": 0.0,
                "yaw": 0.0,
                "width": 1920,
                "height": 1080,
                "fov": 120,
                "id": "front_wide",
            },
            # Camera 2: cross-right 120° FOV
            {
                "type": "sensor.camera.rgb",
                "x": 1.0,
                "y": 0.5,
                "z": 2.4,
                "roll": 0.0,
                "pitch": 0.0,
                "yaw": 60.0,
                "width": 1920,
                "height": 1080,
                "fov": 120,
                "id": "cross_right",
            },
            # Camera 6: front-tele 30° FOV
            {
                "type": "sensor.camera.rgb",
                "x": 1.5,
                "y": 0.0,
                "z": 2.4,
                "roll": 0.0,
                "pitch": 0.0,
                "yaw": 0.0,
                "width": 1920,
                "height": 1080,
                "fov": 30,
                "id": "front_tele",
            },
            # IMU
            {
                "type": "sensor.other.imu",
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
                "roll": 0.0,
                "pitch": 0.0,
                "yaw": 0.0,
                "id": "imu",
            },
            # GNSS
            {
                "type": "sensor.other.gnss",
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
                "id": "gps",
            },
            # Speedometer
            {
                "type": "sensor.speedometer",
                "reading_frequency": 10,
                "id": "speed",
            },
        ]

    def set_global_plan(self, global_plan_gps, global_plan_world_coord):
        super().set_global_plan(global_plan_gps, global_plan_world_coord)
        self._dense_global_plan = list(global_plan_world_coord)

    def _get_nav_instruction(self) -> str:
        """Extract high-level route instruction from global route plan."""
        plan = getattr(self, "_dense_global_plan", None) or getattr(self, "_global_plan_world_coord", None)
        if not plan:
            return "Go straight along the road."

        try:
            from agents.navigation.local_planner import RoadOption
            from srunner.scenariomanager.carla_data_provider import CarlaDataProvider

            hero = CarlaDataProvider.get_hero_actor()
            if hero is not None and hasattr(self, "_dense_global_plan"):
                ego_loc = hero.get_location()
                # Prune waypoints that are behind the ego vehicle
                while len(self._dense_global_plan) > 1:
                    wp_transform, _ = self._dense_global_plan[0]
                    dist = ego_loc.distance(wp_transform.location)
                    if dist < 4.0:
                        self._dense_global_plan.pop(0)
                    else:
                        break
                plan = self._dense_global_plan

            # 1. Look ahead up to 25 waypoints (~35-45m) so the turn command activates well in advance of the intersection
            # NOTE: Every nav string MUST tokenize to exactly 6 tokens to preserve FlashDrive's static KV cache layout!

            for wp_transform, cmd in plan[:25]:
                if cmd == RoadOption.CHANGELANERIGHT:
                    return "Change lane to the right."
                elif cmd == RoadOption.CHANGELANELEFT:
                    return "Change lane to the left."
                elif cmd == RoadOption.RIGHT:
                    return "Turn right at the intersection."
                elif cmd == RoadOption.LEFT:
                    return "Turn left at the intersection."

            # 2. Highway exit / branch divergence check
            # Only check when approaching the exit area (len(plan) < 20, ~35m from end), not on the initial entrance ramp!
            if len(plan) < 20 and len(plan) >= 8:
                wp_curr = plan[0][0]
                wp_near = plan[min(4, len(plan) - 1)][0]
                wp_far = plan[min(18, len(plan) - 1)][0]

                # Heading of the route segment at the vehicle
                dx_near = wp_near.location.x - wp_curr.location.x
                dy_near = wp_near.location.y - wp_curr.location.y
                heading_near = math.atan2(dy_near, dx_near)

                # Heading of the route segment ahead
                dx_far = wp_far.location.x - wp_near.location.x
                dy_far = wp_far.location.y - wp_near.location.y
                heading_far = math.atan2(dy_far, dx_far)

                # Angle between current road direction and future road branch
                branch_angle = (heading_far - heading_near + math.pi) % (2 * math.pi) - math.pi

                # If the road ahead genuinely branches/forks (> 7.0 deg), guide the exit (6 tokens)
                # Normal highway lane curvature is 2-4 deg and should remain "Go straight along the road."
                if branch_angle > math.radians(7.0):
                    return "Take exit to the right."
                elif branch_angle < -math.radians(7.0):
                    return "Take exit to the left."

        except Exception as e:
            print(f"[AlpamayoBridgeAgent] Route parsing error: {e}")

        # Default cruising command: exactly 6 tokens to preserve static cache
        return "Go straight along the road."

    def run_step(self, input_data: dict, timestamp: float) -> carla.VehicleControl:
        control = carla.VehicleControl()
        self.step_idx += 1

        # 1. Extract speed
        speed_data = input_data.get("speed")
        current_speed = float(speed_data[1].get("speed", 0.0)) if speed_data else 0.0

        # 2. Extract cameras (RGB uint8)
        # CARLA outputs BGRA; take first 3 channels (BGR) then flip to RGB
        # Order matches Carlamayo FOUR_CAMERA_RIG:
        #   0: cross_left, 1: front_wide, 2: cross_right, 6: front_tele
        cam_cross_left = input_data["cross_left"][1][:, :, :3][:, :, ::-1].copy()
        cam_front_wide = input_data["front_wide"][1][:, :, :3][:, :, ::-1].copy()
        cam_cross_right = input_data["cross_right"][1][:, :, :3][:, :, ::-1].copy()
        cam_front_tele = input_data["front_tele"][1][:, :, :3][:, :, ::-1].copy()

        current_step_cams = [cam_cross_left, cam_front_wide, cam_cross_right, cam_front_tele]
        self.history_frames.append(current_step_cams)
        while len(self.history_frames) < self.num_cam_frames:
            self.history_frames.appendleft(current_step_cams)

        # Build 16 frames grouped by camera, in chronological order:
        # Camera 0 (frames t-3..t0), Camera 1 (frames t-3..t0), ...
        frames = [
            self.history_frames[t][c]
            for c in range(4)
            for t in range(self.num_cam_frames)
        ]
        # Canonical Alpamayo 1.5 camera indices: [0, 1, 2, 6]
        camera_indices = [0, 1, 2, 6]

        # 3. Maintain true ego history (16 steps at dt = 0.1s: t0-1.5s .. t0)
        from srunner.scenariomanager.carla_data_provider import CarlaDataProvider

        vehicle = CarlaDataProvider.get_hero_actor()
        current_transform = vehicle.get_transform() if vehicle is not None else None

        if self.pid_controller is None and vehicle is not None:
            try:
                from agents.navigation.controller import VehiclePIDController
                # CARLA standard lateral PID parameters (from LocalPlanner / VehiclePIDController)
                args_lateral = {
                    "K_P": 1.95,
                    "K_I": 0.05,
                    "K_D": 0.2,
                    "dt": 0.05,
                }
                args_longitudinal = {
                    "K_P": 1.0,
                    "K_I": 0.05,
                    "K_D": 0.0,
                    "dt": 0.05,
                }
                self.pid_controller = VehiclePIDController(
                    vehicle,
                    args_lateral=args_lateral,
                    args_longitudinal=args_longitudinal,
                    max_throttle=0.6,
                    max_brake=1.0,
                    max_steering=0.8,
                )
            except Exception as e:
                print(f"[AlpamayoBridgeAgent] Warning: could not initialize VehiclePIDController: {e}")

        if current_transform is not None:
            self.pose_history.append((timestamp, current_transform))

        # 16 historical steps spaced by dt = 0.1s: [-1.5, -1.4, ..., -0.1, 0.0]
        history_offsets = [round(-0.1 * i, 2) for i in reversed(range(self.history_traj_len))]

        ego_hist_xyz_list = []
        ego_hist_rot_list = []

        if current_transform is not None and len(self.pose_history) > 0:
            curr_yaw = current_transform.rotation.yaw
            for offset in history_offsets:
                target_t = timestamp + offset
                # Find closest historical pose
                closest_pose = min(self.pose_history, key=lambda p: abs(p[0] - target_t))[1]

                # Location in current vehicle CARLA frame (x forward, y right, z up)
                dx = closest_pose.location.x - current_transform.location.x
                dy = closest_pose.location.y - current_transform.location.y
                dz = closest_pose.location.z - current_transform.location.z
                alpha = math.radians(curr_yaw)
                x_carla_ego = dx * math.cos(alpha) + dy * math.sin(alpha)
                y_carla_ego = -dx * math.sin(alpha) + dy * math.cos(alpha)

                # Convert to Alpamayo ISO 8855 coordinates (x forward, y left, z up)
                xyz = np.array([x_carla_ego, -y_carla_ego, dz], dtype=np.float32)
                ego_hist_xyz_list.append(xyz)

                # Relative yaw rotation matrix (Alpamayo CCW positive)
                delta_yaw_deg = (closest_pose.rotation.yaw - curr_yaw + 180.0) % 360.0 - 180.0
                delta_yaw_rad = -math.radians(delta_yaw_deg)
                cy, sy = math.cos(delta_yaw_rad), math.sin(delta_yaw_rad)
                rot = np.array([
                    [cy, -sy, 0.0],
                    [sy,  cy, 0.0],
                    [0.0, 0.0, 1.0],
                ], dtype=np.float32)
                ego_hist_rot_list.append(rot)

            ego_hist_xyz = np.stack(ego_hist_xyz_list, axis=0)
            ego_hist_rot = np.stack(ego_hist_rot_list, axis=0)
        else:
            # Dead-reckoning fallback using speedometer
            ego_hist_xyz = np.zeros((self.history_traj_len, 3), dtype=np.float32)
            ego_hist_rot = np.tile(np.eye(3, dtype=np.float32), (self.history_traj_len, 1, 1))
            for i, offset in enumerate(history_offsets):
                ego_hist_xyz[i, 0] = current_speed * offset

        nav_text = self._get_nav_instruction()

        # 4. IPC query to FlashDrive server
        if self.sock is None:
            self._connect_to_server()

        pred_waypoints = None
        coc_text = ""
        meta_action = ""
        if self.sock is not None:
            try:
                req = {
                    "cmd": "step",
                    "images": frames,
                    "camera_indices": camera_indices,
                    "ego_history_xyz": ego_hist_xyz,
                    "ego_history_rot": ego_hist_rot,
                    "nav_text": nav_text,
                    "speed": current_speed,
                }
                send_msg(self.sock, req)
                res = recv_msg(self.sock)
                if res and res.get("status") == "ok" and res.get("pred_xyz") is not None:
                    # pred_xyz shape: (1, T_future, 3) or (1, 1, T_future, 3)
                    pred_xyz = res["pred_xyz"]
                    while pred_xyz.ndim > 2:
                        pred_xyz = pred_xyz[0]
                    pred_waypoints = pred_xyz
                    coc_text = res.get("cot", "")
                    meta_action = res.get("meta_action", "")
                    out_msg = f"[Step {self.step_idx:04d} | {current_speed * 3.6:4.1f} km/h] Command: \"{nav_text}\""
                    if coc_text:
                        out_msg += f" | CoC: \"{coc_text}\""
                    if meta_action:
                        out_msg += f" | Action: \"{meta_action}\""
                    print(out_msg, flush=True)
            except Exception as e:
                print(f"[AlpamayoBridgeAgent] Error communicating with server: {e}")
                self.sock = None

        # 5. Fallback if prefilling or no waypoints
        if pred_waypoints is None or len(pred_waypoints) < 5:
            control.steer = float(np.clip(self.prev_steer, -1.0, 1.0))
            control.throttle = float(np.clip(self.prev_throttle if current_speed >= 3.0 else 0.35, 0.0, 1.0))
            control.brake = 0.0
            return control

        # 6. Official CARLA VehiclePIDController (Carlamayo architecture)
        # Convert Alpamayo local frame (x forward, y left) to CARLA local frame (x forward, y right)
        wp_local = np.asarray(pred_waypoints, dtype=np.float64).copy()
        wp_local[:, 1] *= -1.0  # Alpamayo (x, y) -> CARLA (x, -y)
        carla_pts = wp_local[:, :2]

        # Transform local waypoints to world frame
        if current_transform is not None:
            wp_world = []
            for p in wp_local:
                loc_w = current_transform.transform(carla.Location(x=float(p[0]), y=float(p[1]), z=float(p[2])))
                wp_world.append([loc_w.x, loc_w.y, loc_w.z])
            wp_world = np.asarray(wp_world, dtype=np.float64)
        else:
            wp_world = wp_local

        # Compute cumulative chord distance
        seg = np.linalg.norm(np.diff(wp_world[:, :2], axis=0), axis=1)
        cum = np.concatenate([[0.0], np.cumsum(seg)])
        traj_extent = float(cum[-1])

        # Check trajectory curvature in the near-to-mid horizon (0.5s to 3.5s ahead)
        max_turn_angle = 0.0
        if len(wp_local) >= 15:
            angles = [math.atan2(abs(p[1]), max(p[0], 1.0)) for p in wp_local[5:min(35, len(wp_local))]]
            max_turn_angle = max(angles) if angles else 0.0

        # Dynamic lookahead: 5.5m to 8.5m on turns to capture the turn arc (commands 0.60-0.75 steer), 5.0m to 12.0m on straightaways
        is_turning = max_turn_angle > 0.087
        if is_turning:
            lookahead_m = float(np.clip(5.5 + 0.3 * current_speed, 5.0, 8.5))
        else:
            lookahead_m = float(np.clip(5.0 + 0.4 * current_speed, 5.0, 12.0))

        target_idx = int(min(np.searchsorted(cum, lookahead_m), len(wp_world) - 1))
        loc = carla.Location(
            x=float(wp_world[target_idx, 0]),
            y=float(wp_world[target_idx, 1]),
            z=float(wp_world[target_idx, 2]),
        )
        target_wp = RawTargetWaypoint(carla.Transform(loc, carla.Rotation()))

        # Planned speed to target waypoint (derived purely from action model timeline, 10Hz):
        t_target = (target_idx + 1) * 0.1
        s_target = float(cum[target_idx])
        v_target_planned = (s_target / t_target) * 3.6 if t_target > 0.0 else 0.0

        # Downstream speed & tail velocity profile:
        idx_downstream = min(24, len(wp_local) - 1)
        t_downstream = (idx_downstream + 1) * 0.1
        v_downstream = (float(cum[idx_downstream]) / t_downstream) * 3.6 if t_downstream > 0 else v_target_planned
        v_tail = float(np.mean(seg[-5:]) / 0.1 * 3.6) if len(seg) >= 5 else v_target_planned

        # Check near-horizon displacement at t = 1.0s (index 9 in 10Hz waypoints)
        p10_dist = float(np.linalg.norm(wp_local[min(9, len(wp_local) - 1), :2]))

        # Physics-based emergency & safe stopping distances
        d_stop_min = (current_speed ** 2) / (2.0 * 3.5)
        d_stop_safe = (current_speed ** 2) / (2.0 * 2.0)

        # Standstill / traffic queue / obstacle stopping condition (BUG 2 FIX):
        # 1. When stationary (current_speed < 1.0 m/s), vehicle holds standstill only if path ahead is compressed (< 3.0m)
        # 2. When moving (current_speed >= 1.0 m/s), vehicle stops if:
        #    a) Trajectory extent terminates within minimum physical stopping distance
        #    b) Model commands near-zero planned speed (< 2.0 km/h)
        #    c) Tail waypoints collapse (v_tail < 4.0 km/h AND extent within safe stopping distance)
        if current_speed < 1.0:
            is_blocked = (traj_extent < 3.0)
        else:
            is_blocked = (
                (traj_extent < max(2.5, d_stop_min))
                or (v_target_planned < 2.0)
                or (v_tail < 4.0 and traj_extent < max(5.0, d_stop_safe + 3.0))
            )

        if is_blocked:
            target_speed_kmh = 0.0
            if current_transform is not None:
                ahead_loc = current_transform.transform(carla.Location(x=5.0, y=0.0, z=0.0))
                target_wp = RawTargetWaypoint(carla.Transform(ahead_loc, current_transform.rotation))
            else:
                target_wp = RawTargetWaypoint(carla.Transform(carla.Location(5.0, 0.0, 0.0), carla.Rotation()))
        else:
            # Model-derived target speed without arbitrary 10 km/h floor (BUG 1 FIX):
            if v_downstream < v_target_planned:
                # Deceleration ahead: smoothly track downstream slowdown
                base_speed = 0.6 * v_downstream + 0.4 * v_target_planned
            else:
                base_speed = v_target_planned

            # Kinematic extent limit (v_max = sqrt(2 * a * extent)):
            v_extent_limit = math.sqrt(max(0.1, 2.0 * 1.8 * traj_extent)) * 3.6

            # Pure action target speed: clipped to [0.0, 35.0] km/h (no artificial 10 km/h floor)
            target_speed_kmh = float(np.clip(min(base_speed, v_extent_limit), 0.0, 35.0))

            # Curvature-aware speed scaling on sharp turns / curved ramps (slows down to 10-12 km/h on sharp turns)
            if max_turn_angle > 0.06:  # curve > 3.4 degrees
                curve_limit_kmh = max(10.0, 35.0 - max_turn_angle * 100.0)
                target_speed_kmh = min(target_speed_kmh, curve_limit_kmh)

        # Run official CARLA VehiclePIDController
        if self.pid_controller is not None:
            raw_control = self.pid_controller.run_step(target_speed_kmh, target_wp)
            raw_steer = float(raw_control.steer)
            raw_throttle = float(raw_control.throttle)
            raw_brake = float(raw_control.brake)
        else:
            raw_steer = 0.0
            raw_throttle = 0.3 if target_speed_kmh > 5.0 else 0.0
            raw_brake = 1.0 if target_speed_kmh <= 0.0 else 0.0

        # Standstill starting boost: when stationary and path is open (extent >= 4.0m)
        if current_speed < 1.5 and target_speed_kmh > 5.0 and traj_extent >= 4.0:
            raw_throttle = max(raw_throttle, 0.45)
            raw_brake = 0.0

        # Enforce positive stopping when target speed is 0.0
        if target_speed_kmh <= 0.0:
            raw_throttle = 0.0
            raw_brake = max(raw_brake, 0.8)

        # Adaptive steering responsiveness: 0.85 on sharp curves/intersections, 0.60 on straightaways
        alpha_steer = 0.85 if is_turning else 0.60
        alpha_pedal = self.control_smooth_alpha
        steer = (1.0 - alpha_steer) * self.prev_steer + alpha_steer * raw_steer
        throttle = (1.0 - alpha_pedal) * self.prev_throttle + alpha_pedal * raw_throttle
        brake = (1.0 - alpha_pedal) * self.prev_brake + alpha_pedal * raw_brake

        # Mutual exclusion: avoid pressing throttle and brake simultaneously
        if throttle >= brake:
            brake = 0.0
        else:
            throttle = 0.0

        self.prev_steer = steer
        self.prev_throttle = throttle
        self.prev_brake = brake

        control.steer = float(np.clip(steer, -1.0, 1.0))
        control.throttle = float(np.clip(throttle, 0.0, 1.0))
        control.brake = float(np.clip(brake, 0.0, 1.0))
        control.hand_brake = False

        # 7. Log predicted trajectory for offline evaluation metrics
        if self._traj_log_file is not None and pred_waypoints is not None:
            try:
                log_entry = {
                    "step": self.step_idx,
                    "timestamp": timestamp,
                    "pred_waypoints": pred_waypoints.tolist() if hasattr(pred_waypoints, "tolist") else list(pred_waypoints),
                    "steer": control.steer,
                    "throttle": control.throttle,
                    "brake": control.brake,
                    "speed": current_speed,
                    "nav_text": nav_text,
                    "coc": coc_text,
                    "meta_action": meta_action,
                }
                self._traj_log_file.write(json.dumps(log_entry) + "\n")
                self._traj_log_file.flush()
            except Exception as e:
                print(f"[AlpamayoBridgeAgent] Trajectory log error: {e}")

        # 8. Draw predicted waypoints in CARLA debug view (green dots)
        if self._debug_draw:
            try:
                from srunner.scenariomanager.carla_data_provider import CarlaDataProvider
                world = CarlaDataProvider.get_world()
                ego_transform = CarlaDataProvider.get_hero_actor().get_transform()
                for i in range(0, len(carla_pts), 2):  # every other point to reduce clutter
                    pt = carla_pts[i]
                    world_loc = ego_transform.transform(
                        carla.Location(x=float(pt[0]), y=float(pt[1]), z=0.5)
                    )
                    world.debug.draw_point(
                        world_loc, size=0.08,
                        color=carla.Color(0, 255, 0), life_time=0.15,
                    )
            except Exception:
                pass  # non-critical, don't break the agent

        return control

    def destroy(self, results=None):
        """Clean up IPC socket and trajectory log."""
        if self._traj_log_file is not None:
            try:
                self._traj_log_file.close()
            except Exception:
                pass
            self._traj_log_file = None
        if self.sock is not None:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None
        self.pid_controller = None
        print("[AlpamayoBridgeAgent] Destroyed.")
