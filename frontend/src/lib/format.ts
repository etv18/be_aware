// Numbers, dates and text, shown the way the app has always shown them.
const MONEY = new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const DATE = new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
const TIME = new Intl.DateTimeFormat('en-US', { hour: 'numeric', minute: '2-digit' });
const pad = (n: number) => String(n).padStart(2, '0');

export const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

export const toNumber = (value: unknown): number => (Number.isFinite(Number(value)) ? Number(value) : 0);
export const sum = (values: unknown[]): number => values.reduce<number>((total, value) => total + toNumber(value), 0);

/** "1234.5" -> "1,234.50" ("-" when there is nothing to show) */
export function money(value: string | number | null | undefined): string {
  return value !== null && value !== undefined && value !== '' && Number.isFinite(Number(value)) ? MONEY.format(Number(value)) : '-';
}

/** "2026-10-28T15:41:00" -> "Oct 28, 2026" */
export const formatDate = (iso: string | null | undefined): string => (iso ? DATE.format(new Date(iso)) : '-');

/** "2026-10-28T15:41:00" -> "Oct 28, 2026 · 3:41 PM" */
export const formatDateTime = (iso: string | null | undefined): string => (iso ? `${DATE.format(new Date(iso))} · ${TIME.format(new Date(iso))}` : '-');

/** For <input type="datetime-local">: "2026-10-28T15:41". No argument = right now. */
export function toInputValue(iso?: string | null): string {
  const d = iso ? new Date(iso) : new Date();
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

/** The value of a select as the id the API wants (null when nothing is chosen). */
export const idOrNull = (value: string | number | null | undefined): number | null => (value === '' || value === null || value === undefined ? null : Number(value));

/** Where the money came from or went to, as text. */
export function source(row: { is_cash?: boolean; credit_card_name?: string | null; bank_account_name?: string | null; person_name?: string | null }): string {
  return row.is_cash ? 'Cash' : row.credit_card_name || row.bank_account_name || (row.person_name ? 'No money moved' : '–');
}

export const plural = (count: number, one: string, many = `${one}s`) => (count === 1 ? one : many);

/** "bank_transfer" -> "Bank Transfer" */
export const titleCase = (text: string | null | undefined): string => String(text ?? '').toLowerCase().replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

/** "+5.00" in green, "-5.00" in red: the class goes with the text. */
export const signed = (value: string | number) => ({ text: `${Number(value) > 0 ? '+' : ''}${money(value)}`, className: Number(value) < 0 ? 'text-negative' : 'text-positive' });

/** Search a list that is already in the browser: the text matches description, person, code, amount or category; the dates are the created day. */
export function filterRows<T extends object>(rows: T[], { q, start, end }: { q?: string; start?: string; end?: string } = {}): T[] {
  const text = String(q ?? '').trim().toLowerCase();
  const plain = text.replace(/,/g, '');
  return rows.filter((row) => {
    const record = row as Record<string, unknown>;
    if (start && end) {
      const day = String(record.created_at ?? '').slice(0, 10);
      if (day < start || day > end) return false;
    }
    if (!text) return true;
    return [record.description, record.person_name, record.code, record.amount, record.category_name, record.expense_category_name]
      .filter((value) => value !== null && value !== undefined)
      .map((value) => String(value).toLowerCase())
      .some((value) => value.includes(text) || value.includes(plain));
  });
}
