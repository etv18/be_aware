import random
from datetime import datetime

from app.extensions import db

def generate_montly_sequence(prefix, model, field_name="code"):
    now = datetime.now()
    year = now.year
    month = now.month

    while True:
        random_part = random.randint(0, 99999)
        code = f"{prefix}_{year}_{month:02d}_{random_part:05d}"

        exists = (
            db.session.query(model.id)
            .filter(getattr(model, field_name) == code)
            .first()
        )

        if not exists:
            return code

