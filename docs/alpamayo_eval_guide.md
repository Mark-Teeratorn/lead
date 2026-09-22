Viewed z.ai_cmds.txt:1-4
Viewed eval_alpamayo_b2d.sh:1-60
Ran command: `ls src/lead/routes/benchmark_routes/bench2drive/*.xml | head -10`
Viewed task-951.log:1-10
Viewed checkpoint_endpoint.json:1-100

Here are the two ways to run the evaluation test:

---

### Method 1: The All-in-One Automated Command (Recommended)

From the `lead` workspace, run the wrapper script. It automatically manages the model server, starts CARLA, runs the evaluation, and saves the benchmark scores:

```bash
cd /home/aimslab/lead
source .venv/bin/activate

# Run evaluation on route 23687 (default):
bash scripts/common/eval_alpamayo_b2d.sh src/lead/routes/benchmark_routes/bench2drive/23687.xml
```

> **Tip (Fast pipeline test):**  
> To test without waiting 3–5 minutes for the 10B model to load weights, append `--dummy`:
> ```bash
> bash scripts/common/eval_alpamayo_b2d.sh src/lead/routes/benchmark_routes/bench2drive/23687.xml --dummy
> ```

---

### Method 2: Two-Terminal Setup (Best for Monitoring Logs Live)

If you want to see the model server logs and tokenization shapes in real-time in a separate window:

#### Terminal 1 — Start the Model Server:
```bash
cd /home/aimslab/flashdrive
source .venv/bin/activate
python scripts/flashdrive_server.py
```
*(Wait until it prints: `FlashDrive server listening on UNIX socket: /tmp/alpamayo_flashdrive.sock`)*

#### Terminal 2 — Run the Benchmark Route:
```bash
cd /home/aimslab/lead
source .venv/bin/activate
bash scripts/common/eval_alpamayo_b2d.sh src/lead/routes/benchmark_routes/bench2drive/23687.xml
```
*(The script will detect the existing server on `/tmp/alpamayo_flashdrive.sock` and connect immediately)*

---

### Testing Other Benchmark Routes
You can test any Bench2Drive scenario XML from `src/lead/routes/benchmark_routes/bench2drive/`:

```bash
# Example 1: Route 10857
bash scripts/common/eval_alpamayo_b2d.sh src/lead/routes/benchmark_routes/bench2drive/10857.xml

# Example 2: Route 11381
bash scripts/common/eval_alpamayo_b2d.sh src/lead/routes/benchmark_routes/bench2drive/11381.xml

# Example 3: Route 14194
bash scripts/common/eval_alpamayo_b2d.sh src/lead/routes/benchmark_routes/bench2drive/14194.xml
```

---

### Where to Find Results After Running

When the route finishes, the results are written to:
- **Leaderboard Score & Infractions:** [`outputs/local_evaluation/alpamayo_<ROUTE_ID>/checkpoint_endpoint.json`](file:///home/aimslab/lead/outputs/local_evaluation/alpamayo_23687/checkpoint_endpoint.json)  
  *(Shows `score_route`, `score_composed`, collisions, and completion %)*
- **Logged Trajectories:** `outputs/local_evaluation/alpamayo_<ROUTE_ID>/predicted_trajectories.jsonl`

cd /home/aimslab/lead
source .venv/bin/activate

# Set CARLA_GUI=1 to enable the Unreal Engine 3D viewport window:
CARLA_GUI=1 bash scripts/common/eval_alpamayo_b2d.sh src/lead/routes/benchmark_routes/bench2drive/23687.xml