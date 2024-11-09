from datetime import datetime, timedelta

from sqlalchemy import func

from models.database.app import get_app
from models.database.db import db
from models.record import Record
from models.split import Split

app = get_app()


#region period
# -------------- period -------------- #
def _get_start_end_of_year(offset: int = 0):
    now = datetime.now()
    target_year = now.year + offset
    return datetime(target_year, 1, 1), datetime(target_year, 12, 31)

def _get_start_end_of_month(offset: int = 0):
    now = datetime.now()
    # Calculate target month and year
    target_month = now.month + offset
    target_year = now.year + (target_month - 1) // 12
    target_month = ((target_month - 1) % 12) + 1
    
    # Calculate next month and year for end date
    next_month = target_month + 1
    next_year = target_year + (next_month - 1) // 12
    next_month = ((next_month - 1) % 12) + 1
    
    start_of_month = datetime(target_year, target_month, 1)
    end_of_month = datetime(next_year, next_month, 1) - timedelta(microseconds=1)
    
    return start_of_month, end_of_month

def _get_start_end_of_week(offset: int = 0):
    now = datetime.now()
    # Apply offset in weeks
    now = now + timedelta(weeks=offset)
    start_of_week = now - timedelta(days=now.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week

def _get_start_end_of_day(offset: int = 0):
    now = datetime.now()
    # Apply offset in days
    now = now + timedelta(days=offset)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1) - timedelta(microseconds=1)
    return start_of_day, end_of_day

def get_start_end_of_period(offset: int = 0, offset_type: str = "month"):
    match offset_type:
        case "year":
            return _get_start_end_of_year(offset)
        case "month":
            return _get_start_end_of_month(offset)
        case "week":
            return _get_start_end_of_week(offset)
        case "day":
            return _get_start_end_of_day(offset)


#region net
# ---------------- net --------------- #

def get_period_net(accountId=None, offset_type=None, offset=None, isIncome=None):
    with app.app_context():
        query = db.session.query(Record)
        
        if offset_type and offset is not None:
            start_of_period, end_of_period = get_start_end_of_period(offset, offset_type)
            query = query.filter(Record.date >= start_of_period,
                            Record.date < end_of_period)

        income_filter = [Record.isIncome.is_(True)]
        expense_filter = [Record.isIncome.is_(False), Record.isTransfer.is_(False)]
        transfer_received_filter = [Record.isTransfer.is_(True)]
        transfer_sent_filter = [Record.isTransfer.is_(True)]
        
        if accountId is not None:
            income_filter.append(Record.accountId == accountId)
            expense_filter.append(Record.accountId == accountId)
            transfer_received_filter.append(Record.transferToAccountId == accountId)
            transfer_sent_filter.append(Record.accountId == accountId)

        total_income = query.with_entities(func.sum(Record.amount)).filter(
            *income_filter
        ).scalar() or 0

        total_expense = query.with_entities(func.sum(Record.amount)).filter(
            *expense_filter
        ).scalar() or 0
        
        total_transfer_received = query.with_entities(func.sum(Record.amount)).filter(
            *transfer_received_filter
        ).scalar() or 0
        
        total_transfer_sent = query.with_entities(func.sum(Record.amount)).filter(
            *transfer_sent_filter
        ).scalar() or 0

        splits_query = db.session.query(Split)
        if offset_type and offset is not None:
            splits_query = splits_query.filter(
                Split.paidDate >= start_of_period,
                Split.paidDate < end_of_period
            )
        
        split_received_filter = [Record.isIncome.is_(False)]
        split_sent_filter = [Record.isIncome.is_(True)]
        
        if accountId is not None:
            split_received_filter.append(Split.accountId == accountId)
            split_sent_filter.append(Split.accountId == accountId)
        
        total_split_received = splits_query.join(Record).with_entities(func.sum(Split.amount)).filter(
            *split_received_filter
        ).scalar() or 0
        
        total_split_sent = splits_query.join(Record).with_entities(func.sum(Split.amount)).filter(
            *split_sent_filter
        ).scalar() or 0
        
        match isIncome:
            case True:
                result = total_income - total_split_sent
            case False:
                result = total_expense - total_split_received
            case None: # result = net
                result = total_income \
                    - total_expense \
                    + total_transfer_received \
                    - total_transfer_sent \
                    + total_split_received \
                    - total_split_sent
        return round(result, 2)

#region average
# -------------- average ------------- #

def _get_days_in_period(offset: int = 0, offset_type: str = "month"):
    start_of_period, end_of_period = get_start_end_of_period(offset, offset_type)
    days = (end_of_period - start_of_period).days + 1
    return days

def get_period_average(net: int = 0, offset: int = 0, offset_type: str = "month"):
        days = _get_days_in_period(offset, offset_type)
        return round(net / days, 2)