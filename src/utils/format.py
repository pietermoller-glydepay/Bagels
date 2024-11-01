from datetime import datetime, timedelta


def format_date_to_readable(date):
    today = datetime.now().date()
    date = date.date() if isinstance(date, datetime) else date
    
    if date == today:
        return "Today"
    elif date == today - timedelta(days=1):
        return "Yesterday"
    
    # Get start of current week (Monday)
    start_of_week = today - timedelta(days=today.weekday())
    # Get end of current week (Sunday) 
    end_of_week = start_of_week + timedelta(days=6)
    
    if start_of_week <= date <= end_of_week:
        return date.strftime("%A")
    else:
        return date.strftime("%d-%m")