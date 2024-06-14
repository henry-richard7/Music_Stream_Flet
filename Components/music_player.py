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
    icons,
    CrossAxisAlignment,
    MainAxisAlignment,
)
import httpx
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
        self.alignment = MainAxisAlignment.CENTER
        self.horizontal_alignment = CrossAxisAlignment.CENTER

        yt_api = YoutubeMusicApi()
        parsed_lyrics = yt_api.fetch_lyrics(video_id)

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

        controls = [
            Text(
                album_name,
                style="Bold",
                size=20,
            ),
            Image(src=self.art, width=300, height=300),
            Text(
                song_name,
                style="Bold",
                size=20,
            ),
            Text(
                artist_name,
                # style="Bold",
                size=15,
            ),
            self.audio_player,
            self.slider,
            Row(
                controls=[
                    self.audio_button,
                    ElevatedButton(
                        "Download",
                        on_click=self.download_song,
                        data={
                            "url": direct_link,
                            "song_name": song_name,
                            "artist_name": artist_name,
                            "album_name": album_name,
                            "art": art,
                            "extension": eval(
                                music_result["results"]["mimeType"]
                                .split(";")[-1]
                                .split("codecs=")[-1]
                            ),
                            "page": self.page,
                        },
                        icon=icons.DOWNLOAD_SHARP,
                    ),
                ],
                alignment=MainAxisAlignment.CENTER,
            ),
        ]
        self.controls = controls

        if parsed_lyrics["success"]:
            lyrics = parsed_lyrics["results"]
            self.controls.append(
                Column(
                    controls=[
                        Card(
                            width=600,
                            content=Text(
                                lyrics,
                                text_align="center",
                                no_wrap=True,
                            ),
                        )
                    ],
                    horizontal_alignment="center",
                    scroll=ScrollMode.AUTO,
                    height=400,
                )
            )
        else:
            lyrics = "Lyrics Not Available!"

    def download_song(self, e: ControlEvent):
        data_ = e.control.data

        progress_bar = ProgressBar(width=500, height=10)
        percentage_text = Text()

        alert_dialog = AlertDialog(
            modal=True,
            title=Text("Currently Downloading"),
            content=Column(
                controls=[
                    Row(
                        controls=[
                            Text("Song: "),
                            Text(data_["song_name"]),
                        ]
                    ),
                    Row(
                        controls=[
                            Text("Artist: "),
                            Text(data_["artist_name"]),
                        ]
                    ),
                    Row(
                        controls=[
                            Text("Album: "),
                            Text(data_["album_name"]),
                        ]
                    ),
                    Row(
                        controls=[
                            Text("Progress: "),
                            percentage_text,
                        ]
                    ),
                    progress_bar,
                ],
                height=200,
            ),
        )

        self.page.dialog = alert_dialog
        alert_dialog.open = True
        self.page.update()

        dl = 0
        with httpx.stream("GET", data_["url"]) as response:
            total_length = int(response.headers.get("content-length", 0))

            with open(
                f'Downloads/{data_["song_name"] + "." + data_["extension"]}', "wb"
            ) as f:
                for chunk in response.iter_bytes():
                    dl += len(chunk)
                    f.write(chunk)
                    progress_bar.value = dl / total_length
                    percentage_text.value = (
                        str(round((dl / total_length) * 100, 2)) + "%"
                    )
                    self.page.update()

        alert_dialog.open = False
        self.page.update()

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
        self.slider.value = int(value.data)
        self.page.update()
