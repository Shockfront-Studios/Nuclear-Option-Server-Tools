# Server Remote Command

Remote commands can be enabled by adding `-ServerRemoteCommands [port]` when running from command line. If the port is not given then it will default to `7779`.

## Command and Response Structures

All commands and responses are sent over a custom TCP format.

### Command Message (Client $\rightarrow$ Server)

This structure is used to send a command from the client to the server. It is serialized into **UTF8 JSON** and is preceded by a **4-byte length** prefix.

```json
{
    "name": "command-name",
    "arguments": [
        "argument 0",
        "argument 1",
        "argument 2",
    ]
}
```

**TCP Format:**

1.  **4 Bytes:** Length of the JSON data (Little-Endian).
2.  **Length Bytes:** UTF8 JSON string of the `CommandMessage` struct.

### Command Response (Server $\rightarrow$ Client)

**TCP Format:**

1.  **4 Bytes:** The `StatusCode` as an integer (e.g., `2000` for Success).
2.  **4 Bytes:** Length of the Json data (0 if no body is present).
3.  **Length Bytes:** UTF8 JSON data (only present if length \> 0).

### Status Codes

| Code | Name | Description |
| :--- | :--- | :--- |
| **2000** | `Success` | |
| **4000** | `BadRequest` | General malformed request. |
| **4001** | `BadHeader` | Error in the request header |
| **4002** | `BadLength` | Invalid length, either negative or too large |
| **4003** | `JsonError` | Failed to parse the `CommandMessage` JSON. |
| **4004** | `UnknownCommand` | The requested command name is not recognized. |
| **4005** | `BadArguments` | The command was recognized, but the provided arguments are invalid or missing. |
| **5000** | `InternalServerError` | General server-side error. |
| **5001** | `CommandError` | An error occurred during the execution of the command's logic. |
| **5002** | `ConfigError` | The server configuration prevents the command from completing (e.g., no ban lists configured). |

-----

## Default Server Commands

### `update-ready`

Notifies the server that a component is ready, likely to progress a startup sequence.

```json
{
    "name": "update-ready",
    "arguments": []
}
```

### `send-chat-message`

Sends a server message to be displayed in the in-game chat.

Can use rich text to change color and style of message. [Rich Text Supported Tags.](https://docs.unity3d.com/Packages/com.unity.textmeshpro@3.2/manual/RichTextSupportedTags.html)

```json
{
    "name": "send-chat-message",
    "arguments": [
        "<color=#ff0000><b>Alert:</b></color> Important server message."
    ]
}
```

### `reload-config`

Instructs the dedicated server to reload its configuration.

If path is given it will load the new file, otherwise it will reload the previous path used.

```json
{
    "name": "reload-config",
    "arguments": [
        "Optional/path/to/new/config.json" // Optional
    ]
}
```

### `get-mission-time`

Retrieves the current and maximum mission time.

```json
{
    "name": "get-mission-time",
    "arguments": []
}
```

#### Response

If no players are on the server will return 0 for both values.
Values are in seconds

```csharp
{
    "currentTime": 0,
    "maxTime": 0
}
```

### `get-mission`

Retrieves the currently running mission and the next mission scheduled.

```json
{
    "name": "get-mission",
    "arguments": []
}
```

#### Response

```json
{
    "currentMission": {
        "Key": {
            "Group": "BuiltIn",
            "Name": "Escalation"
        },
        "MaxTime": 3600.0
    },
    "nextMission": {
        "Key": {
            "Group": "BuiltIn",
            "Name": "Terminal Control"
        },
        "MaxTime": 3600.0
    }
}
```

### `get-server-id`

Retrieves the Steam ID of the server.

```json
{
    "name": "get-server-id",
    "arguments": []
}
```

#### Response

```json
{
    "serverId": "01234567891234567"
}
```

### `get-player-list`

Retrieves the current connected player list from the server.

```json
{
    "name": "get-player-list",
    "arguments": []
}
```

#### Response
The dedicated server returns only the `steamId`, `faction`, `playerIndex` and `serverTag` fields (the `displayName` field has been removed since the server runs headlessly and does not cache names).

The external server can fetch steam name using Steam's Web API.

Players who are still loading into the map are included.

```json
{
    "Players": [
        {
            "steamId": "0123456789",
            "faction": "Boscali",
            "playerIndex": 1,
            "serverTag": "ADMIN"
        },
        {
            "steamId": "9876543210",
            "faction": "Primeva",
            "playerIndex": 2,
            "serverTag": ""
        }
    ]
}
```

`playerIndex` is the player's number shown in game (eg `[3] PlayerName` in chat or on the leaderboard):
- 1-based, `0` means not assigned yet
- Stays the same if the player reconnects during the same mission
- Changes when the mission changes: connected players are renumbered `1..N`, and a player who rejoins after a mission change gets a new index
- Older game servers don't send this field, treat it as optional (default `0`)

**NOTE:** Do not store `playerIndex` as a player's identity, always store `steamId`. To target a player by `playerIndex` (eg kick/ban), call `get-player-list` first to find their `steamId`, then use the `steamId` based command.

`serverTag` is the tag shown next to the player's name in game:
- Empty if the player has no tag set, or is still loading
- Older game servers don't send this field, treat it as optional (default `""`)

### `set-time-remaining`

Sets the remaining time for the current mission, in seconds

```json
{
    "name": "set-time-remaining",
    "arguments": [
        "600.0"
    ]
}
```

### `set-next-mission`

Sets the mission to be loaded next after the current one concludes.

```json
{
    "name": "set-next-mission",
    "arguments": [
        "BuiltIn", // group
        "Escalation", // name
        "3600.0" // max time (in seconds)
    ]
}
```

### `kick-player`

Kicks a player from the server.

If kicked the player will be unable to rejoin until the server starts.

```json
{
    "name": "kick-player",
    "arguments": [
        "0123456789", // ulong SteamID to kick
    ]
}
```

### `unkick-player`

Removes player from kick list, allowing them to rejoin.

```json
{
    "name": "unkick-player",
    "arguments": [
        "0123456789", // ulong SteamID to kick
    ]
}
```


### `clear-kicked-players`

Clears the list of kicked players allowing them to rejoin.

```json
{
    "name": "clear-kicked-players",
    "arguments": []
}
```

### `banlist-reload`

Reloads the ban list and error kick immune list from the files in server config (`BanListPaths` and `ErrorKickImmuneListPaths`).

**NOTE:** Will only add new Ids, use `banlist-clear` (ban list) or `immunelist-clear` (immune list) before reload if you want to remove all ids first before loading the files again

```json
{
    "name": "banlist-reload",
    "arguments": []
}
```

### `banlist-add`

Adds a SteamID to the ban list appends it to the first configured ban file.

```json
{
    "name": "banlist-add",
    "arguments": [
        "0123456789", // ulong SteamID to ban
        "cheating", // optional reason
    ]
}
```

### `banlist-remove`

Removes a SteamID from the ban list and from the first configured ban file

```json
{
    "name": "banlist-remove",
    "arguments": [
        "0123456789", // ulong SteamID to unban
    ]
}
```

### `banlist-clear`

Clears the ban list loaded in the Authenticator. **NOTE:** This command does **not** modify any ban list files. 

Does not clear the error kick immune list, use `immunelist-clear` for that.

```json
{
    "name": "banlist-clear",
    "arguments": []
}
```

### `immunelist-clear`

Clears the error kick immune list loaded in the Authenticator. **NOTE:** This command does **not** modify any immune list files.

Use `banlist-reload` after to load the files from `ErrorKickImmuneListPaths` again, eg after removing an id from a file.

Older game servers don't have this command and will reply with `UnknownCommand`.

```json
{
    "name": "immunelist-clear",
    "arguments": []
}
```

### `stafflist-reload`

Reloads the staff list from the files in `StaffListPaths` in server config, and updates players in the match whose permission level or tag changed. See `DedicatedServerGuide.md` for the staff list file format.

**NOTE:** Unlike `banlist-reload`, this is a full sync with the files. Players removed from the files go back to `Player` level with no tag, so there is no clear command.

**NOTE:** Assumes no mods are setting permission levels or tags. A player removed from the files has their level and tag reset, even if a mod set them.

`reload-config` also reloads the staff list in the same way.

Older game servers don't have this command and will reply with `UnknownCommand`.

```json
{
    "name": "stafflist-reload",
    "arguments": []
}
```

### `get-mission-rotation`

Retrieves the current mission rotation configuration, type, and next override status.

```json
{
    "name": "get-mission-rotation",
    "arguments": []
}
```

#### Response

```json
{
    "rotationType": "Sequence",
    "rotation": [
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
        }
    ],
    "hasNextOverride": true,
    "nextOverride": {
        "Key": {
            "Group": "BuiltIn",
            "Name": "Escalation"
        },
        "MaxTime": 3600.0
    }
}
```

### `set-mission-rotation`

Sets the mission rotation configuration in memory and reloads the configuration.

Since `arguments` is an array of strings, the rotation configuration object must be serialized/encoded into a JSON string and passed as the first element (`arguments[0]`).

**Example payload:**

```json
{
    "name": "set-mission-rotation",
    "arguments": [
        "{\"rotationType\":\"Sequence\",\"clearNextOverride\":false,\"rotation\":[{\"Key\":{\"Group\":\"BuiltIn\",\"Name\":\"Escalation\"},\"MaxTime\":7200.0}]}"
    ]
}
```

The string in `arguments[0]` is deserialized from the following JSON structure:

```json
{
    "rotationType": "Sequence",
    "clearNextOverride": false,
    "rotation": [
        {
            "Key": {
                "Group": "BuiltIn",
                "Name": "Escalation"
            },
            "MaxTime": 7200.0
        }
    ]
}
```

### `clear-next-mission`

Clears the next overridden mission, reverting back to the standard rotation.

```json
{
    "name": "clear-next-mission",
    "arguments": []
}
```
