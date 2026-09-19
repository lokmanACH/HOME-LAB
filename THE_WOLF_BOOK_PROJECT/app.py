from textual import on
from textual.theme import Theme
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
    background: #100F0F;
}

#home-box {
    width: 44;
    height: auto;
    border: solid #205EA6;
    padding: 1 2;
    background: #1C1B1A;
}

#app-title {
    text-style: bold;
    text-align: center;
    margin-bottom: 1;
    color: #FFFCF0;
}

#creator-footer {
    width: 100%;
    text-align: center;
    text-style: dim italic;
    margin-bottom: 1;
    padding: 0 1;
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
            yield Label("The Wolf Book", id="app-title")
            yield Static("Created by Achouche Lokman Elhakim (Dev Wolf)", id="creator-footer")
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

    TITLE = "THE WOLF BOOK"
    CSS = """
    Screen {
        background: $background;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=False),
        Binding("question_mark", "help", "Help", show=False),
        Binding("slash", "search", "Search", show=False),
        Binding("left", "focus_previous", "Previous widget", show=False, priority=True),
        Binding("right", "focus_next", "Next widget", show=False, priority=True),
    ]

    THEMES = {
        "ansi-dark": Theme(
            name="ansi-dark",
            primary="#00AAFF",
            secondary="#00AAAA",
            accent="#FFFF55",
            foreground="#FFFFFF",
            background="#000000",
            surface="#1A1A1A",
            panel="#101010",
            success="#55FF55",
            warning="#FFFF55",
            error="#FF5555",
        )
    }
    def on_mount(self) -> None:
        self.theme = "ansi-dark"
        self.push_screen(HomeScreen())

    def action_help(self) -> None:
        self.push_screen(HelpModal())

    def action_search(self) -> None:
        self.push_screen(SearchScreen())


if __name__ == "__main__":
    app = TroubleshootingApp()
    app.run()

