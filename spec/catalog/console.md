# The catalog console

This page specifies the catalog console: the screens with which an admin looks
after the library. It says what each view shows, what an admin does there and
in which words, and what the catalog's server, katalog-manager, has to offer
for it. What a library, a folder, a scan, a collection and an export are, and
the rules they follow, are set out in [the library](./library.md); this page
specifies their screens.

The section As built describes what the platform does today. The sections
after it are the target, and the section Changes lists every difference
between the two as a numbered change. Only a change the owner has approved is
built, one change at a time; anything no change names stays as it is built.

## Purpose

The catalog console is where the people who run a household's zaentrum look
after its library: find a title, correct what the catalog got wrong, give a
title its pictures, subtitles and extras, see what became of its files, put
titles into collections, say which folders the library is made of and when
they are scanned, and set how the catalog works. It is for admins alone.

It serves the goal [Keep the library](../goals/README.md#keep-the-library),
and of [what people expect of it](../capabilities/expectations.md#keep-the-library):
correcting a title's match, details and artwork by hand; trailers and extras;
a title that lacks subtitles getting them; collections everyone sees; several
libraries; and new files that appear by themselves.

## As built

This section says what the console does as of 15 November 2026, as the code of
`katalog-manager-ui` and of `katalog-manager` has it at their main branches.

### One image, two apps

The repository `katalog-manager-ui` builds one web app, and the platform's
chart runs it twice. Where it is mounted says which app it is:

| App | Mounted at | Its heading, and the line under it | Its views |
|---|---|---|---|
| the catalog | `/katalog/` | “katalog”, “browse the catalog” | the list of titles; from it a title's page and a person's page. No navigation |
| catalog management | `/katalog-manage/` | “catalog management”, “scan, processing & settings” | a row of five tabs: **scan**, **activity**, **Processing**, **rules**, **settings**. It opens on scan |

- **Each is a page of its own.** The portal's home page opens each from a tile
  of its own, “Catalog” and “Catalog Management”. Neither is hosted inside the
  portal's shell, as an addon's console is
  ([hosted consoles](../../docs/extending/console.md)): each draws its own top
  bar, with the product's lockup, which leads back to the portal, “/ katalog”
  or “/ catalog management” after it, the account's name in a blue badge, and
  **sign out**. The window's title is “katalog · zaentrum” in both.
- **It signs in as the portal does**, with the same client, so it usually
  opens signed in. Someone without the admin role sees “This console is for
  administrators” in place of the app; katalog-manager refuses such a person
  every operation, whatever the console shows.
- **It talks to katalog-manager alone**: GraphQL at `/api/manage/query`; a
  stream of notes at `/api/manage/stream`, which tells an open view to read
  again; a title's poster and a person's portrait at `/api/manage/artwork/…`;
  and the rules report as CSV at `/api/manage/compliance.csv`. The platform
  publishes nothing else of katalog-manager: its other routes answer inside
  the cluster only.
- **The design system 0.1.0**, a copy of the package kept in the console's
  code. That version has a simple table, tabs, a dialog, fields, a select, a
  checkbox, a switch, a badge and a loader. It has no data table, filter bar,
  filter tabs, toolbar, action menu, multi-select, status, banner, toast or
  empty state; the rules view draws its own.

### The catalog: the list of titles

| Feature | As built |
|---|---|
| What is listed | the newest 200 items that match, of every type; nothing leads to the rest |
| The count | “200 items”: the rows shown, not the titles that match |
| The order | newest first; no column sorts |
| Filters | **search**, “title…”, which finds the words in a title; **type**: all, movie, series, episode, album; **genre**; **year**; **has original**: all, yes, no. None is part of the address: a reload or a link starts without them |
| Columns | the poster; **title**, a link to the title's page; **type**; **year**; **has original**, “yes”, “no”, or “—” for a series, a season or an album; **original** and **package**, their sizes on disk; **packaged**, “ready” or “—”; **status**, the pipeline's word for the title |
| Staying current | the list reads again by itself when the catalog changes |
| After a delete | a notice above the list says what was deleted and what the delete could not do, until it is dismissed |
| Loading | a loader and “loading catalog…”, at once |
| Empty | “no items match.” |
| Couldn't load | “error:” and the error as it came, in red; nothing offers to try again |

### The catalog: a title's page

The page has a head and a row of tabs. The head shows the poster, the title,
and badges: the type, the year, the rating after a star, “packaged”, “manual”
with a lock on a title that is locked, and the pipeline's status with its
steps done, “complete (9/9)”. Under them stand the tagline and these buttons;
what a button did is said in one line of the server's own words under them.

| Button | Does |
|---|---|
| **enrich** | asks enrichment for the title again |
| **identify** | a dialog with a title and a “tmdb id”: enrichment searches again with the corrected title, or takes the id. It takes the best match itself; the admin sees none of the matches |
| **edit** | the dialog “edit metadata”: title, year, tagline and description. Saving locks the whole title: enrichment then leaves its title, sort title, year, description, tagline, rating, runtime and credits, and still adds genres and replaces its pictures; **unlock** lets it change them again |
| **delete** | removes the title from the catalog, a series with its episodes; its files and its package leave the disk only when ticked, and then the title has to be typed |
| **package** | has the title packaged |
| **Re-encode** | a movie, an episode or a series: encodes it again with today's settings, after a question |
| **validate** | checks the title's files and says what it found |

| Tab | Shows |
|---|---|
| **overview** | the description, the runtime, the genres, the tags and the reference ids; nothing is changed here |
| **Episodes**, a series | its seasons and episodes as a tree, each episode with its state |
| **Steps** | the pipeline's steps of the title, each with its attempts, its error and **Retry** |
| **assets** | the title's files: kind, path, codec, resolution, size in MB, audio |
| **Tracks**, a movie or an episode | the audio and subtitle tracks of its source; **Set Language** sets the language a track plays as |
| **segments** | intro, recap and credits, as the analyzer marked them |
| **chapters** | the title's chapters |
| **trailers** | the title's links to online videos: title, site, **open**, and “local” or “linked” |
| **cast** | the title's credits: role, name, job, character, order, and a series' episodes; a name opens the person's page |
| **diagnostics** | the path and size of the source, and notes |

Loading shows a loader and “loading item…”; a title that is not there, “item
not found.”; a failure, “error:” and the error as it came.

A person's page shows what the catalog keeps of a person, under **overview**,
and every title that credits them, under **credits**. Nothing is changed
there.

### Catalog management

| View | As built |
|---|---|
| **scan** | **trigger scan** starts a scan of the one folder the catalog scans, the `media` folder of the platform's media volume. Under it the last 25 scans: **source**, **status**, **started**, **files**, **inserted**, **updated**. A scan's error, and the files it passed over, are not shown. “loading jobs…”, “no scan jobs yet.” |
| **activity** | the last 100 changes of the pipeline's steps, as a list in plain words (“friendly”) or as a table (“technical”); it reads again by itself |
| **Processing** | every step with how many titles are in each of its states; the failed steps with their last error; **Retry** and **Retry All Failed** |
| **rules** | the report of the titles that break a rule of the transcoder or the packager: a line on the last check, a summary by rule, a filter bar with a search, the kind and the rules, the count “230 of 279”, **download CSV**, a table whose headers sort it on the server, 100 rows at a time with **show more**, a row's details under it, rows ticked and processed again together, toasts and banners. It says why it couldn't load, by cause, with **try again** and **details** |
| **settings** | first **api keys**: the four keys of the reference data services, write-only, each “set” or “not set”, with **set** and **clear**. Under it a table of every setting someone created: **key**, **value**, **type**, **description**, with **edit** and **del**; **new setting** takes a key typed by hand, a value, a type (string, list_csv, bool, int, float) and a description. A setting the catalog reads that nobody created is not listed: the console names no setting but the four keys |

### What katalog-manager offers, and what the console uses of it

| For | katalog-manager offers | The console uses |
|---|---|---|
| The list | `items`: the newest first, filtered by type, genre, year, the title's words and whether it has an original; at most 200 in one answer, from an offset; no count of all that match and no other order. `searchItems` counts its matches and answers only a title's id, type, name, year and rating | 200, once |
| A title's texts | `updateItem`: title, sort title, year, tagline, description, and the lock; it cannot empty a field. `setItemGenres`, `setItemTags`. `setMinAgeOverride`: an age from 0 to 21 years that wins over the age the title's certification means. `createItem`. One lock, `metadataLocked`, keeps a title's texts, its rating, its runtime and its credits from enrichment, and neither its genres nor its pictures; nothing says where a field's value comes from; genres set by hand are added to at the next refresh. The catalog keeps no original title | title, year, tagline, description and the lock |
| A match | `identify`: a corrected title, or a TMDB id. It searches with the title's own year and takes the best match itself | **identify** |
| Pictures | one poster and one backdrop for a title: the match's, else a frame the analyzer took from the file; an episode without one is served its parent's. The one route that takes a picture is the analyzer's, inside the cluster. No other choice is kept, and no logo | the poster |
| Extras | `Item.extras`, each with its kind, its state and its last error; `addExtra`, which takes the path of a file that already lies on the storage the platform mounts; `removeExtra`; `packageExtra`; `packageExtras` | nothing |
| Subtitles | `Item.subtitles`. Routes that list a title's subtitles with how each came to be, attach one from its text, and remove one attached: inside the cluster only, for an admin, the platform's service account and an addon, and only for a title that has a version in the library | nothing |
| Originals and versions | `Item.library`: whether the title's originals are held; its versions, each with its state and when and how far it was verified; its originals, each with its state, when and by whom it was deleted, what its package doesn't carry of it, and why a deletion didn't go through. `holdOriginal`. A verification that fails is kept by the running service alone and said in its log. With the library's layout `legacy`, the default, no version and no original is recorded | nothing |
| Scans | `triggerScan`; `scanJobs`, at most 200, the newest first; each scan with its error and its report: the first 1,000 files it passed over, each `unsupported` or `not-linked`, with a reason. A scan counts the files it saw, the titles it made and those it touched; it keeps no list of them, and nothing says what started it | the last 25, without their error or report |
| Settings | `settings` lists the rows that exist; `createSetting`, `updateSetting` and `deleteSetting` take any key; `setSecretSetting` and `clearSecretSetting`. Nothing lists the settings there are, their values or their defaults. The catalog and the packager read 43 keys | the four keys by name, every other row as it is |
| Libraries, collections, an export | nothing | nothing |

A scan makes a title of every video file it takes in, named after the file:
dots and underscores as spaces, the year taken out. So a file enrichment could
not match is a title already, listed under its file's name; what it lacks is
its match.

## The two apps and their views

The console stays two apps, as the portal's home page has them
([the home page](../portal/home.md), changes H.C7 and H.C8): **catalog**, to
look through every title and its files, and **catalog admin**, for the
library's folders, its scans, its processing, its rules and its settings.
Each has a row of the design system's tabs under its heading, and every view
has an address of its own under the app's address.

| App | View | Address | Is |
|---|---|---|---|
| catalog | **titles** | the app's own | the list of today, as the section Titles sets it out |
| catalog | **collections** | `collections` | new |
| catalog admin | **scans** | `scans`; `scan` leads to it | today's scan, as the section Scans sets it out |
| catalog admin | **activity** | `activity` | as built |
| catalog admin | **processing** | `processing` | as built, its tab's name in lowercase |
| catalog admin | **rules** | `rules` | as built |
| catalog admin | **libraries** | `libraries` | new |
| catalog admin | **settings** | `settings` | the form of the section Settings |

- **The order** is the table's. In catalog admin the views of daily work come
  first and the two an admin sets up once, libraries and settings, last, as
  the design system's
  [app navigation](https://nalet.github.io/design-system/patterns/app-navigation/)
  orders an app's views. catalog opens on titles, catalog admin on scans.
- **The names.** The catalog app's heading is “catalog”, with “Every title and
  its files” under it; catalog admin's is “catalog admin”, with “Scans,
  processing and rules” under it: the words of each app's tile on the home
  page. The top bar says “/ catalog” and “/ catalog admin”.
- **The window's title** names the view, the app and the product, “titles ·
  catalog · zaentrum”, “scans · catalog admin · zaentrum”; on a page about one
  thing, that thing in place of the view: “Big Buck Bunny · catalog ·
  zaentrum”.
- **A page about one thing** has its own address under its view's: a title
  `item/` and its id, as today; a person `person/` and their id, as today; a
  collection `collections/` and its id; a library `libraries/` and its id; a
  scan `scans/` and its id. Its first line is a quiet button that leads back
  to its view and is named after it; on a title or a person opened from
  another title it leads back to that title and is named after it, as today.
- **From one app into the other** a link is an ordinary link, as the rules
  view links a title's page today: a title named in catalog admin opens in
  catalog, a library named in catalog opens in catalog admin.
- **Signing in keeps the address.** An address opened by someone who is
  signed out is the address they see once they have signed in, so a link to a
  view works for whoever follows it. Today signing in ends on the app's first
  view.
- **The top bar** stays as built, with its two names changed.

## Lists

Every list an admin works through is a table, built the same way in every
view. The rules view is built so already, by hand; the lists of this chapter
take the design system's parts.

1. **The parts, from the top**: the view's heading; the design system's
   [filter bar](https://nalet.github.io/design-system/components/filter-bar/),
   with the search first, then the filters, the count and **clear all**; a
   toolbar with the view's actions, the one main action emphasized; and the
   design system's data table.
2. **50 rows at a time.** The table shows the first 50 rows that match. Under
   it stand the count of rows shown, “50 of 312”, and **show 50 more**, the
   data table's own control, which reads what is left near the end, “show 12
   more”, and goes once every row is shown. There are no page numbers.
3. **The count** in the filter bar is of everything that matches, as the
   server counts it, never of the rows shown: “2,644” while nothing filters,
   “312 of 2,644” while something does.
4. **A header that sorts, sorts the whole list**, on the server: the first
   press in the column's first direction, the next the other way, one column
   at a time. A change of the sort or of a filter shows the first 50 rows
   again.
5. **The address holds the view.** The search's words, every filter that is
   set and the sort are query parameters of the address, as each view's
   section names them; a value that is the default is left out. So a reload,
   the browser's back and a link bring the same list. A change replaces the
   address in place and adds no step to the browser's history. How many rows
   are shown is not in the address.
6. **Values stand in columns.** A number stands to the right, in figures of
   one width. A size is written as the rules view writes sizes, “1.4 GB”. A
   time is the design system's date cell: the date, and how long ago. Nothing
   is “—”. A kind is a badge. A state is the design system's status, one in a
   row, with why in a line under it; a sentence stands nowhere else in a row.
7. **download CSV**, a quiet button in the toolbar of the titles and of a
   scan's page, saves every row the filters match, in the table's order, as
   the server writes it.
8. **The list stays current.** It reads again when katalog-manager's stream
   says the catalog changed, as the list of titles does today; the rows shown
   and the admin's place stay.
9. **On a narrow screen** the filter bar folds behind **filters**, and the
   data table moves columns under the row's name, as the design system has
   both. A column marked “first” in a view's table moves when the table is
   720 px wide or less, one marked “second” at 480 px or less; a column
   without a mark, or marked “never”, stays.

## Titles

The view **titles** lists every item of the catalog.

| Column | Shows | Sorts | Folds |
|---|---|---|---|
| (no name) | the poster, small | | first |
| **title** | the title, a link to its page; the row's name | A first, by the sort title | never |
| **type** | movie, series, episode, season, album or track, a badge | | never |
| **year** | the year | newest first | second |
| **library** | the name of the library the title belongs to | | second |
| **match** | “matched”, “not matched” or “by hand” for a movie and a series; an episode shows its series'; “—” for anything else | | second |
| **has original** | “yes”, “no” or “—”, as today | | first |
| **original** | the size of its originals | largest first | first |
| **package** | the size of its package | largest first | first |
| **packaged** | “ready” or “—”, as today | | first |
| **status** | the pipeline's word for the title, as today | | never |
| **added** | when the catalog first listed it | newest first; the order the view opens in | first |

| Filter | Values | In the address |
|---|---|---|
| the search, “search titles” | words; a title matches when its title, its sort title or its original title holds them | `q` |
| **type** | all, movie, series, episode, album | `type` |
| **genre** | all, then the catalog's genres | `genre` |
| **year** | a year; empty for any | `year` |
| **library** | all, then the libraries by name | `library`, the library's id |
| **match** | all, matched, not matched, by hand | `match`: `matched`, `not-matched`, `by-hand` |
| **has original** | all, yes, no | `original`: `yes`, `no` |
| **file** | all, gone: the titles whose file the last full scan of their library did not find | `file`: `gone` |
| the sort | a column that sorts, and its direction | `sort`: `added`, `title`, `year`, `original`, `package`; `dir`: `asc`, `desc` |

The toolbar holds **download CSV**. A row has no menu: its title opens its
page.

## A title's page

The page keeps its head. Three things in it change: **identify** is named
**match by hand** and shows the matches (section Match by hand and describe by
hand); **edit**, its dialog and the badge “manual” go, because the fields are
changed on the tab details; and the tabs are these, each named in lowercase:

| Tab | For | Is |
|---|---|---|
| **details** | every type | today's overview, as the section details sets it out |
| **episodes** | a series | as built |
| **artwork** | every type | new |
| **files** | every type | today's assets, with what the library holds of the title |
| **subtitles** | a movie, an episode | new |
| **extras** | a movie, a series | new |
| **trailers** | every type | as built: the links to online videos |
| **cast** | every type | as built |
| **chapters** | every type | as built |
| **tracks** | a movie, an episode | as built |
| **segments** | every type | as built |
| **steps** | every type | as built |
| **diagnostics** | every type | as built |

The page opens on details. The tab is part of the address, as `tab` and the
tab's name, `item/` the id `?tab=files`, so a link opens a title on one of its
tabs. A tab that counts what it holds keeps its count, “trailers (2)”.

### details

The tab is a form, built as the design system's
[forms](https://nalet.github.io/design-system/patterns/forms-and-settings/)
are: a label, a hint and an error for each field, and at its foot **cancel**,
**save changes** and, while a value differs from the saved one, “unsaved
changes”.

| Field | Control | Rule |
|---|---|---|
| Title | input | 1 to 255 characters |
| Sort title | input | 255 characters at most; the hint “How the title sorts in lists.” |
| Original title | input | 255 characters at most |
| Year | input for a number | a year from 1888 to 2100, or empty |
| Tagline | input | |
| Description | text area of six lines | |
| Genres | multi-select of the catalog's genres; under it the input “New genres”, for genres the catalog doesn't have yet, separated by commas | 20 genres at most, each of 1 to 80 characters |
| Tags | input, the tags separated by commas | |
| Minimum age (years) | input for a number | a whole number from 0 to 21, or empty |

- **Each field says where its value comes from**, in a tag beside its label:
  “by hand”, “files” (the files beside the title), “enrichment” or “file name”
  (the scan's reading of the file's name). An empty field has no tag.
- **A field changed and saved is kept by hand**: that field alone. No other
  field is locked with it, and enrichment, a new match and a scan leave it as
  the admin set it. A field emptied and saved stays empty.
- **use the catalog's value**, a quiet button beside a field that is kept by
  hand, gives the field back: once saved, the field has the value the files
  beside the title or enrichment give, in [the library](./library.md)'s
  order, and its tag says which. Until it is saved the field is closed and
  reads “The catalog's value after saving”.
- **The age rating.** A line over the field says what enrichment found:
  “Rated 12 in DE, which means from 12 years.”, for an episode “Rated as its
  series: from 12 years.”, or “No rating found in CH, DE, US.”, with the
  countries the catalog asks. The field is the age an admin gives the title;
  it wins over that rating, and a series' over its episodes'. People with an
  age limit see a title only when their limit is at least its age.
- **Under the form**, as today's overview has them and not changed here: the
  runtime, the reference ids, and two more: the library, a link to its page,
  with **move** (section Libraries), and when the title was added.
- **Saving** sends the fields that changed. The toast says “Details saved”; a
  save with nothing changed says “No changes to save”. A field that breaks
  its rule shows how to fix it, and the focus goes to the first such field. A
  save that fails leaves the fields as typed, with a banner over the form.
- **A title that is not matched** has a banner over the form: “This title is
  not matched.”, with **match by hand** and **describe by hand**.

### Match by hand and describe by hand

A movie or a series that enrichment could not match is corrected in one of two
ways. Both are offered in the banner of the tab details and in the menu of a
file's row on a scan's page; **match by hand** is also the button in the head
of a title's page that identify is today, for a title that has a match too. An
episode is matched through its series: on an episode the two lead to its
series' page.

**match by hand** is a dialog.

1. **Title** and **Year**, filled with the title's own, and **search**.
2. **The matches**, at most ten, the best first: for each its poster, its
   title and year, “Big Buck Bunny (2008)”, its original title where it is
   another, the start of its description, and “TMDB 10378”. One is chosen by
   pressing it.
3. **TMDB id**, a field for the id itself, with the hint “Use it when the
   search doesn't find the title.” An id typed wins over a match chosen.
4. A sentence says what a match does: “The match's genres, trailers and
   pictures replace this title's. What is kept by hand, or comes from the
   files beside the title, stays.”, and for a series, “The series' episodes
   are matched again too.”
5. **cancel**, and **match**, the emphasized button, which matches the title
   to the match chosen or the id typed. The dialog closes, the toast says
   “Matched to Big Buck Bunny (2008)”, and the page shows the title as it is
   now.

**describe by hand** opens the tab details with the focus in Title and a line
over the form: “Saving keeps these details by hand. Enrichment won't look for
a match again.” Saving keeps every field that holds a value by hand and marks
the title described by hand: its match reads “by hand”, enrichment searches
for it no more, and the banner becomes “Described by hand. Enrichment doesn't
look for a match.”, with **match by hand**, which still matches it. Leaving
without saving changes nothing.

From a scan's page the two are links into the catalog app: the title's page
with `?tab=details&open=match` or `?tab=details&open=describe`.

### artwork

The tab has two parts, **poster** and **backdrop**. Each shows:

1. **The picture in use**, with a tag for where it comes from: “enrichment”,
   “files”, “uploaded” or “a frame of the file”. An episode without a picture
   of its own shows its series', and a line says so.
2. **The other choices**, as a grid of pictures: those enrichment has for the
   title and those that lie beside its files, each with the same tag and its
   size, “1000 × 1500”. **use this**, a quiet button on a choice, makes it the
   title's picture at once; the toast says “Poster changed”.
3. **upload**, a button that takes a picture from the admin's computer: a JPEG
   or a PNG of 25 MB or less. The hint under it: “A JPEG or PNG of 25 MB or
   less. A poster is upright, 2 : 3; a backdrop is wide, 16 : 9.” The button
   shows the loader while the file goes; then the picture is in use, and the
   toast says “Poster uploaded”.
4. **use the catalog's choice**, a quiet button shown while the picture in use
   was chosen or uploaded by hand: the title's picture is again the one its
   sources give.

A picture chosen or uploaded by hand is kept as a field kept by hand is:
enrichment, a new match and the files beside the title leave it. The apps show
a title's poster and its backdrop, and the tab has those two; a logo that lies
beside a title's files is kept by the catalog and shown nowhere
([the library](./library.md)).

### files

The tab says what the library holds of the title. From the top it has:

1. **export as one file**, a button on a movie and on an episode, which takes
   the title out of the library as one file ([the library](./library.md)).
   It opens a dialog that says what can be had, as katalog-manager answers
   it:
   - **From**, a choice of “its package”, a Matroska file joined from the
     package, and “its original”, the file as it arrived, each with its size.
     One that can't be had is closed, with the server's reason under it.
   - Under its package, what goes into the file, “1920 × 800 HEVC HDR10 · 2
     audio tracks · 3 subtitles · 12 chapters”, and, where the library keeps a
     record of the title, what the file lacks against the original: “Not in
     this file: surround, lossless audio.”
   - **cancel**, and **export**, the emphasized button. The console asks
     katalog-manager for the export's link, which is good once and for 60
     seconds, and hands it to the browser, which saves the file itself: the
     file never passes through the page. The dialog closes once the download
     has begun.
2. **Hold the original**, a switch in a card of its own, with the sentence
   “While it is on, the catalog never deletes this title's original by itself,
   whatever the settings say.”; on a series, “While it is on, the catalog never
   deletes the originals of this series' episodes by itself, whatever the
   settings say.” It applies at once; the toast says “Original held” or
   “Original not held”. If it could not be changed, the switch goes back and a
   banner says so. The hold stops the catalog's own deletions alone:
   **delete**, in the title's head, with its files ticked, removes a held
   original too, as today.
3. **originals**, a table of the files the title was given, the oldest first:
   **file**, its name; **size**; **state**.
4. **versions**, a table of the title's versions, the newest first: **made**,
   when; **state**; **id**, the version's id as the design system's identifier
   cell.
5. **files on disk**, today's table of the title's files. A file the last full
   scan did not find says so in its row, in a line under its path: “gone since
   12 Nov 2026”.
6. **beside the title**, a table of the files beside the title that the
   catalog read: **file**, its path; **gives**, “details”, “poster”,
   “backdrop” or “logo”; **read**, when; and, for one that could not be read,
   why, in a line under its path. A title without such a file has no such
   table.

| An original, as the catalog has it | State | Meaning | The line under it |
|---|---|---|---|
| present, the title not held | kept | neutral | |
| present, the title held | held | neutral | “Not deleted while the hold is on.” |
| present, and its deletion didn't go through | couldn't be deleted | warning | the catalog's reason |
| superseded | replaced | neutral | “Another file took its place on 12 Nov 2026.” |
| superseded, and it waits for an admin | waits for an admin | warning | the catalog's reason |
| retiring | being deleted | information | |
| deleted | deleted | neutral | the date, and what its package doesn't carry of it: “12 Nov 2026 · not in the package: surround, lossless audio” |
| removed | removed | neutral | |

| A version, as the catalog has it | State | Meaning | The line under it |
|---|---|---|---|
| building | being made | information | |
| taken | original only | neutral | “No package. It plays from the original.” |
| complete, never verified | not verified yet | neutral | |
| complete, its last verification failed | verification failed | error | what did not hold, and when it is tried again: “segment-0412.m4s doesn't match its hash · again in 6 h” |
| complete, verified | verified | success | when, and how far: “12 Nov 2026 · every file” or “12 Nov 2026 · the records only” |
| superseded | replaced | neutral | the date |
| removed | removed | neutral | the date |

A title of which the library records no version and no original, as every
title of a library in the layout `legacy`, shows one line in place of those
two tables: “The library keeps no record of this title's versions.” A series
shows the switch and “A series has no file of its own. Its episodes have
theirs.”

Deleting chosen originals, and deciding what becomes of an original that waits
for an admin, have no screen in this chapter
([scope](../capabilities/scope.md)).

### subtitles

The tab lists the subtitles a viewer can choose for the title: the title's
own first, then those that were added, as katalog-manager lists them.

| Column | Shows |
|---|---|
| **language** | the language's name and its tag: “German (de)” |
| **kind** | “full”, “foreign-language parts” (the lines that come on by themselves) or “CC” (with the sounds described), a badge |
| **format** | the format as the catalog names it |
| **from** | “the file” for the title's own; “by hand” for one an admin added; “an addon” for one an addon attached; “made (AI)”; “made (OCR)” |
| **added** | for one that was added: when |

- **add subtitle file**, the emphasized button, opens a dialog: **File**, a
  `.srt` or `.vtt` file, with the hint “A .srt or .vtt file in UTF-8, 5 MB or
  less.”; **Language**, a select of languages by name, those the tab tracks
  offers, with “another language…”, which opens **Language tag** and the hint
  “As en, de or zh-Hans.”; **Kind**, a select of the three kinds, full first;
  **cancel** and
  **add subtitle**. The subtitle is in the list at once, and every app offers
  it from then on; nothing is packaged again. The toast says “Subtitle added”.
- **remove**, in the menu of a row that was added, asks first: “German, by
  hand, stops showing in every app.”, **cancel**, **remove subtitle**. The
  title's own subtitles have no menu.
- A subtitle can be added to a title that has a version in the library. For
  any other the dialog says why not (section States).

### extras

The tab lists the title's extras, in the order a viewer sees them. A removed
extra is not listed.

| Column | Shows |
|---|---|
| **title** | what the extra is called |
| **kind** | trailer, teaser, featurette, behind the scenes, making of, deleted scene, interview, gag reel, short or other, a badge |
| **language** | the language spoken in it, or “—” |
| **season** | a series' extra: the season it belongs to, “specials” for season 0, “—” for the whole series |
| **length** | how long it plays |
| **state** | the status below |

| An extra, as the catalog has it | State | Meaning | The line under it |
|---|---|---|---|
| pending, queued | waiting | neutral | when it is sent again, where the catalog says so |
| transcoding, transcoded, packaging | being packaged | information | |
| ready | ready | success | |
| failed | failed | error | its last error, under **details** |
| missing | file missing | warning | “Hidden until the file is back.” |

- **add extra**, the emphasized button, opens a dialog: **File**, with
  **choose file**; **Kind**, a select of the ten kinds; **Title**, with the
  hint “Left empty, it is named after its kind.”; **Language**, a select that
  starts on “not set”; on a series **Season**, a select of “the whole series”,
  its seasons and “specials”; **cancel** and **add extra**. The toast says
  “Extra added”, and the extra stands in the list as waiting.
- **choose file** opens the folders an extra can be taken in from, one level
  at a time: the folders of a level and its video files, each file with its
  size; a path of the folders opened so far, each a way back; **choose this
  file** on the file pressed. An extra's file lies on the storage the platform
  mounts already: nothing is uploaded.
- **package again** and **remove**, in a row's menu. Remove asks first: “It
  stops playing at once. Its file stays where it is, and its package is
  deleted a day later.”, **cancel**, **remove extra**.
- **package all again**, a quiet button in the toolbar, packages every extra
  of the title again. The toast says how many: “2 extras queued to be packaged
  again”.

## Collections

The view **collections** of the catalog app lists the catalog's collections.
What a collection is, and what the catalog does with one by itself, is in
[the library](./library.md).

| Column | Shows | Sorts |
|---|---|---|
| **name** | the collection's name, a link to its page; the row's name | A first; the order the view opens in |
| **titles** | how many it holds | most first |
| **made by** | “the catalog” or “by hand”, a badge | |
| **changed** | when it last changed | newest first |

The search, “search collections”, finds the words in a name (`q`); the filter
**made by** has all, the catalog and by hand (`by`: `catalog`, `hand`); the
sort is `sort` (`name`, `titles`, `changed`) and `dir`. **new collection**,
the emphasized button, opens a dialog with **Name**, of 1 to 120 characters,
**Description**, of 2,000 at most, **cancel** and **create collection**, and
then the new collection's page.

A collection's page shows:

1. **Its name**, the page's heading, the badge of who made it, and its
   description. **edit** opens a dialog with **Name** and **Description**,
   **cancel** and **save changes**. **delete** asks first: “The collection
   goes. Its titles stay in the library.”, **cancel**, **delete collection**.
2. **On a collection the catalog made**, a line under its head: “The catalog
   made this collection and keeps it up to date. A change to its name, its
   description or its titles makes it a collection by hand, which the catalog
   leaves as it is.” After such a change the badge reads “by hand”. A picture
   chosen or uploaded changes nothing of who made it.
3. **hand back to the catalog**, a quiet button on a collection made by hand.
   It asks first: “The catalog sets this collection's name, description and
   titles again. The changes made by hand to them go.”, **cancel**, **hand
   back**. A collection the catalog never made can't be handed back: the
   server refuses, and a banner says its sentence.
4. **artwork**: a poster and a backdrop, each as on a title's tab artwork: the
   picture in use, the choices enrichment has for the collection, **upload**
   and **use the catalog's choice**.
5. **titles**: its titles in its order, as a table: **#**, the place;
   the poster; **title**, a link to the title's page; **type**; **year**. A
   row's menu holds **move up**, **move down** and **remove**; the first row
   has no move up, the last no move down. Each applies at once. The table
   holds every title of the collection, 500 at most, and does not sort.
6. **add titles**, the emphasized button, opens a dialog: a search, “search
   titles”, and under it the movies and series that match, each with a
   checkbox; a title that is in the collection already is ticked, closed and
   marked “in the collection”. **cancel**, and **add 3 titles**, which names
   how many are ticked and puts them at the end of the order. The toast says
   “3 titles added”.

## Libraries

The view **libraries** of catalog admin lists the libraries, by name. It has
no filter bar: a household has a handful. What a library and its folders are,
and their rules, is in [the library](./library.md).

| Column | Shows |
|---|---|
| **name** | the library's name, a link to its page; the row's name |
| **kind** | “movies” or “shows”, a badge |
| **folders** | how many folders it has; in a line under it, how many of them can't be reached: “1 unavailable” |
| **titles** | how many titles it holds |
| **files gone** | how many of its titles have a file that is gone, a link to the view titles with this library and file gone chosen; “—” for none |
| **audience** | who sees the library: “everyone”, or how many of the household's people, “3 of 5 people” |
| **scans** | “when files change”, “every hour” with the interval it has, or “only by hand”; for a library that can't be watched, “every hour”, with the server's reason in a line under it |
| **last scan** | when its last scan began; while one runs, “running”, a link to it |

**add library**, the emphasized button, opens a dialog: **Name**, of 1 to 60
characters; **Kind**, a select of movies and shows, which never changes
afterwards; **Folder**, with **choose folder**, which may stay empty;
**Scans**, as on a library's page; **cancel** and **add library**. It then
opens the new library's page; with a folder, the library's first scan has
started.

A library's page shows:

1. **Its name**, the page's heading, the badge of its kind, and its id,
   `kids-movies`, which the catalog gives it and never changes.
2. **scan now**, the emphasized button: a full scan of this library. The toast
   says “Scan started”. While a scan of the library runs, the page says “A
   scan is running.”, with **open it**, a link to that scan's page, and scan
   now is not offered.
3. **A library that can't be watched** has a warning banner with the server's
   reason: “This folder's storage doesn't report changes. The library is
   scanned every hour instead.”
4. **Who sees it**, a line: “Everyone who signs in sees this library's
   titles.”, or “3 of 5 people see this library's titles: Alex, Mia and Sam.”,
   with five names at most and then “and 4 more”; and **change in people**, a
   link to the portal's people view. Who sees a library is a right of each
   person and is changed on that person's page
   ([people](../portal/people.md)), not here.
5. **Its fields**, a form with **cancel** and **save changes**:
   - **Name**.
   - **Scans**, a select of “when files change”, “on a schedule” and “only by
     hand”; with on a schedule, **Every**, a number and its unit, minutes,
     hours or days, from 1 minute to 7 days, which starts at 1 hour. A
     sentence under it says what the choice does: “The library is scanned
     when its files change, and in full every night.”, “The library is
     scanned in full at this interval.” or “The library is scanned only when
     someone starts a scan.”
6. **folders**, a table: **folder**, as the catalog writes it,
   `archive:/films`, with the badge “default folder” on the folder the catalog
   scanned before it had libraries; **titles**, how many of the library's
   titles have their file in it; and, for a folder the last scan could not
   reach, the status “unavailable”, warning, with since when and the server's
   reason in the line under it. A row's menu holds **remove**, except on the
   default folder. **add folder** stands over the table.
7. **last scans**: the library's five last scans, with the columns of the view
   scans, and **every scan of this library**, a link to that view with the
   library chosen.
8. **delete**, in the page's head, which asks first, in one of three ways.
   For a library without titles: “The library goes. Its folders are free
   again, and no file is deleted.”, **cancel**, **delete library**. For one
   that holds titles: **Move its titles to**, a select of the other libraries
   of its kind, and “Its 412 titles move to the library chosen. Its folders
   are free again, and no file is deleted.”, **cancel**, **delete library**.
   For one that holds titles while no other library of its kind exists: “This
   library still holds titles. Move them to another library of its kind
   first.”, and **cancel** alone.

**add folder** and **choose folder** open the same dialog, the folder chooser.

- It opens on the volumes the platform mounts, by name. A volume opens its
  folders, a folder its folders, one level at a time, each by its name; a path
  of the folders opened so far stands over the list, each a way back. A level
  lists 500 folders at most, and says how many more there are: “212 more
  folders are not listed.”
- A folder the catalog would not take says why in a line under its name, in
  the server's sentence, “This folder is already in a library.” It can still
  be opened.
- **Move the titles already taken in from this folder to this library**, a
  checkbox, not ticked: without it a title that was made from a file in the
  folder keeps the library it has.
- Its emphasized button takes the folder that is open: **add this folder** on
  a library's page, where it adds the folder at once and the library's scan
  starts; **choose this folder** in the dialog add library, where the folder
  is added with the library. The button is closed while the folder that is
  open can't be taken.

The audience is not the catalog's to keep. The console works it out from
portal-api's list of people, which says for each person the libraries their
right names: a library is seen by everyone who has no such right and by those
whose right names it. Where the console can't read that list, the column shows
“—” and the page's line is left out.

**remove**, on a folder, asks first: “The catalog stops looking in this
folder. The titles it took in from it stay in the library, and no file is
deleted.”, **cancel**, **remove folder**.

A movie's or a series' library is changed on the title's tab details: beside
the library's name stands **move**, a quiet button, which opens a dialog with
**Library**, a select of the other libraries of the title's kind, **cancel**
and **move title**. The toast says “Moved to Kids”. An episode moves with its
series and has no such button; neither has a title when no other library of
its kind exists.

## Scans

The view **scans** of catalog admin lists the scans, the newest first. What a
scan does and keeps is in [the library](./library.md).

| Column | Shows | Sorts | Folds |
|---|---|---|---|
| **when** | when the scan began, a link to its page; the row's name | newest first; the order the view opens in | never |
| **library** | the library scanned, a link to its page | | never |
| **started by** | what started it, in the server's words: an admin's name, “the schedule”, “a file change”, “the nightly scan”, “the platform”, “the catalog, after it started” or “a new folder” | | second |
| **state** | “running”, information; “done”, neutral; “failed”, error, with the scan's error in the line under it | | never |
| **added** | the files it added | most first | first |
| **changed** | the files it found changed | most first | first |
| **gone** | the files it found gone | most first | first |
| **passed over** | the files it passed over | most first | second |
| **took** | how long it ran: “42 s”, “3 min” | longest first | first |

| Filter | Values | In the address |
|---|---|---|
| **library** | all, then the libraries by name | `library`, the library's id |
| **started by** | all, an admin, the schedule, a file change | `by`: `admin`, `schedule`, `watch` |
| **state** | all, running, done, failed | `state` |
| **changes** | all, with changes: the scans that added, changed, lost or passed over a file | `changes`: `1` |
| the sort | a column that sorts, and its direction | `sort`: `when`, `added`, `changed`, `gone`, `passed`, `took`; `dir` |

**scan now**, the emphasized button of the toolbar, starts a full scan. With
one library it scans that library; with several it opens a menu of “every
library” and each library by name. The toast says “Scan started”, or “3 scans
started”. A library that is being scanned is not scanned twice: its running
scan is the answer.

### A scan's page

The page is the design system's
[worklist](https://nalet.github.io/design-system/patterns/worklist/). Its
heading names the library, “scan of Movies”. The line under it says when it
began, what started it, whether it walked the library's folders or took the
files that were reported changed, and how long it took: “12 Nov 2026, 14:00 ·
started by the schedule · a full scan · took 42 s”, “… · started by a file
change · the changed files · took 4 s”. A scan that failed says its error
there too.

- **The tabs** count the scan's files by what happened to them and filter the
  table: **everything**, **added**, **changed**, **gone**, **passed over**
  (`show`: `added`, `changed`, `gone`, `passed`).
- **The search**, “search files”, finds the words in a file's path (`q`).
- **download CSV** is in the toolbar: the scan's files as katalog-manager
  writes them, for the tab and the search that are set.
- **A scan that found more files than it lists** says so in a banner: “This
  scan found 12,400 more files than it lists.”

| Column | Shows | Sorts |
|---|---|---|
| **file** | the file's path inside its library's folder; the row's name | A first; the order the page opens in |
| **what happened** | a status: “added”, “changed” or “gone”, neutral; “passed over”, warning. The line under it is the scan's own sentence for the file: “Taken in as “Big Buck Bunny”.”, “The file is still being written. The next scan takes it in.” | |
| **title** | the title the file belongs to, a link to its page; “—” for a file that has none | |
| **match** | that title's match as it is now: “matched”, “not matched”, “by hand”; “—” without a title | |

A row with a title has a menu: **open title**, and, while the title is not
matched, **match by hand** and **describe by hand** (section Match by hand and
describe by hand). A row without a title has no menu; for a file that was
passed over, its sentence says what to do.

While the scan runs, the page says “Scanning…” beside the loader, and reads
again every 10 seconds; it lists what the scan has found by then.

## Settings

The view **settings** of catalog admin is one page of every setting the
catalog has. No key is typed, and no setting is made by hand.

1. **keys**, first, a card of its own: the four keys of the reference data
   services. A key is write-only, as today: the card says “set” or “not set”
   for each, and has a field for a new key, **set**, and **clear** on a key
   that is set. It is not part of the form below.
2. **The form**: one card for each group, in the order of the table below,
   with the group's name as its title. A setting is one field: its name as the
   label; under it one sentence that says what it does; its control; and
   “Default:” with its default, “Default: 24 hours.” **reset**, a quiet button
   beside a field whose value is not its default, puts the default into the
   field.
3. **The foot**, in view while the form scrolls: “unsaved changes” while a
   value differs from the saved one, **cancel**, and **save changes**, the one
   emphasized button. Saving checks every field, shows each mistake at its
   field with how to fix it, and names them in a banner over the form; with
   none, it saves, and the toast says “Settings saved”. A setting takes effect
   the next time the catalog reads it; nothing is restarted.
4. **other settings**, last, and only when there are any: the rows of the
   catalog's settings whose key the catalog doesn't know, with the sentence
   “The catalog doesn't know these settings. They have no effect.”, each with
   its **key**, its **value** and **remove**. None can be added.

The controls are the design system's. An on or off setting is a checkbox,
because it is saved with the form; the design system's switch is for a setting
that applies at once. A setting that is one of a few values is a select. A
number is an input with its unit after it. A duration is a number and a
select of its unit, seconds, minutes, hours or days. A time of day is an input
that takes “22:00”. A list is one input, its values separated by commas.

- **A value at its default is not stored**: saving a field that holds its
  default removes the setting, so a default that changes with a release
  reaches it.
- **A stored value the catalog can't read**, as one typed by hand before, is
  shown with the error “The stored value “abc” can't be read, so the default
  is in force.” over the field, which holds the default.
- **Originals**, changed to “deleted once their package is verified”, asks
  before the form is saved: “From now on the catalog deletes a title's
  original once its package is verified and lacks nothing the rules keep. A
  deleted original can't be brought back once its time in the trash is over.”,
  **cancel**, and **delete originals**, a danger button.
- **Library layout** is shown and not changed here: the library's migration
  switches it. While it is `legacy`, the catalog records no versions and
  deletes no original, so Originals is shown and not changed either, with the
  sentence “No original is deleted while the library's layout is legacy.”

### The settings

The catalog and the packager read 43 settings today. “Stored” is the value
the form writes for a choice. [The library](./library.md) adds three to the
group scanning, `scan.settle`, `scan.nightly` and `scan.sidecars`, with their
names, controls and sentences; the form shows them with the others once
katalog-manager lists them.

| Key | Name | Group | Control | Values | Default | The sentence under the name |
|---|---|---|---|---|---|---|
| `tmdb.api_key` | TMDB key | keys | write-only field | a TMDB read access token; TMDB is asked whether it is good before it is stored | not set | Titles are looked up at TMDB with it. |
| `omdb.api_key` | OMDb key | keys | write-only field | an API key | not set | A second source of descriptions, ratings and posters, asked where TMDB has nothing. |
| `fanart.api_key` | fanart.tv project key | keys | write-only field | an API key | not set | A source of posters and backdrops, asked where TMDB has no picture. |
| `fanart.client_key` | fanart.tv personal key | keys | write-only field | an API key | not set | Optional. With it, that source answers with its newest pictures. |
| `extras.scan` | Extras from the folders | scanning | checkbox | on, off; stored `on`, `off` | off | A scan takes in the files named or filed as a title's trailers and other extras. It applies from the next scan. |
| `ratings.countries` | Rating countries | age ratings | input | two-letter country codes separated by commas, in the order they are asked, of AU, BR, CA, CH, DE, DK, ES, FI, FR, GB, IE, IT, JP, KR, LU, MX, NL, NO, NZ, PT, RU, SE, SG, US | CH, DE, US | A title takes its age rating from the first of these countries that rates it. |
| `ratings.unrated_for_capped` | Titles without a rating | age ratings | select | “hidden from people with an age limit”, stored `hide`; “shown to everyone”, stored `show` | hidden from people with an age limit | Whether people with an age limit see the titles that nothing rates. |
| `packager.language_whitelist` | Languages shown | languages and sound | input | language codes of two or three letters separated by commas, as `en, de`; empty for every language | empty | The apps list a title's audio and subtitle tracks in these languages; tracks in other languages are packaged hidden. It applies to titles packaged from now on. |
| `packager.keep_original_if_single` | A title in hidden languages only | languages and sound | checkbox | on, off; stored `true`, `false` | on | A title whose every track is in a language not shown lists its tracks all the same. |
| `packager.stereo_loudness` | Stereo loudness | languages and sound | select and a number | “off”, stored `off`; “lifted to” a loudness from −35 to −10 LUFS, stored as the number | lifted to −20 LUFS | A quiet stereo track is lifted to this loudness when a title is packaged. |
| `subtitles.languages` | Subtitle languages | languages and sound | input | language tags separated by commas, as `en, de, zh-Hans`; empty for the languages shown | empty | Every title is to have a subtitle in each of these languages. |
| `library.layout` | Library layout | originals | shown, not changed | `legacy`, `v2` | legacy | How the library lies on storage. The library's migration switches it. |
| `library.originals` | Originals | originals | select | “kept”, stored `keep`; “deleted once their package is verified”, stored `delete-after-package` | kept | What becomes of a title's original once its package is complete and verified and lacks nothing the rules keep. |
| `library.retire.delay` | Wait before deleting | originals | number and unit | a duration of 0 or more | 10 minutes | How long a version has to be complete before the original it was made from is deleted. |
| `library.retire.rate` | Originals deleted a minute | originals | number | 1 or more | 30 | The most originals the catalog deletes in a minute. |
| `library.trash.grace` | Time in the trash | originals | number and unit | a duration of 0 or more; 0 deletes at once | 24 hours | How long a deleted original stays in the trash, where a deletion can be undone. Its space is freed when it leaves the trash. |
| `library.verify` | Check before deleting | originals | select | “every file's hash”, stored `full`; “the records only”, stored `chain` | every file's hash | How a version is checked before its original is deleted. |
| `library.verify.maxAge` | A full check holds for | originals | number and unit | a duration of 0 or more | 30 days | Within this time of a check of every file, the records alone are checked before an original is deleted. |
| `library.verify.new` | Verify new versions | originals | checkbox | on, off; stored `on`, `off` | on | Each new version is checked in full once, soon after it is made. |
| `library.superseded.grace` | A replaced version stays | originals | number and unit | a duration of 0 or more | 24 hours | How long a version stays after a newer one took its place. |
| `library.superseded.delay` | A replaced original stays | originals | number and unit | a duration of 0 or more; 0 for no wait | 7 days | How long the new file's version has to be complete before the original it replaced is deleted, so that a wrong file can be taken back. |
| `library.superseded.accept` | A replaced original may lose | originals | multi-select | the 17 losses of the section Words; none ticked is stored `none` | more audio channels, surround, lossless audio, object audio, 3D | What a replaced original may carry that the new version lacks, and still be deleted without an admin. Any other loss waits for an admin. |
| `library.replace.clients` | Addons that may replace a file | originals | input | client ids separated by commas; empty for none | empty | The addons that may give a title another file and have its old original deleted, each by the client id of its service account. |
| `library.retire.list` | Lists of originals to delete | originals | select | “off”, stored `off`; “dry run only”, stored `dry-run`; “on”, stored `on` | dry run only | What a list of chosen originals, sent through the API, may do. |
| `library.retire.list.maxAge` | A dry run holds for | originals | number and unit | a duration above 0 | 24 hours | How long a dry run's word on its titles holds for the run that deletes them. |
| `library.reencode.rate` | Titles sent each pass | processing again | number | 0 or more; 0 sends none | 4 | How many queued titles the catalog sends to be processed again each time it looks at the queue. |
| `library.reencode.inflight` | Titles processed at once | processing again | number | 1 or more | 4 | How many queued titles may be sent and not done at the same time. |
| `library.reencode.window` | Hours | processing again | select and two times | “any time”, stored empty; “between” two times of day, in the server's local time, stored as `23:00-07:00` | any time | When queued titles are sent to be processed again. |
| `compliance.pass` | Check titles against the rules | rules check | checkbox | on, off; stored `on`, `off` | on | The catalog checks the titles that need it in the background. Off, the rules view keeps what the last check found. |
| `compliance.readers` | Records read at once | rules check | number | 1 to 64 | 4 | How many records the check reads at the same time. |
| `compliance.nightly` | Daily check of every title | rules check | select and a time | “off”, stored `off`; “at” a time of day, in the server's local time, stored as `03:00` | at 03:00 | When every title is checked again each day. |
| `chapters.backfill` | Read missing chapters | chapters | checkbox | on, off; stored `on`, `off` | off | The catalog hands out the titles that miss their chapters, to be read again. |
| `chapters.backfill.window` | Hours | chapters | select and two times | “any time”, stored empty; “between” two times of day, in UTC, stored as `22:00-17:00` | between 22:00 and 17:00 UTC | When titles are handed out. |
| `chapters.backfill.inflight` | Titles out at once | chapters | number | 1 or more | 1 | How many titles may be handed out and not reported back at the same time. |
| `chapters.backfill.rate` | Titles an hour | chapters | number | 0 or more; 0 hands out none | 120 | The most titles handed out in an hour. |
| `chapters.backfill.records` | Records read an hour | chapters | number | 0 or more; 0 reads none, and every title goes to the analyzer | 3,600 | The most source records the catalog reads chapters from in an hour. |
| `chapters.backfill.lease` | A title counts as lost after | chapters | number and unit | a duration of 1 minute or more | 30 minutes | How long a title handed out is its worker's before it is handed out again. |
| `picture.backfill` | Measure missing picture areas | picture areas | checkbox | on, off; stored `on`, `off` | off | The catalog hands out the titles without a picture area, to be measured. |
| `picture.backfill.window` | Hours | picture areas | select and two times | “any time”, stored empty; “between” two times of day, in UTC, stored as `22:00-17:00` | between 22:00 and 17:00 UTC | When titles are handed out. |
| `picture.backfill.inflight` | Titles out at once | picture areas | number | 1 or more | 1 | How many titles may be handed out and not reported back at the same time. |
| `picture.backfill.rate` | Titles an hour | picture areas | number | 0 or more; 0 hands out none | 240 | The most titles handed out in an hour. |
| `picture.backfill.lease` | A title counts as lost after | picture areas | number and unit | a duration of 1 minute or more | 6 hours | How long a title handed out is its worker's before it is handed out again. |
| `validate.small_file_threshold_mb` | Small file (MB) | file check | number | 0 or more | 5 | **validate** reports a file of a title, other than its main file, that is smaller than this. |

A value of `library.superseded.accept` that names a language, as
`subtitleLanguages:de`, is set through the API; the form lists it after the 17
losses, by its name as it is, ticked, and it can be unticked.

## What katalog-manager offers for it

The console needs these of katalog-manager. Each is for admins alone, as every
field and route the console uses today, and each is reached under
`/api/manage`, the one path of katalog-manager the platform publishes. A name
in code face that katalog-manager has today is as it is; a new one is this
chapter's proposal.

### Titles, paged

The query `titles` answers a page of the catalog's items.

| It takes | Meaning |
|---|---|
| `search` | words; an item matches when its title, its sort title or its original title holds them, whatever their case |
| `type`, `genre`, `year`, `hasOriginal` | as `items` takes them today |
| `library` | a library's id: the items of that library |
| `match` | `MATCHED`, `NOT_MATCHED` or `BY_HAND` (section Matches) |
| `missing` | true: the items whose file is gone ([the library](./library.md)) |
| `sort` | `ADDED`, when the item was first listed, the default; `TITLE`, its sort title, else its title; `YEAR`; `ORIGINAL_SIZE`; `PACKAGE_SIZE` |
| `descending` | the direction. Left out, the newest, the largest and A come first. An item without the value comes last either way, and items that tie keep the order they were added in |
| `first`, `after` | at most `first` rows, 1 to 200, 50 when left out, after the cursor `after`, which is a `nextCursor` of the same filters and order |

It answers `rows`, each an item as `items` answers it today, with the library
it belongs to (`inLibrary`: its id and its name), its match and when it was
first listed;
`total`, the number of items the filters match; and `nextCursor`, none on the
last page. `items` stays as it is.

`GET /api/manage/titles.csv` takes the same filters and the same order as
query parameters and answers every item they match, in that order, as CSV in
UTF-8 with a header row: `title`, `type`, `year`, `library`, `match`,
`has_original`, `original_bytes`, `package_bytes`, `packaged`, `status`,
`added`, `id`. It names the file after when it was made, in UTC,
`titles-2026-11-15T1343Z.csv`, as `compliance.csv` names its own.

### A title's fields

1. **Each field says its source.** An item answers, for its title, sort title,
   original title, year, tagline, description, genres, tags and minimum age,
   where the value comes from: `MANUAL`, `FILES`, `ENRICHMENT` or `FILE_NAME`;
   nothing for a field that is empty and that nobody emptied by hand.
2. **By hand, field by field.** A write names the fields it changes. Each is
   stored and is `MANUAL` from then on; nothing else of the item changes. A
   field written empty is empty by hand. Nothing changes a `MANUAL` field but
   an admin: not enrichment, a new match, the refresh from the reference
   data's change lists, a scan, or the files beside the title.
3. **Giving a field back.** A write may name fields to give back. Each stops
   being `MANUAL` and takes the value of the next source in
   [the library](./library.md)'s order. katalog-manager finds that value
   before it answers, from the files beside the title, else from enrichment,
   which it asks then; so its answer holds the new values and their sources.
   Where it has to ask enrichment and can't, it refuses the whole write with
   the code `ENRICHMENT_UNAVAILABLE`, and nothing changes.
4. **An original title**, a text of its own. Enrichment fills it with the
   title the metadata service gives as the original one, where that is not the
   title itself, and the library's record carries it as `titles.original`.
5. **The minimum age** is what `setMinAgeOverride` sets today.
6. **A title locked today.** An item whose `metadataLocked` is set reads its
   title, sort title, year, tagline and description as `MANUAL`, and the lock
   goes on keeping what else it keeps today: the rating, the runtime and the
   credits. The console sets `metadataLocked` no more.

### Matches

- `matchCandidates` takes an item's id, a title and a year, the item's own
  where they are left out. It answers at most ten titles of the metadata
  service, movies for a movie and shows for a series, the best first, as
  `identify` ranks them: each with its TMDB id, its title, its original title,
  its year, the first 200 characters of its description, and a poster the
  console can show. It answers none when nothing is found. It refuses with
  `NO_KEY` when the catalog has no key for the metadata service, and with
  `ENRICHMENT_UNAVAILABLE` when the service gives no answer.
- An item answers its **match**: `MATCHED` when it has the metadata service's
  id, `BY_HAND` when an admin described it by hand, else `NOT_MATCHED`. An
  episode's is its series'.
- `describeByHand` takes a movie's or a series' id and on or off. While it is
  on, enrichment's sweep and `retryNotFound` leave the item; `identify` still
  matches it, and a match ends it.
- `identify` stays as it is.

### Pictures

- An item answers the **choices** for its poster and for its backdrop: the
  metadata service's pictures of that kind for the item's match, at most 30,
  in the service's order, asked when the choices are read and kept for an
  hour; the pictures beside the title's files, as
  [the library](./library.md) reads them; the picture an admin uploaded; and
  the frame the analyzer took from the file. Each has its source,
  `ENRICHMENT`, `FILES`, `UPLOAD` or `FRAME`, its width and height, an address
  the console can read it at with its token, and whether it is the one in use.
  When the metadata service can't be asked, the answer holds the others and
  says so.
- `setPicture` takes an item, a kind and a choice: the choice is the item's
  picture of that kind, kept by hand, so that no source replaces it.
- `POST /api/manage/artwork/{itemId}/{kind}` takes a picture as its body: a
  JPEG or a PNG of at most 25,000,000 bytes. It becomes the item's picture of
  that kind, kept by hand, in place of an earlier upload. It answers 415 for a
  file that is neither, 413 for a larger one, 422 for one that can't be read
  as a picture, and 404 for an item there is not.
- `clearPicture` takes an item and a kind: the item's picture is again the one
  its sources give, and an upload of that kind is deleted.
- The kinds stay `poster` and `backdrop`, and an episode without a picture of
  a kind is served its parent's, as today.
- A collection's poster and backdrop are offered the same way.

### A failed verification

A version answers, beside when and how far it was verified, when its last
verification failed, what did not hold, as the verifier says it in its log
today, and when it is tried again. katalog-manager keeps the three in the
catalog, so that a restart keeps them, and clears them once the version is
verified.

### Subtitles from an admin

The three routes that list a title's subtitles, attach one and remove one
attached are offered to admins under `/api/manage` too, as
`/api/manage/library/items/{itemId}/subtitles`, with what they take and answer
today. An attach names one more way a subtitle came to be, `manual`: an
admin's own file. The limits and the refusals stay: a body of at most 8 MiB;
a text in UTF-8, SubRip or WebVTT, with a cue; a title with a version in the
library. The console takes a file of 5 MB at most, so that the file, wrapped
as the route takes it, stays under the body's limit.

### An extra's file

`extraSources` answers one level of the folders an extra can be taken in from
on this installation. Without a path it answers those folders, each by the
name it is known under. With a path it answers that folder's folders and its
video files, each file with its size, by name, at most 500, and how many more
there are. It never answers the package store, a hidden folder or a link that
leads out of those folders, and it refuses a path outside them. `addExtra`
stays as it is.

### Settings, named

- `knownSettings` answers every setting of the table in the section Settings,
  and every setting another chapter adds to the catalog's settings:
  its key, its group, its kind (on or off, a choice, a number, a duration, a
  time of day, a daily span, a list, a secret, or shown only), the values a
  choice has, the least and the most a number or a duration may be, its unit,
  its default, the value stored or none, when it was last written, and, where
  the stored value can't be read, why.
- `setSetting` takes a key and a value. It refuses a key that is not in the
  list, and a value its kind or its limits don't take, with the code
  `SETTING_REFUSED` and the limits; else it stores the value in the form its
  reader takes. `library.layout` is refused.
- `resetSetting` takes a key and removes what is stored, so that the default
  holds.
- `settings`, `createSetting`, `updateSetting` and `deleteSetting` stay, for
  the library's migration and for tools; the console uses `settings` to find
  the rows whose key is not in the list, and `deleteSetting` to remove one.
  The secrets stay as they are.

## The design system's parts, and the console's own

The lists, forms, dialogs, banners, toasts, empty states and statuses of this
chapter are the design system's, in its version 0.4.0, and so is whatever
this chapter does not say of them, the keyboard and screen readers included.

- **Buttons.** A view, a tab and a dialog have one emphasized button at most,
  for their main action. **cancel** and the lesser actions are quiet buttons.
  An action on one row is in the row's menu, the design system's action menu.
- **Removing asks first.** Whatever removes or deletes opens a dialog with
  what goes and what stays, **cancel**, and the action's own words on a
  danger button: **remove subtitle**, **remove extra**, **remove folder**,
  **delete collection**, **delete library**, **delete originals**. Handing a
  collection back asks first in the same way.
- **What happened.** A toast says what an action did and leaves by itself. A
  banner says what could not be done and stays until it is dismissed (section
  States).

Three parts are the console's own, drawn with the design system's parts and
on its colours, faces and sizes, until the design system has them:

- **A page about one thing**: the head and the row of tabs of a title's page,
  as built. The design system plans a detail page.
- **The folder and file chooser** of add folder and of choose file: a dialog
  with a path and a list.
- **The grid of pictures** of the tab artwork: cards, each with a picture, a
  tag and one quiet button.

## Language and accessibility

The console speaks the person's language
([ADR-0023](../../docs/adr/0023-languages-and-accessibility.md)). Hosted in
the portal it takes the language the shell hands it; opened on its own page it
follows the browser's languages, and English where it has none of them. Every
text comes from the message catalogue, and none is typed into a view's code.

- **What katalog-manager says.** A finding of the compliance check, the reason
  a title waits or can't be processed again, and the result of an action reach
  the console as a code with its values, and the console has the sentence.
  The sentence katalog-manager writes stays in its answer as the detail; the
  console shows it under **details**, and only for a code it doesn't know.
- **The report as a file** is written by katalog-manager in the language the
  request names, from the same message catalogue.
- **Numbers and dates** follow the language.
- **Names from the library.** A language has the name the browser gives it in
  the console's language; a genre the message catalogue knows has its name
  from there. A title's own texts show as the library has them.
- **Every view meets the design system's accessibility baseline**, WCAG 2.2 at
  level AA: every control has a name; the Tab key reaches everything in the
  order of reading, with **skip to content** as its first stop; Esc closes the
  layer on top and gives the focus back; every text is whole at a zoom of
  200 % and in a window 320 px wide; nothing moves on its way where the
  browser asks for less motion. A test in the repository opens every view in
  each of its states, in English and in German, and fails on any finding.

## Changes

Every difference between the section As built and the target is one change in
the table. A change names where it is built, the catalog console or the
server, what they do today and the target, with the section that sets it out;
it is built as its row says, and nothing else changes with it. Each change
starts as proposed. A target that starts with “Recommended” holds a choice
that is the owner's, or takes away something the console has today.

| No. | Change | Where | Today | Target | Status |
|---|---|---|---|---|---|
| K.C1 | The design system 0.4.0 | Catalog console | the package 0.1.0, a copy kept in the console's code, without a data table, filter bar, status, banner, toast or empty state; the rules view draws its own | 0.4.0, the version chino's web and the portal take ([chino, chapter 2](../chino/frame.md), change 2.C11; [the home page](../portal/home.md), change H.C1); every part this chapter calls the design system's is that version's component; a view no change names keeps the parts it draws itself (section The design system's parts, and the console's own) | approved |
| K.C2 | Two apps, each with its views | Catalog console | “katalog”, with “browse the catalog” under it and no navigation; catalog management with the tabs scan, activity, Processing, rules, settings; the window's title “katalog · zaentrum” in both; a view's filters and a title's tab in no address; an address opened signed out ends on the app's first view after signing in | Recommended: the two apps stay, named catalog and catalog admin (H.C8), with the views, order, addresses, names and window titles of the section The two apps and their views: catalog gets the tabs titles and collections, catalog admin scans, activity, processing, rules, libraries and settings; signing in keeps the address; the other choice is one app with all eight views in one navigation | approved |
| K.C3 | A page of titles, counted and sorted | Server | `items` answers the newest first, at most 200 from an offset, without the count of all that match, without another order and without a filter by library or match; nothing answers the list as CSV | katalog-manager answers `titles` and `titles.csv` as the section Titles, paged sets them out: the filters of today and by library, by match and for a file that is gone, a search that also reads the sort title and the original title, five orders, 1 to 200 rows after a cursor, and the count of all that match | approved |
| K.C4 | titles: every title, 50 at a time | Catalog console | the newest 200 that match and no way to the rest; “200 items” counts the rows shown; no column sorts; the filters are lost with a reload; no library, match or added | the sections Lists and Titles: every title 50 rows at a time with show 50 more, the count of all that match, the columns library, match and added, the filters library, match and file, five columns that sort on the server, the search, the filters and the sort in the address, and download CSV; the column and the filter library, and the filter file, show once the catalog has libraries ([the library](./library.md)) | approved |
| K.C5 | A title's page: its tabs | Catalog console | ten tabs, overview, Episodes, Steps, assets, Tracks, segments, chapters, trailers, cast, diagnostics; the tab is in no address | today's tabs in the order of the section A title's page and in lowercase, overview named details and assets named files; the tab in the address as `tab`; each new tab takes its place in that order with its own change | approved |
| K.C6 | A title's fields: a source each, kept by hand one by one | Server | one lock for the whole title, which keeps its texts, rating, runtime and credits from enrichment and neither its genres nor its pictures; no field says where its value comes from; `updateItem` can't empty a field; genres set by hand are added to at the next refresh; no original title | katalog-manager does what the section A title's fields sets out: each of nine fields answers its source; a write keeps the fields it names by hand and no others; a field can be emptied, and given back to the files and enrichment; an original title is kept; a title locked today reads its texts as by hand; the order of the sources is [the library](./library.md)'s | approved |
| K.C7 | details: every field, by hand | Catalog console | overview shows the description, runtime, genres, tags and ids and changes nothing; the dialog “edit metadata” changes title, year, tagline and description and locks the whole title; the sort title, genres, tags and an age by hand through the API alone | the form of the section details: nine fields, each with the tag of its source; a field saved is kept by hand, alone; use the catalog's value gives it back; the age rating enrichment found over the field Minimum age (years); save changes, cancel and unsaved changes as the design system's forms have them; the button edit, its dialog and the badge “manual” go | approved |
| K.C8 | Matches to choose from, and a title described by hand | Server | `identify` takes a corrected title or an id and takes the best match itself; nothing answers the matches; an item is matched when it has the metadata service's id, and nothing else is kept | katalog-manager answers `matchCandidates`, an item's match and `describeByHand` as the section Matches sets them out: at most ten matches for a title and a year, the best first; matched, not matched or by hand; a title described by hand is left by enrichment and can still be matched | approved |
| K.C9 | match by hand, and describe by hand | Catalog console | identify: a dialog with a title and a “tmdb id”; the match is taken unseen, and what happened is a line of the server's words; a title that is not matched is told by its missing ids alone | the section Match by hand and describe by hand: identify is named match by hand, and its dialog has a search by title and year, the matches to choose from, the id, what a match replaces, and the toast; describe by hand on the tab details; the banner of a title that is not matched; both reached from a scan's page | approved |
| K.C10 | A title's pictures: the choices, one by hand, an upload | Server | one poster and one backdrop for a title, the match's, else a frame of its file; no other choice is kept; the one route that takes a picture is the analyzer's, inside the cluster | katalog-manager offers what the section Pictures sets out: the choices for a poster and a backdrop with their source and size, `setPicture`, `clearPicture`, and an upload under `/api/manage` of a JPEG or PNG of at most 25,000,000 bytes; a picture chosen or uploaded is kept by hand; a collection's pictures the same way | approved |
| K.C11 | artwork | Catalog console | the poster in the page's head, and no way to change it | the tab artwork of the section artwork: for the poster and the backdrop the picture in use with its source, the choices as a grid with use this, upload, and use the catalog's choice | approved |
| K.C12 | A failed verification is kept | Server | the verifier keeps a version it could not verify in its own memory, says why in its log, and tries again 6 hours later, then longer; a version answers when and how far it was verified, and nothing of a failure | katalog-manager keeps, for a version, when its last verification failed, what did not hold and when it is tried again, across a restart, and answers them with the version (section A failed verification) | approved |
| K.C13 | files: the originals, the versions and the hold | Catalog console | assets lists the title's files; what the library holds of a title and `holdOriginal` have no screen | the tab files of the section files: the switch Hold the original with what it means; the table originals with the states kept, held, couldn't be deleted, replaced, waits for an admin, being deleted, deleted and removed; the table versions with being made, original only, not verified yet, verified, replaced and removed, and verification failed once katalog-manager keeps it (K.C12); today's table as files on disk; and, once the catalog reads them ([the library](./library.md)), a file that is gone marked in its row and the table beside the title | approved |
| K.C14 | export as one file | Catalog console | nothing takes a title out of the library as a file | export as one file on the tab files of a movie and an episode (section files): a dialog with what can be had, its package or its original, each with its size, what goes into the file and what it lacks against the original; export asks katalog-manager for the link, good once and for 60 seconds, which the browser follows by itself, so the file is saved without passing through the page; the export is [the library](./library.md)'s | approved |
| K.C15 | A subtitle file from an admin | Server | the routes that list, attach and remove a title's subtitles answer inside the cluster only; a subtitle came to be as `source`, `provider`, `transcribed`, `translated`, `converted` or `recognized` | katalog-manager offers the three routes to admins under `/api/manage/library/items/{itemId}/subtitles` and takes `manual` for an admin's own file (section Subtitles from an admin) | approved |
| K.C16 | subtitles | Catalog console | Tracks lists the tracks of the source; the title's subtitles are listed nowhere, and none can be added | the tab subtitles of the section subtitles: the title's subtitles with language, kind, format, from and added; add subtitle file with a file, a language and a kind; remove for one that was added | approved |
| K.C17 | The files an extra can be taken in from | Server | `addExtra` takes a path the caller has to know; nothing lists what lies on the storage | katalog-manager answers `extraSources`: one level at a time, the folders an extra can be taken in from and their video files with their sizes (section An extra's file) | approved |
| K.C18 | extras | Catalog console | trailers lists links to online videos; a title's extras have no screen | Recommended: the tab extras of the section extras: the extras with kind, language, season, length and state; add extra with a file chosen on the storage the platform mounts, package again, package all again and remove; the other choice is an upload from the admin's computer, which needs a route that takes files of several gigabytes | approved |
| K.C19 | collections | Catalog console | none | the view collections and a collection's page of the section Collections: the table with name, titles, made by and changed; new collection; on the page edit, delete, artwork, the titles in order with move up, move down and remove, and add titles; a collection the catalog made says what a change does to it, and one made by hand can be handed back; what katalog-manager offers for collections is [the library](./library.md)'s | approved |
| K.C20 | libraries | Catalog console | none; the catalog scans one folder, the `media` folder of the platform's media volume | the view libraries and a library's page of the section Libraries: the table with name, kind, folders, titles, files gone, audience, scans and last scan; add library; on the page scan now, who sees it, read from portal-api's list of people, the fields name and scans, the folders with add folder and remove, the folder chooser of the mounted volumes one level at a time, which says why a folder can't be taken, the last scans, and delete with the titles moved; move on a title's tab details; what katalog-manager offers for libraries and their folders is [the library](./library.md)'s | approved |
| K.C21 | scans: every scan, by library | Catalog console | scan: trigger scan, and the last 25 scans with source, status, started, files, inserted and updated; a scan's error is not shown | the view scans of the section Scans: when, library, started by, state, added, changed, gone, passed over and took; the filters library, started by, state and changes; 50 rows at a time; scan now for one library or every library; the scans are [the library](./library.md)'s | approved |
| K.C22 | A scan's page | Catalog console | none; what a scan passed over is in the API alone | the page of the section A scan's page: the scan's files with what happened to each and the scan's own sentence for it; the tabs everything, added, changed, gone and passed over with their counts; the search; download CSV; a banner for files the scan did not list; open title, match by hand and describe by hand in a row's menu; the files are [the library](./library.md)'s | approved |
| K.C23 | The catalog's settings, named | Server | `settings` lists the rows someone created; `createSetting` takes any key and any value; nothing says which settings there are, what they take or their defaults | katalog-manager answers `knownSettings`, and takes `setSetting` and `resetSetting`, as the section Settings, named sets them out: the 43 settings with group, kind, limits, default and the value stored; a value outside the limits and an unknown key refused | approved |
| K.C24 | settings: one form | Catalog console, Docs | the four keys, then a table of the rows that exist, with new setting: a key typed by hand, a value, a type and a description; a setting nobody created is not shown | Recommended: the page of the section Settings: the keys as today; one form with a card for each group, each setting with its name, its sentence, its control, its default and reset; one save changes; the rows the catalog doesn't know listed with remove; no key is typed and none is made, where today any key can be; [extras](../../docs/extending/extras.md) then says to tick Extras from the folders; the other choice keeps the table of rows beside the form | approved |
| K.C25 | Loading and couldn't load, said by cause | Catalog console | every view but rules: a loader and “loading catalog…” at once; “error:” and the error as it came, in red, with no way to try again; “no items match.”, “item not found.” | the section States, in every view of this chapter: nothing for 0.4 seconds, then the data table's own line; the design system's empty states for nothing yet, no matches and couldn't load, the last with the reason by cause, try again and details, as the rules view has it; a list that couldn't be read again keeps its rows under a banner | approved |
| K.C26 | The catalog console in the person's language, and to WCAG 2.2 AA | Catalog console, Server | about 290 texts typed into its code, in English; numbers fixed to US English; katalog-manager writes each finding of the compliance check, each reason and each result of an action as an English sentence, 853 lines of wording, and the console shows those and the messages of its GraphQL errors as they come; no test draws a page: a harness started by hand | the section Language and accessibility, and ADR-0023: every text of the console from the message catalogue; the language the portal's shell hands it, on its own page the browser's, else English; katalog-manager gives each finding, reason and result a code and its values (`code`, `values`; in a GraphQL error `extensions.code` and `extensions.values`) and keeps its sentence as the detail, which the console shows under **details** and only for a code it doesn't know; the report as a CSV file is written in the language of the request (`Accept-Language`), from the same message catalogue; every view meets WCAG 2.2 AA, with the portal's test (H.C18) over every view and state | approved |
| K.C27 | A key for every genre | Server | a genre is a name in the one language the catalog reads its reference database in; a title's `genres` and `GET /api/v1/genres` are lists of names | katalog-manager keeps a key beside each genre's name, the reference database's own genre as lowercase words joined by hyphens (`science-fiction`); katalog-api and chino-api give the keys beside the names, in the same order (`genre_keys` on a title, `keys` in `GET /api/v1/genres`), and take a key as the filter (`genre_key`); an app names a key it knows from the message catalogue and shows the stored name for any other (ADR-0023, part 4) | approved |

## States

Every view of this chapter says where it stands in the same way, with the
design system's
[empty states](https://nalet.github.io/design-system/patterns/empty-states/)
and its
[loading and progress](https://nalet.github.io/design-system/patterns/loading-and-progress/),
as the rules view does today.

| State | What the view shows |
|---|---|
| Loading a list | nothing for the first 0.4 seconds; then the data table with its running line over an empty body, the heading and the filter bar in place. A screen reader hears once what loads: “Loading the titles” |
| Loading a page about one thing | nothing for 0.4 seconds; then the loader in the middle of the page with one line, “Loading the title” |
| Reading again | the rows stay, with the data table's line along its top |
| Reading again failed | the rows stay, under a warning banner: “Couldn't refresh the list; it shows what was loaded 5 minutes ago.”, with **try again** and the error under **details** |
| Nothing yet | the empty state of the kind empty, with the view's title, sentence and step of the section Words |
| No matches | the empty state of the kind no match: “no matches”, “Nothing in this list fits the search and filters.”, **clear filters** |
| Couldn't load | the empty state of the kind error: the view's title, “couldn't load the titles”; the reason by cause; **try again**; under **details** the status, “HTTP 502 Bad Gateway” |
| Couldn't load, the reasons | no answer: “Can't reach the server.” · the server ran into a problem: “The server ran into a problem.” · the server is busy: “The server is busy.” · the server didn't accept the request: “The server didn't accept the request. Check for an app update.” |
| Not there any more | on a page about one thing whose thing is gone: “this title isn't in the catalog anymore”, with **back**, which leads to its view |
| Not allowed | “you don't have access to this”, with **back** |
| Signed out | no state: the console sends the person to sign in and comes back to the same address (section The two apps and their views) |

| When | What happens |
|---|---|
| A form is saved with a mistake in it | each mistake stands at its field, with how to fix it; a banner over the form counts and names them, “2 settings need a fix: Originals deleted a minute and Rating countries.”; the focus goes to the first |
| A save fails | the fields keep what was typed, and an error banner over the form says what couldn't be saved, “Couldn't save the settings.”, “Couldn't save the details.”, “Couldn't save the library.”, “Couldn't save the collection.”, with the reason by cause, **try again** and **details** |
| A field can't be given back | enrichment could not be asked: the banner says “Couldn't save the details. Enrichment can't be asked now, so nothing was changed.” |
| An action of a row or a button fails | an error banner over the list or the tab: “Couldn't” and what was asked, as the section Words has it for each, with **details** and **dismiss** |
| The server refuses with a sentence of its own | a library's or a collection's name that is taken or too long, an interval out of its range, a collection that is full, a collection that can't be handed back, a library that can't be deleted: the console shows the server's sentence, at the field it is about, else in the dialog or in a banner ([the library](./library.md), section Words) |
| A picture is refused | the banner stands over the part it was uploaded to, and the picture in use stays: not a JPEG or PNG, “This file is not a JPEG or PNG picture.”; too large, “The picture is larger than 25 MB.”; not readable, “The picture can't be read. Save it again as JPEG or PNG.” |
| A subtitle file is refused | the dialog stays open, with the reason over its buttons: too large, “The file is larger than 5 MB.”, which the console checks before it sends the file; not UTF-8, “The file is not UTF-8 text. Save it as UTF-8.”; no cue, “The file holds no subtitle.”; a cue that ends before it starts, “A subtitle in the file ends before it starts.”; no version in the library, “This title has no version in the library yet. A subtitle can be added once it has one.”; there already, the dialog closes and the toast says “This subtitle is there already” |
| An extra is refused | the dialog stays open: the file is an extra already, “This file is an extra of Big Buck Bunny already.”; anything else, “Couldn't add the extra.”, with the server's reason under **details** |
| A folder can't be taken | in the folder chooser, the reason stands under the folder's name, in the server's sentence, “This folder is already in a library.”, and the chooser's button is closed while that folder is open. A refusal that comes only when the folder is added shows the server's sentence in a banner in the chooser, which stays open |
| The matches can't be asked | in the dialog match by hand: no key, “The catalog has no key for TMDB. Set one in catalog admin, under settings.”; no answer, “Can't reach TMDB.”, with **try again**; nothing found, “No match for “Big Buck Bunny” (2008). Change the words or the year, or give the id.” |
| The choices of a picture can't be asked | the picture in use and the pictures beside the files show, under a warning banner: “Couldn't ask TMDB for pictures.”, with **try again** |
| An export is refused | the dialog stays open, with the server's sentence over its buttons: “Two exports are running. Try again in a minute.” Where no answer comes at all, “Couldn't export the title.”, with the reason by cause and **details** |
| An export breaks off while it downloads | the browser says so in its own list of downloads, because the connection breaks and the file is never ended as if it were whole; the tab shows nothing, and **export as one file** starts a new one |
| The hold can't be changed | the switch goes back, under the banner “Couldn't change the hold.” |

## Words

Every text of the views this chapter changes. A name in the monospace face is
lowercase; a sentence has its full stop. An apostrophe in a text is the
typographic one, as the rules view writes it. A view this chapter leaves as
built keeps its words.

| Where | Text |
|---|---|
| The apps | the headings “catalog” · “catalog admin” · under them “Every title and its files” · “Scans, processing and rules” · in the top bar “/ catalog” · “/ catalog admin” |
| The tabs of catalog | “titles” · “collections” |
| The tabs of catalog admin | “scans” · “activity” · “processing” · “rules” · “libraries” · “settings” |
| The window's title | “titles · catalog · zaentrum” · “Big Buck Bunny · catalog · zaentrum” · “scans · catalog admin · zaentrum” |
| Every list | “clear all” · the count “2,644” · “312 of 2,644” · under the table “50 of 312” · “show 50 more” · “show 12 more” · “download CSV” · “Couldn't download the CSV.” · “filters” · “filters · 2” |
| titles, the filter bar | “search titles” · “type” · “all” · “movie” · “series” · “episode” · “album” · “genre” · “year” · “any” · “library” · “match” · “matched” · “not matched” · “by hand” · “has original” · “yes” · “no” · “file” · “gone” |
| titles, the columns | “title” · “type” · “year” · “library” · “match” · “has original” · “original” · “package” · “packaged” · “status” · “added” |
| titles, nothing yet | “no titles yet” · “The catalog lists a title for every movie and episode a scan takes in.” · “open scans” |
| A title's page, the head | “enrich” · “match by hand” · “package” · “Re-encode” · “validate” · “delete” |
| A title's page, the tabs | “details” · “episodes” · “artwork” · “files” · “subtitles” · “extras” · “trailers (2)” · “cast (14)” · “chapters (12)” · “tracks” · “segments (3)” · “steps (9)” · “diagnostics” |
| details, the fields | “Title” · “Sort title” · “How the title sorts in lists.” · “Original title” · “Year” · “Tagline” · “Description” · “Genres” · “New genres” · “Genres the catalog doesn't have yet, separated by commas.” · “Tags” · “Separated by commas.” · “Minimum age (years)” · “From 0 to 21. People with an age limit see the title only when their limit is at least this.” |
| details, a field's source | “by hand” · “files” · “enrichment” · “file name” · “use the catalog's value” · “The catalog's value after saving” |
| details, the age rating | “Rated 12 in DE, which means from 12 years.” · “Rated as its series: from 12 years.” · “No rating found in CH, DE, US.” |
| details, under the form | “runtime” · “external ids” · “library” · “added” · “move” · the dialog “move title” · “Library” · “cancel” · “move title” · “Moved to Kids” · “Couldn't move the title.” |
| details, the foot | “unsaved changes” · “cancel” · “save changes” · “Details saved” · “No changes to save” |
| details, the mistakes | “Give the title a name of 1 to 255 characters.” · “Use 255 characters at most.” · “Use a year from 1888 to 2100.” · “Use 20 genres at most, each of 80 characters at most.” · “Use a whole number from 0 to 21.” · “2 fields need a fix: Year and Minimum age (years).” |
| details, the banners | “This title is not matched.” · “match by hand” · “describe by hand” · “Saving keeps these details by hand. Enrichment won't look for a match again.” · “Described by hand. Enrichment doesn't look for a match.” · “Couldn't save the details.” · “Couldn't save the details. Enrichment can't be asked now, so nothing was changed.” |
| match by hand | the dialog's title “match by hand” · “Title” · “Year” · “search” · “Big Buck Bunny (2008)” · “TMDB 10378” · “TMDB id” · “Use it when the search doesn't find the title.” · “The match's genres, trailers and pictures replace this title's. What is kept by hand, or comes from the files beside the title, stays.” · “The series' episodes are matched again too.” · “cancel” · “match” · “Matched to Big Buck Bunny (2008)” · “No match for “Big Buck Bunny” (2008). Change the words or the year, or give the id.” · “The catalog has no key for TMDB. Set one in catalog admin, under settings.” · “Can't reach TMDB.” · “try again” · “Couldn't match the title.” |
| artwork | “poster” · “backdrop” · “in use” · “enrichment” · “files” · “uploaded” · “a frame of the file” · “1000 × 1500” · “use this” · “upload” · “A JPEG or PNG of 25 MB or less. A poster is upright, 2 : 3; a backdrop is wide, 16 : 9.” · “use the catalog's choice” · “This episode has no poster of its own and shows its series'.” · “This episode has no backdrop of its own and shows its series'.” |
| artwork, the toasts and banners | “Poster changed” · “Backdrop changed” · “Poster uploaded” · “Backdrop uploaded” · “Couldn't change the picture.” · “Couldn't ask TMDB for pictures.” · “This file is not a JPEG or PNG picture.” · “The picture is larger than 25 MB.” · “The picture can't be read. Save it again as JPEG or PNG.” |
| artwork, no other choice | “no other pictures” · “Enrichment and the title's folder have no other picture of this kind.” |
| files | “export as one file” · “Hold the original” · “While it is on, the catalog never deletes this title's original by itself, whatever the settings say.” · “While it is on, the catalog never deletes the originals of this series' episodes by itself, whatever the settings say.” · “Original held” · “Original not held” · “Couldn't change the hold.” · “originals” · “versions” · “files on disk” · “gone since 12 Nov 2026” · “beside the title” · the columns “file” · “gives” · “read” · “details” · “poster” · “backdrop” · “logo” · “The library keeps no record of this title's versions.” · “A series has no file of its own. Its episodes have theirs.” |
| files, the export | the dialog's title “export as one file” · “From” · “its package” · “its original” · “about 5.3 GB” · “1920 × 800 HEVC HDR10 · 2 audio tracks · 3 subtitles · 12 chapters” · “Not in this file: surround, lossless audio.” · “cancel” · “export” · “Couldn't export the title.” |
| files, the originals | the columns “file” · “size” · “state” · the states “kept” · “held” · “couldn't be deleted” · “replaced” · “waits for an admin” · “being deleted” · “deleted” · “removed” · the lines “Not deleted while the hold is on.” · “Another file took its place on 12 Nov 2026.” · “12 Nov 2026 · not in the package: surround, lossless audio” |
| files, the versions | the columns “made” · “state” · “id” · the states “being made” · “original only” · “not verified yet” · “verification failed” · “verified” · “replaced” · “removed” · the lines “No package. It plays from the original.” · “again in 6 h” · “12 Nov 2026 · every file” · “12 Nov 2026 · the records only” |
| What a package doesn't carry, and what a replaced original may lose | “more audio channels” (`maxAudioChannels`) · “surround” (`surround`) · “lossless audio” (`losslessAudio`) · “object audio” (`objectAudio`) · “HDR10 metadata” (`hdr10Metadata`) · “Dolby Vision” (`dolbyVision`) · “3D” (`stereo3d`) · “picture subtitles” (`imageSubtitles`) · “styled subtitles” (`styledSubtitles`) · “fonts” (`fonts`) · “closed captions” (`closedCaptions`) · “picture height” (`maxVideoHeight`) · “bit depth” (`videoBitDepth`) · “subtitle tracks” (`subtitleTracks`) · “commentary tracks” (`commentaryTracks`) · “commentary subtitles” (`commentarySubtitles`) · “audio description tracks” (`audioDescriptionTracks`) |
| subtitles | the columns “language” · “kind” · “format” · “from” · “added” · the kinds “full” · “foreign-language parts” · “CC” · from “the file” · “by hand” · “an addon” · “made (AI)” · “made (OCR)” · “German (de)” · “add subtitle file” · “remove” |
| subtitles, the dialogs | “add subtitle file” · “File” · “A .srt or .vtt file in UTF-8, 5 MB or less.” · “Language” · “another language…” · “Language tag” · “As en, de or zh-Hans.” · “Kind” · “cancel” · “add subtitle” · “Subtitle added” · “remove subtitle” · “German, by hand, stops showing in every app.” · “Subtitle removed” · “Couldn't remove the subtitle.” |
| subtitles, refused | “The file is larger than 5 MB.” · “The file is not UTF-8 text. Save it as UTF-8.” · “The file holds no subtitle.” · “A subtitle in the file ends before it starts.” · “This title has no version in the library yet. A subtitle can be added once it has one.” · “This subtitle is there already” · “Couldn't add the subtitle.” |
| subtitles, nothing yet | “no subtitles yet” · “Subtitles that come with the title's file, or that are added, are listed here.” · “add subtitle file” |
| extras | the columns “title” · “kind” · “language” · “season” · “length” · “state” · the kinds “trailer” · “teaser” · “featurette” · “behind the scenes” · “making of” · “deleted scene” · “interview” · “gag reel” · “short” · “other” · “specials” · the states “waiting” · “being packaged” · “ready” · “failed” · “file missing” · “Hidden until the file is back.” · “details” |
| extras, the actions | “add extra” · “package all again” · “package again” · “remove” · “Extra added” · “Extra queued to be packaged again” · “2 extras queued to be packaged again” · “Extra removed” · “Couldn't package the extra again.” · “Couldn't remove the extra.” |
| extras, the dialogs | “add extra” · “File” · “choose file” · “choose this file” · “Kind” · “Title” · “Left empty, it is named after its kind.” · “Language” · “not set” · “Season” · “the whole series” · “season 1” · “specials” · “cancel” · “add extra” · “remove extra” · “It stops playing at once. Its file stays where it is, and its package is deleted a day later.” · “This file is an extra of Big Buck Bunny already.” · “Couldn't add the extra.” |
| extras, nothing yet | “no extras yet” · “A title's trailers and other extras are listed here.” · “add extra” |
| collections, the view | “collections” · “search collections” · “made by” · “all” · “the catalog” · “by hand” · the columns “name” · “titles” · “made by” · “changed” · “new collection” |
| collections, the dialogs | “new collection” · “Name” · “Description” · “cancel” · “create collection” · “Collection created” · “edit” · “save changes” · “Collection saved” · “delete” · “delete collection” · “The collection goes. Its titles stay in the library.” · “Collection deleted” · “Couldn't create the collection.” · “Couldn't save the collection.” · “Couldn't delete the collection.” |
| A collection's page | “The catalog made this collection and keeps it up to date. A change to its name, its description or its titles makes it a collection by hand, which the catalog leaves as it is.” · “hand back to the catalog” · “The catalog sets this collection's name, description and titles again. The changes made by hand to them go.” · “hand back” · “Collection handed back” · “artwork” · “titles” · the columns “#” · “title” · “type” · “year” · “move up” · “move down” · “remove” · “add titles” · “search titles” · “in the collection” · “add 3 titles” · “add 1 title” · “3 titles added” · “1 title added” · “1 title removed” · “Couldn't change the collection.” |
| collections, the mistakes | the server's sentences ([the library](./library.md), section Words): “Give the collection a name of 1 to 120 characters.” · “A collection with this name already exists. Choose another name.” · “A description has 2,000 characters at most.” · “A collection holds 500 titles at most.” · “Only a collection the catalog made from a series of films can be handed back.” |
| collections, nothing yet | the view: “no collections yet” · “The catalog makes a collection where movies belong to one series of movies. Make one by hand for anything else.” · “new collection” · a page: “no titles yet” · “Add the titles that belong together.” · “add titles” |
| libraries, the view | “libraries” · the columns “name” · “kind” · “folders” · “titles” · “files gone” · “audience” · “scans” · “last scan” · “movies” · “shows” · “1 unavailable” · “everyone” · “3 of 5 people” · “1 of 5 people” · “when files change” · “every hour” · “every 6 hours” · “every 30 minutes” · “every 2 days” · “only by hand” · “running” · “add library” |
| A library's page and add library | “scan now” · “Scan started” · “A scan is running.” · “open it” · “Name” · “Kind” · “Folder” · “choose folder” · “Everyone who signs in sees this library's titles.” · “3 of 5 people see this library's titles: Alex, Mia and Sam.” · “1 of 5 people sees this library's titles: Mia.” · “and 4 more” · “change in people” · “Scans” · “when files change” · “on a schedule” · “only by hand” · “Every” · “minutes” · “hours” · “days” · “The library is scanned when its files change, and in full every night.” · “The library is scanned in full at this interval.” · “The library is scanned only when someone starts a scan.” · “cancel” · “save changes” · “add library” · “Library added” · “Library saved” · “Couldn't add the library.” · “Couldn't save the library.” |
| A library's page, the folders | “folders” · the columns “folder” · “titles” · “default folder” · “unavailable” · “add folder” · “remove” · the chooser “add folder” · “choose folder” · “212 more folders are not listed.” · “Move the titles already taken in from this folder to this library” · “add this folder” · “choose this folder” · “cancel” · “Folder added” · “Couldn't add the folder.” · “remove folder” · “The catalog stops looking in this folder. The titles it took in from it stay in the library, and no file is deleted.” · “Folder removed” · “Couldn't remove the folder.” · “last scans” · “every scan of this library” |
| A library's page, delete | “delete” · “delete library” · “The library goes. Its folders are free again, and no file is deleted.” · “Move its titles to” · “Its 412 titles move to the library chosen. Its folders are free again, and no file is deleted.” · “Its 1 title moves to the library chosen. Its folders are free again, and no file is deleted.” · “cancel” · “Library deleted” · “Couldn't delete the library.” |
| libraries, the mistakes | the server's sentences for a name and an interval ([the library](./library.md), section Words): “Give the library a name of 1 to 60 characters.” · “A library with this name already exists. Choose another name.” · “Use an interval from 1 minute to 7 days.” |
| libraries, nothing yet | “no libraries yet” · “A library is a set of folders that hold movies or shows. Add one to take its files in.” · “add library” |
| scans, the view | “scans” · the filters “library” · “started by” · “all” · “an admin” · “the schedule” · “a file change” · “state” · “running” · “done” · “failed” · “changes” · “with changes” · the columns “when” · “library” · “started by” · “state” · “added” · “changed” · “gone” · “passed over” · “took” · what started a scan, in the server's words · “42 s” · “3 min” · “scan now” · “every library” · “Scan started” · “3 scans started” · “Couldn't start the scan.” |
| scans, nothing yet | “no scans yet” · “A scan reads a library's folders for new, changed and missing files.” · “scan now” |
| A scan's page | “scan of Movies” · “12 Nov 2026, 14:00 · started by the schedule · a full scan · took 42 s” · “started by Alex Urban” · “started by a file change” · “a full scan” · “the changed files” · “Scanning…” · “This scan found 12,400 more files than it lists.” · the tabs “everything” · “added” · “changed” · “gone” · “passed over” · “search files” · the columns “file” · “what happened” · “title” · “match” · the sentence under what happened, in the server's words · “open title” · “match by hand” · “describe by hand” |
| A scan's page, nothing to list | “nothing changed” · “This scan found every file as the last scan left it.” · on a tab: “nothing added” · “nothing changed” · “nothing gone” · “nothing passed over” |
| settings, the page | “settings” · the groups “keys” · “scanning” · “age ratings” · “languages and sound” · “originals” · “processing again” · “rules check” · “chapters” · “picture areas” · “file check” · “other settings” · “Default: 24 hours.” · “Default: off.” · “reset” · “unsaved changes” · “cancel” · “save changes” · “Settings saved” · “No changes to save” · “Couldn't save the settings.” |
| settings, the keys | “set” · “not set” · “clear” · “A key is never shown again once it is set.” · “Not set. The key this installation was given is used, where it has one.” · “TMDB key set” · “TMDB key cleared” · “TMDB doesn't take this key. It was not stored.” |
| settings, the controls | “any time” · “between” · “and” · “off” · “at” · “lifted to” · “LUFS” · “seconds” · “minutes” · “hours” · “days” · the names, the values and the sentences of the table in the section Settings |
| settings, the mistakes | “Use a whole number of 1 or more.” · “Use a whole number of 0 or more.” · “Use a whole number from 1 to 64.” · “Use a number from −35 to −10.” · “Use a time such as 22:00.” · “Use two-letter country codes from the list, separated by commas.” · “Use language codes of two or three letters, separated by commas.” · “Use language tags such as en, de or zh-Hans, separated by commas.” · “2 settings need a fix: Originals deleted a minute and Rating countries.” · “The stored value “abc” can't be read, so the default is in force.” |
| settings, deleting originals | “delete originals after packaging” · “From now on the catalog deletes a title's original once its package is verified and lacks nothing the rules keep. A deleted original can't be brought back once its time in the trash is over.” · “cancel” · “delete originals” · “No original is deleted while the library's layout is legacy.” |
| settings, the rows the catalog doesn't know | “The catalog doesn't know these settings. They have no effect.” · the columns “key” · “value” · “remove” · “Setting removed” |
| Couldn't load, in every view | the titles “couldn't load the titles” · “couldn't load the title” · “couldn't load the collections” · “couldn't load the collection” · “couldn't load the libraries” · “couldn't load the library” · “couldn't load the scans” · “couldn't load the scan” · “couldn't load the settings” · the reasons “Can't reach the server.” · “The server ran into a problem.” · “The server is busy.” · “The server didn't accept the request. Check for an app update.” · “try again” · “details” · “HTTP 502 Bad Gateway” · “you don't have access to this” · “back” · “Couldn't refresh the list; it shows what was loaded 5 minutes ago.” · “dismiss” |
| Not there any more | “this title isn't in the catalog anymore” · “this collection isn't in the catalog anymore” · “this library isn't in the catalog anymore” · “this scan isn't kept anymore” · “back” |
| No matches, in every list | “no matches” · “Nothing in this list fits the search and filters.” · “clear filters” |
| Loading: the line under a page's loader, and what a screen reader hears | “Loading the titles” · “Loading the title” · “Loading the collections” · “Loading the collection” · “Loading the libraries” · “Loading the library” · “Loading the scans” · “Loading the scan” · “Loading the settings” |
| The Tab key's first stop | “skip to content” |
