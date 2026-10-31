// The banks page. Markup: templates/banks.html
import { $, bindList, formatDate, recordForm } from './common.js';

const form = recordForm($('#record-dialog'), {
  path: '/banks',
  noun: 'bank',
  defaults: () => ({ name: '' }),
  fromRecord: (r) => ({ name: r.name }),
  toBody: (v) => ({ name: v.name }),
  onSaved: () => list.reload(),
});

const list = bindList({
  path: '/banks',
  form,
  noun: 'bank',
  cells: (row) => ({ name: row.name, added: formatDate(row.created_at) }),
});
