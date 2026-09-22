"""
config.py
---------
All settings come from environment variables, with locally-friendly
defaults so `python app.py` works out of the box with no setup. On
Railway you MUST override SECRET_KEY, ADMIN_USERNAME and ADMIN_PASSWORD
(see README.md) — the defaults here are for local testing only.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Where the SQLite file lives locally. On Railway, set DATA_DIR to the
# mount path of an attached Volume (e.g. "/data") so records survive
# redeploys — see README.md "Deploying to Railway".
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(BASE_DIR, "data"))
os.makedirs(DATA_DIR, exist_ok=True)

# DATABASE_URL overrides everything above — set this instead if you'd
# rather use Railway's Postgres plugin than a SQLite file + Volume.
DATABASE_URL = os.environ.get("DATABASE_URL") or f"sqlite:///{os.path.join(DATA_DIR, 'mampondweni.db')}"
# SQLAlchemy 2.x wants "postgresql://", but Railway's Postgres plugin
# hands out "postgres://" — normalize it so DATABASE_URL works either way.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URI = DATABASE_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Signs session cookies. MUST be set on Railway to a long random value,
# or everyone gets logged out every time the app restarts/redeploys.
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key-change-me")

# The one admin account. MUST be overridden on Railway — see README.md.
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "changeme")

USING_DEFAULT_CREDENTIALS = (
    ADMIN_USERNAME == "admin" and ADMIN_PASSWORD == "changeme"
)
USING_DEFAULT_SECRET_KEY = SECRET_KEY == "dev-only-insecure-key-change-me"
