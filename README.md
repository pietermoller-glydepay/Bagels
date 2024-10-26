# Development setup

```sh
python3 -m venv ./.venv
source ./.venv/bin/activate
python3 -m pip install -r requirements.txt
```

# Database schema

```
// Use DBML to define database structure

enum nature {
  "want"
  "need"
  "must"
}

Table account {
  id integer
  name string
  beginningBalance string
  icon string
  description string
  repaymentDate datetime
}

Table record {
  id integer
  label string
  amount float
  isAllUnpaidCleared boolean
  // if all related unpaidRecord is cleared. Null if no unpaid.

  date datetime
  accountId Account
  categoryId Category
  // remember index to improve performance when implementing
}

Table unpaidRecord {
  id integer
  label string
  date datetime
  personId Person
  amount float
  recordId Record
  isCleared boolean // if person paid
  accountId Account
}

Table person {
  id integer
  name string
}

Table category {
  id integer
  parentCategoryId integer // null if top level, super cateogry's id
  name string
  nature nature
  color string
}

Ref: category.id > record.categoryId
Ref: category.parentCategoryId > category.id
Ref: unpaidRecord.recordId < record.id
Ref: record.accountId < account.id
Ref: unpaidRecord.accountId < account.id
Ref: person.id > unpaidRecord.personId
```
