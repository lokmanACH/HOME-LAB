from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Input, Label, ListItem, ListView, TextArea, Static

from app.models.problem import Command, Problem, validate_problem
from app.screens.dialogs import CommandDialog
from app.services.filesystem import StorageError
from app.widgets import AppHeader


class ProblemEditorScreen(Screen):
    BINDINGS = [
        Binding("a", "add_command", "Add command"),
        Binding("e", "edit_command", "Edit command"),
        Binding("d", "delete_command", "Delete command"),
        Binding("u", "move_up", "Move up"),
        Binding("j", "move_down", "Move down"),
        Binding("escape", "cancel", "Cancel"),
        Binding("ctrl+s", "save", "Save"),
    ]

    def __init__(self, category_name: str, problem_name: str, creating: bool = False) -> None:
        super().__init__()
        self.category_name = category_name
        self.problem_name = problem_name
        self.creating = creating
        self.problem: Problem | None = None

    @property
    def problem_path(self):
        return self.app.store.categories_path / self.category_name / self.problem_name

    def compose(self) -> ComposeResult:
        yield AppHeader()
        with Container():
            yield Static(f"Categories > {self.category_name} > {self.problem_name} > Edit", id="breadcrumb")
            yield Input(placeholder="Problem title (1-80 characters)", id="title")
            yield Label("Description (0/2000)", id="description-label")
            yield TextArea(id="description")
            yield Static("Commands", classes="section-title")
            yield ListView(id="command-list")
            with Horizontal():
                yield Button("Save", variant="primary", id="save")
                yield Button("Cancel", id="cancel")
        yield Footer()

    def on_mount(self) -> None:
        if self.creating:
            self.problem = Problem(self.problem_name, "", [])
        else:
            try:
                self.problem = self.app.json_store.load(self.problem_path)
            except StorageError as error:
                self.app.show_error(str(error))
                self.app.pop_screen()
                return
        self.query_one("#title", Input).value = self.problem.title
        self.query_one("#description", TextArea).text = self.problem.description
        self.run_worker(self.refresh_commands(), exclusive=True)
        self.update_description_count()
        self.query_one("#title", Input).focus()

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        if event.text_area.id == "description":
            self.update_description_count()

    def update_description_count(self) -> None:
        text = self.query_one("#description", TextArea).text
        self.query_one("#description-label", Label).update(f"Description ({len(text)}/2000)")

    async def refresh_commands(self) -> None:
        command_list = self.query_one("#command-list", ListView)
        await command_list.clear()
        for command in self.problem.solution if self.problem else []:
            command_list.append(ListItem(Label(f"{command.step}. {command.description}\n$ {command.command}"), name=str(command.step)))
        if self.problem and self.problem.solution:
            command_list.index = 0
        else:
            command_list.append(ListItem(Label("No commands. Press 'a' to add one."), disabled=True))

    def action_add_command(self) -> None:
        self.app.push_screen(CommandDialog(), self.add_command)

    def add_command(self, result: tuple[str, str] | None) -> None:
        if result and self.problem:
            description, command = result
            self.problem.solution.append(Command(len(self.problem.solution) + 1, description, command))
            self.run_worker(self.refresh_commands(), exclusive=True)

    def action_edit_command(self) -> None:
        item = self.query_one("#command-list", ListView).highlighted_child
        if not item or not item.name or not self.problem:
            return
        index = int(item.name) - 1
        command = self.problem.solution[index]
        self.app.push_screen(CommandDialog(command.description, command.command), lambda result: self.update_command(index, result))

    def update_command(self, index: int, result: tuple[str, str] | None) -> None:
        if result and self.problem:
            self.problem.solution[index].description, self.problem.solution[index].command = result
            self.run_worker(self.refresh_commands(), exclusive=True)

    def action_delete_command(self) -> None:
        item = self.query_one("#command-list", ListView).highlighted_child
        if item and item.name and self.problem:
            self.problem.solution.pop(int(item.name) - 1)
            self.problem.renumber()
            self.run_worker(self.refresh_commands(), exclusive=True)

    def action_move_up(self) -> None:
        self.move_command(-1)

    def action_move_down(self) -> None:
        self.move_command(1)

    def move_command(self, offset: int) -> None:
        item = self.query_one("#command-list", ListView).highlighted_child
        if not item or not item.name or not self.problem:
            return
        index = int(item.name) - 1
        target = index + offset
        if 0 <= target < len(self.problem.solution):
            self.problem.solution[index], self.problem.solution[target] = self.problem.solution[target], self.problem.solution[index]
            self.problem.renumber()
            self.run_worker(self.refresh_commands(), exclusive=True)
            self.query_one("#command-list", ListView).index = target

    def action_save(self) -> None:
        if not self.problem:
            return
        title = self.query_one("#title", Input).value.strip()
        description = self.query_one("#description", TextArea).text
        errors = validate_problem(title, description, self.problem.solution)
        if errors:
            self.app.show_error(" ".join(errors))
            return
        try:
            if title.casefold() != self.problem_name.casefold():
                new_path = self.app.store.rename_problem(self.problem_path, title)
                self.problem_path_name = new_path.name
                self.problem_name = new_path.name
            self.problem.title = title
            self.problem.description = description
            self.app.json_store.save(self.problem_path, self.problem)
        except StorageError as error:
            self.app.show_error(str(error))
            return
        self.app.notify("Problem saved.")
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self.action_save()
        else:
            self.action_cancel()

    def action_cancel(self) -> None:
        if self.creating and self.problem_path.exists():
            try:
                self.app.store.delete(self.problem_path)
            except StorageError:
                pass
        self.app.pop_screen()
