from contextlib import contextmanager

from app.extensions import db


def save(commit=True):
    """Finish a database write.

    commit=True  -> commit right away (what the ledger models always did).
    commit=False -> only flush, so the caller can finish several writes as one unit and
                    commit (or roll back) once at the end.
    """
    if commit:
        db.session.commit()
    else:
        db.session.flush()


@contextmanager
def atomic():
    """Run a block as one database transaction: commit once at the end, roll back if anything fails.

        with atomic():
            ...every write that must succeed or fail together...
    """
    try:
        yield
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
