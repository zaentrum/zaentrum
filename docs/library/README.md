# The library format

The library format is how zaentrum keeps a media library **on storage**: every
movie, series and episode is a folder that describes itself completely — what
it is, every text and image about it, what is playable, and what the original
file contained. Storage is the source of truth. Databases are caches that can be
thrown away and rebuilt by reading the folders.

> **Status — format ahead of the code.** Schema v1 is published, and a sample
> library built by the reference migrator validates against it. No platform
> service reads or writes the format yet: the catalog keeps its truth in a
> database, the packager writes version 2 package folders, and the streaming
> origin finds episode packages at `shows/<aa>/<episodeId>/` rather than inside
> a series folder. This section documents the format so tools and services can
> adopt it; [Migrating a library](./migrating.md#before-a-platform-uses-the-format)
> lists what has to change first.

## Why storage, not a database

- **A library outlives its software.** Folders with JSON and images can be read
  by any tool, backed up with any tool, and moved to object storage (S3 and
  compatible) as keys, without an export step.
- **One place to lose, one place to back up.** When the database is a cache, a
  lost or corrupted database is an inconvenience, not data loss.
- **Data, not behaviour.** The library describes what is on storage — what a
  track contains, what an original had, what a package lost. What to play or show
  by default is behaviour: it belongs to players and to per-user settings in a
  database, derived from that description.
- **Nothing is guessed.** A value the source does not hold stays empty. Where
  automation cannot decide — an unmatched item, an edition, a black-and-white
  call from a few sampled frames, an episode whose filename contradicts its
  match — the document records a `review` saying what a person should check.

Per-user state — watch progress, history, lists — is not library data and stays
in a database.

## Layout

```mermaid
flowchart TD
  L["library root"] --> MV["movies/&lt;aa&gt;/&lt;movieId&gt;/"]
  L --> SH["shows/&lt;aa&gt;/&lt;seriesId&gt;/"]
  MV --> M1["manifest.json"]
  MV --> M2["metadata/<br/>metadata.json · poster.jpg · backdrop.jpg · logo.png"]
  MV --> M3["source/&lt;sourceId&gt;/ffprobe.json"]
  MV --> M4["hls/ · subs/ · trickplay/ · .complete<br/>the playable package"]
  MV --> M5["versions/&lt;versionId&gt;/<br/>only for a second version"]
  SH --> S1["manifest.json<br/>seasons and their episodes"]
  SH --> S2["metadata/<br/>metadata.json · poster.jpg · season-01-poster.jpg"]
  SH --> EP["episodes/&lt;episodeId&gt;/<br/>same shape as a movie folder"]
```

`<aa>` is the first two hex characters of the id, which keeps any one folder's
child count small. Folders are named only by stable ids, never by titles or
numbers, so renaming a title, renumbering an episode or switching to a DVD
ordering never moves a file. An episode folder is named by the episode's own id —
the same id its package folder has today.

| File | Holds | Meant to be written by |
|---|---|---|
| `manifest.json` | The entry point: type, primary title, reference ids, the playback fields a streaming origin reads, and every version with what its original contained and what its package lost. See [manifest.json](./manifest.md). | The media pipeline (scan, analyze, package) and people deciding editions |
| `metadata/metadata.json` | Every text — localised titles, overviews, credits, dates, series and season details, video references — and the list of images in the same folder. See [metadata.json](./metadata.md). | Enrichment from a reference database, and people editing texts |
| `metadata/*.jpg`, `*.png` | The images, named by what they are: `poster.jpg`, `still.jpg`, `season-02-poster.jpg`. | Same as metadata.json |
| `source/<sourceId>/` | The verbatim probe of the original file (`ffprobe.json`) and small files that sat next to it, kept after the original is gone. | The media pipeline |
| `hls/`, `subs/`, `trickplay/`, `.complete` | The package: HLS/CMAF segments, subtitles (WebVTT, or PGS/VobSub/DVB files for image subtitles), scrub thumbnails. See [ADR-0002](../adr/0002-prepackaged-playback.md). | The packager |

Two documents per item, split by writer: the pipeline would never touch texts,
and a re-sync from a reference database would never touch what is playable.

## Reading an item

```mermaid
sequenceDiagram
  participant R as Reader
  participant S as Storage
  R->>S: movies/{aa}/{id}/manifest.json
  S-->>R: type, title, externalIds, playback fields, versions
  R->>S: metadata/metadata.json
  S-->>R: texts, credits, image list (file + sha256)
  R->>S: metadata/poster.jpg (cache key = sha256)
  Note over R: a series manifest lists episodes/{id}/ per season
```

1. Read `manifest.json`. `type` says what follows: a movie or episode has
   `versions` and, when packaged, playback fields; a series has `series.seasons`
   listing its episode folders.
2. Read `metadata/metadata.json` for everything shown to a viewer.
3. Fetch images by the file names in `images[]`. Cache them by their `sha256`,
   so a replaced image never serves stale. A missing kind falls back to the
   parent: an episode without a `still` shows its season poster, then the series
   poster.

A cache builder would do exactly this for every folder under `movies/` and `shows/`.

## Schemas and validation

The format is defined by JSON Schema (draft 2020-12):

| Schema | URL |
|---|---|
| `manifest.json` | <https://zaentrum.github.io/schemas/library/v1/manifest.schema.json> |
| `metadata/metadata.json` | <https://zaentrum.github.io/schemas/library/v1/metadata.schema.json> |
| Shared definitions | <https://zaentrum.github.io/schemas/library/v1/defs.schema.json> |

Every document names its schema in a `schema` field
(`zaentrum.library.manifest/1`, `zaentrum.library.metadata/1`). **v1 is a draft
until a platform service adopts it:** until then it may still change, and every
change is listed in the
[schemas changelog](https://github.com/zaentrum/schemas#library-v1-changelog).
Rebuild a library with the current migrator after a change.

The validator in the [schemas repository](https://github.com/zaentrum/schemas)
checks the schemas and the rules that span files or need arithmetic: every
`itemId` equals its folder name and shard; every listed image exists with the
recorded hash, size, content type and dimensions; a series lists exactly the
episode folders it contains and agrees with their numbering; version paths,
truth and deletion state are consistent, every track says what it is for, and the
version 2 playback hints do not contradict it; probe files and sidecars match their
hashes.

```sh
pip install "jsonschema[format-nongpl]>=4.23" referencing
python tools/validate-library.py /path/to/library                 # documents and cross-file rules
python tools/validate-library.py --check-media /path/to/library   # also every playback path and .complete marker
python tools/test-validate-library.py                             # the broken trees it must reject
```

Worked examples — an open movie with a quality ladder, and a fictional series
whose episode exists in two versions — are in
[`library/v1/examples`](https://github.com/zaentrum/schemas/tree/main/library/v1/examples).

## In this section

| Page | Covers |
|---|---|
| [manifest.json](./manifest.md) | Every field of the entry point, and how it stays readable by version 2 readers |
| [metadata.json](./metadata.md) | Texts, images and their naming, credits, video references, locks, and how a re-sync would work |
| [Versions, audio, subtitles and quality](./versions.md) | Director's cuts, black-and-white and colour presentations, stereo and 5.1, SDH, forced and commentary tracks, quality ladders, and when an original may be deleted |
| [Migrating a library](./migrating.md) | Building item folders from an existing catalog, applying them on storage safely, and what must change before a platform uses the format |
