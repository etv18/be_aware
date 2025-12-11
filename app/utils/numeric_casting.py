from decimal import Decimal, InvalidOperation

def is_decimal_type(value: str) -> bool:
    try:
        Decimal(value)
        return True
    except (InvalidOperation, ValueError):
        return False
