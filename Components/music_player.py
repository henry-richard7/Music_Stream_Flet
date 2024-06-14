from flet import (
    Text,
    Audio,
    Image,
    ElevatedButton,
    Row,
    ControlEvent,
    Slider,
    IconButton,
    Card,
    icons,
    ScrollMode,
    Column,
    ProgressBar,
    AlertDialog,
    alignment,
)

from API import YoutubeMusicApi


# TODO: Initi Audio Player
class MusicPlayer(Column):
    def __init__(
        self, video_id: str, song_name: str, artist_name: str, album_name: str, art: str
    ):
        super().__init__()
        self.video_id = video_id
        self.song_name = song_name
        self.artist_name = artist_name
        self.album_name = album_name
        self.art = art
        self.padding = 10

        yt_api = YoutubeMusicApi()
        parsed_lyrics = yt_api.fetch_lyrics(video_id)

        if parsed_lyrics["success"]:
            lyrics = parsed_lyrics["results"]
        else:
            lyrics = "Lyrics Not Available!"

        music_result = yt_api.get_direct_link(video_id)
        direct_link = music_result["results"]["url"]
        duration = music_result["results"]["approxDurationMs"]

        self.player_state_ = "playing"
        self.duration = duration
