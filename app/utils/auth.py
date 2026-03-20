import bcrypt

def verify_password(stored_hash, raw_password):
    return bcrypt.checkpw(raw_password.encode('utf-8'), stored_hash)