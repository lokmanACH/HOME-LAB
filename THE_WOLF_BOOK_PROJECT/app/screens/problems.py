from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, ListItem, ListView, Label, Static

from app.screens.dialogs import InputDialog
from app.services.filesystem import StorageError
from app.widgets import AppHeader


class ProblemsScreen(Screen):
    BINDINGS = [
        Binding("a", "add_problem", "Add problem"),
        Binding("enter", "open_problem", "Open"),
        Binding("x", "delete_problem", "Delete"),
        Binding("escape", "back", "Back"),
        Binding("?", "help", "Help"),
        Binding("/", "search", "Search"),
    ]

    def __init__(self, category_name: str) -> None:
        super().__init__()
        self.category_name = category_name

    def compose(self) -> ComposeResult:
        yield AppHeader()
        with Container():
            yield Static(f"Categories > {self.category_name}", id="breadcrumb")
            yield ListView(id="problem-list")
        yield Footer()

    def on_mount(self) -> None:
        self.run_worker(self.refresh_problems(), exclusive=True)

    async def refresh_problems(self) -> None:
        problem_list = self.query_one("#problem-list", ListView)
        await problem_list.clear()
        category = self.app.store.categories_path / self.category_name
        try:
            problems = self.app.store.problems(category)
        except StorageError as error:
            self.app.show_error(str(error))
            return
        for problem in problems:
            problem_list.append(ListItem(Label(problem.name), name=problem.name))
        if problems:
            problem_list.index = 0
        else:
            problem_list.append(ListItem(Label("No problems yet. Press 'a' to add one."), disabled=True))

    def action_add_problem(self) -> None:
        self.app.push_screen(InputDialog("Add Problem", "Problem title", self.create_problem), self.problem_created)

    def create_problem(self, title: str) -> bool:
        try:
            category = self.app.store.categories_path / self.category_name
            self.app.store.create_problem(category, title)
        except StorageError as error:
            self.app.show_error(str(error))
            return False
        else:
            return True

    def problem_created(self, result: str | None) -> None:
        if result is not None:
            self.run_worker(self.refresh_problems(), exclusive=True)
            self.app.notify("Problem folder created.")
            self.app.open_problem(self.category_name, result.strip(), creating=True)

    def action_open_problem(self) -> None:
        item = self.query_one("#problem-list", ListView).highlighted_child
        if item and item.name:
            self.app.open_problem(self.category_name, item.name)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id == "problem-list" and event.item.name:
            self.app.open_problem(self.category_name, event.item.name)

    def action_delete_problem(self) -> None:
        item = self.query_one("#problem-list", ListView).highlighted_child
        if not item or not item.name:
            return
        from app.screens.dialogs import ConfirmDialog
        problem = self.app.store.categories_path / self.category_name / item.name
        self.app.push_screen(ConfirmDialog(f"Delete '{item.name}'? [y/n]", lambda: self.delete_problem(problem)))

    def delete_problem(self, problem) -> None:
        try:
            self.app.store.delete(problem)
        except StorageError as error:
            self.app.show_error(str(error))
        else:
            self.run_worker(self.refresh_problems(), exclusive=True)
            self.app.notify("Problem deleted.")

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_help(self) -> None:
        self.app.open_help()

    def action_search(self) -> None:
        self.app.open_search()
