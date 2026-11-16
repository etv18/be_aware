// A card with a search bar, a table and its empty state. (partials/ui.html: filter_bar, table_card, row_actions)
import { useEffect, useState, type ReactNode } from 'react';

import { Icon } from '@/components/Icon';
import type { Filters } from '@/lib/queries';

function useDebounced<T>(value: T, wait = 280): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), wait);
    return () => clearTimeout(timer);
  }, [value, wait]);
  return debounced;
}

/** Search box + date range + clear button. Reports {q, start, end}; the dates only count when both are set. */
export function FilterBar({ placeholder, onChange }: { placeholder: string; onChange: (filters: Filters) => void }) {
  const [text, setText] = useState('');
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const q = useDebounced(text);

  useEffect(() => {
    onChange({ ...(q ? { q } : {}), ...(start && end ? { start, end } : {}) });
  }, [q, start, end, onChange]);

  return (
    <div className="flex flex-col gap-2 border-b border-line p-3 sm:flex-row sm:items-center">
      <div className="relative flex-1">
        <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-faint"><Icon name="search" /></span>
        <input className="input pl-9" type="search" placeholder={placeholder} aria-label="Search" value={text} onChange={(e) => setText(e.target.value)} />
      </div>
      <div className="flex items-center gap-2">
        <input className="input w-full sm:w-40" type="date" aria-label="From date" value={start} onChange={(e) => setStart(e.target.value)} />
        <span className="text-faint">–</span>
        <input className="input w-full sm:w-40" type="date" aria-label="To date" value={end} onChange={(e) => setEnd(e.target.value)} />
        <button type="button" className="btn-icon shrink-0" title="Clear filters" aria-label="Clear filters" onClick={() => { setText(''); setStart(''); setEnd(''); }}>
          <Icon name="filter-x" />
        </button>
      </div>
    </div>
  );
}

/**
 * headers: [label, classes][] — 'hidden sm:table-cell' hides a column on a phone, 'text-right' aligns numbers.
 * children: the rows (<tr>), already drawn by the page. note: shown while no search is active.
 * total: adds a "Total · n records" line.
 */
export function TableCard({ headers, children, count, filters, onFilters, placeholder = 'Search…', note, empty, total, actions = true }: {
  headers: [string, string][];
  children: ReactNode;
  count: number;                                       // how many rows there are (0 shows the empty state)
  filters?: Filters;                                   // what is being searched now (to say "Nothing matches")
  onFilters?: (filters: Filters) => void;              // no onFilters: no search bar
  placeholder?: string;
  note?: string;
  empty?: { title?: string; text?: string };
  total?: { label: string; value: string };
  actions?: boolean;
}) {
  const filtering = Boolean(filters?.q || (filters?.start && filters?.end));

  return (
    <section className="card overflow-hidden">
      {onFilters && <FilterBar placeholder={placeholder} onChange={onFilters} />}
      <div className="table-wrap table-scroll">
        <table className="table">
          <thead>
            <tr>
              {headers.map(([label, classes]) => <th key={label} className={classes}>{label}</th>)}
              {actions && <th className="w-px"><span className="sr-only">Actions</span></th>}
            </tr>
          </thead>
          <tbody>{children}</tbody>
        </table>
      </div>
      {count === 0 && (
        <div className="flex flex-col items-center px-6 py-14 text-center">
          <span className="mb-3 flex size-10 items-center justify-center rounded-full bg-sunken text-muted"><Icon name="inbox" /></span>
          <p className="text-sm font-medium">{filtering ? 'Nothing matches' : empty?.title || 'Nothing here yet'}</p>
          <p className="mt-1 max-w-sm text-sm text-muted">{filtering ? 'Try other words or another date range.' : empty?.text}</p>
        </div>
      )}
      {total && (
        <div className="flex items-center justify-between gap-3 border-t border-line bg-sunken/40 px-4 py-2.5 text-sm">
          <span className="text-muted">{total.label}</span>
          <span className="num font-semibold">{total.value}</span>
        </div>
      )}
      {note && !filtering && <p className="border-t border-line px-4 py-2.5 text-xs text-muted">{note}</p>}
    </section>
  );
}

/** The buttons cell of a row. extra: more buttons before edit / delete. */
export function RowActions({ onEdit, onDelete, extra = [] }: {
  onEdit?: () => void; onDelete?: () => void; extra?: { icon: 'banknote'; label: string; onClick: () => void }[];
}) {
  return (
    <td>
      <div className="flex justify-end gap-0.5">
        {extra.map((button) => (
          <button key={button.label} type="button" className="btn-icon" title={button.label} aria-label={button.label} onClick={button.onClick}><Icon name={button.icon} /></button>
        ))}
        {onEdit && <button type="button" className="btn-icon" title="Edit" aria-label="Edit" onClick={onEdit}><Icon name="pencil" /></button>}
        {onDelete && <button type="button" className="btn-icon btn-icon-danger" title="Delete" aria-label="Delete" onClick={onDelete}><Icon name="trash-2" /></button>}
      </div>
    </td>
  );
}
