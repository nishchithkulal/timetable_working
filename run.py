# Run this file instead of the old server.py
# python run.py

import os
import logging
from app import create_app
from app.models.database import db

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Load environment variables
def load_local_env(path):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_local_env(os.path.join(os.path.dirname(__file__), ".env"))

# Get database URL
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set in .env")

# Create app
config = {
    'SQLALCHEMY_DATABASE_URI': DATABASE_URL,
}

app = create_app(config)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='localhost', port=5000, debug=True)
