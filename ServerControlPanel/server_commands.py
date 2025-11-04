"""
This module provides functions to interact with the game server's remote commands.
"""

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


def banlist_add(commander: RemoteCommander, steam_id: str):
    """Adds a SteamID to the in-memory ban list and optionally appends it to the first configured ban file."""
    return commander.send_command("banlist-add", [steam_id])


def banlist_remove(commander: RemoteCommander, steam_id: str):
    """Removes a SteamID from the in-memory ban list and optionally removes it from the first configured ban file."""
    return commander.send_command("banlist-remove", [steam_id])


def banlist_clear(commander: RemoteCommander):
    """Clears the ban list loaded in the Authenticator."""
    return commander.send_command("banlist-clear")


def get_player_list(commander: RemoteCommander):
    """Retrieves the current connected player list from the server."""
    return commander.send_command("get-player-list")