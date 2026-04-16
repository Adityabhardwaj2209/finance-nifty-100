import subprocess
import os
import time

frontend_dir = os.path.join(os.getcwd(), "frontend")
log_file = os.path.join(os.getcwd(), "vite_diagnostic.log")

print(f"Starting diagnostic... log will be at {log_file}")

with open(log_file, "w") as f:
    f.write("=== VITE DIAGNOSTIC START ===\n")
    try:
        # Check npm version
        npm_v = subprocess.run("npm --version", shell=True, capture_output=True, text=True)
        f.write(f"npm version: {npm_v.stdout.strip()}\n")
        
        # Check if node_modules exists
        if os.path.exists(os.path.join(frontend_dir, "node_modules")):
            f.write("node_modules: FOUND\n")
        else:
            f.write("node_modules: MISSING\n")
            
        # Try to run vite --version
        vite_v = subprocess.run("npx vite --version", shell=True, capture_output=True, text=True, cwd=frontend_dir)
        f.write(f"Vite version: {vite_v.stdout.strip() if vite_v.stdout else 'ERROR or EMPTY'}\n")
        f.write(f"Vite stderr: {vite_v.stderr.strip()}\n")
        
        # Try to start the server for 10 seconds and capture output
        print("Starting Vite for 10s...")
        process = subprocess.Popen(
            "npm run dev -- --host 127.0.0.1", 
            shell=True, 
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit
        time.sleep(10)
        
        # Check if it's still running
        poll = process.poll()
        if poll is None:
            f.write("Vite process: STILL RUNNING after 10s (GOOD)\n")
            process.terminate()
        else:
            f.write(f"Vite process: EXITED with code {poll} (BAD)\n")
            
        stdout, stderr = process.communicate()
        f.write("=== STDOUT ===\n")
        f.write(stdout)
        f.write("\n=== STDERR ===\n")
        f.write(stderr)
        
    except Exception as e:
        f.write(f"DIAGNOSTIC CRASHED: {str(e)}\n")

print("Done. Read vite_diagnostic.log")
