import mongoengine
import datetime


class Servers(mongoengine.DynamicDocument):
    discord_id = mongoengine.LongField(required=True)
    currency_name = mongoengine.StringField(default="V-Bucks")

    meta = {
        "db_alias": "default",
        "collection": "Servers"
    }