import mongoengine
import datetime

class Servers(mongoengine.DynamicDocument):
    name = mongoengine.StringField(required=True)
    discord_id = mongoengine.LongField(required=True)
    date_created = mongoengine.DateTimeField(default=datetime.datetime.now)

    meta = {
        "db_alias": "default",
        "collection": "Servers"
    }