/**
 * T-012 — entrée de l'application.
 *
 * Responsabilités :
 *  - Hydrater l'état Redux depuis le localStorage (auth, langue).
 *  - Synchroniser `<html lang>` et `<html dir>` avec la langue du slice.
 *  - Monter le router dans l'arbre Redux.
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { store } from '@/store';
import { hydrateFromStorage } from '@/store/slices/authSlice';
import {
  hydrateI18nFromStorage,
  setLanguage,
  selectLanguage,
} from '@/store/slices/i18nSlice';
import { AppRouter } from '@/router';
import './i18n';
import './styles/index.css';

// Hydratation synchrone avant le 1er render : évite le clignotement « déconnecté »
// et la bascule de langue AR -> FR en plein chargement.
store.dispatch(hydrateFromStorage());
store.dispatch(hydrateI18nStorage());
store.dispatch(setLanguage(store.getState().i18n.language));

function hydrateI18nStorage(): ReturnType<typeof hydrateI18nFromStorage> {
  return hydrateI18nFromStorage();
}

// À ce stade, le slice i18n est déjà hydraté par `setLanguage` (qui pose aussi
// `dir`). On garde un sélecteur accessible pour les tests qui souhaiteraient
// forker l'app à un état précis.
void selectLanguage;

const rootElement = document.getElementById('root');
if (rootElement === null) {
  throw new Error('T-012: élément #root introuvable dans index.html');
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <Provider store={store}>
      <AppRouter />
    </Provider>
  </React.StrictMode>,
);