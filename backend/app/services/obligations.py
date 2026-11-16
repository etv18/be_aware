"""What loans and debts have in common: both are an amount that payments chip away at, and both
turn "paid" (is_active False) once the payments cover the amount.

`payment_model` is LoanPayment / DebtPayment and `fk_column` is the column that points at the parent
(LoanPayment.loan_id / DebtPayment.debt_id).
"""
from decimal import Decimal

from sqlalchemy import func

from app.extensions import db


def total_paid(parent, payment_model, fk_column):
    return (
        db.session.query(func.sum(payment_model.amount))
        .filter(fk_column == parent.id)
        .scalar()
    ) or Decimal()


def refresh_status(parent, payments_attribute, payment_model, fk_column):
    """Flush pending payment changes, then set the parent active while payments do not cover it."""
    db.session.flush()
    db.session.expire(parent, [payments_attribute])  # the cached list of payments is stale now
    parent.is_active = (parent.amount - total_paid(parent, payment_model, fk_column)) > 0


def remaining_of(parents, payment_model, fk_column):
    """Unpaid amount over the given loans / debts, using one query for all their payments."""
    if not parents:
        return Decimal('0.0')

    paid_by_parent = dict(
        db.session.query(fk_column, func.sum(payment_model.amount))
        .filter(fk_column.in_([parent.id for parent in parents]))
        .group_by(fk_column)
        .all()
    )
    return sum((p.amount - (paid_by_parent.get(p.id) or Decimal()) for p in parents), Decimal())


def count_active_and_paid(records):
    actives = sum(1 for record in records if record.is_active)
    return {'actives': actives, 'paids': len(records) - actives}
