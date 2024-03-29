from enum import Enum


class Enums(Enum):
    BOT_AVATAR_URL = "https://media.discordapp.net/attachments/649780106885070868/852369616226353234/New_Johnson.png?width=486&height=468"
    ASTAR_AVATAR_URL = (
        "https://i1.sndcdn.com/avatars-INf0AAl2F1SEzJx8-Uya6IA-t200x200.jpg"
    )
    OWNER_ID = 139374003365216256
    TEST_SERVER_ID = 427299383474782208
    JOHNSON_ID = 600162735975694356
    JOHNSON_COMP_ID = 649740503729963008
    POLL_CREATORS = [139374003365216256, 249997264553115648, 527149614336311299]
    OUR_PLAYLIST_ID = "2PVeZw1omBqUhwj6htPZjZ"


class DiscordEnums(Enum):
    OPTION_TYPE_SUB_COMMAND = 1
    OPTION_TYPE_SUB_COMMAND_GROUP = 2
    OPTION_TYPE_STRING = 3
    OPTION_TYPE_INT = 4
    OPTION_TYPE_BOOL = 5
    OPTION_TYPE_USER = 6
    OPTION_TYPE_CHANNEL = 7
    OPTION_TYPE_ROLE = 8
    OPTION_TYPE_MENTIONABLE = 9
    OPTION_TYPE_NUMBER = 10


class ReturnTypes(Enum):
    RETURN_TYPE_YOUTUBE_URL = 1
    RETURN_TYPE_SPOTIFY_URL = 2
    RETURN_TYPE_INVALID_URL = 3
    RETURN_TYPE_SPOTPLAYLIST_URL = 4
    RETURN_TYPE_SOUNDCLOUD_URL = 5
    RETURN_TYPE_SPOTALBUM_URL = 6
    RETURN_TYPE_SUCCESSFUL_DISCONNECT = 7
    RETURN_TYPE_SUCCESSFUL_CONNECT = 8
