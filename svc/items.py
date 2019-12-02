import mongoengine
import uuid

class BaseItem(mongoengine.Document):
    _id = mongoengine.UUIDField(default=uuid.uuid4())
    name = mongoengine.StringField(required=True)
    value = mongoengine.IntField(required=True)

    meta: {
        "allow_inheritance": True,
        "db_alias": "core"
    }

class Item(mongoengine.EmbeddedDocument):
    ref_id = mongoengine.UUIDField(required=True)
    last_owner = mongoengine.LongField()
    owner = mongoengine.LongField(required=True)

    
