import datetime
from data_models.items import *


class Users(mongoengine.DynamicDocument):
    name = mongoengine.StringField(required=True)
    discord_id = mongoengine.LongField(required=True)
    date_created = mongoengine.DateTimeField(default=datetime.datetime.now)

    vbucks = mongoengine.IntField(default=1000)
    exp = mongoengine.IntField(default=1)
    level = mongoengine.IntField(default=1)
    slur_count = mongoengine.DictField()
    stroke_count = mongoengine.IntField(default=0)

    inventory = mongoengine.EmbeddedDocumentListField(Item)

    meta = {"db_alias": "default"}
