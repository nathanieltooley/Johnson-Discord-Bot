import mongoengine
import datetime


class SongPoll(mongoengine.DynamicDocument):
    created_at = mongoengine.DateTimeField(default=datetime.datetime.now(datetime.timezone.utc))
    creator = mongoengine.LongField(required=True)

    song_url = mongoengine.StringField(required=True)
    poll_id = mongoengine.LongField()

    required_votes = mongoengine.IntField(required=True)
    current_votes = mongoengine.IntField(default=1)
