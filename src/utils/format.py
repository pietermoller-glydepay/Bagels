from datetime import datetime, timedelta


def format_date_to_readable(date):
    today = datetime.now().date()
    if date.date() == today:
        return "Today"
    elif date.date() == today - timedelta(days=1):
        return "Yesterday"
    elif date.date() >= today - timedelta(days=today.weekday()):
        return date.strftime("%A")
    else:
        return date.strftime("%d-%m")