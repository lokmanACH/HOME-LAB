from __future__ import annotations

import json
from pathlib import Path

from app.models.problem import Problem
from app.services.filesystem import StorageError


class JsonStore:
    @staticmethod
    def load(problem_path: Path) -> Problem:
        file_path = problem_path / "problem.json"
        try:
            with file_path.open("r", encoding="utf-8") as stream:
                return Problem.from_dict(json.load(stream))
        except FileNotFoundError as error:
            raise StorageError("Missing problem.json.") from error
        except json.JSONDecodeError as error:
            raise StorageError("Unable to read problem.json. The JSON file may be corrupted.") from error
        except OSError as error:
            raise StorageError(f"Unable to read problem.json: {error}") from error
        except ValueError as error:
            raise StorageError(f"Unable to read problem.json: {error}") from error

    @staticmethod
    def save(problem_path: Path, problem: Problem) -> None:
        file_path = problem_path / "problem.json"
        temporary_path = problem_path / ".problem.json.tmp"
        try:
            with temporary_path.open("w", encoding="utf-8") as stream:
                json.dump(problem.to_dict(), stream, indent=2, ensure_ascii=False)
                stream.write("\n")
            temporary_path.replace(file_path)
        except OSError as error:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise StorageError(f"Unable to write problem.json: {error}") from error
