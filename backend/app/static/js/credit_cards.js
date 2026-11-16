// The credit cards page. Markup: templates/credit_cards.html
import { $, bindList, idOrNull, money, recordForm, setStats, sum } from './common.js';
import { cardPaymentForm } from './forms.js';

const form = recordForm($('#record-dialog'), {
  path: '/credit_cards',
  noun: 'credit card',
  selects: { bank_id: ['banks', 'name', 'Choose a bank'] },
  defaults: () => ({ nick_name: '', limit: '', amount_available: '', bank_id: '' }),
  fromRecord: (r) => ({ nick_name: r.nick_name, limit: r.limit, amount_available: r.amount_available, bank_id: r.bank_id ?? '' }),
  toBody: (v) => ({ nick_name: v.nick_name, limit: v.limit, amount_available: v.amount_available, bank_id: idOrNull(v.bank_id) }),
  onSaved: () => list.reload(),
});

const payment = cardPaymentForm({ onSaved: () => list.reload() });

const list = bindList({
  path: '/credit_cards',
  form,
  noun: 'credit card',
  undo: 'It is hidden; its history stays.',
  open: (row) => { location.href = `/credit_cards/${row.id}`; }, // double click
  handlers: { pay: (row) => payment.open(row) },
  cells: (row) => {
    const share = Number(row.limit) > 0 ? Math.min(100, Math.round((Number(row.used) / Number(row.limit)) * 100)) : 0;
    return {
      name: row.nick_name,
      bank: row.bank_name || '–',
      limit: money(row.limit),
      used: money(row.used),
      share: `${share}%`,
      bar: { width: `${share}%`, class: share > 85 ? 'bg-negative' : 'bg-ink' }, // the usage bar turns red above 85%
      available: money(row.amount_available),
      pay: { show: row.is_active },
    };
  },
  onData: ({ rows }) => setStats({ used: money(sum(rows, 'used')), available: money(sum(rows, 'amount_available')) }),
});
