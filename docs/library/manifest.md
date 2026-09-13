# manifest.json

The entry point of every item folder. Schema:
<https://zaentrum.github.io/schemas/library/v1/manifest.schema.json>.

Every path inside a manifest is relative to the folder the manifest sits in.

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
| `externalIds` | Explicit reference keys: `tmdbMovie`, `tmdbTv`, `tmdbSeason`, `tmdbEpisode`, `tmdbCollection`, `imdb`, `tvdb`. On an episode, `tmdbTv` is the parent series. These are enough to fetch every text and image again. |
| `match` | How far to trust `externalIds`: `status` (`matched`, `unmatched`, `manual`, `disputed`), who decided, and the evidence. A person's decision is never overwritten by automation. |
| `metadata.file` | Always `metadata/metadata.json`. |

## Compatibility with version 2 readers

Version 3 is the version 2 package manifest with library sections added. Every
version 2 field keeps its name, type and meaning at the top level, so a reader
that understands version 2 keeps playing the item:

| Version 2 field | Notes |
|---|---|
| `itemId`, `type`, `title`, `year` | As above. |
| `tmdbId` | Ambiguous — the movie id on a movie but the **series** id on an episode. Kept for version 2 readers; new readers use `externalIds`. |
| `durationMs`, `packagedAt`, `packager` | The package stored in this folder. |
| `renditions.video[]`, `renditions.audio[]` | HLS renditions. More than one video entry is a quality ladder. Version 3 adds `sourceStreamIndex` to each, `sourceChannels` to audio (6 when a 5.1 track was downmixed to stereo), and `dynamicRange` to video. |
| `subtitles[]`, `trickplay`, `trailers[]` | Unchanged. |
| `seriesTitle`, `seasonNumber`, `episodeNumber`, `episodeCode` | Episodes only, aired order. |

A series has no playback fields: its playable content is its episodes.

## Series

```json
"series": {
  "defaultOrdering": "aired",
  "seasons": [
    { "number": 1, "tmdbSeason": "12345",
      "episodes": [ { "itemId": "…", "path": "episodes/…/", "episode": 1, "episodeEnd": null } ] }
  ],
  "masters": [
    { "fingerprint": "hevc/main10/10bit/hdr10/3840x2160", "presentation": "colour hdr10", "episodes": ["…"] }
  ]
}
```

- `seasons[]` lists every episode folder, grouped by season in the default
  ordering. Season `0` holds specials. A series folder contains exactly the
  episode folders listed here — the validator rejects both a missing and an
  unlisted folder.
- `masters[]` groups episodes by the technical fingerprint of their originals.
  More than one master means a season mixes sources: a viewer may see HDR and SDR
  episodes, or two different cuts, side by side.

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
[Versions, audio and quality](./versions.md) explains how they are told apart;
this is the shape.

| Field | Meaning |
|---|---|
| `id` | UUID of the version. |
| `path` | `.` for the package stored in this folder; `versions/<id>/` for any other. |
| `label` | What a viewer picks between: `Director's Cut`, `Black & White`, `Dolby Vision`. `null` when nothing distinguishes it. |
| `primary` | Played when the viewer does not choose. Exactly one version is primary, independent of where it is stored. |
| `edition` | `kind` (`theatrical`, `directors-cut`, `extended`, `unrated`, … `unknown`), with evidence, confidence, who decided, and `review` — set when automation could not decide and says what a person should check. |
| `presentation` | `colour` (`colour`, `black-and-white`, `partial-colour` — measured from the picture), `dynamicRange`, `stereo3d`, `aspectRatio`. |
| `runtime` | `measuredMs` from the original against `referenceMs` from the reference database, and the difference. |
| `completeness` | `complete`, `truncated`, `suspect` or `unknown`, with evidence. |
| `master` | `fingerprint` of the original and whether it is an untouched `original` or already a `derivative` re-encode. |
| `truth` | `source` while the original exists, `package` once it is deleted. |
| `sources[]` | The original file(s) — see [source record](#source-record). |
| `package` | The package's account of itself — see [package record](#package-record). `null` when nothing is packaged. For a version stored in `versions/<id>/` it also carries a `playback` block with the version 2 playback fields. |
| `lostIfOriginalDeleted[]` | Everything the original has that the package lacks. See [the deletion check](./versions.md#deleting-an-original). |

### Source record

Everything known about an original file, kept after the file is deleted.

| Field | Meaning |
|---|---|
| `state` | `present` or `deleted`. |
| `file` | Original `name`, `sizeBytes`, `mtime`, `fixity` (`qh1` always, full `sha256` when computed), `origin.libraryPath` and `origin.folder` (the folder name is often the only record of an edition or a series qualifier such as `(US)`), `ownership`, `part` when a version is split into files, and `deletedAt`/`deletionReason` once gone. |
| `labels` | What the filename claims: quality, release source, resolution, edition wording. Unreliable, and kept exactly as found. |
| `container` | Format, duration, bitrate, and the container title — often the original release name. |
| `fidelity` | `original`, `derivative` or `unknown`, with evidence (encoder tags, a track title naming a format the stream no longer has). |
| `streams[]` | Every stream. Video: codec, profile, bit depth, resolution, colour, HDR10 mastering data, Dolby Vision profile, 3D. Audio: codec, profile, `channels`, `channelLayout`, lossless, Atmos/DTS:X, and `titleClaim`. Subtitles: text or image, styled, variant. Attachments: fonts and covers. Each with language and dispositions (default, forced, commentary, hearing impaired, audio description). |
| `chapters[]`, `segments[]` | Chapter marks; detected intro, recap and credits ranges. |
| `sidecars[]` | Small files that sat next to the original (external subtitles, NFO), copied into `source/<sourceId>/`. |
| `subtitleDecisions` | A curated default subtitle mapped to one of these streams, when the mapping is unambiguous. |
| `covers[]` | Episode ids this file contains, when one file holds several episodes. |
| `essence` | The irreplaceable properties, reduced for comparison: max audio channels, surround, lossless and object audio, video height and bit depth, HDR10 metadata, Dolby Vision, 3D, audio and subtitle languages, image and styled subtitles, fonts, chapters, commentary tracks. |
| `probe` | Where the verbatim `ffprobe` output is (`source/<sourceId>/ffprobe.json`) and its `sha256`. |

### Package record

| Field | Meaning |
|---|---|
| `state` | `complete`, `failed`, `stale` or `building`. |
| `role` | `derived` while the original exists; `canonical` once the package is the only copy. |
| `recipe` | How video, audio and subtitles were produced. |
| `fidelity` | `lossless`, and `losses[]` — every way the package is poorer than the original: `audio-downmix`, `audio-codec`, `audio-dropped`, `video-resolution`, `video-bitdepth`, `dynamic-range`, `dolby-vision`, `stereo3d`, `subtitle-dropped`, `subtitle-styling`, `attachments-dropped`, `chapters-dropped`. |
| `essence` | The same reduced properties as the source, for the package. |
| `chapters[]` | Chapter marks the package carries. A canonical package must carry them. |
| `decisions` | The default audio and subtitle a viewer gets, and where each decision came from. Often hand-corrected, and irreplaceable. |
| `playback` | Only for a version stored in `versions/<id>/`: its `durationMs`, `packagedAt`, `packager`, `renditions`, `subtitles`, `trickplay`. |

## Processing and provenance

`processing` records terminal outcomes of pipeline steps (`done`, `failed`,
`skipped`, `not-applicable`, `pending`) so a rebuilt system does not redo
expensive work; in-flight state stays in the database. `provenance` records how
the item entered the library.

## Example

A trimmed movie manifest (the full file is in the
[examples](https://github.com/zaentrum/schemas/tree/main/library/v1/examples/movies)):

```json
{
  "schema": "zaentrum.library.manifest/1",
  "version": 3,
  "itemId": "68324514-b3cd-5b1c-b8cf-74edb830ddbc",
  "type": "movie",
  "title": "Tears of Steel",
  "year": 2012,
  "tmdbId": "133701",
  "externalIds": { "tmdbMovie": "133701", "imdb": "tt2285752" },
  "match": { "status": "matched", "decidedBy": "tmdb" },
  "metadata": { "file": "metadata/metadata.json" },
  "durationMs": 734000,
  "renditions": {
    "video": [ { "id": "v0", "dir": "hls/v0", "codec": "hev1.1.6.L120.B0", "width": 1920, "height": 800, "hdr": false, "…": "…" } ],
    "audio": [ { "id": "a0", "dir": "hls/a0", "codec": "mp4a.40.2", "channels": 2, "sourceChannels": 6, "…": "…" } ]
  },
  "versions": [ {
    "id": "…", "path": ".", "label": null, "primary": true,
    "edition": { "kind": "theatrical", "decidedBy": "inferred", "confidence": 0.6 },
    "presentation": { "colour": "colour", "dynamicRange": "sdr", "stereo3d": "none" },
    "truth": { "kind": "source" },
    "sources": [ { "state": "present", "file": { "name": "Tears of Steel (2012) Bluray-1080p.mkv", "…": "…" },
                   "streams": [ { "index": 1, "type": "audio", "codec": "ac3", "channels": 6, "channelLayout": "5.1(side)" } ] } ],
    "package": { "state": "complete", "role": "derived",
                 "fidelity": { "lossless": false, "losses": [ { "kind": "audio-downmix", "detail": "6ch -> 2ch (a0)" } ] } },
    "lostIfOriginalDeleted": [ "surround", "chapters", "audioChannels 6->2" ]
  } ]
}
```
