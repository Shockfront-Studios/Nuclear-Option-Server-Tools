# Steam Game Server Update Checker

This script checks for updates to a Steam game server and sends a TCP command to the server if an update is available.

## Requirements

- [Python 3](https://www.python.org/downloads/) (Often pre-installed on modern Linux distributions like Ubuntu).
- [SteamCMD](https://developer.valvesoftware.com/wiki/SteamCMD). Make sure `steamcmd` is in your system's PATH.

## Installation

1.  **Clone this repository** or copy all the files to a directory on your server (e.g., `/home/steam/server-update-checker`).
2.  **Create symbolic links** for the systemd service files. This is better than copying because it makes future updates easier.
    *make sure paths are correct*
    ```bash
    sudo ln -s /home/steam/Nuclear-Option-AutoUpdater/systemd/nuclear_option.service /etc/systemd/system/
    sudo ln -s /home/steam/Nuclear-Option-AutoUpdater/systemd/nuclear_option_check_updates.service /etc/systemd/system/
    sudo ln -s /home/steam/Nuclear-Option-AutoUpdater/systemd/nuclear_option_check_updates.timer /etc/systemd/system/
    ```
3.  **Edit `config.json`** to set your server's installation directory.
4.  **Reload the systemd daemon**: 
    ```bash
    sudo systemctl daemon-reload
    ```
5.  **Make server directory**: the service may need the working directory to be created already to start running
    ```bash
    mkdir /home/steam/NuclearOptionServer
    ```
6.  **Enable and start the services**:
    ```bash
    # To start the server
    sudo systemctl enable --now nuclear_option.service

    # To enable the periodic update checker
    sudo systemctl enable --now nuclear_option_check_updates.timer
    ```

## Configuration

Edit the `config.json` file to match your server's configuration:

- `install_dir`: The absolute path to your game server's installation directory.
- `steam_beta_branch`: The Steam branch you want to check for updates. Leave empty for the default public branch.
- `RemoteCommandPort`: The port for the server's remote command listener.
