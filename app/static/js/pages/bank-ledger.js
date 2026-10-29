import * as columns from '../domain/columns.js';
import { listPage } from './list-page.js';

listPage({
  listPath: '/bank_transaction_ledger',
  title: 'Bank ledger',
  subtitle: 'Every movement of your bank accounts.',
  columns: columns.bankLedger,
  placeholder: 'Search reference, account or type…',
  readOnly: true,
});
