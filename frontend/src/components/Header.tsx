/**
 * T-012 — en-tête applicatif mobile-first.
 *
 * Comportement :
 * - Hauteur fixe 56 px pour libérer la zone principale sur 360 px.
 * - Menu hamburger sous 768 px (tablette portrait).
 * - Liens conditionnels selon l'état d'authentification (`auth.user.role`).
 *   Les liens concrets (catalogue, panier, vendeur, admin) seront ajoutés par
 *   les modules M02/M04/M05/M11.
 *
 * Accessibilité :
 * - Bouton hamburger : aria-expanded, aria-controls, aria-label localisé.
 * - Liste de navigation : role="navigation", aria-label localisé.
 */

import type { ReactElement } from 'react';
import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import {
  selectCurrentRole,
  selectIsAuthenticated,
  logout,
} from '@/store/slices/authSlice';
import { LanguageSwitcher } from './LanguageSwitcher';

interface NavItem {
  to: string;
  labelKey: string;
  roles?: ReadonlyArray<'customer' | 'seller' | 'admin'>;
}

const NAV: ReadonlyArray<NavItem> = [
  { to: '/', labelKey: 'header.home' },
  { to: '/products', labelKey: 'header.catalog' },
  { to: '/orders', labelKey: 'header.myOrders', roles: ['customer'] },
  { to: '/seller', labelKey: 'header.dashboard', roles: ['seller'] },
  { to: '/admin', labelKey: 'header.dashboard', roles: ['admin'] },
];

export function Header(): ReactElement {
  const { t } = useTranslation('common');
  const isAuth = useAppSelector(selectIsAuthenticated);
  const role = useAppSelector(selectCurrentRole);
  const dispatch = useAppDispatch();
  const [menuOpen, setMenuOpen] = useState(false);

  const visibleNav = NAV.filter((item) => {
    if (item.roles === undefined) return true;
    if (role === null) return false;
    return item.roles.includes(role);
  });

  return (
    <header
      className="sticky top-0 z-30 flex items-center justify-between border-b border-ink-300 bg-white px-4"
      style={{ minHeight: 'var(--header-height)' }}
    >
      <NavLink to="/" className="flex items-center gap-2 font-semibold text-brand-700">
        <span aria-hidden="true">🛒</span>
        <span>{t('app.name')}</span>
      </NavLink>

      <button
        type="button"
        aria-controls="primary-nav"
        aria-expanded={menuOpen}
        aria-label={menuOpen ? t('header.closeMenu') : t('header.openMenu')}
        onClick={() => setMenuOpen((v) => !v)}
        className="rounded border border-ink-300 px-3 py-1 text-sm md:hidden"
      >
        ☰
      </button>

      <nav
        id="primary-nav"
        aria-label={t('app.name')}
        className={`${menuOpen ? 'flex' : 'hidden'} absolute inset-x-0 top-full flex-col gap-2 border-b border-ink-300 bg-white p-4 md:static md:flex md:flex-row md:items-center md:gap-4 md:border-0 md:p-0`}
      >
        {visibleNav.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            onClick={() => setMenuOpen(false)}
            className={({ isActive }) =>
              `rounded px-2 py-1 text-sm ${isActive ? 'bg-brand-50 text-brand-700' : 'text-ink-700 hover:bg-ink-100'}`
            }
          >
            {t(item.labelKey)}
          </NavLink>
        ))}

        <div className="md:ml-auto md:flex md:items-center md:gap-3">
          <LanguageSwitcher />
          {isAuth ? (
            <button
              type="button"
              onClick={() => {
                dispatch(logout());
                setMenuOpen(false);
              }}
              className="rounded bg-ink-100 px-3 py-1 text-sm hover:bg-ink-300"
            >
              {t('header.logout')}
            </button>
          ) : (
            <NavLink
              to="/login"
              onClick={() => setMenuOpen(false)}
              className="rounded bg-brand-500 px-3 py-1 text-sm text-white hover:bg-brand-700"
            >
              {t('header.login')}
            </NavLink>
          )}
        </div>
      </nav>
    </header>
  );
}