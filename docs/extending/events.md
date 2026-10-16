# The event bus — reacting to the platform, publishing your own

Stage handoffs in the media pipeline are Kafka events; database rows record
*state* while events drive the *handoff*. The bus is a public integration
surface: an addon consumes platform events to react, and publishes its own
domain events under the same conventions.

## Platform topics

All topic names carry the instance's **tenant prefix** — the CR's
`eventStreaming.topicPrefix`, default `stube.` (a missing trailing dot is
added). The catalog contract:

| Topic (after the prefix) | Emitted when |
|---|---|
| `catalog.item.discovered` | An item entered the catalog (scanner or [ingest](./ingest.md)) |
| `catalog.item.enriched` | Metadata resolution finished |
| `catalog.item.analyzed` | Technical analysis finished |
| `catalog.item.transcoded` | Transcode finished |
| `catalog.item.packaged` | The item is packaged and **playable** — the event an addon usually waits for |
| `catalog.item.removed` | The item was deleted |

Events are keyed by the item's id and carry a minimal JSON envelope (the
item, the step the event unblocks, provenance) — consumers that need more read
it from the APIs:

```json
{"eventId": "9f2b…", "itemId": "8c1cee73-…", "type": "episode", "step": "tmdb",
 "occurredAt": "2026-10-15T08:00:00Z", "source": "ingest",
 "externalIds": {"tmdb-episode": "937631"}, "seriesExternalIds": {"tmdb": "97546", "tvdb": "362392"},
 "seasonNumber": 4, "episodeNumber": 7}
```

`discovered`, `packaged` and `removed` also name the item's **identities**
beside its catalog id
([ADR-0012](../adr/0012-catalog-identity-for-addons.md)), so a consumer
reconciles what it knows of a title without a lookup:

- `externalIds` — the item's own ids, by source as the catalog keeps them:
  `tmdb`, `tvdb`, `imdb`, and an episode's TMDB id under `tmdb-episode`;
- of an episode, `seriesExternalIds` — its series' ids — and `seasonNumber`
  and `episodeNumber`.

Each is optional, left out when the catalog knows none. `removed` names the
item as it was, read before its rows go. `packaged` is sent for the episode
that holds a file; an episode another's file covers plays with it — the
[holdings](./holdings.md) say which.

🔶 No schema of the item events is published yet.
[ADR-0005](../adr/0005-kafka-event-bus-and-schema-contracts.md) decides that
events are Avro contracts in [zaentrum/schemas](https://github.com/zaentrum/schemas);
the item events are JSON today, and the Avro records under `stube/library/`
there describe an earlier design that no service emits. Until a schema is
published, the envelope above is the contract, and it changes only by
additions.

### A title's extras

A title's [extras](./extras.md) — its trailers, teasers, featurettes — are
packaged on a chain of their own, under the same tenant prefix
(`stube.catalog.extra.queued` by default):

| Topic (after the prefix) | From → to | Emitted when |
|---|---|---|
| `catalog.extra.queued` | katalog-manager → transcoder | An extra is due to be packaged: taken in, packaged again, or retried |
| `catalog.extra.transcoded` | transcoder → packager | The transcoder is done with it |
| `catalog.extra.packaged` | katalog-manager → anyone (fan-out) | Its package is recorded, and it plays |

All three are keyed by the extra's id, `extraId`. The two triggers carry the
extra, and **no `itemId`, on purpose**:

```json
{"eventId": "9f2b…", "extraId": "1b5c2a8e-…", "parentId": "ea886f9b-…", "type": "extra",
 "kind": "trailer", "step": "transcode", "status": "queued", "occurredAt": "2026-10-06T08:00:00Z",
 "source": "api"}
```

`parentId` names the movie or series the extra belongs to. An item worker
requires an `itemId`, so one pointed at an extras topic by mistake skips the
event: an extra never enters a title's pipeline. `catalog.extra.transcoded` is
the same envelope with `"step": "package"` and `"source": "transcoder"`; a
trigger sent again after a failed run has `"status": "retry"` and
`"source": "retry"`.

`catalog.extra.packaged` ends the chain, in the shape of an item event of the
title, so a live-refresh bridge that reads item events refreshes the title:
`itemId` is the title the extra belongs to, `type` its type, `step` is
`extra`, and `extraId` and `kind` name the extra.

```json
{"eventId": "…", "itemId": "ea886f9b-…", "type": "movie", "step": "extra", "status": "done",
 "occurredAt": "…", "source": "katalog-manager", "extraId": "1b5c2a8e-…", "kind": "trailer"}
```

**An extra never emits `catalog.item.packaged`.** That event says the title
itself became playable, so an addon waiting for a title is never fooled by
its trailer.

Each consumer reads in a group of its own:

| Consumer group | Service | Reads |
|---|---|---|
| `transcoder-extras` | transcoder | `catalog.extra.queued` |
| `packager-extras` | packager | `catalog.extra.transcoded` |
| `chino-events-extras-<pod>` | chino-api, one group per pod, for live refresh | `catalog.extra.packaged` |

## Addon topics

An addon publishes its own events under the same tenant prefix with its own
domain segment (the acquire addon, for example, emits
`download.client.{started,progress,completed,failed}` from its download plane
and consumes `catalog.item.packaged` to flip a request to *fulfilled*). Two
rules keep this composable:

- **Prefix everything** with the instance's tenant prefix, so two instances can
  share one broker without crosstalk.
- **Own your domain segment.** Addon topics live under a segment the addon
  owns; the `catalog.*` namespace belongs to the platform.

🔶 An addon's topics must exist before its work on them runs: on a broker
that does not create topics on first use, provision them under the prefix.
[ADR-0012](../adr/0012-catalog-identity-for-addons.md) decides that the
manifest declares them and the operator creates and removes them with the
addon; that is not built yet.

## Connecting

The CR declares everything a client needs:

- `eventStreaming.mode` — `bundled` (a single-node broker the operator runs)
  or `external` (bring your own cluster).
- `eventStreaming.bootstrap` — the bootstrap address in external mode.
- `eventStreaming.certSecret` — the Secret holding mTLS client material
  (`user.crt`, `user.key`, `ca.crt`) when the external cluster requires it.
  This is a declared CRD field, not an internal convention — an addon may
  mount the same secret and connect the same way the platform services do.
- `eventStreaming.topicPrefix` — the tenant prefix above.
- `eventStreaming.groupPrefix` — the prefix of the instance's consumer groups:
  the pipeline workers' (`analyzer-workers`, `transcoder-workers`,
  `packager-workers`, `transcoder-extras`, `packager-extras`) and the catalog
  enricher's (`katalog-enricher`). Empty (the default), they keep those names.

**Two instances on one broker need a `groupPrefix` each** (one may keep the
empty one). A group two instances share is led by one of them; where the
broker's ACLs let each instance see only its own topics, the leader cannot
assign the other instance's partitions, and that instance's workers read
nothing, without an error. A group a prefix newly names starts at the
earliest message its topics retain, so setting it re-reads what they hold:
set it on an instance whose topics hold only work it still has to do.

In bundled mode the broker is plaintext in-cluster and topics for the platform
contract are pre-created; in external mode topic provisioning follows whatever
governs your cluster.

A broker that does not create topics on first use, as a shared one often
does not, needs the three [extras topics](#a-titles-extras) provisioned under
the instance's prefix, and must let the groups `<groupPrefix>transcoder-extras`,
`<groupPrefix>packager-extras` and `chino-events-extras-<pod>` read them. Until
then extras wait, `pending`, and are sent again a backoff later; chino-api asks
every minute whether its topic exists; the item pipeline is unaffected.
