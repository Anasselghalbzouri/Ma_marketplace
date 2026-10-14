/**
 * T-012 — store racine.
 *
 * Combine les slices livrés par le socle (auth, i18n) et l'API RTK Query
 * (`mplmApi`, vide à ce stade). Chaque module métier (M01..M11) ajoute son
 * slice et ses endpoints en `injectEndpoints` sur le même store.
 *
 * Sérialisation Redux Toolkit : on exclut par défaut la sérialisation des
 * payloads RTK Query (déjà non-sérialisables), les autres champs sont des
 * primitives.
 */

import { configureStore } from '@reduxjs/toolkit';
import { setupListeners } from '@reduxjs/toolkit/query';
import { api } from '@/api/api';
import authReducer from './slices/authSlice';
import i18nReducer from './slices/i18nSlice';

export const store = configureStore({
  reducer: {
    [api.reducerPath]: api.reducer,
    auth: authReducer,
    i18n: i18nReducer,
  },
  middleware: (getDefault) => getDefault().concat(api.middleware),
});

setupListeners(store.dispatch);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;