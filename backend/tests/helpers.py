"""Small helpers shared by the expense tests. They send the same JSON the frontend sends."""


def expense_form(amount, category, description='Lunch', cash=False, card=None, account=None, created_at='2026-10-15T12:30'):
    return {
        'amount': str(amount),
        'expense_category_id': category.id,
        'description': description,
        'created_at': created_at,
        'credit_card_id': card.id if card else None,
        'bank_account_id': account.id if account else None,
        'is_cash': cash,
    }


def post_expense(client, **kwargs):
    return client.post('/api/expenses', json=expense_form(**kwargs))


def put_expense(client, expense_id, **kwargs):
    return client.put(f'/api/expenses/{expense_id}', json=expense_form(**kwargs))


def delete_expense(client, expense_id):
    return client.delete(f'/api/expenses/{expense_id}')
