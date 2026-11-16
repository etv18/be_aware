class RecordNotFound(Exception):
    """The record the caller asked for does not exist."""
    pass


class LoanAlreadyPaid(Exception):
    """A payment was attempted on a loan whose payments already cover it."""
    pass


class DebtAlreadyPaid(Exception):
    """A payment was attempted on a debt whose payments already cover it."""
    pass

class MarkedAsPaid(Exception):
    """A payment was attempted on a debt whose payments already cover it."""
    pass


class BankInUse(Exception):
    """A bank cannot be deleted while bank accounts or credit cards still belong to it."""
    pass
