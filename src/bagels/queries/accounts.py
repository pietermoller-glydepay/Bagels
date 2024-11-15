from datetime import datetime
from sqlalchemy.orm import sessionmaker

from bagels.models.account import Account
from bagels.models.record import Record
from bagels.models.split import Split
from bagels.models.database.app import db_engine

Session = sessionmaker(bind=db_engine)


def get_account_balance(accountId):
    """Returns the net balance of an account.

    Rules:
    - Consider all record "account" and split "account"
    - Records with isTransfer should consider both "account" and "transferToAccount"
    - Records and splits should be considered separately, unlike net figures which consider records and splits together.

    Args:
        accountId (int): The ID of the account to get the blaance
    """
    session = Session()
    # Initialize balance
    balance = (
        session.query(Account).filter(Account.id == accountId).first().beginningBalance
    )

    # Get all records for this account
    records = session.query(Record).filter(Record.accountId == accountId).all()

    # Calculate balance from records
    for record in records:
        if record.isTransfer:
            # For transfers, subtract full amount (transfers out)
            balance -= record.amount
        elif record.isIncome:
            # For income records, add full amount
            balance += record.amount
        else:
            # For expense records, subtract full amount
            balance -= record.amount

    # Get all records where this account is the transfer destination
    transfer_to_records = (
        session.query(Record)
        .filter(Record.transferToAccountId == accountId, Record.isTransfer == True)
        .all()
    )

    # Add transfers into this account
    for record in transfer_to_records:
        balance += record.amount

    # Get all splits where this account is specified
    splits = session.query(Split).filter(Split.accountId == accountId).all()

    # Add paid splits (they represent money coming into this account)
    for split in splits:
        if split.isPaid:
            balance += split.amount

    return round(balance, 2)


def create_account(data):
    session = Session()
    try:
        new_account = Account(**data)
        session.add(new_account)
        session.commit()
        return new_account
    finally:
        session.close()


def _get_base_accounts_query(session, get_hidden=False):
    query = session.query(Account).filter(Account.deletedAt.is_(None))
    if not get_hidden:
        query = query.filter(Account.hidden.is_(False))
    else:
        query = query.order_by(Account.hidden)
    return query


def get_all_accounts(get_hidden=False):
    session = Session()
    try:
        return _get_base_accounts_query(session, get_hidden).all()
    finally:
        session.close()


def get_accounts_count(get_hidden=False):
    session = Session()
    try:
        return _get_base_accounts_query(session, get_hidden).count()
    finally:
        session.close()


def get_all_accounts_with_balance(get_hidden=False):
    session = Session()
    try:
        accounts = _get_base_accounts_query(session, get_hidden).all()
        for account in accounts:
            account.balance = get_account_balance(account.id)
        return accounts
    finally:
        session.close()


def get_account_balance_by_id(account_id):
    session = Session()
    try:
        return get_account_balance(account_id)
    finally:
        session.close()


def get_account_by_id(account_id):
    session = Session()
    try:
        return session.query(Account).get(account_id)
    finally:
        session.close()


def update_account(account_id, data):
    session = Session()
    try:
        account = session.query(Account).get(account_id)
        if account:
            for key, value in data.items():
                setattr(account, key, value)
            session.commit()
        return account
    finally:
        session.close()


def delete_account(account_id):
    session = Session()
    try:
        account = session.query(Account).get(account_id)
        if account:
            account.deletedAt = datetime.now()
            session.commit()
            session.refresh(account)
            session.expunge(account)
            return True
    finally:
        session.close()
