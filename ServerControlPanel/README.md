# Nuclear Option Server Control Panel

A simple Flask-based web interface for managing a Nuclear Option dedicated server via its remote command interface.

This tool provides a basic web front-end to run server commands, making it easier for server administrators to manage their game servers without direct command-line access.

### Command list

See [Command list](../ServerCommands/Readme.md) for a full list of commands, required arguments and responses

## Features

- Web-based UI for all major server commands.
- Basic Authentication for security.
- Easy to configure and deploy.
- Can be run standalone or behind a reverse proxy like Nginx.

## Setup and Installation

Shell scripts are provided for easy setup on a Linux environment.

1.  **Navigate to the directory**:
    ```bash
    cd ServerControlPanel
    ```

2.  **Run the installation script**:
    This will create a Python virtual environment (`venv`) and install the required dependencies.
    ```bash
    ./install.sh
    ```

## Configuration

All configuration is handled in the `config.py` file. Before running the application, you **must** review and edit this file.

Key settings to change:

-   **`USERNAME` and `PASSWORD`**: This is for the web panel's Basic Authentication. **It is critical that you change the default password** to secure your server.
-   **`SERVER_PORTS`**: A list of remote command ports for your Nuclear Option game servers. *Note: the game server only listens on 127.0.0.1 (localhost), but you can run multiple on the same machine.*
-   **`FLASK_HOST`**: The IP address that the Flask web panel binds to. Set this to `127.0.0.1` to only accept connections from localhost (recommended if using a reverse proxy like Nginx on the same machine), or `0.0.0.0` to listen on all interfaces and allow direct external connections.
-   **`FLASK_PORT`**: The port that the web panel will run on.
-   **`SSL_CERT_PATH` and `SSL_KEY_PATH`**: Optional paths to your SSL certificate and private key files. If both paths are provided, the server will run with HTTPS. If they are left empty, the server will run with standard HTTP (suitable for running behind a reverse proxy).

### Deployment with a Reverse Proxy (Nginx)

For production use, it is highly recommended to run this application behind a reverse proxy like Nginx. The proxy can handle HTTPS/SSL termination, which is more secure and efficient.

When running behind a proxy:

1.  Ensure `SSL_CERT_PATH` and `SSL_KEY_PATH` in `config.py` are left empty, so Flask runs in HTTP mode.
2.  Configure your proxy to forward requests to the Flask application's host and port.

Example nginx config:
```conf
location /ServerControlPanel {
    # Set the address and port of the upstream Flask server
    proxy_pass http://localhost:5000;

    # Rewrite the URI to remove /ServerControlPanel for the upstream server.
    # The Flask server will receive a request for /, not /ServerControlPanel.
    # If the Flask application expects the full path, remove this line.
    rewrite ^/ServerControlPanel(.*)$ $1 break;

    # Standard headers to forward to the backend
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

This setup ensures that communication from the public internet to your proxy is encrypted, and the Flask application handles the application logic internally.

## Running the Application

Once configured, you can start the web panel using the provided run script:

```bash
./run.sh
```

This will activate the virtual environment and start the Flask application. You can then access the web panel in your browser at the host and port you configured.

### Running using systemctl

The app can also be run with systemctl using the `nuclear_option_server_control_panel.service` config.
- make sure paths inside the file are correct
- copy service file to `/etc/systemd/system/`
- reload and run
```
sudo systemctl daemon-reload
sudo systemctl enable --now nuclear_option_server_control_panel.service
```
