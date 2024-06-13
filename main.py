from flet import Page, app
from flet_core import TemplateRoute
from Pages import HomePage, SearchPage


def main(page: Page):
    page.title = "Music Stream"

    def route_change(route):
        router = TemplateRoute(page.route)

        if router.match("/"):
            page.views.clear()
            page.views.append(HomePage())
        elif router.match("/search*"):
            page.views.append(SearchPage(data=route.route))
        elif router.match("/play*"):
            page.views.append()

        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/")


app(main)
