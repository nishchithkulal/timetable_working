# app/__init__.py
# This file allows server.py to import from app
# The actual Flask app is initialized in server.py

from flask import Flask

def create_app(config=None):
    """Application factory - for future modular development"""
    app = Flask(__name__, 
                template_folder='templates', 
                static_folder='static')
    
    if config:
        app.config.update(config)
    
    return app

