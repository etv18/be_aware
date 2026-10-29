// Loaded on every page: theme switch, navbar dropdowns, phone drawer, log out and the counters in the menu.
import { api, getData } from './core/api.js';
import { toastError } from './core/ui.js';

const root = document.documentElement;

// ---------------------------------------------------------------- theme
function setTheme(theme) {
  root.dataset.theme = theme;
  try { localStorage.setItem('theme', theme); } catch { /* private mode */ }
  window.dispatchEvent(new Event('themechange'));
}

document.querySelectorAll('[data-theme-toggle]').forEach((button) => {
  button.addEventListener('click', () => setTheme(root.dataset.theme === 'dark' ? 'light' : 'dark'));
});

// ---------------------------------------------------------------- phone drawer
const drawer = document.querySelector('[data-drawer]');
const backdrop = document.querySelector('[data-drawer-backdrop]');

function toggleDrawer(open) {
  drawer.classList.toggle('-translate-x-full', !open);
  backdrop.classList.toggle('hidden', !open);
  document.body.classList.toggle('overflow-hidden', open);
}

document.querySelector('[data-drawer-open]')?.addEventListener('click', () => toggleDrawer(true));
document.querySelectorAll('[data-drawer-close]').forEach((el) => el.addEventListener('click', () => toggleDrawer(false)));
backdrop?.addEventListener('click', () => toggleDrawer(false));
document.addEventListener('keydown', (event) => { if (event.key === 'Escape') toggleDrawer(false); });

// ---------------------------------------------------------------- navbar dropdowns
const menus = [...document.querySelectorAll('[data-menu]')];

function closeMenus(except = null) {
  menus.forEach((menu) => {
    if (menu === except) return;
    menu.querySelector('[data-menu-panel]').classList.add('hidden');
    menu.querySelector('[data-menu-trigger]').setAttribute('aria-expanded', 'false');
  });
}

menus.forEach((menu) => {
  const trigger = menu.querySelector('[data-menu-trigger]');
  const panel = menu.querySelector('[data-menu-panel]');
  trigger.addEventListener('click', () => {
    const open = panel.classList.contains('hidden');
    closeMenus(menu);
    panel.classList.toggle('hidden', !open);
    trigger.setAttribute('aria-expanded', String(open));
  });
  // move between the entries with the arrow keys
  menu.addEventListener('keydown', (event) => {
    if (!['ArrowDown', 'ArrowUp'].includes(event.key)) return;
    const entries = [...panel.querySelectorAll('a')];
    if (panel.classList.contains('hidden')) return;
    event.preventDefault();
    const at = entries.indexOf(document.activeElement);
    const next = event.key === 'ArrowDown' ? (at + 1) % entries.length : (at - 1 + entries.length) % entries.length;
    entries[next].focus();
  });
});

document.addEventListener('click', (event) => { if (!event.target.closest('[data-menu]')) closeMenus(); });
document.addEventListener('keydown', (event) => {
  if (event.key !== 'Escape') return;
  const open = menus.find((menu) => !menu.querySelector('[data-menu-panel]').classList.contains('hidden'));
  closeMenus();
  open?.querySelector('[data-menu-trigger]').focus();
});

// ---------------------------------------------------------------- log out
document.querySelectorAll('[data-logout]').forEach((button) => {
  button.addEventListener('click', async () => {
    try {
      await api.post('/logout');
      window.location.href = '/login';
    } catch (error) {
      toastError(error);
    }
  });
});

// ---------------------------------------------------------------- counters ("Loans 3" in the tooltip)
async function loadCounters() {
  try {
    const dashboard = await getData('/dashboard');
    const counts = { loans: dashboard.active_loans, debts: dashboard.active_debts };
    Object.entries(counts).forEach(([key, count]) => {
      if (!count) return;
      document.querySelectorAll(`[data-count="${key}"]`).forEach((el) => {
        el.textContent = count;
        el.classList.remove('hidden');
      });
    });
  } catch { /* the menu works without them */ }
}

loadCounters();
