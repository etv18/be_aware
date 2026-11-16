import * as columns from '../domain/columns.js';
import { listPage } from './list-page.js';

listPage({
  resource: 'banks',
  title: 'Banks',
  subtitle: 'The institutions your accounts and cards belong to.',
  columns: columns.banks,
  newLabel: 'New bank',
  noFilters: true,
});
