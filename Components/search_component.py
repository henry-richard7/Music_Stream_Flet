from urllib.parse import quote_plus
from flet import ElevatedButton, TextField, Row


class SearchBar(Row):
    def __init__(
        self,
    ):
        super().__init__()
        self.search_field = TextField(label="Search", hint_text="Search...", expand=1)

        self.controls = [
            self.search_field,
            ElevatedButton("Search", on_click=self.on_click_event),
        ]

    def on_click_event(self, e):
        query = quote_plus(self.search_field.value)
        url_build = f"/search&query={query}"
        self.page.go(url_build)
