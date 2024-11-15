# Bagels - TUI Expense Tracker

Powerful expense tracker that lives in your terminal.

Bagels expense tracker is a TUI application where you can track and analyse your money flow, with convenience oriented features and a complete interface.

Some notable features include:

- accounts, (sub)categories, splits, transfers, records
- templates for recurring transactions
- add templated record with number keys
- clear table layout with toggable splits
- transfer to and from outside tracked accounts
- "jump mode" navigation
- less and less fields to enter per transaction, powered by transactions and input modes
- insights
- customizable keybindings and defaults, such as first day of week

## Installation

```bash
# install uv (package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# restart your terminal, or run the following command:
source $HOME/.local/bin/env # or follow instructions

# install bagels through uv
uv tool install --python 3.13 bagels
```

Usage:

```bash
bagels # start bagels
bagels --at "./" # start bagels with data stored at cd
bagels locate database # find database file path
bagels locate config # find config file path
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

## Attributions

- Heavily inspired by [posting](https://github.com/darrenburns/posting)
- Bagels is built with [textual](https://https://textual.textualize.io/)
- It's called bagels because I like bagels
