# Catalog ingest — a file becomes a library item

The catalog has one writer, katalog-manager, and it exposes one neutral seam
for addons: **`POST /api/ingest`**. Hand it an absolute path to a file that is
already on disk and it creates the item, attaches the file as the primary
asset, and emits `catalog.item.discovered` — from there the standard pipeline
runs (enrich → analyze → transcode → package) and the item becomes playable.

This is what keeps the core honest. The platform never asks *how* a file
arrived; an addon that produces files simply reports them. The seam is the
same one the built-in library scanner uses internally.

An addon hands a title over **by its identity** — the ids it has in the
reference databases, TMDB, TVDB or IMDb — not by a catalog id it would have to
look up and keep ([ADR-0012](../adr/0012-catalog-identity-for-addons.md)). The
catalog finds the series an episode belongs to, or makes it, and answers with
its own ids. To learn what the library holds already, ask the read side by the
same identities: [holdings](./holdings.md).

## The call

In-cluster only (it is not published on the public route map — addons run
inside the platform namespace and call the service directly):

```
POST http://katalog-manager-api/api/ingest
Authorization: Bearer <service token>          # see identity.md
Content-Type: application/json
```

A movie, with its identity:

```json
{
  "path": "/var/lib/katalog/inbox/Some Film (2024)/some-film.mkv",
  "type": "movie",
  "title": "Some Film",
  "year": 2024,
  "identity": {"tmdb": "4711", "imdb": "tt0004711"},
  "sizeBytes": 4816928512
}
```

Response: `{ "itemId": "<uuid>", "created": true }`.

An episode, by its series' identity:

```json
{
  "path": "/var/lib/katalog/inbox/Some Show/Some Show - S02E05.mkv",
  "type": "episode",
  "title": "Some Show",
  "year": 2020,
  "series": {"tmdb": "97546"},
  "seasonNumber": 2,
  "episodeNumber": 5
}
```

Response: `{ "itemId": "<uuid>", "created": true, "seriesId": "<uuid>" }`.

### Rules the endpoint enforces

- `path`, `type`, `title` are required. A disc image is refused (400): it is
  no file the library holds.
- **`path` must live under the media root or the packages root** — or, with
  the library's [v2 layout](../library/record.md), under its arrivals
  (`.work/incoming/`). An ingest can never point the catalog at an arbitrary
  host path.
- **Episodes must arrive linked**: `type: "episode"` requires its series —
  by its catalog id (`parentId`, a series or a season of one) or by its
  identity (`series`), one or the other — and `seasonNumber` and
  `episodeNumber`, or the call is rejected (400): an unlinked episode would
  otherwise be published as a permanent orphan.
- **An identity** is an object of ids by reference database: one or more of
  `tmdb`, `tvdb` and `imdb`, each a string of its form (a TMDB or TVDB id is
  digits, an IMDb id `tt` and digits). Another key, or another form, is 400.
  `series` names an episode's series; `identity` the title's own — a movie's,
  or an episode's (its TMDB id is kept as the catalog keeps an episode's, under
  `tmdb-episode`).
- **Idempotent on `path`.** Re-ingesting the same path returns the existing
  item with `created: false` and does not re-fire the pipeline. Your addon can
  safely retry.
- Optional fields: `year`, `description`, `sortTitle`, `sizeBytes`, and
  `metadataLocked` (true = the enricher must not overwrite your metadata).

On `created: true`, the scan step is seeded as done and
`catalog.item.discovered` is emitted — subscribe to `catalog.item.packaged`
(see [events](./events.md)) to learn when the item is playable.

## By identity

**The series** of an episode is found by its ids: by the first of `tmdb`,
`tvdb` and `imdb` the body names that finds a series. Of a show the library
holds twice, the series made first is the one, as [holdings](./holdings.md)
answer it. When no series holds any of the ids, the catalog makes one, as the
scanner makes a series it finds: from the body's title and year, with the ids
given, its own `discovered` event sent first, so that enrichment matches it by
its id. Many episodes of one new show arriving together make one series.

**One file of several episodes in a row** — `S01E01E02` — names its last
episode in `episodeEnd` (one file covers ten episodes at most). The first episode
holds the file; the others are linked to it as the scanner links the episodes
a file's name numbers: the series' episode of that number, or one made for it
when the series has none. One with a file of its own keeps it (its own file
wins), and so does one another file covers already.

```json
{"path": "…/Some Show - S04E07E08.mkv", "type": "episode", "title": "Some Show",
 "series": {"tmdb": "97546"}, "seasonNumber": 4, "episodeNumber": 7, "episodeEnd": 8}
```

The answer then lists the episodes the file covers besides its first, in
episode order:

```json
{"itemId": "8c1cee73-…", "created": true, "seriesId": "f3ab0c45-…", "covered": ["43afc194-…"]}
```

An episode handed over by `parentId` takes `episodeEnd` too, and covers the
episodes of its parent's series.

**A movie** with an `identity` arrives matched: it gets those ids rather than
being found by its title.

### Refusals

A refusal names the item in the way, `{"error": "...", "itemId": "<uuid>"}`,
and writes nothing:

| Status | When |
|---|---|
| 409 | The path is held, and the identity given contradicts what the catalog holds of it: a title of another type, an episode of another series or other numbers, another movie, an episode's own id of another value. A title is never relinked to an identity. |
| 409 | The library holds the title already as another item: an episode of that series, season and number with a file of its own (or one another file covers), or a movie of that identity with a file. Replacing a held title's file is another decision, never an ingest's. |
| 409 | With the v2 layout, the file is a copy of an original the library holds, or one it retired. |
| 400 | The body is malformed, as above, or names an episode's series both ways. |

An episode of those numbers with no file holds none: the file becomes that
episode's, as a scanned one does.

## The shared filesystem

The path you send must be visible to the pipeline workers, which means your
addon writes into the platform's media storage (typically a subdirectory of the
shared media volume such as an `inbox/`, or with the v2 layout of the
arrivals). Mount the same volume the platform uses; the
[installing](./installing.md) page shows where that is declared.
