# Tues - TUI Expense Tracker

Powerful expense tracker that lives in your terminal. WIP!

[] Add split existing id

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

### Database schema

```dbml
// Use DBML to define database structure

enum nature {
  "Want"
  "Need"
  "Must"
}

Table account {
  id integer [pk]
  name string [not null]
  beginningBalance float [not null]
  description string
  repaymentDate integer
}

Table record {
  id integer [pk]
  label string [not null]
  amount float [not null]
  date datetime [not null]
  accountId integer [ref: > account.id, not null]
  categoryId integer [ref: > category.id]
  isIncome boolean [not null, default: false]
  isTransfer boolean [not null, default: false]
  transferToAccountId integer [ref: > account.id]

  note: 'Constraints: amount > 0, (isTransfer = FALSE) OR (isIncome = FALSE)'
}

Table split {
  id integer [pk]
  recordId integer [ref: > record.id, not null]
  amount float [not null]
  personId integer [ref: > person.id, not null]
  isPaid boolean [not null, default: false]
  paidDate datetime
  accountId integer [ref: > account.id]
}

Table person {
  id integer [pk]
  name string
}

Table category {
  id integer [pk]
  parentCategoryId integer [ref: > category.id] // null if top level
  name string [not null]
  nature nature [not null]
  color string [not null]
}

// Additional relationships
Ref: record.transferToAccountId > account.id
```
