// The icons the app uses (Lucide). To use another one: import it here and add its name to ICONS.
import {
  ArrowDownToLine, ArrowLeftRight, ArrowUpFromLine, Banknote, ChevronDown, ChevronLeft, CircleAlert, CircleCheck, Coins,
  CreditCard, Eye, FilterX, HandCoins, Handshake, House, Inbox, Landmark, LogOut, Menu, Pencil, Plus, Receipt,
  ScrollText, Search, SunMoon, Tags, Trash2, TrendingUp, Wallet, WalletCards, X, type LucideIcon,
} from 'lucide-react';

const ICONS = {
  'arrow-down-to-line': ArrowDownToLine, 'arrow-left-right': ArrowLeftRight, 'arrow-up-from-line': ArrowUpFromLine,
  banknote: Banknote, 'chevron-down': ChevronDown, 'chevron-left': ChevronLeft, 'circle-alert': CircleAlert,
  'circle-check': CircleCheck, coins: Coins, 'credit-card': CreditCard, eye: Eye, 'filter-x': FilterX,
  'hand-coins': HandCoins, handshake: Handshake, house: House, inbox: Inbox, landmark: Landmark, 'log-out': LogOut,
  menu: Menu, pencil: Pencil, plus: Plus, receipt: Receipt, 'scroll-text': ScrollText, search: Search,
  'sun-moon': SunMoon, tags: Tags, 'trash-2': Trash2, 'trending-up': TrendingUp, wallet: Wallet,
  'wallet-cards': WalletCards, x: X,
} satisfies Record<string, LucideIcon>;

export type IconName = keyof typeof ICONS;

export function Icon({ name, className = '' }: { name: IconName; className?: string }) {
  const Glyph = ICONS[name];
  return <Glyph className={`icon ${className}`} aria-hidden="true" />;
}
