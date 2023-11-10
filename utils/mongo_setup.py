import mongoengine
import os
import pymongo

from utils import jlogging, level

host = os.environ.get("DISCORD_HOST")

logger = jlogging.get_logger(__name__, level.get_bot_level())


def global_init():
    try:
        mongoengine.register_connection(alias="default", name="Johnson", host=host)
        logger.info("Connected!")
    except pymongo.errors.ConfigurationError or pymongo.errors.ConnectionFailure:
        logger.warning("Could not connect; Retrying...")
        global_init()
