import json
import socket
import struct
from enum import IntEnum, auto
from typing import List, Dict, Optional, Tuple


class StatusCode(IntEnum):
    """
    Status codes used for the custom TCP protocol response header.
    Matches the server's enum for explicit error handling.
    """
    Success = 2000

    BadRequest = 4000
    BadHeader = 4001
    BadLength = 4002
    JsonError = 4003
    UnknownCommand = 4004
    BadArguments = 4005

    InternalServerError = 5000
    CommandError = 5001


class RemoteCommander:
    """
    A class to send commands to the game server via TCP,
    with built-in protocol handling for the response header (status/length).
    """

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def send_command(self, command_name: str, arguments: List[str] = []) -> Tuple[str, Optional[Dict]]:
        """
        Sends a command to the server and waits for the response.
        {"name": "command", "arguments": ["arg1"]}

        Returns (status_code_name, response_body_dict_or_None).
        status_code_name is the name of the StatusCode enum (e.g., "Success", "BadRequest").
        For network/parsing errors, returns descriptive error names like "NetworkError".
        """
        try:
            payload = {"name": command_name, "arguments": arguments}
            json_data = json.dumps(payload).encode('utf-8')
            message = struct.pack('<i', len(json_data)) + json_data

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                s.sendall(message)

                print(f"Successfully sent command: {command_name}")
                return self._receive_response(s)

        except (socket.error, OverflowError) as e:
            print(f"Network or connection error: {e}")
            return "NetworkError", None

    def _receive_response(self, sock: socket.socket) -> Tuple[str, Optional[Dict]]:
        """
        Handles receiving the response from the server.
        Format: 4 bytes status code | 4 bytes body length | JSON body (variable)
        
        Returns (status_code_name, response_body_dict_or_None).
        status_code_name is the name of the StatusCode enum or an error name for parsing failures.
        """
        try:
            # Protocol uses little-endian ('<') 4-byte integers ('i')
            header = self._recv_n(sock, 8)
            status_int, body_length = struct.unpack('<ii', header)

        except ConnectionResetError as e:
            print(f"Error: Connection reset during header read. {e}")
            return "ConnectionError", None
        except struct.error:
            print("Error: Failed to unpack response header (corrupt data).")
            return "ParseError", None

        try:
            status_code = StatusCode(status_int)
        except ValueError:
            print(f"Error: Server returned unknown status code: {status_int}")
            return f"UnknownStatus_{status_int}", None

        data = None
        if body_length > 0:
            try:
                json_body = self._recv_n(sock, body_length)
                body_str = json_body.decode('utf-8', errors='ignore')
                try:
                    data = json.loads(body_str)
                except json.JSONDecodeError:
                    print(
                        "Error: Successfully received response, but failed to parse JSON body.")
                    return f"{status_code.name}_JsonParseError", data

            except ConnectionResetError as e:
                print(f"Error: Connection reset during body read. {e}")
                return f"{status_code.name}_ConnectionError", None
            except OverflowError:
                print(
                    f"Error: Received body length ({body_length}) is too large.")
                return f"{status_code.name}_OverflowError", None

        # Return the status code name and the data (which may be None for errors)
        print(
            f"Server returned status code {status_code.value} ({status_code.name}).")
        if data is not None and status_code != StatusCode.Success:
            print(f"Error body: {data}")
        return status_code.name, data

    def _recv_n(self, sock: socket.socket, n: int) -> bytes:
        """
        Helper to ensure exactly N bytes are received, handling partial reads.
        Raises ConnectionResetError if the connection closes prematurely.
        """
        data = b''
        while len(data) < n:
            chunk = sock.recv(n - len(data))
            if not chunk:
                raise ConnectionResetError(
                    "Connection closed unexpectedly before full message was received.")
            data += chunk
        return data
