/**
 * T-012 — contrat des erreurs API.
 *
 * Source : specs/001-architecture-socle/contracts/format-erreur.md
 *          + specs/003-contrat-api/contracts/error-codes.md (catalogue fermé, 24 codes).
 *
 * Règles :
 * - Toute réponse avec code HTTP >= 400 suit l'enveloppe `{ error: { code, message, details? } }`.
 * - `code` est en anglais, stable, snakecase (ADR-016) ; le frontend s'appuie dessus
 *   pour toute logique conditionnelle (ex. afficher la modal « panier vide » sur
 *   `cart_empty`, rediriger vers /login sur `unauthenticated`).
 * - `message` est en français et peut être reformulé côté serveur sans casser le frontend.
 * - `details` peut contenir un objet structuré (ex. `validation_failed.details.fields`)
 *   ou être absent. Aucune donnée sensible n'y figure jamais (mot de passe, etc.).
 */

export const ERROR_CODES = [
  'malformed_request',
  'invalid_credentials',
  'unauthenticated',
  'account_suspended',
  'forbidden',
  'not_found',
  'duplicate_name',
  'insufficient_stock',
  'invalid_transition',
  'payout_already_recorded',
  'phone_already_registered',
  'product_unavailable',
  'resource_in_use',
  'cart_empty',
  'city_not_served',
  'commune_not_allowed',
  'file_rejected',
  'nothing_to_pay_out',
  'return_not_eligible',
  'review_not_allowed',
  'validation_failed',
  'rate_limited',
  'server_error',
  'feature_blocked',
] as const;

export type ErrorCode = (typeof ERROR_CODES)[number];

export interface ApiErrorBody {
  error: {
    code: ErrorCode | string;
    message: string;
    details?: Record<string, unknown>;
  };
}

/**
 * Erreur applicative normalisée : tous les chemins (catch fetch, throwResponse
 * RTK Query, parse JSON) convergent vers cette classe avant d'atteindre Redux.
 */
export class ApiError extends Error {
  readonly code: ErrorCode | string;
  readonly httpStatus: number;
  readonly details: Readonly<Record<string, unknown>>;

  constructor(args: {
    code: ErrorCode | string;
    message: string;
    httpStatus: number;
    details?: Record<string, unknown>;
  }) {
    super(args.message);
    this.name = 'ApiError';
    this.code = args.code;
    this.httpStatus = args.httpStatus;
    this.details = Object.freeze(args.details ?? {});
  }

  /** Vrai pour les codes qui exigent une redirection vers /login. */
  get requiresAuth(): boolean {
    return this.code === 'unauthenticated' || this.httpStatus === 401;
  }

  /** Vrai pour les codes qui exigent un toast d'erreur générique. */
  get isRetryable(): boolean {
    return this.code === 'server_error' || this.code === 'rate_limited'
      || this.httpStatus >= 500;
  }
}

/**
 * Convertit une `Response` fetch en `ApiError`. Si le corps n'est pas du JSON
 * conforme à l'enveloppe, on retombe sur un `server_error` avec le statut HTTP
 * d'origine — jamais d'information technique renvoyée à l'utilisateur.
 */
export async function toApiError(response: Response): Promise<ApiError> {
  let body: unknown = null;
  try {
    body = await response.json();
  } catch {
    // Réponse non-JSON : on retombe sur le code générique, sans détail technique.
  }
  if (
    body !== null
    && typeof body === 'object'
    && 'error' in body
    && body.error !== null
    && typeof body.error === 'object'
  ) {
    const err = (body as { error: { code?: unknown; message?: unknown; details?: unknown } }).error;
    // FR-009 : tout code absent du catalogue fermé est traité comme `server_error`.
    // Le backend est censé n'émettre que des codes du catalogue ; cette règle est
    // une défense en profondeur côté frontend (cf. error-codes.md §1).
    let code: ErrorCode | string = 'server_error';
    if (typeof err.code === 'string' && (ERROR_CODES as readonly string[]).includes(err.code)) {
      code = err.code;
    }
    const message = typeof err.message === 'string'
      ? err.message
      : defaultMessageFor(code as string, response.status);
    const details = err.details !== null && typeof err.details === 'object'
      ? (err.details as Record<string, unknown>)
      : undefined;
    return new ApiError({
      code,
      message,
      httpStatus: response.status,
      ...(details !== undefined ? { details } : {}),
    });
  }
  return new ApiError({
    code: 'server_error',
    message: defaultMessageFor('server_error', response.status),
    httpStatus: response.status,
  });
}

function defaultMessageFor(code: string, status: number): string {
  switch (code) {
    case 'unauthenticated':
      return 'Votre session a expiré. Veuillez vous reconnecter.';
    case 'forbidden':
      return 'Vous n\u2019avez pas les droits requis pour cette action.';
    case 'not_found':
      return 'Ressource introuvable.';
    case 'validation_failed':
      return 'Certaines donn\u00e9es sont invalides.';
    case 'rate_limited':
      return 'Trop de requ\u00eates. Veuillez patienter quelques instants.';
    case 'server_error':
    default:
      return `Erreur serveur (${status}). Veuillez r\u00e9essayer.`;
  }
}

/**
 * Garde de type : un objet ressemble-t-il à une enveloppe d'erreur API ?
 * Utilisé pour les tests, et par les intercepteurs RTK Query.
 */
export function isApiErrorBody(value: unknown): value is ApiErrorBody {
  if (value === null || typeof value !== 'object') return false;
  const err = (value as { error?: unknown }).error;
  if (err === null || typeof err !== 'object') return false;
  const code = (err as { code?: unknown }).code;
  const message = (err as { message?: unknown }).message;
  return typeof code === 'string' && typeof message === 'string';
}