# Memory Scramble Lab Report

## Introduction

This repository hosts a Python implementation of the MIT 6.102 (Spring 2025) Memory Scramble lab. Starting from the official TypeScript skeleton, we re-created the full backend stack—`Board` ADT, command layer, and HTTP interface—while preserving the original API surface so the provided frontend continues to function unchanged.

## Objectives

- Re-implement the starter’s mutable Board ADT in Python with clear rep invariants and `check_rep()` enforcement.
- Port the string-based command handlers so the HTTP layer never talks to the Board directly.
- Deliver an HTTP API (FastAPI) that mirrors the TypeScript routes and remains compatible with the static frontend.
- Provide a small suite of automated tests that capture the specified Board behaviors (flips, maps, watches).

## Theory

Memory Scramble models a board filled with symbols that players flip to discover matching pairs. The Board ADT therefore maintains:

- a grid of concealed symbols and their revealed states,
- a watch/notify mechanism for subscribers,
- invariants ensuring symbols remain balanced and state transitions follow the spec.

Commands form a pure textual protocol (e.g., `"flip x y"`, `"map"`). The server is a thin translation layer that exposes HTTP endpoints directly tied to these commands, ensuring clear separation of concerns:

```
HTTP request -> commands module -> Board ADT
```

## Implementation

### Environment

- Python 3.11+
- `pip` (any PEP 517 installer)

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]   # installs FastAPI, pytest, httpx, etc.
```

### Components

- `memory_scramble/board.py`: concurrency-safe Board with rep invariants, snapshotting, and `check_rep()` calls.
- `memory_scramble/commands.py`: parses the textual commands, delegates to Board operations, and returns protocol-compliant strings.
- `memory_scramble/server.py`: FastAPI routes that validate inputs, invoke command functions, and stream responses to clients.
- `boards/*.txt`: sample board definitions identical in format to the starter kit.

### Running the Server

```bash
python -m memory_scramble.server 8080 boards/ab.txt
```

- `PORT` can be `0` to auto-select a free port.
- `FILENAME` must reference a valid board description.
- The static frontend lives in `public/index.html`; open it in a browser and aim it at the running backend.

## Results

- End-to-end lab workflow now runs entirely in Python while satisfying the structural constraints of the original assignment.
- Automated tests (`pytest`) validate Board semantics, ensuring flips, matching logic, and watch notifications behave per spec.
- The HTTP API passes manual smoke tests using the provided frontend and command-line clients (`httpx`, `curl`).

## Conclusion

We successfully ported the MIT Memory Scramble lab to Python without changing its architectural contract. The Board ADT, command protocol, and HTTP façade retain their original responsibilities, enabling students to reason about representation invariants, modular design, and API layering while working in a familiar Python environment.
