from textual.widgets import Static


class AppHeader(Static):
    """Small header that avoids Textual Header internals across versions."""

    DEFAULT_CSS = """
    AppHeader {
        height: 1;
        padding: 0 2;
        background: #17324d;
        color: #f5c96a;
        text-style: bold;
    }
    """

    def __init__(self) -> None:
        super().__init__("Troubleshooting Terminal")
