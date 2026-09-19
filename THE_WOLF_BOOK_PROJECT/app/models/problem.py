from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Command:
    step: int
    description: str
    command: str

    def to_dict(self) -> dict[str, object]:
        return {"step": self.step, "description": self.description, "command": self.command}


@dataclass
class Problem:
    title: str
    description: str
    solution: list[Command] = field(default_factory=list)

    def renumber(self) -> None:
        for index, command in enumerate(self.solution, start=1):
            command.step = index

    def to_dict(self) -> dict[str, object]:
        self.renumber()
        return {
            "title": self.title,
            "description": self.description,
            "solution": [command.to_dict() for command in self.solution],
        }

    @classmethod
    def from_dict(cls, data: object) -> Problem:
        if not isinstance(data, dict):
            raise ValueError("problem.json must contain an object")
        title = data.get("title")
        description = data.get("description")
        solution = data.get("solution")
        if not isinstance(title, str) or not isinstance(description, str) or not isinstance(solution, list):
            raise ValueError("problem.json has an invalid structure")
        commands: list[Command] = []
        for item in solution:
            if not isinstance(item, dict):
                raise ValueError("problem.json contains an invalid command")
            command = item.get("command")
            command_description = item.get("description")
            if not isinstance(command, str) or not isinstance(command_description, str):
                raise ValueError("problem.json contains an invalid command")
            commands.append(Command(len(commands) + 1, command_description, command))
        return cls(title, description, commands)


def validate_problem(title: str, description: str, commands: list[Command]) -> list[str]:
    errors: list[str] = []
    if not title.strip() or len(title.strip()) > 80:
        errors.append("Title must be between 1 and 80 characters.")
    if not description.strip() or len(description) > 2000:
        errors.append("Description must be between 1 and 2000 characters.")
    if not commands:
        errors.append("Add at least one command before saving.")
    for index, item in enumerate(commands, start=1):
        if not item.description.strip() or len(item.description) > 300:
            errors.append(f"Command {index} description must be between 1 and 300 characters.")
        if not item.command.strip() or len(item.command) > 1000:
            errors.append(f"Command {index} must be between 1 and 1000 characters.")
    return errors
