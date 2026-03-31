---
title: "Art Direction"
tags: ["art", "visual", "aesthetics", "ui"]
status: review
last-updated: 2026-03-30
sort_order: 70
---

## Visual Style Philosophy

**Medium:** Isometric perspective, hand-drawn 2D pixel art with modern animation techniques.

**Inspiration Sources:**
- *Tactics Ogre: Let Us Cling Together* (sprite work, isometric angle, medieval aesthetic)
- *Fire Emblem: Three Houses* (character portraits, faction identity through color/silhouette)
- *Disco Elysium* (hand-painted backgrounds, unique UI design)

**Core Principles:**
1. **Clarity:** Units must be immediately readable at a glance
2. **Faction Identity:** Color palettes distinguish factions; no ambiguity about ownership
3. **Hand-Crafted Feel:** Every asset is custom; no procedural generation or AI art
4. **Readable Typography:** UI text must be legible on small screens

---

## Color Palettes by Faction

### Harmonists

**Primary Colors:** Soft gold, sage green, cream

**Reasoning:** Represents growth, harmony, natural cycles.

**Application:**
- Unit armor/clothes: cream with gold trim
- UI accents: sage green
- Flags/shields: gold and green quartered design

### Isolationists

**Primary Colors:** Deep steel blue, iron grey, dark red

**Reasoning:** Harsh, industrial, defensive.

**Application:**
- Unit armor: dark steel with red accents (symbols of individuality)
- UI accents: blood red
- Flags/shields: geometric blue and grey patterns

### Adaptors

**Primary Colors:** Vibrant teal, amber, deep purple

**Reasoning:** Represents change, adaptability, transformation.

**Application:**
- Unit armor: shifts color as units morph (teal → purple → amber)
- UI accents: bright cyan
- Flags/shields: spiraling, flowing patterns

### Archivists

**Primary Colors:** Deep wine red, antique gold, shadow grey

**Reasoning:** Represents knowledge, history, preservation.

**Application:**
- Unit armor: burgundy robes with gold embroidery
- UI accents: antique gold
- Flags/shields: manuscripts, heraldry, rune patterns

---

## Unit Design

### Sprite Specifications

**Resolution:** 96×96 pixels per frame (standing pose)

**Animation Frames per Unit:**
- Idle (4–6 frames, looping)
- Move (8 frames, smooth)
- Attack (4–6 frames, quick impact)
- Hurt (2 frames)
- Die (4 frames, one-shot)

**Total:** ~30–35 frames per unit type

### Unit Categories & Silhouettes

```
Infantry (broad, grounded)       Ranger (tall, narrow)
□□                               ░░
■■      Mage (centered, thin)   ░░
■■      ▲
        ▲                        Cavalry (wide, long)
                                ░░░░░░
```

Each unit type has a **distinct silhouette** for instant recognition.

---

## UI/UX Design

### Main Menu

- Title screen with animated background (subtle parallax)
- "New Campaign" → faction selection with animated previews
- "Load Game" → campaign slots with thumbnail
- "Settings" → audio/video/gameplay options
- "Credits" → hand-rolled credits scroll (no auto-generated list)

### In-Game HUD

**Top Bar:**
- Current turn number | Faction name | Current objective | Time elapsed

**Left Panel (Unit Status):**
- Selected unit portrait
- Health bar, armor, status effects
- Available abilities with cooldown indicators
- Experience bar and current level

**Right Panel (Economy):**
- Production (current / max)
- Influence (current / max)
- Morale (current / max)
- Income per turn forecast

**Bottom Panel (Message Log):**
- Last 5 events (unit defeated, territory captured, ability used)
- Scrollable for full log

### Action Indicators

- **Green outline:** Selected unit
- **Blue highlight:** Valid move destination
- **Red highlight:** Enemy in range
- **Yellow glow:** Ability ready; hovering shows range/effect
- **Greyed out:** Ability on cooldown; shows remaining turns

---

## Environment Design

### Terrain Tiles

**Base Tiles (repeating 64×64 patterns):**
- Grass: light green with subtle texture
- Stone: grey flagstones with wear patterns
- Forest: dark green canopy, dappled shadows
- Water: blue with animated wave ripples
- Sand: tan with dune patterns

**Props (placed on tiles):**
- Trees (unique silhouettes per region)
- Rocks and boulders (breakable; destroys if unit moves through)
- Ruins (pre-Cataclysm architecture; faction-colored banners)
- Buildings (faction-specific architecture)

### Map Variety

**Meridian Prime** (Harmonist/Archivist lands):
- Temperate forest, river valleys
- Ancient ruins, stone structures
- Warm lighting, golden hour aesthetic

**Isolde** (Isolationist lands):
- Rocky canyons, elevated plateaus
- Fortified stone strongholds
- Cool lighting, sharp shadows

**Verdant Reaches** (Adaptor lands):
- Dense jungle, waterfalls
- Organic structures (hive-like, grown buildings)
- Warm, humid lighting; thick fog layers

---

## Animation & Effects

### Combat Effects

**Hit Effects:**
- Screen shake (small, ~2 pixels)
- Damage number float (red, +20 HP) / (yellow, critical) / (grey, blocked)
- Unit knockback (1 square away if hit hard)

**Ability Effects:**
- Firewall: Animated flames along a line
- Heal: Green radial glow expanding from unit
- Stun: Visual "dizzy stars" orbiting unit; slowed animation

### Transitions

- Map entrance: Fade in from black with faction banner
- Mission success: Slow-mo end, golden flash, victory fanfare
- Unit defeat: Fade to grey, fall animation, dust cloud
- All transitions under 2 seconds (player control maintained)

---

## Critical Standards

✓ **All assets are custom or hand-curated from royalty-free sources**
✗ **NO AI-generated art or audio**
✗ **NO procedurally-generated visuals**
✓ **Every faction must be visually distinct**
✓ **Every unit type must be immediately identifiable**

---

> **Art Direction Note:** Consistency across 50+ unit sprites and 20+ maps is resource-intensive but critical. Consider outsourcing pixel art to a studio that specializes in this style (e.g., artists who have worked on titles like *Chained Echoes* or *Wildermyth*).

