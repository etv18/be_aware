// The shell every page shares: top navbar from 1024px up, top bar and drawer below that. (templates/layout.html + static/js/app.js)
import { useQueryClient } from '@tanstack/react-query';
import { useEffect, useRef, useState, type CSSProperties, type KeyboardEvent, type ReactNode } from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';

import { Icon } from '@/components/Icon';
import { useTheme, useToast } from '@/components/Providers';
import { api } from '@/lib/api';
import { GROUPS, currentItem, type NavGroup, type NavItem } from '@/lib/nav';
import { useDashboard, useSession } from '@/lib/queries';

const moduleStyle = (key: string) => ({ '--module': `var(--m-${key})` }) as CSSProperties;

function NavLink({ item, className, style, children, onClick, role }: { item: NavItem; className: string; style?: CSSProperties; children: ReactNode; onClick?: () => void; role?: string }) {
  return <Link to={item.path} className={className} style={style} onClick={onClick} role={role}>{children}</Link>;
}

function EnvBadge({ className = '' }: { className?: string }) {
  const session = useSession().data?.data;
  if (!session || session.env_name === 'production') return null;
  return <span className={`env-badge ${className}`} data-env={session.env_name} title={`Running with APP_ENV=${session.env_name}`}>{session.env_label}</span>;
}

function Count({ item, className }: { item: NavItem; className: string }) {
  const dashboard = useDashboard().data;
  const count = item.key === 'loans' ? dashboard?.active_loans : item.key === 'debts' ? dashboard?.active_debts : 0;
  return count ? <span className={`ml-auto rounded px-1.5 text-xs ${className}`}>{count}</span> : null;
}

/** One dropdown of the navbar. Arrow keys move between the entries, Esc closes and gives the focus back. */
function NavMenu({ group, current, open, onToggle, onClose }: { group: NavGroup; current: NavItem | null; open: boolean; onToggle: () => void; onClose: () => void }) {
  const trigger = useRef<HTMLButtonElement>(null);
  const panel = useRef<HTMLDivElement>(null);
  const active = group.items.some((item) => item.key === current?.key);

  function onKeyDown(event: KeyboardEvent) {
    if (event.key === 'Escape' && open) { onClose(); trigger.current?.focus(); return; }
    if (!open || !['ArrowDown', 'ArrowUp'].includes(event.key)) return;
    event.preventDefault();
    const entries = [...(panel.current?.querySelectorAll('a') ?? [])];
    const at = entries.indexOf(document.activeElement as HTMLAnchorElement);
    entries[(event.key === 'ArrowDown' ? at + 1 : at - 1 + entries.length) % entries.length]?.focus();
  }

  return (
    <div className="relative" data-menu onKeyDown={onKeyDown}>
      <button ref={trigger} type="button" className={`nav-link ${active ? 'nav-link-active' : ''}`} style={active && current ? moduleStyle(current.key) : undefined}
        aria-expanded={open} aria-haspopup="true" onClick={onToggle}>
        <Icon name={group.icon} /><span>{group.name}</span><Icon name="chevron-down" className="size-3.5 opacity-70" />
      </button>
      <div ref={panel} className={`menu-panel ${open ? '' : 'hidden'}`} role="menu">
        {group.items.map((item) => (
          <NavLink key={item.key} item={item} style={moduleStyle(item.key)} onClick={onClose} role="menuitem"
            className={`menu-item ${item.key === current?.key ? 'menu-item-active' : ''}`}>
            <span className="menu-icon"><Icon name={item.icon} /></span><span>{item.label}</span>
            <Count item={item} className="bg-module/15 font-medium text-module" />
          </NavLink>
        ))}
      </div>
    </div>
  );
}

export function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  const client = useQueryClient();
  const { toastError } = useToast();
  const { toggle } = useTheme();
  const { item: current, group: currentGroup } = currentItem(location.pathname);

  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const [drawer, setDrawer] = useState(false);

  // each page's color comes from <body data-module>
  useEffect(() => { document.body.dataset.module = current?.key ?? ''; }, [current?.key]);
  // a click anywhere else, Esc, or going to another page closes the menus
  useEffect(() => {
    const away = (event: MouseEvent) => { if (!(event.target as HTMLElement).closest('[data-menu]')) setOpenMenu(null); };
    const escape = (event: globalThis.KeyboardEvent) => { if (event.key === 'Escape') setDrawer(false); };
    document.addEventListener('click', away);
    document.addEventListener('keydown', escape);
    return () => { document.removeEventListener('click', away); document.removeEventListener('keydown', escape); };
  }, []);
  useEffect(() => { setOpenMenu(null); setDrawer(false); }, [location.pathname]);
  useEffect(() => { document.body.classList.toggle('overflow-hidden', drawer); }, [drawer]);

  async function logout() {
    try {
      await api.post('/logout');
      client.clear();
      navigate('/login');
    } catch (error) {
      toastError(error);
    }
  }

  const label = current?.label ?? 'Be Aware';
  const glyph = current?.icon ?? 'eye';

  return (
    <>
      {/* top navbar (tablet and desktop) */}
      <header className="sticky top-0 z-30 hidden border-b border-line bg-surface lg:block">
        <div className="mx-auto flex h-14 max-w-[1440px] items-center gap-2 px-4 sm:px-6 lg:gap-4 lg:px-8">
          <Link to="/" className="flex shrink-0 items-center gap-2.5 text-sm font-semibold" aria-label="Be Aware">
            <span className="flex size-8 items-center justify-center rounded-lg bg-ink text-ink-inverse"><Icon name="eye" /></span><span className="hidden lg:inline">Be Aware</span>
          </Link>

          <nav className="flex min-w-0 flex-1 items-center gap-0.5 lg:gap-1" aria-label="Main">
            {GROUPS.map((group) => group.items.length === 1 ? (
              <NavLink key={group.name} item={group.items[0]} style={moduleStyle(group.items[0].key)}
                className={`nav-link ${group.items[0].key === current?.key ? 'nav-link-active' : ''}`}>
                <Icon name={group.items[0].icon} /><span>{group.items[0].label}</span>
              </NavLink>
            ) : (
              <NavMenu key={group.name} group={group} current={current} open={openMenu === group.name}
                onToggle={() => setOpenMenu(openMenu === group.name ? null : group.name)} onClose={() => setOpenMenu(null)} />
            ))}
          </nav>

          <div className="flex shrink-0 items-center gap-1">
            <EnvBadge className="mr-1" />
            <button type="button" className="btn-icon" aria-label="Switch theme" onClick={toggle}><Icon name="sun-moon" /></button>
            <button type="button" className="btn-icon" aria-label="Log out" onClick={logout}><Icon name="log-out" /></button>
          </div>
        </div>
      </header>

      {/* top bar (phone) */}
      <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-line bg-surface px-4 lg:hidden">
        <button type="button" className="btn-icon -ml-1.5 size-9" aria-label="Open menu" onClick={() => setDrawer(true)}><Icon name="menu" className="size-5" /></button>
        <span className="flex min-w-0 items-center gap-2 text-sm font-semibold">
          <span className="flex size-7 shrink-0 items-center justify-center rounded-lg bg-module text-on-module"><Icon name={glyph} className="size-4" /></span>
          <span className="truncate">{label}</span>
        </span>
        <EnvBadge className="ml-auto" />
      </header>

      {/* drawer (phone) */}
      {drawer && <div className="fixed inset-0 z-40 bg-black/50 lg:hidden" onClick={() => setDrawer(false)} />}
      <aside className={`fixed inset-y-0 left-0 z-50 flex w-72 max-w-[85%] flex-col border-r border-line bg-surface transition-transform duration-200 lg:hidden ${drawer ? '' : '-translate-x-full'}`} aria-label="Menu">
        <div className="flex h-14 items-center justify-between border-b border-line px-4">
          <span className="flex items-center gap-2 text-sm font-semibold"><span className="flex size-8 items-center justify-center rounded-lg bg-ink text-ink-inverse"><Icon name="eye" /></span>Be Aware</span>
          <button type="button" className="btn-icon" aria-label="Close menu" onClick={() => setDrawer(false)}><Icon name="x" /></button>
        </div>
        <div className="flex-1 overflow-y-auto p-3">
          {GROUPS.map((group) => (
            <div key={group.name}>
              {group.items.length > 1 && <p className="mb-1 mt-4 px-3 text-xs font-medium uppercase tracking-wide text-faint">{group.name}</p>}
              {group.items.map((item) => (
                <NavLink key={item.key} item={item} style={moduleStyle(item.key)} onClick={() => setDrawer(false)}
                  className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm ${item.key === current?.key ? 'bg-module font-medium text-on-module' : 'text-ink hover:bg-sunken'}`}>
                  <span className={item.key === current?.key ? '' : 'text-module'}><Icon name={item.icon} /></span><span>{item.label}</span>
                  <Count item={item} className="bg-ink-inverse/20" />
                </NavLink>
              ))}
            </div>
          ))}
        </div>
        <div className="flex gap-2 border-t border-line p-3">
          <button type="button" className="btn btn-outline flex-1" onClick={toggle}><Icon name="sun-moon" />Theme</button>
          <button type="button" className="btn btn-outline flex-1" onClick={logout}><Icon name="log-out" />Log out</button>
        </div>
      </aside>

      <main>
        <div className="mx-auto w-full max-w-[1280px] px-4 py-5 sm:px-6 md:py-8 lg:px-8">
          <span className="module-badge mb-4 hidden lg:inline-flex">
            <Icon name={glyph} className="size-3.5" />{currentGroup && currentGroup.name !== label ? `${currentGroup.name} · ` : ''}{label}
          </span>
          <Outlet />
        </div>
      </main>
    </>
  );
}
