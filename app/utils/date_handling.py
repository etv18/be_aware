from datetime import datetime, timezone

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def utcnow():
    return datetime.now(timezone.utc)