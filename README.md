# Bagels - TUI Expense Tracker

[[HEAVY WIP]] Powerful expense tracker that lives in your terminal.

<img width="1637" alt="Screenshot 2024-11-09 at 8 55 41 PM" src="https://github.com/user-attachments/assets/1813fec6-55ae-412b-8e36-69d3de587f69">

## Install

```bash
# install uv (package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
# add bin to PATH
source $HOME/.local/bin/env # or follow instructions
# install bagels
uv tool install --python 3.13 bagels
```

## Development setup

```sh
git clone https://github.com/EnhancedJax/Bagels.git
cd Bagels
uv sync
mkdir instance
uv run bagels --at "./instance/" # runs app with storage in ./instance/
# alternatively, use textual dev mode to catch prints
uv run textual run --dev "./src/bagels/textualrun.py"
uv run textual console -x SYSTEM -x EVENT -x DEBUG -x INFO # for logging
```

- Please use the black formatter to format the code.
