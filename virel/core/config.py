import os
from dotenv import load_dotenv

load_dotenv()

class Configuration:
    """
    Main configuration class for Virel, containing all configuration
    sections such as bot settings and core services.
    """

    class Bot:
        """
        Configuration for the bot itself, such as the command prefix.
        """

        prefix = os.environ.get("prefix", "!")
        token = os.environ.get("token")

    class Core:
        """
        Configuration for core services such as the database and cache.
        """
        
        postgres_url = os.environ.get("postgres_url")
        redis_url = os.environ.get("redis_url")