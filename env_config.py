# env_config.py
import os
from dotenv import load_dotenv

load_dotenv()

def get_env_variable(key, default=None):
    return os.getenv(key, default)
