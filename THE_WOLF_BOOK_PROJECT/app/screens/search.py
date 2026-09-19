from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Input, Label, ListItem, ListView, Static

from app.services.filesystem import StorageError
from app.widgets import AppHeader


class SearchScreen(Screen):
    BINDINGS = [Binding("escape", "back", "Back"), Binding("?", "help", "Help")]

    def compose(self) -> ComposeResult:
        yield AppHeader()
        with Container():
            yield Static("Search problems", classes="screen-title")
            yield Input(placeholder="Search title, description, or commands", id="search-input")
            yield ListView(id="search-results")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#search-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        self.run_worker(self.refresh_results(event.value), exclusive=True)

    async def refresh_results(self, query: str) -> None:
        results = self.query_one("#search-results", ListView)
        await results.clear()
        query = query.casefold().strip()
        if not query:
            return
        try:
            categories = self.app.store.categories()
        except StorageError as error:
            self.app.show_error(str(error))
            return
        for category in categories:
            try:
                problems = self.app.store.problems(category)
            except StorageError:
                continue
            for problem_path in problems:
                try:
                    problem = self.app.json_store.load(problem_path)
                except StorageError:
                    continue
                haystack = " ".join([problem.title, problem.description] + [f"{item.description} {item.command}" for item in problem.solution]).casefold()
                if query in haystack:
                    label = f"{category.name} > {problem_path.name}"
                    results.append(ListItem(Label(label), name=f"{category.name}\0{problem_path.name}"))
        if results.children:
            results.index = 0
        else:
            results.append(ListItem(Label("No matching problems."), disabled=True))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item.name:
            category, problem = event.item.name.split("\0")
            self.app.open_problem(category, problem)

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_help(self) -> None:
        self.app.open_help()
