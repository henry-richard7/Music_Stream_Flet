from flet import (
    Text,
    Column,
    Row,
    ImageFit,
    Image,
)

from flet_core import ControlEvent


class SongItem(Row):
    def __init__(
        self, video_id: str, song_name: str, artist_name: str, album_name: str, art: str
    ):
        super().__init__()
        self.video_id = video_id
        self.song_name = song_name
        self.artist_name = artist_name
        self.album_name = album_name
        self.art = art

        self.on_click = self.click_handler
        self.padding = 10

        self.controls.append(
            Image(
                src=self.art,
                height=180,
                fit=ImageFit.COVER,
            )
        )
        self.controls.append(
            Column(
                controls=[
                    Text(
                        self.song_name,
                        style="TitleLarge",
                        font_family="Encore Font Circular Bold",
                    ),
                    Text(artist_name, font_family="Encore Font Circular Book"),
                    Text(album_name, font_family="Encore Font Circular Book"),
                ]
            )
        )

    def click_handler(self, e: ControlEvent):
        video_id = self.video_id
        song_name = self.song_name
        artist_name = self.artist_name
        album_name = self.album_name
        art = self.art
        url_build = f"/play&video_id={video_id}&song_name={song_name}&artist_name={artist_name}&album_name={album_name}&art={art}"
        self.page.go(url_build)
