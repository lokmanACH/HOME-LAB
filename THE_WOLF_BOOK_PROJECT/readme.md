# 🐺 THE WOLF BOOK

**Version:** `v1.1.0`

> A simple, keyboard-first terminal troubleshooting knowledge base.

**THE WOLF BOOK 🐺** is a lightweight TUI application for storing problems you've encountered and the commands you used to solve them.

Instead of searching for the same solution again and again, save it once and find it whenever you need it.

---

## ✨ Features

* 🐺 Keyboard-first terminal interface
* 📂 Organize troubleshooting knowledge by categories
* 📁 Each problem is stored as its own folder
* 📝 Store a problem title and description
* 🛠️ Store multiple solution steps
* 💻 Store commands for each solution step
* 🔎 Browse your troubleshooting knowledge easily
* 💾 Data stored as simple JSON files
* 🐳 Docker support
* 🖥️ Works directly in a terminal
* 🖱️ Mouse is optional

---

## 📁 Data Structure

THE WOLF BOOK uses the filesystem as its storage.

There is no database.

The structure looks like this:

```text
data/
└── categories/
    ├── Linux/
    │   ├── Permission denied/
    │   │   └── problem.json
    │   │
    │   └── Disk full/
    │       └── problem.json
    │
    ├── Docker/
    │   └── Container keeps restarting/
    │       └── problem.json
    │
    └── Nginx/
        └── Port already in use/
            └── problem.json
```

Each problem contains a `problem.json` file.

Example:

```json
{
    "title": "Container keeps restarting",
    "description": "The Docker container starts and immediately stops.",
    "solution": [
        {
            "description": "Check the container status",
            "command": "docker ps -a"
        },
        {
            "description": "Check the container logs",
            "command": "docker logs <container>"
        }
    ]
}
```

Your troubleshooting knowledge therefore remains simple, portable, and human-readable.

---

# 🚀 Getting Started

## Requirements

To run THE WOLF BOOK directly on your machine:

* Python `3.12+`
* pip
* A terminal

The project uses:

```text
Textual >= 0.80.0
```

---

## 🖥️ Run on Your Machine

### 1. Clone the project

```bash
git clone <your-repository-url>
cd THE_WOLF_BOOK_PROJECT
```

### 2. Create a virtual environment

Linux/macOS:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

The current requirement is:

```text
textual>=0.80.0
```

### 4. Start THE WOLF BOOK

```bash
python app.py
```

The TUI will open directly in your terminal.

---

# ⌨️ Keyboard Usage

THE WOLF BOOK is designed to be usable with the keyboard.

Typical navigation:

```text
↑ / ↓       Navigate
Enter       Select / Open
Esc         Back / Cancel
a           Add
e           Edit
d           Delete
?           Help
q           Quit
```

The exact available shortcuts may depend on the current screen.

The mouse is optional.

---

# 🐳 Run with Docker

THE WOLF BOOK can also run inside Docker.

The Docker image contains the application and its Python dependencies.

Your troubleshooting data should remain **outside the container**.

This means you can remove or recreate the container without losing your problems.

---

## Dockerfile

The project uses the following Dockerfile:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

---

## Build the Docker Image

From the project directory:

```bash
docker build -t the-wolf-book:v1.1.0 .
```

You can verify the image:

```bash
docker images
```

---

## Run THE WOLF BOOK with Docker

Create the data directory if it doesn't exist:

```bash
mkdir -p data/categories
```

Then run:

```bash
docker run --rm -it \
    -e TERM=xterm-256color \
    -v "$(pwd)/data:/app/data" \
    the-wolf-book:v1.1.0
```

### Why `-it`?

THE WOLF BOOK is an interactive terminal application.

```text
-i
```

keeps standard input open.

```text
-t
```

allocates a terminal.

Both are required for a proper interactive TUI experience.

---

# 💾 Docker Data Storage

The most important part of the Docker command is:

```bash
-v "$(pwd)/data:/app/data"
```

This creates a bind mount:

```text
Your Machine                     Docker Container

./data  ──────────────────────>  /app/data
```

Therefore, when THE WOLF BOOK creates a problem inside the container:

```text
/app/data/categories/Docker/
└── Container keeps restarting/
    └── problem.json
```

the file is actually stored on your machine:

```text
./data/categories/Docker/Container keeps restarting/problem.json
```

Your data does **not** depend on the lifetime of the Docker container.

---

# 🔄 Recreating the Container

You can safely remove and recreate the container.

Your data remains on your machine:

```text
data/
└── categories/
    ├── Linux/
    ├── Docker/
    └── Nginx/
```

Run the application again:

```bash
docker run --rm -it \
    -e TERM=xterm-256color \
    -v "$(pwd)/data:/app/data" \
    the-wolf-book:v1.1.0
```

Your previously saved problems will still be available.

---

# 🏗️ Project Architecture

THE WOLF BOOK intentionally keeps the architecture simple:

```text
             🐺 THE WOLF BOOK
                    │
                    ▼
             Textual TUI
                    │
                    ▼
             Filesystem Storage
                    │
                    ▼
              JSON Files
```

With Docker:

```text
┌───────────────────────────────┐
│       Docker Container        │
│                               │
│   Python + Textual + App      │
│                               │
│          /app/data             │
└───────────────┬───────────────┘
                │
           Bind Mount
                │
                ▼
┌───────────────────────────────┐
│        Your Machine           │
│                               │
│       ./data/categories/      │
│                               │
│       📝 Your knowledge       │
└───────────────────────────────┘
```

---

# 📦 Version

Current version:

```text
v1.1.0
```

---

# 🐺 THE WOLF BOOK

**Build your own troubleshooting knowledge.**

> Encounter it once.
> Solve it once.
> Remember it forever. 🐺
