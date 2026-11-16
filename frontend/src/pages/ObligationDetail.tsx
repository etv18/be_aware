// One loan or one debt: its figures and its payments. (templates/loan.html + loan.js, debt.html + debt.js)
import { useParams } from 'react-router-dom';

import { Icon } from '@/components/Icon';
import { PaymentForm } from '@/components/forms/shared';
import { PageHeader, StatRow } from '@/components/ui/page';
import { RowActions, TableCard } from '@/components/ui/table';
import { useCrud } from '@/lib/crud';
import { formatDate, money, source, sum } from '@/lib/format';
import { useReport, usePageTitle } from '@/lib/queries';
import type { Debt, Loan, Payment } from '@/types';

function ObligationDetail({ kind }: { kind: 'loan' | 'debt' }) {
  const loan = kind === 'loan';
  const word = loan ? 'Loan' : 'Debt';
  usePageTitle(word);
  const id = Number(useParams().id);
  const base = loan ? '/loans' : '/debts';

  const record = useReport<Loan | Debt>(`${base}/${id}`);
  const { rows, filters, onFilters, editing, setEditing, onDelete } = useCrud<Payment>({
    path: `${base}/${id}/payments`, recordPath: loan ? '/loan_payments' : '/debt_payments', noun: 'payment', localFilter: true,
  });
  const r = record.data;
  const filtering = Boolean(filters.q || (filters.start && filters.end));

  return (
    <>
      <PageHeader
        title={r?.person_name ?? ''} subtitle={r ? r.description || `${word} created ${new Date(r.created_at ?? '').toLocaleDateString()}` : ''}
        back={{ to: base, label: loan ? 'Loans' : 'Debts' }}
      />

      <StatRow stats={[
        { label: 'Amount', value: r ? money(r.amount) : '–' },
        { label: 'Paid', value: r ? money(r.total_paid) : '–' },
        { label: 'Remaining', value: r ? money(r.remaining_amount) : '–' },
        { label: 'Status', value: r ? (r.is_active ? 'Active' : 'Paid') : '–' },
      ]} />

      <div className="mb-3 flex items-center justify-between gap-3">
        <h2 className="text-base font-semibold">Payments</h2>
        <button type="button" className="btn btn-primary" onClick={() => setEditing('new')}><Icon name="plus" />New payment</button>
      </div>

      <TableCard
        headers={[['Date', ''], [loan ? 'Received in' : 'Paid from', 'hidden sm:table-cell'], ['Amount', 'text-right']]}
        placeholder="Search description or amount…"
        empty={{ text: 'No payments yet.' }}
        count={rows.length} filters={filters} onFilters={onFilters}
        total={{ label: `${filtering ? 'Filtered total' : 'Total'} · ${rows.length} ${rows.length === 1 ? 'record' : 'records'}`, value: money(sum(rows.map((p) => p.amount))) }}
      >
        {rows.map((row) => (
          <tr key={row.id}>
            <td className="whitespace-nowrap">{formatDate(row.created_at)}</td>
            <td className="hidden sm:table-cell">{source(row)}</td>
            <td className={`num text-right font-medium ${loan ? 'text-positive' : 'text-negative'}`}>{money(row.amount)}</td>
            <RowActions onEdit={() => setEditing(row)} onDelete={() => onDelete(row)} />
          </tr>
        ))}
      </TableCard>

      {editing && <PaymentForm key={editing === 'new' ? 'new' : editing.id} kind={kind} parentId={id} record={editing === 'new' ? null : editing} onClose={() => setEditing(null)} />}
    </>
  );
}

export const LoanDetail = () => <ObligationDetail kind="loan" />;
export const DebtDetail = () => <ObligationDetail kind="debt" />;
