import os
from dotenv import load_dotenv

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '336c8e1b3598c552b1b672b42e1271d04357c3a09d550eb83c609b512acc875b'
    DB_SERVER = os.environ.get('DB_SERVER') or 'localhost'
    DB_USER = os.environ.get('DB_USER') or 'diana'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'zzzz'
    DB_NAME = os.environ.get('DB_NAME') or 'stream_db'
