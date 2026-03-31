---
title: Campaign Progression
slug: ''
parent: ''
sort_order: 100
tags:
  - Campaign
status: draft
last-updated: 2026-03-31
---

***

title: "Campaign Progression"
tags: ["design", "systems", "progression", "campaign"]
status: draft
last-updated: 2026-03-30
sort_order: 4

***

## Overview

Campaign progression in _Nexus: Echoes of Empire_ operates on two levels:
**unit-level growth** (XP, abilities, stats) and **campaign-level resources**
(reinforcements, faction-specific currencies). Both layers are designed to
reinforce each faction's identity — progression should feel as distinct as
the factions themselves.

> **Design Principle:** Progression is not cosmetic. A Harmonist army at
> Mission 12 should play fundamentally differently from a Harmonist army at
> Mission 1 — not just stronger, but structurally more capable of
> coordination.

***

## Unit Persistence

Units that survive a mission carry forward into the next with full XP and
unlocked abilities intact. Units lost in battle are replaced at base stats
with no carry-over bonuses.

This makes **roster preservation a strategic layer**, particularly for:

- **Isolationists** — veteran stat gains are permanent and lost with the unit
- **Archivists** — knowledge buffs require accumulated experience

> ⚠️ \*Open question: Does unit carry-over apply across Act II branching
> paths? Decision needed before finalising this section.\*

***

## XP and Leveling

All units gain experience through combat and mission objectives. Leveling
follows a three-tier structure:

| Tier | Range | Primary Source |
| --- | --- | --- |
| Early | Level 1–3 | Kills and skirmish objectives |
| Mid | Level 3–5 | Mission completion bonuses |
| Veteran | Level 5+ | Faction-specific unlock triggers |

### Faction Unlock Triggers at Level 5+

| Faction | Veteran Unlock |
| --- | --- |
| **Harmonists** | Formation abilities replace individual stat gains |
| **Isolationists** | Permanent +1 to a chosen stat (player selects) |
| **Adaptors** | New morph forms unlocked (learn-gated, not automatic) |
| **Archivists** | Archivist Knowledge buffs become available |

For full stat details, see [Economy & Progression](/economy-progression).

***

## Act-Gated Progression

Major capability unlocks are tied to the three-act structure regardless of
individual unit level. This ensures narrative pacing and prevents early-game
power spikes.

| Act | Progression State |
| --- | --- |
| **Act I** (Missions 1–5) | Core unit types only; basic abilities |
| **Act II** (Missions 6–12) | Mid-tier tech tree unlocks; veteran bonuses active |
| **Act III** (Missions 13–18) | Full roster available; artifact-related abilities enabled |

The Act III power spike is intentional — it should feel earned and align
with the climactic revelation of the Cataclysm's origins.

For mission structure, see [World & Story](/world-story).

***

## Campaign-Level Resources

Between missions, players manage a small persistent resource pool separate
from in-mission economy.

### Reinforcement Points

- Spent to replace units lost in the previous mission
- Pool is limited and does not fully refill between missions
- Encourages unit preservation as a long-term strategy

### Faction-Specific Currencies

| Faction | Currency | Source | Spend |
| --- | --- | --- | --- |
| **Archivists** | Archive Tokens | Ruins discovered in missions | Copy opponent techs at 80% cost |
| **Adaptors** | Morph Research | Completed environmental objectives | Unlock new morph forms |

> ⚠️ \*Harmonists and Isolationists have no faction-specific between-mission
> currency currently planned. Flag if this creates balance asymmetry.\*

***

## Open Questions

The following decisions are unresolved and block finalising this page:

1. **Branching carry-over** — Do unit XP and abilities persist across the
   Act II branching paths, or does each path start from a checkpoint state?
2. **Fresh army vs. full carry-over** — Is carry-over the default for all
   missions, or do some missions
