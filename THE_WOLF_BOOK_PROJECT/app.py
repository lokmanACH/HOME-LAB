from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from screens import (
    AddCategoryModal,
    CategoriesScreen,
    HelpModal,
    SearchScreen,
)


class HomeScreen(Screen[None]):
    """Home navigation screen."""

    DEFAULT_CSS = """
    HomeScreen {
        align: center middle;
    }
    #home-box {
        width: 44;
        height: auto;
        border: solid $primary;
        padding: 1 2;
        background: $surface;
    }
    #app-title {
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
        color: $accent;
    }
    #menu-list {
        height: auto;
    }
    """

    BINDINGS = [
        Binding("slash", "search", "Search"),
        Binding("question_mark", "show_help", "Help"),
        Binding("q", "quit_app", "Quit"),
    ]

    MENU_ITEMS = [
        "Categories",
        "Search",
        "Add Category",
        "Help",
        "Quit",
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="home-box"):
            yield Label("Troubleshooting", id="app-title")
            yield ListView(
                *[ListItem(Static(f"> {item}")) for item in self.MENU_ITEMS],
                id="menu-list"
            )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#menu-list", ListView).focus()

    @on(ListView.Selected, "#menu-list")
    def on_menu_selected(self, event: ListView.Selected) -> None:
        idx = event.list_view.index
        if idx == 0:  # Categories
            self.app.push_screen(CategoriesScreen())
        elif idx == 1:  # Search
            self.app.push_screen(SearchScreen())
        elif idx == 2:  # Add Category
            def on_added(res):
                if res:
                    self.app.push_screen(CategoriesScreen())
            self.app.push_screen(AddCategoryModal(), on_added)
        elif idx == 3:  # Help
            self.app.push_screen(HelpModal())
        elif idx == 4:  # Quit
            self.app.exit()

    def action_search(self) -> None:
        self.app.push_screen(SearchScreen())

    def action_show_help(self) -> None:
        self.app.push_screen(HelpModal())

    def action_quit_app(self) -> None:
        self.app.exit()


class TroubleshootingApp(App[None]):
    """Main Textual application."""

    TITLE = "Troubleshooting"
    CSS = """
    Screen {
        background: $background;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=False),
        Binding("question_mark", "help", "Help", show=False),
        Binding("slash", "search", "Search", show=False),
    ]

    def on_mount(self) -> None:
        self.push_screen(HomeScreen())

    def action_help(self) -> None:
        self.push_screen(HelpModal())

    def action_search(self) -> None:
        self.push_screen(SearchScreen())


if __name__ == "__main__":
    app = TroubleshootingApp()
    app.run()

