// The data set the suite relies on, in one place: open-licensed titles the
// public demo seeds into its library, and what TMDB publishes about them.
//
// Checked against the live demo's API on 2026-10-03; tests/api/catalog-data.spec.ts
// checks the parts the catalog serves today on every run, so a changed library
// shows up there first, by name, instead of as a mystery in a UI test.
//
// Ids are not kept here: they belong to one catalog. Tests look titles and
// people up by name at run time (support/catalog.ts), so the same suite runs
// against any instance holding the same titles.

export type TitleType = 'movie' | 'series';

export interface TitleRef {
  title: string;
  year: number;
  type: TitleType;
}

/** Sintel (2010), TMDB movie 45745: two actors and a director today; TMDB
 *  also credits a writer, a producer and the music. */
export const SINTEL = {
  title: 'Sintel',
  year: 2010,
  type: 'movie',
  tmdbId: 45745,
  actors: ['Halina Reijn', 'Thom Hoffman'],
  directors: ['Colin Levy'],
  /** Crew roles TMDB lists beyond the director (the next backend round). */
  crewRoles: ['director', 'writer', 'producer', 'composer'],
} as const;

/** Agent 327: Operation Barbershop (2017): shares its director and an actor with Sintel. */
export const AGENT_327 = {
  title: 'Agent 327: Operation Barbershop',
  year: 2017,
  type: 'movie',
} as const;

/** Tears of Steel (2012): more actors (seven) than the five the detail page shows. */
export const TEARS_OF_STEEL = {
  title: 'Tears of Steel',
  year: 2012,
  type: 'movie',
  directors: ['Ian Hubert'],
} as const;

/** Spring (2019): directed by Andreas Goralczyk. */
export const SPRING = {
  title: 'Spring',
  year: 2019,
  type: 'movie',
  directors: ['Andreas Goralczyk'],
} as const;

/** HERO (2018): directed by Daniel Martínez Lara — a name with an accent. */
export const HERO = {
  title: 'HERO',
  year: 2018,
  type: 'movie',
  directors: ['Daniel Martínez Lara'],
} as const;

/** Pioneer One (2010), TMDB tv 33050: one season of six episodes, created by
 *  Josh Bernhard; five lead actors, each in all six episodes. (Credits taken
 *  from every episode may add guest actors after them.) */
export const PIONEER_ONE = {
  title: 'Pioneer One',
  year: 2010,
  type: 'series',
  tmdbId: 33050,
  creator: 'Josh Bernhard',
  /** The lead actors, in TMDB's billing order. */
  actors: ['Alexandra Blatt', 'Laura Graham', 'James Rich', 'Einar Gunn', 'Jack Haley'],
  actorEpisodeCount: 6,
  seasons: [
    {
      season: 1,
      episodes: [
        'Earthfall',
        'The Man From Mars',
        'Alone in the Night',
        'Triangular Diplomacy',
        'Sea Change',
        'War of the World',
      ],
    },
  ],
} as const;

/** The titles a browse page must show with their posters. */
export const BROWSE_MOVIES = [SINTEL, TEARS_OF_STEEL, SPRING, HERO] as const;

/** A director credited on two titles of the data set. */
export const DIRECTOR = {
  name: 'Colin Levy',
  titles: [SINTEL, AGENT_327],
} as const;

/** An actor credited on two titles of the data set, whose catalog record
 *  has a birth date, a birthplace and a biography. */
export const ACTOR = {
  name: 'Thom Hoffman',
  /** What a viewer would type: part of the name, lower case. */
  search: 'hoffman',
  titles: [SINTEL, AGENT_327],
  birthDate: '1957-03-03',
  birthplace: 'Wassenaar, Zuid-Holland, Netherlands',
  biographyExcerpt: 'Dutch film and television actor',
} as const;

/** A person found by a query without the accent their name carries. */
export const ACCENTED = {
  name: 'Daniel Martínez Lara',
  search: 'martinez',
  title: HERO,
} as const;
