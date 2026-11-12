#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import datetime
import json

LOG_FILE = "/workspace/auto_chain.log"
STATUS_FILE = "/workspace/pipeline_status.json"

def log(msg: str):
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def update_status(stage: str, details: dict):
    data = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "active_stage": stage,
        "details": details
    }
    with open(STATUS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def is_process_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def is_golden_running() -> bool:
    try:
        res = subprocess.run(["pgrep", "-f", "golden_1600"], capture_output=True, text=True)
        return bool(res.stdout.strip())
    except Exception:
        return False

def wait_for_golden_completion():
    log("Supervisor started: Monitoring golden_1600 training...")
    update_status("monitoring_golden_1600", {"info": "Waiting for golden_1600 to complete 2,000 steps"})
    
    while is_golden_running():
        time.sleep(15)
    
    log("golden_1600 training process has exited.")
    time.sleep(5)
    
    # Check if zip exists
    zip_path = "/workspace/Alpamayo-1.5-10B-Matrix-Golden-1600-A15.zip"
    if not os.path.exists(zip_path):
        log(f"{zip_path} not found yet. Running conversion and zipping for golden_1600...")
        # Check latest ckpt
        ckpt_dir = "/workspace/alpamayo-recipes/recipes/alpamayo1_5_sft/output_stage2_golden_1600"
        ckpts = sorted([os.path.join(ckpt_dir, d) for d in os.listdir(ckpt_dir) if d.startswith("checkpoint-")])
        if ckpts:
            latest = ckpts[-1]
            out_a15 = "/workspace/Alpamayo-1.5-10B-Matrix-Golden-1600-A15"
            log(f"Converting {latest} -> {out_a15}")
            conv_cmd = [
                "/workspace/alpamayo-recipes/recipes/alpamayo1_5_sft/a1_5_sft/bin/python",
                "/workspace/alpamayo-recipes/scripts/convert_checkpoint.py",
                "to-a15",
                "--input", latest,
                "--output", out_a15,
                "--overwrite"
            ]
            subprocess.run(conv_cmd, check=True)
            log("Conversion complete. Packaging zip...")
            import zipfile
            with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(out_a15, followlinks=True):
                    for file in files:
                        fp = os.path.join(root, file)
                        rel = os.path.relpath(fp, os.path.dirname(out_a15))
                        zf.write(fp, arcname=rel)
            log(f"Zip created successfully: {zip_path}")
    else:
        log(f"Found existing finalized archive: {zip_path}")

def launch_flooded_1600():
    log("====================================================================")
    log("AUTO-CHAIN TRIGGER: Launching flooded_1600 training (10 epochs = 2,000 steps)")
    log("====================================================================")
    update_status("launching_flooded_1600", {"target": "flooded_1600"})
    
    # Wait for GPU memory to settle
    time.sleep(10)
    
    flooded_log = "/workspace/train_flooded_1600.log"
    log_file_handle = open(flooded_log, "a")
    
    cmd = ["/workspace/launch_matrix_training.sh", "flooded_1600"]
    proc = subprocess.Popen(
        cmd,
        stdout=log_file_handle,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        start_new_session=True
    )
    
    with open("/workspace/train_flooded_1600.pid", "w") as f:
        f.write(str(proc.pid))
    
    log(f"flooded_1600 launched with PID {proc.pid}. Log: {flooded_log}")
    update_status("running_flooded_1600", {"pid": proc.pid, "log": flooded_log})
    
    # Monitor flooded_1600 until finish
    proc.wait()
    log(f"flooded_1600 finished with exit code {proc.returncode}")
    update_status("flooded_1600_completed", {"exit_code": proc.returncode})
    log("PIPELINE SEQUENCE (golden_1600 -> flooded_1600) FULLY FINISHED!")

def main():
    try:
        wait_for_golden_completion()
        launch_flooded_1600()
    except Exception as e:
        log(f"Error in chain supervisor: {e}")
        update_status("error", {"error": str(e)})

if __name__ == "__main__":
    main()
