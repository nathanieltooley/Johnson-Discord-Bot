import mongoengine
import datetime


class Song(mongoengine.EmbeddedDocument):
    name = mongoengine.StringField()
    artists = mongoengine.ListField()
    added_at = mongoengine.DateTimeField()

    album = mongoengine.StringField()
    album_url = mongoengine.StringField()


class SpotifyCheck(mongoengine.DynamicDocument):
    count = mongoengine.IntField()
    last_updated = mongoengine.DateTimeField(default=datetime.datetime.now(datetime.timezone.utc))

    songs = mongoengine.EmbeddedDocumentListField(Song)


