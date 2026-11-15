# ADR-0024: One product for listening: musig plays music, audiobooks and podcasts; books to read and a household's own photos and videos are not goals

**Status:** Accepted · 2026-11-11 for parts 1, 3 and 4, 2026-11-15 for parts 2 and 5, by the owner. Design ahead of the code: no part of musig is built.

## Context

[ADR-0001](./0001-neutral-core-and-addon-seams.md) names three products of the core: chino for video, and musig for music and tv for live TV, both planned. [ADR-0004](./0004-per-product-streaming-origins.md) gives each product its own streaming origin and describes musig's as audio for music. Neither says where audiobooks and podcasts belong, and the list of what people expect of a media server holds them, along with books to read and a household's own photos and home videos.

Left open, each of these invites a product or an app of its own. A household would then have one app for music, one for audiobooks, one for podcasts and one for books, each with its own library, its own way of keeping a place, and its own tile.

As built: the repositories `musig-api` and `musig-stream` hold a scaffold that nothing runs, and the portal registers a tile for musig that is switched off.

## Decision

1. **musig is the one product for listening.** Music, audiobooks and podcasts are played by musig, in one app, from one library of things to listen to. There is no separate product or app for audiobooks or for podcasts.
2. **What sets the three apart is kept inside it.** An audiobook and a podcast episode keep a place to come back to, as a film does in chino; a piece of music does not. The product's design says how each is browsed and played; this record only says they share the product.
3. **Books to read are not a goal.** zaentrum plays what is watched or listened to. A book has its place in it as an audiobook. The platform gets no reader and no library of books to read.
4. **A household's own photos and home videos are not a goal.** zaentrum is for what a household owns, not for what it made itself. chino is built for films and shows, and the platform gets no product for photos.
5. **The design of musig comes after watching is complete.** Until then the specification holds its goal, its two expectations and its capabilities as stubs, marked as left for later in [scope](../../spec/capabilities/scope.md).

## Consequences

- One listening product to design, build and translate, and one tile for it.
- The catalog and the pipeline gain kinds of title when musig is designed: an album and its tracks, a book and its chapters, a podcast and its episodes. [ADR-0004](./0004-per-product-streaming-origins.md)'s description of `musig-stream` as audio for music then covers spoken audio too.
- Where a podcast's episodes come from is not decided here. The core plays what is in the library ([ADR-0001](./0001-neutral-core-and-addon-seams.md)); fetching a feed's new episodes is the kind of work an addon does, and the design of musig says so or decides otherwise.

What it rules out:

- A product, an app or a tile of its own for audiobooks, for podcasts, or for books to read.
- Photos and home videos as a kind of title in chino, or as a product.
