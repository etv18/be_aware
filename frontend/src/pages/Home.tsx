// The home page. (templates/home.html + static/js/home.js)
import { useEffect, useRef, useState } from 'react';

import { Icon } from '@/components/Icon';
import { drawChart } from '@/components/charts/draw';
import { ReportChart } from '@/components/charts/ReportChart';
import { useTheme } from '@/components/Providers';
import { PageHeader, Tile } from '@/components/ui/page';
import { MONTHS, money, sum, titleCase, toNumber } from '@/lib/format';
import { useDashboard, useOptions, usePageTitle, useReport } from '@/lib/queries';
import type { CashFlow, YearlyAll } from '@/types';

const KIND_KEY = 'home-chart-kind';
const today = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? '' : 's'}`;
const sign = (value: number) => (value < 0 ? 'text-negative' : value > 0 ? 'text-positive' : 'text-faint');

/** The doughnut of this month: incomes against expenses. */
function ThisMonth({ incomes, expenses }: { incomes: number; expenses: number }) {
  const { theme } = useTheme();
  const canvas = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvas.current) return;
    const chart = drawChart(canvas.current, {
      type: 'doughnut', labels: ['Incomes', 'Expenses'], legend: false,
      series: [{ label: 'This month', data: incomes + expenses === 0 ? [0, 0] : [incomes, expenses], color: ['c-incomes', 'c-expenses'] }],
    });
    return () => chart.destroy();
  }, [incomes, expenses, theme]);

  return <div className="relative mx-auto h-48 max-w-[14rem]"><canvas ref={canvas} /></div>;
}

function MonthRow({ label, incomes, expenses, strong }: { label: string; incomes: number; expenses: number; strong: boolean }) {
  const balance = incomes - expenses;
  return (
    <tr>
      <td className={strong ? 'font-semibold' : 'font-medium'}>{label}</td>
      <td className={`num text-right ${strong ? 'font-semibold' : incomes ? '' : 'text-faint'}`}>{money(incomes)}</td>
      <td className={`num text-right ${strong ? 'font-semibold' : expenses ? '' : 'text-faint'}`}>{money(expenses)}</td>
      <td className={`num text-right ${strong ? 'font-semibold' : 'font-medium'} ${sign(balance)}`}>{money(balance)}</td>
    </tr>
  );
}

export function Home() {
  usePageTitle('Home');
  const dashboard = useDashboard().data;
  const years = useOptions().data?.years;

  const [kind, setKind] = useState<'bar' | 'line'>(() => {
    try { return localStorage.getItem(KIND_KEY) === 'line' ? 'line' : 'bar'; } catch { return 'bar'; } // private mode
  });
  const pickKind = (next: 'bar' | 'line') => {
    setKind(next);
    try { localStorage.setItem(KIND_KEY, next); } catch { /* private mode */ }
  };

  const thisYear = new Date().getFullYear();
  const [picked, setPicked] = useState<number | null>(null);
  const year = picked ?? (years?.includes(thisYear) || !years?.length ? thisYear : years[0]); // this year, or the latest one that has records

  const flow = useReport<CashFlow>('/reports/cash_flow', { year }, years !== undefined);
  const all = useReport<YearlyAll>('/reports/yearly/all', { year }, years !== undefined);

  const incomes = toNumber(dashboard?.month.incomes);
  const expenses = toNumber(dashboard?.month.expenses);
  const monthly = flow.data?.report;

  return (
    <>
      <PageHeader title="Home" subtitle={today} />

      {/* the figures that matter today */}
      <div className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
        <Tile to="/cash_ledger" icon="coins" label="Cash on hand" value={dashboard ? money(dashboard.cash_balance) : '–'} />
        <Tile to="/bank_accounts" icon="wallet" label="In bank accounts" value={dashboard ? money(dashboard.bank_total) : '–'} />
        <Tile to="/credit_cards" icon="credit-card" label="Used on cards" value={dashboard ? money(dashboard.cards_used) : '–'} />
        <Tile to="/loans" icon="hand-coins" label="To collect" value={dashboard ? money(dashboard.to_collect) : '–'} hint={dashboard ? plural(dashboard.active_loans, 'active loan') : ''} />
        <Tile to="/debts" icon="scroll-text" label="To pay" value={dashboard ? money(dashboard.to_pay) : '–'} hint={dashboard ? plural(dashboard.active_debts, 'active debt') : ''} />
        <Tile to="/expenses" icon="trending-up" label="Left this month" value={dashboard ? money(incomes - expenses) : '–'} />
      </div>

      <div className="mb-6 grid gap-4 lg:grid-cols-3">
        {/* incomes and expenses, month by month */}
        <ReportChart className="lg:col-span-2" title="Incomes and expenses"
          options={monthly ? { type: kind, series: [{ label: 'Incomes', data: monthly.incomes, color: 'c-incomes' }, { label: 'Expenses', data: monthly.expenses, color: 'c-expenses' }] } : null}>
          <div className="flex items-center gap-2">
            <div className="tabs" role="tablist" aria-label="Chart type">
              <button type="button" role="tab" aria-selected={kind === 'bar'} onClick={() => pickKind('bar')}><Icon name="chart-column" />Bars</button>
              <button type="button" role="tab" aria-selected={kind === 'line'} onClick={() => pickKind('line')}><Icon name="chart-line" />Lines</button>
            </div>
            <select className="select h-8 w-24 text-xs" aria-label="Year" value={year} onChange={(e) => setPicked(Number(e.target.value))}>
              {(years?.length ? years : [thisYear]).map((y) => <option key={y} value={y}>{y}</option>)}
            </select>
          </div>
        </ReportChart>

        {/* this month */}
        <section className="card card-pad">
          <h2 className="mb-4 text-sm font-semibold">This month</h2>
          <ThisMonth incomes={incomes} expenses={expenses} />
          <dl className="num mt-4 space-y-1.5 text-sm">
            <div className="flex justify-between"><dt className="flex items-center gap-2"><span className="dot" style={{ background: 'rgb(var(--c-incomes))' }} />Incomes</dt><dd>{dashboard ? money(dashboard.month.incomes) : '–'}</dd></div>
            <div className="flex justify-between"><dt className="flex items-center gap-2"><span className="dot" style={{ background: 'rgb(var(--c-expenses))' }} />Expenses</dt><dd>{dashboard ? money(dashboard.month.expenses) : '–'}</dd></div>
          </dl>
        </section>
      </div>

      {/* one row per month */}
      <section className="card mb-6 overflow-hidden">
        <h2 className="border-b border-line px-4 py-3 text-sm font-semibold">Month by month <span className="font-normal text-muted">· {year}</span></h2>
        <div className="table-wrap">
          <table className="table">
            <thead><tr><th>Month</th><th className="text-right">Incomes</th><th className="text-right">Expenses</th><th className="text-right">Balance</th></tr></thead>
            <tbody>
              {monthly && MONTHS.map((month, i) => <MonthRow key={month} label={month} incomes={toNumber(monthly.incomes[i])} expenses={toNumber(monthly.expenses[i])} strong={false} />)}
              {monthly && <MonthRow label="Total" incomes={sum(monthly.incomes)} expenses={sum(monthly.expenses)} strong />}
            </tbody>
          </table>
        </div>
      </section>

      {/* the year by kind of record */}
      <section className="card overflow-hidden">
        <h2 className="border-b border-line px-4 py-3 text-sm font-semibold">Year by kind of record</h2>
        <ul className="divide-y divide-line">
          {all.data && Object.entries(all.data.report).map(([name, months]) => {
            const total = sum(months);
            return (
              <li key={name} className="flex items-center justify-between px-4 py-2.5 text-sm">
                <span>{titleCase(name)}</span>
                <span className={`num ${total ? 'font-medium' : 'text-faint'}`}>{money(total)}</span>
              </li>
            );
          })}
        </ul>
      </section>
    </>
  );
}
