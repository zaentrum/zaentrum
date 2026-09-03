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
