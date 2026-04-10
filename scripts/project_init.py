import os
import subprocess
import shutil
from pathlib import Path

from scripts.utils import run_command
from scripts.update_env import update_env, update_supabase_env

def init():
    """Initialize the project by setting up Supabase and environment variables."""
    # Check if .env exists, if not ask to create it
    if not Path(".env").exists():
        print("No .env file found.")
        response = input("Would you like to create it now? (y/N): ").strip().lower()
        if response == 'y':
            update_env()
        else:
            print("Cannot proceed without environment variables.")
            return

    # Check if Supabase already exists
    if Path("supabase").exists():
        print("Supabase repository already exists. Run 'update' command to update it.")
        return

    # Clone Supabase repository
    print("Cloning the Supabase repository...")
    run_command([
        "git", "clone", "--filter=blob:none", "--no-checkout",
        "https://github.com/supabase/supabase.git"
    ])
    os.chdir("supabase")
    run_command(["git", "sparse-checkout", "init", "--cone"])
    run_command(["git", "sparse-checkout", "set", "docker"])
    run_command(["git", "checkout", "master"])
    os.chdir("..")

    # Stop any existing containers
    print("Stopping any existing containers...")
    run_command([
        "docker", "compose",
        "-f", "supabase/docker/docker-compose.yml",
        "down"
    ], ignore_errors=True)

    # Update only Supabase's environment variables
    update_supabase_env()

    print("Project initialized successfully")
    print("\nYou can now:")
    print("1. Review the environment variables in .env")
    print("2. Start the project using: python -m script start")


def reset():
    """Reset the project by deleting all data.
    
    This will remove all data, including databases, containers, and volumes.
    User will be asked to confirm before proceeding.
    """
    print("\033[91m" + "WARNING: This will delete ALL data in the project!" + "\033[0m")
    print("This includes:")
    print("- All database data")
    print("- All docker containers")
    print("- All docker volumes")
    print("- All Supabase data and containers")
    print("- Any stored workflows and credentials")
    print("\nThis action CANNOT be undone!")
    
    confirmation = input("To confirm, please type 'DELETE ALL DATA': ").strip()
    
    if confirmation != "DELETE ALL DATA":
        print("Reset cancelled.")
        return
    
    print("Stopping all containers...")
    # Stop both n8n and Supabase containers
    subprocess.run(["docker", "compose", "down"], check=False)
    subprocess.run([
        "docker", "compose",
        "-f", "supabase/docker/docker-compose.yml",
        "down", "-v", "--remove-orphans"
    ], check=False)
    
    print("Removing all volumes...")
    # Get all project-related volumes
    result = subprocess.run(
        ["docker", "volume", "ls", "--filter", "name=n8n", "--filter", "name=supabase", "--quiet"],
        check=True, 
        capture_output=True, 
        text=True
    )
    
    volumes = result.stdout.strip().split('\n')
    volumes = [v for v in volumes if v]  # Remove empty strings
    
    if volumes:
        # Remove each volume
        for volume in volumes:
            print(f"Removing volume: {volume}")
            subprocess.run(["docker", "volume", "rm", "-f", volume], check=False)
    
    print("Pruning unused volumes...")
    subprocess.run(["docker", "volume", "prune", "-f"], check=False)
    
    # Remove Supabase directory if it exists
    supabase_dir = Path("supabase")
    if supabase_dir.exists():
        print("Removing Supabase directory...")
        shutil.rmtree(supabase_dir)
    
    print("All data has been reset. You can now run 'init' to start fresh.")


def update():
    """Update the project."""
    print("update") 