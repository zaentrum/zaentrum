// The suite runs against a live, shared instance and must never change it.
// Every browser context the tests open goes through this guard: reads pass,
// and of the writes only the few that change nothing pass — signing in,
// exchanging a code for a token, minting an artwork token, GraphQL reads.
// Anything else (marking watched, adding to a list, a bug report the app
// files on its own, a console mutation, signing out of the shared session)
// is aborted before it leaves the browser and reported on the test.
import type { BrowserContext, Request } from '@playwright/test';
import { env } from './env';

const SAFE_METHODS = new Set(['GET', 'HEAD', 'OPTIONS']);

interface Allowed {
  method: string;
  path: RegExp;
  /** Further check on the request, e.g. that a GraphQL body only reads. */
  only?: (request: Request) => boolean;
}

const ALLOWED_WRITES: Allowed[] = [
  // Keycloak's login form, during the setup project's sign-in.
  { method: 'POST', path: /\/realms\/[^/]+\/login-actions\/authenticate$/ },
  // OIDC: authorization code exchange and token refresh.
  { method: 'POST', path: /\/realms\/[^/]+\/protocol\/openid-connect\/token$/ },
  // chino-api mints a signed, short-lived artwork/stream token; it stores nothing.
  { method: 'POST', path: /^\/api\/v1\/me\/stream-token$/ },
  // katalog-manager GraphQL: queries only, never a mutation.
  { method: 'POST', path: /^\/api\/manage\/(query|graphql)$/, only: isGraphQLRead },
];

// Requests that are blocked whatever their method: a sign-out ends the
// Keycloak session every test shares.
const BLOCKED: RegExp[] = [/\/protocol\/openid-connect\/logout\b/];

/** True when a GraphQL POST body holds only query operations. */
export function isGraphQLRead(request: Request): boolean {
  let payload: unknown;
  try {
    payload = JSON.parse(request.postData() ?? '');
  } catch {
    return false;
  }
  const ops = Array.isArray(payload) ? payload : [payload];
  return ops.every((op) => {
    const doc = (op as { query?: unknown } | null)?.query;
    if (typeof doc !== 'string') return false;
    const code = doc
      .replace(/"""[\s\S]*?"""/g, '""')
      .replace(/"(?:[^"\\]|\\.)*"/g, '""')
      .replace(/#[^\n]*/g, '');
    return !/\b(mutation|subscription)\b/.test(code);
  });
}

/** Route every request of a context through the guard. `onBlocked` gets a
 *  short description ("POST /api/v1/feedback") of each aborted request. */
export async function guardReadOnly(
  context: BrowserContext,
  onBlocked: (what: string) => void,
): Promise<void> {
  const origin = new URL(env.baseURL).origin;
  await context.route(
    () => true,
    async (route, request) => {
      const url = new URL(request.url());
      const where = url.origin === origin ? url.pathname : `${url.origin}${url.pathname}`;
      const method = request.method();
      if (BLOCKED.some((re) => re.test(url.pathname))) {
        onBlocked(`${method} ${where}`);
        return route.abort('blockedbyclient');
      }
      if (SAFE_METHODS.has(method)) return route.fallback();
      const allowed =
        url.origin === origin &&
        ALLOWED_WRITES.some((a) => a.method === method && a.path.test(url.pathname) && (!a.only || a.only(request)));
      if (allowed) return route.fallback();
      onBlocked(`${method} ${where}`);
      return route.abort('blockedbyclient');
    },
  );
}
