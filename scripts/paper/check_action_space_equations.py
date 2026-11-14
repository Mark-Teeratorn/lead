#!/usr/bin/env python3
"""Numerical check of the integration equations of manuscript Section 3.1 against the released Alpamayo action-space code
(UnicycleAccelCurvatureActionSpace.action_to_traj), and of the initial speed that the model estimates from a given ego history.
Run with the FlashDrive Python (torch needed), CPU only. Output is quoted in docs/ANALYSIS_ADDENDUM.md section 11-A."""
import sys, json, numpy as np, torch
sys.path.insert(0, '/home/aimslab/alpamayo-autoware-alpamayo1.5/src')
from alpamayo1_5.action_space.unicycle_accel_curvature import UnicycleAccelCurvatureActionSpace as AS
cfg = json.load(open('/home/aimslab/checkpoints/action_experts/Alpamayo-1.5-10B-Matrix-Golden-6400-A15/config.json'))
def find(o):
    if isinstance(o, dict):
        if 'accel_mean' in o: return o
        for v in o.values():
            r = find(v)
            if r: return r
ac = find(cfg)
mu_a, sd_a, mu_k, sd_k = ac['accel_mean'], ac['accel_std'], ac['curvature_mean'], ac['curvature_std']
sp = AS(accel_mean=mu_a, accel_std=sd_a, curvature_mean=mu_k, curvature_std=sd_k, dt=0.1, n_waypoints=64)
rng = np.random.default_rng(0); dt = 0.1
def paper(u, v0):          # the equations of Section 3.1, written out with explicit loops
    a = u[:, 0] * sd_a + mu_a; kap = u[:, 1] * sd_k + mu_k
    v = np.zeros(65); psi = np.zeros(65); x = np.zeros(65); y = np.zeros(65); v[0] = v0
    for k in range(1, 65):
        v[k] = v[k-1] + a[k-1] * dt
        psi[k] = psi[k-1] + kap[k-1] * (v[k-1] * dt + 0.5 * a[k-1] * dt**2)
        x[k] = x[k-1] + dt / 2 * (v[k-1] * np.cos(psi[k-1]) + v[k] * np.cos(psi[k]))
        y[k] = y[k-1] + dt / 2 * (v[k-1] * np.sin(psi[k-1]) + v[k] * np.sin(psi[k]))
    return np.stack([x[1:], y[1:]], 1)
worst = 0.0
for trial in range(5):
    u = rng.normal(size=(64, 2)); v0 = float(rng.uniform(0, 12))
    hist = torch.zeros(1, 16, 3); rot = torch.eye(3).repeat(1, 16, 1, 1)
    xyz, _ = sp.action_to_traj(torch.tensor(u, dtype=torch.float32)[None], hist, rot, t0_states={'v': torch.tensor([v0])})
    worst = max(worst, float(np.abs(xyz[0, :, :2].numpy() - paper(u, v0)).max()))
print('max |code - paper equations| over 5 random control sets (m):', worst)
# initial speed estimated from a swapped history
for name, sp_mps in (('moving 4.0 m/s', 4.0), ('stationary', 0.0)):
    off = np.array([round(-0.1 * i, 2) for i in reversed(range(16))])
    h = np.zeros((16, 3), dtype=np.float32); h[:, 0] = sp_mps * off
    st = sp.estimate_t0_states(torch.tensor(h)[None], torch.eye(3).repeat(1, 16, 1, 1)[None].reshape(1, 16, 3, 3))
    print('history', name, '-> estimated v0 =', float(st['v'].reshape(-1)[0]))
# plan extent when every control equals the training mean (a_k = mean accel, no curvature), v0 given
for v0 in (0.0, 0.4, 4.0):
    xyz, _ = sp.action_to_traj(torch.zeros(1, 64, 2), torch.zeros(1, 16, 3), torch.eye(3).repeat(1, 16, 1, 1), t0_states={'v': torch.tensor([v0])})
    p = xyz[0, :, :2].numpy(); L = np.hypot(*np.diff(p, axis=0).T).sum()
    print(f'mean-control plan from v0={v0}: L (63 segments) = {L:.2f} m, first segment = {np.hypot(*p[0]):.3f} m')
