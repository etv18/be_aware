// The top of a page: title and buttons, then the figures above the table. (partials/ui.html: page_header, stat_card, stat_row)
import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';

import { Icon } from '@/components/Icon';

export function PageHeader({ title, subtitle, newLabel, onNew, back, children }: {
  title: string; subtitle?: string; newLabel?: string; onNew?: () => void;
  back?: { to: string; label: string }; children?: ReactNode; // children: more buttons next to "New"
}) {
  return (
    <header className="mb-6 flex flex-wrap items-end justify-between gap-3">
      <div className="min-w-0">
        {back && <Link to={back.to} className="mb-2 inline-flex items-center gap-1 text-sm text-muted hover:text-ink"><Icon name="chevron-left" />{back.label}</Link>}
        <h1 className="truncate text-xl font-semibold">{title}</h1>
        <p className="mt-0.5 text-sm text-muted">{subtitle}</p>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        {children}
        {newLabel && <button type="button" className="btn btn-primary" onClick={onNew}><Icon name="plus" />{newLabel}</button>}
      </div>
    </header>
  );
}

export type Stat = {
  label: string;
  value: ReactNode;                // "–" while loading
  hint?: string;                   // the small line under the figure
  negative?: boolean;              // red figure
  valueClassName?: string;         // more classes for the figure, e.g. 'text-orange-500'
};

function StatCard({ label, value, hint, negative, valueClassName = '' }: Stat) {
  return (
    <div className="card px-4 py-3.5">
      <p className="text-xs text-muted">{label}</p>
      <p className={`num mt-1 truncate text-xl font-semibold ${negative ? 'text-negative' : ''} ${valueClassName}`}>{value}</p>
      {hint !== undefined && <p className="mt-0.5 truncate text-xs text-muted">{hint}</p>}
    </div>
  );
}

const COLUMNS: Record<number, string> = { 1: 'lg:grid-cols-1', 2: 'lg:grid-cols-2', 3: 'lg:grid-cols-3', 4: 'lg:grid-cols-4' };

export function StatRow({ stats }: { stats: Stat[] }) {
  return (
    <div className={`mb-4 grid grid-cols-2 gap-3 ${COLUMNS[Math.min(stats.length, 4)]}`}>
      {stats.map((stat) => <StatCard key={stat.label} {...stat} />)}
    </div>
  );
}
