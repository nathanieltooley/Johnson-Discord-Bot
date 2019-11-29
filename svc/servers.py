import mongoengine
import datetime

class Servers(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    discord_id = mongoengine.LongField(required=True)
    user_ids = mongoengine.ListField(default=[])
    date_created = mongoengine.DateTimeField(default=datetime.datetime.now)

    meta = {
        "db_alias": "core",
        "collection": "Servers"
    }