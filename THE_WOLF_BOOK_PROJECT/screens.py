from typing import Any, Dict, List, Optional
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
    TextArea,
)

import storage


class HelpModal(ModalScreen[None]):
    """Modal displaying keyboard shortcuts."""

    DEFAULT_CSS = """
    HelpModal {
        align: center middle;
    }
    #help-box {
        width: 60;
        height: auto;
        border: solid green;
        background: $surface;
        padding: 1 2;
    }
    #help-title {
        text-style: bold;
        margin-bottom: 1;
    }
    #help-content {
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close", show=True),
        Binding("q", "close", "Close", show=False),
        Binding("question_mark", "close", "Close", show=False),
    ]

    def compose(self) -> ComposeResult:
        help_text = (
            "Keyboard Shortcuts\n\n"
            "↑ ↓       Navigate\n"
            "Enter     Select\n"
            "Esc       Back / Close\n"
            "a         Add\n"
            "e         Edit\n"
            "d         Delete\n"
            "/         Search\n"
            "?         Help\n"
            "q         Quit\n\n"
            "Press Esc to close"
        )
        with Vertical(id="help-box"):
            yield Label("Help", id="help-title")
            yield Static(help_text, id="help-content")

    def action_close(self) -> None:
        self.dismiss()


class ConfirmDeleteModal(ModalScreen[bool]):
    """Modal dialog asking for deletion confirmation with y/n."""

    DEFAULT_CSS = """
    ConfirmDeleteModal {
        align: center middle;
    }
    #confirm-box {
        width: 60;
        height: auto;
        border: solid red;
        background: $surface;
        padding: 1 2;
    }
    #confirm-title {
        text-style: bold;
        color: $error;
        margin-bottom: 1;
    }
    #confirm-text {
        margin-bottom: 1;
    }
    #confirm-buttons {
        width: 100%;
        align: center middle;
        height: auto;
    }
    #confirm-buttons Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("y", "confirm_yes", "Yes", show=True),
        Binding("n", "confirm_no", "No", show=True),
        Binding("escape", "confirm_no", "Cancel", show=True),
    ]

    def __init__(self, target_name: str, item_type: str = "item") -> None:
        super().__init__()
        self.target_name = target_name
        self.item_type = item_type

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-box"):
            yield Label("Confirm Deletion", id="confirm-title")
            yield Static(f'Delete "{self.target_name}"?\n\n[y] Yes    [n] No', id="confirm-text")
            with Horizontal(id="confirm-buttons"):
                yield Button("Yes (y)", variant="error", id="btn-yes")
                yield Button("No (n)", variant="default", id="btn-no")

    def action_confirm_yes(self) -> None:
        self.dismiss(True)

    def action_confirm_no(self) -> None:
        self.dismiss(False)

    @on(Button.Pressed, "#btn-yes")
    def on_yes_pressed(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#btn-no")
    def on_no_pressed(self) -> None:
        self.dismiss(False)


class AddCategoryModal(ModalScreen[Optional[str]]):
    """Modal to enter a new category name."""

    DEFAULT_CSS = """
    AddCategoryModal {
        align: center middle;
    }
    #cat-box {
        width: 60;
        height: auto;
        border: solid $primary;
        background: $surface;
        padding: 1 2;
    }
    #cat-error {
        color: $error;
        margin-top: 1;
    }
    #cat-buttons {
        margin-top: 1;
        width: 100%;
        align: right middle;
    }
    #cat-buttons Button {
        margin-left: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="cat-box"):
            yield Label("Add Category", id="cat-title")
            yield Label("Category name:")
            yield Input(placeholder="e.g. Linux, Docker, AWS", id="cat-input", max_length=50)
            yield Static("", id="cat-error")
            with Horizontal(id="cat-buttons"):
                yield Button("Cancel", id="btn-cancel")
                yield Button("Create", variant="primary", id="btn-create")

    def on_mount(self) -> None:
        self.query_one("#cat-input", Input).focus()

    def action_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#btn-cancel")
    def on_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#btn-create")
    @on(Input.Submitted, "#cat-input")
    def submit(self) -> None:
        val = self.query_one("#cat-input", Input).value
        valid, result = storage.create_category(val)
        if not valid:
            self.query_one("#cat-error", Static).update(result)
            return
        self.dismiss(result)


class CommandModal(ModalScreen[Optional[Dict[str, str]]]):
    """Modal to add or edit a command."""

    DEFAULT_CSS = """
    CommandModal {
        align: center middle;
    }
    #cmd-box {
        width: 70;
        height: auto;
        border: solid $primary;
        background: $surface;
        padding: 1 2;
    }
    #cmd-error {
        color: $error;
        margin-top: 1;
    }
    #cmd-buttons {
        margin-top: 1;
        width: 100%;
        align: right middle;
    }
    #cmd-buttons Button {
        margin-left: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, initial_desc: str = "", initial_cmd: str = "") -> None:
        super().__init__()
        self.initial_desc = initial_desc
        self.initial_cmd = initial_cmd

    def compose(self) -> ComposeResult:
        with Vertical(id="cmd-box"):
            yield Label("Command Details")
            yield Label("Description:")
            yield Input(value=self.initial_desc, placeholder="e.g. Find what is using the port", id="cmd-desc", max_length=300)
            yield Label("Command:")
            yield Input(value=self.initial_cmd, placeholder="e.g. sudo ss -lntp | grep :3000", id="cmd-text", max_length=1000)
            yield Static("", id="cmd-error")
            with Horizontal(id="cmd-buttons"):
                yield Button("Cancel", id="btn-cmd-cancel")
                yield Button("Save Command", variant="primary", id="btn-cmd-save")

    def on_mount(self) -> None:
        self.query_one("#cmd-desc", Input).focus()

    def action_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#btn-cmd-cancel")
    def on_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#btn-cmd-save")
    def on_save(self) -> None:
        desc = self.query_one("#cmd-desc", Input).value
        cmd = self.query_one("#cmd-text", Input).value
        valid, err = storage.validate_command_item(desc, cmd)
        if not valid:
            self.query_one("#cmd-error", Static).update(err)
            return
        self.dismiss({"description": desc.strip(), "command": cmd.strip()})


class ProblemEditScreen(Screen[Optional[str]]):
    """Screen for adding or editing a problem."""

    DEFAULT_CSS = """
    #form-container {
        padding: 1 2;
    }
    .field-label {
        text-style: bold;
        margin-top: 1;
    }
    #desc-input {
        height: 6;
    }
    #commands-list {
        height: 7;
        border: solid $secondary;
        margin-top: 1;
    }
    #cmd-actions {
        margin-top: 1;
        height: auto;
    }
    #cmd-actions Button {
        margin-right: 1;
    }
    #bottom-actions {
        margin-top: 1;
        height: auto;
    }
    #bottom-actions Button {
        margin-right: 1;
    }
    #form-error {
        color: $error;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel / Back"),
        Binding("ctrl+s", "save", "Save"),
        Binding("a", "add_command", "Add command"),
        Binding("e", "edit_command", "Edit command"),
        Binding("d", "delete_command", "Delete command"),
        Binding("question_mark", "show_help", "Help"),
    ]

    def __init__(
        self,
        category: str,
        initial_title: str = "",
        initial_desc: str = "",
        initial_commands: Optional[List[Dict[str, str]]] = None,
        is_edit: bool = False,
    ) -> None:
        super().__init__()
        self.category = category
        self.old_title = initial_title if is_edit else None
        self.initial_title = initial_title
        self.initial_desc = initial_desc
        self.commands: List[Dict[str, str]] = list(initial_commands) if initial_commands else []
        self.is_edit = is_edit

    def compose(self) -> ComposeResult:
        mode_str = "Edit Problem" if self.is_edit else "Add Problem"
        yield Header()
        with VerticalScroll(id="form-container"):
            yield Label(f"{self.category} > {mode_str}", classes="field-label")
            yield Label("Title (max 80 chars):", classes="field-label")
            yield Input(value=self.initial_title, id="title-input", max_length=80)

            yield Label("Description (max 2000 chars):", classes="field-label")
            yield TextArea(text=self.initial_desc, id="desc-input")

            yield Label("Commands (at least one required):", classes="field-label")
            yield ListView(id="commands-list")

            with Horizontal(id="cmd-actions"):
                yield Button("Add Command (a)", id="btn-add-cmd", variant="default")
                yield Button("Edit Selected Command (e)", id="btn-edit-cmd", variant="default")
                yield Button("Delete Selected Command (d)", id="btn-del-cmd", variant="default")

            yield Static("", id="form-error")

            with Horizontal(id="bottom-actions"):
                yield Button("Save Problem (Ctrl+S)", id="btn-save", variant="primary")
                yield Button("Cancel (Esc)", id="btn-cancel", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_commands_list()
        self.query_one("#title-input", Input).focus()

    def refresh_commands_list(self) -> None:
        lv = self.query_one("#commands-list", ListView)
        lv.clear()
        for idx, item in enumerate(self.commands, 1):
            lv.append(ListItem(Static(f"{idx}. {item['description']}  ->  `{item['command']}`")))

    def action_show_help(self) -> None:
        self.app.push_screen(HelpModal())

    def action_cancel(self) -> None:
        self.dismiss(None)

    def action_save(self) -> None:
        self.perform_save()

    def on_key(self, event) -> None:
        if event.key not in {"a", "e", "d"}:
            return
        if self.focused is not self.query_one("#commands-list", ListView):
            return
        actions = {
            "a": self.on_add_cmd_btn,
            "e": self.on_edit_cmd_btn,
            "d": self.on_del_cmd_btn,
        }
        actions[event.key]()
        event.stop()

    def action_add_command(self) -> None:
        self.on_add_cmd_btn()

    def action_edit_command(self) -> None:
        self.on_edit_cmd_btn()

    def action_delete_command(self) -> None:
        self.on_del_cmd_btn()

    @on(Button.Pressed, "#btn-cancel")
    def on_cancel_btn(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#btn-save")
    def on_save_btn(self) -> None:
        self.perform_save()

    @on(Button.Pressed, "#btn-add-cmd")
    def on_add_cmd_btn(self) -> None:
        def on_cmd_saved(cmd: Optional[Dict[str, str]]) -> None:
            if cmd:
                self.commands.append(cmd)
                self.refresh_commands_list()
        self.app.push_screen(CommandModal(), on_cmd_saved)

    @on(Button.Pressed, "#btn-edit-cmd")
    def on_edit_cmd_btn(self) -> None:
        lv = self.query_one("#commands-list", ListView)
        if lv.index is None or lv.index < 0 or lv.index >= len(self.commands):
            self.query_one("#form-error", Static).update("Select a command from the list first.")
            return
        idx = lv.index
        curr = self.commands[idx]

        def on_cmd_edited(cmd: Optional[Dict[str, str]]) -> None:
            if cmd:
                self.commands[idx] = cmd
                self.refresh_commands_list()
        self.app.push_screen(CommandModal(curr["description"], curr["command"]), on_cmd_edited)

    @on(Button.Pressed, "#btn-del-cmd")
    def on_del_cmd_btn(self) -> None:
        lv = self.query_one("#commands-list", ListView)
        if lv.index is None or lv.index < 0 or lv.index >= len(self.commands):
            self.query_one("#form-error", Static).update("Select a command from the list first.")
            return
        del self.commands[lv.index]
        self.refresh_commands_list()

    def perform_save(self) -> None:
        title = self.query_one("#title-input", Input).value
        desc = self.query_one("#desc-input", TextArea).text
        valid, result = storage.save_problem(
            self.category,
            title,
            desc,
            self.commands,
            old_title=self.old_title
        )
        if not valid:
            self.query_one("#form-error", Static).update(result)
            return
        self.dismiss(result)


class ProblemDetailScreen(Screen[None]):
    """Screen displaying problem details."""

    DEFAULT_CSS = """
    #detail-container {
        padding: 1 2;
    }
    .sec-header {
        text-style: bold;
        color: $accent;
        margin-top: 1;
    }
    .sec-body {
        margin-left: 2;
        margin-top: 0;
        margin-bottom: 1;
    }
    .cmd-item {
        margin-top: 1;
        margin-left: 2;
    }
    .cmd-desc {
        text-style: bold;
    }
    .cmd-code {
        margin-left: 3;
        color: $success;
        text-style: bold;
    }
    #error-label {
        color: $error;
        margin: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("e", "edit_problem", "Edit"),
        Binding("d", "delete_problem", "Delete"),
        Binding("slash", "search", "Search"),
        Binding("question_mark", "show_help", "Help"),
        Binding("q", "quit_app", "Quit"),
    ]

    def __init__(self, category: str, problem_title: str) -> None:
        super().__init__()
        self.category = category
        self.problem_title = problem_title

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(id="detail-container")
        yield Footer()

    def on_mount(self) -> None:
        self.load_data()

    def load_data(self) -> None:
        container = self.query_one("#detail-container", VerticalScroll)
        container.remove_children()

        data, err = storage.get_problem(self.category, self.problem_title)
        if err or not data:
            container.mount(Label(f"Error loading problem: {err or 'Unknown error'}", id="error-label"))
            return

        title = data.get("title", self.problem_title)
        desc = data.get("description", "")
        solution = data.get("solution", [])

        container.mount(Label(f"{self.category} > {title}", classes="sec-header"))
        container.mount(Label("Title:", classes="sec-header"))
        container.mount(Static(title, classes="sec-body"))

        container.mount(Label("Description:", classes="sec-header"))
        container.mount(Static(desc, classes="sec-body"))

        container.mount(Label("Solution:", classes="sec-header"))
        if not solution:
            container.mount(Static("No commands listed.", classes="sec-body"))
        else:
            for idx, item in enumerate(solution, 1):
                c_desc = item.get("description", "")
                c_cmd = item.get("command", "")
                container.mount(Static(f"{idx}. {c_desc}", classes="cmd-desc"))
                container.mount(Static(f"   {c_cmd}", classes="cmd-code"))

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_edit_problem(self) -> None:
        data, err = storage.get_problem(self.category, self.problem_title)
        if not data:
            return

        def on_saved(saved_title: Optional[str]) -> None:
            if saved_title:
                self.problem_title = saved_title
                self.load_data()

        self.app.push_screen(
            ProblemEditScreen(
                category=self.category,
                initial_title=data.get("title", self.problem_title),
                initial_desc=data.get("description", ""),
                initial_commands=data.get("solution", []),
                is_edit=True,
            ),
            on_saved,
        )

    def action_delete_problem(self) -> None:
        def on_confirmed(confirmed: Optional[bool]) -> None:
            if confirmed:
                storage.delete_problem(self.category, self.problem_title)
                self.app.pop_screen()

        self.app.push_screen(ConfirmDeleteModal(self.problem_title, "problem"), on_confirmed)

    def action_search(self) -> None:
        self.app.push_screen(SearchScreen())

    def action_show_help(self) -> None:
        self.app.push_screen(HelpModal())

    def action_quit_app(self) -> None:
        self.app.exit()


class ProblemsScreen(Screen[None]):
    """Screen listing problems in a category."""

    DEFAULT_CSS = """
    #prob-box {
        padding: 1 2;
    }
    #prob-header {
        text-style: bold;
        margin-bottom: 1;
    }
    #problems-list {
        height: 1fr;
        border: solid $accent;
    }
    #status-msg {
        color: $error;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("a", "add_problem", "Add problem"),
        Binding("d", "delete_problem", "Delete problem"),
        Binding("slash", "search", "Search"),
        Binding("question_mark", "show_help", "Help"),
        Binding("q", "quit_app", "Quit"),
    ]

    def __init__(self, category: str) -> None:
        super().__init__()
        self.category = category

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="prob-box"):
            yield Label(self.category, id="prob-header")
            yield ListView(id="problems-list")
            yield Static("", id="status-msg")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_list()

    def refresh_list(self) -> None:
        lv = self.query_one("#problems-list", ListView)
        lv.clear()
        problems = storage.list_problems(self.category)
        if not problems:
            lv.append(ListItem(Static("No problems found. Press 'a' to add one.")))
        else:
            for p in problems:
                lv.append(ListItem(Static(f"> {p}")))
        lv.focus()

    def get_selected_problem(self) -> Optional[str]:
        lv = self.query_one("#problems-list", ListView)
        problems = storage.list_problems(self.category)
        if lv.index is not None and 0 <= lv.index < len(problems):
            return problems[lv.index]
        return None

    @on(ListView.Selected, "#problems-list")
    def on_select(self, event: ListView.Selected) -> None:
        problem = self.get_selected_problem()
        if problem:
            self.app.push_screen(ProblemDetailScreen(self.category, problem))

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_add_problem(self) -> None:
        def on_saved(saved_title: Optional[str]) -> None:
            if saved_title:
                self.refresh_list()
                self.app.push_screen(ProblemDetailScreen(self.category, saved_title))
        self.app.push_screen(ProblemEditScreen(self.category, is_edit=False), on_saved)

    def action_delete_problem(self) -> None:
        prob = self.get_selected_problem()
        if not prob:
            self.query_one("#status-msg", Static).update("No problem selected to delete.")
            return

        def on_confirmed(confirmed: Optional[bool]) -> None:
            if confirmed:
                storage.delete_problem(self.category, prob)
                self.refresh_list()

        self.app.push_screen(ConfirmDeleteModal(prob, "problem"), on_confirmed)

    def action_search(self) -> None:
        self.app.push_screen(SearchScreen())

    def action_show_help(self) -> None:
        self.app.push_screen(HelpModal())

    def action_quit_app(self) -> None:
        self.app.exit()


class CategoriesScreen(Screen[None]):
    """Screen listing category folders."""

    DEFAULT_CSS = """
    #cat-screen-box {
        padding: 1 2;
    }
    #categories-title {
        text-style: bold;
        margin-bottom: 1;
    }
    #categories-list {
        height: 1fr;
        border: solid $primary;
    }
    #cat-status {
        color: $error;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("a", "add_category", "Add category"),
        Binding("d", "delete_category", "Delete category"),
        Binding("slash", "search", "Search"),
        Binding("question_mark", "show_help", "Help"),
        Binding("q", "quit_app", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="cat-screen-box"):
            yield Label("Categories", id="categories-title")
            yield ListView(id="categories-list")
            yield Static("", id="cat-status")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_list()

    def refresh_list(self) -> None:
        lv = self.query_one("#categories-list", ListView)
        lv.clear()
        categories = storage.list_categories()
        if not categories:
            lv.append(ListItem(Static("No categories yet. Press 'a' to add one.")))
        else:
            for cat in categories:
                lv.append(ListItem(Static(f"> {cat}")))
        lv.focus()

    def get_selected_category(self) -> Optional[str]:
        lv = self.query_one("#categories-list", ListView)
        categories = storage.list_categories()
        if lv.index is not None and 0 <= lv.index < len(categories):
            return categories[lv.index]
        return None

    @on(ListView.Selected, "#categories-list")
    def on_select(self, event: ListView.Selected) -> None:
        cat = self.get_selected_category()
        if cat:
            self.app.push_screen(ProblemsScreen(cat))

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_add_category(self) -> None:
        def on_added(new_cat: Optional[str]) -> None:
            if new_cat:
                self.refresh_list()
        self.app.push_screen(AddCategoryModal(), on_added)

    def action_delete_category(self) -> None:
        cat = self.get_selected_category()
        if not cat:
            self.query_one("#cat-status", Static).update("No category selected to delete.")
            return

        def on_confirmed(confirmed: Optional[bool]) -> None:
            if confirmed:
                storage.delete_category(cat)
                self.refresh_list()

        self.app.push_screen(ConfirmDeleteModal(cat, "category"), on_confirmed)

    def action_search(self) -> None:
        self.app.push_screen(SearchScreen())

    def action_show_help(self) -> None:
        self.app.push_screen(HelpModal())

    def action_quit_app(self) -> None:
        self.app.exit()


class SearchScreen(Screen[None]):
    """Screen for full-text search across titles, descriptions, and commands."""

    DEFAULT_CSS = """
    #search-box {
        padding: 1 2;
    }
    #search-input {
        margin-bottom: 1;
    }
    #results-list {
        height: 1fr;
        border: solid $accent;
    }
    """

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("question_mark", "show_help", "Help"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="search-box"):
            yield Label("Search:")
            yield Input(placeholder="Type search terms...", id="search-input")
            yield Label("Results:")
            yield ListView(id="results-list")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#search-input", Input).focus()
        self.matched_items: List[tuple[str, str, str]] = []

    @on(Input.Changed, "#search-input")
    def on_input_changed(self, event: Input.Changed) -> None:
        self.run_search(event.value)

    @on(Input.Submitted, "#search-input")
    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.run_search(event.value)
        lv = self.query_one("#results-list", ListView)
        if len(self.matched_items) > 0:
            lv.focus()

    def run_search(self, query: str) -> None:
        lv = self.query_one("#results-list", ListView)
        lv.clear()
        if not query.strip():
            self.matched_items = []
            return

        self.matched_items = storage.search_all(query)
        if not self.matched_items:
            lv.append(ListItem(Static("No matching problems found.")))
        else:
            for cat, prob, match_reason in self.matched_items:
                lv.append(ListItem(Static(f"> {cat} > {prob}  ({match_reason})")))

    @on(ListView.Selected, "#results-list")
    def on_select(self, event: ListView.Selected) -> None:
        lv = self.query_one("#results-list", ListView)
        if lv.index is not None and 0 <= lv.index < len(self.matched_items):
            cat, prob, _ = self.matched_items[lv.index]
            self.app.push_screen(ProblemDetailScreen(cat, prob))

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_show_help(self) -> None:
        self.app.push_screen(HelpModal())

