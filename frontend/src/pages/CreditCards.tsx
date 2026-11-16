// The credit cards page. (templates/credit_cards.html + static/js/credit_cards.js)
import { useState } from 'react';
import { Link } from 'react-router-dom';

import { Icon } from '@/components/Icon';
import { CardPaymentForm } from '@/components/forms/shared';
import { useToast } from '@/components/Providers';
import { AmountField, FormDialog, SelectField, TextField } from '@/components/ui/form';
import { PageHeader, StatRow } from '@/components/ui/page';
import { RowActions, TableCard } from '@/components/ui/table';
import { useCrud, useOpenRow } from '@/lib/crud';
import { idOrNull, money, sum } from '@/lib/format';
import { useOptions, usePageTitle, useSave } from '@/lib/queries';
import type { CreditCard } from '@/types';

function CardForm({ record, onClose }: { record: CreditCard | null; onClose: () => void }) {
  const options = useOptions().data;
  const save = useSave('/credit_cards');
  const { toast } = useToast();
  const [values, setValues] = useState({ nick_name: record?.nick_name ?? '', limit: record?.limit ?? '', amount_available: record?.amount_available ?? '', bank_id: String(record?.bank_id ?? '') });
  const set = (key: keyof typeof values) => (value: string) => setValues((current) => ({ ...current, [key]: value }));

  async function submit() {
    await save.mutateAsync({ id: record?.id, body: { nick_name: values.nick_name, limit: values.limit, amount_available: values.amount_available, bank_id: idOrNull(values.bank_id) } });
    toast(`Credit card ${record ? 'updated' : 'created'}.`);
    onClose();
  }

  return (
    <FormDialog open title={record ? 'Edit credit card' : 'New credit card'} onClose={onClose} onSubmit={submit}>
      <TextField name="nick_name" label="Nickname" value={values.nick_name} onChange={set('nick_name')} />
      <AmountField name="limit" label="Credit limit" value={values.limit} onChange={set('limit')} />
      <AmountField name="amount_available" label="Available credit" value={values.amount_available} onChange={set('amount_available')} />
      <SelectField name="bank_id" label="Bank" blank="Choose a bank" value={values.bank_id} onChange={set('bank_id')} items={(options?.banks ?? []).map((b) => ({ id: b.id, label: b.name }))} />
    </FormDialog>
  );
}

export function CreditCards() {
  usePageTitle('Credit cards');
  const openRow = useOpenRow();
  const { rows, editing, setEditing, onDelete } = useCrud<CreditCard>({ path: '/credit_cards', noun: 'credit card', undo: 'It is hidden; its history stays.' });
  const [paying, setPaying] = useState<CreditCard | null>(null);

  return (
    <>
      <PageHeader title="Credit cards" subtitle="Limits, what you used and what is left." newLabel="New card" onNew={() => setEditing('new')}>
        <Link to="/card_ledger" className="btn btn-outline"><Icon name="book-open" />Ledger</Link>
      </PageHeader>

      <StatRow stats={[{ label: 'Used', value: money(sum(rows.map((r) => r.used))) }, { label: 'Available', value: money(sum(rows.map((r) => r.amount_available))) }]} />

      <TableCard
        headers={[['Card', ''], ['Bank', 'hidden sm:table-cell'], ['Limit', 'hidden md:table-cell text-right'], ['Used', 'text-center'], ['Available', 'hidden sm:table-cell text-right']]}
        count={rows.length} openRows
      >
        {rows.map((row) => (
          <tr key={row.id} {...openRow(`/credit_cards/${row.id}`)}>
            <td className="font-medium">{row.nick_name}</td>
            <td className="hidden sm:table-cell">{row.bank_name || '–'}</td>
            <td className="num hidden text-right md:table-cell">{money(row.limit)}</td>
            <td className="num text-center text-orange-500 font-bold">{money(row.used)}</td>
            <td className="num hidden text-right font-medium sm:table-cell">{money(row.amount_available)}</td>
            <RowActions extra={row.is_active ? [{ icon: 'banknote', label: 'Pay the card', onClick: () => setPaying(row) }] : []} onEdit={() => setEditing(row)} onDelete={() => onDelete(row)} />
          </tr>
        ))}
      </TableCard>

      {editing && <CardForm key={editing === 'new' ? 'new' : editing.id} record={editing === 'new' ? null : editing} onClose={() => setEditing(null)} />}
      {paying && <CardPaymentForm card={paying} onClose={() => setPaying(null)} />}
    </>
  );
}
