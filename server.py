#!/usr/bin/env python3
"""
Simple HTTP server that serves static files from the current directory.
Open http://localhost:8000 in your browser.
"""

import http.server
import socketserver
import os

PORT = 8000
DIRECTORY = "."


class Handler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve files from specified directory."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)


def main():
    """Start the web server."""
    print(f"Serving '{DIRECTORY}' at http://localhost:{PORT}")
    print("Press CTRL+C to stop.")

    # Change to the directory we want to serve
    os.chdir(DIRECTORY)

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()