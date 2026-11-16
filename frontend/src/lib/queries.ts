// Talking to the server from components: what to load (queries) and what to save (mutations).
// One rule keeps it simple: after anything is saved or deleted, everything on screen is loaded again.
import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';

import { api, fetchSession } from '@/lib/api';
import type { Dashboard, List, One, Options } from '@/types';

export type Filters = { q?: string; start?: string; end?: string };

export const useSession = () => useQuery({ queryKey: ['session'], queryFn: fetchSession, staleTime: Infinity });

/** Banks, accounts, cards, categories and years for the selects. */
export const useOptions = () => useQuery({ queryKey: ['options'], queryFn: () => api.get<One<Options>>('/options').then((r) => r.data), staleTime: Infinity });

export const useDashboard = () => useQuery({ queryKey: ['dashboard'], queryFn: () => api.get<One<Dashboard>>('/dashboard').then((r) => r.data) });

/** One report or one record: useReport<CashFlow>('/reports/cash_flow', { year: 2026 }). Loaded again after anything is saved. */
export function useReport<T>(path: string, params: Record<string, string | number> = {}, enabled = true) {
  return useQuery({ queryKey: ['report', path, params], queryFn: () => api.get<One<T>>(path, params).then((r) => r.data), enabled });
}

/** A list of records: useList<Expense, ExpenseListMeta>('/expenses', { q: 'pizza' }). The old rows stay on screen while the new ones load. */
export function useList<T, M = List<T>['meta']>(path: string, filters: Filters = {}) {
  return useQuery({
    queryKey: ['list', path, filters],
    queryFn: () => api.get<List<T, M>>(path, filters),
    placeholderData: keepPreviousData,
  });
}

/** Create (no id) or update (id) a record. `body` is the JSON the server validates. */
export function useSave(path: string) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id?: number; body: unknown }) => (id ? api.put<One<unknown>>(`${path}/${id}`, body) : api.post<One<unknown>>(path, body)),
    onSuccess: () => client.invalidateQueries(),
  });
}

export function useRemove(path: string) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.delete(`${path}/${id}`),
    onSuccess: () => client.invalidateQueries(),
  });
}

/** The tab title the Jinja pages had: "[DEV] Expenses · Be Aware". */
export function usePageTitle(title: string) {
  const session = useSession().data?.data;
  const badge = session && session.env_name !== 'production' ? `[${session.env_label}] ` : '';
  useEffect(() => { document.title = `${badge}${title} · Be Aware`; }, [badge, title]);
}
