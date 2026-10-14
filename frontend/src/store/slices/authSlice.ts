/**
 * T-012 — slice authentification.
 *
 * Source : specs/001-architecture-socle/contracts/authentification.md
 *          + specs/003-contrat-api/contracts/openapi.yaml (M01).
 *
 * Responsabilités du socle (T-012) :
 * - Stocker le jeton et les informations publiques du compte (rôle, téléphone).
 * - Persister via localStorage (clé `mplm.auth`) pour survivre aux rechargements.
 *   Le mot de passe n'est jamais stocké, ni chiffré, ni manipulé côté client.
 * - Exposer des actions synchrones (`hydrateFromStorage`, `logout`, `setSession`)
 *   que les modules M01 (inscription, connexion) brancheront ensuite via
 *   `matchFulfilled` sur leurs endpoints RTK Query (livré par Anvil).
 *
 * Le jeton et la session seront branchés sur `/api/v1/auth/login` etc. par les
 * tâches filles T-014/T-016. Ce slice ne contient pas la logique réseau.
 */

import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

export type Role = 'customer' | 'seller' | 'admin';

export interface SessionUser {
  id: number;
  role: Role;
  phone: string;
  name?: string;
}

export interface Session {
  token: string;
  tokenType: 'Bearer';
  expiresAt: string; // ISO 8601 UTC (ADR-016).
  user: SessionUser;
}

export interface AuthState {
  token: string | null;
  tokenType: 'Bearer' | null;
  expiresAt: string | null;
  user: SessionUser | null;
  hydrated: boolean;
}

const STORAGE_KEY = 'mplm.auth';

function loadInitial(): Pick<AuthState, 'token' | 'tokenType' | 'expiresAt' | 'user'> {
  if (typeof window === 'undefined') {
    return { token: null, tokenType: null, expiresAt: null, user: null };
  }
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (raw === null) return { token: null, tokenType: null, expiresAt: null, user: null };
    const parsed = JSON.parse(raw) as Partial<Session> | null;
    if (
      parsed === null
      || typeof parsed !== 'object'
      || typeof parsed.token !== 'string'
      || typeof parsed.tokenType !== 'string'
      || typeof parsed.expiresAt !== 'string'
      || parsed.user === null
      || typeof parsed.user !== 'object'
    ) {
      return { token: null, tokenType: null, expiresAt: null, user: null };
    }
    return {
      token: parsed.token,
      tokenType: parsed.tokenType,
      expiresAt: parsed.expiresAt,
      user: parsed.user as SessionUser,
    };
  } catch {
    return { token: null, tokenType: null, expiresAt: null, user: null };
  }
}

const initial: AuthState = {
  ...loadInitial(),
  hydrated: false,
};

const authSlice = createSlice({
  name: 'auth',
  initialState: initial,
  reducers: {
    /**
     * Posée par le `Provider` au montage, après le premier render. Empêche
     * l'affichage d'un état « déconnecté » clignotant à l'hydratation.
     */
    hydrateFromStorage(state) {
      state.hydrated = true;
    },
    setSession(state, action: PayloadAction<Session>) {
      state.token = action.payload.token;
      state.tokenType = action.payload.tokenType;
      state.expiresAt = action.payload.expiresAt;
      state.user = action.payload.user;
      state.hydrated = true;
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(action.payload));
      }
    },
    logout(state) {
      state.token = null;
      state.tokenType = null;
      state.expiresAt = null;
      state.user = null;
      state.hydrated = true;
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem(STORAGE_KEY);
      }
    },
    /**
     * Utilisée par les endpoints M01 (login/register) en cas d'échec d'auth :
     * force la déconnexion locale pour purger un jeton invalide côté client.
     */
    forceUnauthenticated(state) {
      state.token = null;
      state.tokenType = null;
      state.expiresAt = null;
      state.user = null;
      state.hydrated = true;
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem(STORAGE_KEY);
      }
    },
  },
});

export const { hydrateFromStorage, setSession, logout, forceUnauthenticated } = authSlice.actions;
export default authSlice.reducer;

/** Sélecteurs. */
export const selectIsAuthenticated = (s: { auth: AuthState }): boolean => s.auth.token !== null;
export const selectCurrentRole = (s: { auth: AuthState }): Role | null => s.auth.user?.role ?? null;
export const selectAuthHydrated = (s: { auth: AuthState }): boolean => s.auth.hydrated;
export const selectAuthToken = (s: { auth: AuthState }): string | null => s.auth.token;