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

Events are keyed by `item_id` and carry a minimal envelope (identity, the step
the event unblocks, provenance) — consumers that need more read it from the
APIs. Schemas are published contracts in
[zaentrum/schemas](https://github.com/zaentrum/schemas) (Avro).

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

In bundled mode the broker is plaintext in-cluster and topics for the platform
contract are pre-created; in external mode topic provisioning follows whatever
governs your cluster.

A broker that does not create topics on first use, as a shared one often
does not, needs the three [extras topics](#a-titles-extras) provisioned under
the instance's prefix, and must let the groups `transcoder-extras`,
`packager-extras` and `chino-events-extras-<pod>` read them. Until then extras
wait, `pending`, and are sent again a backoff later; chino-api asks every
minute whether its topic exists; the item pipeline is unaffected.
