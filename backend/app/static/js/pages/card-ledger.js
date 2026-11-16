import * as columns from '../domain/columns.js';
import { listPage } from './list-page.js';

listPage({
  listPath: '/credit_card_ledger',
  title: 'Card ledger',
  subtitle: 'Every movement of your credit cards.',
  columns: columns.cardLedger,
  placeholder: 'Search reference, account or type…',
  readOnly: true,
});
