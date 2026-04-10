import subprocess

def run_command(cmd, cwd=None, ignore_errors=False):
    """Run a shell command and print it."""
    print("Running:", " ".join(cmd) if isinstance(cmd, list) else cmd)
    try:
        return subprocess.run(
            cmd,
            cwd=cwd,
            shell=isinstance(cmd, str),
            check=not ignore_errors
        )
    except subprocess.CalledProcessError as e:
        if not ignore_errors:
            raise e 