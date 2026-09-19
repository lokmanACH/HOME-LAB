from __future__ import annotations

from collections.abc import Callable

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, TextArea


class InputDialog(ModalScreen[str | None]):
    def __init__(self, heading: str, prompt: str, on_submit: Callable[[str], bool]) -> None:
        super().__init__()
        self.heading = heading
        self.prompt = prompt
        self.on_submit = on_submit
        self._submitting = False

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Label(self.heading, id="dialog-heading")
            yield Label(self.prompt)
            yield Input(placeholder="Type a name", id="dialog-input")
            with Horizontal():
                yield Button("Save", variant="primary", id="save")
                yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        self.query_one("#dialog-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._submit(event.value)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self._cancel()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self._submit(self.query_one("#dialog-input", Input).value)
        else:
            self._cancel()

    def _submit(self, value: str) -> None:
        if self._submitting:
            return
        self._submitting = True
        if not self.on_submit(value):
            self._submitting = False
            return
        self.dismiss(value)

    def _cancel(self) -> None:
        if self._submitting:
            return
        self._submitting = True
        self.dismiss(None)


class ConfirmDialog(ModalScreen[bool]):
    def __init__(self, message: str, on_confirm: Callable[[], None]) -> None:
        super().__init__()
        self.message = message
        self.on_confirm = on_confirm
        self._closing = False

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Label(self.message)
            with Horizontal():
                yield Button("Yes", variant="error", id="yes")
                yield Button("No", id="no")

    def on_mount(self) -> None:
        self.query_one("#yes", Button).focus()

    def on_key(self, event) -> None:
        if event.key.lower() == "y":
            self._confirm()
        elif event.key.lower() == "n" or event.key == "escape":
            self._cancel()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self._confirm()
        else:
            self._cancel()

    def _confirm(self) -> None:
        if self._closing:
            return
        self._closing = True
        self.dismiss(True)
        self.on_confirm()

    def _cancel(self) -> None:
        if self._closing:
            return
        self._closing = True
        self.dismiss(False)


class CommandDialog(ModalScreen[tuple[str, str] | None]):
    def __init__(self, description: str = "", command: str = "") -> None:
        super().__init__()
        self.initial_description = description
        self.initial_command = command
        self._closing = False

    def compose(self) -> ComposeResult:
        with Container(id="dialog", classes="wide-dialog"):
            yield Label("Command")
            yield Label("Description (300 characters maximum)")
            yield Input(value=self.initial_description, id="command-description")
            yield Label("Command (1000 characters maximum)")
            yield TextArea(self.initial_command, id="command-text")
            with Horizontal():
                yield Button("Save", variant="primary", id="save")
                yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        self.query_one("#command-description", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            description = self.query_one("#command-description", Input).value.strip()
            command = self.query_one("#command-text", TextArea).text.strip()
            if not description or not command:
                self.notify("Both command fields are required.", severity="error")
                return
            if len(description) > 300 or len(command) > 1000:
                self.notify("Command fields exceed their limits.", severity="error")
                return
            self._close((description, command))
        else:
            self._close(None)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self._close(None)

    def _close(self, result: tuple[str, str] | None) -> None:
        if self._closing:
            return
        self._closing = True
        self.dismiss(result)
