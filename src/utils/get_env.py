import os

from dotenv import load_dotenv


def get_env(key, default=None):
    """
    Get an environment variable, return None if it doesn't exist.
    The optional second argument can specify an alternate default.
    key, default and the result are str.
    """
    # Load the variables from .env file
    load_dotenv()
    return os.getenv(key, default)
