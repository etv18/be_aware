// One expense category: its limit, what was spent and the expenses. Markup: templates/expense_category.html
import { $, api, money, setStats, sum, toastError } from './common.js';
import { recordsTabs } from './records.js';

const id = $('#page').dataset.id;

async function main() {
  const { data: { expense_category: category, records } } = await api.get(`/expense_categories/${id}/records`);
  const expenses = records.expenses || [];

  $('[data-page-title]').textContent = category.display_name;
  setStats({
    limit: Number(category.limit) > 0 ? money(category.limit) : 'No limit',
    spent: { text: money(sum(expenses, 'amount')), hint: `${expenses.length} expenses` },
  });
  recordsTabs($('[data-records]'), records);
}

main().catch(toastError);
