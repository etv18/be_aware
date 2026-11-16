def normalize_string(value: str) -> str:
    value = value.replace('_', ' ')
    
    return value[:-1].upper() if value.lower().endswith('s') else value.upper()

