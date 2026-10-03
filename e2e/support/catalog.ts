// chino-api's wire shapes as the web client reads them today, and lookups
// that turn the data set's names (data/catalog.ts) into this instance's ids.
import type { TitleRef } from '../data/catalog';
import { env } from './env';
import type { Api } from './fixtures';

export interface CastEntry {
  person_id?: string;
  name: string;
  role: string;
  // The next backend round (see tests/api/next-contract.spec.ts):
  job?: string;
  character?: string;
  order?: number;
  episode_count?: number;
}

export interface Item {
  id: string;
  type: string;
  title: string;
  year?: number;
  poster_url?: string;
  backdrop_url?: string;
  cast?: CastEntry[];
  roles?: string[]; // next round: the person's roles on a filmography item
}

export interface PersonSummary {
  id: string;
  name: string;
  credits?: number;
  has_profile?: boolean; // next round
}

export interface PersonDetail {
  id: string;
  name: string;
  items: Item[];
  // The next backend round:
  biography?: string;
  birth_date?: string;
  birthplace?: string;
  has_profile?: boolean;
  profile_url?: string;
}

export interface Season {
  season: number;
  episodes: (Item & { episode_number?: number; season_number?: number })[];
}

/** Find a title of the data set in this instance's catalog. */
export async function findTitle(api: Api, ref: TitleRef): Promise<Item> {
  const q = new URLSearchParams({ q: ref.title, type: ref.type, limit: '50' });
  const { items } = await api.json<{ items: Item[] }>(`/api/v1/items?${q}`);
  const hit = items.find((it) => it.title === ref.title && it.year === ref.year);
  if (!hit) {
    throw new Error(`${ref.type} "${ref.title}" (${ref.year}) is not in the catalog of ${env.baseURL}`);
  }
  return hit;
}

/** A title's detail record: GET /api/v1/items/{id}, the call the detail page makes. */
export async function titleDetail(api: Api, ref: TitleRef): Promise<Item> {
  const { id } = await findTitle(api, ref);
  return api.json<Item>(`/api/v1/items/${id}`);
}

/** Find a person by their full name through the people search. */
export async function findPerson(api: Api, name: string): Promise<PersonSummary> {
  const { people } = await api.json<{ people: PersonSummary[] }>(
    `/api/v1/people?${new URLSearchParams({ q: name, limit: '50' })}`,
  );
  const hit = people.find((p) => p.name === name);
  if (!hit) throw new Error(`no person named "${name}" in the catalog of ${env.baseURL}`);
  return hit;
}

/** A person's record: GET /api/v1/people/{id}, the call the person page makes. */
export async function personDetail(api: Api, name: string): Promise<PersonDetail> {
  const { id } = await findPerson(api, name);
  return api.json<PersonDetail>(`/api/v1/people/${id}`);
}
