"""Group the records hanging from a bank account, credit card or category by table name.

The frontend reads {'<table name>': [record dicts]} and shows one tab per table that has rows.
"""


def group_by_table(*record_lists):
    grouped = {}
    for records in record_lists:
        if records:
            grouped[records[0].__class__.__tablename__] = [record.to_dict() for record in records]
    return grouped
