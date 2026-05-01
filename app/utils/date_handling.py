from datetime import datetime, timezone

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def utcnow():
    return datetime.now(timezone.utc)

def get_years(starting_year=2025) -> list:
    current_year = int(datetime.now().year)
    years = []

    for i in range(0, ((current_year - starting_year) + 1)):
        years.append(starting_year + i)

    years.reverse()

    return years


def format_datetime_filter(value, format_str="%a, %d %b %Y %I:%M %p"):
    """
    Custom Jinja filter to format datetime objects.
    Default format: Fri, 01 May 2026 04:45 PM
    """
    if value is None:
        return ""
    
    # If it's a string (from some databases), try to parse it first
    if isinstance(value, str):
        # Adjust the format here if your DB returns a specific string format
        value = datetime.fromisoformat(value)
        
    return value.strftime(format_str)
