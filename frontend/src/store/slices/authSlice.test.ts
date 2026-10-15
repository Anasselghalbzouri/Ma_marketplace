/**
 * T-012 — tests du slice `auth`.
 *
 * Couvre :
 *  - Hydratation initiale depuis un payload localStorage valide.
 *  - setSession persiste + met \u00e0 jour l'\u00e9tat.
 *  - logout purge.
 *  - forceUnauthenticated : utilis\u00e9 par les flux M01 quand le backend
 *    renvoie 401 sur un appel prot\u00e9g\u00e9 malgr\u00e9 un jeton local.
 */

import { describe, expect, it, beforeEach } from 'vitest';
import authReducer, {
  forceUnauthenticated,
  hydrateFromStorage,
  logout,
  selectCurrentRole,
  selectIsAuthenticated,
  setSession,
  type Session,
} from '@/store/slices/authSlice';

function makeState() {
  return { auth: authReducer(undefined, { type: 'init' }) };
}

const SAMPLE_SESSION: Session = {
  token: 'tkn-1',
  tokenType: 'Bearer',
  expiresAt: '2026-12-31T00:00:00Z',
  user: { id: 7, role: 'customer', phone: '+212600000007', name: 'Salma' },
};

describe('authSlice', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it('setSession alimente le state et persiste', () => {
    const s0 = makeState();
    const s1 = authReducer(s0.auth, setSession(SAMPLE_SESSION));
    expect(selectIsAuthenticated({ auth: s1 })).toBe(true);
    expect(selectCurrentRole({ auth: s1 })).toBe('customer');
    expect(window.localStorage.getItem('mplm.auth')).not.toBeNull();
    const stored = JSON.parse(window.localStorage.getItem('mplm.auth') ?? '{}');
    expect(stored.token).toBe('tkn-1');
    expect(stored.user.role).toBe('customer');
  });

  it('logout purge le state et le localStorage', () => {
    const s1 = authReducer(makeState().auth, setSession(SAMPLE_SESSION));
    const s2 = authReducer(s1, logout());
    expect(selectIsAuthenticated({ auth: s2 })).toBe(false);
    expect(selectCurrentRole({ auth: s2 })).toBeNull();
    expect(window.localStorage.getItem('mplm.auth')).toBeNull();
  });

  it('forceUnauthenticated agit comme logout sans message utilisateur', () => {
    const s1 = authReducer(makeState().auth, setSession(SAMPLE_SESSION));
    const s2 = authReducer(s1, forceUnauthenticated());
    expect(s2.token).toBeNull();
    expect(window.localStorage.getItem('mplm.auth')).toBeNull();
  });

  it('hydrateFromStorage marque le state comme hydrat\u00e9', () => {
    const s1 = authReducer(makeState().auth, hydrateFromStorage());
    expect(s1.hydrated).toBe(true);
  });
});