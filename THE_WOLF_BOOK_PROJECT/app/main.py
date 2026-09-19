from __future__ import annotations

from pathlib import Path

from textual.app import App

from app.screens.categories import CategoriesScreen
from app.screens.edit import ProblemEditorScreen
from app.screens.help import HelpScreen
from app.screens.home import HomeScreen
from app.screens.problem import ProblemScreen
from app.screens.problems import ProblemsScreen
from app.screens.search import SearchScreen
from app.services.filesystem import FileSystemStore, StorageError
from app.services.json_store import JsonStore


class TroubleshootingTerminal(App):
    TITLE = "Troubleshooting Terminal"
    CSS_PATH = "app.css"

    def __init__(self, data_root: Path | str | None = None) -> None:
        super().__init__()
        project_root = Path(data_root) if data_root else Path(__file__).resolve().parent.parent / "data"
        self.store = FileSystemStore(project_root)
        self.json_store = JsonStore()

    def on_mount(self) -> None:
        self.push_screen(HomeScreen())

    def open_categories(self) -> None:
        self.push_screen(CategoriesScreen())

    def open_problems(self, category_name: str) -> None:
        self.push_screen(ProblemsScreen(category_name))

    def open_problem(self, category_name: str, problem_name: str, creating: bool = False) -> None:
        if creating:
            self.push_screen(ProblemEditorScreen(category_name, problem_name, creating=True))
        else:
            self.push_screen(ProblemScreen(category_name, problem_name))

    def edit_problem(self, category_name: str, problem_name: str) -> None:
        self.push_screen(ProblemEditorScreen(category_name, problem_name))

    def open_search(self) -> None:
        self.push_screen(SearchScreen())

    def open_help(self) -> None:
        self.push_screen(HelpScreen())

    def show_error(self, message: str) -> None:
        self.notify(message, severity="error", timeout=6)


def main() -> None:
    TroubleshootingTerminal().run()


if __name__ == "__main__":
    main()
