#!/usr/bin/env node
/**
 * T-012 — mini serveur mock pour la vérification locale de l'intégration
 * frontend.
 *
 * Ce serveur **n'est pas** un backend de production. Il existe pour deux
 * raisons strictement délimitées :
 *
 *   1. Prouver que le socle frontend (RTK Query, baseQuery, ApiError,
 *      LoadingState, ErrorState, EmptyState, pagination, format-erreur,
 *      auth, i18n) est correctement câblé au contrat T-003, sans dépendre
 *      d'un backend Laravel démarrable (étape 4.x — Anvil).
 *   2. Servir de cible reproductible aux tests d'intégration Vitest et à
 *      la preuve manuelle demandée par le critère exit du socle
 *      (« application lancée en local »).
 *
 * Le mock **n'implémente aucune logique métier**. Il se contente de
 * répondre aux endpoints publics du contrat T-003, en respectant
 * scrupuleusement :
 *   - le préfixe /api/v1 (ADR-007)
 *   - l'enveloppe d'erreur { error: { code, message, details? } }
 *   - le catalogue fermé des codes (error-codes.md)
 *   - la pagination { data, meta: { page, per_page, total, total_pages } }
 *   - les enums (snakecase anglais) et les montants en chaîne décimale
 *
 * Chaque endpoint documente en commentaire la ligne du contrat qu'il
 * implémente et la règle qu'il vérifie. Tout endpoint réellement
 * consommé par un écran métier sera remplacé par Anvil dans T-006+.
 *
 * Démarrage : `node tools/mock-server.mjs` (port 8080 par défaut).
 */

import http from 'node:http';
import { URL } from 'node:url';

const PORT = Number.parseInt(process.env.MOCK_PORT ?? '8080', 10);
const HOST = process.env.MOCK_HOST ?? '127.0.0.1';

/** Catalogue fermé — cf. specs/003-contrat-api/contracts/error-codes.md */
const ERROR_CODES = new Set([
  'malformed_request', 'invalid_credentials', 'unauthenticated', 'account_suspended',
  'forbidden', 'not_found', 'duplicate_name', 'insufficient_stock', 'invalid_transition',
  'payout_already_recorded', 'phone_already_registered', 'product_unavailable',
  'resource_in_use', 'cart_empty', 'city_not_served', 'commune_not_allowed',
  'file_rejected', 'nothing_to_pay_out', 'return_not_eligible', 'review_not_allowed',
  'validation_failed', 'rate_limited', 'server_error', 'feature_blocked',
]);

/** Réponse d'erreur normalisée (ADR-016, ADR-017, format-erreur.md). */
function sendError(res, status, code, message, details) {
  if (!ERROR_CODES.has(code)) code = 'server_error';
  const body = { error: { code, message, ...(details ? { details } : {}) } };
  res.writeHead(status, { 'content-type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(body));
}

/** Réponse succès (200/201/204). */
function sendJson(res, status, payload) {
  res.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'cache-control': 'no-store',
  });
  res.end(payload === null ? '' : JSON.stringify(payload));
}

/** Lit le corps d'une requête (limite 1 Mo pour éviter DoS). */
async function readBody(req) {
  const chunks = [];
  let total = 0;
  for await (const chunk of req) {
    total += chunk.length;
    if (total > 1_048_576) throw new Error('payload_too_large');
    chunks.push(chunk);
  }
  if (chunks.length === 0) return null;
  return Buffer.concat(chunks).toString('utf8');
}

/**
 * Routes du mock : un objet = (méthode + matcher pathname + handler).
 * Le handler résout soit :
 *  - `{ status, payload }` : réponse JSON succès.
 *  - `{ status, code, message, details? }` : erreur normalisée.
 *  - `null/undefined` et écrit lui-même la réponse (cas spéciaux).
 */
const ROUTES = [
  {
    method: 'GET',
    match: (u) => u.pathname === '/api/v1/served-cities',
    handler: () => ({ status: 200, payload: { data: [{ id: 1, name: 'Tanger' }] } }),
    doc: 'UC-007 + MX-02 : villes desservies (V1 = Tanger, CA-F007-2).',
  },
  {
    method: 'GET',
    match: (u) => u.pathname === '/api/v1/categories',
    handler: () => ({
      status: 200,
      payload: {
        data: [
          { id: 1, slug: 'huiles', name: 'Huiles' },
          { id: 2, slug: 'miels', name: 'Miels' },
          { id: 3, slug: 'cosmetiques', name: 'Cosm\u00e9tiques' },
        ],
      },
    }),
    doc: 'UC-001 + MX-02 : r\u00e9f\u00e9rentiel public des cat\u00e9gories.',
  },
  {
    method: 'GET',
    match: (u) => u.pathname === '/api/v1/products',
    handler: (_req, _res, u) => {
      const page = Math.max(1, Number.parseInt(u.searchParams.get('page') ?? '1', 10));
      const perPage = Math.min(50, Math.max(1, Number.parseInt(u.searchParams.get('per_page') ?? '20', 10)));
      if (u.searchParams.get('demo') === '1') {
        return {
          status: 200,
          payload: {
            data: [
              { id: 1, name: 'Huile d\u2019argan', price: '85.00' },
              { id: 2, name: 'Miel de thym', price: '120.00' },
              { id: 3, name: 'Savon noir', price: '35.00' },
            ],
            meta: { page, per_page: perPage, total: 3, total_pages: 1 },
          },
        };
      }
      return {
        status: 200,
        payload: { data: [], meta: { page, per_page: perPage, total: 0, total_pages: 0 } },
      };
    },
    doc: 'UC-001 + MP-01 : catalogue public pagin\u00e9 (vide par d\u00e9faut, ?demo=1 pour 3 stubs).',
  },
  {
    method: 'POST',
    match: (u) => u.pathname === '/api/v1/auth/login',
    handler: async (req, res) => {
      let body;
      try { body = JSON.parse((await readBody(req)) ?? '{}'); }
      catch { return sendError(res, 400, 'malformed_request', 'JSON invalide.'); }
      if (typeof body.phone !== 'string' || typeof body.password !== 'string') {
        return sendError(res, 422, 'validation_failed',
          'Champs requis : phone, password.',
          { fields: ['phone', 'password'] });
      }
      if (body.phone !== '+212600000001' || body.password !== 'demo') {
        return sendError(res, 401, 'invalid_credentials',
          'Identifiants incorrects.');
      }
      sendJson(res, 200, {
        data: {
          token: 'demo-token-' + Date.now(),
          token_type: 'Bearer',
          expires_at: new Date(Date.now() + 3600_000).toISOString(),
          user: { id: 1, role: 'customer', phone: body.phone, name: 'Demo' },
        },
      });
      return null;
    },
    doc: 'M01 login : +212600000001 / demo -> 200, autres -> 401 invalid_credentials.',
  },
  {
    method: 'GET',
    match: (u) => u.pathname === '/api/v1/me',
    handler: (req) => {
      const auth = req.headers['authorization'];
      if (typeof auth !== 'string' || !auth.startsWith('Bearer ')) {
        return { status: 401, code: 'unauthenticated', message: 'Jeton manquant.' };
      }
      const token = auth.slice('Bearer '.length);
      return {
        status: 200,
        payload: {
          data: { id: 1, role: 'customer', phone: '+212600000001', name: 'Demo', token },
        },
      };
    },
    doc: 'MP-04 : /me prot\u00e9g\u00e9 (401 sans jeton, 200 avec).',
  },
];

const server = http.createServer(async (req, res) => {
  const start = Date.now();
  let pathname = '';
  try {
    const u = new URL(req.url ?? '/', `http://${req.headers.host ?? HOST}`);
    pathname = u.pathname;
    for (const route of ROUTES) {
      if (route.method !== req.method) continue;
      if (!route.match(u)) continue;
      const out = await route.handler(req, res, u);
      if (out === null || out === undefined) {
        log(req, res, start, pathname);
        return;
      }
      if ('payload' in out) {
        sendJson(res, out.status, out.payload);
      } else {
        sendError(res, out.status, out.code, out.message, out.details);
      }
      log(req, res, start, pathname);
      return;
    }
    sendError(res, 404, 'not_found', 'Ressource introuvable.');
    log(req, res, start, pathname);
  } catch (err) {
    console.error('[mock] erreur interne :', err);
    sendError(res, 500, 'server_error', 'Erreur interne.');
    log(req, res, start, pathname);
  }
});

function log(req, res, start, pathname) {
  const ms = Date.now() - start;
  console.log(`[mock] ${req.method} ${pathname} -> ${res.statusCode} (${ms} ms)`);
}

server.listen(PORT, HOST, () => {
  console.log(`[mock] T-012 mock serveur en \u00e9coute sur http://${HOST}:${PORT}`);
  console.log('[mock] endpoints : GET /api/v1/served-cities, /categories, /products,');
  console.log('                 POST /api/v1/auth/login, GET /api/v1/me');
});

process.on('SIGINT', () => {
  console.log('\n[mock] arr\u00eat...');
  server.close(() => process.exit(0));
});