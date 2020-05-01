import mongoengine
import os
import pymongo

host = os.environ.get('HOST')


def global_init():
    try:
        mongoengine.register_connection(alias="default", name="Johnson", host=host)
        print("Connected!")
    except pymongo.errors.ConfigurationError:
        print("Could not connect; Retrying...")
        global_init()
