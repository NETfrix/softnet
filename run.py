"""
Softnet - Single entry point.

Usage:
    python run.py           # Build frontend + start server
    python run.py --dev     # Dev mode with auto-reload (no frontend build)
"""
import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Softnet - Network Analysis Tool")
    parser.add_argument("--dev", action="store_true", help="Development mode (auto-reload, no build)")
    parser.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser")
    args = parser.parse_args()

    os.environ["SOFTNET_PORT"] = str(args.port)
    if not args.no_browser:
        os.environ["SOFTNET_OPEN_BROWSER"] = "1"
    if args.dev:
        os.environ["SOFTNET_DEV_MODE"] = "true"

    if args.dev:
        # Dev mode: run vite dev server + uvicorn with reload
        import subprocess
        import threading

        npm = "npm.cmd" if sys.platform == "win32" else "npm"
        frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")

        # Install frontend deps if needed
        if not os.path.exists(os.path.join(frontend_dir, "node_modules")):
            print("Installing frontend dependencies...")
            subprocess.run([npm, "install"], cwd=frontend_dir, check=True)

        # Start Vite dev server in background
        vite_proc = subprocess.Popen(
            [npm, "run", "dev"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        def _stream_vite():
            for line in vite_proc.stdout:
                sys.stdout.buffer.write(b"[vite] " + line)
                sys.stdout.buffer.flush()

        threading.Thread(target=_stream_vite, daemon=True).start()

        import uvicorn

        print(f"\n  Softnet DEV mode")
        print(f"  Backend:  http://localhost:{args.port}")
        print(f"  Frontend: http://localhost:5173\n")

        if not args.no_browser:
            import webbrowser
            webbrowser.open("http://localhost:5173")

        try:
            uvicorn.run("backend.main:app", host="0.0.0.0", port=args.port, reload=True)
        finally:
            vite_proc.terminate()
    else:
        # Production mode: build frontend, serve everything from FastAPI
        from backend.main import main as start_server
        start_server()


if __name__ == "__main__":
    main()
