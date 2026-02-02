BEGIN TRANSACTION;

UPDATE incomes
SET created_at = '2026-01-31 ' || substr(created_at, 12) --the space at the end is mandatory for updating the column
WHERE date(created_at) = '2026-02-01';

SELECT id, amount, created_at
FROM incomes
WHERE date(created_at) = '2026-02-01';

