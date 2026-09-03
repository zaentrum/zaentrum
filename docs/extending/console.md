# Hosted consoles — a full addon UI inside the portal

An addon with real administrative surface (queues, settings, dashboards) gets a
**console**: a React app the portal shell hosts in-page. The addon needs **no
origin, no Ingress/Route, and no session of its own** — the portal proxies to
it in-cluster and mounts its UI in the shell's React tree.

Remotes are attached **at runtime**, not declared at build time, because which
apps exist is a registry decision. Adding a console never requires rebuilding
or releasing the portal.

## How hosting works

1. An app is registered in the portal (key, title, and a **proxy url** — the
   addon's in-cluster address, e.g. `http://acquire`). Registration is
   admin-only today (settings console → apps); addon self-registration of apps
   is 🧭 roadmap.
2. The portal serves `/portal/app/{key}` and reverse-proxies
   `/api/apps/{key}/*` to the proxy url. The proxy is deliberately the front
   door: a browser cannot attach a bearer token to a module `import()`, and the
   proxy also guards against SSRF by only accepting in-cluster targets.
3. The shell fetches the addon's federated bundle **through that proxy**, mounts
   its exported component, and passes it the host props below.

## The contract your console must satisfy

Your UI is a [module federation](https://github.com/originjs/vite-plugin-federation)
remote, built with `@originjs/vite-plugin-federation` (`format: 'esm'`). The
host expects, relative to your service's HTTP root:

| The host fetches | Meaning |
|---|---|
| `embed/assets/remoteEntry.js` | The federation entry of your embed build |
| module `./Console` | Exposed by your federation config |
| **named** export `Console` | A default export is rejected — the host looks for `Console` |
| `embed/assets/console.css` | Your styles; loaded alongside the module |

Shared dependencies: `react` and `react-dom` are shared **singletons at
`^18.3.0`**. Your embed build must accept that version range or your console
will not mount.

The host renders:

```tsx
<Console apiBase={string} token={string | undefined} onUnauthorized={() => void} />
```

- `apiBase` — the base URL for your own API **through the portal proxy**
  (`/api/apps/{key}`). Call your backend via this base and every request
  carries the user's bearer.
- `token` — the current access token, when you need it directly (e.g. an SSE
  fetch-stream).
- `onUnauthorized` — call it when your API answers 401; the shell owns the
  re-auth flow.

Failures are contained: the host wraps your console in an error boundary, so a
broken remote degrades to an error card rather than taking the shell down.

> 🧭 This contract is currently defined by the host implementation
> (`zaentrum-portal/src/apps/AppHost.tsx`) and this page. A versioned,
> importable types package is roadmap; until then, treat this page as the
> contract and expect it to change only with a note in the release notes.

## Worked example

[acquire](https://github.com/laedeli/acquire) ships its console this way: one
Vite embed build in the addon image, zero Ingress objects in its manifests, and
the portal tile opens `/portal/app/acquire`.
