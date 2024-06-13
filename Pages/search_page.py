from Models import SongItem
from API import YoutubeMusicApi
from urllib.parse import parse_qs
from flet import View, ScrollMode, AppBar, Text


class SearchPage(View):
    def __init__(self, data: str):
        super().__init__()

        self.appbar = AppBar(
            title=Text("Search Results"),
        )

        self.scroll = ScrollMode.ALWAYS

        yt_api = YoutubeMusicApi()
        parsed_data = parse_qs(data)

        normalized_data = {key_: value[0] for key_, value in parsed_data.items()}

        search_results = yt_api.search(**normalized_data)

        if search_results.get("success"):
            song_items = [SongItem(**item) for item in search_results.get("results")]
            self.controls = song_items
