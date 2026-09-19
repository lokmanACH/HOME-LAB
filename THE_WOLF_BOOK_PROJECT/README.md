# Troubleshooting Terminal

A keyboard-first Textual TUI for a personal troubleshooting knowledge base.

## Requirements

- Python 3.10+
- A terminal with keyboard input

## Install and run

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m app.main
```

The default data directory is `data/categories/`. Override it in Python by passing a different `data_root` to `TroubleshootingTerminal`.

## Storage

Each category is a directory. Each problem is a directory inside its category, and each problem directory contains one indented `problem.json` file. Directory names are the user-facing category and problem names; no IDs or slugs are generated.

## Keyboard

Use arrow keys and Enter to navigate. `a` adds, `e` edits a selected command, `d` deletes with confirmation where destructive, `u` and `j` reorder commands, `c` copies a command, `/` searches, `?` opens help, `Esc` goes back, and `q` quits.
