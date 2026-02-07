BEGIN TRANSACTION;

UPDATE cash_ledger
SET created_at = '2026-01-31 ' || substr(created_at, 12) --the space at the end is mandatory for updating the column
WHERE date(created_at) = '2026-02-01'
AND type = 'EXPENSE'
;

SELECT id, amount, created_at
FROM incomes
WHERE date(created_at) = '2026-02-01';

--select cash ledger table
SELECT *
FROM cash_ledger
WHERE date(created_at) = '2026-01-31'
AND type = 'EXPENSE';

ROLLBACK;

