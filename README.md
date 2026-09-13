# 🌙 July Ruby IDE

<img src="https://github.com/ulsidae/July-Ruby-IDE/blob/main/img/img.jpg" height="400"/>

> A lightweight Ruby IDE for learning, experimenting, and understanding how code execution works.

**July Ruby IDE** is a lightweight Ruby development environment built with Python and Tkinter.

Instead of trying to compete with full-scale IDEs, this project focuses on something simpler:

> **Write Ruby → run it → observe the process → interact with it.**

It was created as an experimental learning project to explore how a small coding environment can connect an editor, a local interpreter, and an interactive terminal.

🌐 [日本語版 (Japanese Version)](https://github.com/ulsidae/July-Ruby-IDE/blob/main/README.ja.md)

---

## 📖 Contents

| 📚 Table of Contents |
| :--- |
|[✨ Features](#-features) |
| [⚙️ Architecture](#️-architecture) |
| [🧠 Engineering Lessons](#-engineering-lessons) |
| [🎯 Why build another Ruby IDE?](#-why-build-another-ruby-ide) |
| [🎨 Design Philosophy](#-design-philosophy) |
| [🛠️ Built With](#️-built-with) |
| [🚀 Run](#-run) |
| [📌 Limitations](#-limitations) |
| [🌙 Why "July"?](#-why-july) |
| [🧪 Project Status](#-project-status) |
| [🧠 Core Insight](#-core-insight) |
| [🌙 Author](#-author) |

---

## ✨ Features

### 📝 Code Editor

* Lightweight editor built with **Tkinter**
* Ruby syntax highlighting
* Undo support
* Adjustable editor font size
* Tab-based indentation

### 💡 Autocomplete

Basic autocomplete for commonly used Ruby syntax and methods.

Suggestions currently cover:

* Ruby keywords
* Object-oriented programming methods
* I/O methods
* Enumerable methods
* String methods
* Array methods
* Hash methods
* Numeric methods
* Type conversion methods
* Proc / Lambda methods
* Miscellaneous Ruby methods

Autocomplete can be accepted with:

* `Tab`
* `Enter`
* Double-click

---

### ▶️ Interactive Ruby Execution

Ruby code is executed through the **local Ruby interpreter** installed on the system.

The IDE provides:

* ▶ Run
* ■ Stop
* Real-time output
* Error output
* Interactive standard input
* Process exit status

Ruby programs using `gets` can therefore receive input directly from the IDE.

```ruby
puts "What is your name?"

name = gets.chomp

puts "Hello, #{name}!"
```

---

### 💻 Built-in Terminal

The IDE includes an integrated terminal for interacting with the running Ruby process.

You can:

* View program output in real time
* Send input to `stdin`
* Monitor process status
* Adjust terminal font size

The terminal can also be detached into a separate window.

---

### 🪟 Detachable Terminal

Don't want the terminal inside the IDE?

Click:

**Detach Terminal**

The terminal opens in a separate window while remaining connected to the same running Ruby process.

You can later restore it with:

**Attach Terminal**

---

### 📂 File Management

Basic Ruby source file support:

* Save `.rb` files
* Load `.rb` files
* Edit and execute source code directly

---

## ⚙️ Architecture

July Ruby IDE intentionally keeps its execution pipeline simple.

```
┌──────────────────────┐
│      Ruby Editor     │
│      Tkinter Text    │
└──────────┬───────────┘
           │
           │ Run
           ▼
┌──────────────────────┐
│   Temporary .rb File │
└──────────┬───────────┘
           │
           │ subprocess.Popen()
           ▼
┌──────────────────────┐
│   Local Ruby Runtime │
└──────────┬───────────┘
           │
       stdout / stderr
           │
           ▼
┌──────────────────────┐
│     Output Queue     │
│  threading + queue   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Integrated Terminal │
└──────────────────────┘
```

The Ruby interpreter runs as a separate process.

Python communicates with that process through:

* `subprocess`
* `stdin`
* `stdout`
* `stderr`
* `threading`
* `queue`

The output-reading work is handled outside the Tkinter main thread, allowing the UI to remain responsive while Ruby is running.

---

## 🧠 Engineering Lessons

July Ruby IDE started as a relatively simple Ruby code runner.

However, making it behave like an interactive development environment introduced a different set of engineering problems.

### From Code Execution to Process Management

Initially, the basic execution model was straightforward:

```text
Source Code
    ↓
Temporary .rb File
    ↓
Ruby Interpreter
    ↓
Output
```

This was enough to execute Ruby code, but it was not enough for interactive programs.

Once features such as `gets`, real-time output, and process termination became requirements, the Ruby interpreter had to be treated as a **running process**, not simply as a command that returns a result.

The implementation therefore had to handle:

* Process creation and termination
* Standard input communication
* Real-time `stdout` and `stderr` handling
* Background output processing
* Communication between the worker thread and the Tkinter UI
* Process status and exit handling

This changed the project's central question from:

> **"Can I run this Ruby code?"**

to:

> **"Can I manage and interact with a running Ruby program?"**

### Concurrency Driven by a Real Problem

The Ruby process can continue producing output while the GUI needs to remain responsive.

Reading process output directly from the Tkinter main thread could block the interface, so July Ruby IDE uses a background thread to read the process output and a `queue.Queue` to pass that data back to the UI.

```text
Ruby Process
     ↓
stdout / stderr
     ↓
Background Thread
     ↓
Output Queue
     ↓
Tkinter Main Thread
     ↓
Terminal
```

The important lesson was not simply learning how to use threads.

It was learning to introduce concurrency **because the application had a concrete responsiveness problem that needed to be solved**.

### Redefining "Working"

The project also changed how I define whether software is actually working.

A Ruby program producing the expected output is only one part of correctness.

For an interactive development environment, the system must also:

* Remain responsive while code is running
* Display output as it is produced
* Accept user input
* Handle errors
* Allow the process to be stopped
* Keep the terminal and process state synchronized

In other words:

> **A program running successfully is not the same as an application behaving correctly while it runs.**

### Learning Through Constraints

July Ruby IDE deliberately keeps its technology stack small instead of relying on a language server or other heavyweight tooling.

This introduced limitations, but it also made the underlying execution model easier to understand.

Instead of hiding process management behind abstractions, I had to explicitly deal with:

* OS-level processes
* Standard streams
* Thread boundaries
* UI responsiveness
* Temporary source files
* Process lifecycle

The project therefore became less about building a feature-complete IDE and more about understanding the systems underneath one.

---

## 🎯 Why build another Ruby IDE?

There are already excellent Ruby development environments.

This project isn't intended to replace them.

The purpose was to understand what happens **between pressing "Run" and seeing program output**.

Instead of hiding the execution process behind an IDE, July Ruby IDE keeps the pipeline relatively visible:

```text
Source Code
    ↓
Temporary Ruby File
    ↓
Ruby Process
    ↓
stdin / stdout / stderr
    ↓
Terminal
```

Building the tool itself became part of learning Ruby and developer tooling.

---

## 🎨 Design Philosophy

July Ruby IDE deliberately avoids becoming a feature-heavy IDE.

The goal is not:

> "Build another RubyMine."

The goal is:

> **"Build just enough IDE to understand what an IDE actually does."**

The project therefore favors:

* Simplicity over feature count
* Visibility over abstraction
* Local execution over remote services
* Experimentation over production workflows

It is closer to a **Ruby playground with an IDE-shaped interface** than a professional Ruby development environment.

---

## 🛠️ Built With

* **Python**
* **Tkinter**
* **Ruby**
* `subprocess`
* `threading`
* `queue`
* `re`

No external Python GUI framework is required.

---

## 🚀 Run

### Requirements

* Windows
* Python 3.x
* Ruby

Ruby must be installed and available on the system.

The IDE automatically attempts to locate the Ruby executable using:

1. System `PATH`
2. Common Ruby installation directories
3. Known Ruby Windows installation paths

### Run from Source

```bash
python main.py
```

Source:

🍯 [main.py](https://github.com/ulsidae/July-Ruby-IDE/blob/main/main.py)

---

## 📌 Limitations

July Ruby IDE is an experimental and educational project.

It is **not** intended to replace professional Ruby development environments.

Current limitations include:

* Basic syntax highlighting rather than a full Ruby parser
* Basic autocomplete rather than language-server-based completion
* No debugging interface
* No project management system
* No integrated gem management
* No Ruby language server integration
* Windows-oriented Ruby executable detection

For larger Ruby projects, a full-featured environment such as VS Code or RubyMine is recommended.

---

## 🌙 Why "July"?

The project was originally started in June.

It was named **July Ruby IDE** because Ruby is the birthstone for July.

A small coincidence turned into the project's name.

---

## 🧪 Project Status

**Educational**

The project is intentionally small and may not grow into a full-scale IDE.

Its main purpose is to experiment with:

* Developer tooling
* Code execution
* Process management
* Interactive terminals
* Syntax highlighting
* Autocomplete
* Lightweight GUI development

---

## 🧠 Core Insight

July Ruby IDE started with a simple question:

> **"What actually happens when I press Run?"**

The answer became a small software project.

The editor is only the surface.

Underneath it is a chain of processes:

```
Code
 ↓
Editor
 ↓
Python
 ↓
Operating System
 ↓
Ruby Process
 ↓
stdin / stdout / stderr
 ↓
Terminal
```

Understanding that chain is the real purpose of this project.

More importantly, the project taught me to treat limitations as **engineering problems to investigate**, rather than simply documenting them as limitations.

> **An idea is only the beginning. Engineering begins when you try to make it work.**

---

## 🌙 Author

Built by **ulsidae**.

A small experiment in building developer tools from scratch.
