import json
import socket
import struct


class RemoteCommander:
    """
    A class to send commands to the game server via TCP.
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def send_command(self, command_name, arguments=[]):
        """
        Sends a single command to the server.
        """
        return self.send_commands([{"Name": command_name, "Arguments": arguments}])

    def send_commands(self, commands):
        """
        Sends a list of commands to the server.
        'commands' should be a list of dictionaries, e.g.:
        [{"Name": "command1", "Arguments": ["arg1"]}, {"Name": "command2", "Arguments": []}]
        """
        payload = {
            "Commands": commands
        }

        try:
            json_data = json.dumps(payload).encode('utf-8')
            message = struct.pack('<i', len(json_data)) + json_data

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                s.sendall(message)
            print(
                f"Successfully sent command(s): {[cmd['Name'] for cmd in commands]}")
            return True
        except (socket.error, OverflowError) as e:
            print(f"Error sending TCP command: {e}")
            return False
