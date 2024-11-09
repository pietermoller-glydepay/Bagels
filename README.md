 # Tues - TUI Expense Tracker

Powerful expense tracker that lives in your terminal. WIP!

<img width="1637" alt="Screenshot 2024-11-09 at 8 55 41 PM" src="https://github.com/user-attachments/assets/1813fec6-55ae-412b-8e36-69d3de587f69">

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
