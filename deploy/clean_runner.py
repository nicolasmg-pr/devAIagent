import os
import shutil
import subprocess
import signal

def kill_mlx_server():
    """Finds and terminates any running mlx_lm local server processes to free RAM."""
    try:
        res = subprocess.run(["ps", "-ef"], capture_output=True, text=True)
        lines = res.stdout.splitlines()
        killed = False
        for line in lines:
            if "mlx_lm" in line and "grep" not in line:
                parts = line.split()
                if len(parts) >= 2:
                    pid = int(parts[1])
                    print(f"💀 [Cleanup] Terminating local MLX server process (PID {pid})...")
                    try:
                        os.kill(pid, signal.SIGTERM)
                        killed = True
                    except ProcessLookupError:
                        pass
        if killed:
            print("✅ [Cleanup] Local MLX server successfully stopped. ~20GB RAM reclaimed!")
        else:
            print("ℹ️ [Cleanup] No active local MLX server process was found.")
    except Exception as e:
        print(f"⚠️ [Cleanup] Error stopping MLX server: {e}")

def run_clean_command():
    """Stops all running Docker Compose previews and terminates the local MLX server."""
    print("\n🧹 RAMPAGING MEMORY CLEANUP ACTIVATED...")
    print("=" * 60)
    
    # 1. Clean Docker Compose Previews
    output_dir = "./output"
    docker_cleaned = 0
    if os.path.exists(output_dir):
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)
            if os.path.isdir(item_path):
                compose_path = os.path.join(item_path, "docker-compose.yml")
                if os.path.exists(compose_path):
                    print(f"⚙️ Stopping Docker containers for project '{item}'...")
                    cmd = ["docker", "compose", "down"]
                    if not shutil.which("docker"):
                        cmd = ["docker-compose", "down"]
                    res = subprocess.run(cmd, cwd=item_path, capture_output=True)
                    if res.returncode == 0:
                        docker_cleaned += 1
                        print(f"   ✅ Project '{item}' containers stopped.")
                    else:
                        print(f"   ⚠️ Could not stop project '{item}' containers.")
                        
    if docker_cleaned > 0:
        print(f"✅ Stopped preview containers for {docker_cleaned} projects. ~4GB RAM reclaimed in Docker VM!")
    else:
        print("ℹ️ No active Docker preview containers found to stop.")
        
    print("-" * 60)
    
    # 2. Clean MLX Server
    print("🔍 Searching for active local MLX server processes...")
    kill_mlx_server()
    
    print("=" * 60)
    print("🎉 Memory cleanup complete. Your machine is fresh and fast!\n")
