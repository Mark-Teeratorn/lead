#!/usr/bin/env python3
"""
Immune Daemon for Flooded 1600 Training
- Double-forks to be adopted directly by init (PID 1)
- Setsid to detach completely from pts controlling terminal
- Ignores SIGHUP, SIGTERM, SIGINT
- Self-healing loop: continuously keeps flooded_1600 running until
  /workspace/Alpamayo-1.5-10B-Matrix-Flooded-1600-A15.tar.gz is produced.
"""
import os
import sys
import time
import signal
import subprocess
import datetime

TARGET_ARCHIVE = "/workspace/Alpamayo-1.5-10B-Matrix-Flooded-1600-A15.tar.gz"
LOG_FILE = "/workspace/train_flooded_1600.log"
PID_FILE = "/workspace/flooded_1600_daemon.pid"

def log(msg: str):
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{now}] [IMMUNE_DAEMON] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def run_loop():
    # Ignore hangup and termination signals
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)

    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

    log(f"Immune daemon active (PID: {os.getpid()}, PPID: {os.getppid()}). Target: {TARGET_ARCHIVE}")

    while not os.path.exists(TARGET_ARCHIVE):
        log("Checking / Launching launch_matrix_training.sh flooded_1600...")
        with open(LOG_FILE, "a") as out:
            proc = subprocess.Popen(
                ["/workspace/launch_matrix_training.sh", "flooded_1600"],
                stdout=out,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
                cwd="/workspace"
            )
            # Record training sub-process PID
            with open("/workspace/train_flooded_1600.pid", "w") as pf:
                pf.write(str(proc.pid))

            ret = proc.wait()
            log(f"launch_matrix_training.sh exited with return code {ret}")

        if os.path.exists(TARGET_ARCHIVE):
            log(f"Target archive {TARGET_ARCHIVE} created successfully! Training complete.")
            break

        log("Target archive not found yet. Auto-recovering in 10 seconds...")
        time.sleep(10)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        run_loop()
        return

    # First fork
    pid = os.fork()
    if pid > 0:
        # Exit parent
        print(f"Daemon launcher forked intermediate PID {pid}. Exiting foreground.")
        sys.exit(0)

    # Detach session
    os.setsid()

    # Second fork
    pid2 = os.fork()
    if pid2 > 0:
        # Exit first child
        sys.exit(0)

    # Grandchild: reparented to PID 1
    # Redirect standard file descriptors
    devnull = os.open(os.devnull, os.O_RDWR)
    os.dup2(devnull, sys.stdin.fileno())

    run_loop()

if __name__ == "__main__":
    main()
