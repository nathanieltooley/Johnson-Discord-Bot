import mongoengine
import os

host = os.environ.get('HOST')

def global_init():
    mongoengine.register_connection(alias="default", name="Johnson", host=host)