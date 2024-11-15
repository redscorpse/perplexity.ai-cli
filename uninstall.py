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
    """Get the path to the executable file that was installed."""
    dist_folder = os.path.join(os.getcwd(), "dist")
    executable_path = os.path.join(dist_folder, executable_name)

    # Try to find it in system-wide directories or user-specific directories
    if platform.system() == "Linux":
        # Check if it's in the user's local bin directory
        user_bin_path = os.path.expanduser("~/.local/bin")
        if os.path.exists(os.path.join(user_bin_path, executable_name)):
            executable_path = os.path.join(user_bin_path, executable_name)
        # Check if it's in /usr/local/bin
        elif os.path.exists(f"/usr/local/bin/{executable_name}"):
            executable_path = f"/usr/local/bin/{executable_name}"

    elif platform.system() == "Windows":
        # On Windows, check if it's in the PATH (typically installed globally)
        executable_path = shutil.which(executable_name)

    if not executable_path or not os.path.exists(executable_path):
        print(f"Error: Executable {executable_name} not found.")
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


def remove_executable(executable_path):
    """Remove the executable file."""
    try:
        os.remove(executable_path)
        print(f"Successfully removed executable: {executable_path}")
    except Exception as e:
        print(f"Error removing executable: {e}")
        sys.exit(1)


def remove_from_linux_path():
    """Remove the path modification from ~/.bashrc or /etc/profile."""
    install_dir = os.path.expanduser("~/.local/bin")
    bashrc_file = os.path.expanduser("~/.bashrc")

    if os.path.exists(bashrc_file):
        with open(bashrc_file, "r") as f:
            lines = f.readlines()

        with open(bashrc_file, "w") as f:
            for line in lines:
                if install_dir not in line:
                    f.write(line)
        print(
            f"Removed {install_dir} from {bashrc_file}. Please restart your terminal or run 'source ~/.bashrc'."
        )
    else:
        print(f"Could not find {bashrc_file}. Skipping PATH removal.")


def remove_from_windows_path():
    """Remove the executable directory from Windows PATH."""
    try:
        # Check if the directory containing the executable is in the PATH
        executable_dir = os.path.dirname(get_executable_path())
        subprocess.check_call(["setx", "PATH", "/M", f"%PATH%;{executable_dir}"])
        print(f"Successfully removed {executable_dir} from the system PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error modifying PATH on Windows: {e}")
        sys.exit(1)


def uninstall_on_linux():
    """Uninstall the executable on Linux."""
    executable_name = "perplexity.ai-cli"
    executable_path = get_executable_path(executable_name)

    # Ensure executable_path is a valid string before passing it to os.path.dirname
    if executable_path is None:
        print(f"Error: Executable path is None.")
        sys.exit(1)

    executable_dir = os.path.dirname(executable_path)

    # Now you can safely proceed with other logic, such as removing the executable
    print(f"Executable directory: {executable_dir}")

    # Continue with removing the executable and handling PATH if needed...
    remove_executable(executable_path)
    remove_from_linux_path()


def uninstall_on_windows():
    """Uninstall the executable on Windows."""
    executable_name = "perplexity.ai-cli"
    executable_path = get_executable_path(executable_name)

    # Ensure executable_path is valid
    if executable_path is None:
        print(f"Error: Executable path is None.")
        sys.exit(1)

    executable_dir = os.path.dirname(executable_path)

    print(f"Executable directory: {executable_dir}")

    # Remove executable
    remove_executable(executable_path)

    # Remove from PATH (if added to the system PATH)
    remove_from_windows_path()


def main():
    # Determine which OS the script is running on
    if platform.system() == "Linux":
        uninstall_on_linux()
    elif platform.system() == "Windows":
        uninstall_on_windows()
    else:
        print(f"Unsupported OS: {platform.system()}")
        sys.exit(1)

    print("Uninstallation complete.")


if __name__ == "__main__":
    main()
