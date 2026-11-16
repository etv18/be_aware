// Every payment on every loan / every debt, read only. (templates/loan_payments.html, debt_payments.html)
import { PageHeader } from '@/components/ui/page';
import { TableCard } from '@/components/ui/table';
import { useCrud, useOpenRow } from '@/lib/crud';
import { formatDate, money, source } from '@/lib/format';
import { usePageTitle } from '@/lib/queries';
import type { Payment } from '@/types';

function PaymentList({ kind }: { kind: 'loan' | 'debt' }) {
  const loan = kind === 'loan';
  const title = loan ? 'Loan payments' : 'Debt payments';
  usePageTitle(title);
  const openRow = useOpenRow();
  const { rows, filters, onFilters } = useCrud<Payment>({ path: loan ? '/loan_payments' : '/debt_payments', noun: 'payment' });

  return (
    <>
      <PageHeader title={title} subtitle={loan ? 'Everything people paid back, across all loans.' : 'Everything you paid, across all debts.'} />

      <TableCard
        headers={[['Person', ''], [loan ? 'Received in' : 'Paid from', 'hidden sm:table-cell'], ['Date', 'hidden sm:table-cell'], ['Amount', 'text-right']]}
        placeholder="Search person or account…" actions={false} openRows
        count={rows.length} filters={filters} onFilters={onFilters}
      >
        {rows.map((row) => {
          const parent = 'loan_id' in row ? row.loan_id : 'debt_id' in row ? row.debt_id : null; // double click: the loan / debt it belongs to
          return (
            <tr key={row.id} {...(parent ? openRow(`/${loan ? 'loans' : 'debts'}/${parent}`) : {})}>
              <td className="font-medium">
                <span className="block">{row.person_name || '–'}</span>
                <span className="block text-xs font-normal text-muted sm:hidden">{`${source(row)} · ${formatDate(row.created_at)}`}</span>
              </td>
              <td className="hidden sm:table-cell">{source(row)}</td>
              <td className="hidden whitespace-nowrap text-muted sm:table-cell">{formatDate(row.created_at)}</td>
              <td className={`num text-right font-medium ${loan ? 'text-positive' : 'text-negative'}`}>{money(row.amount)}</td>
            </tr>
          );
        })}
      </TableCard>
    </>
  );
}

export const LoanPayments = () => <PaymentList kind="loan" />;
export const DebtPayments = () => <PaymentList kind="debt" />;
