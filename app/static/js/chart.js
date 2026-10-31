// Chart.js with the app's look. Chart.js itself is loaded by layout.html (static/vendor/chart.umd.js).
// Colors come from the CSS variables, so charts follow the light / dark theme.
import { $, MONTHS, api, loadOptions, money, sum, toNumber, toastError } from './common.js';

const charts = new Map(); // canvas -> {chart, colorVars}

const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(`--${name}`).trim();
const color = (name, alpha = 1) => {
  const [r, g, b] = css(name).split(/\s+/);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};

function theme(chart, colorVars) {
  const grid = color('line');
  const text = color('muted');
  chart.options.color = text;
  Object.values(chart.options.scales || {}).forEach((axis) => {
    axis.grid = { ...(axis.grid || {}), color: grid, drawBorder: false };
    axis.ticks = { ...(axis.ticks || {}), color: text };
    axis.border = { display: false };
  });
  chart.data.datasets.forEach((dataset, i) => {
    const variable = colorVars[i];
    if (!variable) return;
    if (Array.isArray(variable)) {
      dataset.backgroundColor = variable.map((v) => color(v));
    } else {
      dataset.borderColor = color(variable);
      dataset.backgroundColor = chart.config.type === 'line' ? color(variable, 0.12) : color(variable);
    }
  });
  if (chart.options.plugins?.legend?.labels) chart.options.plugins.legend.labels.color = text;
}

window.addEventListener('themechange', () => {
  charts.forEach(({ chart, colorVars }) => { theme(chart, colorVars); chart.update('none'); });
});

const compact = (value) => new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(value);

/**
 * draw(canvas, { type: 'line'|'bar'|'doughnut', labels, series: [{label, data, color: 'c-expenses'}], stacked?: bool })
 * Calling it again on the same canvas replaces the chart.
 */
export function draw(canvas, { type = 'line', labels = MONTHS, series, stacked = false, legend = series.length > 1 }) {
  charts.get(canvas)?.chart.destroy();

  const colorVars = series.map((s) => s.color);
  const isDoughnut = type === 'doughnut';

  const chart = new window.Chart(canvas, {
    type,
    data: {
      labels,
      datasets: series.map((s) => ({
        label: s.label,
        data: s.data.map(toNumber),
        borderWidth: isDoughnut ? 0 : 2,
        tension: 0,
        pointRadius: 0,
        pointHoverRadius: 4,
        borderRadius: type === 'bar' ? 4 : 0,
        maxBarThickness: 28,
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: legend, position: 'bottom', labels: { boxWidth: 10, boxHeight: 10, usePointStyle: true } },
        tooltip: {
          callbacks: { label: (item) => ` ${item.dataset.label}: ${money(item.parsed.y ?? item.parsed)}` },
        },
      },
      scales: isDoughnut ? {} : {
        x: { stacked, grid: { display: false } },
        y: { stacked, beginAtZero: true, ticks: { callback: compact, maxTicksLimit: 6 } },
      },
      cutout: isDoughnut ? '68%' : undefined,
    },
  });

  theme(chart, colorVars);
  chart.update('none');
  charts.set(canvas, { chart, colorVars });
  return chart;
}

/**
 * The "per month" card of partials/ui.html chart_card: a year picker, the chart of one kind of record and its total.
 *   yearlyChart({ model: 'expenses', label: 'Expenses', color: 'c-expenses' }) -> { reload }
 */
export function yearlyChart({ model, label, color: seriesColor, type = 'line', root = document }) {
  const select = $('[data-chart-year]', root);
  const canvas = $('[data-chart]', root);
  const total = $('[data-chart-total]', root);

  async function reload() {
    if (!select.value) return;
    try {
      const { data } = await api.get('/reports/yearly', { model, year: select.value });
      const months = Object.entries(data).find(([key, value]) => Array.isArray(value) && key !== 'months')?.[1] || [];
      total.textContent = money(sum(months));
      draw(canvas, { type, series: [{ label, data: months, color: seriesColor }] });
    } catch (error) {
      toastError(error);
    }
  }

  loadOptions().then(({ years }) => {
    const thisYear = new Date().getFullYear();
    select.replaceChildren(...(years?.length ? years : [thisYear]).map((y) => new Option(y, y)));
    select.value = String(thisYear);
    if (!select.value) select.selectedIndex = 0; // this year has no records yet: show the latest year that has
    select.addEventListener('change', reload);
    reload();
  }).catch(toastError);

  return { reload };
}
