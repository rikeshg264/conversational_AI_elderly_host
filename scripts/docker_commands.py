import os
import subprocess
from scripts.utils import run_command

def check_project_running(project_prefix):
    """Check if containers with the given project prefix are running."""
    try:
        # List all containers in JSON format
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
        container_names = result.stdout.strip().split('\n')
        return any(project_prefix in name for name in container_names if name)
    except subprocess.CalledProcessError:
        return False

def start():
    """Start the project."""
    project_name = os.getenv('PROJECT_NAME')
    if not project_name:
        print("Error: PROJECT_NAME not found in environment")
        print("Please make sure you have a .env file with PROJECT_NAME defined")
        print("You can create one by running: python -m script update_env")
        return
    
    # Check if either n8n or supabase services are already running
    if check_project_running(f"{project_name}_n8n") or check_project_running(f"{project_name}_supabase"):
        print(f"\nProject '{project_name}' is already running!")
        print("To stop it, run: python -m script stop")
        print("To see running containers: docker ps")
        return
    
    # Start Supabase services with project name
    print("Starting Supabase...")
    run_command([
        "docker", "compose",
        "-f", "supabase/docker/docker-compose.yml",
        "-p", f"{project_name}_supabase",
        "up", "-d"
    ])

    # Start n8n services with project name
    print("Starting n8n...")
    run_command([
        "docker", "compose",
        "-p", f"{project_name}_n8n",
        "up", "-d"
    ])

    print("\nServices started!")
    print("- n8n: http://localhost:5678")
    print("- Supabase Dashboard: http://localhost:8000")
    print("- Supabase Inside N8N: http://host.docker.internal:8000")


def stop():
    """Stop the project."""
    project_name = os.getenv('PROJECT_NAME')
    if not project_name:
        print("Error: PROJECT_NAME not found in environment")
        print("Please make sure you have a .env file with PROJECT_NAME defined")
        print("You can create one by running: python -m script update_env")
        return
    
    print("Stopping n8n services...")
    run_command([
        "docker", "compose",
        "-p", f"{project_name}_n8n",
        "down"
    ], ignore_errors=True)

    print("Stopping Supabase services...")
    run_command([
        "docker", "compose",
        "-f", "supabase/docker/docker-compose.yml",
        "-p", f"{project_name}_supabase",
        "down"
    ], ignore_errors=True)

    print("\nAll services stopped!") 