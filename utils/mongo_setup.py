import mongoengine
import os
import pymongo

from utils import jlogging

host = os.environ.get('DISCORD_HOST')

def global_init():
    try:
        mongoengine.register_connection(alias="default", name="Johnson", host=host)
        jlogging.log(__name__, "Connected!")
    except pymongo.errors.ConfigurationError or pymongo.errors.ConnectionFailure:
        jlogging.warning("global_init", "Could not connect; Retrying...")
        global_init()
