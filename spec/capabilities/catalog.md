# The catalog and the pipeline

The capabilities of the catalog, the library and its originals, and the pipeline
that prepares titles to play. No chapter describes them yet; the
[architecture](../../docs/architecture.md) and the decision records do in part,
and the [library format](../../docs/library/README.md) is its own document. The columns are
explained in [how to read it](./README.md#how-to-read-it); every row comes from
[capabilities.csv](./capabilities.csv).

<!-- generated: areas -->
## The catalog

What the library holds, as the catalog knows it: scanning, details, metadata, the rules a title must meet. Not specified yet. Depth: working. For the goal [Keep the library](../goals/README.md#keep-the-library).

| Capability | Who | Portal | Catalog console | CLI | Spec |
|---|---|---|---|---|---|
| Scan the library for new, moved and missing files | admin | built | partial | built | [self hosting](../../docs/self-hosting.md), [extras](../../docs/extending/extras.md), [First run](../portal/settings.md#first-run) |
| Hand a file on disk to the catalog as a title, by its outside identity | addon | — | — | — | [ingest](../../docs/extending/ingest.md), [0012 catalog identity for addons](../../docs/adr/0012-catalog-identity-for-addons.md) |
| Add a trailer or other extra to a title, remove one, or package them again | admin | — | no | — | [extras](../../docs/extending/extras.md) |
| Set the metadata key the catalog looks titles up with | admin | built | built | built | [self hosting](../../docs/self-hosting.md), [First run](../portal/settings.md#first-run) |
| Fill titles' texts, artwork, cast and crew and age ratings from a reference database | system | — | partial | — | [metadata](../../docs/library/metadata.md), [self hosting](../../docs/self-hosting.md) |
| Match a title by hand: search again by a corrected title, or pin its TMDB id | admin | — | built | — | — |
| Edit a title's texts, genres, tags and age rating by hand, kept from enrichment | admin | — | partial | — | [metadata](../../docs/library/metadata.md) |
| Remove a title from the catalog, and its files and package when asked | admin | — | built | — | [record](../../docs/library/record.md) |
| Correct the language of a title's audio or subtitle track | admin | — | built | — | — |
| Browse every title with its state and files, its episodes, and each person's credits | admin | — | partial | — | [architecture](../../docs/architecture.md) |
| Change the catalog's settings | admin | — | partial | — | — |
| See which titles break the master spec's rules, and why | admin | — | built | — | [0015 the package is the master](../../docs/adr/0015-the-package-is-the-master.md) |
| Read what the library holds, by catalog id or by a title's outside identity | addon | — | — | — | [holdings](../../docs/extending/holdings.md), [0012 catalog identity for addons](../../docs/adr/0012-catalog-identity-for-addons.md), [0003 catalog cqrs sole writer](../../docs/adr/0003-catalog-cqrs-sole-writer.md) |
| Read a title's original or its subtitles straight from the catalog | system | — | — | — | — |
| Add a folder that already holds films or shows to the library, from the console | admin | — | no | no | [Getting content in](../../docs/self-hosting.md#getting-content-in) |
| Keep several libraries, each with its own folders, kind and audience | admin | — | no | — | — |
| Take in new files by themselves, on a schedule or as they arrive | system | — | no | — | — |
| Read a title's details and artwork from the files kept beside it | system | — | no | — | — |
| Fill titles' details without a key of the admin's own | system | — | no | — | [First run](../../docs/self-hosting.md#first-run) |
| Choose a title's poster and backdrop, or give it one's own | admin | — | no | — | — |
| Put titles into a collection everyone sees | admin | — | no | — | — |
| Add a subtitle file to a title from the console | admin | — | no | — | — |

- Scan the library for new, moved and missing files: Never on a schedule: a scan runs when started. The console lists the last 25 scans, not the files a scan passed over
- Hand a file on disk to the catalog as a title, by its outside identity: In-cluster only; idempotent on the path. A title the library holds already is refused (409), never relinked
- Add a trailer or other extra to a title, remove one, or package them again: API only: the console's trailers tab lists a title's links, not its extras. Addons and Jobs take one in with POST /api/extras
- Set the metadata key the catalog looks titles up with: A TMDB key, write-only, checked with TMDB first: a refused one is not stored. Cleared, the env default (katalog-tmdb Secret) holds
- Fill titles' texts, artwork, cast and crew and age ratings from a reference database: Console: enrich one title again. Pending titles, people, ratings and backdrops API only. A video still fills missing artwork
- Match a title by hand: search again by a corrected title, or pin its TMDB id: For a title the search got wrong, or one scanned before there was a key, which is listed by its file name
- Edit a title's texts, genres, tags and age rating by hand, kept from enrichment: Console: title, year, tagline, description, and the lock. Genres, tags, a by-hand age rating and a new title API only
- Remove a title from the catalog, and its files and package when asked: A show takes its episodes; files go only when ticked and the title typed. Each removal is logged; the log is API only
- Correct the language of a title's audio or subtitle track: Wins over the file's tag; the packager labels the track with it the next time it packages the title
- Browse every title with its state and files, its episodes, and each person's credits: The list filters by type, genre, year and kept original, with sizes on disk, but shows the newest 200 that match: no paging
- Change the catalog's settings: Beyond its four API keys, a table of keys and values: a key is typed by hand; the console names no other setting or its values
- See which titles break the master spec's rules, and why: Against the rules the transcoder and packager report, checked in the background; sorted on the server, saved as CSV
- Read what the library holds, by catalog id or by a title's outside identity: With the addon's service account; holdings are refused to a capped token (403). The apps' reads of this API are chino rows
- Read a title's original or its subtitles straight from the catalog: Kept from an earlier service; nothing calls it: chino-stream serves playback and subtitles
- Add a folder that already holds films or shows to the library, from the console: the catalog scans one folder of the media volume, which the resource names
- Take in new files by themselves, on a schedule or as they arrive: a scan is started by an admin or the CLI; an addon hands its files over itself
- Read a title's details and artwork from the files kept beside it: subtitle files beside a video are taken in; files of details and artwork are not read
- Fill titles' details without a key of the admin's own: the published images carry no key; a file scanned without one is listed by its file name
- Choose a title's poster and backdrop, or give it one's own: a title shows the artwork enrichment found
- Add a subtitle file to a title from the console: a subtitle file beside the video is taken in by a scan; an addon can attach one

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `scan-library` | — | `katalog-manager mutation triggerScan`, `katalog-manager query scanJobs`, `katalog-manager query scanJob` and 2 more | `extras-scan`, `step-timeouts`, `scan-report-limit`, `episodes-per-file`, `catalog-events` |
| `hand-over-file` | — | `katalog-manager POST /api/ingest` | `episodes-per-file` |
| `manage-extras` | — | `katalog-manager mutation addExtra`, `katalog-manager POST /api/extras`, `katalog-manager mutation removeExtra` and 2 more | `removed-extra-grace`, `extras-scan` |
| `set-metadata-key` | — | `katalog-manager mutation setSecretSetting`, `katalog-manager mutation clearSecretSetting`, `zaentrum-portal POST /api/portal/setup/metadata` and 1 more | `metadata-key`, `key-check-timeout`, `metadata-keys` |
| `enrich-titles` | 12.C10 | `katalog-manager mutation enrichOne`, `katalog-manager mutation enrichPending`, `katalog-manager mutation retryNotFound` and 9 more | `ratings-countries`, `credit-roles`, `metadata-language`, `metadata-refresh`, `keyframe-artwork`, `fallback-metadata-key`, `artwork-source-keys`, `credit-caps`, `metadata-key`, `catalog-events`, `metadata-keys` |
| `match-title` | — | `katalog-manager mutation identify` | — |
| `edit-title` | — | `katalog-manager mutation updateItem`, `katalog-manager mutation createItem`, `katalog-manager mutation setItemGenres` and 2 more | `ratings-countries` |
| `remove-title` | — | `katalog-manager mutation deleteItem`, `katalog-manager query deletedItems` | — |
| `set-track-language` | — | `katalog-manager mutation setTrackLanguage` | — |
| `browse-catalog` | — | `katalog-manager query items`, `katalog-manager query movies`, `katalog-manager query series` and 14 more | `series-episodes-page` |
| `change-catalog-settings` | — | `katalog-manager query settings`, `katalog-manager mutation createSetting`, `katalog-manager mutation updateSetting` and 2 more | — |
| `check-compliance` | — | `katalog-manager query pipelineRules`, `katalog-manager query libraryCompliance`, `katalog-manager mutation refreshCompliance` and 3 more | `compliance-pass`, `compliance-readers`, `compliance-nightly`, `compliance-tolerance`, `rules-report-interval`, `compliance-report-page`, `shown-languages`, `video-caps`, `audio-language-rules` |
| `read-library-holdings` | — | `katalog-api ANY /api/v1`, `katalog-api GET /api/v1/holdings` | `holdings-page-size` |
| `read-originals-directly` | — | `katalog-manager GET /api/play/{itemId}`, `katalog-manager GET /api/subtitles/items/{itemId}`, `katalog-manager GET /api/subtitles/{subId}` | — |
| `add-library-folder` | — | — | — |
| `keep-several-libraries` | — | — | — |
| `scan-by-itself` | — | — | — |
| `read-local-metadata` | — | — | — |
| `enrich-without-own-key` | — | — | — |
| `choose-artwork` | — | — | — |
| `curate-collections` | — | — | — |
| `add-own-subtitle` | — | — | — |

## The library and its originals

The packages the apps play, and the originals they were made from: verified, then retired. Not specified yet. Depth: working. For the goal [Keep the library](../goals/README.md#keep-the-library).

| Capability | Who | Portal | Catalog console | CLI | Resource | Spec |
|---|---|---|---|---|---|---|
| Retire an original once its package is verified and lacks nothing the spec keeps | system | — | no | — | — | [0015 the package is the master](../../docs/adr/0015-the-package-is-the-master.md), [versions](../../docs/library/versions.md), [migrating](../../docs/library/migrating.md), [record](../../docs/library/record.md) |
| Verify each new version against its own checksums, by a reader apart from the packager | system | — | no | — | — | [record](../../docs/library/record.md) |
| Retire the originals of chosen titles: a dry run first, then a run of what it found | admin | — | no | — | — | [0015 the package is the master](../../docs/adr/0015-the-package-is-the-master.md) |
| Hold a title's originals so that none is retired | admin | — | no | — | — | — |
| Decide whether an original another file replaced may go when it gives up more | admin | — | no | — | — | — |
| Give a title another file and keep its id, history, ratings and progress | addon | — | — | — | — | [0015 the package is the master](../../docs/adr/0015-the-package-is-the-master.md) |
| Encode queued titles again at a set pace and in set hours | system | — | partial | — | — | [0015 the package is the master](../../docs/adr/0015-the-package-is-the-master.md) |
| Queue titles that break a rule to be processed again under the current rules | admin | — | built | — | — | [0015 the package is the master](../../docs/adr/0015-the-package-is-the-master.md) |
| Keep a title that gets no package playable from its original in the library | system | — | no | — | — | — |
| Move a platform's store into the library layout, verify it, and undo it | operator | — | — | — | — | [migrating](../../docs/library/migrating.md), [record](../../docs/library/record.md) |
| Check a title's files on disk: its original, its package, and whether they match | admin | — | built | — | — | — |
| Fill in what the catalog records of titles' originals: probe, size and tracks | admin | — | no | — | — | — |
| Take a title out of the library again as one ordinary file | admin | — | no | no | — | [0015 the package is the master](../../docs/adr/0015-the-package-is-the-master.md) |
| Back up the library's files along with the databases | operator | no | — | no | no | — |

- Retire an original once its package is verified and lacks nothing the spec keeps: Off until library.originals says delete-after-package; v2 layout. Held titles stay. The console shows no retire state
- Verify each new version against its own checksums, by a reader apart from the packager: The newest first, one at a time, every file's hash. One that fails is tried again 6 h later, then longer. Not in the console
- Retire the originals of chosen titles: a dry run first, then a run of what it found: API only; v2 layout. Dry runs alone by default; a run takes what its dry run found, each title checked again
- Hold a title's originals so that none is retired: API only; a show's hold is its episodes'. The retire job then leaves them, whatever library.originals says
- Decide whether an original another file replaced may go when it gives up more: API only. Lists the originals held for an admin with what each gives up against the title's master; accept or keep
- Give a title another file and keep its id, history, ratings and progress: Addons library.replace.clients names; admins too, API only. With v2 the old original stays superseded till the new one verifies
- Encode queued titles again at a set pace and in set hours: The rules view shows the queue's counts and pace; clearing it, and its oldest and newest titles, API only
- Queue titles that break a rule to be processed again under the current rules: A selection, or every title the filter matches. One that processing again can't help is not queued, and says why
- Keep a title that gets no package playable from its original in the library: v2 layout: after a refused transcode or a packaging that failed for good, the original gets a version of its own; admins by hand
- Move a platform's store into the library layout, verify it, and undo it: A staging tool, then the catalog's routes with a service token; no zae command. library.layout v2 switches the scan and workers
- Check a title's files on disk: its original, its package, and whether they match: Read-only: ok, no package, original missing, stale, codec mismatch, retired or lost; a show rolls up its episodes
- Fill in what the catalog records of titles' originals: probe, size and tracks: API only, for titles packaged before the catalog kept these; running one again changes nothing
- Take a title out of the library again as one ordinary file: matters once an original is retired: its package is renditions in segments, not a file
- Back up the library's files along with the databases: the backups are dumps of the bundled databases; the media volume is left to its storage

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `retire-originals` | — | — | `originals-policy`, `retire-delay`, `retire-rate`, `trash-grace`, `verify-mode`, `verify-max-age`, `verify-reads`, `library-layout` |
| `verify-versions` | — | — | `verify-new`, `verify-mode`, `verify-max-age`, `verify-reads`, `verify-retry` |
| `retire-list` | — | `katalog-manager mutation retireOriginals`, `katalog-manager mutation stopRetireRun`, `katalog-manager query retireRun` | `retire-list-mode`, `retire-list-max-age`, `retire-rate`, `retire-list-size`, `retire-list-tries`, `library-layout` |
| `hold-originals` | — | `katalog-manager mutation holdOriginal` | — |
| `decide-superseded` | — | `katalog-manager query supersededOriginals`, `katalog-manager mutation decideSupersededOriginal` | `superseded-accept`, `superseded-delay`, `retire-rate` |
| `replace-title-file` | — | `katalog-manager mutation replaceSource`, `katalog-manager query replaceSourceDone` | `replace-clients`, `superseded-delay`, `superseded-accept`, `superseded-grace`, `library-layout` |
| `reencode-queue` | — | `katalog-manager POST /api/library/reencode`, `katalog-manager GET /api/library/reencode`, `katalog-manager mutation clearReencodeQueue` and 1 more | `reencode-rate`, `reencode-inflight`, `reencode-window`, `retry-interval` |
| `queue-rework` | — | `katalog-manager mutation queueRework`, `katalog-manager mutation queueReworkMatching` | — |
| `take-in-title` | — | `katalog-manager POST /api/items/{id}/takein` | `library-layout` |
| `move-to-library` | — | `katalog-manager POST /api/library/migrations/{run}/adopt`, `katalog-manager POST /api/library/migrations/{run}/revert`, `katalog-manager POST /api/library/migrations/{run}/names` and 4 more | `library-layout` |
| `check-title-files` | — | `katalog-manager mutation validateItem` | `small-file-threshold` |
| `backfill-source-facts` | — | `katalog-manager mutation backfillSourceProbes`, `katalog-manager mutation backfillSourceSizes`, `katalog-manager mutation backfillSourceTracks` | — |
| `export-title` | — | — | — |
| `back-up-library` | — | — | — |

## Preparing titles to play

What happens to a new title: analysed, encoded, packaged, given subtitles; and encoding while it plays. Not specified yet. Depth: working. For the goal [Keep the library](../goals/README.md#keep-the-library).

| Capability | Who | Catalog console | Resource | Spec |
|---|---|---|---|---|
| Find a title's intro, recap and credits | system | built | — | [11.8](../chino/playback.md#118-skip-and-up-next) |
| Read a title's chapters from its original, and of titles that miss them at a set pace | system | partial | — | [0015 the package is the master](../../docs/adr/0015-the-package-is-the-master.md), [11.3](../chino/playback.md#113-the-player-on-a-computer) |
| Settle titles whose chapters can't be read, or put back chapters a read replaced | admin | no | — | [0015 the package is the master](../../docs/adr/0015-the-package-is-the-master.md) |
| Measure the picture inside a title's frame, and of titles that lack it at a set pace | system | no | — | [11.11](../chino/playback.md#1111-the-picture), [0015 the package is the master](../../docs/adr/0015-the-package-is-the-master.md) |
| Encode a title's video to the master spec, copying a source that already meets it | system | built | built | [0015 the package is the master](../../docs/adr/0015-the-package-is-the-master.md), [0002 prepackaged playback](../../docs/adr/0002-prepackaged-playback.md), [11.9](../chino/playback.md#119-quality-names) |
| Package a title to play: segments, audio, subtitles, scrub thumbnails and checksums | system | built | built | [0002 prepackaged playback](../../docs/adr/0002-prepackaged-playback.md), [0015 the package is the master](../../docs/adr/0015-the-package-is-the-master.md), [README](../../docs/library/README.md) |
| Encode and package a title's extras on a chain of their own | system | no | built | [extras](../../docs/extending/extras.md) |
| Package a title now, or encode it again under the pipeline's current settings | admin | built | — | [0015 the package is the master](../../docs/adr/0015-the-package-is-the-master.md) |
| Make subtitles in the instance's languages where a title has none | system | no | no | [0014 subtitles in every language](../../docs/adr/0014-subtitles-in-every-language.md), [12.7](../chino/subtitles.md#127-the-subtitles-column), [18.1](../chino/words.md#181-the-word-list) |
| Attach a subtitle file to a title, and remove one it attached | addon | — | — | [0014 subtitles in every language](../../docs/adr/0014-subtitles-in-every-language.md) |
| Convert a title as it plays where its package doesn't fit the device or the connection | system | — | built | [0013 live rungs safety net](../../docs/adr/0013-live-rungs-safety-net.md), [11.13](../chino/playback.md#1113-when-the-quality-changes-by-itself) |
| Retry failed steps by themselves after a backoff, and take silent ones for failed | system | built | — | — |
| See which steps failed and why, and retry one or every one | admin | built | — | — |
| Follow what the pipeline does to each title, as it happens | admin | built | — | — |

- Find a title's intro, recap and credits: An outside database of intro times first, then black frames, silence, subtitle gaps, chapter names, and an episode's siblings
- Read a title's chapters from its original, and of titles that miss them at a set pace: Kept in the catalog, not the package; an original stays until they are read. The chapters tab lists them; progress API only
- Settle titles whose chapters can't be read, or put back chapters a read replaced: API only. Accepting an unreadable title lets its original go without its chapters
- Measure the picture inside a title's frame, and of titles that lack it at a set pace: From the original: the bars baked into the frame, for the players to fit. Not shown in the console
- Encode a title's video to the master spec, copying a source that already meets it: HEVC within the caps. The resource sets the encoder, the ladder and the segment length (spec.pipeline, features.gpu)
- Package a title to play: segments, audio, subtitles, scrub thumbnails and checksums: Every track as stereo AAC, quiet mixes lifted. 5.1, segment length, default language, HLS subtitles: spec.pipeline
- Encode and package a title's extras on a chain of their own: Transcode, then package: no intro or credits pass, no scrub thumbnails. Their ladder: spec.pipeline.extraLadder. Not in the console
- Package a title now, or encode it again under the pipeline's current settings: The current package plays until the new one is in place. Refused once the original is retired. No app calls chino-api's route
- Make subtitles in the instance's languages where a title has none: The subtitler, run by hand as a Job over a list of titles; no pipeline step. It also makes OCR copies, which ADR-0015 rules out
- Attach a subtitle file to a title, and remove one it attached: Kept as WebVTT beside the title's version, labelled by how it was made (AI, OCR); nothing is packaged again
- Convert a title as it plays where its package doesn't fit the device or the connection: By default chino-stream's own encoder; spec.liveWorker, mode on, sends it to the live worker. Rungs beside the package not built
- Retry failed steps by themselves after a backoff, and take silent ones for failed: Three runs in a row, waits of 1 min doubling to 1 h, then failed for an admin. The processing view shows the policy
- See which steps failed and why, and retry one or every one: Each step's titles by state; the failed ones with their last error, the latest first, 100 at most in the console
- Follow what the pipeline does to each title, as it happens: A feed of step changes, in plain words or technical, pushed live by the catalog's stream

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `find-intro-credits` | 11.C39 | `katalog-manager PUT /api/segments/items/{itemId}`, `katalog-manager DELETE /api/segments/items/{itemId}`, `katalog-manager GET /api/analyze/items/{id}` and 6 more | `intro-times-lookup`, `analyzer-error-wait`, `step-heartbeat`, `intro-search-window`, `credits-search-window`, `intro-sibling-agreement`, `segment-max-share`, `worker-poll-interval` |
| `read-chapters` | — | `katalog-manager PUT /api/chapters/items/{itemId}`, `katalog-manager GET /api/chapters/items/{itemId}`, `katalog-manager DELETE /api/chapters/items/{itemId}` and 2 more | `chapters-backfill`, `chapters-backfill-window`, `chapters-backfill-inflight`, `chapters-backfill-rate`, `chapters-backfill-records`, `chapters-backfill-lease`, `chapter-backfill-claims`, `chapter-read-timeout`, `chapter-read-failures` |
| `settle-chapter-reads` | — | `katalog-manager mutation acceptChapterReads`, `katalog-manager mutation revertChapterReplacement` | `chapter-read-failures` |
| `measure-picture-area` | — | `katalog-manager GET /api/picture/items/{id}`, `katalog-manager PUT /api/picture/items/{id}`, `katalog-manager GET /api/picture/extras/{id}` and 3 more | `picture-backfill`, `picture-backfill-window`, `picture-backfill-inflight`, `picture-backfill-rate`, `picture-backfill-lease`, `picture-on-arrival`, `picture-backfill-claims`, `picture-nice`, `picture-threads`, `picture-pass-deadline`, `picture-measure-again` |
| `transcode-title` | — | `katalog-manager GET /api/analyze/items/{id}`, `katalog-manager PUT /api/analyze/items/{id}/steps/{step}` | `video-caps`, `decoder`, `x264-preset`, `x264-crf`, `x265-preset`, `x265-crf`, `encode-stall-timeout`, `worker-poll-interval`, `rules-report-interval` |
| `package-title` | — | `katalog-manager POST /api/items/{id}/packaging-complete`, `katalog-manager GET /api/analyze/items/{id}`, `katalog-manager PUT /api/analyze/items/{id}/steps/{step}` and 1 more | `shown-languages`, `keep-single-language`, `surround-bitrate`, `old-package-grace`, `packager-error-wait`, `stereo-loudness`, `trickplay-interval`, `trickplay-size`, `superseded-grace`, `worker-poll-interval`, `rules-report-interval`, `audio-language-rules` |
| `package-extras` | — | `katalog-manager GET /api/analyze/extras/{id}`, `katalog-manager PUT /api/analyze/extras/{id}/steps/{step}`, `katalog-manager POST /api/extras/{id}/packaging-complete` | `extra-step-timeouts` |
| `process-again` | — | `katalog-manager mutation packageItem`, `katalog-manager mutation reencodeItem`, `katalog-manager POST /api/items/{id}/package` and 2 more | `superseded-grace`, `old-package-grace` |
| `make-subtitles` | 12.C3 | `katalog-manager POST /api/library/items/{itemId}/subtitles`, `katalog-manager GET /api/library/subtitles/languages` | `subtitle-languages`, `subtitler-languages`, `asr-threads`, `shown-languages`, `subtitle-fullness` |
| `attach-subtitle` | — | `katalog-manager GET /api/library/items/{itemId}/subtitles`, `katalog-manager POST /api/library/items/{itemId}/subtitles`, `katalog-manager DELETE /api/library/items/{itemId}/subtitles/{subtitleId}` and 1 more | `subtitle-languages` |
| `encode-while-playing` | — | `live-worker POST /v1/segment`, `live-worker POST /v1/init`, `live-worker POST /v1/subtitle` and 3 more | `live-queue`, `live-deadlines`, `live-attempts`, `live-watchdog`, `live-circuit-breaker`, `live-threads`, `live-tonemap`, `live-hw-frames`, `live-process-timeouts`, `live-audio-bitrate`, `live-diagnostics` |
| `heal-failed-steps` | — | `katalog-manager query retryPolicy` | `retry-attempts`, `retry-backoff`, `retry-backoff-max`, `retry-interval`, `step-timeouts`, `step-heartbeat` |
| `retry-steps` | — | `katalog-manager query processingOverview`, `katalog-manager mutation retryStep`, `katalog-manager mutation retryFailed` and 1 more | `failed-steps-shown` |
| `follow-activity` | — | `katalog-manager query activity`, `katalog-manager GET /api/manage/stream` | — |
<!-- end: areas -->
