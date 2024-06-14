from Components import MusicPlayer
from flet import View, AppBar, Text
from urllib.parse import parse_qs


class PlayerPage(View):
    def __init__(self, data: str):
        super().__init__()

        self.appbar = AppBar(
            title=Text("Your Now Playing"),
        )

        parsed_data = parse_qs(data)

        normalized_data = {key_: value[0] for key_, value in parsed_data.items()}

        music_player = MusicPlayer(**normalized_data)

        self.controls.append(music_player)
