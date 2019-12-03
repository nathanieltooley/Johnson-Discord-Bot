import mongoengine
import uuid

choices = ("Common", "Rare", "Epic")

class BaseItem(mongoengine.Document):
    item_id = mongoengine.StringField(required=True, unique=True)
    name = mongoengine.StringField(required=True)
    description = mongoengine.StringField()
    value = mongoengine.IntField(required=True)
    rarity = mongoengine.StringField(default="Common", choices=choices)

    meta: {
        "db_alias": "default",
        "collection": "Items"
    }

class Item(mongoengine.EmbeddedDocument):
    ref_id = mongoengine.UUIDField(required=True)
    last_owner = mongoengine.LongField()
    owner = mongoengine.LongField(required=True)

    
