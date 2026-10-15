/**
 * T-012 — tests unitaires de l'enveloppe d'erreur API.
 *
 * Couvre :
 *  - Décodage d'une réponse 4xx JSON valide.
 *  - Décodage d'une réponse 5xx sans JSON (fallback `server_error`).
 *  - Garde de type `isApiErrorBody`.
 *  - Accesseurs dérivés (`requiresAuth`, `isRetryable`).
 */

import { describe, expect, it } from 'vitest';
import {
  ApiError,
  ERROR_CODES,
  isApiErrorBody,
  toApiError,
} from '@/api/errorEnvelope';

describe('errorEnvelope', () => {
  it('d\u00e9code une r\u00e9ponse JSON conforme', async () => {
    const res = new Response(
      JSON.stringify({ error: { code: 'validation_failed', message: 'invalide', details: { fields: ['phone'] } } }),
      { status: 422 },
    );
    const err = await toApiError(res);
    expect(err).toBeInstanceOf(ApiError);
    expect(err.code).toBe('validation_failed');
    expect(err.httpStatus).toBe(422);
    expect(err.message).toBe('invalide');
    expect(err.details).toEqual({ fields: ['phone'] });
  });

  it('retombe sur server_error quand le code est inconnu', async () => {
    const res = new Response(
      JSON.stringify({ error: { code: 'unknown_thing', message: '?' } }),
      { status: 500 },
    );
    const err = await toApiError(res);
    expect(err.code).toBe('server_error');
    expect(err.httpStatus).toBe(500);
  });

  it('retombe sur server_error quand le corps est invalide', async () => {
    const res = new Response('not-json', { status: 502 });
    const err = await toApiError(res);
    expect(err.code).toBe('server_error');
    expect(err.httpStatus).toBe(502);
  });

  it('isApiErrorBody accepte une enveloppe valide', () => {
    expect(isApiErrorBody({ error: { code: 'forbidden', message: 'x' } })).toBe(true);
  });

  it('isApiErrorBody rejette les formes invalides', () => {
    expect(isApiErrorBody({})).toBe(false);
    expect(isApiErrorBody({ error: { code: 1, message: 'x' } })).toBe(false);
    expect(isApiErrorBody({ error: { code: 'forbidden' } })).toBe(false);
    expect(isApiErrorBody(null)).toBe(false);
    expect(isApiErrorBody('string')).toBe(false);
  });

  it('requiresAuth refl\u00e8te le contrat', () => {
    expect(new ApiError({ code: 'unauthenticated', message: '', httpStatus: 401 }).requiresAuth).toBe(true);
    expect(new ApiError({ code: 'forbidden', message: '', httpStatus: 403 }).requiresAuth).toBe(false);
  });

  it('isRetryable distingue les erreurs transitoires', () => {
    expect(new ApiError({ code: 'server_error', message: '', httpStatus: 500 }).isRetryable).toBe(true);
    expect(new ApiError({ code: 'rate_limited', message: '', httpStatus: 429 }).isRetryable).toBe(true);
    expect(new ApiError({ code: 'validation_failed', message: '', httpStatus: 422 }).isRetryable).toBe(false);
  });

  it('catalogue ferm\u00e9 : ERROR_CODES contient 24 codes stables', () => {
    expect(ERROR_CODES.length).toBe(24);
    expect(ERROR_CODES).toContain('unauthenticated');
    expect(ERROR_CODES).toContain('feature_blocked');
    // codes inconnus explicitement interdits
    expect(ERROR_CODES).not.toContain('acces_refuse'); // redaction ADR-016
    expect(ERROR_CODES).not.toContain('ressource_introuvable'); // redaction ADR-016
  });
});