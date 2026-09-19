from pathlib import Path

import pytest

from app.models.problem import Command, Problem
from app.services.filesystem import FileSystemStore, StorageError, validate_folder_name
from app.services.json_store import JsonStore


def test_name_validation() -> None:
    assert validate_folder_name("  Docker  ", 50, "Category name") == "Docker"
    with pytest.raises(StorageError):
        validate_folder_name("bad/name", 50, "Category name")
    with pytest.raises(StorageError):
        validate_folder_name("..", 50, "Category name")


def test_case_insensitive_category_collision(tmp_path: Path) -> None:
    store = FileSystemStore(tmp_path / "troubleshooting")
    store.create_category("Docker")
    with pytest.raises(StorageError, match="already exists"):
        store.create_category("docker")


def test_json_round_trip_and_command_steps(tmp_path: Path) -> None:
    problem_path = tmp_path / "troubleshooting" / "categories" / "Linux" / "Disk full"
    problem_path.mkdir(parents=True)
    problem = Problem("Disk full", "The disk is full.", [Command(99, "Check usage", "df -h")])
    JsonStore.save(problem_path, problem)
    loaded = JsonStore.load(problem_path)
    assert loaded.to_dict()["solution"][0]["step"] == 1
    assert loaded.title == "Disk full"
