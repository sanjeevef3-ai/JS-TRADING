import os
import sys
import time
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PYTHON = sys.executable
NGROK = ROOT / "tools" / "ngrok.exe"
LOG_DIR = ROOT / "data" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

server_log = open(LOG_DIR / "server.log", "a", encoding="utf-8")
ngrok_log = open(LOG_DIR / "ngrok.log", "a", encoding="utf-8")

def start_server():
    print("[SUPERVISOR] Starting Python Backend Server...")
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.Popen(
        [PYTHON, str(ROOT / "server.py")],
        cwd=str(ROOT),
        env=env,
        stdout=server_log,
        stderr=subprocess.STDOUT
    )

def start_ngrok():
    print("[SUPERVISOR] Starting Permanent Ngrok Tunnel...")
    return subprocess.Popen(
        [str(NGROK), "start", "jyoti_terminal", "--log=stdout"],
        cwd=str(ROOT),
        stdin=subprocess.DEVNULL,
        stdout=ngrok_log,
        stderr=subprocess.STDOUT
    )

def main():
    print("=== JYOTI SINGH TERMINAL • SELF-HEALING SUPERVISOR ===")
    server_proc = start_server()
    time.sleep(2)
    ngrok_proc = start_ngrok()

    try:
        while True:
            time.sleep(3)
            # Check server health
            if server_proc.poll() is not None:
                print(f"[SUPERVISOR WARNING] Server died (exit code {server_proc.returncode}). Restarting now...")
                server_proc = start_server()

            # Check ngrok health
            if ngrok_proc.poll() is not None:
                print(f"[SUPERVISOR WARNING] Ngrok died (exit code {ngrok_proc.returncode}). Restarting now...")
                ngrok_proc = start_ngrok()
    except KeyboardInterrupt:
        print("[SUPERVISOR] Shutting down...")
    finally:
        try: server_proc.terminate()
        except: pass
        try: ngrok_proc.terminate()
        except: pass

if __name__ == "__main__":
    main()
