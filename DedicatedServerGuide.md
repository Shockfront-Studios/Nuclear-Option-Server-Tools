## How to run server

- **Install SteamCMD** 
  - instructions: https://developer.valvesoftware.com/wiki/SteamCMD
  - create user called `steam` or change `force_install_dir` to be your full path 

- **Install NuclearOptionServer**
template: 
```sh
steamcmd +force_install_dir <install_dir> +login anonymous +app_update 3930080 -beta <branch> -betapassword <branch_pw> validate +quit
```
example:
```sh
steamcmd +force_install_dir /home/steam/NuclearOptionServer +login anonymous +app_update 3930080 validate +quit
```
- **UDP ports** 
  - (defaults, can be changed in `DedicatedServerConfig.json`)
  - if running locally or behind firewall then these UDP ports might need to be opened to allow users to find and connect to the server
  - game port `7777`
  - query port `7778`

- **Run Server (linux)**
  - `cd NuclearOptionServer` enter the install directory
  - `chmod +x NuclearOptionServer.x86_64` *set server as executable*
  - `chmod +x RunServer.sh` *set the bash script as executable*
  - `./RunServer.sh`
    - `RunServer.sh` can be edited copied or modified to change how it is run

- **Run Server (windows)**
  - `cd NuclearOptionServer` enter the install directory
  - `./RunServer.bat`
    - `RunServer.bat` can be edited copied or modified to change how it is run
  - or run manually using `NuclearOptionServer.exe -logFile server.log -limitframerate 30`

- use `-DedicatedServer <json path>` argument to set custom config path
  - on linux this should be added to `RunServer.sh` 

- **Configure** `DedicatedServerConfig.json`
  - After first running the server DedicatedServerConfig.json will be created with default values, you can then edit this to change the server settings


example config
```json
{
    "MissionDirectory": "/home/steam/NuclearOption-Missions",
    "ModdedServer": false,
    "Hidden": false,
    "ServerName": "Nuclear Option Server",
    "Port": {
        "IsOverride": false,
        "Value": 0
    },
    "QueryPort": {
        "IsOverride": false,
        "Value": 0
    },
    "Password": "",
    "MaxPlayers": 16,
    "NoPlayerStopTime": 30.0,
    "BanListPaths": [
        "./banlist1.txt",
        "./banlist2.txt"
    ],
    "RotationType": 0,
    "MissionRotation": [
        {
            "Key": {
                "Group": "BuiltIn",
                "Name": "Escalation"
            },
            "MaxTime": 7200.0
        },
        {
            "Key": {
                "Group": "BuiltIn",
                "Name": "Terminal Control"
            },
            "MaxTime": 7200.0
        },
        {
            "Key": {
                "Group": "User",
                "Name": "Custom Mission"
            },
            "MaxTime": 7200.0
        }
    ]
}
```

### Mission Rotation

The `RotationType` field can be changed to tell the server in what order to play the missions. Set the value to one of the following numeric codes:

| Value | Rotation Method | Description |
| :---: | :--- | :--- |
| `0` | **Sequence** | Missions are selected in the order. |
| `1` | **Pure Random** | Each missions is selected at random, allowing for immediate repeats. |
| `2` | **Random Queue** | Missions are shuffled and selected in that random order, guaranteeing that all missions are played before the shuffle repeats. |

### Loading Missions

Mission group options:
- `Default` *loads from game files*
- `Tutorial` *loads from game files*
- `BuiltIn` *loads from game files*
- `User` *loads from `MissionDirectory` folder*
- ~~`Workshop`~~ *not implemented* (use `User` instead)

when using `MissionDirectory`, mission will be loaded at path `<MissionDirectory>/<name>/<name>.json`.

For example if `MissionDirectory` is `/home/steam/NuclearOption-Missions` and mission name is `test1` then the path will be `/home/steam/NuclearOption-Missions/test1/test1.json`

**note:** MissionDirectory should be a full path

**Important:** The mission folder name must exactly match the mission JSON file's base name.  
For example, for a mission named `test1`, the folder must be `.../test1/` and the file must be `.../test1/test1.json`. If these names do not match, the mission will not load.

#### Workshop missions
- Download workshop items using steamcmd. You must log in with a Steam account that owns NuclearOption (see [SteamCmd](https://developer.valvesoftware.com/wiki/SteamCMD)). Anonymous login cannot access Workshop content.
- After download, copy the mission folder to `<MissionDirectory>` and **ensure the folder name matches the mission JSON file** name as noted above.
- Use `User` group in `DedicatedServerConfig.json`.

Login and download (interactive login; you'll be prompted for password/Steam Guard):
```sh
steamcmd +login <your_steam_username> +workshop_download_item 2168680 <WorkshopID> +quit
```

By default, Workshop files are placed under `.../steamapps/workshop/content/2168680/<WorkshopID>/`. Locate the mission folder within that directory, copy it into your `<MissionDirectory>`, and verify the folder name exactly matches the mission's JSON filename.


## Troubleshooting

### Check if server started correctly

With the default run arguments the server will create log files in the `logs` directory with the timestamp the server was started. (`./logs/server-$(date +%Y-%m-%d-%H-%M-%S).log`). Checking these log files will help tell you if the server started correctly.

If you see this line, it is likely the server is running ok: `[DedicatedServerManager] Waiting for Players before loading next map`.


### Steam Server Query

To check if your server is accessible on the query point, there are two ways:
1.  **Using a Steam server query tool:** Various online tools and applications allow you to query Steam servers directly. Provide your server's IP address and query port (default `7778`) to these tools. (example tool: https://saraserenity.net/steam/server_query.php)

2.  **Using the in-game server list:** Attempt to find your server in the game's server browser. If it doesn't appear, check your client-side log files (`%USERPROFILE%\AppData\LocalLow\Shockfront\NuclearOption\Player.log`) for entries like:
    `[Warn] Request Server List, fail index:<i>, Query Address:<ip>:<query port>`
    where `<ip>` and `<query port>` correspond to your server's details.


### NAT Reflection (running server on the same network as client)

If you are absolutely sure that your port forwarding settings are correct yet you cannot see your server listed in the game, check if your router has NAT reflection enabled on your port. This issue usually occurs when it's disabled and you're in the same network as the server. However, not all routers will have an option to enable NAT reflection at all.
