# Capabilities

What zaentrum does, for whom, and where: every capability of the platform, which
app or console offers it today, what in the code serves it, the settings that
govern it, and where this specification describes it. It is the first layer of
the specification. The chapters of [chino](../chino/README.md) and the
[portal](../portal/README.md) say how a capability looks and behaves; this layer
says that it exists, and keeps the list complete.

> **A model, checked against the code.** The capabilities and their settings are
> data, written by hand; what the code offers is listed from the main branch of
> every repository by a program. A check fails when the code offers something no
> capability claims, when a reference into the specification leads nowhere, or
> when a table on these pages is not what the data says. The numbers here are
> computed, never typed.

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

## Areas, depth and keys

Capabilities are grouped in areas, the areas in parts: chino, the portal, the
catalog and the pipeline, the platform. Only a capability is counted, linked and
checked; an area is a heading. Each area says how deep it is modelled:

| Depth | Means |
|---|---|
| deep | every capability is described screen by screen in a chapter |
| working | every capability is named and served; described where something depends on it |
| stub | a heading, so that the model isn't silent about a product that is only registered |

A capability's key, such as `resume-title`, is short and stable: it says what the
capability does, not where it sits, so it doesn't change when an area or a wording
does. Chapters and changes refer to capabilities by their keys.

## The files

| File | Written by | Holds |
|---|---|---|
| [areas.csv](./areas.csv) | hand | the areas: part, depth, chapter |
| [capabilities.csv](./capabilities.csv) | hand | one row a capability |
| [settings.csv](./settings.csv) | hand | one row a setting |
| [inventory.csv](./inventory.csv) | `scripts/inventory.py` | what the code offers, one row a route, operation, screen, tab, command, field, environment variable, catalog setting or constant |
| the tables of these pages | `scripts/capabilities.py` | never edited by hand |

To change the model, edit the CSV files and run `python3 scripts/capabilities.py`,
which checks them and writes the tables. To list the code again, run
`python3 scripts/inventory.py --src <a folder of clones> --fetch`.

## What is checked

`scripts/capabilities.py --check` runs in docs-check and fails when:

- a route, GraphQL operation, screen, tab or CLI command of the inventory has no
  capability, or a resource field, environment variable or catalog setting has no
  setting, or more than one;
- an id in the model is not in the inventory, or a key is not in the model;
- a reference into the specification leads to no page or heading, or a change
  named is no numbered change of the specification;
- a value is none of those the model allows;
- a table on these pages is not what the data says.

## The state of the model

<!-- generated: overview -->
| Part | Capabilities | In a chapter | Only in the docs | Nowhere | With a change |
|---|---|---|---|---|---|
| [chino](./chino.md) | 129 | 124 | 0 | 5 | 122 |
| [the portal](./portal.md) | 41 | 22 | 9 | 10 | 10 |
| [the catalog and the pipeline](./catalog.md) | 40 | 8 | 20 | 12 | 3 |
| [the platform](./platform.md) | 18 | 0 | 15 | 3 | 0 |
| [later products](./platform.md) | 2 | 2 | 0 | 0 | 2 |
| all | 230 | 156 | 44 | 30 | 137 |

| App or face | built | partial | no | — | ? |
|---|---|---|---|---|---|
| Web | 84 | 14 | 11 | 121 | 0 |
| Phone | 77 | 32 | 13 | 108 | 0 |
| Android TV | 79 | 20 | 13 | 118 | 0 |
| Samsung TV | 44 | 30 | 38 | 118 | 0 |
| Portal | 37 | 7 | 14 | 172 | 0 |
| Catalog console | 14 | 7 | 12 | 197 | 0 |
| CLI | 21 | 2 | 27 | 180 | 0 |
| Resource | 29 | 1 | 1 | 199 | 0 |

| Numbered changes | Named by a capability | Not yet | Proposed | Approved | Built | Verified |
|---|---|---|---|---|---|---|
| 288 | 275 | 13 | 285 | 3 | 0 | 0 |
<!-- end: overview -->

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
| environment variables | 278 | a setting |  |
| the catalog's settings | 41 | a setting |  |
| constants in the code | 858 | listed | 279 in a setting |

From the main branch of 18 repositories, as [inventory-sources.csv](./inventory-sources.csv) names them.
<!-- end: inventory -->

Constants are listed, not claimed: the ones a person notices, or that an admin
might want to change, are settings with “Where” code; the rest are the code's own.

## Pages

| Page | Covers |
|---|---|
| [chino](./chino.md) | the apps for watching, chapter by chapter |
| [the portal](./portal.md) | the portal's home, its registry, addons, people, running the platform |
| [the catalog and the pipeline](./catalog.md) | the catalog, the library and its originals, preparing titles |
| [the platform](./platform.md) | installing and configuring; the products that are only registered |
| [configuration](./configuration.md) | every setting: who changes it, where, its default, a proposal |
