from __future__ import annotations

import shutil
from pathlib import Path

INVALID_NAME_CHARACTERS = set('/:*?"<>|')


class StorageError(Exception):
    pass


def validate_folder_name(value: str, maximum: int, label: str) -> str:
    name = value.strip()
    if not name:
        raise StorageError(f"{label} cannot be empty.")
    if name in {".", ".."}:
        raise StorageError(f"{label} cannot be '.' or '..'.")
    if len(name) > maximum:
        raise StorageError(f"{label} must be {maximum} characters or fewer.")
    if any(character in INVALID_NAME_CHARACTERS for character in name):
        raise StorageError(f"{label} contains an invalid filesystem character.")
    return name


class FileSystemStore:
    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)
        self.categories_path = self.root / "categories"
        self.categories_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _find_case_insensitive(parent: Path, name: str) -> Path | None:
        try:
            for child in parent.iterdir():
                if child.is_dir() and child.name.casefold() == name.casefold():
                    return child
        except OSError as error:
            raise StorageError(f"Unable to read {parent}: {error}") from error
        return None

    def categories(self) -> list[Path]:
        try:
            return sorted((item for item in self.categories_path.iterdir() if item.is_dir()), key=lambda item: item.name.casefold())
        except OSError as error:
            raise StorageError(f"Unable to read categories: {error}") from error

    def create_category(self, name: str) -> Path:
        clean_name = validate_folder_name(name, 50, "Category name")
        if self._find_case_insensitive(self.categories_path, clean_name):
            raise StorageError(f"Category '{clean_name}' already exists.")
        path = self.categories_path / clean_name
        try:
            path.mkdir()
        except OSError as error:
            raise StorageError(f"Unable to create category: {error}") from error
        return path

    def problems(self, category: Path) -> list[Path]:
        try:
            return sorted((item for item in category.iterdir() if item.is_dir()), key=lambda item: item.name.casefold())
        except OSError as error:
            raise StorageError(f"Unable to read problems: {error}") from error

    def create_problem(self, category: Path, title: str) -> Path:
        clean_title = validate_folder_name(title, 80, "Problem title")
        if self._find_case_insensitive(category, clean_title):
            raise StorageError(f"Problem '{clean_title}' already exists.")
        path = category / clean_title
        try:
            path.mkdir()
        except OSError as error:
            raise StorageError(f"Unable to create problem: {error}") from error
        return path

    def delete(self, path: Path) -> None:
        try:
            shutil.rmtree(path)
        except OSError as error:
            raise StorageError(f"Unable to delete '{path.name}': {error}") from error

    def rename_problem(self, problem_path: Path, new_title: str) -> Path:
        clean_title = validate_folder_name(new_title, 80, "Problem title")
        if clean_title.casefold() != problem_path.name.casefold() and self._find_case_insensitive(problem_path.parent, clean_title):
            raise StorageError(f"Problem '{clean_title}' already exists.")
        destination = problem_path.parent / clean_title
        try:
            problem_path.rename(destination)
        except OSError as error:
            raise StorageError(f"Unable to rename problem: {error}") from error
        return destination
