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

## Game Rules

1. **Hidden pairs**  
   Every board starts as an axis-aligned grid of symbols with even counts so each symbol can be matched. The state rendering uses a concise textual vocabulary:

   ```
   5x5
   down _
   my A
   up A
   none _
   ```

   - `down _` — a card is present but face-down for the viewing player.  
   - `my X` — the viewing player currently controls the revealed card with label `X`.  
   - `up X` — another player controls the face-up card `X`.  
   - `none _` — the pair has been cleared and the space is empty.

2. **Flipping constraints**  
   Players may expose at most two distinct cards at a time. Attempting to flip the same square twice, flip a removed card, or flip while already controlling two cards raises an error (or, in the async API, blocks until the existing pair resolves). These rules ensure fairness and mirror the physical board game.

3. **Pair resolution**  
   After the second flip, the board schedules an asynchronous task:
   - Matching labels stay visible for `MATCH_CLEAR_DELAY_SECONDS` (0.4 s by default) and then vanish (`none _`).
   - Mismatched cards flip back down after `MISMATCH_HIDE_DELAY_SECONDS` (0.6 s by default).
   - Once resolved, the player’s control list clears so they may flip again.

4. **Map/replace actions**  
   Teaching staff can issue a `map` command that rewrites every label via an async transform. This powers administrative commands such as `/replace/A/B` and demonstrates that the Board ADT protects its rep even when bulk mutations occur.

5. **Watch notifications**  
   Clients can long-poll using the `watch` command. Each watcher blocks until the board version changes and then receives the fully rendered state, enabling responsive UIs without direct board access.

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

### Board File Format

Board definitions match the MIT starter kit:

1. First non-empty line: `HEIGHTxWIDTH` (e.g., `5x5`).  
2. Followed by `HEIGHT * WIDTH` lines containing the card labels in row-major order.  

Parsing enforces rectangularity, positive dimensions, and exact card counts so malformed input fails fast.

### Running the Server

```bash
python -m memory_scramble.server 8080 boards/ab.txt
```

- `PORT` can be `0` to auto-select a free port.
- `FILENAME` must reference a valid board description.
- The static frontend lives in `public/index.html`; open it in a browser and aim it at the running backend.

### Command Protocol & HTTP API

| HTTP Route | Underlying Command | Purpose |
| --- | --- | --- |
| `GET /look/{player}` | `look(board, player)` | Snapshot the board for a single viewer. |
| `GET /flip/{player}/{row,col}` | `flip(board, player, row, col)` | Reveal a card; enforces all flipping rules before returning the new state. |
| `GET /replace/{player}/{from}/{to}` | `map(board, player, transform)` | Apply a server-side label transform (used for teaching tools). |
| `GET /watch/{player}` | `watch(board, player)` | Block until the next board mutation and return that state. |

The FastAPI layer performs basic input validation, translates exceptions into HTTP status codes (`400` for bad input, `409` when a flip violates the rules), and streams plain-text responses so the existing static frontend can reuse its TypeScript parsing logic verbatim.

### Implementation Notes

- **Representation**: `_Card` instances track `label`, `face_up`, and `controller`. The Board never returns these objects, instead rendering strings so no client can mutate internal state.  
- **Concurrency**: An `asyncio.Condition` guards every mutation, allowing concurrent flips and watchers without data races. Pair resolution runs in background tasks stored in `_pending_resolutions` so tests can await eventual consistency.  
- **Rep checking**: `check_rep()` is invoked after every externally visible mutation to keep debugging cheap and enforce the abstraction boundary students are expected to reason about.

## Testing Strategy

Automated tests in `tests/test_board.py` exercise each rule:

- Parsing a board file, rendering the initial `look`, and confirming every card starts face-down.  
- Matching and mismatched flip flows, including their asynchronous delays.  
- Map/replace transformations and the `watch` notification channel.  
- Additional rule-coverage tests (added in this branch) assert that:
  - Players cannot flip the same square twice in a row.
  - Flips targeting removed cards are rejected once a match has cleared.
  - Attempts to flip a third card block until the prior pair resolves, demonstrating the “at most two cards” invariant.

Together these tests act as executable documentation for both the gameplay loop and the concurrency guarantees of the Python port.

## Results

![Screenshot](imgs/11.png)
![Screenshot](imgs/12.png)
![Screenshot](imgs/13.png)
![Screenshot](imgs/14.png)
![Screenshot](imgs/15.png)



## Conclusion

We successfully ported the MIT Memory Scramble lab to Python without changing its architectural contract. The Board ADT, command protocol, and HTTP façade retain their original responsibilities, enabling students to reason about representation invariants, modular design, and API layering while working in a familiar Python environment.
