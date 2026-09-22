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
from typing import Any

import carla
import numpy as np

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

        # PID gains for lateral tracking
        self.turn_kp = 1.25
        self.turn_ki = 0.05
        self.turn_kd = 0.2
        self.turn_integral = 0.0
        self.prev_turn_error = 0.0

        # PID gains for longitudinal tracking
        self.speed_kp = 0.5
        self.speed_ki = 0.02
        self.speed_kd = 0.05
        self.speed_integral = 0.0
        self.prev_speed_error = 0.0

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
        """Configure multi-view camera suite for Alpamayo 1.5."""
        return [
            # Front camera (Camera 1)
            {
                "type": "sensor.camera.rgb",
                "x": 1.3,
                "y": 0.0,
                "z": 1.6,
                "roll": 0.0,
                "pitch": 0.0,
                "yaw": 0.0,
                "width": 800,
                "height": 600,
                "fov": 100,
                "id": "front",
            },
            # Front-left camera (Camera 0)
            {
                "type": "sensor.camera.rgb",
                "x": 1.3,
                "y": -0.4,
                "z": 1.6,
                "roll": 0.0,
                "pitch": 0.0,
                "yaw": -55.0,
                "width": 800,
                "height": 600,
                "fov": 100,
                "id": "front_left",
            },
            # Front-right camera (Camera 2)
            {
                "type": "sensor.camera.rgb",
                "x": 1.3,
                "y": 0.4,
                "z": 1.6,
                "roll": 0.0,
                "pitch": 0.0,
                "yaw": 55.0,
                "width": 800,
                "height": 600,
                "fov": 100,
                "id": "front_right",
            },
            # Rear camera (Camera 4)
            {
                "type": "sensor.camera.rgb",
                "x": -1.3,
                "y": 0.0,
                "z": 1.6,
                "roll": 0.0,
                "pitch": 0.0,
                "yaw": 180.0,
                "width": 800,
                "height": 600,
                "fov": 100,
                "id": "rear",
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

    def _get_nav_instruction(self) -> str:
        """Extract high-level route instruction from global route plan."""
        if not hasattr(self, "_global_plan_world_coord") or not self._global_plan_world_coord:
            return "Keep straight."

        try:
            from agents.navigation.local_planner import RoadOption
            from srunner.scenariomanager.carla_data_provider import CarlaDataProvider

            hero = CarlaDataProvider.get_hero_actor()
            if hero is not None:
                ego_loc = hero.get_location()

                # Prune waypoints that are behind or within 5 meters of the ego vehicle
                while len(self._global_plan_world_coord) > 1:
                    wp_transform, _ = self._global_plan_world_coord[0]
                    dist = ego_loc.distance(wp_transform.location)
                    if dist < 5.0:
                        self._global_plan_world_coord.pop(0)
                        if hasattr(self, "_global_plan") and len(self._global_plan) > 1:
                            self._global_plan.pop(0)
                    else:
                        break

            # Look ahead up to 5 waypoints to find the next active command
            for _, cmd in self._global_plan_world_coord[:5]:
                if cmd == RoadOption.CHANGELANERIGHT:
                    return "Change lane to the right."
                elif cmd == RoadOption.CHANGELANELEFT:
                    return "Change lane to the left."
                elif cmd == RoadOption.RIGHT:
                    return "Turn right at the intersection."
                elif cmd == RoadOption.LEFT:
                    return "Turn left at the intersection."
                elif cmd == RoadOption.STRAIGHT:
                    return "Go straight at the intersection."
        except Exception as e:
            print(f"[AlpamayoBridgeAgent] Route parsing error: {e}")

        return "Keep straight."

    def run_step(self, input_data: dict, timestamp: float) -> carla.VehicleControl:
        control = carla.VehicleControl()
        self.step_idx += 1

        # 1. Extract speed
        speed_data = input_data.get("speed")
        current_speed = float(speed_data[1].get("speed", 0.0)) if speed_data else 0.0

        # 2. Extract cameras (RGB uint8)
        # CARLA outputs BGRA; take first 3 channels (BGR) then flip to RGB
        # Order: 0: front_left, 1: front, 2: front_right, 4: rear
        cam_front_left = input_data["front_left"][1][:, :, :3][:, :, ::-1].copy()
        cam_front = input_data["front"][1][:, :, :3][:, :, ::-1].copy()
        cam_front_right = input_data["front_right"][1][:, :, :3][:, :, ::-1].copy()
        cam_rear = input_data["rear"][1][:, :, :3][:, :, ::-1].copy()

        current_step_cams = [cam_front_left, cam_front, cam_front_right, cam_rear]
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
        camera_indices = [0, 1, 2, 4]

        # 3. Maintain true ego history (16 steps at dt = 0.1s: t0-1.5s .. t0)
        from srunner.scenariomanager.carla_data_provider import CarlaDataProvider

        vehicle = CarlaDataProvider.get_hero_actor()
        current_transform = vehicle.get_transform() if vehicle is not None else None

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
            except Exception as e:
                print(f"[AlpamayoBridgeAgent] Error communicating with server: {e}")
                self.sock = None

        # 5. Fallback if prefilling or no waypoints
        if pred_waypoints is None or len(pred_waypoints) < 5:
            control.steer = 0.0
            control.throttle = 0.35 if current_speed < 3.0 else 0.0
            control.brake = 0.0
            return control

        # 6. PID Tracking of predicted waypoints
        # In CARLA coordinates: X is forward, Y is right
        # In Alpamayo coordinates: X is forward, Y is left
        # Alpamayo (x, y) -> CARLA (x, -y)
        carla_pts = np.copy(pred_waypoints[:, :2])
        carla_pts[:, 1] = -carla_pts[:, 1]

        # Select lookahead point for steering
        aim_dist = max(3.5, 0.6 * current_speed)
        dists = np.linalg.norm(carla_pts, axis=1)
        valid_idxs = np.where(dists >= aim_dist)[0]
        aim_idx = valid_idxs[0] if len(valid_idxs) > 0 else len(carla_pts) - 1
        target_pt = carla_pts[aim_idx]

        # Desired heading angle
        target_angle = math.atan2(target_pt[1], target_pt[0])

        # Lateral PID (CARLA ticks at 20 Hz -> dt = 0.05s)
        turn_error = target_angle
        self.turn_integral = np.clip(self.turn_integral + turn_error * 0.05, -1.0, 1.0)
        turn_deriv = (turn_error - self.prev_turn_error) / 0.05
        self.prev_turn_error = turn_error

        steer = self.turn_kp * turn_error + self.turn_ki * self.turn_integral + self.turn_kd * turn_deriv
        control.steer = float(np.clip(steer, -1.0, 1.0))

        # Longitudinal PID: estimate target speed from waypoint progression
        # Waypoints are at 10 Hz (dt = 0.1s): index 5 is 0.6s, index 15 is 1.6s
        idx_near = min(5, len(carla_pts) - 1)
        idx_far = min(15, len(carla_pts) - 1)
        if idx_far > idx_near:
            dt_interval = (idx_far - idx_near) * 0.1
            target_speed = float(np.linalg.norm(carla_pts[idx_far] - carla_pts[idx_near]) / dt_interval)
        else:
            target_speed = float(np.linalg.norm(carla_pts[-1]) / (len(carla_pts) * 0.1))

        # Speed cap suitable for urban & highway (13.5 m/s ≈ 48.6 km/h)
        target_speed = min(target_speed, 13.5)

        speed_error = target_speed - current_speed
        self.speed_integral = np.clip(self.speed_integral + speed_error * 0.05, -5.0, 5.0)
        speed_deriv = (speed_error - self.prev_speed_error) / 0.05
        self.prev_speed_error = speed_error

        accel = self.speed_kp * speed_error + self.speed_ki * self.speed_integral + self.speed_kd * speed_deriv
        if accel > 0.0:
            # Overcome CARLA static friction and rolling resistance
            min_throttle = 0.30 if (current_speed < 1.5 and target_speed > 0.4) else 0.0
            control.throttle = float(np.clip(max(accel, min_throttle), 0.0, 0.85))
            control.brake = 0.0
        else:
            control.throttle = 0.0
            control.brake = float(np.clip(-accel, 0.0, 1.0)) if speed_error < -0.5 else 0.0

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
        print("[AlpamayoBridgeAgent] Destroyed.")
