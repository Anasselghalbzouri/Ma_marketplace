/**
 * T-012 — tests du Header (mobile-first).
 *
 * Couvre :
 *  - Pr\u00e9sence du bouton hamburger sous 768 px (toujours vrai dans jsdom).
 *  - Bouton hamburger bascule aria-expanded.
 *  - Lien "Se connecter" visible pour un visiteur.
 *  - Apr\u00e8s login (setSession), le bouton "Se d\u00e9connecter" remplace le lien.
 */

import { describe, expect, it, beforeEach } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { combineReducers, configureStore } from '@reduxjs/toolkit';
import { MemoryRouter } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import i18n from '@/i18n';
import authReducer from '@/store/slices/authSlice';
import i18nReducer, { type I18nState } from '@/store/slices/i18nSlice';
import type { AuthState } from '@/store/slices/authSlice';
import { Header } from '@/components/Header';

type RootSlice = { auth?: AuthState; i18n?: I18nState };
const rootReducer = combineReducers({ auth: authReducer, i18n: i18nReducer });

function renderHeader(preloaded?: RootSlice) {
  const store = configureStore({
    reducer: rootReducer,
    preloadedState: preloaded as never,
  });
  return {
    store,
    ...render(
      <Provider store={store}>
        <MemoryRouter>
          <I18nextProvider i18n={i18n}>
            <Header />
          </I18nextProvider>
        </MemoryRouter>
      </Provider>,
    ),
  };
}

describe('Header', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it('affiche le titre et le bouton hamburger', () => {
    renderHeader();
    expect(screen.getByText('March\u00e9 local Maroc')).toBeInTheDocument();
    const button = screen.getByRole('button', { name: /Ouvrir le menu/i });
    expect(button).toHaveAttribute('aria-expanded', 'false');
  });

  it('le hamburger bascule l\u2019attribut aria-expanded', async () => {
    const user = userEvent.setup();
    renderHeader();
    const button = screen.getByRole('button', { name: /Ouvrir le menu/i });
    await user.click(button);
    expect(button).toHaveAttribute('aria-expanded', 'true');
    expect(screen.getByRole('button', { name: /Fermer le menu/i })).toBeInTheDocument();
  });

  it('propose "Se connecter" quand aucun utilisateur', () => {
    renderHeader();
    const nav = screen.getByRole('navigation');
    expect(within(nav).getByRole('link', { name: /Se connecter/i })).toBeInTheDocument();
  });

  it('affiche "Se d\u00e9connecter" quand l\u2019utilisateur est connect\u00e9', () => {
    renderHeader({
      auth: {
        token: 'tkn', tokenType: 'Bearer', expiresAt: '2030-01-01T00:00:00Z',
        user: { id: 1, role: 'customer', phone: '+212600000001' }, hydrated: true,
      },
      i18n: { language: 'fr', hydrated: true },
    });
    const nav = screen.getByRole('navigation');
    expect(within(nav).getByRole('button', { name: /Se d\u00e9connecter/i })).toBeInTheDocument();
  });
});