# Bagels - TUI Expense Tracker

Powerful expense tracker that lives in your terminal.

![Bagels](https://github.com/JaxxDev/bagels/raw/main/assets/preview.gif)

Bagels expense tracker is a TUI application where you can track and analyse your money flow, with convenience oriented features and a complete interface.

Some notable features include:

<details><summary>accounts, (sub)categories, splits, transfers, records</summary> You can track your money flow through different accounts, categories, and splits. You can also transfer money between your accounts and even outside tracked accounts.</details>
<details><summary>templates for recurring transactions</summary> Create templates for frequently added transactions, so you can quickly add them without typing much.</details>
<details><summary>add templated record with number keys</summary> Press a number key to quickly add a transaction based on a template.</details>
<details><summary>clear table layout with toggable splits</summary> The clear table layout makes it easy to read and understand even the most complex transactions.</details>
<details><summary>transfer to and from outside tracked accounts</summary> You can transfer money between your accounts and even outside tracked accounts.</details>
<details><summary>"jump mode" navigation</summary> Quickly navigate between different parts of the application.</details>
<details><summary>less and less fields to enter per transaction, powered by transactions and input modes</summary> The input mode system helps you quickly enter transactions by automatically selecting the right field for you to enter. And with the transaction history, you can quickly see what you entered before.</details>
<details><summary>insights</summary> Bagels provides insights in the form of charts and tables, to help you understand your money flow.</details>
<details><summary>customizable keybindings and defaults, such as first day of week</summary> You can customize the keybindings and defaults of the application to fit your needs.</details>

> Who is this for?

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

> It is recommended, but not required, to use "modern" terminals to run the app. MacOS users are recommended to use iTerm2, and Windows users are recommended to use Windows Terminal.

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

Please use the black formatter to format the code.

## Roadmap

- [] More insight displays and analysis (by nature etc.)
- [] "Processing" bool on records for transactions in process
- [] Record flags for future insights implementation
- [] Repayment reminders
- [] Code review
- [] Daily check-ins
- [] Budgets
- [] Add tests
- [] Bank sync

## Attributions

- Heavily inspired by [posting](https://github.com/darrenburns/posting)
- Bagels is built with [textual](https://https://textual.textualize.io/)
- It's called bagels because I like bagels
