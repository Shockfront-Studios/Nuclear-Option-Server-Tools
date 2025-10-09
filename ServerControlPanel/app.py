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
    return render_template('index.html')


def create_remote_commander():
    """Creates and returns a RemoteCommander instance."""
    return server_commands.RemoteCommander(config.SERVER_HOST, config.SERVER_PORT)


@app.route('/command/update-ready', methods=['POST'])
@requires_auth
def update_ready():
    commander = create_remote_commander()
    success, response = server_commands.update_ready(commander)
    return jsonify({'success': success, 'response': response})


@app.route('/command/send-chat-message', methods=['POST'])
@requires_auth
def send_chat_message():
    data = request.get_json()
    message = data.get('message')
    if not message:
        return jsonify({'success': False, 'error': 'Message not provided'}), 400
    commander = create_remote_commander()
    success, response = server_commands.send_chat_message(commander, message)
    return jsonify({'success': success, 'response': response})


@app.route('/command/reload-config', methods=['POST'])
@requires_auth
def reload_config():
    data = request.get_json()
    path = data.get('path')
    commander = create_remote_commander()
    success, response = server_commands.reload_config(commander, path)
    return jsonify({'success': success, 'response': response})


@app.route('/command/get-mission-time', methods=['POST'])
@requires_auth
def get_mission_time():
    commander = create_remote_commander()
    success, response = server_commands.get_mission_time(commander)
    return jsonify({'success': success, 'response': response})


@app.route('/command/get-mission', methods=['POST'])
@requires_auth
def get_mission():
    commander = create_remote_commander()
    success, response = server_commands.get_mission(commander)
    return jsonify({'success': success, 'response': response})


@app.route('/command/set-time-remaining', methods=['POST'])
@requires_auth
def set_time_remaining():
    data = request.get_json()
    time = data.get('time')
    if time is None:
        return jsonify({'success': False, 'error': 'Time not provided'}), 400
    commander = create_remote_commander()
    success, response = server_commands.set_time_remaining(
        commander, float(time))
    return jsonify({'success': success, 'response': response})


@app.route('/command/set-next-mission', methods=['POST'])
@requires_auth
def set_next_mission():
    data = request.get_json()
    group = data.get('group')
    name = data.get('name')
    max_time = data.get('max_time')
    if not all([group, name, max_time]):
        return jsonify({'success': False, 'error': 'Missing arguments'}), 400
    commander = create_remote_commander()
    success, response = server_commands.set_next_mission(
        commander, group, name, float(max_time))
    return jsonify({'success': success, 'response': response})


@app.route('/command/kick-player', methods=['POST'])
@requires_auth
def kick_player():
    data = request.get_json()
    steam_id = data.get('steam_id')
    ban = data.get('ban', False)
    if not steam_id:
        return jsonify({'success': False, 'error': 'Steam ID not provided'}), 400
    commander = create_remote_commander()
    success, response = server_commands.kick_player(commander, steam_id, ban)
    return jsonify({'success': success, 'response': response})


@app.route('/command/clear-kicked-players', methods=['POST'])
@requires_auth
def clear_kicked_players():
    commander = create_remote_commander()
    success, response = server_commands.clear_kicked_players(commander)
    return jsonify({'success': success, 'response': response})


@app.route('/command/banlist-reload', methods=['POST'])
@requires_auth
def banlist_reload():
    commander = create_remote_commander()
    success, response = server_commands.banlist_reload(commander)
    return jsonify({'success': success, 'response': response})


@app.route('/command/banlist-add', methods=['POST'])
@requires_auth
def banlist_add():
    data = request.get_json()
    steam_id = data.get('steam_id')
    append = data.get('append', False)
    if not steam_id:
        return jsonify({'success': False, 'error': 'Steam ID not provided'}), 400
    commander = create_remote_commander()
    success, response = server_commands.banlist_add(
        commander, steam_id, append)
    return jsonify({'success': success, 'response': response})


@app.route('/command/banlist-remove', methods=['POST'])
@requires_auth
def banlist_remove():
    data = request.get_json()
    steam_id = data.get('steam_id')
    remove = data.get('remove', False)
    if not steam_id:
        return jsonify({'success': False, 'error': 'Steam ID not provided'}), 400
    commander = create_remote_commander()
    success, response = server_commands.banlist_remove(
        commander, steam_id, remove)
    return jsonify({'success': success, 'response': response})


@app.route('/command/banlist-clear', methods=['POST'])
@requires_auth
def banlist_clear():
    commander = create_remote_commander()
    success, response = server_commands.banlist_clear(commander)
    return jsonify({'success': success, 'response': response})


if __name__ == '__main__':
    # SSL REQUIRED IF RUNNING ON PUBLIC PORT
    # ssl_context = ('/path/to/your/certificate.crt',
    #                '/path/to/your/private.key')
    # app.run(host=config.FLASK_HOST, port=config.FLASK_PORT,
    #         ssl_context=ssl_context)

    # if running behind reverse proxy like Nginx, ssl is not required by flask
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT)
