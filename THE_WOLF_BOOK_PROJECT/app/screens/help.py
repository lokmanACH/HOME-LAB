from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Static

from app.widgets import AppHeader


class HelpScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back"), ("?", "app.pop_screen", "Back")]

    def compose(self) -> ComposeResult:
        yield AppHeader()
        yield Static(
            "[b]Keyboard Shortcuts[/b]\n\n"
            "[b]Navigation[/b]\n"
            "↑ / ↓   Move selection\n"
            "Enter   Open or select\n"
            "Esc     Back or cancel\n\n"
            "[b]General[/b]\n"
            "/       Search problems\n"
            "?       Show this help\n"
            "q       Quit\n\n"
            "[b]Categories and Problems[/b]\n"
            "a       Add\n"
            "m       Edit problem details\n"
            "x       Delete selected item\n\n"
            "[b]Commands[/b]\n"
            "a       Add command\n"
            "e       Edit command\n"
            "d       Delete command\n"
            "u / j   Move command up / down\n"
            "c       Copy selected command",
            classes="help-content",
        )
        yield Footer()
