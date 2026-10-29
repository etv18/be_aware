// Forms from a description. A form definition is:
//   (a field with editOnly: true is left out of the create form)
//   { title, submitLabel?, fields: [...], toBody(values) -> JSON body, fromRecord?(record) -> values, defaults?() -> values }
// A field is { name, label, type, required?, placeholder?, options?, when?(values), help?, half? } where type is one of
//   text | textarea | money | number | select | datetime | switch | segmented
// Everything the user types goes out as JSON; the server's 422 `fields` are shown under the matching input.
import { html, raw } from './html.js';
import { ApiError } from './api.js';
import { openDialog, toast, icon } from './ui.js';
import { enhanceDates, visibleInput } from './datepicker.js';

const inputId = (formId, name) => `${formId}-${name}`;

function optionTags(options, value, blank) {
  const items = blank !== undefined ? [{ value: '', label: blank }, ...options] : options;
  return items.map((o) => html`<option value="${o.value}" ${String(o.value) === String(value ?? '') ? raw('selected') : ''}>${o.label}</option>`);
}

function renderField(field, values, formId) {
  const id = inputId(formId, field.name);
  const value = values[field.name] ?? '';
  const required = field.required ? raw('required') : '';
  const span = field.half ? '' : 'sm:col-span-2';
  const label = html`<label class="label" for="${id}">${field.label}${field.required ? '' : html` <span class="font-normal text-faint">(optional)</span>`}</label>`;
  const error = html`<p class="field-error hidden" data-error-for="${field.name}"></p>`;

  let control;
  switch (field.type) {
    case 'textarea':
      control = html`<textarea class="textarea" id="${id}" name="${field.name}" placeholder="${field.placeholder || ''}" ${required}>${value}</textarea>`;
      break;
    case 'select':
      control = html`<select class="select" id="${id}" name="${field.name}" ${required}>${optionTags(field.options || [], value, field.blank)}</select>`;
      break;
    case 'datetime':
      control = html`<input class="input" type="text" data-picker="datetime" autocomplete="off" id="${id}" name="${field.name}" value="${value}" ${required}>`;
      break;
    case 'money':
      control = html`<input class="input num" type="text" inputmode="decimal" autocomplete="off" id="${id}" name="${field.name}" value="${value}" placeholder="${field.placeholder || '0.00'}" ${required}>`;
      break;
    case 'switch':
      return html`
        <div class="${span}" data-field="${field.name}">
          <label class="flex cursor-pointer items-center justify-between gap-3 rounded-lg border border-line px-3 py-2.5">
            <span class="text-sm">${field.label}${field.help ? html`<span class="block text-xs text-muted">${field.help}</span>` : ''}</span>
            <input type="checkbox" class="switch" name="${field.name}" ${value ? raw('checked') : ''}>
          </label>
          ${error}
        </div>`;
    case 'segmented':
      control = html`<div class="segmented" role="radiogroup" aria-label="${field.label}">
        ${(field.options || []).map((o) => html`
          <label><input class="peer sr-only" type="radio" name="${field.name}" value="${o.value}" ${String(o.value) === String(value) ? raw('checked') : ''}><span>${o.label}</span></label>`)}
      </div>`;
      break;
    default:
      control = html`<input class="input" type="${field.type === 'number' ? 'number' : 'text'}" id="${id}" name="${field.name}" value="${value}" placeholder="${field.placeholder || ''}" autocomplete="off" ${required}>`;
  }

  return html`<div class="${span}" data-field="${field.name}">${label}${control}${field.help ? html`<p class="mt-1 text-xs text-muted">${field.help}</p>` : ''}${error}</div>`;
}

/** Read the current values of every visible control. */
function readValues(form, fields) {
  const values = {};
  fields.forEach((field) => {
    if (field.type === 'switch') {
      values[field.name] = form.elements[field.name].checked;
    } else if (field.type === 'segmented') {
      values[field.name] = form.querySelector(`input[name="${field.name}"]:checked`)?.value ?? '';
    } else {
      values[field.name] = form.elements[field.name].value;
    }
  });
  return values;
}

function applyVisibility(form, fields) {
  const values = readValues(form, fields);
  fields.forEach((field) => {
    if (!field.when) return;
    const wrapper = form.querySelector(`[data-field="${field.name}"]`);
    const visible = field.when(values);
    wrapper.classList.toggle('hidden', !visible);
    wrapper.querySelectorAll('input, select, textarea').forEach((control) => { control.disabled = !visible; });
  });
}

function showErrors(form, error) {
  form.querySelectorAll('[data-error-for]').forEach((p) => { p.classList.add('hidden'); p.textContent = ''; });
  form.querySelectorAll('[aria-invalid]').forEach((c) => c.removeAttribute('aria-invalid'));

  const general = form.querySelector('[data-form-error]');
  const shown = Object.entries(error.fields || {}).filter(([name]) => form.querySelector(`[data-error-for="${name}"]`));

  shown.forEach(([name, message]) => {
    const target = form.querySelector(`[data-error-for="${name}"]`);
    target.textContent = message;
    target.classList.remove('hidden');
    visibleInput(form.elements[name])?.setAttribute?.('aria-invalid', 'true');
  });

  // a failure that belongs to no single field (not enough money, ...) goes in the banner
  if (shown.length === 0 || shown.length < Object.keys(error.fields || {}).length) {
    general.textContent = error.message;
    general.classList.remove('hidden');
  } else {
    general.classList.add('hidden');
  }
}

/**
 * Open a dialog with the form. Resolves to the saved result, or null when the user cancels.
 *   definition.onSubmit(body, values) must return a promise (the API call)
 */
export function openForm({ title, submitLabel = 'Save', fields: allFields, values = {}, toBody = (v) => v, record = null, onSubmit, wide = false }) {
  const fields = allFields.filter((f) => !f.editOnly || record); // editOnly: shown when editing an existing record
  const formId = `f${Math.random().toString(36).slice(2, 8)}`;

  return new Promise((resolve) => {
    const dialog = openDialog(html`
      <form id="${formId}" novalidate>
        <div class="flex items-center justify-between border-b border-line px-5 py-3.5">
          <h2 class="text-base font-semibold">${title}</h2>
          <button type="button" class="btn-icon -mr-1.5" data-close aria-label="Close">${icon('x')}</button>
        </div>
        <div class="max-h-[70vh] overflow-y-auto px-5 py-4">
          <p class="mb-4 hidden rounded-lg border border-negative/30 bg-negative/10 px-3 py-2 text-sm text-negative" data-form-error role="alert"></p>
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">${fields.map((f) => renderField(f, values, formId))}</div>
        </div>
        <div class="flex justify-end gap-2 border-t border-line px-5 py-3.5">
          <button type="button" class="btn btn-outline" data-close>Cancel</button>
          <button type="submit" class="btn btn-primary" data-submit>${submitLabel}</button>
        </div>
      </form>`);

    if (wide) dialog.classList.replace('max-w-lg', 'max-w-2xl');

    const form = dialog.querySelector('form');
    const submit = form.querySelector('[data-submit]');
    let result = null;

    enhanceDates(form);
    applyVisibility(form, fields);
    form.addEventListener('input', () => applyVisibility(form, fields));
    form.addEventListener('change', () => applyVisibility(form, fields));

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const formValues = readValues(form, fields.filter((f) => !f.when || f.when(readValues(form, fields))));
      const label = submit.textContent;
      submit.disabled = true;
      submit.textContent = 'Saving…';
      try {
        result = await onSubmit(toBody(formValues, record), formValues);
        dialog.close();
      } catch (error) {
        if (!(error instanceof ApiError)) throw error;
        showErrors(form, error);
        submit.disabled = false;
        submit.textContent = label;
      }
    });

    dialog.addEventListener('close', () => resolve(result));
    form.querySelector('input:not([type=hidden]):not(:disabled), select:not(:disabled)')?.focus();
  });
}

// ---------------------------------------------------------------- helpers the form definitions use
export const blankToNull = (value) => (value === '' || value === undefined ? null : value);
export const idOrNull = (value) => (value === '' || value === null || value === undefined ? null : Number(value));
export const toOptions = (items, label, value = 'id') => items.map((item) => ({ value: item[value], label: typeof label === 'function' ? label(item) : item[label] }));
