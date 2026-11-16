// What every list page does: load the rows, search them, open the form for a new or an existing row, ask before deleting.
// A page that needs more (a chart, extra buttons) just adds it next to what this returns.
import { useCallback, useMemo, useState, type MouseEvent } from 'react';
import { useNavigate } from 'react-router-dom';

import { useConfirm, useToast } from '@/components/Providers';
import { filterRows } from '@/lib/format';
import { useList, useRemove, type Filters } from '@/lib/queries';
import type { List } from '@/types';

type Options = {
  path: string;               // GET /api<path>
  noun: string;               // "expense": used in "Delete this expense?" and "Expense deleted."
  undo?: string;              // the second line of the delete question
  recordPath?: string;        // where one record lives, when it is not `path` (the payments of a loan)
  localFilter?: boolean;      // search in the browser instead of asking the server (a short list)
  query?: Filters;
};

const capitalize = (text: string) => text.charAt(0).toUpperCase() + text.slice(1);

export function useCrud<T extends { id: number }, M = List<T>['meta']>({ path, noun, undo = 'This cannot be undone.', recordPath = path, localFilter = false, query = {} }: Options) {
  const confirm = useConfirm();
  const { toast, toastError } = useToast();
  const remove = useRemove(recordPath);

  const [filters, setFilters] = useState<Filters>({});
  const onFilters = useCallback((next: Filters) => setFilters(next), []);
  const [editing, setEditing] = useState<T | 'new' | null>(null);

  const list = useList<T, M>(path, localFilter ? query : { ...query, ...filters });
  const all = list.data?.data;
  const rows = useMemo(() => (all ? (localFilter ? filterRows(all, filters) : all) : []), [all, localFilter, filters]);

  async function onDelete(row: T) {
    if (!(await confirm({ title: `Delete this ${noun}?`, text: undo }))) return;
    try {
      await remove.mutateAsync(row.id);
      toast(`${capitalize(noun)} deleted.`);
    } catch (error) {
      toastError(error);
    }
  }

  return { rows, meta: list.data?.meta, loading: list.isPending, filters, onFilters, editing, setEditing, onDelete };
}

/** A double click on a row opens its page: <tr {...openRow(`/loans/${row.id}`)}>. Clicks on a button inside the row do nothing. */
export function useOpenRow() {
  const navigate = useNavigate();
  return (to: string) => ({
    onDoubleClick: (event: MouseEvent) => {
      if ((event.target as HTMLElement).closest('button, a, input, select')) return;
      window.getSelection()?.removeAllRanges();
      navigate(to);
    },
  });
}
