import mongoengine
import os

host = os.environ.get('HOST')

def global_init():
    mongoengine.register_connection(alias="core", name="Johnson", host=host)