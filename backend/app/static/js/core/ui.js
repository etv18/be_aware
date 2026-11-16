// Small building blocks every page uses: icons, toasts and the confirm dialog.
import { html, raw, escapeHtml } from './html.js';

const SPRITE = '/static/img/icons.svg';

/** An inline Lucide icon from the sprite. icon('trash-2') */
export function icon(name, classes = '') {
  return raw(`<svg class="icon ${classes}" aria-hidden="true"><use href="${SPRITE}#${name}"></use></svg>`);
}

// ---------------------------------------------------------------- toasts
function toastHost() {
  let host = document.getElementById('toasts');
  if (!host) {
    host = document.createElement('div');
    host.id = 'toasts';
    host.setAttribute('aria-live', 'polite');
    host.className = 'pointer-events-none fixed inset-x-4 bottom-4 z-[60] flex flex-col items-center gap-2 sm:inset-x-auto sm:right-4 sm:items-end';
    document.body.append(host);
  }
  return host;
}

export function toast(message, kind = 'success') {
  const tone = kind === 'error' ? 'text-negative' : 'text-positive';
  const name = kind === 'error' ? 'circle-alert' : 'circle-check';
  const item = document.createElement('div');
  item.className = 'pointer-events-auto flex max-w-sm items-start gap-2.5 rounded-lg border border-line bg-surface px-3.5 py-2.5 text-sm shadow-lg';
  item.innerHTML = `<span class="${tone} mt-0.5">${icon(name)}</span><span>${escapeHtml(message)}</span>`;
  toastHost().append(item);
  setTimeout(() => item.remove(), kind === 'error' ? 6000 : 3200);
}

export const toastError = (error) => toast(error?.message || 'Something went wrong.', 'error');

// ---------------------------------------------------------------- dialogs
/** Open a <dialog class="modal"> with the given markup; resolves the element, removes it when closed. */
export function openDialog(markup) {
  const dialog = document.createElement('dialog');
  dialog.className = 'modal';
  dialog.innerHTML = markup.toString();
  document.body.append(dialog);
  dialog.addEventListener('close', () => dialog.remove());
  // a click on the backdrop (the dialog element itself, outside its content) closes it
  dialog.addEventListener('mousedown', (event) => {
    if (event.target === dialog) dialog.close();
  });
  dialog.querySelectorAll('[data-close]').forEach((button) => button.addEventListener('click', () => dialog.close()));
  dialog.showModal();
  return dialog;
}

/** "Are you sure?" -> Promise<boolean> */
export function confirmDialog({ title = 'Are you sure?', message = '', confirmLabel = 'Delete', danger = true } = {}) {
  return new Promise((resolve) => {
    const dialog = openDialog(html`
      <div class="p-5">
        <h2 class="text-base font-semibold">${title}</h2>
        ${message ? html`<p class="mt-1.5 text-sm text-muted">${message}</p>` : ''}
        <div class="mt-5 flex justify-end gap-2">
          <button type="button" class="btn btn-outline" data-close>Cancel</button>
          <button type="button" class="btn ${danger ? 'btn-danger' : 'btn-primary'}" data-confirm>${confirmLabel}</button>
        </div>
      </div>`);
    let answer = false;
    dialog.querySelector('[data-confirm]').addEventListener('click', () => { answer = true; dialog.close(); });
    dialog.addEventListener('close', () => resolve(answer));
  });
}

// ---------------------------------------------------------------- misc
export const debounce = (fn, wait = 280) => {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), wait);
  };
};

export function emptyState(title, text = '') {
  return html`
    <div class="flex flex-col items-center px-6 py-14 text-center">
      <span class="mb-3 flex size-10 items-center justify-center rounded-full bg-sunken text-muted">${icon('inbox')}</span>
      <p class="text-sm font-medium">${title}</p>
      ${text ? html`<p class="mt-1 max-w-sm text-sm text-muted">${text}</p>` : ''}
    </div>`;
}

export function loadingRows(count = 5) {
  return html`<div class="space-y-3 p-4">${Array.from({ length: count }, () => html`<div class="skeleton h-9 w-full"></div>`)}</div>`;
}
