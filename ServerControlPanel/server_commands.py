"""
This module provides functions to interact with the game server's remote commands.
"""

import json
from typing import Optional

from remote_commander import RemoteCommander


def update_ready(commander: RemoteCommander):
    """Notifies the server that a component is ready."""
    return commander.send_command("update-ready")


def send_chat_message(commander: RemoteCommander, message: str):
    """Sends a server message to be displayed in the in-game chat."""
    return commander.send_command("send-chat-message", [message])


def reload_config(commander: RemoteCommander, path: Optional[str] = None):
    """Instructs the dedicated server to reload its configuration."""
    args = [path] if path else []
    return commander.send_command("reload-config", args)


def get_mission_time(commander: RemoteCommander):
    """Retrieves the current and maximum mission time."""
    return commander.send_command("get-mission-time")


def get_mission(commander: RemoteCommander):
    """Retrieves the currently running mission and the next mission scheduled."""
    return commander.send_command("get-mission")


def set_time_remaining(commander: RemoteCommander, time_in_seconds: float):
    """Sets the remaining time for the current mission, in seconds."""
    return commander.send_command("set-time-remaining", [str(time_in_seconds)])


def set_next_mission(commander: RemoteCommander, group: str, name: str, max_time: float):
    """Sets the mission to be loaded next after the current one concludes."""
    return commander.send_command("set-next-mission", [group, name, str(max_time)])


def kick_player(commander: RemoteCommander, steam_id: str):
    """Kicks a player from the server and optionally adds them to the ban list."""
    return commander.send_command("kick-player", [steam_id])


def unkick_player(commander: RemoteCommander, steam_id: str):
    """Kicks a player from the server and optionally adds them to the ban list."""
    return commander.send_command("unkick-player", [steam_id])


def clear_kicked_players(commander: RemoteCommander):
    """Clears the list of kicked players allowing them to rejoin."""
    return commander.send_command("clear-kicked-players")


def banlist_reload(commander: RemoteCommander):
    """Reloads the ban list from the list of files in server config."""
    return commander.send_command("banlist-reload")


def banlist_add(commander: RemoteCommander, steam_id: str, reason: Optional[str] = None):
    """Adds a SteamID to the in-memory ban list and optionally appends it to the first configured ban file."""
    args = [steam_id]
    if reason:
        args.append(reason)
    return commander.send_command("banlist-add", args)


def banlist_remove(commander: RemoteCommander, steam_id: str):
    """Removes a SteamID from the in-memory ban list and optionally removes it from the first configured ban file."""
    return commander.send_command("banlist-remove", [steam_id])


def banlist_clear(commander: RemoteCommander):
    """Clears the ban list loaded in the Authenticator."""
    return commander.send_command("banlist-clear")


def get_player_list(commander: RemoteCommander):
    """Retrieves the current connected player list from the server."""
    return commander.send_command("get-player-list")


def find_steam_id_by_player_index(players: list, player_index: int):
    """Looks up the SteamID of the player with the given in-game Player Index (playerIndex).

    Args:
        players: the "Players" list from a fresh get-player-list response.

    Returns:
        tuple: (steam_id, error) where error is None if a player was found.
    """
    for player in players:
        # older game servers don't send playerIndex, so default to 0 (not assigned)
        if player.get("playerIndex", 0) == player_index:
            return player.get("steamId"), None

    # if nobody has an index, the user's input isn't the problem, the server is too old to send it
    if players and all("playerIndex" not in player for player in players):
        return None, "Game server did not send playerIndex, it may be an older version. Use Steam ID instead"

    return None, f"No player found with Player Index {player_index}"


def get_server_id(commander: RemoteCommander):
    """Retrieves the Steam ID of the server."""
    return commander.send_command("get-server-id")


def get_mission_rotation(commander: RemoteCommander):
    """Retrieves the current mission rotation configuration."""
    return commander.send_command("get-mission-rotation")


def set_mission_rotation(commander: RemoteCommander, rotation_data: dict):
    """Sets the mission rotation configuration."""
    rotation_json = json.dumps(rotation_data)
    return commander.send_command("set-mission-rotation", [rotation_json])


def clear_next_mission(commander: RemoteCommander):
    """Clears the next overridden mission."""
    return commander.send_command("clear-next-mission")