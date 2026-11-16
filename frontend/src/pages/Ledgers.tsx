// The cash ledger (you can add an adjustment) and the bank and card ledgers (read only). (templates/*_ledger.html)
import { useState } from 'react';

import { useToast } from '@/components/Providers';
import { AmountField, DateField, FormDialog } from '@/components/ui/form';
import { PageHeader, StatRow } from '@/components/ui/page';
import { RowActions, TableCard } from '@/components/ui/table';
import { useCrud } from '@/lib/crud';
import { formatDateTime, money, signed, titleCase, toInputValue } from '@/lib/format';
import { usePageTitle, useSave } from '@/lib/queries';
import type { BankLedgerRow, CardLedgerRow, CashLedgerRow } from '@/types';

function AdjustmentForm({ onClose }: { onClose: () => void }) {
  const save = useSave('/cash_ledger');
  const { toast } = useToast();
  const [values, setValues] = useState({ amount: '', created_at: toInputValue() });

  async function submit() {
    await save.mutateAsync({ body: { amount: values.amount, created_at: values.created_at || null } });
    toast('Adjustment created.');
    onClose();
  }

  return (
    <FormDialog open title="Cash adjustment" onClose={onClose} onSubmit={submit}>
      <AmountField help="Positive adds cash, negative takes it away." value={values.amount} onChange={(amount) => setValues({ ...values, amount })} />
      <DateField value={values.created_at} onChange={(created_at) => setValues({ ...values, created_at })} />
    </FormDialog>
  );
}

export function CashLedger() {
  usePageTitle('Cash ledger');
  const { rows, meta, filters, onFilters, editing, setEditing, onDelete } = useCrud<CashLedgerRow, { balance: string; count: number }>({ path: '/cash_ledger', noun: 'adjustment' });

  return (
    <>
      <PageHeader title="Cash ledger" subtitle="Every movement of the cash you hold." newLabel="Adjust cash" onNew={() => setEditing('new')} />
      <StatRow stats={[{ label: 'Cash on hand', value: meta ? money(meta.balance) : '–' }]} />

      <TableCard
        headers={[['Reference', ''], ['Type', 'hidden sm:table-cell'], ['Date', 'hidden sm:table-cell'], ['Amount', 'text-right']]}
        placeholder="Search reference or type…" count={rows.length} filters={filters} onFilters={onFilters}
      >
        {rows.map((row) => {
          const amount = signed(row.amount);
          return (
            <tr key={row.id}>
              <td>
                <span className="block font-mono text-xs font-medium">{row.reference_code}</span>
                <span className="block text-xs text-muted sm:hidden">{`${titleCase(row.type)} · ${formatDateTime(row.created_at)}`}</span>
              </td>
              <td className="hidden sm:table-cell"><span className="tag">{titleCase(row.type)}</span></td>
              <td className="hidden whitespace-nowrap text-muted sm:table-cell">{formatDateTime(row.created_at)}</td>
              <td className={`num text-right ${amount.className}`}>{amount.text}</td>
              {/* only manual adjustments can be deleted */}
              {row.is_adjustment ? <RowActions onDelete={() => onDelete(row)} /> : <td />}
            </tr>
          );
        })}
      </TableCard>

      {editing && <AdjustmentForm onClose={() => setEditing(null)} />}
    </>
  );
}

/** The bank and the card ledger: the same columns, another thing in the second one. */
function ProductLedger({ path, title, subtitle, productHeader, placeholder }: { path: '/bank_ledger' | '/card_ledger'; title: string; subtitle: string; productHeader: string; placeholder: string }) {
  usePageTitle(title);
  const { rows, filters, onFilters } = useCrud<BankLedgerRow | CardLedgerRow>({ path, noun: 'movement' });

  return (
    <>
      <PageHeader title={title} subtitle={subtitle} />

      <TableCard
        headers={[['Reference', ''], [productHeader, 'hidden sm:table-cell'], ['Type', 'hidden md:table-cell'], ['Date', 'hidden sm:table-cell'], ['Before', 'hidden lg:table-cell text-right'], ['After', 'hidden lg:table-cell text-right'], ['Amount', 'text-right']]}
        placeholder={placeholder} actions={false} count={rows.length} filters={filters} onFilters={onFilters}
      >
        {rows.map((row) => {
          const product = ('bank_account_name' in row ? row.bank_account_name : row.credit_card_name) || '–';
          const amount = signed(row.amount);
          return (
            <tr key={row.id}>
              <td>
                <span className="block font-mono text-xs font-medium">{row.reference_code}</span>
                <span className="block text-xs text-muted sm:hidden">{`${product} · ${formatDateTime(row.created_at)}`}</span>
              </td>
              <td className="hidden sm:table-cell">{product}</td>
              <td className="hidden md:table-cell"><span className="tag">{titleCase(row.transaction_type)}</span></td>
              <td className="hidden whitespace-nowrap text-muted sm:table-cell">{formatDateTime(row.created_at)}</td>
              <td className="num hidden text-right lg:table-cell">{money(row.before_balance)}</td>
              <td className="num hidden text-right lg:table-cell">{money(row.after_balance)}</td>
              <td className={`num text-right ${amount.className}`}>{amount.text}</td>
            </tr>
          );
        })}
      </TableCard>
    </>
  );
}

export const BankLedger = () => <ProductLedger path="/bank_ledger" title="Bank ledger" subtitle="Every movement of your bank accounts." productHeader="Account" placeholder="Search reference, account or type…" />;
export const CardLedger = () => <ProductLedger path="/card_ledger" title="Card ledger" subtitle="Every movement of your credit cards." productHeader="Card" placeholder="Search reference, card or type…" />;
