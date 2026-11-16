// The bank accounts page. (templates/bank_accounts.html + static/js/bank_accounts.js)
import { useState } from 'react';
import { Link } from 'react-router-dom';

import { Icon } from '@/components/Icon';
import { TransferForm } from '@/components/forms/shared';
import { useToast } from '@/components/Providers';
import { AmountField, FormDialog, SelectField, TextField } from '@/components/ui/form';
import { PageHeader, StatRow } from '@/components/ui/page';
import { RowActions, TableCard } from '@/components/ui/table';
import { useCrud, useOpenRow } from '@/lib/crud';
import { formatDate, idOrNull, money, sum } from '@/lib/format';
import { useOptions, usePageTitle, useSave } from '@/lib/queries';
import type { BankAccount } from '@/types';

function AccountForm({ record, onClose }: { record: BankAccount | null; onClose: () => void }) {
  const options = useOptions().data;
  const save = useSave('/bank_accounts');
  const { toast } = useToast();
  const [values, setValues] = useState({
    nick_name: record?.nick_name ?? '', account_number: record?.account_number ?? '', amount_available: record?.amount_available ?? '', bank_id: String(record?.bank_id ?? ''),
  });
  const set = (key: keyof typeof values) => (value: string) => setValues((current) => ({ ...current, [key]: value }));

  async function submit() {
    await save.mutateAsync({
      id: record?.id,
      body: { nick_name: values.nick_name, account_number: values.account_number || null, amount_available: values.amount_available, bank_id: idOrNull(values.bank_id) },
    });
    toast(`Bank account ${record ? 'updated' : 'created'}.`);
    onClose();
  }

  return (
    <FormDialog open title={record ? 'Edit bank account' : 'New bank account'} onClose={onClose} onSubmit={submit}>
      <TextField name="nick_name" label="Nickname" half value={values.nick_name} onChange={set('nick_name')} />
      <TextField name="account_number" label="Account number" optional half placeholder="Up to 6 characters" value={values.account_number} onChange={set('account_number')} />
      <AmountField name="amount_available" label="Balance" value={values.amount_available} onChange={set('amount_available')} />
      <SelectField name="bank_id" label="Bank" half blank="Choose a bank" value={values.bank_id} onChange={set('bank_id')} items={(options?.banks ?? []).map((b) => ({ id: b.id, label: b.name }))} />
    </FormDialog>
  );
}

export function BankAccounts() {
  usePageTitle('Bank accounts');
  const openRow = useOpenRow();
  const { rows, editing, setEditing, onDelete } = useCrud<BankAccount>({ path: '/bank_accounts', noun: 'bank account', undo: 'It is hidden; its history stays.' });
  const [transferFrom, setTransferFrom] = useState<BankAccount | null>(null);

  return (
    <>
      <PageHeader title="Bank accounts" subtitle="Where your money sits." newLabel="New account" onNew={() => setEditing('new')}>
        <Link to="/bank_ledger" className="btn btn-outline"><Icon name="book-open" />Ledger</Link>
      </PageHeader>

      <StatRow stats={[{ label: 'In all accounts', value: money(sum(rows.map((r) => r.amount_available))) }, { label: 'Accounts', value: rows.length }]} />

      <TableCard
        headers={[['Account', ''], ['Bank', 'hidden sm:table-cell'], ['Status', 'hidden md:table-cell'], ['Added', 'hidden lg:table-cell'], ['Balance', 'text-right']]}
        count={rows.length} openRows
      >
        {rows.map((row) => (
          <tr key={row.id} {...openRow(`/bank_accounts/${row.id}`)}>
            <td>
              <span className="block font-medium">{row.nick_name}</span>
              {row.account_number && <span className="block font-mono text-xs text-muted">{row.account_number}</span>}
            </td>
            <td className="hidden sm:table-cell">{row.bank_name || '–'}</td>
            <td className="hidden md:table-cell"><span className="tag">{row.is_active ? 'Active' : 'Inactive'}</span></td>
            <td className="hidden whitespace-nowrap text-muted lg:table-cell">{formatDate(row.created_at)}</td>
            <td className="num text-right font-medium">{money(row.amount_available)}</td>
            <RowActions extra={row.is_active ? [{ icon: 'arrow-left-right', label: 'Transfer', onClick: () => setTransferFrom(row) }] : []} onEdit={() => setEditing(row)} onDelete={() => onDelete(row)} />
          </tr>
        ))}
      </TableCard>

      {editing && <AccountForm key={editing === 'new' ? 'new' : editing.id} record={editing === 'new' ? null : editing} onClose={() => setEditing(null)} />}
      {transferFrom && <TransferForm from={transferFrom} onClose={() => setTransferFrom(null)} />}
    </>
  );
}
