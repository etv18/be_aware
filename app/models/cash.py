from app.extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Cash(db.Model):
    __tablename__ = 'cash'

    id = db.Column(db.Integer, primary_key=True)

    amount = db.Column(db.Numeric(10,2), nullable=False, default=0.00)
