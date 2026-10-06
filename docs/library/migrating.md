# Migrating a library

How a platform's catalog and the store it kept before become the library of
[Database first, storage as the record](./record.md), and — further down — the
reference tooling that builds v1 item folders from an export.

> **Status — being built.** The staging tool is published in the
> [schemas repository](https://github.com/zaentrum/schemas); the catalog's adopt,
> its layout switch and its retire job are being built. No environment has been
> migrated yet.

## Moving a platform to the library

Before the move, a platform keeps its originals under `media/`, its packages
under `packages/` and the extras it took in under `extras/`, all at the share's
root. After it, the root holds the library — `movies/`, `series/`, `people/` —
and `.work/`, where an original waits among the arrivals (`.work/incoming/`,
laid out as `media/` was) until it is deleted. Nothing is copied but small
files: every package folder and every original is renamed, on the same
filesystem.

```mermaid
flowchart LR
  I["inventory<br/>--dry-run: report.json"] --> S["stage<br/>records under .work/migration/run/"]
  S --> A["adopt<br/>renames + one transaction per item"]
  A --> V["verify<br/>validator · media check · compare · play"]
  V --> L["library.layout = v2"]
  L --> R["library.originals = delete-after-package<br/>originals retired"]
  R --> C["cleanup<br/>the old folders aside"]
```

### 1. Inventory

Export the catalog (`db/export/library-export.sql` of the catalog service) and
run the staging tool with `--dry-run` where the share is mounted and `ffprobe` is
on the path — the packager's image has both:

```sh
cat tools/libv2_records.py tools/library-v2-from-catalog.py | \
  python3 - --platform --export catalog.json --root /var/lib/katalog --run 2026-10-07a --dry-run
```

It probes every original and hashes nothing, and writes only
`.work/migration/<run>/report.json`: what is ready, every problem by its class —
an original that is missing, a package that never finished, an episode no series
holds, music (which the library does not record), a sidecar no subtitle of the
package was made from — and what deleting every original would cost: how many
titles would lose surround sound, image subtitles, a subtitle language. Review
that before anything is deleted.

### 2. Stage

The same command without `--dry-run` stages the records under
`.work/migration/<run>/`, online, reading the store and writing nothing outside
the run's folder: every item's folder as the library will hold it, its version
records with the checksums of the package files hashed where they are, copies
of the sidecars, the people the items credit, and per item a plan,
`units/<itemId>.json`, of what moves where and what the database changes. A
version keeps no original — the original goes to the arrivals and is deleted
later — and a package whose original is already gone gets a source record that
says so. Staging again writes the same records. A large catalog is staged by
shard: an export of one shard (`psql -v shard=f0 -f library-export.sql`) and
`--shard f0`, every shard of a run with the same `--as-of`.

### 3. Adopt

With the transcoder and the packager paused, the catalog service adopts the
run, item by item — series before episodes, items before people — under a lock on
the item: it checks the plan's guards (the old package unchanged since it was
staged), renames the package folders into the staged records, the item folder
into place and the original and its sidecars to the arrivals, moves what is left
of the old package folder aside, and changes the database in one transaction —
keeping every subtitle default someone chose, which no record holds. A journal
records every step, so an item's adopt is undone in reverse, and a run can be
reverted while its originals have not been purged.

### 4. Verify

```sh
python tools/library-v2-media-check.py /var/lib/katalog
python tools/validate-library-v2.py --check-media /var/lib/katalog
python tools/library-v2-rebuild.py /var/lib/katalog --compare catalog-after.json \
  --arrivals-root /var/lib/katalog/.work --ignore-fields id,path,hash
```

The media check prints `OK`; the validator finds no error — it reads past
`.work/`, and the folders of the old store are a note until the cleanup; the
compare against an export taken after the adopt exits 0 — the rows of the files
waiting at the arrivals are no part of the record, and a subtitle's default is
behaviour it never compares. Then every title and every extra plays, and the
count of packaged rows is the count of `.complete` markers.

### 5. Switch the layout

Set `library.layout` to `v2`: the scan finds new arrivals in `.work/incoming/`,
the workers get the library's paths in their work records, and the catalog
projects `metadata.json` and `person.json` as the database changes.

### 6. Retire the originals

Set `library.originals` to `delete-after-package`. The retire job takes each
original once its version is recorded and the steps that read it are done:
verifies the package — the chain, or every byte, read by the catalog service
itself, not by the packager that wrote it — checks the original is still the
file that was recorded, writes the `original-deleted` event and moves the
original to `.work/trash/`, at a limited rate. The trash is emptied after its
grace period, the window in which a retirement can still be undone.

### 7. Clean up

`media/`, `packages/`, `extras/` and `incoming/` hold nothing the catalog knows
any more: what is left is moved to `.work/legacy/` and reported, and the
migration's folder is deleted once the last retired original has left the trash.

## Building v1 item folders from an export

The rest of this page is the reference tooling of v1, where storage is the source
of truth: it builds and validates sample libraries from an export of a legacy
catalog. There is no in-platform job for it.

### The tools

| Tool | Does |
|---|---|
| [`tools/library-migrate.py`](https://github.com/zaentrum/schemas/blob/main/tools/library-migrate.py) | Builds a staging tree of `manifest.json`, `metadata/` and `source/` for every item, a plan of storage operations for the large files, and a report. |
| [`tools/validate-library.py`](https://github.com/zaentrum/schemas/blob/main/tools/validate-library.py) | Validates a tree against the schemas and the cross-file rules. |
| [`tools/test-validate-library.py`](https://github.com/zaentrum/schemas/blob/main/tools/test-validate-library.py) | The broken trees the validator must reject. |
| [`tools/package-checksums.py`](https://github.com/zaentrum/schemas/blob/main/tools/package-checksums.py) | Writes each package's `checksums.sha256` and records it in the manifest, or verifies them with `--verify`. Runs where the package files are readable. |
| [`tools/make-library-examples.py`](https://github.com/zaentrum/schemas/blob/main/tools/make-library-examples.py) | Regenerates the published examples. |

### Steps

```mermaid
flowchart LR
  X["export<br/>catalog · probes · package manifests · artwork"] --> G["library-migrate.py<br/>staging tree + plan + report"]
  G --> C["validate-library.py<br/>on the staging tree"]
  C --> A["apply on storage<br/>new folder, never in place"]
  A --> V["validate-library.py --check-media<br/>on storage"]
  V --> S["swap into place<br/>one rename"]
```

#### 1. Export

The migrator reads one folder of inputs. The export that produces them is
specific to the legacy catalog and is not published; the migrator's docstring
defines each file.

| Input | Content |
|---|---|
| `paths.tsv` | One row per item: id, type, parent id, season, episode, original file path, size, package manifest path. |
| `catalog.json` | Rows of the legacy catalog tables: items, external ids, people, genres, tags, artwork, chapters, segments, playback, subtitles, trailers, processing steps. |
| `probes.jsonl` | Per original: the `ffprobe` JSON and a file stat (size, mtime, owner, mode) with `qh1` fixity — sha256 of the first and last 64 KiB plus the size. The migrator refuses an original without `qh1`. |
| `fetched.jsonl` | Per item: the existing package manifest, its sha256, whether `.complete` exists, the package folder, and sidecar files next to the original. |
| `artwork.jsonl` | Artwork bytes per item and kind. |
| `colour.tsv` | Per item: peak chroma at sampled times (`sec:satmax,…`). Without it every `presentation.colour` is `unknown`. |
| `tmdb.json`, `tmdb_images.json` + `images/` | Optional: reference-database data the catalog never stored — release dates, season details, season posters, episode stills, logos, person ids. |

#### 2. Build

```sh
python tools/library-migrate.py --inputs export/ --out staging/ \
  --library-root /var/lib/katalog/media --packages-root /var/lib/katalog/packages
```

`--library-root` and `--packages-root` are the path prefixes the export's paths
start with. `--items id,id` builds only those movies or series. `--originals leave`
keeps originals in the source library (their `file.path` stays null), so the
version folders hold only their packages — the end state once originals are
deleted; the default `place` plans each original into its version folder. The run
writes:

| Output | Content |
|---|---|
| `staging/library/` | The item folders: `movies/` and `series/`. Validate this folder: `python tools/validate-library.py staging/library`. |
| `staging/plan.tsv` | The storage plan: an `original` row per original file (the file in the source library, and where it goes in its version folder) and a `package` row per package (the existing package folder, and the item folder it belongs in). |
| `staging/report.json` | What needs a person or blocks deleting originals, below. |

Report entries:

| Report entry | Meaning |
|---|---|
| `unmatched-needs-review` | No reference id. |
| `package-checksums-to-compute` | Every package: its checksums can only be computed where its files are. |
| `segments-beyond-runtime` | A detected intro or credits range that ends after the measured runtime — a detector error, kept as found. |
| `disc-image-not-probed` | A disc image whose streams, runtime and colour were never measured. |
| `episode-match-disputed` | The original filename names a different episode of the season than the one the catalog matched. |
| `edition-needs-review` | Runtime far beyond the reference with no edition wording. |
| `colour-needs-review` | Black-and-white from sparse samples. |
| `mixed-masters` | A series whose episodes come from different masters. |
| `lost-if-original-deleted` | Every version whose package lacks something its original has. |
| `package-forced-flag-missing` | A forced or signs-and-songs track, recognised by its title or content, that the package does not flag forced. Only version 2 readers are affected; the migration does not change the hint. |
| `forced-track-flagged-default` | A forced or signs-and-songs track the package flags default. |
| `rendition-title-overclaims` | A package audio rendition whose title names more channels or another format than it carries, e.g. "TrueHD 7.1 Atmos" on two-channel AAC. |
| `interchangeable-audio-renditions` | Renditions of one language and purpose that are identical and titled only by their former format; a menu offers them once. |
| `indistinguishable-audio-renditions` | Renditions that look identical without such titles and may differ in content; name them by hand. |
| `commentary-subtitles-without-commentary-audio` | Commentary subtitles, but no audio track recognisable as the commentary: set its purpose by hand. |
| `empty-in-legacy-catalog` | Movie release date or content rating missing. |
| `credits-without-tmdb-person` | Credits that could not be tied to a reference-database person. |
| `episode-identity-differs-from-package` | An episode's series title or code in the old package manifest differs from the catalog; the package's value is kept. |
| `episode-art-kept-as-two-images` | An episode whose catalog poster and backdrop were different images. |
| `created-at-missing` | An item without a catalog creation time; it gets the migration time. |

A staging tree is always `rev` 1. The migration time is recorded as such
(`provenance.migratedAt`, decision times). A probe's `at` and a fetched image's
`fetchedAt` are the modification times of `probes.jsonl` and `tmdb_images.json`,
so keep file times when copying an export (`cp -p`, `rsync -t`). Catalog times
without a time zone are taken as UTC.

#### 3–6. Validate, apply, check, swap

Validate `staging/library`, apply it on storage into a new folder next to the
live one, compute the package checksums there with `tools/package-checksums.py`
(on storage, or in a pod that mounts it — the staging tree has no media), validate
that folder with `--check-checksums`, then swap it into place with one rename and
keep the old folder until the new one has been read back.

### Applying on storage

The library is read by machines. It holds nothing but `<category>/<aa>/<id>` item
folders — no browsing views, no symbolic links, no hard links — so it can be
copied anywhere, including object storage, and read back unchanged.

The documents and images are small and are copied. Originals and packages are
large: the plan **moves** each into its version folder. On the same filesystem a
move is a rename — instant, no extra space, and nothing is left behind at the
old path. Across filesystems it is a copy followed by removing the source once the
copy is verified. Either way every file in the library is an ordinary, independent
file. The existing package's `manifest.json` is not moved: the item folder gets
the new manifest instead.

When applying over an existing library rather than into a new folder, carry each
document's `rev` forward and increment it, so a cache that keys on `rev` sees the
change.

#### Writing safely

- **Build next to the live tree, then rename.** A half-applied tree is never
  visible to readers.
- **Replace a document by writing a new file next to it and renaming it over the
  old name**, as `package-checksums.py` does with `manifest.json`: a reader sees
  either the old or the new file, never a partial one.
- **Verify before removing anything:** compute the package checksums in the new
  folder and check them (`validate-library.py --check-checksums`); only then
  remove the old package folder or original.
- **No hard links.** A test library may be filled faster with hard links, but a
  hard link ties a library file to another path — a write through either name
  changes both, and a copy of the tree duplicates the data. `--check-media`
  rejects any package or original file that is a hard link.

### Before a platform uses the format

The migrated tree can be built, validated and inspected today. Serving from it,
or deleting the old package folders or any original, needs these changes first:

| Component | Today | Needed |
|---|---|---|
| Streaming origin, catalog manager | Find a package in today's package store at `{movies,shows}/<aa>/<itemId>/`; episode packages are flat. | Resolve an episode through its series manifest, or an index built from the manifests. Until then, keep the flat episode folders. |
| Packager | Re-packaging empties the whole item folder and writes a version 2 manifest; it flags a subtitle `forced` only from the stream flag. | Replace only package artifacts (`hls/`, `subs/`, `trickplay/`, markers) and merge the version 2 playback fields into the existing version 3 manifest, keeping or recomputing the version 3 track fields (`purpose`, `purposeFrom`, `variant`, `original`) and incrementing `rev`. Until then, do not point it at a migrated library. |
| Players (web, TV, mobile) | Read only the version 2 `forced` and `default` hints. | Derive forced display and defaults from `purpose`, language and the viewer's settings, and build the track menu from language, `variant` and `purpose`. |
| Streaming origin, unpackaged items | Plays an original from the path the catalog stores, in the source library. | Play it from the version folder named by `sources[].file.path`. |
| Catalog | Keeps its truth in a database. | A cache builder that reads the folders, and writers that update the documents. |
| Stream manifest reader | Documents a policy of rejecting unknown versions, not implemented. | Accept version 3 explicitly, with a test on a version 3 manifest. |

Do not delete an original while the version's `lostIfOriginalDeleted` is not
empty, while its match is `disputed` or `unmatched`, or before the readers above
can find its package.

### Building a cache

A catalog database becomes a cache of the library: walk
`movies/*/*/manifest.json` and `series/*/*/manifest.json` (and each series'
episodes), read each item's `metadata/metadata.json`, and upsert. Store each
document's `rev` together with its file hash; on a rebuild skip items where both
are unchanged. A lost cache is rebuilt the same way.
