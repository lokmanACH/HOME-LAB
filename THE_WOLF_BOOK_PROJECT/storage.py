import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

FORBIDDEN_CHARS = set(r'/\:*?"<>|')
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "categories"


def get_categories_dir() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def validate_name(name: str, max_length: int, field_label: str) -> Tuple[bool, str]:
    cleaned = name.strip()
    if len(cleaned) < 1:
        return False, f"{field_label} cannot be empty."
    if len(cleaned) > max_length:
        return False, f"{field_label} cannot exceed {max_length} characters."
    if cleaned in {".", ".."}:
        return False, f"{field_label} cannot be '.' or '..'."
    for char in cleaned:
        if char in FORBIDDEN_CHARS:
            return False, f"{field_label} contains forbidden character: '{char}'"
    return True, cleaned


def validate_category_name(name: str) -> Tuple[bool, str]:
    return validate_name(name, 50, "Category name")


def validate_problem_title(title: str) -> Tuple[bool, str]:
    return validate_name(title, 80, "Problem title")


def validate_problem_description(desc: str) -> Tuple[bool, str]:
    cleaned = desc.strip()
    if len(cleaned) < 1:
        return False, "Description cannot be empty."
    if len(cleaned) > 2000:
        return False, "Description cannot exceed 2000 characters."
    return True, cleaned


def validate_command_item(desc: str, cmd: str) -> Tuple[bool, str]:
    d_clean = desc.strip()
    c_clean = cmd.strip()
    if len(d_clean) < 1:
        return False, "Command description cannot be empty."
    if len(d_clean) > 300:
        return False, "Command description cannot exceed 300 characters."
    if len(c_clean) < 1:
        return False, "Command cannot be empty."
    if len(c_clean) > 1000:
        return False, "Command cannot exceed 1000 characters."
    return True, ""


def list_categories() -> List[str]:
    cat_dir = get_categories_dir()
    try:
        entries = [
            d.name for d in cat_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]
        return sorted(entries, key=lambda s: s.lower())
    except Exception:
        return []


def category_exists_case_insensitive(name: str) -> bool:
    target = name.strip().lower()
    for cat in list_categories():
        if cat.lower() == target:
            return True
    return False


def create_category(name: str) -> Tuple[bool, str]:
    valid, result = validate_category_name(name)
    if not valid:
        return False, result
    clean_name = result
    if category_exists_case_insensitive(clean_name):
        return False, f"Category '{clean_name}' already exists."

    target_path = get_categories_dir() / clean_name
    try:
        target_path.mkdir(parents=True, exist_ok=False)
        return True, clean_name
    except Exception as e:
        return False, f"Cannot create category folder: {e}"


def delete_category(name: str) -> Tuple[bool, str]:
    cat_path = get_categories_dir() / name
    if not cat_path.exists() or not cat_path.is_dir():
        return False, f"Category '{name}' not found."
    try:
        shutil.rmtree(cat_path)
        return True, f"Category '{name}' deleted."
    except Exception as e:
        return False, f"Cannot delete category: {e}"


def list_problems(category: str) -> List[str]:
    cat_path = get_categories_dir() / category
    if not cat_path.exists() or not cat_path.is_dir():
        return []
    try:
        entries = [
            d.name for d in cat_path.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]
        return sorted(entries, key=lambda s: s.lower())
    except Exception:
        return []


def problem_exists_case_insensitive(category: str, title: str, exclude_title: Optional[str] = None) -> bool:
    target = title.strip().lower()
    exclude = exclude_title.strip().lower() if exclude_title else None
    for p in list_problems(category):
        if exclude and p.lower() == exclude:
            continue
        if p.lower() == target:
            return True
    return False


def get_problem(category: str, problem_title: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    file_path = get_categories_dir() / category / problem_title / "problem.json"
    if not file_path.exists():
        return None, f"Missing problem.json for '{problem_title}'."
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return None, "Invalid JSON structure (must be an object)."
        return data, None
    except json.JSONDecodeError:
        return None, "Invalid JSON in problem.json file."
    except Exception as e:
        return None, f"Cannot read file: {e}"


def save_problem(
    category: str,
    title: str,
    description: str,
    solution: List[Dict[str, str]],
    old_title: Optional[str] = None
) -> Tuple[bool, str]:
    valid_t, title_res = validate_problem_title(title)
    if not valid_t:
        return False, title_res
    clean_title = title_res

    valid_d, desc_res = validate_problem_description(description)
    if not valid_d:
        return False, desc_res
    clean_desc = desc_res

    if not solution or len(solution) < 1:
        return False, "A problem must contain at least one command."

    clean_solution = []
    for idx, item in enumerate(solution, 1):
        c_desc = item.get("description", "")
        c_cmd = item.get("command", "")
        valid_c, c_err = validate_command_item(c_desc, c_cmd)
        if not valid_c:
            return False, f"Command #{idx}: {c_err}"
        clean_solution.append({
            "description": c_desc.strip(),
            "command": c_cmd.strip()
        })

    cat_path = get_categories_dir() / category
    if not cat_path.exists() or not cat_path.is_dir():
        return False, f"Category '{category}' does not exist."

    if problem_exists_case_insensitive(category, clean_title, exclude_title=old_title):
        return False, f"Problem '{clean_title}' already exists in '{category}'."

    problem_dir = cat_path / clean_title

    if old_title and old_title != clean_title:
        old_dir = cat_path / old_title
        if old_dir.exists() and old_dir.is_dir():
            try:
                old_dir.rename(problem_dir)
            except Exception as e:
                return False, f"Cannot rename problem folder: {e}"
        else:
            problem_dir.mkdir(parents=True, exist_ok=True)
    else:
        problem_dir.mkdir(parents=True, exist_ok=True)

    data = {
        "title": clean_title,
        "description": clean_desc,
        "solution": clean_solution
    }

    json_path = problem_dir / "problem.json"
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True, clean_title
    except Exception as e:
        return False, f"Cannot write problem.json: {e}"


def delete_problem(category: str, problem_title: str) -> Tuple[bool, str]:
    prob_path = get_categories_dir() / category / problem_title
    if not prob_path.exists() or not prob_path.is_dir():
        return False, f"Problem '{problem_title}' not found."
    try:
        shutil.rmtree(prob_path)
        return True, f"Problem '{problem_title}' deleted."
    except Exception as e:
        return False, f"Cannot delete problem: {e}"


def search_all(query: str) -> List[Tuple[str, str, str]]:
    q = query.strip().lower()
    if not q:
        return []

    results = []
    for cat in list_categories():
        for prob in list_problems(cat):
            data, err = get_problem(cat, prob)
            if not data:
                continue

            title = data.get("title", prob)
            desc = data.get("description", "")
            solution = data.get("solution", [])

            match_reason = ""
            if q in title.lower():
                match_reason = "Matched title"
            elif q in desc.lower():
                match_reason = "Matched description"
            else:
                for cmd_item in solution:
                    c_desc = cmd_item.get("description", "")
                    c_cmd = cmd_item.get("command", "")
                    if q in c_desc.lower():
                        match_reason = f"Matched command description: {c_desc}"
                        break
                    elif q in c_cmd.lower():
                        match_reason = f"Matched command: {c_cmd}"
                        break

            if match_reason:
                results.append((cat, prob, match_reason))

    return results

