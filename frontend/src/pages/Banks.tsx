// The banks page. (templates/banks.html + static/js/banks.js)
import { useState } from 'react';

import { Icon } from '@/components/Icon';
import { useToast } from '@/components/Providers';
import { FormDialog, TextField } from '@/components/ui/form';
import { PageHeader } from '@/components/ui/page';
import { RowActions, TableCard } from '@/components/ui/table';
import { useCrud } from '@/lib/crud';
import { formatDate } from '@/lib/format';
import { usePageTitle, useSave } from '@/lib/queries';
import type { Bank } from '@/types';

function BankForm({ record, onClose }: { record: Bank | null; onClose: () => void }) {
  const save = useSave('/banks');
  const { toast } = useToast();
  const [name, setName] = useState(record?.name ?? '');

  async function submit() {
    await save.mutateAsync({ id: record?.id, body: { name } });
    toast(`Bank ${record ? 'updated' : 'created'}.`);
    onClose();
  }

  return (
    <FormDialog open title={record ? 'Edit bank' : 'New bank'} onClose={onClose} onSubmit={submit}>
      <TextField name="name" label="Bank name" value={name} onChange={setName} />
    </FormDialog>
  );
}

export function Banks() {
  usePageTitle('Banks');
  const { rows, editing, setEditing, onDelete } = useCrud<Bank>({ path: '/banks', noun: 'bank' });

  return (
    <>
      <PageHeader title="Banks" subtitle="The institutions your accounts and cards belong to." newLabel="New bank" onNew={() => setEditing('new')} />

      <TableCard headers={[['Bank', ''], ['Added', 'hidden sm:table-cell']]} count={rows.length}>
        {rows.map((row) => (
          <tr key={row.id}>
            <td><span className="inline-flex items-center gap-2 font-medium"><span className="text-muted"><Icon name="landmark" /></span><span>{row.name}</span></span></td>
            <td className="hidden whitespace-nowrap text-muted sm:table-cell">{formatDate(row.created_at)}</td>
            <RowActions onEdit={() => setEditing(row)} onDelete={() => onDelete(row)} />
          </tr>
        ))}
      </TableCard>

      {editing && <BankForm key={editing === 'new' ? 'new' : editing.id} record={editing === 'new' ? null : editing} onClose={() => setEditing(null)} />}
    </>
  );
}
