#!/usr/bin/env python3
import os
import sys

# Debug aus
os.environ['FLASK_DEBUG'] = '0'
os.environ['FLASK_ENV'] = 'production'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == '__main__':
    print("🚀 Starting West Money OS Production Server...")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=True
    )
