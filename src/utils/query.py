from datetime import datetime, timedelta


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
