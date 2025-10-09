"""Configuration for the Flask application."""

# Game Server Configuration
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 7779

# Web Application Configuration
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000

# Security Configuration
USERNAME = "admin"
PASSWORD = "changeme"  # PLEASE CHANGE THIS!
SSL_CERT_PATH = ""  # Path to your SSL certificate file (e.g., /path/to/cert.pem)
SSL_KEY_PATH = ""   # Path to your SSL private key file (e.g., /path/to/key.pem)
