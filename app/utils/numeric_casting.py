from decimal import Decimal, InvalidOperation

def is_decimal_type(value: str) -> bool:
    try:
        Decimal(value)
        return True
    except (InvalidOperation, ValueError):
        return False

def total_amount(obj_list):
        total = Decimal()
        for o in obj_list:
            total += o.amount
        return f'DOP {total:,.2f}'