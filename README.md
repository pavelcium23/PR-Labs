# MIT 6.102 (Spring 2025) Problem Set 4: Memory Scramble

This repository now contains a fully Python-based backend for the Memory Scramble lab. It keeps the original structure from the TypeScript starter:

- a mutable, concurrency-safe `Board` ADT with rep invariants and `check_rep()`
- a `commands` module that provides the string-based game API
- an HTTP server that only depends on the commands API

## Requirements

- Python 3.11+
- `pip` (or another PEP 517 installer)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

The optional `dev` extras install `pytest` and `httpx` for local testing.

## Running the server

The FastAPI server exposes the same routes as the TypeScript version. Start it with:

```bash
python -m memory_scramble.server 8080 boards/ab.txt
```

- `PORT` (`8080` above) may be `0` to pick an available port automatically.
- `FILENAME` must point to a valid board description such as the files in `boards/`.

The frontend remains a static page in `public/index.html`. Open it directly in a browser (or host it from any static file server) and point it at your running backend.

## Testing

```bash
pytest
```

This exercises the Python `Board` implementation asynchronously, ensuring flips, map operations, and watch semantics behave as specified.
