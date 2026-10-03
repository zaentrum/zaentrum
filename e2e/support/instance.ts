// What the instance says about itself: GET /api/config, the public
// self-describe document every client bootstraps from (OIDC issuer and the
// per-client ids). Reading it here keeps the suite free of instance-specific
// identity settings.
import { env } from './env';

export interface InstanceConfig {
  apiBase: string;
  oidcEnabled: boolean;
  oidcIssuer: string;
  oidcAudience?: string;
  oidcClientId: { web: string; portal?: string; [k: string]: string | undefined };
}

let cached: Promise<InstanceConfig> | undefined;

export function instanceConfig(): Promise<InstanceConfig> {
  cached ??= (async () => {
    const url = `${env.baseURL}/api/config`;
    const res = await fetch(url, { headers: { Accept: 'application/json' } });
    if (!res.ok) throw new Error(`${url} answered ${res.status}`);
    const cfg = (await res.json()) as InstanceConfig;
    if (!cfg.oidcIssuer || !cfg.oidcClientId?.web) {
      throw new Error(`${url} names no OIDC issuer or web client id`);
    }
    return cfg;
  })();
  return cached;
}

/** The client the web client (chino) signs in with. */
export const webClient = (cfg: InstanceConfig) => cfg.oidcClientId.web;

/** The client the portal and the catalog console share. */
export const portalClient = (cfg: InstanceConfig) => cfg.oidcClientId.portal || cfg.oidcClientId.web;
