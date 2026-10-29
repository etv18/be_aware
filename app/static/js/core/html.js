// A tiny template tag that escapes everything you interpolate, so a description like
// <img onerror=...> shows up as text and never runs. Use raw() only for markup you built yourself.

class Safe {
  constructor(text) { this.text = text; }
  toString() { return this.text; }
}

const ENTITIES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };

export const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (c) => ENTITIES[c]);

export const raw = (text) => new Safe(String(text));

function render(value) {
  if (value === null || value === undefined || value === false) return '';
  if (value instanceof Safe) return value.text;
  if (Array.isArray(value)) return value.map(render).join('');
  return escapeHtml(value);
}

export function html(strings, ...values) {
  let out = '';
  strings.forEach((chunk, i) => {
    out += chunk;
    if (i < values.length) out += render(values[i]);
  });
  return new Safe(out);
}

/** Replace the content of an element with a template result. */
export function mount(element, template) {
  element.innerHTML = template.toString();
  return element;
}
