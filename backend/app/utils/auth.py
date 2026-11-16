import bcrypt


def verify_password(stored_hash, raw_password):
    """True when `raw_password` matches the bcrypt hash. A missing or malformed hash never matches."""
    if not stored_hash or not raw_password:
        return False

    try:
        return bcrypt.checkpw(raw_password.encode('utf-8'), stored_hash)
    except (ValueError, TypeError):
        return False
