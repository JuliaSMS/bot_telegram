import os
from dotenv import load_dotenv


def load_env():
    # Look for .env in project root
    root = os.path.dirname(os.path.dirname(__file__))
    env_path = os.path.join(root, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        load_dotenv()  # fallback to environment


def get_env(name: str, default=None):
    return os.getenv(name, default)
