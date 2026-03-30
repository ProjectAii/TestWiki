---
title: "Audio Design"
tags: ["audio", "music", "sound", "sfx"]
status: review
last-updated: 2026-03-30
sort_order: 50
---

## Audio Philosophy

**Principle:** Every audio element (music, voice, SFX) is custom-composed or professionally sourced. No procedurally-generated or AI-synthesized audio.

**Goal:** Create an immersive, cohesive soundscape that reinforces the game's strategic pacing and faction identity.

---

## Music & Composition

### Orchestral Foundation

**Instrumentation:**
- Strings (primary emotional layer)
- Brass (tactical intensity)
- Woodwinds (character themes)
- Percussion (rhythm and tension)
- Piano (melancholic, introspective moments)

### Music by Context

#### Menu & Exploration

**Main Menu:** 2–3 minute orchestral piece that introduces the game's themes
- Tempo: 90 BPM, 4/4 time
- Mood: Hopeful, slightly uncertain
- Key: C Major (versatile, accessible)

**Map Exploration (Non-Combat):** Ambient exploration theme
- Tempo: 80 BPM, relaxed
- Instrumentation: Gentle strings, solo cello
- Mood: Contemplative, inviting discovery

#### Combat Themes

**Tier 1 Combat (Early Game):** Moderately tense theme
- Tempo: 110 BPM
- Instrumentation: Strings + soft brass
- Key: D Minor (slightly foreboding)
- Duration: 3 minutes, loops seamlessly

**Tier 2 Combat (Mid-Game):** Increased intensity
- Tempo: 130 BPM
- Instrumentation: Full orchestra with prominent brass
- Key: G Minor (darker, more urgent)
- Duration: 4 minutes, builds tension

**Tier 3 Combat (Boss/Final):** Climactic theme
- Tempo: 150 BPM
- Instrumentation: Full orchestra with timpani, cymbals
- Key: E Minor (dramatic, powerful)
- Duration: 5 minutes, ends with heroic resolution

#### Faction Themes

Each faction has a **15–20 second musical motif** that plays when:
- Faction enters battle
- Faction completes objective
- Faction loses a major unit

**Harmonists:** Major key, flowing strings, cooperative harmonies
**Isolationists:** Minor key, staccato brass, solitary high notes
**Adaptors:** Modulating key (shifts between Major/Minor), exotic instruments (erhu, oboe)
**Archivists:** Baroque-style theme, harpsichord, scholarly feel

#### Story Moments

**Victory Fanfare:** 8-second celebratory theme (varied per faction)
**Defeat Theme:** 8-second mournful theme
**Mission Complete:** 10-second resolving theme with narrative setup for next mission

### Music Composition Specifications

| Moment | Duration | Tempo | Mood | Composer Notes |
|--------|----------|-------|------|-----------------|
| Main Menu | 2–3 min | 90 BPM | Hopeful | Establish core theme |
| Exploration | Loop | 80 BPM | Calm | Minimal percussion; focus on melody |
| Early Combat | Loop | 110 BPM | Tense | Introduce conflict |
| Mid Combat | Loop | 130 BPM | Intense | Build emotional peak |
| Boss Combat | Loop | 150 BPM | Climactic | Maximum energy |
| Victory | 8 sec | Varies | Triumphant | Quick resolution |
| Defeat | 8 sec | Varies | Melancholy | Respect the loss |

---

## Sound Effects

### Combat SFX

| Sound | Context | Notes |
|-------|---------|-------|
| Sword slash | Melee attack | Varies by weapon (sword, axe, spear) |
| Arrow release | Ranged attack | Pitch changes based on distance |
| Magic cast | Ability use | Faction-specific tone |
| Impact thud | Damage dealt | Varies by armor type (light, heavy) |
| Unit defeat | Death | Brief 1-second sound, respectful |
| Block/parry | Evasion | High-pitched metal chime |

### UI/Interaction SFX

**Selection & Confirmation:**
- Click (button press): Short, neutral tone
- Hover (mouse over button): Soft rise tone
- Confirm (action executed): Resolving chord
- Error (invalid action): Dissonant buzz

**Resource Feedback:**
- Production gained: Positive ping
- Influence increase: Ascending notes
- Morale loss: Descending notes

### Environmental Ambience

**In Battle:**
- Wind whooshing (outdoor areas)
- Cave drips (underground areas)
- Forest ambience (bird chirps, rustling)
- Water flow (water-based maps)

All ambience is **subtle, looped, sub-5dB** to not interfere with music.

---

## Voice Acting & Dialogue

### Character Categories

**Faction Leaders** (4 total):
- ~2 minutes of dialogue per faction (intro/victory/defeat lines)
- Professional voice actors
- High production quality

**Unit Types** (20+ units total):
- Brief voice lines for certain actions (ability use, level-up)
- ~5-10 seconds per unit type
- Accent varies by faction (Harmonists: warm, Isolationists: gruff, etc.)

### Dialogue Quality Standards

- No AI voice synthesis
- All professionally voiced
- Multiple takes to ensure clarity and emotion
- All dialogue fully subtitled
- Option to disable voices (text-only mode available)

---

## Audio Accessibility

### Options Menu

- **Master Volume:** 0–100%
- **Music Volume:** 0–100%
- **SFX Volume:** 0–100%
- **Voice Volume:** 0–100%
- **Mute in Background:** Toggle (mute when window loses focus)
- **Subtitles:** On/Off
- **Audio Description:** On/Off (describes SFX for hearing-impaired players)

### Quality Specifications

- **Sample Rate:** 48 kHz (industry standard for games)
- **Bit Depth:** 24-bit (high-fidelity audio)
- **Compression:** Opus or FLAC (lossless where possible)
- **Format Support:** OGG Vorbis, WAV (for development); streamed in-engine

---

## Sourcing & Rights

### Original Composition

- Hire a composer or composition team experienced in orchestral game music
- Estimated cost: $5K–$15K per minute of unique music (industry standard)
- Contract ensures perpetual license for all game uses

### Sound Effects Library

- Royalty-free sources: Freesound.org, Epidemic Sound (with attribution/license)
- Custom recording where royalty-free unavailable
- All SFX licensed for commercial game use

### Voice Acting

- Hire voice actors through casting platforms (Voices.com, Fiverr Pro)
- Union rates not required (indie game budget)
- Ensure all voice talent contracts allow perpetual use

---

> **Audio Direction Note:** Music and sound design are 40% of the emotional impact. Budget appropriately. A mediocre strategy game with excellent audio feels better than a great game with placeholder SFX.

