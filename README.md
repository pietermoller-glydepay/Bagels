# Tues - TUI Expense Tracker

Powerful expense tracker that lives in your terminal. WIP!

## Development setup

Install uv:

```
curl -LsSf https://astral.sh/uv/install.sh | s
```

Sync packages and run dev:

```sh
uv sync
uv run textual console -x SYSTEM -x EVENT -x DEBUG -x INFO # for logging
uv run textual run --dev src/app.py # in another terminal
```
