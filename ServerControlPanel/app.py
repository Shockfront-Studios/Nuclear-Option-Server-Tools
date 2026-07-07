"""
Main Flask application for the Nuclear Option Server Manager.
"""

from functools import wraps
import json
import urllib.error
import urllib.parse
import urllib.request
from flask import Flask, jsonify, request, Response, render_template

import config
import server_commands
import remote_commander

app = Flask(__name__)


def check_auth(username, password):
    """Check if a username password combination is valid."""
    return username == config.USERNAME and password == config.PASSWORD


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route('/')
@requires_auth
def index():
    return render_template('index.html', allowed_ports=config.SERVER_PORTS)


def create_remote_commander(port=None):
    """Creates and returns a RemoteCommander instance."""
    if port is None:
        port = config.SERVER_PORTS[0]
    return server_commands.RemoteCommander("127.0.0.1", port)


def validate_port(port):
    """Validates that the port is in the allowed list."""
    if port is None:
        return True  # None means use default port
    try:
        port_int = int(port)
        return port_int in config.SERVER_PORTS
    except (ValueError, TypeError):
        return False


def get_commander_from_data(data):
    """Extracts port from data, validates it, and returns commander and error tuple.

    Returns:
        tuple: (commander, error_response) where error_response is None if successful
    """
    port = data.get('server_port', None)
    if not validate_port(port):
        return None, jsonify({'success': False, 'error': f'Port {port} not allowed'}), 400

    commander = create_remote_commander(port)
    return commander, None


@app.route('/command/update-ready', methods=['POST'])
@requires_auth
def update_ready():
    data = request.get_json()
    commander, error = get_commander_from_data(data)
    if error:
        return error

    status_code, response = server_commands.update_ready(commander)
    return jsonify({'status_code': status_code, 'response': response})


@app.route('/command/send-chat-message', methods=['POST'])
@requires_auth
def send_chat_message():
    data = request.get_json()
    message = data.get('message')
    if not message:
        return jsonify({'success': False, 'error': 'Message not provided'}), 400

    commander, error = get_commander_from_data(data)
    if error:
        return error

    status_code, response = server_commands.send_chat_message(commander, message)
    return jsonify({'status_code': status_code, 'response': response})


@app.route('/command/reload-config', methods=['POST'])
@requires_auth
def reload_config():
    data = request.get_json()
    path = data.get('path')

    commander, error = get_commander_from_data(data)
    if error:
        return error

    status_code, response = server_commands.reload_config(commander, path)
    return jsonify({'status_code': status_code, 'response': response})


@app.route('/command/get-mission-time', methods=['POST'])
@requires_auth
def get_mission_time():
    data = request.get_json()

    commander, error = get_commander_from_data(data)
    if error:
        return error

    status_code, response = server_commands.get_mission_time(commander)
    return jsonify({'status_code': status_code, 'response': response})


@app.route('/command/get-mission', methods=['POST'])
@requires_auth
def get_mission():
    data = request.get_json()

    commander, error = get_commander_from_data(data)
    if error:
        return error

    status_code, response = server_commands.get_mission(commander)
    return jsonify({'status_code': status_code, 'response': response})


def resolve_steam_names(steam_ids):
    """Resolves a list of SteamID strings to their display names via the Steam Web API.
    
    Returns:
        tuple: (name_map, warning) where name_map maps steam_id to personaname.
    """
    # Check if API key is configured
    api_key = getattr(config, 'STEAM_API_KEY', None)
    if not api_key:
        return {}, "Steam API key is not configured. Player names cannot be resolved. Please set STEAM_API_KEY in config.py."

    # Clean up and get unique non-empty steam IDs
    steam_ids_clean = list(set([str(sid) for sid in steam_ids if sid]))
    if not steam_ids_clean:
        return {}, None

    url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
    params = {
        'key': api_key,
        'steamids': ','.join(steam_ids_clean)
    }
    
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"

    try:
        req = urllib.request.Request(
            full_url, 
            headers={'User-Agent': 'Nuclear-Option-Server-Panel/1.0'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                players = data.get('response', {}).get('players', [])
                name_map = {player['steamid']: player['personaname'] for player in players if 'steamid' in player and 'personaname' in player}
                return name_map, None
            else:
                return {}, f"Steam API returned status code {response.status}."
    except urllib.error.URLError as e:
        print(f"Error fetching Steam summaries: {e}")
        return {}, f"Network error contacting Steam API: {e.reason}"
    except Exception as e:
        print(f"Unexpected error resolving Steam names: {e}")
        return {}, f"Unexpected error resolving Steam names: {str(e)}"


@app.route('/command/get-player-list', methods=['POST'])
@requires_auth
def get_player_list():
    data = request.get_json()

    commander, error = get_commander_from_data(data)
    if error:
        return error

    status_code, response = server_commands.get_player_list(commander)
    
    # Resolve SteamIDs to names and handle the API response mapping
    if status_code == 'Success' and isinstance(response, dict):
        players = response.get("Players", [])
        steam_ids = [p.get("steamId") for p in players if p.get("steamId")]
        
        name_map, warning = resolve_steam_names(steam_ids)
        
        for player in players:
            sid = player.get("steamId")
            if sid:
                player["displayName"] = name_map.get(sid, sid)
            else:
                player["displayName"] = "Unknown"
        
        if warning:
            response["warning"] = warning

    return jsonify({'status_code': status_code, 'response': response})


@app.route('/command/get-server-id', methods=['POST'])
@requires_auth
def get_server_id():
    data = request.get_json()

    commander, error = get_commander_from_data(data)
    if error:
        return error

    status_code, response = server_commands.get_server_id(commander)
    return jsonify({'status_code': status_code, 'response': response})


@app.route('/command/get-mission-rotation', methods=['POST'])
@requires_auth
def get_mission_rotation():
    data = request.get_json()

    commander, error = get_commander_from_data(data)
    if error:
        return error

    status_code, response = server_commands.get_mission_rotation(commander)
    return jsonify({'status_code': status_code, 'response': response})


@app.route('/command/set-mission-rotation', methods=['POST'])
@requires_auth
def set_mission_rotation():
    data = request.get_json()
    rotation_data = data.get('rotation_data')
    if not rotation_data:
        return jsonify({'success': False, 'error': 'Rotation data not provided'}), 400

    commander, error = get_commander_from_data(data)
    if error:
        return error

    status_code, response = server_commands.set_mission_rotation(
        commander, rotation_data)
    return jsonify({'status_code': status_code, 'response': response})


@app.route('/command/clear-next-mission', methods=['POST'])
@requires_auth
def clear_next_mission():
    data = request.get_json()

    commander, error = get_commander_from_data(data)
    if error:
        return error

    status_code, response = server_commands.clear_next_mission(commander)
    return jsonify({'status_code': status_code, 'response': response})


@app.route('/command/set-time-remaining', methods=['POST'])
@requires_auth
def set_time_remaining():
    data = request.get_json()
    time = data.get('time')
    if time is None:
        return jsonify({'success': False, 'error': 'Time not provided.'}), 400
    try:
        time_float = float(time)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid time format.'}), 400

    commander, error = get_commander_from_data(data)
    if error:
        return error

    status_code, response = server_commands.set_time_remaining(
        commander, time_float)
    return jsonify({'status_code': status_code, 'response': response})


@app.route('/command/set-next-mission', methods=['POST'])
@requires_auth
def set_next_mission():
    data = request.get_json()
    group = data.get('group')
    name = data.get('name')
    max_time = data.get('max_time')
    if not all([group, name, max_time]):
        return jsonify({'success': False, 'error': 'Missing parameters.'}), 400
    try:
        max_time_float = float(max_time)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid time format.'}), 400

    commander, error = get_commander_from_data(data)
    if error:
        return error

    status_code, response = server_commands.set_next_mission(
        commander, group, name, max_time_float)
    return jsonify({'status_code': status_code, 'response': response})


@app.route('/command/kick-player', methods=['POST'])
@requires_auth
def kick_player():
    data = request.get_json()
    steam_id = data.get('steam_id')
    if not steam_id:
        return jsonify({'success': False, 'error': 'Steam ID not provided'}), 400

    commander, error = get_commander_from_data(data)
    if error:
        return error

    status_code, response = server_commands.kick_player(commander, steam_id)
    return jsonify({'status_code': status_code, 'response': response})


@app.route('/command/unkick-player', methods=['POST'])
@requires_auth
def unkick_player():
    data = request.get_json()
    steam_id = data.get('steam_id')
    if not steam_id:
        return jsonify({'success': False, 'error': 'Steam ID not provided'}), 400

    commander, error = get_commander_from_data(data)
    if error:
        return error

    status_code, response = server_commands.unkick_player(commander, steam_id)
    return jsonify({'status_code': status_code, 'response': response})


@app.route('/command/clear-kicked-players', methods=['POST'])
@requires_auth
def clear_kicked_players():
    data = request.get_json()

    commander, error = get_commander_from_data(data)
    if error:
        return error

    status_code, response = server_commands.clear_kicked_players(commander)
    return jsonify({'status_code': status_code, 'response': response})


@app.route('/command/banlist-reload', methods=['POST'])
@requires_auth
def banlist_reload():
    data = request.get_json()

    commander, error = get_commander_from_data(data)
    if error:
        return error

    status_code, response = server_commands.banlist_reload(commander)
    return jsonify({'status_code': status_code, 'response': response})


@app.route('/command/banlist-add', methods=['POST'])
@requires_auth
def banlist_add():
    data = request.get_json()
    steam_id = data.get('steam_id')
    reason = data.get('reason')
    if not steam_id:
        return jsonify({'success': False, 'error': 'Steam ID not provided'}), 400

    commander, error = get_commander_from_data(data)
    if error:
        return error

    status_code, response = server_commands.banlist_add(
        commander, steam_id, reason)
    return jsonify({'status_code': status_code, 'response': response})


@app.route('/command/banlist-remove', methods=['POST'])
@requires_auth
def banlist_remove():
    data = request.get_json()
    steam_id = data.get('steam_id')
    if not steam_id:
        return jsonify({'success': False, 'error': 'Steam ID not provided'}), 400

    commander, error = get_commander_from_data(data)
    if error:
        return error

    status_code, response = server_commands.banlist_remove(
        commander, steam_id)
    return jsonify({'status_code': status_code, 'response': response})


@app.route('/command/banlist-clear', methods=['POST'])
@requires_auth
def banlist_clear():
    data = request.get_json()

    commander, error = get_commander_from_data(data)
    if error:
        return error

    status_code, response = server_commands.banlist_clear(commander)
    return jsonify({'status_code': status_code, 'response': response})


if __name__ == '__main__':
    ssl_context = None
    if config.SSL_CERT_PATH and config.SSL_KEY_PATH:
        ssl_context = (config.SSL_CERT_PATH, config.SSL_KEY_PATH)

    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT,
            ssl_context=ssl_context)
