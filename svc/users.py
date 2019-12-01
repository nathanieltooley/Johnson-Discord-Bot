import mongoengine
import datetime

class Users(mongoengine.Document):
    server_name = mongoengine.StringField(required=True)
    server_id = mongoengine.LongField(required=True)

    name = mongoengine.StringField(required=True)
    discord_id = mongoengine.LongField(required=True)
    date_created = mongoengine.DateTimeField(default=datetime.datetime.now)

    vbucks = mongoengine.IntField(default=1000)
    exp = mongoengine.IntField(default=1)
    level = mongoengine.IntField(default=1)
    
    meta = {
        "db_alias": "core",
        "collection": "Users"
    }