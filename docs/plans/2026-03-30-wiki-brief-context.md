# Wiki Brief Context Implementation Plan

**Goal:** Give downstream forks a structured, human-readable `pages/brief.md` file that configures the AI sidebar with project context — replacing the ad-hoc `CLAUDE.local.md` approach.

**Architecture:** `pages/brief.md` is a normal wiki page (shows in nav/search) with a fixed section structure. At AI sidebar open-time, JS fetches and parses the file, extracts the `## System prompt` section as the verbatim system prompt, strips the remaining sections into a "project context" block, and injects both as cached system content blocks ahead of the doc index. A notification bar appears if the file is missing or exceeds ~1,500 tokens. When `brief.md` itself is the current page, the "current page content" block is omitted from the API call — its content is already present in the system blocks. `brief-example.md` is excluded from the search index entirely.

**Tech Stack:** Vanilla JS (ES2020+), Python 3.11 stdlib, CSS custom properties.

---

## Progress

- [x] Task 1: Create `pages/brief.md` (template) and `pages/brief-example.md` (Duty Calls reference)
- [x] Task 2: Rework `wiki.js` — brief fetch, parse, strip, inject, notification bar + CSS
- [x] Task 3: Remove `CLAUDE.local.md` / `system_prompt_file` traces from `build_wiki.py`, `config.yml`, `CLAUDE.md`

---

## Files

- Create: `pages/brief.md` — template forks fill in; ships with placeholder content + frontmatter
- Create: `pages/brief-example.md` — read-only Duty Calls reference; forks delete after setup
- Modify: `wiki/wiki.js` — replace systemPromptFile fetch with brief parsing + notification bar logic; thread `currentPageId` through `initAIModal` → `makeAPICall`; skip current page block when page is `brief.md`
- Modify: `wiki/style.css` — add `.brief-notification` styles (warning + missing states)
- Modify: `wiki/page.html` — pass `docId` as third arg to `initAIModal`
- Modify: `build_wiki.py` — remove `system_prompt_file` default + `{{AI_SYSTEM_PROMPT_FILE}}` replacement; exclude `brief-example.md` from search index
- Modify: `config.yml` — remove `system_prompt_file` key
- Modify: `CLAUDE.md` — update docs to describe `brief.md`, remove `CLAUDE.local.md` references

---

### Task 1: Create `pages/brief.md` and `pages/brief-example.md`

**Files:** `pages/brief.md`, `pages/brief-example.md`

**`pages/brief.md`** — the template shipped with upstream. Forks fill it in. Ships with frontmatter so `build_wiki.py` indexes it as a real wiki page. Placeholder content throughout; `## System prompt` at the bottom is extracted verbatim by JS.

Content to write:

```markdown
---
title: "Project Brief"
tags: ["setup"]
status: draft
last-updated: 2026-03-30
sort_order: 0
---

This file configures the AI sidebar for your Lorengine wiki. Fill in each
section below — no developer tooling required. The build script indexes this
page and the JS sidebar reads it to give the AI context for every session.

See `pages/brief-example.md` for a fully completed reference. Delete it
after setup.

Aim for under 1,000 tokens of content. A warning appears in the AI sidebar
above 1,500 tokens (~6,000 characters). The leaner and more specific each
section, the better the AI performs.

---

## Project identity

[One paragraph. What is this project? What is the wiki for?
This is the first thing the AI reads — it sets the frame for every session.]

---

## Audience and purpose

[Who reads and writes in this wiki? What do they primarily use the AI
sidebar for — drafting new docs, answering questions, extending sections?]

---

## Key decisions

<!-- Settled canon. Number each entry. One to two sentences maximum.
     This prevents the AI from relitigating prior design work. -->

1. [First settled decision.]
2. [Second settled decision.]
3. [Add as many as needed.]

---

## Writing conventions

<!-- Spelling standard, tone, preferred structure, forbidden phrases.
     The AI applies these on every draft it writes. -->

- [Convention one.]
- [Convention two.]

---

## Domain glossary

<!-- Project-specific terms the AI might misinterpret or hallucinate.
     Format: **Term** — definition. -->

- **[Term]** — [Definition specific to this project.]

---

## Inspirations and references

<!-- Works that define this project's tone and design vocabulary.
     One line each. Helps the AI use apt analogies. -->

- [Reference — why it is relevant.]

---

## Planned documents

<!-- Docs not yet written but expected. Helps the AI flag gaps
     and avoid inventing content for sections that do not exist.
     Format: `pages/filename.md` — brief description. -->

- `pages/[filename].md` — [What this doc will cover.]

---

## System prompt

<!-- IMPORTANT: Do not remove or rename this section heading.
     The AI sidebar extracts everything below this heading as the
     verbatim system prompt sent to Claude. Keep under 400 tokens.
     Write it as instructions to the AI, not a description of it. -->

You are an AI assistant embedded in the [project name] wiki, built on Lorengine.

[One sentence describing the project for the AI's context.]

Help the user draft, extend, and refine documentation pages. Match the style
and conventions of existing documents. When asked about something not yet
documented, flag it as a gap and offer to draft a stub. Only reference
documents that appear in the index — do not invent content.
```

**`pages/brief-example.md`** — the Duty Calls example. Copy content from the user's trimmed `D:\Downloads\wiki-context-example.md` file (already read earlier in this session). Add frontmatter at top and a "delete after setup" callout. Content:

```markdown
---
title: "Project Brief — Example"
tags: ["setup", "reference"]
status: reference
last-updated: 2026-03-30
sort_order: 1
---

> **This is a read-only reference example shipped with Lorengine.**
> It uses a fictional *Duty Calls: Iron Curtain* game design wiki to show
> a fully completed `pages/brief.md`. Delete this file after setup.

[then: full content from D:\Downloads\wiki-context-example.md, starting from
"## Project identity" — omitting the opening "# Wiki context — example" header
and the "Do not modify this file" paragraph, since frontmatter + callout replace them]
```

**Verify:** Run `python build_wiki.py` — both pages appear in `search_index.json` without warnings. Check `_site/pages/brief.md` and `_site/pages/brief-example.md` exist. Browse to the wiki locally and confirm both pages appear in the sidebar tree.

---

### Task 2: Rework `wiki.js` — brief fetch, parse, strip, inject, notification bar + CSS

**Files:** `wiki/wiki.js`, `wiki/style.css`
**Depends on:** Task 1 (establishes `pages/brief.md` as the target path)

**Step 1 — Remove `systemPromptFile` from `WIKI_CONFIG`** (around line 14):

```js
// REMOVE this line:
systemPromptFile: "{{AI_SYSTEM_PROMPT_FILE}}",
```

**Step 2 — Add brief helper functions** (insert before `makeAPICall`, around line 812):

```js
// ---------------------------------------------------------------------------
// Brief context (pages/brief.md)
// ---------------------------------------------------------------------------

function parseBriefSections(markdown) {
  // Split on ## headings, return object keyed by lowercase heading name
  const sections = {};
  const parts = markdown.split(/^## /m);
  for (const part of parts) {
    if (!part.trim()) continue;
    const newline = part.indexOf("\n");
    if (newline === -1) continue;
    const heading = part.slice(0, newline).trim().toLowerCase();
    const body = part.slice(newline + 1).trim();
    sections[heading] = body;
  }
  return sections;
}

function stripForAI(text) {
  // Remove HTML comments
  text = text.replace(/<!--[\s\S]*?-->/g, "");
  // Remove images entirely
  text = text.replace(/!\[[^\]]*\]\([^)]+\)/g, "");
  // Collapse links to their text
  text = text.replace(/\[([^\]]+)\]\([^)]+\)/g, "$1");
  // Remove fenced code blocks
  text = text.replace(/```[\s\S]*?```/g, "");
  // Remove inline code
  text = text.replace(/`[^`]+`/g, "");
  // Collapse excess blank lines
  text = text.replace(/\n{3,}/g, "\n\n");
  return text.trim();
}

function estimateTokens(text) {
  return Math.ceil(text.length / 4);
}

async function fetchBrief() {
  const base = WIKI_CONFIG.baseUrl ? WIKI_CONFIG.baseUrl + "/" : "";
  try {
    const resp = await fetch(`${base}pages/brief.md`);
    if (!resp.ok) return { found: false };
    const raw = await resp.text();
    const sections = parseBriefSections(raw);

    // Extract system prompt section separately
    const systemPromptRaw = sections["system prompt"] || "";
    const systemPrompt = stripForAI(systemPromptRaw);

    // Everything else (except preamble before first ##) becomes project context
    const SKIP = new Set(["system prompt"]);
    const contextParts = Object.entries(sections)
      .filter(([k]) => !SKIP.has(k))
      .map(([k, v]) => `## ${k}\n${v}`)
      .join("\n\n");
    const contextText = stripForAI(contextParts);

    const totalTokens = estimateTokens(systemPrompt + contextText);
    return { found: true, systemPrompt, contextText, totalTokens };
  } catch {
    return { found: false };
  }
}
```

**Step 3 — Add notification bar helper** (insert after `fetchBrief`):

```js
function showBriefNotification(type) {
  const modalBody = document.querySelector(".ai-modal-body");
  if (!modalBody) return;

  // Remove any existing notification
  const existing = modalBody.querySelector(".brief-notification");
  if (existing) existing.remove();

  if (!type) return;

  const bar = document.createElement("div");
  bar.className = `brief-notification brief-notification--${type}`;

  if (type === "missing") {
    bar.textContent =
      "Set up pages/brief.md to give the AI context for this wiki.";
  } else if (type === "long") {
    bar.textContent =
      "Project brief is quite long — aim for under 1,000 tokens for best AI performance.";
  }

  // Insert before .ai-messages
  const messages = modalBody.querySelector(".ai-messages");
  if (messages) {
    modalBody.insertBefore(bar, messages);
  } else {
    modalBody.prepend(bar);
  }
}
```

**Step 4 — Thread `currentPageId` through the call chain.**

In `page.html`, change line 190:
```js
// Before:
initAIModal(body, searchIndex);
// After:
initAIModal(body, searchIndex, docId);
```

Update `initAIModal` signature and pass `currentPageId` down to `makeAPICall`:
```js
// Before:
function initAIModal(currentDocContent, searchIndex) {
// After:
function initAIModal(currentDocContent, searchIndex, currentPageId = "") {
```

And at the `makeAPICall` call site inside `initAIModal` (~line 775):
```js
// Before:
const response = await makeAPICall(conversation, currentDocContent, searchIndex);
// After:
const response = await makeAPICall(conversation, currentDocContent, searchIndex, currentPageId);
```

Update `makeAPICall` signature:
```js
// Before:
async function makeAPICall(conversation, currentDocContent, searchIndex) {
// After:
async function makeAPICall(conversation, currentDocContent, searchIndex, currentPageId = "") {
```

Then in the `messages` array construction, skip the current page block when on `brief.md`:
```js
const messages = [
  ...(currentPageId !== "pages/brief.md"
    ? [{ role: "user", content: `[Current page content]\n${currentDocContent}\n\n---` }]
    : []),
  ...conversation,
];
```

**Step 6 — Cache brief at module level + fetch on modal open** (add near the top of `initAIModal`):

```js
// Brief is fetched once per page load and cached
let _briefCache = null;

async function getBrief() {
  if (_briefCache !== null) return _briefCache;
  _briefCache = await fetchBrief();
  return _briefCache;
}
```

In `initAIModal`, after the early-return guard (`if (!floatBtn || !modal) return;`), add a one-time fetch when the modal first opens. Find the existing open-modal event (likely a click handler on `floatBtn`) and add:

```js
let briefFetched = false;
floatBtn.addEventListener("click", async () => {
  if (!briefFetched) {
    briefFetched = true;
    const brief = await getBrief();
    if (!brief.found) {
      showBriefNotification("missing");
    } else if (brief.totalTokens > 1500) {
      showBriefNotification("long");
    }
  }
  // existing open logic follows...
});
```

Note: Read the exact floatBtn click handler in `initAIModal` and splice in the brief fetch at the top of the existing handler rather than adding a second listener. The existing handler likely toggles the modal open — the brief fetch should happen before or at the start of that block.

**Step 7 — Update `makeAPICall`** to use `brief` and respect `currentPageId` (replace lines 813–843):

```js
async function makeAPICall(conversation, currentDocContent, searchIndex, currentPageId = "") {
  const docSummary = searchIndex
    .map((d) => `- ${d.title} [${(d.tags || []).join(", ")}]: ${d.excerpt.slice(0, 80)}`)
    .join("\n");

  const brief = await getBrief();

  const defaultSystemPrompt =
    "You are an AI assistant embedded in a documentation wiki. " +
    "Be helpful, concise, and reference the current document when relevant.";

  const systemContent = [
    {
      type: "text",
      text: brief.found && brief.systemPrompt ? brief.systemPrompt : defaultSystemPrompt,
      ...(WIKI_CONFIG.ai.enablePromptCaching ? { cache_control: { type: "ephemeral" } } : {}),
    },
    ...(brief.found && brief.contextText
      ? [
          {
            type: "text",
            text: `## Project context\n${brief.contextText}`,
            ...(WIKI_CONFIG.ai.enablePromptCaching ? { cache_control: { type: "ephemeral" } } : {}),
          },
        ]
      : []),
    {
      type: "text",
      text: `## Document index\n${docSummary}`,
      ...(WIKI_CONFIG.ai.enablePromptCaching ? { cache_control: { type: "ephemeral" } } : {}),
    },
  ];

  // Skip current page block when viewing brief.md — its content is already
  // present in the system prompt and project context blocks above.
  const messages = [
    ...(currentPageId !== "pages/brief.md"
      ? [{ role: "user", content: `[Current page content]\n${currentDocContent}\n\n---` }]
      : []),
    ...conversation,
  ];

  // rest of fetch call unchanged...
```

**Step 8 — Add CSS** to `wiki/style.css` (append after the `.ai-locked-content p` block, around line 1112):

```css
/* ── Brief Notification Bar ────────────────── */

.brief-notification {
  padding: 0.45rem 0.9rem;
  font-size: 0.78rem;
  line-height: 1.4;
  border-radius: 4px;
  margin: 0.5rem 0.75rem 0;
  flex-shrink: 0;
}

.brief-notification--missing {
  background: color-mix(in srgb, #f59e0b 15%, transparent);
  color: var(--text);
  border: 1px solid color-mix(in srgb, #f59e0b 50%, transparent);
}

.brief-notification--long {
  background: color-mix(in srgb, var(--accent) 10%, transparent);
  color: var(--text-secondary);
  border: 1px solid color-mix(in srgb, var(--accent) 30%, transparent);
}
```

**Verify:** Open the wiki locally. Without `pages/brief.md` filled in (or rename it temporarily), open AI modal — yellow "missing" bar appears. Restore and fill `brief.md` past 6,000 chars — "long" bar appears. With a well-formed `brief.md`, no bar. Open browser devtools Network tab, open AI modal, confirm `pages/brief.md` is fetched once. Send a message, check the API request payload in Network — confirm `system` array has 3 blocks (system prompt, project context, doc index) when brief is configured, 2 blocks when it isn't.

---

### Task 3: Remove `CLAUDE.local.md` / `system_prompt_file` traces

**Files:** `build_wiki.py`, `config.yml`, `CLAUDE.md`

**`build_wiki.py`:**

Add a module-level constant near the top (after imports):
```python
# Pages excluded from the search index (reference artifacts, not content)
EXCLUDED_FROM_INDEX = {"brief-example.md"}
```

In `build_search_index()`, add a skip check immediately after the slug is derived:
```python
slug = md_path.stem
if md_path.name in EXCLUDED_FROM_INDEX:
    continue
```

In `load_config()` defaults dict, remove the `system_prompt_file` key from the `"ai"` section:
```python
# REMOVE:
"system_prompt_file": "CLAUDE.local.md",
```

In `assemble_site()` replacements dict, remove the `{{AI_SYSTEM_PROMPT_FILE}}` entry:
```python
# REMOVE:
"{{AI_SYSTEM_PROMPT_FILE}}": str(config["ai"]["system_prompt_file"]),
```

**`config.yml`:**

Remove the `system_prompt_file` line from the `ai:` block:
```yaml
# REMOVE:
  system_prompt_file: "CLAUDE.local.md"
```

**`CLAUDE.md`:**

1. In "Configuration" section — remove the `system_prompt_file` line from the `config.yml` example block and its description.
2. In "AI sidebar — API call design" section — replace the mention of `CLAUDE.local.md` as system prompt source with: *"System prompt — from `pages/brief.md` in the downstream repo (the `## System prompt` section, cached). Project context — all other sections of `pages/brief.md` (key decisions, glossary, conventions, cached)."*
3. In "Repo structure" table and `_site/` description — no mention of `CLAUDE.local.md` (verify it doesn't appear).
4. In "Setup instructions for new forks" — replace step 5 (`Create CLAUDE.local.md`) with: *"Fill in `pages/brief.md` with your project identity, key decisions, and system prompt."*
5. Remove the `CLAUDE.local.md template` section entirely (the full template block at the bottom).
6. In "Separation of concerns" table — update the row for `CLAUDE.local.md` to reference `pages/brief.md` instead.

**Verify:** `grep -r "CLAUDE.local" wiki/ build_wiki.py config.yml CLAUDE.md` returns zero matches. `grep -r "system_prompt_file" wiki/ build_wiki.py config.yml` returns zero matches. Run `python build_wiki.py` — no warnings about unknown config keys.
