// Filtering and summing a list that is already in the browser (the records of one account, card, loan...).
// Text matches the description, person, code or amount; dates are the day the record was created.
import { toNumber } from './format.js';

export function filterRows(rows, { q, start, end } = {}) {
  const text = String(q || '').trim().toLowerCase();
  const plain = text.replace(/,/g, '');
  return rows.filter((row) => {
    if (start && end) {
      const day = String(row.created_at || '').slice(0, 10);
      if (day < start || day > end) return false;
    }
    if (!text) return true;
    const haystack = [row.description, row.person_name, row.code, row.amount, row.category_name, row.expense_category_name]
      .filter((v) => v !== null && v !== undefined)
      .map((v) => String(v).toLowerCase());
    return haystack.some((v) => v.includes(text) || v.includes(plain));
  });
}

export const totalOf = (rows) => rows.reduce((sum, row) => sum + toNumber(row.amount), 0);
