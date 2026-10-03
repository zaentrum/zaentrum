// The run's configuration, read from the environment.
//
// Credentials only ever come from the environment and are never logged,
// printed or written anywhere but the browser's own login form. Missing
// values are reported by NAME, never by value.
//
// Variables may also come from a KEY=VALUE file: set E2E_ENV_FILE to its
// path, or keep one at e2e/.env (gitignored). A variable already set in the
// environment wins over the file, as with `node --env-file`.
import fs from 'node:fs';
import path from 'node:path';

export const E2E_ROOT = path.resolve(__dirname, '..');

/** Parse a KEY=VALUE file: `#` comments, blank lines, an optional
 *  `export ` prefix and single or double quotes around a value. */
export function parseEnvFile(text: string): Record<string, string> {
  const out: Record<string, string> = {};
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith('#')) continue;
    const m = line.match(/^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$/);
    if (!m) continue;
    let value = m[2];
    const quoted = value.match(/^(['"])(.*)\1$/);
    if (quoted) value = quoted[2];
    else value = value.replace(/\s+#.*$/, '');
    out[m[1]] = value;
  }
  return out;
}

function loadEnvFile(file: string, required: boolean) {
  if (!fs.existsSync(file)) {
    if (required) throw new Error(`E2E_ENV_FILE points at ${file}, which does not exist`);
    return;
  }
  for (const [k, v] of Object.entries(parseEnvFile(fs.readFileSync(file, 'utf8')))) {
    if (process.env[k] === undefined) process.env[k] = v;
  }
}

if (process.env.E2E_ENV_FILE) loadEnvFile(path.resolve(process.env.E2E_ENV_FILE), true);
else loadEnvFile(path.join(E2E_ROOT, '.env'), false);

function mount(name: string, fallback: string): string {
  const v = (process.env[name] || fallback).trim();
  // Always "/x/" — a leading and a trailing slash — so paths join cleanly.
  return ('/' + v.replace(/^\/+|\/+$/g, '') + '/').replace(/^\/\/$/, '/');
}

const baseURL = (process.env.E2E_BASE_URL || 'https://zaentrum.demo.nalet.cloud').replace(/\/+$/, '');

export const env = {
  /** Origin of the instance under test, without a trailing slash. */
  baseURL,
  /** Where the web client is mounted (the demo serves it under /chino/). */
  chinoPath: mount('E2E_CHINO_PATH', '/chino/'),
  /** Where the catalog console is mounted (browse mode, not /katalog-manage/). */
  consolePath: mount('E2E_CONSOLE_PATH', '/katalog/'),
  /** Where the portal launchpad is mounted. */
  portalPath: mount('E2E_PORTAL_PATH', '/portal/'),
  /** Run the @next contract tests (they are excluded otherwise). */
  includeNext: process.env.E2E_NEXT === '1',
  /** `run` turns the runtime test.fixme() of the UI-change specs into a
   *  real run, so the assertions execute and show what is still missing. */
  runFixme: process.env.E2E_FIXME === 'run',
};

export type Account = 'viewer' | 'admin';

const CREDENTIAL_VARS: Record<Account, { user: string; password: string }> = {
  viewer: { user: 'E2E_USER', password: 'E2E_PASSWORD' },
  admin: { user: 'E2E_ADMIN_USER', password: 'E2E_ADMIN_PASSWORD' },
};

/** The credentials of one account. Throws naming the missing variables. */
export function credentials(account: Account): { username: string; password: string } {
  const vars = CREDENTIAL_VARS[account];
  const username = process.env[vars.user];
  const password = process.env[vars.password];
  const missing = [!username && vars.user, !password && vars.password].filter(Boolean);
  if (missing.length) {
    throw new Error(
      `the ${account} account needs ${missing.join(' and ')} in the environment ` +
        '(see e2e/README.md: set -a; . ./e2e.env; set +a)',
    );
  }
  return { username: username!, password: password! };
}

/** Where the setup project saves an account's signed-in browser state. */
export function authFile(account: Account): string {
  return path.join(E2E_ROOT, '.auth', `${account}.json`);
}

/** Absolute URL of a path inside a mounted app: app('/chino/', '/i/x'). */
export function appURL(mountPath: string, sub = '/'): string {
  const rest = sub.replace(/^\/+/, '');
  return `${baseURL}${mountPath}${rest}`;
}
