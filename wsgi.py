#!/usr/bin/env python3
"""
WCL Time Splits Analyzer - WSGI Entry Point

This is the WSGI entry point for the WCL Time Splits Analyzer application.
It imports and exposes the Flask application from the src directory.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
