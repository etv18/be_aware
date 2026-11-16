import { Link } from 'react-router-dom';

import { usePageTitle } from '@/lib/queries';

export function NotFound() {
  usePageTitle('Page not found');
  return (
    <div className="flex flex-col items-center px-6 py-20 text-center">
      <p className="text-sm font-medium">Page not found</p>
      <p className="mt-1 max-w-sm text-sm text-muted">There is nothing at this address. Use the menu, or go back <Link to="/" className="underline">home</Link>.</p>
    </div>
  );
}
