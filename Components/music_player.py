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

from ffmpeg import FFmpeg
from io import BytesIO
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC, error, USLT


def convert_to_mp3(file_bytes: bytes) -> bytes:
    bytes_io = BytesIO(file_bytes)

    process = FFmpeg().input("pipe:0").output("pipe:1", f="mp3")
    raw_mp3 = process.execute(bytes_io)

    return raw_mp3


def add_meta_data(
    raw_mp3: bytes,
    song_name: str,
    artist_name: str,
    album_name: str,
    art: str,
    lyrics: str = None,
) -> BytesIO:
    muta_input = BytesIO(raw_mp3)

    audio = MP3(muta_input)

    audio["TIT2"] = TIT2(encoding=3, text=song_name)
    audio["TPE1"] = TPE1(encoding=3, text=artist_name)
    audio["TALB"] = TALB(encoding=3, text=album_name)
    cover_image_data = httpx.get(art).content

    if lyrics is not None:
        audio["USLT"] = USLT(
            encoding=3,
            lang="eng",
            text=lyrics,
        )

    audio["APIC"] = APIC(
        encoding=3,  # 3 is for utf-8
        mime="image/jpeg",  # image mime type
        type=3,  # 3 is for the cover image
        desc="Cover",
        data=cover_image_data,
    )

    audio.save(muta_input)

    return muta_input


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
        self.direct_link = direct_link
        duration = music_result["results"]["approxDurationMs"]
        self.extension = eval(
            music_result["results"]["mimeType"].split(";")[-1].split("codecs=")[-1]
        )

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
                            "extension": self.extension,
                            "page": self.page,
                        },
                        icon=icons.DOWNLOAD_SHARP,
                    ),
                ],
                alignment=MainAxisAlignment.CENTER,
            ),
        ]
        self.controls = controls

        self.lyrics_present = parsed_lyrics["success"]

        if parsed_lyrics["success"]:
            lyrics = parsed_lyrics["results"]
            self.lyrics = lyrics
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
                            Text(self.song_name),
                        ]
                    ),
                    Row(
                        controls=[
                            Text("Artist: "),
                            Text(self.artist_name),
                        ]
                    ),
                    Row(
                        controls=[
                            Text("Album: "),
                            Text(self.album_name),
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
        download_opus = []
        with httpx.stream("GET", self.direct_link) as response:
            total_length = int(response.headers.get("content-length", 0))
            for chunk in response.iter_bytes():
                dl += len(chunk)
                download_opus.append(chunk)
                progress_bar.value = dl / total_length
                percentage_text.value = str(round((dl / total_length) * 100, 2)) + "%"
                self.page.update()

        download_opus = b"".join(download_opus)
        try:
            raw_mp3 = convert_to_mp3(download_opus)
            meta_added_mp3 = add_meta_data(
                raw_mp3,
                song_name=self.song_name,
                art=self.art,
                artist_name=self.artist_name,
                album_name=self.album_name,
                lyrics=self.lyrics if self.lyrics_present else None,
            )
            with open(f"Downloads/{self.song_name}.mp3", "wb") as file:
                file.write(meta_added_mp3.getvalue())
        except Exception as e:
            print(e)
            print("FFMPEG not found please install if you want to convert to MP3")
            with open(f"Downloads/{self.song_name}.{self.extension}", "wb") as file:
                byte_io = BytesIO(download_opus)
                file.write(byte_io.getvalue())
        alert_dialog.open = False
        self.page.update()

    def set_seek_position(self, value: ControlEvent):
        self.audio_player.seek(int(value.control.value))

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
