from Models import SongItem
from Components import SearchBar
from API import YoutubeMusicApi


from flet import View, GridView, AppBar, Text, PopupMenuButton, PopupMenuItem, icons


class HomePage(View):
    def __init__(self):
        super().__init__()

        self.route = "/"

        self.appbar = AppBar(
            title=Text("Music Stream"),
        )

        controls = [SearchBar()]
        self.controls = controls
