# Example Config

Example files for a Nuclear Option dedicated server. See [DedicatedServerGuide.md](../DedicatedServerGuide.md) for what each setting does, and for the default config.

Copy these next to the server, then replace the example values:
- **SteamIDs** in the list files are placeholders (`00000000000000001` etc) that can never be real accounts, replace them with real ones. The server logs an error for each placeholder left in `staff_list.json`.
- **`Password`** in `DedicatedServerConfig.json`, or set it to `""` for no password.
- **`Workshop` mission `Name`** is the mission's Workshop ID (the number in its Steam Workshop URL), `1234567890` is a placeholder.
- **`User` mission `Name`** is the mission's name in your `MissionDirectory`.

| File | Used by | Format |
|---|---|---|
| `DedicatedServerConfig.json` | the server | Example config with a password, port overrides, a mission from each group, and all list files set |
| `ban_list.txt` | `BanListPaths` | One SteamID per line, optional `// reason` |
| `error_kick_immune_list.txt` | `ErrorKickImmuneListPaths` | Same as the ban list |
| `staff_list.json` | `StaffListPaths` | SteamID with a permission level and optional tag, see the guide |

`RotationType` is a number: `0` Sequence, `1` PureRandom, `2` RandomQueue.
