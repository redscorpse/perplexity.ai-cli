import os
import platform
import shutil
import subprocess
import sys


def is_windows():
    """Check if the system is Windows."""
    return platform.system() == "Windows"


def is_linux():
    """Check if the system is Linux."""
    return platform.system() == "Linux"


def get_executable_path(executable_name="perplexity.ai-cli"):
    """Get the path to the executable file created by PyInstaller."""
    # The executable should be in the 'dist' folder
    dist_folder = os.path.join(os.getcwd(), "dist")
    executable_path = os.path.join(dist_folder, executable_name)

    if not os.path.exists(executable_path):
        print(f"Error: Executable {executable_name} not found in the dist directory.")
        sys.exit(1)

    return executable_path


def run_command(command, use_sudo=False):
    """Run a command, optionally with sudo."""
    if use_sudo:
        command = ["sudo"] + command  # Prepend sudo if necessary
    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        sys.exit(1)


def run_build_script():
    """Run the build script (build.py) to generate the executable."""
    print("Running the build script (build.py)...")
    try:
        subprocess.check_call([sys.executable, "build.py"])
    except subprocess.CalledProcessError as e:
        print(f"Error running build script: {e}")
        sys.exit(1)


def install_on_windows(executable_path):
    """Install the executable by adding its folder to the Windows PATH."""
    # Get the directory of the executable
    executable_dir = os.path.dirname(executable_path)

    # Add executable directory to PATH environment variable
    print(f"Adding {executable_dir} to system PATH...")
    try:
        # Update the PATH permanently for the user
        subprocess.check_call(["setx", "PATH", f"%PATH%;{executable_dir}"])
        print(f"Successfully added {executable_dir} to PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error adding to PATH: {e}")
        sys.exit(1)


def install_on_linux(executable_path):
    """Install the executable by moving it to /usr/local/bin or $HOME/.local/bin."""
    # Check if the user has root privileges
    is_root = os.geteuid() == 0

    # Decide the installation directory based on whether we are root or not
    if is_root:
        install_dir = "/usr/local/bin"
    else:
        install_dir = os.path.expanduser("~/.local/bin")

    # Create the target directory if it doesn't exist
    if not os.path.exists(install_dir):
        print(f"Creating directory {install_dir}...")
        os.makedirs(install_dir, exist_ok=True)

    # Copy the executable to the install directory
    try:
        shutil.copy(executable_path, install_dir)
        print(f"Executable installed to {install_dir}.")
    except Exception as e:
        print(f"Error copying executable: {e}")
        sys.exit(1)

    # Ensure the install directory is in the PATH
    if install_dir not in os.environ["PATH"]:
        print(f"Adding {install_dir} to PATH...")
        if is_root:
            # If we are root, we can modify global configuration
            run_command(
                [
                    "sh",
                    "-c",
                    f"echo 'export PATH=\"$PATH:{install_dir}\"' >> /etc/profile",
                ],
                use_sudo=True,
            )
            print(
                f"Added {install_dir} to /etc/profile. This will take effect for all users after a reboot or new shell."
            )
        else:
            # For non-root users, we add it to ~/.bashrc or ~/.profile
            with open(os.path.expanduser("~/.bashrc"), "a") as f:
                f.write(
                    f'\n# Added by install script\nexport PATH="$PATH:{install_dir}"\n'
                )
            print(
                f"Added {install_dir} to ~/.bashrc. Please restart your terminal or run 'source ~/.bashrc'."
            )


def main():
    run_build_script()

    # Name of the executable created by PyInstaller (without extension)
    executable_name = "perplexity.ai-cli"

    # Get the path of the generated executable
    executable_path = get_executable_path(executable_name)

    # Install on Windows
    if is_windows():
        install_on_windows(executable_path)
    # Install on Linux
    elif is_linux():
        install_on_linux(executable_path)
    else:
        print(f"Unsupported OS: {platform.system()}")
        sys.exit(1)

    print(
        f"Installation successful. You can now run {executable_name} from any terminal."
    )


if __name__ == "__main__":
    main()
