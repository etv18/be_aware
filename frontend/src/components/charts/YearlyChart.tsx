// The "per month" card of one kind of record: a year picker, the chart and its total. (partials/ui.html chart_card + chart.js yearlyChart)
import type { Chart } from 'chart.js';
import { useEffect, useRef, useState } from 'react';

import { drawChart } from '@/components/charts/draw';
import { useTheme } from '@/components/Providers';
import { api } from '@/lib/api';
import { money, sum } from '@/lib/format';
import { useOptions } from '@/lib/queries';
import { useQuery } from '@tanstack/react-query';
import type { One, YearlyReport } from '@/types';

export function YearlyChart({ title, model, label, color, type = 'line', className = 'mt-6' }: {
  title: string; model: string; label: string; color: string; type?: 'line' | 'bar'; className?: string;
}) {
  const { theme } = useTheme();
  const years = useOptions().data?.years;
  const thisYear = new Date().getFullYear();
  const [picked, setPicked] = useState<number | null>(null);
  const year = picked ?? (years?.includes(thisYear) || !years?.length ? thisYear : years[0]); // this year, or the latest one that has records

  const report = useQuery({
    queryKey: ['report', 'yearly', model, year],
    queryFn: () => api.get<One<YearlyReport>>('/reports/yearly', { model, year }).then((r) => r.data),
    enabled: years !== undefined,
  });

  // the 12 totals are the one list in the report that is not `months`: it is named after the table
  const months = report.data
    ? (Object.entries(report.data).find(([key, value]) => Array.isArray(value) && key !== 'months')?.[1] as (string | number)[] | undefined) ?? []
    : [];

  const canvas = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    if (!canvas.current || !report.data) return;
    const chart: Chart = drawChart(canvas.current, { type, series: [{ label, data: months, color }] });
    return () => chart.destroy();
  }, [report.data, theme]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <section className={`card card-pad ${className}`}>
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className="text-sm font-semibold">{title}</h2>
        <select className="select h-8 w-24 text-xs" aria-label="Year" value={year} onChange={(e) => setPicked(Number(e.target.value))}>
          {(years?.length ? years : [thisYear]).map((y) => <option key={y} value={y}>{y}</option>)}
        </select>
      </div>
      <div className="relative h-64"><canvas ref={canvas} /></div>
      <p className="num mt-3 text-sm text-muted">Total <span className="font-medium text-ink">{report.data ? money(sum(months)) : ''}</span></p>
    </section>
  );
}
