from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Label, ListItem, ListView, Static

from app.models.problem import Problem
from app.screens.dialogs import CommandDialog, ConfirmDialog
from app.services.filesystem import StorageError
from app.widgets import AppHeader


class ProblemScreen(Screen):
    BINDINGS = [
        Binding("a", "add_command", "Add command"),
        Binding("e", "edit_command", "Edit command"),
        Binding("d", "delete_command", "Delete command"),
        Binding("c", "copy_command", "Copy command"),
        Binding("m", "edit_details", "Edit problem"),
        Binding("x", "delete_problem", "Delete problem"),
        Binding("u", "move_up", "Move up"),
        Binding("j", "move_down", "Move down"),
        Binding("escape", "back", "Back"),
        Binding("?", "help", "Help"),
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
            yield Static(f"Categories > {self.category_name} > {self.problem_name}", id="breadcrumb")
            yield Static(id="problem-title", classes="problem-title")
            with VerticalScroll(id="problem-scroll"):
                yield Label(id="problem-description")
                yield Static("Solution", classes="section-title")
                yield ListView(id="command-list")
        yield Footer()

    def on_mount(self) -> None:
        try:
            self.problem = self.app.json_store.load(self.problem_path)
        except StorageError:
            if self.creating:
                self.problem = Problem(self.problem_name, "", [])
            else:
                self.app.show_error("Unable to open this problem.")
                self.app.pop_screen()
                return
        self.run_worker(self.refresh_view(), exclusive=True)
        if self.creating:
            self.notify("Add at least one command with 'a', then edit the description in the next step.")

    async def refresh_view(self) -> None:
        if not self.problem:
            return
        self.query_one("#problem-title", Static).update(self.problem.title)
        self.query_one("#problem-description", Label).update(self.problem.description or "No description yet.")
        command_list = self.query_one("#command-list", ListView)
        await command_list.clear()
        for command in self.problem.solution:
            command_list.append(ListItem(Label(f"{command.step}. {command.description}\n$ {command.command}"), name=str(command.step)))
        if self.problem.solution:
            command_list.index = 0
        else:
            command_list.append(ListItem(Label("No commands. Press 'a' to add one."), disabled=True))

    def action_add_command(self) -> None:
        if not self.problem:
            return
        self.app.push_screen(CommandDialog(), self.add_command)

    def add_command(self, result: tuple[str, str] | None) -> None:
        if result and self.problem:
            description, command = result
            from app.models.problem import Command
            self.problem.solution.append(Command(len(self.problem.solution) + 1, description, command))
            try:
                self.app.json_store.save(self.problem_path, self.problem)
            except StorageError as error:
                self.app.show_error(str(error))
            else:
                self.run_worker(self.refresh_view(), exclusive=True)

    def action_edit_command(self) -> None:
        if not self.problem:
            return
        item = self.query_one("#command-list", ListView).highlighted_child
        if not item or not item.name:
            return
        index = int(item.name) - 1
        command = self.problem.solution[index]
        self.app.push_screen(CommandDialog(command.description, command.command), lambda result: self.save_command(index, result))

    def save_command(self, index: int, result: tuple[str, str] | None) -> None:
        if result and self.problem:
            self.problem.solution[index].description, self.problem.solution[index].command = result
            self.save_problem()

    def action_delete_command(self) -> None:
        if not self.problem:
            return
        item = self.query_one("#command-list", ListView).highlighted_child
        if item and item.name:
            index = int(item.name) - 1
            self.app.push_screen(ConfirmDialog("Delete this command? [y/n]", lambda: self.delete_command(index)))

    def delete_command(self, index: int) -> None:
        if self.problem:
            self.problem.solution.pop(index)
            self.problem.renumber()
            self.save_problem()

    def action_move_up(self) -> None:
        self.move_command(-1)

    def action_move_down(self) -> None:
        self.move_command(1)

    def move_command(self, offset: int) -> None:
        if not self.problem:
            return
        list_view = self.query_one("#command-list", ListView)
        item = list_view.highlighted_child
        if not item or not item.name:
            return
        index = int(item.name) - 1
        target = index + offset
        if 0 <= target < len(self.problem.solution):
            self.problem.solution[index], self.problem.solution[target] = self.problem.solution[target], self.problem.solution[index]
            self.problem.renumber()
            self.save_problem()
            list_view.index = target

    def action_copy_command(self) -> None:
        if not self.problem:
            return
        item = self.query_one("#command-list", ListView).highlighted_child
        if not item or not item.name:
            return
        try:
            import pyperclip
            pyperclip.copy(self.problem.solution[int(item.name) - 1].command)
        except Exception:
            self.notify("Clipboard is unavailable in this terminal.", severity="warning")
        else:
            self.notify("Command copied.")

    def save_problem(self) -> None:
        if self.problem:
            try:
                self.app.json_store.save(self.problem_path, self.problem)
            except StorageError as error:
                self.app.show_error(str(error))
            else:
                self.run_worker(self.refresh_view(), exclusive=True)

    def action_back(self) -> None:
        if self.creating and self.problem and not self.problem.solution:
            try:
                self.app.store.delete(self.problem_path)
            except StorageError:
                pass
        self.app.pop_screen()

    def action_edit_details(self) -> None:
        self.app.edit_problem(self.category_name, self.problem_name)

    def action_delete_problem(self) -> None:
        from app.screens.dialogs import ConfirmDialog
        self.app.push_screen(ConfirmDialog(f"Delete '{self.problem_name}'? [y/n]", self.delete_problem))

    def delete_problem(self) -> None:
        try:
            self.app.store.delete(self.problem_path)
        except StorageError as error:
            self.app.show_error(str(error))
        else:
            self.app.notify("Problem deleted.")
            self.app.pop_screen()

    def action_help(self) -> None:
        self.app.open_help()
