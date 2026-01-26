
# env_config.py
import environ
import os

env = environ.Env()
environ.Env.read_env(os.path.join(os.path.dirname(__file__), ".env"))