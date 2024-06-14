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
        self.duration = eval(duration)

        self.audio_player = Audio(
            src=direct_link,
            autoplay=True,
            on_position_changed=lambda x: self.set_slider_value(x),
            on_state_changed=lambda x: self._on_state_change(x),
        )
        self.slider = Slider(
            max=self.duration, min=0, value=0, on_change=self.set_seek_position
        )
        self.audio_button = IconButton(
            icon=icons.PAUSE_CIRCLE, on_click=self.set_player_state, icon_size=82
        )

        controls = [self.audio_player, self.slider, self.audio_button]
        self.controls = controls

    def set_seek_position(self, value: ControlEvent):
        print(value.control.value)

    def set_player_state(self, e: ControlEvent):
        if self.player_state_ == "playing":
            self.player_state_ = "paused"
            self.audio_player.pause()

        elif self.player_state_ == "paused":
            self.player_state_ = "playing"
            self.audio_player.resume()

    def _on_state_change(self, e: ControlEvent):
        if e.data == "playing":
            self.player_state_ = "playing"
            self.audio_button.icon = icons.PAUSE_CIRCLE
            self.page.update()
        elif e.data == "paused":
            self.player_state_ = "paused"
            self.audio_button.icon = icons.PLAY_CIRCLE
            self.page.update()

    def set_slider_value(self, value: ControlEvent):
        # self.slider.value = int(value.data)
        # self.page.update()
        print(value.data)
