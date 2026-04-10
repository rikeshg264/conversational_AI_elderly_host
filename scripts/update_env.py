"""
Update environment variables by copying from .env.example and updating with secure values.
"""
import re
import uuid
import shutil
from pathlib import Path
from datetime import datetime

# Import the generate_env_vars function
from scripts.generate_env_vars import generate_env_vars


def read_env_file(file_path):
    """Read and parse environment variables from a file into a dictionary."""
    env_vars = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    return env_vars


def update_env_content(content, variables):
    """Update environment variables in content string with new values."""
    updated_content = content
    for key, value in variables.items():
        pattern = re.compile(f"^{re.escape(key)}=.*$", re.MULTILINE)
        if pattern.search(updated_content):
            updated_content = pattern.sub(f"{key}={value}", updated_content)
            print(f"Updated {key}")
        else:
            if updated_content and not updated_content.endswith('\n'):
                updated_content += '\n'
            updated_content += f"{key}={value}\n"
            print(f"Added {key}")
    return updated_content


def create_env_backup():
    """Create a backup of the current .env file."""
    env_path = Path(".env")
    backup_path = Path(f".env.backup.{datetime.now().strftime('%Y%m%d%H%M%S')}")
    shutil.copy2(env_path, backup_path)
    print(f"Created backup of .env at {backup_path}")


def get_user_confirmation():
    """Get user confirmation for updating existing .env file."""
    print("Warning: .env file already exists")
    print("Updating environment variables may impact access to the database")
    return input("Do you want to continue? (y/N): ").strip().lower() == 'y'


def update_supabase_env():
    """Update Supabase environment variables from local .env."""
    supabase_dir = Path("supabase")
    if not supabase_dir.exists():
        return None

    supabase_env_example = supabase_dir / "docker" / ".env.example"
    supabase_env = supabase_dir / "docker" / ".env"
    local_env = Path(".env")

    if not all(path.exists() for path in [supabase_env_example, local_env]):
        print("Warning: Required Supabase environment files not found")
        return None

    print("Copying Supabase .env.example to .env...")
    shutil.copy2(supabase_env_example, supabase_env)

    local_vars = read_env_file(local_env)
    
    with open(supabase_env, 'r') as f:
        supabase_content = f.read()
    
    updated_content = update_env_content(supabase_content, local_vars)
    
    with open(supabase_env, 'w') as f:
        f.write(updated_content)
    
    print("Supabase environment variables updated successfully")


def generate_project_name():
    """Generate a unique project name."""
    return f"n8n_supabase_{uuid.uuid4().hex[:8]}"


def update_env():
    """Update environment variables."""
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if not env_example_path.exists():
        print("Error: .env.example file not found")
        print("Please create an .env.example file first")
        return None
    
    if env_path.exists():
        if not get_user_confirmation():
            print("Operation canceled")
            return None
        create_env_backup()
    
    print(f"Copying .env.example to .env")
    shutil.copy2(env_example_path, env_path)
    
    new_vars = generate_env_vars()
    new_vars['PROJECT_NAME'] = generate_project_name()
    
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    updated_content = update_env_content(env_content, new_vars)
    
    with open(env_path, 'w') as f:
        f.write(updated_content)
    
    print(f"Environment variables updated in {env_path}")
    
    update_supabase_env()
    
    return new_vars


if __name__ == "__main__":
    update_env()