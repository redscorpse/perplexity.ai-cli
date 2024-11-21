import os
import subprocess
import sys


def create_virtualenv(env_name):
    """Create a virtual environment."""
    if not os.path.exists(env_name):
        print(f"Creating virtual environment: {env_name}...")
        subprocess.check_call([sys.executable, "-m", "venv", env_name])
    else:
        print(f"Virtual environment {env_name} already exists.")


def install_requirements(env_name, requirements_file="requirements.txt"):
    """Install dependencies from requirements.txt."""
    pip_path = (
        os.path.join(env_name, "bin", "pip")
        if sys.platform != "win32"
        else os.path.join(env_name, "Scripts", "pip.exe")
    )

    if os.path.exists(requirements_file):
        print(f"Installing dependencies from {requirements_file}...")
        subprocess.check_call([pip_path, "install", "-r", requirements_file])
    else:
        print(f"{requirements_file} not found.")
        sys.exit(1)


def build_executable_with_pyinstaller(
    script_name="perplexity.ai-cli.py", venv_path="./ppl-ai-venv"
):
    """Use PyInstaller to create a single-file executable."""
    print("Activating the virtual environment...")
    activate_virtualenv(venv_path)

    print("Building the executable with PyInstaller...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "PyInstaller", "--onefile", script_name]
        )
    except subprocess.CalledProcessError as e:
        print(f"Error during PyInstaller execution: {e}")
        sys.exit(1)


def activate_virtualenv(venv_path):
    """Activate the virtual environment."""
    if not os.path.exists(venv_path):
        raise FileNotFoundError(f"Virtual environment not found at: {venv_path}")

    # Activate the virtual environment by modifying PATH and sys.executable
    venv_bin = os.path.join(venv_path, "bin")  # For Linux/Mac
    if not os.path.exists(venv_bin):
        raise FileNotFoundError(f"Virtual environment bin folder not found: {venv_bin}")

    os.environ["PATH"] = f"{venv_bin}:{os.environ['PATH']}"
    sys.executable = os.path.join(venv_bin, "python")


def main():
    env_name = "ppl-ai-venv"

    create_virtualenv(env_name)

    install_requirements(env_name)

    build_executable_with_pyinstaller()


if __name__ == "__main__":
    main()
