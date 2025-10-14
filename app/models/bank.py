from app.extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Bank(db.Model):
    __tablename__ = 'banks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())   

    bank_accounts = relationship('BankAccount', back_populates='bank')
    credit_cards = relationship('CreditCard', back_populates='bank')

    @classmethod
    def get_all(cls):
        result_set = cls.query.all()
        records = []

        for e in result_set:
            records.append(e)

        return records
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter(cls.id == id).first()