# file: config.py
import os

class Config:
    SECRET_KEY = "dev-secret-key-change-me"
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///blog.db")
    DEBUG = True
    SESSION_COOKIE_HTTPONLY = True
