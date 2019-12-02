import mongoengine
import uuid

choices = ("Common", "Rare", "Epic")

class BaseItem(mongoengine.Document):
    _id = mongoengine.UUIDField(default=uuid.uuid4())
    name = mongoengine.StringField(required=True)
    description = mongoengine.StringField()
    value = mongoengine.IntField(required=True)
    rarity = mongoengine.StringField(default="Common", choices=choices)

    meta: {
        "allow_inheritance": True,
        "db_alias": "core",
        "collection": "Items"
    }

class Item(mongoengine.EmbeddedDocument):
    ref_id = mongoengine.UUIDField(required=True)
    last_owner = mongoengine.LongField()
    owner = mongoengine.LongField(required=True)

    
