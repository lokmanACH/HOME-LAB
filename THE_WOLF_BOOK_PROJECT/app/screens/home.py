from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Static

from app.widgets import AppHeader


class HomeScreen(Screen):
    BINDINGS = [
        Binding("enter", "open_categories", "Open categories"),
        Binding("c", "open_categories", "Categories"),
        Binding("/", "search", "Search"),
        Binding("?", "help", "Help"),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield AppHeader()
        yield Static("[b]Troubleshooting Terminal[/b]\n\nYour filesystem-backed troubleshooting knowledge base.\n\n[c]  Open Categories\n[/]  Search\n[?]  Help\n[q]  Quit", classes="home-content")
        yield Footer()

    def action_open_categories(self) -> None:
        self.app.open_categories()

    def action_search(self) -> None:
        self.app.open_search()

    def action_help(self) -> None:
        self.app.open_help()

    def action_quit(self) -> None:
        self.app.exit()
