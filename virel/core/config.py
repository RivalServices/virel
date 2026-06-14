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
        owner_ids = [int(x) for x in os.environ.get("owner_ids", "").split(",") if x]
        client_id = os.environ.get("client_id")

    class Core:
        """
        Configuration for core services such as the database and cache.
        """
        
        postgres_url = os.environ.get("postgres_url")
        redis_url = os.environ.get("redis_url")
    
    class Colors:
        """
        Contains the default color values for embed messages used by the bot
        for approved, denied, informational, and warning messages.
        """

        approved = int(os.environ.get("color_approved", "729BB0"), 16)
        denied = int(os.environ.get("color_denied", "FF3939"), 16)
        info = int(os.environ.get("color_info", "729BB0"), 16)
        warning = int(os.environ.get("color_warning", "FFD600"), 16)
        neutral = int(os.environ.get("color_neutral", "729BB0"), 16)

    class Emojis:
        """
        Contains the default emoji values for embed messages used by the bot
        for approved, denied, informational, and warning messages.
        """
        
        approved = os.environ.get("emoji_approved")
        denied = os.environ.get("emoji_denied")
        info = os.environ.get("emoji_info")
        warning = os.environ.get("emoji_warning")