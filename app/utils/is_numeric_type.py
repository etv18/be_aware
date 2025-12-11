from decimal import Decimal, InvalidOperation

def is_numeric_type(value: str) -> bool:
    try:
        Decimal(value)
        return True
    except (InvalidOperation, ValueError):
        return False
