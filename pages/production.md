---
title: "Production"
tags: ["production", "timeline", "team", "tools"]
status: final
last-updated: 2026-03-30
sort_order: 60
---

## Team Structure

### Core Team (6–8 people)

| Role | Headcount | Primary Responsibilities |
|------|-----------|------------------------|
| **Producer/Director** | 1 | Vision, scope control, schedule |
| **Gameplay Programmer** | 2 | Core systems, pathfinding, combat |
| **Engine/Tools Programmer** | 1 | Build system, editor tools, QA harness |
| **Pixel Artist** | 2 | Units, environments, UI art |
| **Designer** | 1 | Mission design, balance, economy tuning |
| **Audio Director** | 1 | Music, SFX, voice direction |
| **QA Lead** | 1 | Testing, bug tracking, release criteria |

### Support (Contract/Part-Time)

- **Composer:** 2–3 people (seasonal)
- **Voice Actors:** 8–12 people (2–3 day recording sessions)
- **Sound Designer:** 1 person (3 months)
- **Narrative Designer:** 1 person (dialogue, lore, story structure)

---

## Production Timeline

### Phase 1: Preproduction (Months 1–3)

**Goal:** Finalize design, build tooling, establish aesthetic.

#### Month 1: Design & Scoping
- Finalize design document (gameplay, factions, tech trees)
- Create core systems flowchart
- Establish art style guide
- Assign design ownership (who owns what system?)
- **Deliverable:** Design Spec v1.0, Art Bible v1.0

#### Month 2: Tooling & Prototyping
- Build game engine framework (grid, pathfinding, unit system)
- Create sprite importing pipeline
- Build level editor
- Prototype combat in editor
- **Deliverable:** Playable prototype (5 minutes of gameplay)

#### Month 3: Asset Kickoff
- Model 5–6 core units per faction (20+ total)
- Compose first combat music theme
- Record faction leader voice lines
- Build campaign mission 1 layout
- **Deliverable:** First mission playable with final art

---

### Phase 2: Production (Months 4–18)

**Goal:** Create all content, reach feature-complete alpha.

#### Months 4–6: Early Game Content
- Complete all unit sprites (50+ units)
- Design & implement missions 1–5 (Act I complete)
- Implement Tier 1 tech tree
- Create 3 unique maps (one per environment type)
- **Milestone:** Act I playable, all units in game

#### Months 7–10: Mid Game Content
- Design & implement missions 6–12 (Act II complete)
- Implement Tier 2–3 tech trees
- Create faction-specific mission variants
- Compose mid-game and boss combat themes
- Create 5 additional unique maps
- **Milestone:** Acts I–II playable, 80% of music

#### Months 11–15: End Game Content
- Design & implement missions 13–18 (Act III complete)
- Implement Tier 4 (ultimate abilities)
- Create endgame difficulty scaling
- Compose final themes and victory fanfares
- Create 3 bonus/challenge maps
- Record all voice lines (100+ unique lines)
- **Milestone:** Campaign fully playable soup-to-nuts

#### Months 16–18: Feature Polish
- Implement save/load system
- Build main menu and UI flow
- Create difficulty select and new game+ system
- Implement controller support
- **Milestone:** Beta version feature-complete

---

### Phase 3: Polish & QA (Months 19–24)

**Goal:** Bug fixes, balance tuning, release-ready build.

#### Months 19–20: Bug Fixing & Optimization
- QA runs through all missions, reports critical bugs
- Performance optimization (frame rate targets: 60 FPS)
- Memory profiling and leak fixes
- **Deliverable:** Alpha build (0.1.0)

#### Months 21–22: Balance Tuning & Playtesting
- External playtesting (5–10 players)
- Difficulty adjustment based on feedback
- Unit stat tweaking (DPS, cooldowns, costs)
- **Deliverable:** Beta build (0.5.0)

#### Months 23–24: Final Polish & Release
- Dialogue and text polish (no typos, localization-ready)
- Final music mixing and mastering
- Platform-specific testing (Windows, Linux, macOS)
- Day-one patch preparation
- **Deliverable:** Release version (1.0.0)

---

## Development Tools

### Engine & Framework

| Tool | Purpose | Rationale |
|------|---------|-----------|
| **Godot 4.2+** | Game engine | Open-source, free, good 2D support |
| **GDScript** | Scripting | Native to Godot, fast iteration |
| **Aseprite** | Pixel art | Industry standard, $20 one-time fee |
| **Tiled** | Map editor | Free, supports isometric grids |
| **Git** | Version control | Industry standard, free |

### Asset Creation

| Tool | Purpose | Notes |
|------|---------|-------|
| **Aseprite** | Sprite animation | Animated sprite export to Godot |
| **Audacity** | Sound editing | Free, trim and mix SFX |
| **FL Studio** or **Reaper** | Music composition | Industry-standard DAWs |
| **Visual Studio Code** | Code editor | Free, excellent GDScript support |

### QA & Deployment

| Tool | Purpose | Notes |
|------|---------|-------|
| **GitLab Issues** | Bug tracking | Free, integrated with Git |
| **GitHub Actions** | CI/CD | Automated builds, version tagging |
| **itch.io** | Distribution | Free hosting, supports indie pricing |

---

## Budget Estimate

### Personnel (24 months)

| Role | Count | Monthly Rate | Total |
|------|-------|--------------|-------|
| Producer | 1 | $3K | $72K |
| Programmers | 3 | $2.5K ea | $180K |
| Artists | 2 | $2K ea | $96K |
| Designer | 1 | $2K | $48K |
| Audio Director | 1 | $1.5K | $36K |
| QA Lead | 1 | $1.5K | $36K |
| **Subtotal (Full-Time)** | | | **$468K** |

### Contract/Part-Time

| Role | Estimate |
|------|----------|
| Composer (3 months) | $8K |
| Voice Actors (10 people, 2 days each) | $5K |
| Sound Designer (3 months) | $4.5K |
| Narrative Designer (6 months, part-time) | $9K |
| **Subtotal (Contract)** | **$26.5K** |

### Equipment & Software

| Item | Cost |
|------|------|
| Development licenses (Godot: free, Aseprite: $20) | $100 |
| Hosting & infrastructure (Git, CI/CD, itch.io) | $300 |
| Music/SFX library licenses (Epidemic Sound, etc.) | $500 |
| Voice recording equipment (if in-house) | $2K |
| **Subtotal (Equipment)** | **$2.9K** |

### **Total Estimated Budget: $497.4K (~$500K)**

> **Funding Strategy:** Seek publisher partnership or crowdfunding (Kickstarter). $500K is achievable for a mid-scale indie project with a clear vision.

---

## Milestones & Sign-Off Gates

| Milestone | Month | Sign-Off Required |
|-----------|-------|-------------------|
| Design Document v1.0 | 1 | Producer + Creative Director |
| Playable Prototype | 3 | Producer + Lead Programmer |
| Act I Complete | 6 | Producer + Designer |
| Acts I–II Playable | 10 | Producer + Team Lead |
| Full Campaign Playable | 15 | Producer + Director |
| Alpha Build (0.1.0) | 20 | Producer + QA Lead |
| Beta Build (0.5.0) | 22 | Producer + Full Team |
| Release Build (1.0.0) | 24 | Producer + QA Lead |

---

> **Production Reality:** Ship dates always slip. Build in a 2-3 month buffer for unexpected issues. The difference between a good game and a great game is often the polish month no one budgeted for.

