#!/usr/bin/env python
"""
Project management script that provides various utility commands.
Run with `python -m main [command]` from the project root.
"""

import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv

from scripts.generate_env_vars import generate_env_vars
from scripts.update_env import update_env
from scripts.docker_commands import start, stop
from scripts.project_init import init, reset, update


def main():
    """Main entry point for the script."""
    # Load environment variables from .env file
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)

    parser = argparse.ArgumentParser(description="Project management commands")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Register commands
    subparsers.add_parser("generate_env_vars", help="Generate environment variables and print them")
    subparsers.add_parser("update_env", help="Update environment variables")
    subparsers.add_parser("init", help="Initialize the project")
    subparsers.add_parser("start", help="Start the project")
    subparsers.add_parser("stop", help="Stop the project")
    subparsers.add_parser("update", help="Update the project")
    subparsers.add_parser("reset", help="Reset the project by deleting all data")

    args = parser.parse_args()

    # Run the appropriate function based on the command
    if args.command == "generate_env_vars":
        generate_env_vars()
    elif args.command == "update_env":
        update_env()
    elif args.command == "init":
        init()
    elif args.command == "start":
        start()
    elif args.command == "stop":
        stop()
    elif args.command == "update":
        update()
    elif args.command == "reset":
        reset()
    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
