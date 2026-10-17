"""
Main Unified Entry Point for Indian Stock Market MiroFish AI Engine
Run with:
  python main.py --web      (Launches full Interactive Web UI & REST Server)
  python main.py --cli      (Launches Terminal CLI mode)
  python main.py --refine   (Executes Self-Refining Code & System Diagnostics)
"""

import sys
import argparse

# Force UTF-8 on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def main():
    parser = argparse.ArgumentParser(description="Indian Stock Market MiroFish AI Engine")
    parser.add_argument("--web", action="store_true", help="Launch Web Dashboard and REST API Server")
    parser.add_argument("--cli", action="store_true", help="Launch Terminal CLI mode")
    parser.add_argument("--symbol", "-s", type=str, default=None, help="Stock or Index symbol for CLI")
    parser.add_argument("--refine", action="store_true", help="Run Self-Refinement and Health Check")
    parser.add_argument("--port", type=int, default=8000, help="Port for web server (default 8000)")

    args = parser.parse_args()

    if args.refine:
        from learning import SelfRefineEngine
        print("Running Self-Refining AI Diagnostics & System Health Check...")
        refiner = SelfRefineEngine()
        result = refiner.run_full_self_refinement()
        import pprint
        pprint.pprint(result)
        return

    if args.cli or (not args.web and args.symbol):
        from cli import run_cli_analysis
        sym = args.symbol or "NIFTY"
        run_cli_analysis(sym)
        return

    # Default: Start Web Server
    import uvicorn
    from config import SERVER_HOST
    print("=" * 70)
    print("🇮🇳 Indian Stock Market MiroFish AI Swarm Engine")
    print(f"🚀 Web Dashboard & REST Server running at: http://{SERVER_HOST}:{args.port}")
    print("🛡️ Loop Protector: 0 Infinite Loops Guaranteed (Bounded DAG Swarm)")
    print("⚡ Self-Developing & Self-Learning Engine: Online")
    print("=" * 70)
    uvicorn.run("server:app", host=SERVER_HOST, port=args.port, reload=False)

if __name__ == "__main__":
    main()
