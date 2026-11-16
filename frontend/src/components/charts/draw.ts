// Chart.js with the app's look. Colors come from the CSS variables, so charts follow the light / dark theme.
import {
  ArcElement, BarController, BarElement, CategoryScale, Chart, DoughnutController, Legend, LinearScale, LineController,
  LineElement, PointElement, Tooltip, type ChartType,
} from 'chart.js';

import { MONTHS, money, toNumber } from '@/lib/format';

Chart.register(ArcElement, BarController, BarElement, CategoryScale, DoughnutController, Legend, LinearScale, LineController, LineElement, PointElement, Tooltip);

const css = (name: string) => getComputedStyle(document.documentElement).getPropertyValue(`--${name}`).trim();
const color = (name: string, alpha = 1) => {
  const [r, g, b] = css(name).split(/\s+/);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};
const compact = (value: number | string) => new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(Number(value));

export type Series = { label: string; data: (string | number)[]; color: string | string[] }; // color: the name of a CSS variable ('c-expenses')

export type DrawOptions = { type?: Extract<ChartType, 'line' | 'bar' | 'doughnut'>; labels?: string[]; series: Series[]; stacked?: boolean; legend?: boolean };

/** Draw into a canvas. Destroy the returned chart when the component goes away. Call again (after destroying) when the theme changes. */
export function drawChart(canvas: HTMLCanvasElement, { type = 'line', labels = MONTHS, series, stacked = false, legend = series.length > 1 }: DrawOptions): Chart {
  const isDoughnut = type === 'doughnut';
  const text = color('muted');

  return new Chart(canvas, {
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
        ...(Array.isArray(s.color)
          ? { backgroundColor: s.color.map((variable) => color(variable)) }
          : { borderColor: color(s.color), backgroundColor: type === 'line' ? color(s.color, 0.12) : color(s.color) }),
      })),
    },
    options: {
      animation: false,
      responsive: true,
      maintainAspectRatio: false,
      color: text,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: legend, position: 'bottom', labels: { boxWidth: 10, boxHeight: 10, usePointStyle: true, color: text } },
        tooltip: { callbacks: { label: (item) => ` ${item.dataset.label}: ${money((item.parsed as { y?: number }).y ?? (item.parsed as unknown as number))}` } },
      },
      scales: isDoughnut ? {} : {
        x: { stacked, grid: { display: false, color: color('line') }, ticks: { color: text }, border: { display: false } },
        y: { stacked, beginAtZero: true, grid: { color: color('line') }, ticks: { color: text, callback: compact, maxTicksLimit: 6 }, border: { display: false } },
      },
      ...(isDoughnut ? { cutout: '68%' } : {}),
    },
  });
}
