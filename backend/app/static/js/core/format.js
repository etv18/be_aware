// Numbers and dates as the pages show them.

const MONEY = new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const DATE = new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
const TIME = new Intl.DateTimeFormat('en-US', { hour: 'numeric', minute: '2-digit' });

export const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

/** "1234.5" -> "1,234.50" */
export function money(value) {
  const number = Number(value);
  return Number.isFinite(number) ? MONEY.format(number) : '-';
}

export const toNumber = (value) => {
  const number = Number(value);
  return Number.isFinite(number) ? number : 0;
};

// The API sends local wall-clock time without an offset, which the browser reads as local time too.
const parse = (iso) => (iso ? new Date(iso) : null);

export function date(iso) {
  const value = parse(iso);
  return value ? DATE.format(value) : '-';
}

export function dateTime(iso) {
  const value = parse(iso);
  return value ? `${DATE.format(value)} · ${TIME.format(value)}` : '-';
}

const pad = (n) => String(n).padStart(2, '0');

/** For <input type="datetime-local">: "2026-10-28T12:35" */
export function toInputValue(iso) {
  const value = iso ? new Date(iso) : new Date();
  return `${value.getFullYear()}-${pad(value.getMonth() + 1)}-${pad(value.getDate())}T${pad(value.getHours())}:${pad(value.getMinutes())}`;
}

export const nowInputValue = () => toInputValue(null);

export const titleCase = (text) => String(text ?? '').toLowerCase().replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

export const currentYear = () => new Date().getFullYear();
