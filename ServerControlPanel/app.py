"""
Main Flask application for the Nuclear Option Server Manager.
"""

from functools import wraps
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

    success, response = server_commands.update_ready(commander)
    return jsonify({'success': success, 'response': response})


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

    success, response = server_commands.send_chat_message(commander, message)
    return jsonify({'success': success, 'response': response})


@app.route('/command/reload-config', methods=['POST'])
@requires_auth
def reload_config():
    data = request.get_json()
    path = data.get('path')

    commander, error = get_commander_from_data(data)
    if error:
        return error

    success, response = server_commands.reload_config(commander, path)
    return jsonify({'success': success, 'response': response})


@app.route('/command/get-mission-time', methods=['POST'])
@requires_auth
def get_mission_time():
    data = request.get_json()

    commander, error = get_commander_from_data(data)
    if error:
        return error

    success, response = server_commands.get_mission_time(commander)
    return jsonify({'success': success, 'response': response})


@app.route('/command/get-mission', methods=['POST'])
@requires_auth
def get_mission():
    data = request.get_json()

    commander, error = get_commander_from_data(data)
    if error:
        return error

    success, response = server_commands.get_mission(commander)
    return jsonify({'success': success, 'response': response})


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

    success, response = server_commands.set_time_remaining(
        commander, time_float)
    return jsonify({'success': success, 'response': response})


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

    success, response = server_commands.set_next_mission(
        commander, group, name, max_time_float)
    return jsonify({'success': success, 'response': response})


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

    success, response = server_commands.kick_player(commander, steam_id)
    return jsonify({'success': success, 'response': response})


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

    success, response = server_commands.unkick_player(commander, steam_id)
    return jsonify({'success': success, 'response': response})


@app.route('/command/clear-kicked-players', methods=['POST'])
@requires_auth
def clear_kicked_players():
    data = request.get_json()

    commander, error = get_commander_from_data(data)
    if error:
        return error

    success, response = server_commands.clear_kicked_players(commander)
    return jsonify({'success': success, 'response': response})


@app.route('/command/banlist-reload', methods=['POST'])
@requires_auth
def banlist_reload():
    data = request.get_json()

    commander, error = get_commander_from_data(data)
    if error:
        return error

    success, response = server_commands.banlist_reload(commander)
    return jsonify({'success': success, 'response': response})


@app.route('/command/banlist-add', methods=['POST'])
@requires_auth
def banlist_add():
    data = request.get_json()
    steam_id = data.get('steam_id')
    if not steam_id:
        return jsonify({'success': False, 'error': 'Steam ID not provided'}), 400

    commander, error = get_commander_from_data(data)
    if error:
        return error

    success, response = server_commands.banlist_add(
        commander, steam_id)
    return jsonify({'success': success, 'response': response})


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

    success, response = server_commands.banlist_remove(
        commander, steam_id)
    return jsonify({'success': success, 'response': response})


@app.route('/command/banlist-clear', methods=['POST'])
@requires_auth
def banlist_clear():
    data = request.get_json()

    commander, error = get_commander_from_data(data)
    if error:
        return error

    success, response = server_commands.banlist_clear(commander)
    return jsonify({'success': success, 'response': response})


if __name__ == '__main__':
    ssl_context = None
    if config.SSL_CERT_PATH and config.SSL_KEY_PATH:
        ssl_context = (config.SSL_CERT_PATH, config.SSL_KEY_PATH)

    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT,
            ssl_context=ssl_context)
