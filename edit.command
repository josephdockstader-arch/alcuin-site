#!/bin/bash
# Double-click to start the Alcuin site editor at http://localhost:8788
cd "$(dirname "$0")"
exec /usr/bin/python3 edit_server.py
