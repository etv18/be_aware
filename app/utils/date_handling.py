from datetime import datetime, timezone

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def utcnow():
    return datetime.now(timezone.utc)

def get_years(starting_year=2020) -> list:
    current_year = int(datetime.now().year)
    years = []

    for i in range(0, ((current_year - starting_year) + 1)):
        years.append(starting_year + i)

    years.reverse()

    return years