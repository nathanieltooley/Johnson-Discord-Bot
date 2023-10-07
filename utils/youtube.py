from enums import bot_enums
from yt_dlp import YoutubeDL


def construct_url_from_suffix(suffix):
    return f"https://www.youtube.com{suffix}"


def construct_url_from_id(id):
    return f"https://www.youtube.com/watch?v={id}"


def get_video_info(url):
    with YoutubeDL({}) as ydl:
        info = ydl.extract_info(url, download=False)

        return info


def find_best_audio_link(formats, url_type):
    if url_type == bot_enums.ReturnTypes.RETURN_TYPE_SOUNDCLOUD_URL:
        for f in formats:
            if f["audio_ext"] == "opus":
                return f["url"]
    else:
        for f in formats:
            if f["acodec"] == "opus":
                return f["url"]
