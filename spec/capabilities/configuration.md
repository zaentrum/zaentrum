# Configuration

Every setting of the platform: what it sets, who changes it today and where, its
default, and a proposal for where it should be changed. The design system's rule
holds: [every setting has exactly one place where it is changed](https://nalet.github.io/design-system/patterns/settings-and-setup/).
A proposal is only that: the owner decides each one, as with a numbered change.

Every row comes from [settings.csv](./settings.csv). **Who** can change it today:
the operator (in the operator's resources or a service's environment), an admin
(in the portal or the catalog console), a person (in an app's settings), or
nobody (it is fixed in the code, and a release changes it). **Where** it is
changed: `resource`, `env`, `catalog` (the catalog's settings), `registry` (the
portal's registry), `app` or `code`. A **choice** is a value someone decides;
**wiring** is an address, a credential or a name the platform sets itself.

| Proposal | Means |
|---|---|
| keep | stays where it is |
| setting | becomes a setting an admin changes in the portal |
| shared | one value the server gives every app, instead of one in each |
| person | becomes a person's preference |
| constant | stays fixed in the code, on purpose |

## Where the settings are today

<!-- generated: summary -->
| Changed in | Settings | operator | admin | person | nobody | of them wiring |
|---|---|---|---|---|---|---|
| resource | 66 | 57 | 8 | 0 | 1 | 20 |
| env | 65 | 64 | 0 | 0 | 1 | 13 |
| catalog | 43 | 0 | 43 | 0 | 0 | 3 |
| registry | 5 | 0 | 5 | 0 | 0 | 0 |
| app | 8 | 0 | 0 | 8 | 0 | 0 |
| code | 126 | 0 | 0 | 0 | 126 | 8 |
<!-- end: summary -->

## The proposals

<!-- generated: proposals -->
| Proposal | Settings |
|---|---|
| keep | 204 |
| setting | 3 |
| shared | 24 |
| person | 1 |
| constant | 33 |
<!-- end: proposals -->

## Choices: chino

<!-- generated: choices-chino -->
| Setting | Who | Where | Default (values) | Proposal |
|---|---|---|---|---|
| The audio language titles start in `audio-language`, for `set-play-languages`, `choose-audio` | person | app | web English; phone English; androidtv English; samsung Original (Original, or a language) | keep |
| The subtitle language that comes on when the audio is in another `subtitle-language`, for `set-play-languages`, `choose-subtitles`, `switch-on-subtitles` | person | app | web English; phone off; androidtv off; samsung off (off, or one of the server's subtitle languages) | keep |
| Whether the player skips intros and recaps by itself `auto-skip-intros`, for `auto-skip-intro`, `set-binge-watching` | person | app | on in every app (on, off) | keep |
| Whether the player skips the credits by itself `auto-skip-credits`, for `auto-skip-intro`, `set-binge-watching` | person | app | phone on, not read; androidtv on; samsung on; the web has none (on, off) | constant |
| Whether the next episode starts by itself after up next `auto-play-next`, for `play-next-episode`, `set-binge-watching` | person | app | on in every app (on, off) | keep |
| Seconds the player counts down before it skips or starts the next episode `binge-countdown`, for `auto-skip-intro`, `play-next-episode`, `set-binge-watching` | person | app | web 3 s; phone 5 s, not offered; androidtv 5 s; samsung 10 s (1 s to 15 s) | person |
| The quality a title downloads in `download-quality`, for `download-titles` | person | app | phone Medium (720p) (the qualities the server names, each with what an hour takes) | keep |
| Whether downloads wait for Wi-Fi `download-wifi-only`, for `download-titles` | person | app | phone on (on, off) | keep |
| Whether the server offers downloads to the phone app `downloads-switch`, for `download-titles`, `manage-downloads`, `play-downloads-offline` | operator | env | on (on, off) | setting |
| How many warm-ups chino-stream runs at once for zap and the next episode `zap-warm-slots`, for `zap-through-titles`, `play-next-episode` | operator | env | 2 (a number) | keep |
| Whether a person with an age cap sees titles that have no age rating `unrated-for-capped`, for `limit-to-age-cap`, `cap-person-rating` | admin | catalog | — (on, off) | — |

- `audio-language`: 16.C18: Original first everywhere; Original plays the file's default track, as the catalog keeps no original language
- `subtitle-language`: Samsung offers eight fixed languages; 16.C18: the device's language where the server offers it, else off
- `auto-skip-intros`: the phone app's player doesn't read it
- `auto-skip-credits`: 11.C27 and 16.C4 take it away: the credits are never skipped by themselves
- `auto-play-next`: off, the web's up next card waits; the phone app then shows no up next at all
- `binge-countdown`: 16.C4: 3 s at first in every app
- `download-quality`: the Android app only
- `download-wifi-only`: the Android app only; downloads never wait for a charger
- `downloads-switch`: told to the apps as features.downloads; the operator's resource doesn't set it
- `zap-warm-slots`: a pool apart from the titles playing, so a warm-up never takes their slot; the operator's resource doesn't set it
<!-- end: choices-chino -->

## Choices: the portal

<!-- generated: choices-portal -->
| Setting | Who | Where | Default (values) | Proposal |
|---|---|---|---|---|
| How long an invite link holds `invite-lifetime`, for `invite-person`, `accept-invite` | operator | env | 7 days (168h) (duration) | keep |
| How long a notification is kept, read or not `notification-retention`, for `notify-person`, `read-portal-notifications`, `count-addon-notifications` | operator | env | 90 days (2160h) (duration) | keep |
| The parts the consoles never scale or restart `protected-parts`, for `scale-part`, `restart-part`, `see-platform-parts` | operator | env | postgres, kafka, valkey, keycloak (a list of part names) | keep |
| The parts the consoles run on: never scaled to zero, not restarted if that stops them `console-stack`, for `scale-part`, `restart-part`, `see-platform-parts` | operator | env | portal-api, zaentrum-portal, keycloak, postgres, katalog-manager-api (a list of part names) | keep |
| Which of the namespace's parts the consoles list, by label `parts-selector`, for `see-platform-parts`, `see-addon-state`, `run-declared-commands` | operator | env | every Deployment in the namespace (a label selector) | keep |
| The platform's own accounts the People page leaves out `hidden-accounts`, for `see-people` | operator | env | zaentrum-verify (a list of usernames) | keep |
| The realm role every person is given `user-role`, for `add-person`, `change-person` | operator | env | zaentrum-user (a realm role name) | keep |
| The realm role that marks a token as an addon's service account `addon-role`, for `notify-person`, `add-slot-buttons` | operator | env | zaentrum-addon (a realm role name) | keep |
| An app: its title, description, kind, addresses, icon, and whether it is on `app-entry`, for `register-app`, `open-app-from-tile`, `open-console-in-portal` | admin | registry | kind tool; on (key; title; description; kind product, manage, tool or external; base url; icon; health url; proxy url; on, off) | keep |
| A space: its title, its order and who sees it `space-entry`, for `arrange-spaces`, `limit-tile-audience`, `open-app-from-tile`, `switch-space` | admin | registry | audience everyone signed in (key; title; order; audience none (everyone), the admin role, or realm roles) | keep |
| A tile: its app, space, words, icon, target, order, badges, how it opens and who sees it `tile-entry`, for `place-tiles`, `limit-tile-audience`, `open-app-from-tile`, `search-tiles` | admin | registry | opens inline; audience everyone signed in; on (title; description; icon; target; order; badge and tone; status; open inline or newtab; external; audience; on, off) | keep |
| An extension's slot row: its slot, kind, label, icon, address, order, addon, on or off `slot-row`, for `edit-slot-rows`, `add-slot-buttons` | admin | registry | kind link; method POST; on (slot such as search.empty; kind link or action; url a path on this instance or its own origin; order) | keep |
| The entries a fresh registry starts with `registry-seed`, for `open-app-from-tile`, `register-app`, `arrange-spaces`, `place-tiles`, `watch-live-channels`, `play-music` | admin | registry | apps chino, tv, musig, catalog and catalog management with a tile each; spaces apps and manage (edited in the registry) | keep |
| Whether the checks run after every update `verification-switch`, for `verify-platform` | operator | resource | on (on, off) | keep |
| The chart an addon installs: its reference, version and digest `addon-chart`, for `install-addon-chart` | admin | resource | none (an oci:// or https:// reference; a version; a sha256 digest) | keep |
| The values an addon's chart is rendered with `addon-values`, for `install-addon-chart` | admin | resource | none (JSON; Secrets or ConfigMaps, by key or path) | keep |
| Whether an addon is only planned, with nothing applied `addon-plan-only`, for `install-addon-chart` | admin | resource | off (on, off) | keep |

- `invite-lifetime`: the People page says it in days
- `notification-retention`: older ones are swept at start and every hour
- `protected-parts`: the stateful parts; zae is refused the same way
- `console-stack`: nothing would be left to scale them back up from
- `parts-selector`: also what CLI discovery and the addons' part states look at
- `hidden-accounts`: the verification's test account
- `user-role`: an admin holds the admin role as well
- `addon-role`: the catalog reads its own, KATALOG_ADDON_ROLE
- `app-entry`: the proxy url, in-cluster only, lets it open inside the portal; the health url is stored, never read
- `space-entry`: core spaces, apps and manage, are never deleted
- `tile-entry`: an audience names at most 32 roles
- `slot-row`: an addon's service account writes only its own rows, keyed <addon>.<name>
- `registry-seed`: core: chino, apps, manage, never deleted; tv and musig off, badged soon; a deleted seed row comes back at the next start
- `verification-switch`: Also on each new zaentrum.io/verify-request
- `addon-chart`: A fetched archive that does not match the digest is refused
- `addon-values`: Applied in order: chart defaults, generated, values, valuesFrom, then the operator's zaentrum block
- `addon-plan-only`: The portal and zae add an addon suspended, show status.plan, then apply it
<!-- end: choices-portal -->

## Choices: the catalog and the pipeline

<!-- generated: choices-catalog -->
| Setting | Who | Where | Default (values) | Proposal |
|---|---|---|---|---|
| Whether a scan takes in files named or filed as a title's extras `extras-scan`, for `scan-library`, `manage-extras` | admin | catalog | off (on, off (true, on, yes, 1)) | keep |
| How the library lies on storage: legacy, or v2 with its record and arrivals `library-layout`, for `move-to-library`, `retire-originals`, `retire-list`, `replace-title-file`, `take-in-title` | admin | catalog | legacy (legacy, v2) | keep |
| Whether the retire job deletes originals once their package is verified `originals-policy`, for `retire-originals` | admin | catalog | keep (keep, delete-after-package) | keep |
| How long a version is complete before the original it was made from is retired `retire-delay`, for `retire-originals` | admin | catalog | 10 min (a duration) | keep |
| How many originals the retire job retires a minute at most `retire-rate`, for `retire-originals`, `retire-list`, `decide-superseded` | admin | catalog | 30 a minute (a number) | keep |
| How long a retired original stays in the trash, where a retirement can be undone `trash-grace`, for `retire-originals` | admin | catalog | 24 h (a duration; 0 deletes at once) | keep |
| How a version is checked before its original goes: every file's hash, or the chain `verify-mode`, for `retire-originals`, `verify-versions` | admin | catalog | full (full, chain) | keep |
| How recent a full verification must be for the chain alone to do `verify-max-age`, for `retire-originals`, `verify-versions` | admin | catalog | 30 d (a duration) | keep |
| Whether each new version is verified in full once, ahead of its retirement `verify-new`, for `verify-versions` | admin | catalog | on (on, off) | keep |
| How long a version a newer one replaced stays before it is removed `superseded-grace`, for `process-again`, `package-title`, `replace-title-file` | admin | catalog | 24 h (a duration) | keep |
| How long a replaced title's new master is complete before its old original is retired `superseded-delay`, for `decide-superseded`, `replace-title-file` | admin | catalog | 7 d (a duration; 0 none) | keep |
| What a replaced original may give up against its title's master before an admin decides `superseded-accept`, for `decide-superseded`, `replace-title-file` | admin | catalog | maxAudioChannels, surround, losslessAudio, objectAudio, stereo3d (names of the deletion gate, by commas or spaces; none) | keep |
| The addons that may give a title another file and have its old original go `replace-clients`, for `replace-title-file` | admin | catalog | none (OIDC client ids of addons' service accounts) | keep |
| How many queued titles the sweep sends to be encoded again a pass `reencode-rate`, for `reencode-queue` | admin | catalog | 4 a pass (a number; 0 sends none) | keep |
| How many queued titles may be sent and not done at once `reencode-inflight`, for `reencode-queue` | admin | catalog | 4 (a number) | keep |
| When the re-encode queue is sent `reencode-window`, for `reencode-queue` | admin | catalog | any time (HH:MM-HH:MM, the service's local time) | keep |
| What an admin's list of originals to retire may do `retire-list-mode`, for `retire-list` | admin | catalog | dry-run (off, dry-run, on) | keep |
| How long a dry run's word on its titles holds for a run of them `retire-list-max-age`, for `retire-list` | admin | catalog | 24 h (a duration, above 0) | keep |
| Whether the background pass checks the titles that need it `compliance-pass`, for `check-compliance` | admin | catalog | on (on, off) | keep |
| How many records the compliance pass reads at once `compliance-readers`, for `check-compliance` | admin | catalog | 4 (a number, 1 to 64) | keep |
| When every title is checked again each day `compliance-nightly`, for `check-compliance` | admin | catalog | 03:00 (HH:MM, the service's local time; off) | keep |
| Whether the catalog hands out titles that miss their chapters to be read `chapters-backfill`, for `read-chapters` | admin | catalog | off (on, off) | keep |
| When the chapter backfill hands titles out `chapters-backfill-window`, for `read-chapters` | admin | catalog | 22:00-17:00 UTC (HH:MM-HH:MM in UTC; empty, any time) | keep |
| How many titles the chapter backfill may have out and not reported at once `chapters-backfill-inflight`, for `read-chapters` | admin | catalog | 1 (a number, 1 or more) | keep |
| How many titles the chapter backfill hands out an hour `chapters-backfill-rate`, for `read-chapters` | admin | catalog | 120 an hour (a number; 0 none) | keep |
| How many source records the catalog reads chapters from an hour `chapters-backfill-records`, for `read-chapters` | admin | catalog | 3600 an hour (a number; 0 none, every title to the analyzer) | keep |
| How long a title handed out for its chapters is the worker's before it counts as lost `chapters-backfill-lease`, for `read-chapters` | admin | catalog | 30 min (a duration) | keep |
| Whether the catalog hands out titles without a picture area to be measured `picture-backfill`, for `measure-picture-area` | admin | catalog | off (on, off) | keep |
| When the picture backfill hands titles out `picture-backfill-window`, for `measure-picture-area` | admin | catalog | 22:00-17:00 UTC (HH:MM-HH:MM in UTC; empty, any time) | keep |
| How many titles the picture backfill may have out and not reported at once `picture-backfill-inflight`, for `measure-picture-area` | admin | catalog | 1 (a number, 1 or more) | keep |
| How many titles the picture backfill hands out an hour `picture-backfill-rate`, for `measure-picture-area` | admin | catalog | 240 an hour (a number; 0 none) | keep |
| How long a title handed out to be measured is the worker's before it counts as lost `picture-backfill-lease`, for `measure-picture-area` | admin | catalog | 6 h (a duration) | keep |
| The countries whose certifications rate a title by age, in the order asked `ratings-countries`, for `enrich-titles`, `edit-title` | admin | catalog | CH, DE, US (country codes, ISO 3166-1) | keep |
| The languages whose audio and subtitle tracks the apps list; others are packaged hidden `shown-languages`, for `package-title`, `check-compliance`, `make-subtitles` | admin | catalog | none: every track listed (a list of language codes) | keep |
| Whether a title whose every track is in a hidden language lists them all `keep-single-language`, for `package-title` | admin | catalog | on (on, off) | keep |
| The languages every title is to have a subtitle in `subtitle-languages`, for `make-subtitles`, `attach-subtitle` | admin | catalog | the shown languages (a list of language tags, as en, de, zh-Hans) | keep |
| Below what size a title's file is reported when its files are checked `small-file-threshold`, for `check-title-files` | admin | catalog | 5 MB (a number of MB) | — |
| Whether an analyzer asks the catalog's chapter backfill for titles `chapter-backfill-claims`, for `read-chapters` | operator | env | true (true, false) | keep |
| How long one read of an original's chapters may take `chapter-read-timeout`, for `read-chapters` | operator | env | 120 s (seconds, 5 to 3600) | keep |
| How long the analyzer waits after an error before it takes the next title `analyzer-error-wait`, for `find-intro-credits` | operator | env | 30 s (seconds) | keep |
| Whether a still from the video fills a title's missing poster or backdrop `keyframe-artwork`, for `enrich-titles` | operator | env | true (true, false) | keep |
| Whether the analyzer measures the picture area of each title it analyzes `picture-on-arrival`, for `measure-picture-area` | operator | env | true (true, false) | keep |
| Whether an analyzer asks the catalog's picture backfill for titles `picture-backfill-claims`, for `measure-picture-area` | operator | env | true (true, false) | keep |
| How far a picture measurement yields the CPU to other work, as a nice level `picture-nice`, for `measure-picture-area` | operator | env | 10 (a nice level) | keep |
| How long one title's picture measurement may run `picture-pass-deadline`, for `measure-picture-area` | operator | env | 6 h (seconds, 60 to 86400) | keep |
| How many decoder threads a picture measurement uses `picture-threads`, for `measure-picture-area` | operator | env | 2 (1 to 8) | keep |
| How often a long analysis says again that it still runs `step-heartbeat`, for `find-intro-credits`, `heal-failed-steps` | operator | env | 600 s (seconds) | keep |
| Whether the analyzer first asks an outside database of intro and credits times `intro-times-lookup`, for `find-intro-credits` | operator | env | true (true, false) | setting |
| The roles a title's cast and crew are read in from TMDB `credit-roles`, for `enrich-titles` | operator | env | actor, creator, director, writer, producer, composer, cinematographer, editor (a list of those roles) | keep |
| The language titles' texts are read from TMDB in `metadata-language`, for `enrich-titles` | operator | env | en-US (a language tag) | setting |
| How often titles and people are refreshed from TMDB's change lists `metadata-refresh`, for `enrich-titles` | operator | env | 24 h (a duration; 0 or off) | keep |
| How many runs in a row a failing step gets before it waits for an admin `retry-attempts`, for `heal-failed-steps` | operator | env | 3 (a number; 1 retries nothing by itself) | keep |
| The wait after a step's first failure, doubled after each failure that follows `retry-backoff`, for `heal-failed-steps` | operator | env | 1 min (a duration) | keep |
| The longest wait before a failed step is retried `retry-backoff-max`, for `heal-failed-steps` | operator | env | 1 h (a duration) | keep |
| How often the sweep sends due retries, reaps silent steps and sends the re-encode queue `retry-interval`, for `heal-failed-steps`, `reencode-queue` | operator | env | 30 s (a duration; 0 or off, no sweep) | keep |
| How long each step may go without a word from its worker before it counts as failed `step-timeouts`, for `heal-failed-steps`, `scan-library` | operator | env | scan, tmdb 15 min; analysis, package, takein 2 h; transcode 6 h (step=duration, by commas) | keep |
| How long the packager waits after an error before it takes the next title `packager-error-wait`, for `package-title` | operator | env | 60 s (seconds) | keep |
| How long a replaced package stays on disk for the sessions that began on it `old-package-grace`, for `package-title`, `process-again` | operator | env | 600 s (seconds) | keep |
| The bit rate of a 5.1 companion track `surround-bitrate`, for `package-title` | operator | env | 448k (a bit rate, as 448k) | keep |
| Where a source is decoded: on the GPU where that works, or always on the CPU `decoder`, for `transcode-title` | operator | env | auto (auto, cpu) | keep |
| The software H.264 encoder's preset, for rungs encoded without a GPU `x264-preset`, for `transcode-title` | operator | env | medium (an x264 preset) | keep |
| The software H.264 encoder's constant rate factor `x264-crf`, for `transcode-title` | operator | env | 23 (a number) | keep |
| The software HEVC encoder's preset, for encodes without a GPU `x265-preset`, for `transcode-title` | operator | env | medium (an x265 preset) | keep |
| The software HEVC encoder's constant rate factor `x265-crf`, for `transcode-title` | operator | env | 24 (a number) | keep |
| The master's video caps: Mbit/s by kind and height, and the largest movie file copied `video-caps`, for `transcode-title`, `check-compliance` | operator | env | movies 8 and 14 Mbit/s (1080p, 2160p); episodes 6 and 8; a movie file 15 GiB (numbers; 0 switches a rule off) | — |
| Whether the catalog sends the item events that start enrichment and the pipeline `catalog-events`, for `scan-library`, `enrich-titles` | operator | env | on wherever KAFKA_BROKERS is set (true, false) | keep |
| How many playhead jobs may wait for a slot, and how many idle slots a prefetch leaves `live-queue`, for `encode-while-playing` | operator | env | 16 a lane; 1 (numbers) | keep |
| A segment's deadline where a request names none, the longest it may ask, a subtitle's `live-deadlines`, for `encode-while-playing` | operator | env | 12 s; 120 s; 120 s (durations) | keep |
| How many workers a job is tried on, how long one attempt runs, when a slow one is doubled `live-attempts`, for `encode-while-playing` | operator | env | 3; 8 s; never (a number; durations) | keep |
| When a worker is given up on: no progress, no letting go of a job, or too much memory `live-watchdog`, for `encode-while-playing` | operator | env | 5 s; 3 s; no memory limit (durations; MB) | keep |
| How many failures of a source open its circuit, within what time, and for how long `live-circuit-breaker`, for `encode-while-playing` | operator | env | 3 within 1 min; open 30 s (a number; durations) | keep |
| The threads a job decodes, encodes and filters with, and a CPU job's threads `live-threads`, for `encode-while-playing` | operator | env | the libraries' own; 2 a CPU job (numbers) | keep |
| How HDR is tone-mapped to SDR on the GPU `live-tonemap`, for `encode-while-playing` | operator | env | auto (auto, interop, roundtrip, cpu) | keep |
| How many hardware frames a decoder holds beyond its own pool `live-hw-frames`, for `encode-while-playing` | operator | env | 8 (a number) | keep |
| How long running jobs may finish on shutdown, and a worker may take to start `live-process-timeouts`, for `encode-while-playing` | operator | env | 10 s; 60 s (durations) | keep |
| The languages the subtitler makes subtitles in when a run names none `subtitler-languages`, for `make-subtitles` | operator | env | en, de, zh-Hans (a list of language tags) | shared |
| How many CPU threads speech recognition uses where it runs on the CPU `asr-threads`, for `make-subtitles` | operator | env | 0, the library's own choice (a number) | keep |
| The live worker's diagnostics: its filter chains logged, the media libraries' log level, faults for tests `live-diagnostics`, for `encode-while-playing` | operator | env | off; error; none (on, off; a log level; a list of faults) | keep |
| The keys the catalog looks titles up with at the reference data services `metadata-keys`, for `set-metadata-key`, `enrich-titles` | admin | catalog | none (a key each) | keep |
| Which audio languages a package keeps, and whether a lone original-language track always stays `audio-language-rules`, for `check-compliance`, `package-title` | admin | catalog | every language; on (a list of language codes; on, off) | — |

- `extras-scan`: Typed into the settings table by hand; applies from the next scan
- `library-layout`: Switched once, by the migration; refused while a transcode waits for its packager
- `originals-policy`: A list of originals to retire leaves it as it is
- `trash-grace`: The space is freed only when it leaves the trash
- `superseded-delay`: So that a wrong file given in its place can be taken back; the trash's grace follows
- `superseded-accept`: The inventory's value column holds a parse slip; this is the code's default
- `replace-clients`: An addon not named is refused, whatever its role
- `reencode-window`: Local time, where the backfills' windows are UTC
- `retire-list-mode`: The inventory's value column holds a parse slip; dry-run is the code's default
- `compliance-pass`: Off, the report keeps what the last pass found
- `chapters-backfill-window`: Unset, never from 17:00 to 22:00 UTC; set empty, any time
- `picture-backfill-window`: Unset, never from 17:00 to 22:00 UTC; set empty, any time
- `ratings-countries`: The inventory's value column holds a parse slip; CH, DE, US is the code's default
- `shown-languages`: packager.language_whitelist: not in the inventory. Also the default of the languages to make subtitles in
- `keep-single-language`: packager.keep_original_if_single: not in the inventory
- `subtitle-languages`: subtitles.languages (ADR-0014): not in the inventory; any signed-in caller reads it
- `small-file-threshold`: validate.small_file_threshold_mb: not in the inventory
- `chapter-backfill-claims`: The catalog's chapters.backfill decides whether any are handed out
- `keyframe-artwork`: An episode gets a still of its own as its backdrop
- `picture-backfill-claims`: The catalog's picture.backfill decides whether any are handed out
- `picture-pass-deadline`: As the catalog's picture.backfill.lease
- `step-heartbeat`: Must stay under the catalog's step timeout, or the step is taken for failed
- `intro-times-lookup`: On by default: each title's reference id goes to an outside service. Its key is install's
- `credit-roles`: A refresh drops a title's credits in any other role
- `metadata-language`: One language for the whole catalog
- `retry-interval`: Off, nothing is retried by itself and the re-encode queue waits
- `step-timeouts`: A scan silent for longer is failed by the sweep
- `old-package-grace`: Keep it above the shared storage's attribute cache time
- `surround-bitrate`: Only where spec.pipeline.surroundAudio makes 5.1 companions
- `x265-preset`: Used where the transcoder has no GPU, as the operator renders it unless features.gpu
- `x265-crf`: ADR-0015 names CQ 23 on the GPU; a CPU encode runs at CRF 24
- `video-caps`: The heart of ADR-0015's master spec, yet no field of the resource; NVENC_MAXRATE_* override a height's cap for every kind
- `catalog-events`: Off, a scanned title is never enriched or processed
- `live-tonemap`: auto keeps the frames in GPU memory where it can, and falls back to the CPU
- `subtitler-languages`: A second list beside the catalog's subtitles.languages, which ADR-0014 makes the one setting
- `metadata-keys`: Kept secret: never shown again once set; the portal's setup checklist sets the first
<!-- end: choices-catalog -->

## Choices: the platform

<!-- generated: choices-platform -->
| Setting | Who | Where | Default (values) | Proposal |
|---|---|---|---|---|
| How many replicas each app service runs `replica-counts`, for `install-platform` | admin | resource | 1 each; packager 2 (a Deployment name and a count) | keep |
| Whether the platform ships its own identity provider or uses an external one `identity-mode`, for `choose-identity` | operator | resource | bundled (bundled, external) | keep |
| Whether the derived issuer and Keycloak's hostname use http or https `issuer-scheme`, for `choose-identity`, `provide-certificates` | operator | resource | http (http, https) | keep |
| The image of the bundled identity provider `keycloak-image`, for `choose-identity` | operator | resource | quay.io/keycloak/keycloak:26.0.7 (an image reference) | keep |
| Whether the bundled provider's admin console is on the public host `identity-console`, for `expose-identity-console` | operator | resource | off (on, off) | keep |
| Whether chino has a host of its own beside the path-routed one `chino-host`, for `set-public-host` | operator | resource | pathRouted: chino at /chino/ (pathRouted; subdomains and a host) | keep |
| Whether the platform renders a Kubernetes Ingress `ingress-switch`, for `set-public-host` | operator | resource | on (on, off) | keep |
| Whether the platform renders OpenShift Routes `routes-switch`, for `set-public-host`, `provide-certificates` | operator | resource | off (on, off) | keep |
| The size of the media library's claim `media-size`, for `configure-storage` | operator | resource | 50Gi (a quantity) | keep |
| The access mode of the media claim `media-access-mode`, for `configure-storage` | operator | resource | ReadWriteOnce (ReadWriteOnce, ReadWriteMany) | keep |
| Whether the chart makes the media claim, or a volume of yours backs it `media-claim-provision`, for `configure-storage` | operator | resource | on (on, off) | keep |
| The storage class of the platform's claims `storage-class`, for `configure-storage` | operator | resource | the cluster's default (a class name) | keep |
| The size of the bundled database's claim `database-volume-size`, for `configure-storage` | operator | resource | 10Gi (a quantity) | keep |
| The storage class of the bundled database's claim `database-volume-class`, for `configure-storage` | operator | resource | storage.className (a class name) | keep |
| Whether a database on a temporary volume is copied onto its claim `database-migrate`, for `configure-storage` | operator | resource | off (on, off) | keep |
| Whether the services use the bundled Postgres or an external one `database-mode`, for `choose-databases` | operator | resource | perApp (perApp, single, external) | — |
| Whether the platform uses its bundled broker or an external one `event-broker-mode`, for `configure-event-streaming` | operator | resource | bundled (bundled, external) | keep |
| Whether the bundled single-node broker runs `bundled-broker`, for `configure-event-streaming` | operator | resource | on (on, off) | keep |
| Whether the media pipeline runs `pipeline-switch`, for `enable-pipeline` | admin | resource | off (on, off) | keep |
| Where the transcoder encodes `encoder`, for `choose-encoder` | operator | resource | gpu (gpu, cpu) | keep |
| The renditions each title gets beside the source's `rendition-ladder`, for `configure-pipeline` | operator | resource | one rendition a title (rungs: source or a height, with a codec and a maxrate) | keep |
| The renditions a title's extras get `extras-ladder`, for `configure-pipeline` | operator | resource | 720p and 480p H.264 (rungs, as the ladder) | keep |
| The length of a playlist segment, and so the keyframe interval `segment-length`, for `configure-pipeline` | operator | resource | 6 s (1 to 30 s) | keep |
| Whether packages carry a 5.1 rendition beside the stereo one `surround-audio`, for `configure-pipeline` | operator | resource | off (off, eac3, ac3) | keep |
| Whether the master playlist names the WebVTT subtitles `playlist-subtitles`, for `configure-pipeline` | operator | resource | off (on, off) | keep |
| The order of languages that picks a package's default audio `default-audio-language`, for `configure-pipeline` | operator | resource | the catalog's language order (a list of language codes) | keep |
| Whether the live worker runs, and chino-stream is told where `live-worker-switch`, for `enable-live-worker` | operator | resource | off (on, off) | keep |
| How far chino-stream uses the live worker `live-worker-mode`, for `enable-live-worker` | operator | resource | off (off, shadow, on) | keep |
| How many encodes the live worker runs at once, on the GPU and the CPU `live-worker-slots`, for `enable-live-worker` | operator | resource | GPU 4; CPU 2 (0 to 32 each) | keep |
| Whether the live worker asks for an NVIDIA GPU `live-worker-gpu`, for `enable-live-worker` | operator | resource | on (on, off) | keep |
| The nodes the live worker runs on, and the taints it tolerates `live-worker-placement`, for `enable-live-worker` | operator | resource | the transcoder's GPU placement (node labels; tolerations) | keep |
| The live worker container's CPU, memory and GPU `live-worker-resources`, for `enable-live-worker` | operator | resource | GPU: 1 CPU, 2Gi to 4 CPUs, 8Gi and one GPU; CPU: 500m, 1Gi (resource requests and limits) | keep |
| Hardware encoding on the stream plane, as the resource names it `stream-gpu`, for `enable-live-worker` | nobody | resource | off (on, off) | — |
| Whether the bundled databases are backed up `backup-switch`, for `schedule-backups` | operator | resource | on where the database is on a claim (on, off) | keep |
| When a backup runs `backup-schedule`, for `schedule-backups` | operator | resource | @daily (a cron schedule) | keep |
| How many dumps are kept `backup-retention`, for `schedule-backups` | operator | resource | 7 (1 or more) | keep |
| The size of the backups' claim `backup-volume-size`, for `schedule-backups` | operator | resource | 5Gi (a quantity) | keep |
| The storage class of the backups' claim `backup-volume-class`, for `schedule-backups` | operator | resource | the bundled database's (a class name) | keep |
| The version every platform image runs `platform-version`, for `pin-version` | admin | resource | latest: follow the channel (latest or a tag) | keep |
| The release train the platform follows `release-channel`, for `choose-update-channel` | admin | resource | stable (stable, edge) | keep |
| Whether the channel's updates apply by themselves `update-mode`, for `choose-update-channel` | admin | resource | manual (manual, auto) | keep |
| Whether images are pinned to their digest, so a moving tag rolls `digest-pinning`, for `pin-version`, `choose-update-channel` | operator | env | on (on, off) | keep |
| Whether the platform's Secrets come from outside `external-secrets`, for `bring-own-secrets` | operator | resource | off: generated (on, off) | keep |

- `replica-counts`: The console's and zae's scale write it; stateful services are not scaled this way
- `identity-mode`: external renders no Keycloak; the broker mode of ADR-0007 is not built
- `issuer-scheme`: https whatever it says with spec.tls; over plain http only a localhost name can sign in
- `keycloak-image`: The realm, verification and account Jobs run it too
- `identity-console`: Off: a port-forward reaches it at localhost:8080/auth/admin/
- `chino-host`: subdomains is additive: the path-routed surfaces stay, and the portal's chino tile opens the new host
- `routes-switch`: Routes end TLS at the edge and carry the certificate inline
- `media-access-mode`: ReadWriteMany for storage that shares one volume across nodes
- `storage-class`: The database's and the backups' claims fall back to it
- `database-migrate`: Writes made during the copy are not carried over; the DatabasePersistent condition reports it
- `database-mode`: single renders exactly as perApp: no template reads it
- `bundled-broker`: Ignored with an external broker
- `pipeline-switch`: Admins switch it in the setup checklist and with zae setup pipeline
- `encoder`: cpu: what cannot pass through costs an x265 encode, hours a title
- `rendition-ladder`: Every rung is stored beside the library
- `surround-audio`: Left off until chino-stream keeps it from players that cannot decode it
- `playlist-subtitles`: Off: the apps draw the subtitle files themselves
- `live-worker-mode`: shadow asks for the same segments and drops them; a session keeps the pipeline it began on
- `live-worker-slots`: The pods sharing a GPU, the transcoder's included, stay within its encode-session limit
- `live-worker-gpu`: Off: video is encoded with libx264 on the CPU, slowly
- `stream-gpu`: Read by no template, so it changes nothing; the setup checklist reports it as the GPU asked for
- `backup-schedule`: In the time zone of the cluster's controller manager
- `platform-version`: zae platform update --version pins any tag; the console pins only the update on offer
- `update-mode`: A channel on latest, edge, is followed in both
- `external-secrets`: Off: zaentrum-db, -stream-signing, -keycloak, -keycloak-admin, -demo-user and the rest are made once, never rotated
<!-- end: choices-platform -->

## Fixed in the code

The values a person notices that each app or service fixes in its code. Where
apps fix the same thing, the default names each app's value.

<!-- generated: fixed -->
| Setting | Default in each app (values) | Proposal |
|---|---|---|
| How many titles take turns in the hero `hero-pool-size`, for `start-featured-title` | web 8; phone 8; androidtv 8; samsung 8 (a number of titles) | shared |
| Which titles the hero picks from `hero-candidates`, for `start-featured-title` | web, phone: the 40 newest movies and 40 newest shows with a trailer; androidtv, samsung: unwatched movies rated 7 or more (a number of newest titles, or a rating) | shared |
| How long the hero shows each title `hero-rotation`, for `start-featured-title` | web 20 s; phone 12 s; androidtv 12 s; samsung 12 s (duration) | shared |
| How long an app keeps the hero's titles before it picks them again `hero-refresh`, for `start-featured-title` | web 1 h, per browser session; phone 1 h, per server and account; androidtv while home is open; samsung until home opens again (duration) | shared |
| Play an online trailer by itself behind the hero `hero-trailer-autoplay`, for `play-hero-trailer` | web off (on, off) | keep |
| How many titles a row on home holds `home-row-size`, for `see-new-titles`, `see-top-rated` | web 20; phone 20; androidtv 20; samsung 20 (a number of titles) | shared |
| The rating a movie needs to be in top rated `top-rated-floor`, for `see-top-rated` | web 8; phone 8; androidtv 8; samsung 8 (a rating from 0 to 10) | shared |
| How many genre rows Samsung's home adds, and how many titles each holds `genre-rows`, for `see-genre-rows` | samsung 3 rows of 20 (a number of rows; a number of titles) | — |
| How far into a title a place must be to count as begun `resume-floor`, for `continue-watching`, `see-time-left`, `resume-title` | server 30 s; web 30 s; phone 30 s; androidtv 30 s; samsung 30 s (duration) | shared |
| When a played title counts as watched `watched-rule`, for `count-as-watched`, `mark-watched`, `continue-watching`, `resume-title` | web, phone, androidtv, samsung: in the credits or past 95 %; server: a place saved in the last 5 % or 2 min (a share of the length; a duration) | shared |
| How many titles the grid of movies or shows loads at a time `browse-page-size`, for `browse-library` | web 48; phone 48; androidtv 48; samsung 60 (a number of titles) | shared |
| How many actors a title's page shows before full cast `cast-preview`, for `see-cast-and-crew` | web 6; phone 6; androidtv every actor; samsung every actor (a number of actors) | constant |
| How many actors, and how many of each other role, the catalog gives a title `credits-cap`, for `see-cast-and-crew` | 20 actors; 10 of every other role (a number of people) | keep |
| How many titles more like this holds `similar-size`, for `see-similar-titles` | web 12; phone 12; androidtv 12; samsung 12 (a number of titles) | shared |
| How many of a person's titles their page shows `person-titles-limit`, for `see-person` | web 100; phone 100; androidtv 100, the server's default; samsung 100 (a number of titles) | shared |
| How many titles a list's row shows on the watchlist `watchlist-shelf-size`, for `see-lists` | web 12; phone 12; androidtv 12; samsung 12 (a number of titles) | shared |
| How long a list's name may be `list-name-length`, for `create-list`, `create-list-from-title`, `rename-list` | 1 to 60 bytes (a number of characters) | keep |
| How many lists an account may have `lists-per-account`, for `create-list`, `create-list-from-title` | 50, the Watchlist among them (a number of lists) | keep |
| How many titles the watch history shows `watch-history-size`, for `see-watch-history` | web 60; phone 60; androidtv 60; samsung none (a number of titles) | shared |
| How many titles and people a search shows `search-result-limits`, for `search-titles`, `search-people` | web 60 titles, 12 people, 8 titles under the field; phone 40, 12; androidtv 60, 12; samsung 60, 12; server 30, 12 when not asked, at most 100, 50 (a number of titles; a number of people) | shared |
| How long after the last key a search runs `search-debounce`, for `search-as-you-type` | web 0.2 s, from the second letter; phone 0.25 s; androidtv 0.25 s; samsung 0.25 s (duration) | constant |
| How close a misspelled word must be to still match `search-spelling-tolerance`, for `search-titles`, `search-people` | a word of 4 letters or more, at a similarity of 0.5 (a number of letters; a share) | keep |
| How long an app waits for a server or its sign-in to answer the check `server-check-timeout`, for `connect-server`, `sign-in`, `sign-in-with-code` | phone 4 s before sign in; androidtv 6 s to connect, 15 s to read; samsung 6 s, and 8 s for its sign-in (duration) | — |
| How close to its end a stopped title starts again from the start `restart-near-end`, for `resume-title` | web 60 s; phone 60 s; androidtv 60 s; samsung 60 s (a duration) | shared |
| How often the place is saved while a title plays `progress-save-interval`, for `resume-title`, `control-cast` | web 10 s; phone 10 s; androidtv 10 s; samsung 10 s; a cast 10 s (a duration) | constant |
| When up next comes in an episode without known credits `up-next-trigger`, for `play-next-episode` | web never; phone the later of 95 % and 20 s before the end; androidtv at the end; samsung at the end (a share and a duration) | constant |
| How recently another episode must have played for one to count as in a row `binge-window`, for `auto-skip-intro` | web 6 h; phone none; androidtv none, every episode; samsung none, every episode (a duration) | constant |
| How long an episode must have played before the next starts by itself `next-episode-guard`, for `play-next-episode` | web none; phone none; androidtv a picture and 10 s; samsung none (a duration) | constant |
| When the player warms the next episode's stream `next-episode-warm`, for `play-next-episode` | web from the credits; phone 30 s before the credits or the end; androidtv the same; samsung never (a duration) | constant |
| How long the player's controls stay after the last touch, key or move `controls-hide`, for `play-title` | web 3 s, 8 s paused; phone 4 s, 8 s; androidtv 4 s, 8 s; samsung 3.5 s, never while paused (a duration) | constant |
| How far back or forward a key or a button skips `seek-step`, for `seek-title`, `use-player-keys`, `control-cast` | web 10 s; phone 10 s; androidtv 10 s; samsung 10 s, fast forward and rewind 30 s; a cast 10 s (a duration) | constant |
| How long a start may show no picture before the player gives up `startup-deadline`, for `explain-playback-failure` | web 20 s; phone 20 s on iOS, none on Android; androidtv none; samsung none (a duration) | constant |
| When the player tries a stalled stream again, and steps it down `stall-recovery`, for `recover-faltering-stream` | web the picture still 8 s, 3 tries in place; phone 3 tries in place; androidtv 3 tries, a watchdog at 12 s; samsung its engine's (durations and counts) | constant |
| How long a stream token lasts `stream-token-lifetime`, for `play-title`, `recover-faltering-stream`, `download-titles`, `cast-title` | 6 h (a duration) | constant |
| How many reports an app files by itself in a session `auto-report-limit`, for `report-playback-failure`, `report-crash` | web 3; phone 3; androidtv 3; samsung 3 (a count) | constant |
| How many reports one person may file in a while `report-rate-limit`, for `report-bug`, `report-playback-bug`, `report-playback-failure`, `report-crash` | 5 in 10 minutes (a count in a duration) | — |
| How long a report of the same failure is added to the earlier one `report-dedup-window`, for `report-bug`, `report-playback-bug`, `report-playback-failure`, `report-crash` | 14 days (a duration) | — |
| How many titles the server keeps ready for zap, and how often each is handed out `zap-ready-pool`, for `zap-through-titles`, `pick-zap-titles` | 8 titles, each handed out twice, those warmed in the last 10 min last; the web asks for 8 and waits 1.5 s (counts and durations) | keep |
| How many titles of each kind zap takes from the library `zap-list-size`, for `pick-zap-titles` | web 30; phone 30; androidtv 30; samsung 30 (a count) | shared |
| How many of the person's watched titles zap checks its cards against `zap-watched-check`, for `pick-zap-titles` | web 200; phone 200; androidtv 200; samsung 200 (a count) | shared |
| Where in a title a zap scene may start `zap-scene-window`, for `pick-zap-scene` | server, web, phone, androidtv, samsung: 10 % to 80 %, not in the first 60 s or the last 90 s; 40 % without a random pick (two shares and two durations) | shared |
| Where the first card of a session starts `zap-first-card`, for `pick-zap-scene` | web 35 %; phone 35 %, the same title each session, warmed 1.2 s after start; androidtv the same; samsung random (a share) | — |
| How long a card must play to count for its title, or be passed to count against `zap-dwell`, for `learn-from-zapping` | web 8 s, 2 s; phone 8 s, 2 s; androidtv 8 s, 2 s; samsung learns nothing (two durations) | shared |
| How many cards zap picks at random, whatever it learned `zap-exploration`, for `learn-from-zapping` | web 60 of 100; phone 60; androidtv 60; samsung every card, shuffled (a share) | shared |
| How much each thing a person does counts for a title's kind, genres and cast `zap-weights`, for `learn-from-zapping` | web, phone, androidtv: save 2, watch 1.5, to the end 1, 8 s 0.5, 2 to 8 s −0.3, under 2 s −1; earlier weights × 0.92 each time (weights) | shared |
| How long the TV's info stays after zap opens, or up or right is pressed `zap-info-linger`, for `zap-through-titles` | androidtv 60 s; samsung 60 s (a duration) | constant |
| How many titles that can't be played zap skips in a row `zap-dead-channels`, for `skip-unplayable-channel` | androidtv 6; samsung 6 (a count) | constant |
| How often the apps ask the server for notifications `notice-poll`, for `see-notifications` | web 60 s; phone 60 s; androidtv 60 s, never within 10 s of the last; samsung 60 s (a duration) | constant |
| How long a download plays without a check with the server `download-check-age`, for `play-downloads-offline`, `remove-unavailable-downloads` | phone 30 days (a duration) | — |
| How far apart two answers must be before a download no longer allowed is deleted `download-removal-gap`, for `remove-unavailable-downloads` | phone 1 h; 24 h where an answer leaves out every title (a duration) | constant |
| How often the phone asks the server again while it can't be reached `server-recheck`, for `play-downloads-offline` | phone 15 s, while the app is in front (a duration) | constant |
| The text subtitles' size, place and width on the picture `subtitle-look`, for `keep-subtitles-readable` | web, phone, androidtv: 5.33 % of the picture's height, 8 % above its foot, 80 % wide; samsung one size, 5rem above the foot (shares of the picture) | constant |
| How far one press moves the subtitles, and how far at most `subtitle-timing-step`, for `time-subtitles` | web 0.25 s a press, up to 10 s either way (durations) | constant |
| How much a fill may crop for the next title to start filled too `fill-carry-limit`, for `fit-picture` | web 10 %; phone 10 % (a share) | constant |
| The longest title a notification may have `notification-title-length`, for `notify-person` | 80 characters (characters) | keep |
| The longest text a notification may have `notification-body-length`, for `notify-person` | 280 characters (characters) | keep |
| How many notifications a person keeps, the newest `notifications-kept`, for `read-portal-notifications`, `notify-person`, `count-addon-notifications` | 100 (a count) | keep |
| How fast notifications may be posted `notification-post-rate`, for `notify-person` | an addon 100 at once, then 1 a second; to oneself 10, then 1 every 6 s (a count and a duration) | keep |
| How often the portal's bell asks for notifications `portal-bell-refresh`, for `read-portal-notifications` | portal 60 s (duration) | keep |
| The ages a rating cap may be `rating-cap-range`, for `cap-person-rating` | portal-api 0 to 21; web 0 to 21 (a whole age) | keep |
| How long a username may be `username-length`, for `add-person` | 3 to 64 characters (characters) | keep |
| The longest name a person's account may have `person-name-length`, for `add-person`, `change-person` | 100 characters (characters) | keep |
| The most accounts the People page reads `people-list-limit`, for `see-people` | 2000 (a count) | keep |
| How long a closed invite is kept, for the People page to say what became of it `invite-record-kept`, for `see-people`, `invite-person` | 90 days (duration) | keep |
| The most replicas the consoles scale a part to `replica-limit`, for `scale-part` | portal 20; portal-api 20 (a count) | keep |
| How often the operator console reads the parts again `operator-console-refresh`, for `see-platform-parts`, `see-addon-state` | portal parts 5 s; addons 30 s (duration) | keep |
| How many of a container's last lines a read shows `log-tail-lines`, for `read-logs` | portal 500, a choice of 200 to 5000; zae 500, --tail up to 5000 (lines) | keep |
| How often a live log reads again `log-live-refresh`, for `read-logs` | portal 4 s; zae --follow 2 s (duration) | keep |
| How many of the latest events the tap keeps `event-tail-size`, for `watch-events` | portal-api 500; zae 500 (a count) | shared |
| How often the events console reads again `event-live-refresh`, for `watch-events` | portal 4 s (duration) | keep |
| The longest event payload the tap keeps `event-payload-cap`, for `watch-events` | 4000 characters (characters) | keep |
| How many rows a page of the database console holds `db-page-size`, for `browse-database` | 100, at most 500 (rows) | keep |
| How much of a cell the database console shows `db-cell-length`, for `browse-database` | 400 characters (characters) | keep |
| How long a read of the database console may take `db-query-timeout`, for `browse-database` | 6 s (duration) | keep |
| How long a scan runs before the checklist takes it for stopped `stale-scan-age`, for `set-up-platform` | portal 30 min; zae 30 min (duration) | shared |
| The longest name a chart addon may have `addon-name-length`, for `install-addon-chart` | portal-api 40; zae 40 (characters) | keep |
| The longest values path a chart addon's secret input may have `values-path-length`, for `install-addon-chart`, `upgrade-addon` | portal-api 250; zae 250 (characters) | keep |
| How soon a chart addon the operator made ready is registered `chart-registration-pace`, for `install-addon-chart` | every 15 s; sooner when asked, at most every 5 s (duration) | keep |
| How long an app inside the portal may take to answer `app-proxy-timeout`, for `open-console-in-portal`, `check-addon-setup` | 60 s (duration) | keep |
| How long the CLI's discovery document is kept `discovery-cache-age`, for `run-declared-commands` | 30 s (duration) | keep |
| How long zae waits for an addon's plan, and with --wait for it to be ready `addon-wait-timeout`, for `install-addon-chart`, `upgrade-addon` | zae 5 min (duration) | keep |
| How long zae waits for a rollout or a verification `platform-wait-timeout`, for `update-platform`, `pin-version`, `scale-part`, `restart-part`, `verify-platform` | zae 10 min (duration) | keep |
| How long a support bundle may take `bundle-timeout`, for `download-support-bundle` | zae waits 2 min; portal-api assembles in at most 60 s (duration) | keep |
| The bit rate of the stereo audio the live worker encodes, where a request names none `live-audio-bitrate`, for `encode-while-playing` | 160 kbit/s (a bit rate) | — |
| How many files of a package a verification reads at once `verify-reads`, for `verify-versions`, `retire-originals` | 4 (a number) | constant |
| How long a version that did not verify waits before it is verified again `verify-retry`, for `verify-versions` | 6 h, doubled each time, 7 d at most (durations) | — |
| How many titles one list of originals to retire may name `retire-list-size`, for `retire-list` | 10000 (a number) | — |
| How often a run tries a title an error stops, and how many such titles stop it `retire-list-tries`, for `retire-list` | 3 tries; 5 titles in a row (numbers) | — |
| How long a removed extra's package stays before it is deleted `removed-extra-grace`, for `manage-extras` | 24 h (a duration) | — |
| How long an extra waits for a worker to start it, and may run without a word `extra-step-timeouts`, for `package-extras` | 24 h to start; 2 h silent (durations) | — |
| How many failed reads in a row make a title's chapters unreadable, for an admin `chapter-read-failures`, for `read-chapters`, `settle-chapter-reads` | 5, the waits 1 h doubling to 24 h (a number; durations) | — |
| How long until a title whose picture area came out unknown is measured again `picture-measure-again`, for `measure-picture-area` | 30 d; never twice within 24 h (durations) | — |
| How far above its cap a package's video may measure and still be within it `compliance-tolerance`, for `check-compliance` | 3 % (a share) | constant |
| How often the transcoder and the packager report the rules they run with `rules-report-interval`, for `check-compliance`, `transcode-title`, `package-title` | transcoder 600 s; packager 600 s (seconds) | — |
| How many titles a page of the rules report holds `compliance-report-page`, for `check-compliance` | console 100; the API 500 at most (a number) | — |
| How many passed-over files a scan's report names; the log names every one `scan-report-limit`, for `scan-library` | 1000 (a number) | — |
| How many episodes one file may cover `episodes-per-file`, for `scan-library`, `hand-over-file` | katalog-manager 10; packager 10 (a number) | constant |
| How many cast and crew a title keeps from TMDB, by role `credit-caps`, for `enrich-titles` | a movie's cast 12; a show's cast and directors 20; any other role 10 (numbers) | — |
| How long saving a TMDB key waits for TMDB's check before it stores it unchecked `key-check-timeout`, for `set-metadata-key` | 4 s (a duration) | — |
| How many failed steps the console's processing view lists `failed-steps-shown`, for `retry-steps` | 100 (a number) | — |
| How many episodes the console's episodes tab reads at a time `series-episodes-page`, for `browse-catalog` | 200 (a number) | — |
| How long a worker may spend on one title before the event bus takes it for gone `worker-poll-interval`, for `find-intro-credits`, `transcode-title`, `package-title` | analyzer 24 h; transcoder 24 h; packager 24 h (a duration) | — |
| How long an encode may make no progress before it is stopped `encode-stall-timeout`, for `transcode-title` | 600 s (seconds) | — |
| The loudness a quiet stereo track is lifted to `stereo-loudness`, for `package-title` | -20 LUFS, lifted 14 dB at most (a loudness) | — |
| How far apart the scrub thumbnails are `trickplay-interval`, for `package-title` | 10 s (seconds) | — |
| The size of a scrub thumbnail, and how many a sheet holds `trickplay-size`, for `package-title` | 320 x 180; 10 x 10 a sheet (pixels; numbers) | — |
| Where an episode's intro is looked for, and how late it may start `intro-search-window`, for `find-intro-credits` | the first 600 s, starting within 180 s (seconds) | — |
| How far from the end credits are looked for, by each detector `credits-search-window`, for `find-intro-credits` | fingerprints 300 s; black frames the last 15 %; subtitles 15 min (seconds; a share) | — |
| How many other episodes must share an intro for it to count `intro-sibling-agreement`, for `find-intro-credits` | 2, of up to 6 compared (numbers) | — |
| The longest an intro or a recap may be, as a share of the runtime `segment-max-share`, for `find-intro-credits` | 25 % (a share) | — |
| How many titles a page of holdings holds `holdings-page-size`, for `read-library-holdings` | 200; 1000 at most (a number) | — |
| When a subtitle track counts as full dialogue rather than signs and songs `subtitle-fullness`, for `make-subtitles` | 1 cue a minute, and 30 % of the fullest track's cues (numbers) | — |
| The in-cluster addresses the services call each other at `service-addresses`, for `install-platform` | http://<service> in the namespace (URLs) | constant |
| The port each service listens on `listen-ports`, for `install-platform` | :8080 (a port) | constant |
| The paths the web consoles are served under and call their APIs at `web-app-paths`, for `install-platform` | /katalog/, /katalog-manage/; /api/manage/query; /api/portal (paths) | constant |
| Where the images keep the tools the services run `tool-paths`, for `install-platform` | ffmpeg and ffprobe on the path; the image's OCR data (paths) | constant |
| The version a worker records on what it makes `image-version-stamp`, for `install-platform` | baked in by the image build (a commit or a release tag) | constant |
| How the portal's People page reaches the realm's accounts `people-admin-client`, for `choose-identity` | keycloak, realm zaentrum, client zaentrum-people (a URL, a realm, a client) | keep |
| Whether each service checks sign-in tokens, and their audience `token-checks`, for `choose-identity` | tokens checked; audience not required by katalog-manager and portal-api (on, off) | constant |
| The theme of the bundled provider's sign-in pages `login-theme`, for `choose-identity` | zaentrum (a theme name) | — |
| The realm's password policy the invite page states `password-policy-hint`, for `choose-identity` | the realm import's (a Keycloak password policy) | keep |
| Where the services find the library, the packages and their caches `media-paths`, for `configure-storage` | /var/lib/katalog: media/ and packages/ (paths) | constant |
| The hardware encoder's preset and quality `nvenc-quality`, for `choose-encoder`, `enable-live-worker` | p5, CQ 23 (a preset; a quality, 0 to 51) | — |
| Whether the analyzer runs speech recognition `speech-recognition`, for `configure-pipeline` | off (on, off) | — |
| Whether the catalog looks chapter names up in an outside database `chapters-lookup`, for `configure-pipeline` | off (on, off) | — |
| How chino-stream encodes itself while the live worker does not `stream-encoder`, for `enable-live-worker` | CPU, preset veryfast, 4 encodes at once (on, off; an x264 preset; a count) | — |

- `hero-pool-size`: the same in every app, fixed in each
- `hero-candidates`: 4.C1 and 4.C2 make it one rule; the web's 40 and the TVs' 7 are written inline
- `hero-rotation`: 4.C3 sets 20 s; the phone's 12 s is a default parameter, not in the inventory
- `hero-refresh`: 4.C2 keeps them an hour in every app; the phone's hour is written inline
- `hero-trailer-autoplay`: it would embed a player from an outside site; no app plays one
- `home-row-size`: continue watching and next up hold all they have; web and phone write 20 inline
- `top-rated-floor`: written inline in each app's request, not in the inventory
- `genre-rows`: 4.C12 recommends leaving the genre rows out
- `resume-floor`: below it a title is in no continue watching and plays from its start; web and Android TV write 30 inline
- `watched-rule`: 11.C39: the server's rule alone, from the credits; only Samsung names its 95 %, the others write it inline
- `browse-page-size`: the phone's 48 is a default parameter; 5.C15 drops Samsung's load more button
- `cast-preview`: 6.8.2: six, and a cast at most two longer shows whole; a TV has a row of cards instead
- `credits-cap`: full cast never shows more than 20
- `similar-size`: each app asks for 12, written inline, not in the inventory
- `person-titles-limit`: 7.6.4 says every title of theirs; written inline in chino-api and the apps
- `watchlist-shelf-size`: the 12 added last; see all opens the rest
- `list-name-length`: 8.C17 counts characters instead of bytes
- `watch-history-size`: web and phone write 60 inline
- `search-result-limits`: 9.C4: 60 titles and 12 people in every app; the web writes its numbers inline
- `search-debounce`: 9.6.1: a quarter of a second, from the first letter; the others write it inline
- `server-check-timeout`: Android TV's are written inline in its check
- `restart-near-end`: each app's own beside the server's finished rule; 11.C39: the apps show what the server says
- `progress-save-interval`: 11.C40: also on pause and on leaving, and only a place that has played
- `up-next-trigger`: 11.C23: the later of 20 s before the end and 95 % in every app
- `binge-window`: 11.C20: from the second episode in a row, in every app
- `next-episode-guard`: 11.C25: so a title that fails at once can't run through a season
- `next-episode-warm`: 11.C26: 30 s before the credits, or before the end without them
- `controls-hide`: 11.C14: 3 s playing and 8 s paused in every app
- `seek-step`: 11.C13: 10 s for fast forward and rewind on Samsung too
- `startup-deadline`: counted only while the player is on the screen; 11.C44
- `stall-recovery`: 11.13.1: still for 8 s; three waits in 30 s step down, at most once every 2 minutes
- `stream-token-lifetime`: lets a stream outlive the sign-in's renewals; after a longer pause the player asks for a new one
- `auto-report-limit`: 11.17: at most 3 a session and one for each kind of failure
- `report-rate-limit`: past it the phone app says to try again in a few minutes
- `report-dedup-window`: the person is told the number of the report it was added to
- `zap-ready-pool`: the same for everyone; only the web asks for it
- `zap-list-size`: the best-rated movies, the newest shows and, on the web and Samsung, the newest episodes
- `zap-watched-check`: a title watched before the latest 200 can come back in zap
- `zap-scene-window`: fixed alike in five places; a title of 2½ minutes or less has no such stretch
- `zap-first-card`: 10.C12 recommends a random first card, its scene too
- `zap-weights`: the table of 10.6.1: genres count in full, the first five cast half, the kind 30 %; samsung learns nothing
- `zap-dead-channels`: then zap stays until the person moves on
- `notice-poll`: and as an app starts, comes back to the front, and opens the list
- `download-check-age`: DownloadBook.CHECK_EVERY_MS, not in the inventory; past it play is dimmed until the server can be reached
- `download-removal-gap`: DownloadBook.GONE_CONFIRM_MS and EMPTY_ANSWER_CONFIRM_MS, not in the inventory
- `subtitle-look`: the device's caption preferences win where an app reads them
- `fill-carry-limit`: of the picture's width and of its height
- `notification-body-length`: line breaks allowed; plain text
- `notifications-kept`: older ones go when a new one comes
- `notification-post-rate`: per replica of portal-api; past it 429 with Retry-After
- `portal-bell-refresh`: also when the page is shown again and when the bell opens
- `rating-cap-range`: the realm's user profile holds the same bounds
- `username-length`: letters a to z, digits, and . _ - between them; it cannot change later
- `replica-limit`: portal-api refuses more whoever asks
- `event-tail-size`: zae holds its own copy of the tap's size to check --limit
- `stale-scan-age`: past it both offer to start another scan
- `addon-name-length`: it is the release name and the registry key
- `values-path-length`: the resource's limit on valuesFrom targetPath
- `app-proxy-timeout`: event streams are exempt
- `discovery-cache-age`: an addon added or removed clears it
- `addon-wait-timeout`: --timeout changes it for one command
- `platform-wait-timeout`: --timeout changes it for one command
- `live-audio-bitrate`: The package's own stereo is AAC at 192 kbit/s
- `verify-reads`: On a network share the wait for each file, not its bytes, is the cost
- `extra-step-timeouts`: Not among the steps' KATALOG_STEP_TIMEOUTS
- `compliance-tolerance`: The packager measures from the segments, whose boxes add a little
- `episodes-per-file`: The library format's own limit, fixed in two services
- `credit-caps`: A movie keeps every director, a show every creator
- `failed-steps-shown`: The API gives at most 200 a page
- `stereo-loudness`: Louder tracks, 5.1 companions and copied tracks are left as they are
- `service-addresses`: Fixed in the operator's chart; not set there: ANALYZER_BASE_URL (an old alias), PORTAL_KATALOG_MANAGER_URL, the subtitler's
- `listen-ports`: Fixed in the operator's chart; PORT is portal-api's alias, not set
- `web-app-paths`: VITE_* fixed at build; BASE_URL rewritten at start from the chart's BASE_PATH. VITE_MANAGE_API_BASE: the older admin app
- `tool-paths`: Set by the images, not the chart
- `image-version-stamp`: Else the installed package's version
- `people-admin-client`: Set by the chart with bundled identity only; PORTAL_PEOPLE_MANAGE_URL, for an external provider, it never sets
- `token-checks`: The chart fixes OIDC_ENABLED and AUTH_ENABLED true; the others keep their defaults
- `login-theme`: identity.loginTheme is read by no template: the realm import always names the zaentrum theme
- `password-policy-hint`: Bundled identity only; Keycloak enforces the realm's own
- `media-paths`: The chart mounts the media claim at /var/lib/katalog; portal-api reads katalog-manager's roots to show them
- `nvenc-quality`: Fixed in the operator's chart for both
- `speech-recognition`: Fixed off in the operator's chart; the model's settings are left to the pipeline The model, device and precision are read; no pass uses them
- `chapters-lookup`: Fixed off in the operator's chart; the database is at CHAPTERSDB_BASE_URL
- `stream-encoder`: Fixed in the operator's chart: chino-stream never encodes on a GPU
<!-- end: fixed -->

## Wiring

<!-- generated: wiring -->
| Wiring | Where | Is |
|---|---|---|
| The TMDB key titles are looked up with `metadata-key` | catalog |  |
| The key of a second metadata source, asked where TMDB has nothing `fallback-metadata-key` | catalog |  |
| The project and personal keys of an artwork source, asked where TMDB has no image `artwork-source-keys` | catalog |  |
| The part-of label every workload of the platform carries `part-of-label` | resource | `Zaentrum.spec.partOf` |
| Pull secrets added to every workload, for a private registry `image-pull-secrets` | resource | `Zaentrum.spec.imagePullSecrets` |
| The in-cluster addresses the services call each other at `service-addresses` | code | `ANALYZER_BASE_URL`, `ARTWORK_BASE_URL`, `KATALOG_BASE_URL`, `KATALOG_MANAGER_URL` and 12 more |
| The port each service listens on `listen-ports` | code | `ADDR`, `LISTEN_ADDR`, `KATALOG_API_ADDR`, `KATALOG_INGEST_ADDR` and 3 more |
| The paths the web consoles are served under and call their APIs at `web-app-paths` | code | `BASE_URL`, `VITE_KATALOG_GQL`, `VITE_KATALOG_STREAM`, `VITE_PORTAL_API` and 2 more |
| The cluster's API server, which portal-api calls and the chart fetcher refuses to dial `kubernetes-api` | env | `KUBERNETES_SERVICE_HOST`, `KUBERNETES_SERVICE_PORT`, `KUBERNETES_SERVICE_HOST` |
| The namespace and the workloads the portal's consoles act on `portal-cluster-scope` | env | `PORTAL_NAMESPACE` |
| The operator's API group, version and plurals portal-api reads and writes `operator-api-names` | env | `PORTAL_OPERATOR_GROUP`, `PORTAL_OPERATOR_VERSION`, `PORTAL_OPERATOR_PLURAL`, `PORTAL_ADDON_PLURAL` |
| The keys of the outside metadata services the catalog and the analyzer call `outside-service-keys` | env | `TMDB_API_KEY`, `FANART_API_KEY`, `FANART_CLIENT_KEY`, `OMDB_API_KEY` and 1 more |
| Where chino files the problems people report: the address, token, project and type of report `bug-report-target` | env | `OPENPROJECT_URL`, `OPENPROJECT_TOKEN`, `OPENPROJECT_PROJECT_ID`, `OPENPROJECT_BUG_TYPE_ID` |
| Where the images keep the tools the services run `tool-paths` | code | `FFMPEG_BIN`, `FFPROBE_BIN`, `TESSDATA_PREFIX` |
| The version a worker records on what it makes `image-version-stamp` | code | `IMAGE_VERSION`, `IMAGE_VERSION` |
| The issuer every service takes sign-in tokens from `oidc-issuer` | resource | `Zaentrum.spec.identity.issuer`, `OIDC_ISSUER`, `OIDC_ISSUER`, `KATALOG_API_OIDC_ISSUER` and 5 more |
| The token audience every service accepts `token-audience` | resource | `Zaentrum.spec.identity.audience`, `OIDC_AUDIENCE`, `OIDC_AUDIENCE`, `KATALOG_API_OIDC_AUDIENCE` and 2 more |
| The client ids the web, TV, phone, portal and CLI sign in through `sign-in-clients` | resource | `Zaentrum.spec.identity.clientId`, `Zaentrum.spec.identity.tvClientId`, `Zaentrum.spec.identity.mobileClientId`, `OIDC_CLIENT_ID_WEB` and 5 more |
| The client credentials the workers sign in with `service-clients` | env | `KEYCLOAK_KATALOG_CLIENT_ID`, `KATALOG_SERVICE_CLIENTS`, `OIDC_CLIENT_ID`, `OIDC_CLIENT_SECRET` and 8 more |
| How the portal's People page reaches the realm's accounts `people-admin-client` | code | `PORTAL_PEOPLE_KEYCLOAK_URL`, `PORTAL_PEOPLE_REALM`, `PORTAL_PEOPLE_CLIENT_ID`, `PORTAL_PEOPLE_CLIENT_SECRET` and 1 more |
| The realm roles, and the token claim, services take admins, addons and people from `role-names` | env | `ADMIN_ROLE`, `KATALOG_ADMIN_ROLE`, `KATALOG_ADDON_ROLE`, `KATALOG_ROLES_CLAIM` and 1 more |
| The address the token-checking pods resolve the public host to `issuer-host-alias` | resource | `Zaentrum.spec.network.issuerHostAliasIP` |
| The realm's password policy the invite page states `password-policy-hint` | code | `PORTAL_PASSWORD_POLICY` |
| The public host people reach the platform at `public-host` | resource | `Zaentrum.spec.hostname`, `PUBLIC_BASE_URL` |
| The Secret holding the platform's certificate and key `tls-secret` | resource | `Zaentrum.spec.tls.secretName` |
| The cert-manager issuer that signs the certificate into that Secret `tls-issuer` | resource | `Zaentrum.spec.tls.issuerRef.name`, `Zaentrum.spec.tls.issuerRef.kind`, `Zaentrum.spec.tls.issuerRef.group` |
| An existing claim to keep the bundled database on `database-claim` | resource | `Zaentrum.spec.storage.postgres.claimName` |
| A claim you made for the bundled broker to keep its topics on `broker-claim` | resource | `Zaentrum.spec.storage.kafkaPvc` |
| The node the bundled broker is pinned to `broker-node` | resource | `Zaentrum.spec.storage.kafkaNode` |
| Where the services find the library, the packages and their caches `media-paths` | code | `MEDIA_ROOT`, `HLS_CACHE_DIR`, `NFS_ROOT`, `SCANNER_NFS_ROOT` and 10 more |
| The database host, names, TLS mode and credentials each service connects with `database-connection` | resource | `Zaentrum.spec.databases.chino`, `Zaentrum.spec.databases.katalog`, `Zaentrum.spec.databases.keycloak`, `Zaentrum.spec.databases.portal` and 18 more |
| The brokers every service connects to `kafka-brokers` | resource | `Zaentrum.spec.eventStreaming.bootstrap`, `KAFKA_BROKERS`, `KAFKA_BROKERS`, `KAFKA_BROKERS` and 4 more |
| The client certificate the services reach an external broker with `kafka-tls` | resource | `Zaentrum.spec.eventStreaming.certSecret`, `KAFKA_CERT_DIR`, `KAFKA_CERT_DIR`, `KAFKA_CERT_DIR` and 7 more |
| The topic prefix, and the topics and step the pipeline hands titles on with `event-topics` | resource | `Zaentrum.spec.eventStreaming.topicPrefix`, `KAFKA_TOPIC_PREFIX`, `KAFKA_TOPIC_PREFIX`, `KAFKA_TOPIC_PREFIX` and 9 more |
| The consumer-group prefix that keeps instances on one broker apart `consumer-groups` | resource | `Zaentrum.spec.eventStreaming.groupPrefix`, `KAFKA_GROUP_ID`, `KAFKA_GROUP_ID`, `EXTRAS_GROUP_ID` and 3 more |
| An existing claim to keep the dumps on, one from an earlier install `backup-claim` | resource | `Zaentrum.spec.backup.claimName` |
| Where the operator reads which version each channel serves `releases-url` | env | `RELEASES_URL` |
| The test account the checks sign in with, kept off the People page `verification-account` | env |  |
| The VPN's SOCKS5 proxy every addon is handed `vpn-proxy` | resource | `Zaentrum.spec.vpn.proxy` |
| The only networks a pod on the VPN may connect to directly `vpn-cluster-networks` | resource | `Zaentrum.spec.vpn.clusterCIDRs` |
| The shared secrets services prove themselves to each other with `service-tokens` | env | `STREAM_SIGNING_KEY`, `ACCOUNT_DELETION_TOKEN`, `STREAM_SIGNING_KEY`, `LIVE_WORKER_TOKEN` and 3 more |
| Where the live worker listens, the media it reads, its worker processes' program, sockets and GPU `live-worker-wiring` | env | `LIVE_WORKER_LISTEN`, `LIVE_WORKER_MEDIA_ROOTS`, `LIVE_WORKER_SLOT_BIN`, `LIVE_WORKER_SOCKET_DIR` and 1 more |
| Accounts chino-api's admin routes accept by their subject, besides the admin role `admin-subjects` | env | `ADMIN_SUBJECTS` |
| The folder the CLI keeps its sign-ins in `cli-config-folder` | env | `XDG_CONFIG_HOME` |
<!-- end: wiring -->
