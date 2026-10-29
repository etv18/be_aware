// Packs the Lucide icons the app uses into one SVG sprite (app/static/img/icons.svg).
// Add a name to ICONS, run `npm run build:icons`, then use it as icon('name') in the scripts.
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const iconsDir = join(here, '..', 'node_modules', 'lucide-static', 'icons');

const ICONS = [
  'house', 'landmark', 'wallet', 'credit-card', 'trending-up', 'trending-down', 'receipt', 'tags', 'hand-coins', 'scroll-text',
  'arrow-up-from-line', 'arrow-down-to-line', 'coins', 'book-open', 'arrow-left-right', 'search', 'plus', 'x', 'check',
  'pencil', 'trash-2', 'sun', 'moon', 'log-out', 'menu', 'chevron-right', 'chevron-left', 'chevron-down', 'calendar',
  'info', 'triangle-alert', 'circle-check', 'circle-alert', 'eye', 'banknote', 'piggy-bank', 'handshake', 'chart-line',
  'chart-column', 'list', 'inbox', 'file-text', 'send', 'archive', 'users', 'refresh-cw', 'filter-x', 'arrow-up-right',
  'arrow-down-right', 'ellipsis', 'wallet-cards', 'circle-dollar-sign', 'book-open-check', 'sliders-horizontal',
  'sun-moon', 'layout-grid', 'percent', 'lock', 'user',
];

const inner = (svg) => svg.replace(/^[\s\S]*?<svg[^>]*>/, '').replace(/<\/svg>\s*$/, '').trim();

const symbols = ICONS.map((name) => {
  const file = join(iconsDir, `${name}.svg`);
  let svg;
  try { svg = readFileSync(file, 'utf8'); } catch { console.error(`missing icon: ${name}`); process.exit(1); }
  return `<symbol id="${name}" viewBox="0 0 24 24">${inner(svg)}</symbol>`;
});

const sprite = `<svg xmlns="http://www.w3.org/2000/svg">\n${symbols.join('\n')}\n</svg>\n`;
writeFileSync(join(here, '..', '..', 'app', 'static', 'img', 'icons.svg'), sprite);
console.log(`icons.svg: ${ICONS.length} icons`);
