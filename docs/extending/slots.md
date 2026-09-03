# UI slots — a native button, zero coupling

The portal keeps a small registry table, `ui_extensions`. Each row is one
contribution to a named **slot**: "in this slot, render a button with this
label that goes to this URL." Product apps read their slots at render time and
draw whatever they find as **native** buttons — same design system, same feel.
The core ships the socket; the addon ships the plug.

An empty slot renders nothing. That is the uninstall story: delete the rows and
the UI is gone, and the core never knew the addon's name.

## The row

| Field | Meaning |
|---|---|
| `key` | Unique id, by convention `<addon>.<purpose>` (e.g. `acquire.search-request`) |
| `addon` | Owning addon id — enables bulk removal of everything an addon contributed |
| `slot` | Where it appears (see the catalog below) |
| `kind` | `link` (navigate) or `action` (the client POSTs to `url`) |
| `label`, `icon` | Button text and a [lucide](https://lucide.dev) icon name (safe fallback if unknown) |
| `url` | Destination. Placeholders are substituted client-side: `{q}` = the current search query |
| `status_url` | Optional: a feed the client may poll to decorate the button with live state |
| `ord`, `enabled` | Ordering within the slot; kill-switch |

## The API

- **Write** — `POST /api/portal/extensions` (upsert by `key`), `PATCH`/`DELETE
  /api/portal/extensions/{key}`. Callers need the admin role **or** the addon
  role — see [identity](./identity.md) for the honest state of the addon role.
- **Read** — `GET /api/portal/slots/{slot}` returns the enabled rows for one
  slot, ordered. Any signed-in user; product apps forward the user's bearer.

Product apps don't call portal-api directly from the browser in every case:
`chino-api` proxies the read (`GET /api/v1/extensions?slot=…`) best-effort, so
an unreachable portal yields an empty slot rather than an error.

## Slot catalog

The catalog is deliberately explicit: a slot exists when a product app renders
it, not when a doc mentions it.

| Slot | Rendered by | When it shows |
|---|---|---|
| `search.empty` | chino-web (search page) | A search returned no titles and no people |

That is the entire catalog today — one slot. 🧭 Roadmap: item detail actions
and portal-shell slots; they will be added to this table when a client actually
renders them, and not before.

## Worked example

Installing [acquire](https://github.com/laedeli/acquire) registers one row:

```json
{
  "key": "acquire.search-request",
  "addon": "acquire",
  "slot": "search.empty",
  "kind": "link",
  "label": "Request this",
  "icon": "download",
  "url": "/portal/app/acquire?q={q}#/discover",
  "ord": 10,
  "enabled": true
}
```

"No results for _X_" grows a **Request this** button that carries the query
into the addon's console. Delete the row and it is gone.
