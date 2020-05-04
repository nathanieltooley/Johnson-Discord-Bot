import mongoengine
import os
import pymongo
import svc.svc as svc

host = os.environ.get('HOST')


def global_init():
    try:
        mongoengine.register_connection(alias="default", name="Johnson", host=host)
        svc.Logging.log(__name__, "Connected!")
    except pymongo.errors.ConfigurationError or pymongo.errors.ConnectionFailure:
        svc.Logging.warning("global_init", "Could not connect; Retrying...")
        global_init()
