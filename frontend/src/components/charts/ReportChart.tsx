// A card with one chart that is drawn from data the page already has (the pages with a "per month" chart of their own).
import type { Chart } from 'chart.js';
import { useEffect, useRef, type ReactNode } from 'react';

import { drawChart, type DrawOptions } from '@/components/charts/draw';
import { useTheme } from '@/components/Providers';

export function ReportChart({ title, options, className = 'mt-6', children }: {
  title: string; options: DrawOptions | null; className?: string; children?: ReactNode; // null while it loads; children: next to the title (tabs, a year)
}) {
  const { theme } = useTheme();
  const canvas = useRef<HTMLCanvasElement>(null);
  const key = JSON.stringify(options);

  useEffect(() => {
    if (!canvas.current || !options) return;
    const chart: Chart = drawChart(canvas.current, options);
    return () => chart.destroy();
  }, [key, theme]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <section className={`card card-pad ${className}`}>
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className="text-sm font-semibold">{title}</h2>
        {children}
      </div>
      <div className="relative h-64"><canvas ref={canvas} /></div>
    </section>
  );
}
