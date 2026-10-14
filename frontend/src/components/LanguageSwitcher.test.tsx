/**
 * T-012 — tests du LanguageSwitcher.
 *
 * V\u00e9rifie que :
 *  - Les deux langues du socle (fr, ar) sont propos\u00e9es.
 *  - Changer la langue d\u00e9clenche setLanguage et persiste dans localStorage.
 *  - L'attribut `dir` du document bascule en `rtl` pour l'arabe.
 */

import { describe, expect, it, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import i18nReducer from '@/store/slices/i18nSlice';
import { I18nextProvider } from 'react-i18next';
import i18n from '@/i18n';
import { LanguageSwitcher } from '@/components/LanguageSwitcher';

function makeStore() {
  return configureStore({ reducer: { i18n: i18nReducer } });
}

function renderWithProviders() {
  const store = makeStore();
  return {
    store,
    ...render(
      <Provider store={store}>
        <I18nextProvider i18n={i18n}>
          <LanguageSwitcher />
        </I18nextProvider>
      </Provider>,
    ),
  };
}

describe('LanguageSwitcher', () => {
  beforeEach(() => {
    window.localStorage.clear();
    document.documentElement.lang = 'fr';
    document.documentElement.dir = 'ltr';
  });

  it('propose fr et ar avec les libell\u00e9s localis\u00e9s', () => {
    renderWithProviders();
    const select = screen.getByRole('combobox', { name: /Langue/i });
    const options = select.querySelectorAll('option');
    expect(options.length).toBe(2);
    expect(options[0]?.value).toBe('fr');
    expect(options[1]?.value).toBe('ar');
  });

  it('changer pour ar bascule le document en RTL', async () => {
    const user = userEvent.setup();
    renderWithProviders();
    await user.selectOptions(screen.getByRole('combobox', { name: /Langue/i }), 'ar');
    expect(document.documentElement.dir).toBe('rtl');
    expect(document.documentElement.lang).toBe('ar');
    expect(window.localStorage.getItem('mplm.lang')).toBe('ar');
  });
});