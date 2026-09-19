from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Label, ListItem, ListView, Static

from app.services.filesystem import StorageError
from app.screens.dialogs import InputDialog
from app.widgets import AppHeader


class CategoriesScreen(Screen):
    BINDINGS = [
        Binding("a", "add_category", "Add category"),
        Binding("enter", "open_category", "Open"),
        Binding("x", "delete_category", "Delete"),
        Binding("escape", "back", "Back"),
        Binding("?", "help", "Help"),
        Binding("/", "search", "Search"),
    ]

    def compose(self) -> ComposeResult:
        yield AppHeader()
        with Container():
            yield Static("Categories", classes="screen-title")
            yield Static("Categories", id="breadcrumb")
            yield ListView(id="category-list")
        yield Footer()

    def on_mount(self) -> None:
        self.run_worker(self.refresh_categories(), exclusive=True)

    async def refresh_categories(self) -> None:
        category_list = self.query_one("#category-list", ListView)
        await category_list.clear()
        try:
            categories = self.app.store.categories()
        except StorageError as error:
            self.app.show_error(str(error))
            return
        for category in categories:
            category_list.append(ListItem(Label(category.name), name=category.name))
        if categories:
            category_list.index = 0
        else:
            category_list.append(ListItem(Label("No categories yet. Press 'a' to add one."), disabled=True))

    def action_add_category(self) -> None:
        self.app.push_screen(InputDialog("Add Category", "Category name", self.create_category), self.category_created)

    def create_category(self, name: str) -> bool:
        try:
            self.app.store.create_category(name)
        except StorageError as error:
            self.app.show_error(str(error))
            return False
        else:
            return True

    def category_created(self, result: str | None) -> None:
        if result is not None:
            self.run_worker(self.refresh_categories(), exclusive=True)
            self.app.notify("Category created.")

    def action_open_category(self) -> None:
        item = self.query_one("#category-list", ListView).highlighted_child
        if item and item.name:
            self.app.open_problems(item.name)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id == "category-list" and event.item.name:
            self.app.open_problems(event.item.name)

    def action_delete_category(self) -> None:
        item = self.query_one("#category-list", ListView).highlighted_child
        if not item or not item.name:
            return
        from app.screens.dialogs import ConfirmDialog
        category = self.app.store.categories_path / item.name
        self.app.push_screen(ConfirmDialog(f"Delete '{item.name}' and all its problems? [y/n]", lambda: self.delete_category(category)))

    def delete_category(self, category) -> None:
        try:
            self.app.store.delete(category)
        except StorageError as error:
            self.app.show_error(str(error))
        else:
            self.run_worker(self.refresh_categories(), exclusive=True)
            self.app.notify("Category deleted.")

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_help(self) -> None:
        self.app.open_help()

    def action_search(self) -> None:
        self.app.open_search()
