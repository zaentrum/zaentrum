# Capabilities

What zaentrum does, for whom, and where: every capability of the platform, which
app or console offers it today, what in the code serves it, the settings that
govern it, and where this specification describes it. It is the first layer of
the specification. The chapters of [chino](../chino/README.md) and the
[portal](../portal/README.md) say how a capability looks and behaves; this layer
says that it exists, and keeps the list complete.

On the site the model is also a [map](https://zaentrum.github.io/spec/capabilities/map/):
a lane for each part, a cluster for each area, a tile for each capability, coloured
by where it is built, whether this specification describes it, the requirements open
on it, or whether its values can be set. Each tile opens the capability's fact sheet:
its requirements (the numbered changes that name it, with today and the target), the
sections that specify it, the screens and interfaces in the code that serve it, and
its settings.

> **A model, checked against the code.** The capabilities and their settings are
> data, written by hand; what the code offers is listed from the main branch of
> every repository by a program. A check fails when the code offers something no
> capability claims, when a reference into the specification leads nowhere, or
> when a table on these pages is not what the data says. The numbers here are
> computed, never typed.
>
> **And against what is expected of it.** The code can only say what is there.
> What a media server is expected to do, and zaentrum doesn't, is kept as a list of
> [expectations](./expectations.md): each names the capabilities that meet it, and
> a capability nothing serves yet is in the model because an expectation or a
> numbered change names it.

## How to read it

A **capability** is something someone can do with the platform, or something the
platform does for them, at the grain where an app either has it or hasn't:
“Resume a title where it stopped”, “Sign in on a TV with a code”, “Invite a
person”, “Retire an original once its package is verified”. A screen is not a
capability; it is where one is offered. A route of an API is not one either; it
is what serves one. A setting is a row of [configuration](./configuration.md).

**Who** it is for:

| Who | Is |
|---|---|
| person | someone watching, in a chino app |
| admin | someone with the admin role, in the portal or a console |
| operator | whoever installs and runs the platform: the operator's resources, the CLI |
| addon | an addon's own service account |
| system | the platform itself, when nobody asks |

**Where it is today**, for each chino app (web, phone, Android TV, Samsung TV) and
each face of the platform (the portal, the catalog console, the `zae` CLI, the
operator's resources), as deployed:

| Value | Means |
|---|---|
| built | there, as the specification's “As deployed” describes it |
| partial | there, with the gap its note names |
| no | not there today |
| — | not meant for it: a TV keeps no downloads |
| ? | not checked yet |

**Served by** names the routes, GraphQL operations, CLI commands and resource
fields that serve it, as the [inventory](./inventory.csv) lists them. **Spec**
names the chapter and section that describe it; a dash means the specification
doesn't describe it yet. **Changes** names the specification's numbered changes
that touch it.

A capability **nothing serves** is one no app or face has, with no screen, route,
command, field or setting of its own: the platform doesn't do it at all. It is
“no” wherever it would be meant, and it is in the model only because a numbered
change or an [expectation](./expectations.md) names it. That is different from
a “no” beside something the platform does: “Retire an original once its package
is verified” is the platform's own work, with its settings, and “no” only in the
catalog console, which doesn't offer it.

## Areas, depth and keys

Capabilities are grouped in areas, the areas in parts: chino, the portal, the
catalog and the pipeline, the platform. Only a capability is counted, linked and
checked; an area is a heading. A part is where a capability is built; what it
is there for is its area's **goal**, one of the goals of
[what zaentrum is for](../goals/README.md). Each area says how deep it is modelled:

| Depth | Means |
|---|---|
| deep | every capability is described screen by screen in a chapter |
| working | every capability is named and served; described where something depends on it |
| stub | a heading, so that the model isn't silent about a product that is only registered, or only expected |

A capability's key, such as `resume-title`, is short and stable: it says what the
capability does, not where it sits, so it doesn't change when an area or a wording
does. Chapters and changes refer to capabilities by their keys.

## The files

| File | Written by | Holds |
|---|---|---|
| [areas.csv](./areas.csv) | hand | the areas: part, goal, depth, chapter |
| [capabilities.csv](./capabilities.csv) | hand | one row a capability |
| [settings.csv](./settings.csv) | hand | one row a setting |
| [expectations.csv](./expectations.csv) | hand | one row a thing people expect of a media server: the capabilities and components that meet it, or the decision record that rules it out |
| [inventory.csv](./inventory.csv) | `scripts/inventory.py` | what the code offers, one row a route, operation, screen, tab, command, field, environment variable, catalog setting or constant |
| the tables of these pages | `scripts/capabilities.py` | never edited by hand |

To change the model, edit the CSV files and run `python3 scripts/capabilities.py`,
which checks them and writes the tables. To list the code again, run
`python3 scripts/inventory.py --src <a folder of clones> --fetch`. The site's map and
fact sheets are built from `python3 scripts/capabilities.py --json <file>`: the same
model, each reference, change and id resolved, written by the same program.

## What is checked

`scripts/capabilities.py --check` runs in docs-check and fails when:

- a route, GraphQL operation, screen, tab or CLI command of the inventory has no
  capability, or a resource field, environment variable or catalog setting has no
  setting, or more than one;
- an id in the model is not in the inventory, or a key is not in the model;
- a reference into the specification leads to no page or heading, or a change
  named is no numbered change of the specification;
- an expectation names no capability, no component and no decision record, or
  one that doesn't exist;
- an area or an expectation is for no goal of [goals.csv](../goals/goals.csv);
- a capability nothing serves is named by no change and no expectation;
- a value is none of those the model allows;
- a table on these pages is not what the data says.

## The state of the model

<!-- generated: overview -->
| Part | Capabilities | In a chapter | Only in the docs | Nowhere | With a change | Served by nothing |
|---|---|---|---|---|---|---|
| [chino](./chino.md) | 142 | 124 | 5 | 13 | 122 | 13 |
| [the portal](./portal.md) | 54 | 22 | 13 | 19 | 10 | 13 |
| [the catalog and the pipeline](./catalog.md) | 50 | 8 | 23 | 19 | 3 | 10 |
| [the platform](./platform.md) | 24 | 0 | 19 | 5 | 0 | 5 |
| [later products](./platform.md) | 3 | 2 | 0 | 1 | 2 | 1 |
| all | 273 | 156 | 60 | 57 | 137 | 42 |

| App or face | built | partial | no | — | ? |
|---|---|---|---|---|---|
| Web | 84 | 14 | 18 | 155 | 2 |
| Phone | 77 | 32 | 24 | 138 | 2 |
| Android TV | 79 | 20 | 21 | 151 | 2 |
| Samsung TV | 44 | 30 | 46 | 151 | 2 |
| Portal | 37 | 7 | 35 | 194 | 0 |
| Catalog console | 14 | 7 | 22 | 230 | 0 |
| CLI | 21 | 2 | 42 | 208 | 0 |
| Resource | 30 | 1 | 7 | 235 | 0 |

| Numbered changes | Named by a capability | Not yet | Proposed | Approved | Built | Verified |
|---|---|---|---|---|---|---|
| 288 | 275 | 13 | 285 | 3 | 0 | 0 |
<!-- end: overview -->

## What is expected of it

What people expect of a media server they run themselves, goal by goal, and
what the model says of each: [expectations](./expectations.md) has every one with
the capabilities that meet it. An expectation is **there** when every capability
and component it names is built, **partly** when some are, **not there** when
none is, **not checked** when none was looked at, and **decided otherwise** when
a decision record rules it out.

<!-- generated: expected -->
| Expected, for the goal | Expectations | there | partly | not there | not checked | decided otherwise |
|---|---|---|---|---|---|---|
| [Watch films and shows](./expectations.md#watch-films-and-shows) | 14 | 0 | 9 | 4 | 1 | 0 |
| [Listen to music](./expectations.md#listen-to-music) | 1 | 0 | 0 | 1 | 0 | 0 |
| [Watch live channels](./expectations.md#watch-live-channels) | 1 | 0 | 0 | 1 | 0 | 0 |
| [Listen to books and podcasts](./expectations.md#listen-to-books-and-podcasts) | 1 | 0 | 0 | 1 | 0 | 0 |
| [Keep the library](./expectations.md#keep-the-library) | 12 | 1 | 5 | 5 | 0 | 1 |
| [Share it with a household](./expectations.md#share-it-with-a-household) | 11 | 1 | 5 | 5 | 0 | 0 |
| [Run it oneself](./expectations.md#run-it-oneself) | 12 | 2 | 6 | 4 | 0 | 0 |
| [Make it one's own](./expectations.md#make-it-ones-own) | 4 | 2 | 1 | 1 | 0 | 0 |
| all | 56 | 6 | 26 | 22 | 1 | 1 |

Nothing serves 42 of the 273 capabilities yet: no app or face has them, and no screen, route, command, field or setting is theirs.
<!-- end: expected -->

## What the code offers

<!-- generated: inventory -->
| What the code offers | Rows | Claimed by |  |
|---|---|---|---|
| HTTP routes | 298 | a capability |  |
| GraphQL operations | 71 | a capability |  |
| screens | 86 | a capability |  |
| tabs | 24 | a capability |  |
| CLI commands | 30 | a capability |  |
| fields of the operator's resources | 87 | a setting |  |
| environment variables | 280 | a setting |  |
| the catalog's settings | 41 | a setting |  |
| constants in the code | 858 | listed | 279 in a setting |

From the main branch of 31 repositories, as [inventory-sources.csv](./inventory-sources.csv) names them.
<!-- end: inventory -->

Constants are listed, not claimed: the ones a person notices, or that an admin
might want to change, are settings with “Where” code; the rest are the code's own.
The inventory also lists what the operator's chart runs, how it sets each part up,
and the organisation's repositories: the [architecture](../architecture/README.md)
claims those.

## Pages

| Page | Covers |
|---|---|
| [the map](https://zaentrum.github.io/spec/capabilities/map/) | every capability as a tile, by part and area, and its fact sheet (on the site only) |
| [chino](./chino.md) | the apps for watching, chapter by chapter |
| [the portal](./portal.md) | the portal's home, its registry, addons, people, running the platform |
| [the catalog and the pipeline](./catalog.md) | the catalog, the library and its originals, preparing titles |
| [the platform](./platform.md) | installing and configuring; the products that are only registered, or only expected |
| [expectations](./expectations.md) | what people expect of a media server, and what of it is there |
| [configuration](./configuration.md) | every setting: who changes it, where, its default, a proposal |
