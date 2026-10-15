# Holdings — what the library holds, by identity

An addon thinks in the identities titles have outside any one library — a
TMDB, TVDB or IMDb id — and needs to know what the library holds of them. The
read side, katalog-api, answers by those identities
([ADR-0012](../adr/0012-catalog-identity-for-addons.md)), so an addon follows
the library without a copy of the catalog and without keeping catalog ids.

The holdings say what the library **holds**, never what anyone wants. Deciding
what is missing is the addon's.

```
GET http://katalog-api/api/v1/holdings?type=series&tmdb=97546
Authorization: Bearer <service token>          # see identity.md
```

## A series

`type=series` with one of `tmdb`, `tvdb` or `imdb` answers the series that
carries the identity, season by season:

```json
{"seriesId": "3f6b2c1e-…", "title": "Some Show", "year": 2020,
 "externalIds": {"imdb": "tt9208876", "tmdb": "97546", "tvdb": "362392"},
 "seasons": [
   {"season": 1, "episodes": [
     {"episode": 1, "itemId": "7d6c5b4a-…", "hasFile": true, "playable": false, "coveredBy": null},
     {"episode": 9, "itemId": "a1b2c3d4-…", "hasFile": true, "playable": true, "coveredBy": null},
     {"episode": 10, "itemId": "0c9d8e7f-…", "hasFile": true, "playable": true, "coveredBy": "a1b2c3d4-…"}]}]}
```

- Seasons come in order, the specials (`0`) among them; each holds the
  episodes the catalog has of it, in episode order.
- `hasFile`: the catalog records a file for the episode — the one it was taken
  in from, or its package.
- `playable`: the episode is packaged and plays.
- An episode another's file covers (one file of several episodes — see
  [ingest](./ingest.md#by-identity)) names that episode in `coveredBy`, and
  is held as it is: its `hasFile` and `playable` are the holder's.

## A movie

`type=movie` with `tmdb` or `imdb`:

```json
{"itemId": "f001aeff-…", "title": "Some Film", "year": 2024,
 "externalIds": {"imdb": "tt0004711", "tmdb": "4711"}, "hasFile": true, "playable": true}
```

## Every title, paged

`type=series` or `type=movie` alone pages every title of the type, with its
identities:

```json
{"items": [
   {"itemId": "3f6b2c1e-…", "title": "Some Show", "year": 2020,
    "externalIds": {"imdb": "tt9208876", "tmdb": "97546", "tvdb": "362392"}, "heldEpisodes": 4}],
 "page": 1, "pageSize": 200, "total": 2}
```

- In id order, which renaming a title does not change. `page` from 1,
  `pageSize` 200 unless asked, at most 1000.
- A title the catalog keeps no identity of is listed with `externalIds: {}`:
  until enrichment gives it one, no lookup by identity finds it.
- `heldEpisodes`, on a series: how many of its episodes have a file.

## The rules

- One identity is enough; one that no title carries does not keep the others
  from finding it. Identities that name different titles are 400.
- A TMDB id names a title with its type: TMDB numbers films and shows apart.
- A title the catalog holds twice (two series of one show) is answered as one:
  a series as the first made, with the episodes of each — the series an
  [ingest by identity](./ingest.md#by-identity) adds to.
- 404 says which identities no title of the type carries; 400 says why a
  request cannot be answered (no or another `type`, a malformed id, a
  parameter the holdings do not take, a page past the last). 503 while the
  read side cannot read the identities — never an answer that nothing is
  held.
- Every item the read side serves carries `externalIds` too, so a title met
  anywhere — a list, a search, a series' episodes — says what it is.

## Who may read them

Whoever reads the catalog: a signed-in person, or an addon's service account
whose tokens carry the instance's audience ([identity](./identity.md)). The
holdings are the library's, not a viewer's: no rating cap filters them, so a
request capped at an age is refused them (403).

To learn about changes without asking, consume the catalog's item events
([events](./events.md)): `discovered`, `packaged` and `removed` name the
item's identities beside its catalog id.
