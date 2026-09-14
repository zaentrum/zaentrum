# manifest.json

The entry point of every item folder. Schema:
<https://zaentrum.github.io/schemas/library/v1/manifest.schema.json>.

> **Status — format ahead of the code.** No platform service writes or reads
> this document yet; the [reference migrator](./migrating.md) produces it. See
> [the library format](./README.md) for what exists today.

**Paths.** The top-level playback fields, `versions[].path`, probe files and
sidecars are relative to the item folder. The original file (`sources[].file.path`),
paths inside a version's `package.playback` block and its checksums file are
relative to that version's folder (the item folder for `.`, otherwise `versions/<id>/`). A source's `origin.libraryPath` is relative to the root of
the source library it came from.

## Identity

| Field | Meaning |
|---|---|
| `schema` | Always `zaentrum.library.manifest/1`. |
| `version` | Playback format version, `3`. See [compatibility](#compatibility-with-version-2-readers). |
| `itemId` | UUID; equals the folder name. Never changes. |
| `rev`, `createdAt`, `updatedAt` | `rev` increments on every write. `createdAt` is when the item entered the library; it orders "recently added" and survives every migration unchanged. |
| `type` | `movie`, `series` or `episode`. |
| `title` | Primary title as matched: the English title where the reference database has one, otherwise the original title. Localised and edited titles are in [metadata](./metadata.md). |
| `year` | Release year (first air year for a series). |
| `externalIds` | Explicit reference keys: `tmdbMovie`, `tmdbCollection`, `imdb` on a movie; `tmdbTv`, `imdb`, `tvdb` on a series; `tmdbTv` (the parent series), `tmdbSeason`, `tmdbEpisode` on an episode. Enough to fetch every text and image again. |
| `match` | How far to trust `externalIds`: `status` (`matched`, `unmatched`, `manual`, `disputed`), who decided, the evidence, and `review` when a person should look — for example an episode whose original filename names a different episode than the one it was matched to. A person's decision is never overwritten by automation. |
| `metadata.file` | Always `metadata/metadata.json`. |

## Compatibility with version 2 readers

Version 3 is the version 2 package manifest with library sections added. Every
version 2 field keeps its name, type and meaning at the top level. Decoding
every manifest of the migrated sample with the streaming origin's own version 2
types gives values identical to the original version 2 manifests.

| Version 2 field | Notes |
|---|---|
| `itemId`, `type`, `title`, `year` | As above. |
| `tmdbId` | Ambiguous — the movie id on a movie but the **series** id on an episode. Kept for version 2 readers; new readers use `externalIds`. Absent on a series. |
| `durationMs`, `packagedAt`, `packager` | The package stored in the item folder. Every timestamp in the format is RFC 3339 with an upper-case `T` and `Z`, and integer fields are whole numbers within 64 bits (`2`, never `2.0`), because the version 2 reader rejects anything else. |
| `renditions.video[]`, `renditions.audio[]` | HLS renditions. More than one video entry is a quality ladder. Version 3 adds `sourceStreamIndex` to each, `dynamicRange` to video, and to audio `sourceChannels` (6 when a 5.1 track was downmixed to stereo), `purpose` (`main`, `commentary`, `description`, `unknown`), `purposeFrom`, `variant` and `original` (true when the file flags the track as the original language, otherwise null) — see [subtitles and audio for different viewers](./versions.md#subtitles-and-audio-for-different-viewers). The version 2 `default` and `visible` fields are playback hints the packager writes for existing readers, not library data. |
| `subtitles[]` | Version 3 adds `sourceStreamIndex` (null when the original stream is not known), `purpose` (`dialogue`, `sdh`, `forced`, `signs-songs`, `commentary`, `lyrics`, `unknown`), `purposeFrom` and `variant`. Every rendition must carry `purpose` and `purposeFrom`. The version 2 `default`, `forced` and `visible` fields are playback hints, not library data. |
| `trickplay`, `trailers[]` | Unchanged. |
| `seriesTitle`, `seasonNumber`, `episodeNumber`, `episodeCode` | Episodes only, aired order. |

The document is compatible; the **location** of episodes is not. A version 2
reader finds a package at `shows/<aa>/<episodeId>/`, while this format nests the
episode under its series. See
[before a platform uses the format](./migrating.md#before-a-platform-uses-the-format).

A series has no playback fields and no `tmdbId`: its playable content is its episodes.

## Series

```json
"series": {
  "defaultOrdering": "aired",
  "seasons": [
    { "number": 1, "tmdbSeason": null,
      "episodes": [ { "itemId": "…", "path": "episodes/…/", "episode": 1, "episodeEnd": null } ] }
  ],
  "masters": [
    { "fingerprint": "hevc/main10/10bit/hdr10/3840x2160", "presentation": "colour hdr10", "episodes": ["…"] }
  ]
}
```

- `seasons[]` lists every episode folder, grouped by season in the default
  ordering. Season `0` holds specials. A series folder contains exactly the
  episode folders listed here, and each episode's coordinates for the default
  ordering must agree with its place in this list.
- `masters[]` groups all episodes of the series by the technical fingerprint of
  their originals. More than one master means the series mixes sources; compare
  each master's episodes with `seasons[]` to see which seasons are affected.

Season names, overviews and posters are texts and images, so they live in the
series' [metadata](./metadata.md#series-and-seasons).

## Episode

```json
"episode": {
  "seriesId": "…",
  "coordinates": [
    { "scheme": "aired", "season": 1, "episode": 3, "episodeEnd": null },
    { "scheme": "file",  "season": 1, "episode": 3, "episodeEnd": null }
  ]
}
```

`seriesId` is the series folder two levels up. `coordinates` records the same
episode under every numbering scheme that is known: `aired`, `dvd`, `absolute`,
`production`, and `file` — how the original filename numbered it, the only
record of how a file was labelled. `episodeEnd` is set when one file holds
several episodes.

## Versions

Movies and episodes carry `versions[]`: every cut or presentation of the item.
[Versions, audio, subtitles and quality](./versions.md) explains how they are told apart;
this is the shape.

| Field | Meaning |
|---|---|
| `id` | UUID of the version. |
| `path` | `.` for the version stored in the item folder (at most one); otherwise exactly `versions/<id>/`. |
| `label` | What a viewer picks between: `Director's Cut`, `Black & White`, `Dolby Vision`. `null` when nothing distinguishes it. |
| `primary` | Played when the viewer does not choose. Exactly one version is primary, independent of where it is stored. |
| `edition` | `kind` (`theatrical`, `directors-cut`, `extended`, `unrated`, … `unknown`), with evidence, confidence, who decided, and `review` when a person should confirm. |
| `presentation` | `colour` (`colour`, `black-and-white`, `partial-colour`, `unknown` — measured from the picture, with its own decision and review), `dynamicRange`, `stereo3d`, `aspectRatio`. |
| `runtime` | `measuredMs` from the original against `referenceMs` from the reference database, and the difference. |
| `chapters[]`, `chaptersFrom` | Chapter marks (start, end, title) on this version's timeline, and where they came from: the `original-file`, the `legacy-catalog`, or a `human`. Kept on the version rather than in any file, so they survive the original's deletion and apply to every package of the version. |
| `segments[]` | Intro, recap and credits ranges on the version's timeline, each with the `detector` that found it and its `confidence`. |
| `completeness` | `complete`, `truncated`, `suspect` or `unknown`, with evidence. |
| `master` | `fingerprint` of the original and whether it is an untouched `original`, already a `derivative` re-encode, or `unknown`. |
| `truth` | `source` while any original exists, `package` once every original of the version is deleted. |
| `sources[]` | The original file(s) — see [source record](#source-record). |
| `package` | The package's account of itself — what it carries and lost, not how it should be played — see [package record](#package-record). `null` when nothing is packaged. The top-level playback fields exist exactly when the version at `.` has a package. |
| `lostIfOriginalDeleted[]` | Everything the original has that the package lacks. See [deleting an original](./versions.md#deleting-an-original). |

### Source record

Everything known about an original file, kept after the file is deleted.

| Field | Meaning |
|---|---|
| `state` | `present` or `deleted`. |
| `file` | Original `name`; `path`, the original file in the version's folder while it is kept there (null while it still lives only in the source library, and after deletion); `sizeBytes`, `mtime`, `fixity` (`qh1` always, full `sha256` when computed), `origin.libraryPath` and `origin.folder` (the folder name is often the only record of an edition or of a series qualifier such as `(US)`), `ownership`, `part` when a version is split into files, and `deletedAt`/`deletionReason` once gone. |
| `labels` | What the filename claims: the quality token as found, the `medium` it names (`disc`, `web`, `broadcast`, `unknown`), resolution, edition wording. Unreliable — a name can claim a disc copy that is a re-encode — and kept exactly as found. |
| `container` | Format, duration, bitrate, tags, and the container title, often the richest record of what the file was before any re-encode. |
| `fidelity` | `original`, `derivative` or `unknown`, with evidence (encoder tags, a track title naming a format the stream no longer has). |
| `streams[]` | Every stream. Video: codec, profile, bit depth, resolution, colour, HDR10 mastering data, Dolby Vision profile, 3D. Audio: codec, profile, `channels`, `channelLayout` (null when the probe did not record one), lossless, Atmos/DTS:X, `titleClaim`, `purpose`, `purposeFrom` and `variant`. Subtitles: text or image, styled, `variant`, `events` (the number of subtitle events the container records), `purpose` and `purposeFrom`. Video also records embedded `closedCaptions`. Attachments: fonts and covers. Each with language and dispositions exactly as the file flags them (default, forced, original, dub, commentary, hearing impaired, visual impaired, captions, lyrics, descriptions). |
| `sidecars[]` | Small files that sat next to the original (external subtitles, NFO), copied into `source/<sourceId>/` with size, hash and, for subtitles, `purpose`. |
| `covers[]` | Episode ids this file contains, when one file holds several episodes. |
| `essence` | The irreplaceable properties, reduced for comparison: max audio channels, surround, lossless and object audio, video height and bit depth, HDR10 metadata, Dolby Vision, 3D, audio and subtitle languages, SDH and forced subtitle languages (forced includes signs-and-songs tracks), commentary subtitles, audio description tracks, closed captions, image and styled subtitles, fonts, chapters, commentary tracks. |
| `probe` | Where the verbatim `ffprobe` output is (`source/<sourceId>/ffprobe.json`), its `sha256`, and when the probe ran — all `null` for an original that was never probed. |

### Package record

| Field | Meaning |
|---|---|
| `state` | `complete`, `failed`, `stale` (complete and playable, but outdated against its original or recipe) or `building`. |
| `role` | `derived` while an original exists; `canonical` once the package is the only copy. |
| `sizeBytes`, `peakBandwidthBps` | Total size of the package's files, and the highest `BANDWIDTH` in its master playlist, audio included — a peak, not an average. (The version 2 rendition field `bitrateBps` is often `0`.) |
| `recipe` | How video, audio and subtitles were produced. |
| `fidelity` | `lossless` (true exactly when `losses` is empty), and `losses[]` — every way the package is poorer than the original: `audio-downmix`, `audio-codec`, `audio-dropped`, `video-resolution`, `video-bitdepth`, `dynamic-range`, `dolby-vision`, `stereo3d`, `subtitle-dropped`, `subtitle-styling`, `closed-captions-dropped`, `attachments-dropped`, `other`. Chapter marks are not a loss: the version keeps them. |
| `essence` | The same reduced properties as the source, for the package. |
| `checksums` | The package's fixity: `file` (`checksums.sha256` in the version's folder, one `<sha256>  <path>` line per file of `hls/`, `subs/`, `trickplay/`, `trailers/` and `.complete`, readable by `sha256sum -c`), the file's own `sha256`, the number of `files`, their total `bytes`, and when it was computed. `null` until computed on storage. Once the original is deleted the package is the truth, and this is how a copy of it is verified file by file. |
| `playback` | Only for a version stored in `versions/<id>/`: its `durationMs`, `packagedAt`, `packager`, `renditions`, `subtitles`, `trickplay`. |

## Processing and provenance

`processing` holds the last recorded outcome of each pipeline step (`done`,
`failed`, `skipped`, `not-applicable`, `pending`) so a rebuilt system does not
redo expensive work. `provenance` records how the item entered the library,
including the legacy catalog's item id and who created and last modified it there.

## Example

A shortened movie manifest; `"…"` marks what was left out. The full file is in the
[examples](https://github.com/zaentrum/schemas/tree/main/library/v1/examples/movies).

```json
{
  "schema": "zaentrum.library.manifest/1",
  "version": 3,
  "itemId": "68324514-b3cd-5b1c-b8cf-74edb830ddbc",
  "rev": 1, "createdAt": "2026-09-13T12:00:00Z", "updatedAt": "2026-09-13T12:00:00Z",
  "type": "movie",
  "title": "Tears of Steel",
  "year": 2012,
  "tmdbId": "133701",
  "externalIds": { "tmdbMovie": "133701", "imdb": "tt2285752" },
  "match": { "status": "matched", "decidedBy": "tmdb" },
  "metadata": { "file": "metadata/metadata.json" },
  "durationMs": 734000,
  "packagedAt": "2026-09-01T10:00:00+00:00",
  "packager": "packager example",
  "renditions": {
    "video": [
      { "id": "v0", "dir": "hls/v0", "width": 1920, "height": 800, "bitrateBps": 8000000, "…": "…" },
      { "id": "v1", "dir": "hls/v1", "width": 1280, "height": 533, "bitrateBps": 3000000, "…": "…" }
    ],
    "audio": [ { "id": "a0", "dir": "hls/a0", "channels": 2, "default": true, "sourceChannels": 6, "…": "…" } ]
  },
  "versions": [ {
    "id": "…", "path": ".", "label": null, "primary": true,
    "edition": { "kind": "theatrical", "decidedBy": "inferred", "confidence": 0.6, "…": "…" },
    "presentation": { "colour": "colour", "dynamicRange": "sdr", "stereo3d": "none", "aspectRatio": "12:5" },
    "truth": { "kind": "source", "…": "…" },
    "sources": [ {
      "state": "present",
      "file": { "name": "Tears of Steel (2012).mkv", "…": "…" },
      "streams": [ "…", { "index": 1, "type": "audio", "codec": "ac3", "channels": 6, "channelLayout": "5.1(side)", "…": "…" }, "…" ],
      "…": "…"
    } ],
    "package": {
      "state": "complete", "role": "derived", "sizeBytes": 734000000, "peakBandwidthBps": 8192000,
      "fidelity": { "lossless": false, "losses": [ { "kind": "audio-downmix", "detail": "6ch -> 2ch (a0)" }, "…" ] },
      "…": "…"
    },
    "lostIfOriginalDeleted": [ "surround", "audioChannels 6->2", "…" ]
  } ],
  "…": "…"
}
```
