import json
import subprocess
import os
import re
from remote_commander import RemoteCommander


def get_latest_build_id(app_id, branch, install_dir):
    """
    Gets the latest build ID for a given app and branch from SteamCMD.
    """
    if not branch:
        branch = "public"

    try:
        command = [
            "/usr/games/steamcmd",
            "+login", "anonymous",
            "+app_info_print", app_id,
            "+quit"
        ]
        process = subprocess.run(
            command, capture_output=True, text=True, check=True, encoding='utf-8', cwd=install_dir)

        lines = process.stdout.splitlines()
        in_branches_section = False
        in_target_branch_section = False

        for line in lines:
            # print(line)
            stripped_line = line.strip()

            if not in_branches_section:
                if stripped_line == '"branches"':
                    in_branches_section = True
                continue

            # We are inside the "branches" section.
            if not in_target_branch_section:
                if stripped_line == f'"{branch}"':
                    in_target_branch_section = True
                continue

            # We are inside the target branch's section.
            if '"buildid"' in stripped_line:
                match = re.search(r'"buildid"\s+"(\d+)"', stripped_line)
                if match:
                    return match.group(1)

            # If we see a '}' this could be the end of our section.
            if stripped_line == '}':
                # We were in the target branch, but we're leaving.
                # The buildid was not found.
                if in_target_branch_section:
                    break

        print(
            f"Could not find build ID for branch '{branch}'. full result below:")
        for line in lines:
            print(line)
        return None

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error running steamcmd: {e}")
        print("Please ensure steamcmd is installed and in your system's PATH.")
        return None


def get_local_build_id(manifest_path):
    """
    Gets the local build ID from the appmanifest file.
    """
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            for line in f:
                # check TargetBuildID instead, because buildid might be a merged build id from multiple depots
                if '"TargetBuildID"' in line:
                    match = re.search(r'"TargetBuildID"\s+"(\d+)"', line)
                    if match:
                        return match.group(1)
        print("Could not parse build ID from appmanifest file.")
        return None
    except FileNotFoundError:
        print(f"Could not find appmanifest file at: {manifest_path}")
        return None


def main():
    """
    Main function to check for updates and notify the server.
    """
    try:
        with open("config.json", 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("config.json not found. Please create it.")
        return

    install_dir = config.get("install_dir")
    branch = config.get("steam_beta_branch")
    remote_command_port = config.get("RemoteCommandPort")

    if not all([install_dir, remote_command_port]):
        print("Invalid config.json. Please check the contents.")
        return

    app_id = "3930080"
    manifest_path = os.path.join(
        install_dir, "steamapps", f"appmanifest_{app_id}.acf")

    print("Checking for updates...")
    latest_build_id = get_latest_build_id(app_id, branch, install_dir)
    local_build_id = get_local_build_id(manifest_path)

    print(f"Latest build ID: {latest_build_id}")
    print(f"Local build ID:  {local_build_id}")

    if latest_build_id and local_build_id and latest_build_id != local_build_id:
        print("New update available!")
        commander = RemoteCommander("localhost", remote_command_port)
        status_code, response = commander.send_command("update-ready")
        if status_code == "Success":
            print("Command success")
        else:
            print(f"Command failed with status: {status_code}")
    else:
        print("No new update available.")


if __name__ == "__main__":
    main()
