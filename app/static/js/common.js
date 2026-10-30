// Everything the pages share, in one file. A page imports only what it uses:
//   import { api, money, bindList, recordForm } from './common.js';
// Sections: server calls · numbers and text · toasts · dialogs · forms · stats · table rows · search bar · lists · record forms.

// Every JSON endpoint lives under /api: scripts write api.get('/expenses') and the request goes to /api/expenses.
const API = '/api';

export const $ = (selector, root = document) => root.querySelector(selector);
export const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

// ------------------------------------------------------------------ server calls (JSON in, JSON out)
export class ApiError extends Error {
  constructor(status, error = {}) {
    super(error.message || 'Something went wrong.');
    this.status = status;
    this.code = error.code || 'error';
    this.fields = error.fields || {}; // {field_name: 'message'} for a form
  }
}

let csrf = $('meta[name="csrf-token"]')?.content || null;

async function csrfToken(force = false) {
  if (!csrf || force) csrf = (await (await fetch(`${API}/session`, { credentials: 'same-origin' })).json()).data.csrf_token;
  return csrf;
}

async function request(method, path, { query, body } = {}, retried = false) {
  const url = new URL(API + path, window.location.origin);
  Object.entries(query || {}).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') url.searchParams.set(key, value);
  });

  const headers = { Accept: 'application/json' };
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  if (method !== 'GET') headers['X-CSRFToken'] = await csrfToken();

  let response;
  try {
    response = await fetch(url, { method, headers, credentials: 'same-origin', body: body === undefined ? undefined : JSON.stringify(body) });
  } catch {
    throw new ApiError(0, { code: 'network_error', message: 'Could not reach the server. Check your connection.' });
  }
  if (response.status === 204) return null;

  let payload = null;
  try { payload = await response.json(); } catch { /* not JSON */ }

  if (!response.ok) {
    const error = payload?.error || {};
    if (response.status === 401) window.location.href = '/login';
    if (error.code === 'csrf_failed' && !retried) { // the token expired: get a new one and try once more
      await csrfToken(true);
      return request(method, path, { query, body }, true);
    }
    throw new ApiError(response.status, error);
  }
  return payload;
}

export const api = {
  get: (path, query) => request('GET', path, { query }),   // -> {data, meta?}
  post: (path, body) => request('POST', path, { body }),
  put: (path, body) => request('PUT', path, { body }),
  delete: (path) => request('DELETE', path),
};

let optionsCache = null;
/** Banks, accounts, cards, categories and years for the selects. Asked once, and again after anything is saved or deleted. */
export const loadOptions = () => (optionsCache ??= api.get('/options').then((payload) => payload.data));
const forgetOptions = () => { optionsCache = null; }; // a new account or category must show up in the next form

// ------------------------------------------------------------------ numbers, dates and text
const MONEY = new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const DATE = new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
const TIME = new Intl.DateTimeFormat('en-US', { hour: 'numeric', minute: '2-digit' });
const pad = (n) => String(n).padStart(2, '0');

export const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

/** "1234.5" -> "1,234.50" */
export const money = (value) => (value !== null && value !== undefined && value !== '' && Number.isFinite(Number(value)) ? MONEY.format(Number(value)) : '-');
export const toNumber = (value) => (Number.isFinite(Number(value)) ? Number(value) : 0);
export const sum = (list, key) => list.reduce((total, item) => total + toNumber(key ? item[key] : item), 0);

/** "2026-10-28T15:41:00" -> "Oct 28, 2026" */
export const formatDate = (iso) => (iso ? DATE.format(new Date(iso)) : '-');
export const formatDateTime = (iso) => (iso ? `${DATE.format(new Date(iso))} · ${TIME.format(new Date(iso))}` : '-');

/** For <input type="datetime-local">: "2026-10-28T15:41". No argument = right now. */
export function toInputValue(iso) {
  const d = iso ? new Date(iso) : new Date();
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}
export const nowInputValue = () => toInputValue(null);

export const idOrNull = (value) => (value === '' || value === null || value === undefined ? null : Number(value));
export const titleCase = (text) => String(text ?? '').toLowerCase().replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
const capitalize = (text) => text.charAt(0).toUpperCase() + text.slice(1);

export const debounce = (fn, wait = 280) => {
  let timer;
  return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), wait); };
};

/** Where the money came from or went to, as text. */
export const source = (row) => (row.is_cash ? 'Cash' : row.credit_card_name || row.bank_account_name || (row.person_name ? 'No money moved' : '–'));

/** "+10.00" in green, "-10.00" in red: a cell value for renderRows. */
export const signed = (value) => ({ text: `${Number(value) > 0 ? '+' : ''}${money(value)}`, class: Number(value) < 0 ? 'text-negative' : 'text-positive' });

// ------------------------------------------------------------------ toasts (the small message in the corner)
export function toast(message, kind = 'success') {
  let host = $('#toasts');
  if (!host) {
    host = document.createElement('div');
    host.id = 'toasts';
    host.setAttribute('aria-live', 'polite');
    host.className = 'pointer-events-none fixed inset-x-4 bottom-4 z-[60] flex flex-col items-center gap-2 sm:inset-x-auto sm:right-4 sm:items-end';
    document.body.append(host);
  }
  const error = kind === 'error';
  const item = document.createElement('div');
  item.className = 'pointer-events-auto flex max-w-sm items-start gap-2.5 rounded-lg border border-line bg-surface px-3.5 py-2.5 text-sm shadow-lg';
  const glyph = document.createElement('span');
  glyph.className = `mt-0.5 ${error ? 'text-negative' : 'text-positive'}`;
  glyph.innerHTML = `<svg class="icon" aria-hidden="true"><use href="/static/img/icons.svg#${error ? 'circle-alert' : 'circle-check'}"></use></svg>`; // fixed markup, no user text
  const text = document.createElement('span');
  text.textContent = message; // textContent: whatever the message contains is shown as text, never run
  item.append(glyph, text);
  host.append(item);
  setTimeout(() => item.remove(), error ? 6000 : 3200);
}

export const toastError = (error) => toast(error?.message || 'Something went wrong.', 'error');

// ------------------------------------------------------------------ dialogs (<dialog class="modal"> that is already in the page)
/** Makes the X / Cancel buttons (data-close) and a click outside close the dialog. Safe to call twice. */
export function setupDialog(dialog) {
  if (dialog.dataset.ready) return;
  dialog.dataset.ready = '1';
  $$('[data-close]', dialog).forEach((button) => button.addEventListener('click', () => dialog.close()));
  dialog.addEventListener('mousedown', (event) => { if (event.target === dialog) dialog.close(); });
}

/** "Are you sure?" -> Promise<boolean>. Uses partials/confirm_dialog.html. */
export function confirmDialog({ title, text = '' }) {
  const dialog = $('#confirm-dialog');
  setupDialog(dialog);
  $('[data-confirm-title]', dialog).textContent = title;
  $('[data-confirm-text]', dialog).textContent = text;
  return new Promise((resolve) => {
    let answer = false;
    $('[data-confirm]', dialog).addEventListener('click', () => { answer = true; dialog.close(); }, { once: true });
    dialog.addEventListener('close', () => resolve(answer), { once: true });
    dialog.showModal();
  });
}

// ------------------------------------------------------------------ forms
/** Put values in the form: setValues(form, {amount: '10', method: 'cash'}). Works for inputs, selects, radio groups and switches. */
export function setValues(form, values) {
  Object.entries(values).forEach(([name, value]) => {
    const control = form.elements[name];
    if (!control) return;
    if (control.type === 'checkbox') control.checked = Boolean(value);
    else control.value = value ?? '';
  });
}

/** What the person typed, as {name: value}. Fields hidden by data-show-when are left out; switches are true / false. */
export function getValues(form) {
  const values = Object.fromEntries(new FormData(form));
  $$('input[type=checkbox]', form).forEach((box) => { values[box.name] = box.checked; });
  return values;
}

/** Fill a <select> with {id, <labelKey>} items, keeping a first "Choose…" entry. */
export function fillSelect(select, items, labelKey, blank) {
  const current = select.value;
  select.replaceChildren(new Option(blank, ''), ...items.map((item) => new Option(item[labelKey], item.id)));
  select.value = current;
}

/** Fields with data-show-when="method=bank" appear only while that value is chosen. Returns refresh() for after setValues(). */
export function bindShowWhen(form) {
  const refresh = () => {
    const values = getValues(form);
    $$('[data-show-when]', form).forEach((box) => {
      const [name, wanted] = box.dataset.showWhen.split('=');
      const show = String(values[name]) === wanted;
      box.classList.toggle('hidden', !show);
      $$('input, select, textarea', box).forEach((control) => { control.disabled = !show; });
    });
  };
  form.addEventListener('change', refresh);
  return refresh;
}

export function clearErrors(form) {
  $$('[data-error-for]', form).forEach((p) => { p.classList.add('hidden'); p.textContent = ''; });
  $$('[aria-invalid]', form).forEach((control) => control.removeAttribute('aria-invalid'));
  $('[data-form-error]', form).classList.add('hidden');
}

/** Show the server's field errors under their inputs; anything else goes in the banner at the top. */
export function showErrors(form, error) {
  clearErrors(form);
  const all = Object.entries(error.fields || {});
  const shown = all.filter(([name]) => $(`[data-error-for="${name}"]`, form));
  shown.forEach(([name, message]) => {
    const line = $(`[data-error-for="${name}"]`, form);
    line.textContent = message;
    line.classList.remove('hidden');
    form.elements[name]?.setAttribute?.('aria-invalid', 'true');
  });
  if (shown.length === 0 || shown.length < all.length) {
    const banner = $('[data-form-error]', form);
    banner.textContent = error.message;
    banner.classList.remove('hidden');
  }
}

// ------------------------------------------------------------------ figures above a list: <p data-stat="total"> and <p data-stat-hint="total">
/** setStats({ total: '10.00', count: 3, left: { text: '-5.00', negative: true }, loans: { text: '9.00', hint: '2 active' } }) */
export function setStats(values, root = document) {
  Object.entries(values).forEach(([key, value]) => {
    const item = value !== null && typeof value === 'object' ? value : { text: value };
    const figure = $(`[data-stat="${key}"]`, root);
    if (figure) {
      figure.textContent = item.text;
      figure.classList.toggle('text-negative', item.negative === true);
    }
    const hint = $(`[data-stat-hint="${key}"]`, root);
    if (hint && item.hint !== undefined) hint.textContent = item.hint;
  });
}

// ------------------------------------------------------------------ table rows
/**
 * Draw the rows from a <template data-row-template> that holds one <tr>. cells(row) returns {cellName: value}, and each value goes
 * in the element marked data-cell="cellName". A value is text, or {text?, class?, show?, width?} to also add classes, hide the
 * element (show: false) or set its width (a progress bar). Always textContent, so a description like <b>x</b> can never run as HTML.
 */
export function renderRows(tbody, template, rows, cells) {
  tbody.replaceChildren(...rows.map((row) => {
    const tr = template.content.firstElementChild.cloneNode(true);
    tr.dataset.id = row.id;
    Object.entries(cells(row)).forEach(([name, value]) => {
      const target = $(`[data-cell="${name}"]`, tr);
      if (!target) return;
      const item = value !== null && typeof value === 'object' ? value : { text: value };
      if (item.text !== undefined) target.textContent = item.text;
      if (item.class) target.classList.add(...item.class.split(' '));
      if (item.show === false) target.classList.add('hidden');
      if (item.width !== undefined) target.style.width = item.width;
    });
    return tr;
  }));
}

/** Clicks on buttons marked data-action="edit" run handlers.edit(row). */
export function onRowAction(tbody, getRows, handlers) {
  tbody.addEventListener('click', (event) => {
    const button = event.target.closest('[data-action]');
    if (!button) return;
    const id = button.closest('tr').dataset.id;
    const row = getRows().find((r) => String(r.id) === id);
    if (row) handlers[button.dataset.action]?.(row);
  });
}

// ------------------------------------------------------------------ search bar (partials/ui.html filter_bar)
/** Calls onChange({q, start, end}) when the person types or picks dates. Empty values are left out. */
export function bindFilters(root, onChange) {
  const inputs = $$('[data-filter]', root);
  const state = () => Object.fromEntries(inputs.map((i) => [i.dataset.filter, i.value]).filter(([, value]) => value));

  const typed = debounce(() => onChange(state()), 280);
  inputs.forEach((input) => input.addEventListener('input', () => {
    const { start, end } = state();
    if (input.type === 'date' && Boolean(start) !== Boolean(end)) return; // wait until both dates are set
    if (input.type === 'search') typed(); else onChange(state());
  }));

  $('[data-filter-clear]', root)?.addEventListener('click', () => {
    inputs.forEach((input) => { input.value = ''; });
    onChange(state());
  });
}

/** Search a list that is already in the browser (text matches description, person, code or amount; dates are the created day). */
export function filterRows(rows, { q, start, end } = {}) {
  const text = String(q || '').trim().toLowerCase();
  const plain = text.replace(/,/g, '');
  return rows.filter((row) => {
    if (start && end) {
      const day = String(row.created_at || '').slice(0, 10);
      if (day < start || day > end) return false;
    }
    if (!text) return true;
    return [row.description, row.person_name, row.code, row.amount, row.category_name, row.expense_category_name]
      .filter((v) => v !== null && v !== undefined)
      .map((v) => String(v).toLowerCase())
      .some((v) => v.includes(text) || v.includes(plain));
  });
}

// ------------------------------------------------------------------ a list: load, search, draw rows, edit / delete buttons
/**
 * Wires the markup of partials/ui.html table_card (rows, empty message, search bar, total line).
 *   path        the endpoint that lists the records        recordPath  where one record lives (default: path)
 *   cells(row)  what each cell shows (see renderRows)      onData({data, meta, rows, filtering})  figures, charts...
 *   form        a recordForm: the New button and the edit button open it
 *   noun, undo  for the delete confirmation                handlers    extra row buttons: { pay: (row) => ... }
 *   open(row)   double click on a row                      localFilter search in the browser instead of asking the server
 *   onDeleted   runs after a delete                        empty       { title, text } when there is nothing to show
 * Returns { reload, rows }.
 */
export function bindList({ root = document, path, recordPath = path, query = {}, cells, onData, form, noun = 'record', undo = 'This cannot be undone.', handlers = {}, localFilter = false, empty = {}, open, onDeleted }) {
  const tbody = $('[data-rows]', root);
  const template = $('[data-row-template]', root);
  const emptyBox = $('[data-empty]', root);
  const note = $('[data-note]', root);
  const totalBar = $('[data-total-bar]', root);
  let rows = [];
  let filters = {};
  let latest = 0; // so a slow answer never overwrites a newer one

  async function load() {
    const mine = ++latest;
    try {
      const { data, meta } = await api.get(path, localFilter ? query : { ...query, ...filters });
      if (mine !== latest) return;
      const filtering = Boolean(filters.q || (filters.start && filters.end));
      rows = localFilter ? filterRows(data, filters) : data;

      renderRows(tbody, template, rows, cells);
      emptyBox.classList.toggle('hidden', rows.length > 0);
      $('[data-empty-title]', emptyBox).textContent = filtering ? 'Nothing matches' : (empty.title || 'Nothing here yet');
      $('[data-empty-text]', emptyBox).textContent = filtering ? 'Try other words or another date range.' : (empty.text || '');
      note?.classList.toggle('hidden', filtering);
      if (totalBar) {
        $('[data-total-label]', totalBar).textContent = `${filtering ? 'Filtered total' : 'Total'} · ${rows.length} ${rows.length === 1 ? 'record' : 'records'}`;
        $('[data-total-value]', totalBar).textContent = money(sum(rows, 'amount'));
      }
      onData?.({ data, meta, rows, filtering });
    } catch (error) {
      toastError(error);
    }
  }

  async function remove(row) {
    const sure = await confirmDialog({ title: `Delete this ${noun}?`, text: undo });
    if (!sure) return;
    try {
      await api.delete(`${recordPath}/${row.id}`);
      forgetOptions();
      toast(`${capitalize(noun)} deleted.`);
      load();
      onDeleted?.();
    } catch (error) {
      toastError(error);
    }
  }

  onRowAction(tbody, () => rows, { ...(form ? { edit: (row) => form.open(row) } : {}), delete: remove, ...handlers });
  $$('[data-new]', root).forEach((button) => button.addEventListener('click', () => form?.open(null)));

  if (open) { // double click on a row
    tbody.classList.add('row-open');
    tbody.addEventListener('dblclick', (event) => {
      if (event.target.closest('button, a, input, select')) return;
      const row = rows.find((r) => String(r.id) === event.target.closest('tr')?.dataset.id);
      if (!row) return;
      window.getSelection()?.removeAllRanges();
      open(row);
    });
  }

  const bar = $('[data-filters]', root);
  if (bar) bindFilters(bar, (state) => { filters = state; load(); });

  load();
  return { reload: load, rows: () => rows };
}

// ------------------------------------------------------------------ a form in a dialog: new and edit
/**
 * Wires a <dialog> made with partials/ui.html form_dialog.
 *   path, noun    where it saves (POST path, PUT path/<id>) and what it is called in messages
 *   selects       fill the selects from /options: { bank_account_id: ['bank_accounts', 'nick_name', 'Choose an account'] }
 *   defaults(options) -> values of a new record        fromRecord(record) -> values of the record being edited
 *   toBody(values, record) -> the JSON the server gets   title(record) -> the dialog title (default "New <noun>" / "Edit <noun>")
 *   onSaved()     runs after a successful save
 * Returns { open(record = null), close }.
 */
export function recordForm(dialog, { path, noun, selects = {}, defaults = () => ({}), fromRecord = (record) => record, toBody, title, onSaved = () => {} }) {
  setupDialog(dialog);
  const form = $('[data-form]', dialog);
  const refresh = bindShowWhen(form);
  let editing = null;

  async function open(record = null) {
    editing = record;
    try {
      const options = await loadOptions();
      Object.entries(selects).forEach(([name, [key, label, blank]]) => fillSelect(form.elements[name], options[key], label, blank));
      clearErrors(form);
      setValues(form, record ? fromRecord(record) : defaults(options));
      refresh();
      $$('[data-edit-only]', form).forEach((box) => { // fields that only make sense on an existing record
        box.classList.toggle('hidden', !record);
        $$('input, select, textarea', box).forEach((control) => { control.disabled = !record; });
      });
      $('[data-title]', dialog).textContent = title ? title(record) : `${record ? 'Edit' : 'New'} ${noun}`;
      dialog.showModal();
    } catch (error) {
      toastError(error);
    }
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const submit = $('[data-submit]', form);
    submit.disabled = true;
    try {
      const body = toBody(getValues(form), editing);
      if (editing) await api.put(`${path}/${editing.id}`, body);
      else await api.post(path, body);
      forgetOptions();
      dialog.close();
      toast(`${capitalize(noun)} ${editing ? 'updated' : 'created'}.`);
      onSaved();
    } catch (error) {
      if (!(error instanceof ApiError)) throw error;
      showErrors(form, error); // the server's messages, under each field
    } finally {
      submit.disabled = false;
    }
  });

  return { open, close: () => dialog.close() };
}
