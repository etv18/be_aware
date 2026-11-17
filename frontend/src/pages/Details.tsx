// The page of one bank account, one credit card or one expense category: its figures, a chart and everything that moved through it.
// (templates/bank_account.html, credit_card.html, expense_category.html and their scripts)
import { useState } from 'react';
import { useParams } from 'react-router-dom';

import { ReportChart } from '@/components/charts/ReportChart';
import { Icon } from '@/components/Icon';
import { CardPaymentForm, TransferForm } from '@/components/forms/shared';
import { PageHeader, StatRow } from '@/components/ui/page';
import { RecordsTabs } from '@/components/ui/records';
import { money, sum } from '@/lib/format';
import { usePageTitle, useReport } from '@/lib/queries';
import type { AccountCashFlow, BankAccountRecords, CardYearly, CreditCardRecords, ExpenseCategoryRecords } from '@/types';

const year = new Date().getFullYear();

export function BankAccountDetail() {
  usePageTitle('Bank account');
  const id = Number(useParams().id);
  const records = useReport<BankAccountRecords>(`/bank_accounts/${id}/records`);
  const flow = useReport<AccountCashFlow>(`/bank_accounts/${id}/reports/cash_flow`, { year });
  const [transferring, setTransferring] = useState(false);
  const account = records.data?.bank_account;

  return (
    <div>
      <PageHeader title={account?.nick_name ?? ''} subtitle={account ? [account.bank_name, account.account_number].filter(Boolean).join(' · ') : ''} back={{ to: '/bank_accounts', label: 'Bank accounts' }}>
        {account?.is_active && <button type="button" className="btn btn-primary" onClick={() => setTransferring(true)}><Icon name="arrow-left-right" />Transfer</button>}
      </PageHeader>

      <StatRow stats={[{ label: 'Balance', value: account ? money(account.amount_available) : '–' }, { label: 'Status', value: account ? (account.is_active ? 'Active' : 'Inactive') : '–' }]} />

      <ReportChart title={`Money in and out, per month · ${year}`} className="mb-6"
        options={flow.data ? { type: 'bar', series: [{ label: 'In', data: flow.data.incomings, color: 'c-incomes' }, { label: 'Out', data: flow.data.outgoings, color: 'c-expenses' }] } : null} />

      {records.data && <RecordsTabs records={records.data.records} bankProduct='bank_account'/>}
      {account && transferring && <TransferForm from={account} onClose={() => setTransferring(false)} />}
    </div>
  );
}

export function CreditCardDetail() {
  usePageTitle('Credit card');
  const id = Number(useParams().id);
  const records = useReport<CreditCardRecords>(`/credit_cards/${id}/records`);
  const yearly = useReport<CardYearly>(`/credit_cards/${id}/reports/yearly`, { year });
  const [paying, setPaying] = useState(false);
  const card = records.data?.credit_card;
  const info = yearly.data?.associations_info;

  return (
    <div>
      <PageHeader title={card?.nick_name ?? ''} subtitle={card?.bank_name || ''} back={{ to: '/credit_cards', label: 'Credit cards' }}>
        {card?.is_active && <button type="button" className="btn btn-primary" onClick={() => setPaying(true)}><Icon name="banknote" />Pay the card</button>}
      </PageHeader>

      <StatRow stats={[
        { label: 'Limit', value: card ? money(card.limit) : '–' },
        { label: 'Used', value: card ? money(card.used) : '–', valueClassName: 'text-orange-500' },
        { label: 'Available', value: card ? money(card.amount_available) : '–' },
      ]} />

      <ReportChart title={`Per month · ${year}`} className="mb-6"
        options={info ? {
          type: 'bar',
          series: [{ label: 'Expenses', data: info.expenses, color: 'c-expenses' }, { label: 'Payments', data: info.credit_card_payments, color: 'c-incomes' }, { label: 'Loans', data: info.loans, color: 'c-loans' }],
        } : null} />

      {records.data && <RecordsTabs records={records.data.records} bankProduct='credit_card'/>}
      {card && paying && <CardPaymentForm card={card} onClose={() => setPaying(false)} />}
    </div>
  );
}

export function ExpenseCategoryDetail() {
  usePageTitle('Expense category');
  const id = Number(useParams().id);
  const records = useReport<ExpenseCategoryRecords>(`/expense_categories/${id}/records`);
  const category = records.data?.expense_category;
  const expenses = records.data?.records.expenses ?? [];

  return (
    <div>
      <PageHeader title={category?.display_name ?? ''} back={{ to: '/expense_categories', label: 'Expense categories' }} />

      <StatRow stats={[
        { label: 'Monthly limit', value: category ? (Number(category.limit) > 0 ? money(category.limit) : 'No limit') : '–' },
        { label: 'Spent so far', value: records.data ? money(sum(expenses.map((e) => e.amount))) : '–', hint: records.data ? `${expenses.length} expenses` : '' },
      ]} />

      {records.data && <RecordsTabs records={records.data.records} bankProduct='expense'/>}
    </div>
  );
}
