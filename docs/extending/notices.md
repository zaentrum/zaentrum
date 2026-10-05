# Notices — tell one person something

An addon can tell one person something — *your title is ready* — and every
client that person uses shows it: the bell in the portal's header, and the
product apps. The core ships the socket; the addon writes the words. portal-api
keeps a notice for its person, shows it to them and to nobody else, and
forgets it; it never interprets what a notice says.

A notice is for one person. Something for everyone is a [slot row](./slots.md)
or the addon's own [console](./console.md).

## The notice

| Field | Meaning |
|---|---|
| `id` | The notice's id, a UUID |
| `addon` | The key of the addon it is from |
| `addonTitle`, `addonIcon` | The addon's app, as the registry has it — what a client shows the notice is from |
| `title` | Plain text, at most 80 characters, one line |
| `body` | Plain text, at most 280 characters; line breaks allowed |
| `link` | `""` for none, else where the notice leads: a path on the instance, or an absolute http(s) URL on its own origin |
| `itemId` | `""` for none, else the id of a catalog item a client can open |
| `createdAt`, `readAt` | RFC 3339, UTC; `readAt` is `null` while unread |

Whom a notice is for is never in an answer: a person reads their own.

## Posting a notice

### With the addon's service account

An addon tells a person something — now or hours later — with its
[service account](./identity.md): a client-credentials token of the
confidential client named after the addon, with the `zaentrum-addon` role.
The addon is the one the token binds, never one the body names, and it must be
installed on the instance.

```sh
# a client-credentials token from the instance's issuer
TOKEN=$(curl -s -X POST "$ISSUER/protocol/openid-connect/token" \
  -d grant_type=client_credentials -d client_id=my-addon -d client_secret="$SECRET" | jq -r .access_token)

curl -X POST http://portal-api/api/portal/notices \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"sub":"<the person'"'"'s token subject>","title":"Your title is ready",
       "body":"It is in your library now.","link":"/portal/app/my-addon#/done","itemId":"<item id>"}'
# 201 {"id":"…","addon":"my-addon","addonTitle":"My Addon",…,"readAt":null}
```

`sub` is the subject of the person's token. The addon learns it from the
bearer it validates when the person calls its API through the portal's proxy
— the [sample addon](https://github.com/zaentrum/sample-addon)'s `requireUser`
reads it — and keeps it with whatever it is doing for them.

| Answer | When |
|---|---|
| `201` with the notice | posted |
| `400` | the body breaks a [rule](#the-rules), or names a field it does not take — `addon` among them |
| `403` | the token is no addon's service account (an admin's is not either), or the addon is not installed here |
| `409` | the addon was removed while the notice was posted |
| `429` with `Retry-After` | the addon posted more than its limit |

### To yourself, without a credential

An addon that holds no credential — the sample addon holds none — can still
tell the person at its console something: `POST /api/portal/me/notices` with
`{addon, title, body, link?, itemId?}` and the person's own bearer, which the
shell hands every console (`token`). The notice goes to that bearer's person
and nobody else: the body names no person, and one that does is refused.

```ts
// inside a console: apiBase is <portal API>/apps/<key>/
await fetch('/api/portal/me/notices', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
  body: JSON.stringify({ addon: 'my-addon', title: 'Saved', body: 'Your settings are saved.', link: '/portal/app/my-addon' }),
})
```

Whoever holds a person's bearer can already act as that person, and this
reaches nobody else, so it grants nothing new. It also proves nothing about
which addon sent it — any holder of the bearer may name any installed addon.
Use it to tell the person in front of the console something now; a notice for
someone else, or for later, takes the service account. A service account is
refused here.

## The rules

They hold whoever posts.

| Rule | |
|---|---|
| Text | `title` at most 80 characters, one line; `body` at most 280, line breaks allowed; both plain text — no control characters, no bidirectional formatting characters. Clients show them as text, never as markup |
| Link | Held to the [slot link rule](./slots.md#where-a-row-may-lead) — one function decides both: a path on the instance, or an absolute http(s) URL on its own origin; never `javascript:`, `data:`, another host, `//host`, credentials or dot segments. A path is made absolute on the instance's public origin when portal-api knows it |
| Item | Letters, digits and `. _ : -`, at most 128 |
| Limits | Per addon: 100 at once, then one a second. Per person posting to themselves: 10, then one every six seconds. Per replica of portal-api |
| Kept | A person keeps their newest 100: a new one past that removes the oldest. Every notice goes after `PORTAL_NOTICE_RETENTION` (default `2160h`, 90 days), swept at boot and every hour |
| Gone with | Removing the addon removes its notices, with its slot rows; deleting a person — on the People page or from the apps — removes theirs |
| Logged | Every write — who, which notice — and never what a notice says |

## Reading notices — what a client does

A person reads their own on portal-api, with their bearer:

| Route | |
|---|---|
| `GET /api/portal/me/notices` | `{notices, unread}`: their own, newest first |
| `POST /api/portal/me/notices/{id}/read` | one of theirs, read — once: reading again keeps when it was first read; `{unread}` |
| `POST /api/portal/me/notices/read-all` | all of theirs, read: `{read, unread}` |
| `DELETE /api/portal/me/notices/{id}` | one of theirs, deleted: `204` |

Someone else's notice is `404`, as one there is not. The product apps use
chino-api's copy of the same routes, which forwards their bearer and keeps
nothing: `GET /api/v1/notices` (adding `available`),
`POST /api/v1/notices/{noticeId}/read`, `POST /api/v1/notices/read-all`,
`DELETE /api/v1/notices/{noticeId}`. It is best effort: with no portal-api, or
one that does not answer, the list is empty with `"available": false` and the
answer still `200`, so a home screen never fails for notices; a change it
cannot make is `502`, and the app keeps the notice as it was.

Every client does the same:

- shows the unread count where the person looks first, and the list newest
  first, each with whom it is from (`addonTitle`, else `addon`) and when;
- shows `title` and `body` as plain text, never as markup, `body`'s line
  breaks kept;
- follows `link` only to its own server — a path, or an http(s) URL on the
  server's own origin — checking it again as portal-api did; a client that
  cannot show a web page shows the text alone;
- opens `itemId` with its own item routes, which hold a capped viewer to
  their cap;
- marks a notice read when it is opened, and offers read all and delete;
- asks again now and then while it is shown — the portal's bell asks every
  minute and when the page is shown again — and shows nothing, not an error,
  when the answer is `available: false`.

## Counting them

`GET /api/portal/notices?addon=<key>` answers an admin each addon's notices
counted — `notices`, `unread`, `people`, `latest`, with the `kept` cap and
`retentionHours` — and never what one says, nor whom it is for.

## Honest status

| Capability | Status |
|---|---|
| Notices in portal-api: posting, reading, limits, retention, deletion with the person and the addon | ✅ shipped |
| The bell in the portal's header | ✅ shipped |
| chino-api's `/api/v1/notices` for the apps | ✅ shipped |
| Notices in chino on the web, the TV apps and the phone apps | 🔶 next — each reads `/api/v1/notices` as above |
| Push to a device that is not open | 🧭 not designed |
| Addon service accounts made by the platform | 🧭 roadmap — made by hand today, see [identity](./identity.md) |

The [sample addon](https://github.com/zaentrum/sample-addon)'s console has
**Send Me a Notice**: a notice to yourself, posted with your own bearer.
