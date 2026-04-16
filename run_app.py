import subprocess
import sys
import os
import time
import threading

def run_backend():
    print("🚀 Starting Django Backend on http://127.0.0.1:8000")
    venv_python = os.path.join("venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        venv_python = "python"
    
    subprocess.run([venv_python, "manage.py", "runserver", "127.0.0.1:8000"])

def run_frontend():
    print("🎨 Starting Vite Frontend on http://127.0.0.1:5173")
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    
    if not os.path.exists(os.path.join(frontend_dir, "node_modules")):
        print("📦 Installing dependencies (holding for 30s)...")
        subprocess.run("npm install", shell=True, cwd=frontend_dir)
    
    subprocess.run("npm run dev", shell=True, cwd=frontend_dir)

if __name__ == "__main__":
    print("="*60)
    print("  NIFTY 100 INTEL - RESILIENT RUNNER")
    print("="*60)
    
    # Run both in separate threads so neither blocks the other
    t1 = threading.Thread(target=run_backend)
    t2 = threading.Thread(target=run_frontend)
    
    t1.daemon = True
    t2.daemon = True
    
    t1.start()
    time.sleep(1) # Give backend a head start
    t2.start()
    
    print("\n✅ System initialization complete.")
    print("🔗 Access Dashboard: http://127.0.0.1:5173")
    print("🛑 Press Ctrl+C to shut down both servers.\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
