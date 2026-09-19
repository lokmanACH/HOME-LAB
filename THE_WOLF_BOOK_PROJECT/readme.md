# 🐺 THE WOLF BOOK

**Version:** `v1.1.0`

> A simple, keyboard-first terminal troubleshooting knowledge base.

**THE WOLF BOOK 🐺** is a lightweight TUI application for saving and organizing troubleshooting knowledge.

When you encounter a problem, you can save:

* The problem title
* A description of the problem
* Multiple solution steps
* Commands used to solve the problem

Problems are organized into categories using folders, and each problem is stored as a JSON file.

The goal is simple:

> **Solve it once. Remember it forever. 🐺**

---

## ✨ Features

* 🐺 Keyboard-first terminal interface
* ⌨️ Designed to work without a mouse
* 📂 Organize problems by categories
* 📁 Each category is a folder
* 📁 Each problem is a folder
* 📝 Store problem title and description
* 🛠️ Store multiple solution steps
* 💻 Store commands for every solution step
* 🔎 Browse your troubleshooting knowledge
* 💾 Simple JSON-based storage
* 🐳 Docker support
* 📦 Available as a Docker image
* 🖥️ Works directly in a terminal

---

# 🏗️ How It Works

THE WOLF BOOK does not use a database.

Your filesystem is the knowledge base.

The structure is:

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

Each category is represented by a directory.

Each problem is represented by a directory.

Each problem contains a `problem.json` file.

For example:

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

This makes your troubleshooting knowledge:

* Simple
* Portable
* Human-readable
* Easy to back up
* Easy to move between machines

---

# 🚀 Getting Started

## Requirements

To run THE WOLF BOOK directly on your machine, you need:

* Python `3.12+`
* pip
* A terminal

The project uses:

```text
Textual >= 0.80.0
```

---

# 🖥️ Run on Your Machine

## 1. Clone the repository

```bash
git clone <your-repository-url>
cd THE_WOLF_BOOK_PROJECT
```

Replace `<your-repository-url>` with the actual repository URL.

---

## 2. Create a virtual environment

### Linux / macOS

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

### Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

The current dependency is:

```text
textual>=0.80.0
```

---

## 4. Run THE WOLF BOOK

```bash
python app.py
```

The TUI will open directly inside your terminal.

---

# ⌨️ Keyboard First

THE WOLF BOOK is designed to be used primarily with the keyboard.

Typical controls include:

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

The exact shortcuts can depend on the current screen.

The mouse is optional.

You can use THE WOLF BOOK in a minimal terminal environment without depending on a graphical desktop.

---

# 🐳 Docker

THE WOLF BOOK can also run inside Docker.

There are two ways to use Docker:

1. Build the image yourself
2. Pull the published image from Docker Hub

The application is designed so that your troubleshooting data remains **outside the container**.

---

# 🐳 Option 1 — Build the Docker Image

The project includes a `Dockerfile`.

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

Build the image:

```bash
docker build -t the-wolf-book:v1.1.0 .
```

Check that the image exists:

```bash
docker images
```

---

## Run the locally built image

Create the data directory:

```bash
mkdir -p data/categories
```

Run:

```bash
docker run --rm -it \
    -e TERM=xterm-256color \
    -v "$(pwd)/data:/app/data" \
    the-wolf-book:v1.1.0
```

THE WOLF BOOK will now run inside your terminal.

---

# 📦 Option 2 — Docker Hub

You can run the published version directly from Docker Hub without cloning the source code or building the image.

## 1. Pull the image

```bash
docker pull lokman2/the_wolf_book:v1.1.0
```

## 2. Create your data directory

```bash
mkdir -p data/categories
```

## 3. Run THE WOLF BOOK

```bash
docker run --rm -it \
    -e TERM=xterm-256color \
    -v "$(pwd)/data:/app/data" \
    lokman2/the_wolf_book:v1.1.0
```

That's it.

You can now use THE WOLF BOOK from your terminal.

---

# 💾 Docker Data Storage

Your troubleshooting data is stored on **your machine**, not inside the Docker container.

The important part of the Docker command is:

```bash
-v "$(pwd)/data:/app/data"
```

This creates a bind mount:

```text
YOUR MACHINE                    CONTAINER

./data  ─────────────────────>  /app/data
```

For example, if THE WOLF BOOK creates this inside the container:

```text
/app/data/categories/
└── Docker/
    └── Port already in use/
        └── problem.json
```

the actual file is stored on your machine:

```text
./data/categories/
└── Docker/
    └── Port already in use/
        └── problem.json
```

So your data remains available even after the container is removed.

---

# 🔄 Recreate the Container

You can safely remove and recreate the container.

Your data will remain on your machine.

For example:

```bash
docker run --rm -it \
    -e TERM=xterm-256color \
    -v "$(pwd)/data:/app/data" \
    lokman2/the_wolf_book:v1.1.0
```

Your existing categories and problems will still be available.

---

# 📁 Data Portability

Because THE WOLF BOOK stores its knowledge as folders and JSON files, you can easily back up your data.

For example:

```bash
cp -r data data-backup
```

Or copy the `data` directory to another machine.

You can also keep it in a Git repository if you want to version your troubleshooting knowledge.

---

# 🏗️ Architecture

THE WOLF BOOK intentionally keeps the architecture simple.

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
┌──────────────────────────────────┐
│          Docker Container        │
│                                  │
│      Python + Textual + App      │
│                                  │
│            /app/data             │
└────────────────┬─────────────────┘
                 │
                 │ Bind Mount
                 ▼
┌──────────────────────────────────┐
│           Your Machine           │
│                                  │
│         ./data/categories/       │
│                                  │
│       📝 Your knowledge          │
└──────────────────────────────────┘
```

---

# 📦 Project Version

Current version:

```text
v1.1.0
```

Docker image:

```text
lokman2/the_wolf_book:v1.1.0
```

---

# 🐺 THE WOLF BOOK

A personal terminal knowledge base for the problems you encounter while working with technology.

```text
Encounter it.
     ↓
Solve it.
     ↓
Save it.
     ↓
Find it when you need it.
```

**Solve it once. Remember it forever. 🐺**
