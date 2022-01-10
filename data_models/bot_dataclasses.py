from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class QueuedSong:
    yt_url: str
    title: str
    creator: str
