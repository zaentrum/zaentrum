# Catalog ingest — a file becomes a library item

The catalog has one writer, katalog-manager, and it exposes one neutral seam
for addons: **`POST /api/ingest`**. Hand it an absolute path to a file that is
already on disk and it creates the item, attaches the file as the primary
asset, and emits `catalog.item.discovered` — from there the standard pipeline
runs (enrich → analyze → transcode → package) and the item becomes playable.

This is what keeps the core honest. The platform never asks *how* a file
arrived; an addon that produces files simply reports them. The seam is the
same one the built-in library scanner uses internally.

## The call

In-cluster only (it is not published on the public route map — addons run
inside the platform namespace and call the service directly):

```
POST http://katalog-manager-api/api/ingest
Authorization: Bearer <service token>          # see identity.md
Content-Type: application/json
```

```json
{
  "path": "/var/lib/katalog/inbox/Some Film (2024)/some-film.mkv",
  "type": "movie",
  "title": "Some Film",
  "year": 2024,
  "description": "…",
  "sizeBytes": 4816928512
}
```

Response: `{ "itemId": "<uuid>", "created": true }`.

### Rules the endpoint enforces

- `path`, `type`, `title` are required.
- **`path` must live under the media root or the packages root.** An ingest can
  never point the catalog at an arbitrary host path.
- **Episodes must arrive linked**: `type: "episode"` requires `parentId`,
  `seasonNumber` and `episodeNumber`, or the call is rejected — an unlinked
  episode would otherwise be published as a permanent orphan.
- **Idempotent on `path`.** Re-ingesting the same path returns the existing
  item with `created: false` and does not re-fire the pipeline. Your addon can
  safely retry.
- Optional fields: `sortTitle`, `metadataLocked` (true = the enricher must not
  overwrite your metadata), `parentId`/`seasonNumber`/`episodeNumber` for
  episodes, `sizeBytes`.

On `created: true`, the scan step is seeded as done and
`catalog.item.discovered` is emitted — subscribe to `catalog.item.packaged`
(see [events](./events.md)) to learn when the item is playable.

## The shared filesystem

The path you send must be visible to the pipeline workers, which means your
addon writes into the platform's media storage (typically a subdirectory of the
shared media volume such as an `inbox/`). Mount the same volume the platform
uses; the [installing](./installing.md) page shows where that is declared.
