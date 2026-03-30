# Wiki Editing & Page Management Implementation Plan

**Goal:** Add page creation/editing via Decap CMS, frontmatter-based slug hierarchy, sort_order-based tree ordering, auto-updated timestamps, and a drag-and-drop tree management page.

**Architecture:** Decap CMS handles create/edit via direct GitHub API commits. `build_wiki.py` resolves slug-based `parent` frontmatter references to full paths, validates slug uniqueness (hard fail), warns on duplicate titles (soft), auto-updates `last-updated` when body content hash changes, and populates `sort_order` into `search_index.json`. Wiki JS uses `sort_order` from the index for tree ordering. The tree management page (`/admin/tree.html`) reads the search index and writes frontmatter changes via GitHub API using Decap's stored OAuth token. Core flow: `pages/*.md` frontmatter → `build_wiki.py` → `search_index.json` → wiki JS tree/nav. Edit flow: Decap → GitHub commit → Actions rebuild.

**Tech Stack:** Python 3.11 (stdlib), Vanilla JS ES2020+, Decap CMS 3.x (CDN), GitHub Contents API, DOMPurify (all dynamic HTML sanitized)

---

## Progress

- [ ] Task 1: Build System — Slug Validation, Frontmatter Hierarchy, Sort Order, Auto Timestamps
- [ ] Task 2: Decap CMS — Config, Admin Page, Pre-Checks
- [ ] Task 3: Create/Edit Buttons in Wiki UI
- [ ] Task 4: Tree Sidebar — Sort Order Support
- [ ] Task 5: Tree Management Page — Drag-to-Reorder + Reparent

---

## Files

**Create:**
- `wiki/admin/index.html` — Decap CMS admin page with custom pre-check JS
- `wiki/admin/tree.html` — Drag-and-drop tree management page
- `content_hashes.json` — committed artifact: `{"pages/slug.md": "abcd1234"}` — used to detect content changes

**Modify:**
- `build_wiki.py` — slug validation, frontmatter hierarchy, sort_order, auto-timestamps, copy decap.yml to `_site/admin/config.yml`
- `decap.yml` — add `sort_order`/`parent` fields, add `{{GITHUB_REPO}}` placeholder
- `config.yml` — add `github.repo` field
- `.github/workflows/build.yml` — add `contents: write` permission + git commit step for auto-updated files
- `wiki/wiki.js` — `sort_order` in `sortDocIds()`, `adminEditUrl()`/`adminNewUrl()` helpers
- `wiki/index.html` — "New Page" button in nav
- `wiki/page.html` — "Edit Page" button in nav
- `wiki/style.css` — `.btn-edit` styles

---

### Task 1: Build System — Slug Validation, Frontmatter Hierarchy, Sort Order, Auto Timestamps

**Files:** `build_wiki.py`, `content_hashes.json`, `.github/workflows/build.yml`

#### 1a. Slug extraction + uniqueness validation

In `build_search_index()`, extract `slug` and `sort_order` from frontmatter, check for duplicate slugs (hard exit) and duplicate titles (soft warn):

```python
from pathlib import Path
import hashlib

def build_search_index(root, pages_dir="pages"):
    docs_dir = root / pages_dir
    if not docs_dir.exists():
        print(f"Warning: {pages_dir}/ directory not found")
        return []

    entries = []
    slug_seen = {}    # slug -> rel_path, hard-fail on duplicate
    title_seen = {}   # title_lower -> rel_path, soft-warn on duplicate

    for md_path in sorted(docs_dir.rglob("*.md")):
        rel_path = md_path.relative_to(root).as_posix()
        slug = md_path.stem  # filename without extension

        # Hard fail: duplicate slug means two files with same name (flat structure)
        if slug in slug_seen:
            print(f"ERROR: Duplicate slug '{slug}' in {rel_path} (already defined by {slug_seen[slug]})")
            sys.exit(1)
        slug_seen[slug] = rel_path

        text = md_path.read_text(encoding="utf-8")
        metadata, body = parse_frontmatter(text)
        if metadata is None or "title" not in metadata:
            print(f"Warning: skipping {rel_path} — missing title in frontmatter")
            continue

        # Soft warn: duplicate title
        title_key = metadata["title"].lower()
        if title_key in title_seen:
            print(f"Warning: duplicate title '{metadata['title']}' in {rel_path} (also in {title_seen[title_key]})")
        title_seen[title_key] = rel_path

        headings = extract_headings(body)
        plain_body = strip_markdown(body)
        excerpt = plain_body[:300]

        entry = {
            "id": rel_path,
            "slug": slug,
            "title": metadata.get("title", ""),
            "sort_order": int(metadata.get("sort_order", 100)),
            "parent_slug": str(metadata.get("parent", "")).strip(),
            "tags": metadata.get("tags", []),
            "status": metadata.get("status", "draft"),
            "last_updated": str(metadata.get("last-updated", "")),
            "headings": headings,
            "excerpt": excerpt,
            "body": plain_body,
        }
        entries.append(entry)

    return entries
```

#### 1b. Frontmatter-based hierarchy (replaces folder-based compute_hierarchy)

Replace the entire `compute_hierarchy()` function:

```python
def compute_hierarchy(entries):
    """Build parent/child relationships from frontmatter 'parent' slug field.

    Each page may set parent: <slug> in frontmatter. The slug is the filename
    stem (e.g. 'getting-started' for pages/getting-started.md).
    Resolves slug references to full IDs stored in the search index.
    """
    slug_map = {entry["slug"]: entry["id"] for entry in entries}

    for entry in entries:
        parent_slug = entry.pop("parent_slug", "")
        if parent_slug and parent_slug in slug_map:
            entry["parent"] = slug_map[parent_slug]
        else:
            if parent_slug:
                print(f"Warning: '{entry['id']}' references unknown parent slug '{parent_slug}'")
            entry["parent"] = None
        entry["children"] = []

    id_map = {entry["id"]: entry for entry in entries}
    for entry in entries:
        if entry["parent"] and entry["parent"] in id_map:
            id_map[entry["parent"]]["children"].append(entry["id"])

    return entries
```

#### 1c. Auto-update last-updated on content change

Add these two functions before `main()`:

```python
def load_content_hashes(root):
    path = root / "content_hashes.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}

def update_frontmatter_field(text, field, value):
    """Surgically update one field in YAML frontmatter without re-serializing."""
    if not text.startswith("---"):
        return text
    end = text.find("---", 3)
    if end == -1:
        return text
    fm_text = text[3:end]
    body = text[end:]
    updated, count = re.subn(
        rf'^({re.escape(field)}\s*:).*$',
        rf'\1 {value}',
        fm_text,
        flags=re.MULTILINE
    )
    if count == 0:
        updated = fm_text.rstrip() + f'\n{field}: {value}\n'
    return f"---{updated}{body}"

def auto_update_timestamps(root, entries, pages_dir="pages"):
    """Compare body content hashes; rewrite last-updated frontmatter if changed."""
    import datetime
    stored = load_content_hashes(root)
    new_hashes = {}
    updated_count = 0

    for entry in entries:
        page_id = entry["id"]
        body_hash = hashlib.sha256(entry["body"].encode()).hexdigest()[:16]
        new_hashes[page_id] = body_hash

        if stored.get(page_id) != body_hash:
            today = datetime.date.today().isoformat()
            md_path = root / page_id
            original = md_path.read_text(encoding="utf-8")
            patched = update_frontmatter_field(original, "last-updated", today)
            if patched != original:
                md_path.write_text(patched, encoding="utf-8")
                entry["last_updated"] = today
                updated_count += 1

    (root / "content_hashes.json").write_text(
        json.dumps(new_hashes, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if updated_count:
        print(f"  Auto-updated last-updated on {updated_count} page(s)")
    return entries
```

Call in `main()` between steps 2 and 3:

```python
search_index = build_search_index(root, pages_dir)
search_index = auto_update_timestamps(root, search_index, pages_dir)  # NEW
search_index = compute_hierarchy(search_index)
search_index = compute_backlinks(search_index, pages_dir)
```

#### 1d. Copy decap.yml to `_site/admin/config.yml` during site assembly

In `assemble_site()`, after the HTML injection loop:

```python
# Copy Decap CMS config into _site/admin/
admin_dir = site_dir / "admin"
admin_dir.mkdir(exist_ok=True)
decap_config = root / "decap.yml"
if decap_config.exists():
    decap_content = decap_config.read_text(encoding="utf-8")
    github_repo = str(config.get("github", {}).get("repo", ""))
    decap_content = decap_content.replace("{{GITHUB_REPO}}", github_repo)
    (admin_dir / "config.yml").write_text(decap_content, encoding="utf-8")
```

Add `{{GITHUB_REPO}}` replacement to the build replacements dict too, so admin HTML gets it:

```python
"{{GITHUB_REPO}}": str(config.get("github", {}).get("repo", "")),
```

#### 1e. GitHub Actions — commit auto-updated timestamps

In `.github/workflows/build.yml`:

Change `permissions.contents` from `read` to `write`, and add a commit step after "Build wiki":

```yaml
permissions:
  contents: write
  pages: write
  id-token: write

# After "Build wiki" step:
- name: Commit auto-updated timestamps
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git add pages/ content_hashes.json
    git diff --staged --quiet || (git commit -m "chore: auto-update last-updated timestamps [skip ci]" && git push)
```

Also update the `on.push.paths` trigger to include `content_hashes.json`:

```yaml
on:
  push:
    paths: ['docs/**', 'pages/**', 'wiki/**', 'build_wiki.py', 'config.yml', 'decap.yml']
```

**Create `content_hashes.json`** in the repo root with contents `{}`.

**Verify:** Edit a page body. Run `python build_wiki.py` locally. Confirm `last-updated` in that file's frontmatter updates to today and `content_hashes.json` has a new hash for it. Run again unchanged — confirm no second update. Introduce two `.md` files with the same name — confirm build exits with `ERROR: Duplicate slug`.

---

### Task 2: Decap CMS — Config, Admin Page, Pre-Checks

**Files:** `decap.yml`, `config.yml`, `wiki/admin/index.html`
**Depends on:** Task 1 (build copies decap.yml to `_site/admin/config.yml`)

#### 2a. Update `decap.yml`

```yaml
backend:
  name: github
  repo: "{{GITHUB_REPO}}"
  branch: master
  auth_scope: repo

media_folder: pages/assets
public_folder: /assets

collections:
  - name: pages
    label: Pages
    folder: pages
    create: true
    slug: "{{slug}}"
    identifier_field: title
    fields:
      - { label: Title, name: title, widget: string, required: true }
      - label: Slug
        name: slug
        widget: string
        required: false
        hint: "⚠ Auto-generated from title. DO NOT CHANGE after creation — breaks all parent references pointing to this page."
        pattern: ['^[a-z0-9-]*$', "Lowercase letters, numbers, and hyphens only"]
      - label: Parent
        name: parent
        widget: string
        required: false
        hint: "Slug of the parent page (e.g. 'getting-started'). Leave empty for a root-level page."
      - label: Sort Order
        name: sort_order
        widget: number
        default: 100
        value_type: int
        hint: "Lower numbers appear first in the tree. Siblings with the same value sort alphabetically."
      - { label: Tags, name: tags, widget: list, field: { label: Tag, name: tag, widget: string }, default: [] }
      - { label: Status, name: status, widget: select, options: [draft, review, final], default: draft }
      - { label: "Last Updated", name: last-updated, widget: datetime, format: YYYY-MM-DD, picker_utc: true }
      - { label: Body, name: body, widget: markdown }
    filter:
      field: title
      pattern: .+
```

#### 2b. Update `config.yml`

Add at the top, before the `wiki:` section:

```yaml
github:
  repo: "YOUR_USERNAME/YOUR_REPO"   # set this in your fork (e.g. "alice/my-wiki")
```

#### 2c. Create `wiki/admin/index.html`

The preSave handler loads `search_index.json` once, checks for slug collisions (hard block with suggested alternative), and duplicate title (soft warning). All user-visible strings are escaped before display.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Admin — {{WIKI_TITLE}}</title>
  <style>
    #lorengine-nav {
      position: fixed; top: 0; right: 0; z-index: 9999;
      padding: 6px 14px; background: rgba(0,0,0,0.75);
      border-radius: 0 0 0 8px; display: flex; gap: 12px;
    }
    #lorengine-nav a { color: #ccc; text-decoration: none; font-size: 13px; }
    #lorengine-nav a:hover { color: #fff; }
  </style>
</head>
<body>
  <div id="lorengine-nav">
    <a href="../">&#8592; Wiki</a>
    <a href="tree.html">Tree Manager</a>
  </div>
  <script src="https://unpkg.com/decap-cms@^3.0.0/dist/decap-cms.js"></script>
  <script>
  (async function initAdminPreChecks() {
    if (typeof CMS === 'undefined') return;

    const existingTitles = new Set();
    const existingSlugs = new Set();

    // Load current index for validation — done once at startup
    try {
      const base = window.location.pathname.replace(/\/admin\/?.*$/, '');
      const resp = await fetch(`${base}/search_index.json`);
      if (resp.ok) {
        const index = await resp.json();
        for (const doc of index) {
          existingTitles.add(doc.title.toLowerCase());
          existingSlugs.add(doc.slug);
        }
      }
    } catch (e) {
      console.warn('[Lorengine] Could not load search_index for pre-checks:', e);
    }

    CMS.registerEventListener({
      name: 'preSave',
      handler: ({ entry }) => {
        const data = entry.get('data');
        const title = (data.get('title') || '').trim();
        // entry.get('path') is empty/null for new entries
        const isNew = !entry.get('path');

        // Determine the slug that will be used for this entry
        const rawSlug = (data.get('slug') || title)
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, '-')
          .replace(/^-+|-+$/g, '');

        // Soft warn: duplicate title (allowed if slugs differ, but discouraged)
        if (isNew && existingTitles.has(title.toLowerCase())) {
          // Non-blocking: just notify via console and a window message
          console.info(`[Lorengine] Title "${title}" already exists on another page. Consider a more specific title.`);
          // We cannot reliably inject into Decap's UI, so use a non-blocking banner
          const banner = document.createElement('div');
          const safeTitle = title.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
          banner.textContent = `Note: Another page is already named "${safeTitle}". Consider a more specific title.`;
          Object.assign(banner.style, {
            position: 'fixed', top: '40px', left: '50%', transform: 'translateX(-50%)',
            background: '#f0a500', color: '#000', padding: '8px 20px',
            borderRadius: '6px', zIndex: '99999', fontSize: '14px'
          });
          document.body.appendChild(banner);
          setTimeout(() => banner.remove(), 5000);
          // Allow save to continue
        }

        // Hard block: slug collision — suggest a free slug
        if (isNew && existingSlugs.has(rawSlug)) {
          let counter = 2;
          let candidate = `${rawSlug}-${counter}`;
          while (existingSlugs.has(candidate)) { counter++; candidate = `${rawSlug}-${counter}`; }
          // alert() is intentional here — this is a blocking admin action, not a page the end-user sees
          window.alert(
            `The slug "${rawSlug}" is already taken by another page.\n\n` +
            `Suggested free slug: "${candidate}"\n\n` +
            `Please update the Slug field before saving.`
          );
          return false; // block save
        }

        return true; // allow save
      }
    });
  })();
  </script>
</body>
</html>
```

**Verify:** Open `/admin/`. Log in with GitHub. Confirm `sort_order`, `parent`, and `Slug` fields appear in the new-page form. Create a page. Attempt to create a second page with the same computed slug — confirm blocked with the suggested alternative slug. Create two pages with the same title — confirm the orange banner appears but save succeeds.

---

### Task 3: Create/Edit Buttons in Wiki UI

**Files:** `wiki/wiki.js`, `wiki/index.html`, `wiki/page.html`, `wiki/style.css`

#### 3a. Add admin URL helpers to `wiki/wiki.js`

After the `docUrl()` function (after line ~94):

```js
function adminEditUrl(slug) {
  const base = WIKI_CONFIG.baseUrl ? WIKI_CONFIG.baseUrl + "/" : "";
  return `${base}admin/#/collections/pages/entries/${encodeURIComponent(slug)}`;
}

function adminNewUrl() {
  const base = WIKI_CONFIG.baseUrl ? WIKI_CONFIG.baseUrl + "/" : "";
  return `${base}admin/#/collections/pages/new`;
}
```

#### 3b. Add "New Page" button to `wiki/index.html`

In `<nav class="header-nav">`, after the Search link:

```html
<a href="admin/" id="new-page-btn" class="btn-admin">New Page</a>
```

In the inline script, after `initThemePanel()`:

```js
const newBtn = document.getElementById('new-page-btn');
if (newBtn) newBtn.href = adminNewUrl();
```

#### 3c. Add "Edit Page" button to `wiki/page.html`

In `<nav class="header-nav">`, after the Search link:

```html
<a href="#" id="edit-page-btn" class="btn-admin" hidden>Edit Page</a>
```

In the inline page script, after the `if (meta)` block that sets `document.title` (~line 112):

```js
const editBtn = document.getElementById('edit-page-btn');
if (editBtn && meta && meta.slug) {
  editBtn.href = adminEditUrl(meta.slug);
  editBtn.removeAttribute('hidden');
}
```

#### 3d. Add `.btn-admin` styles to `wiki/style.css`

Find the `.header-nav` block and append:

```css
.btn-admin {
  padding: 3px 10px;
  border: 1px solid var(--accent);
  border-radius: 4px;
  color: var(--accent);
  font-size: 0.82rem;
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
  white-space: nowrap;
}
.btn-admin:hover {
  background: var(--accent);
  color: #fff;
}
```

**Verify:** Load any wiki page. Confirm "Edit Page" button appears in the nav and links to `/admin/#/collections/pages/entries/{slug}`. Load `index.html`. Confirm "New Page" links to `/admin/#/collections/pages/new`. On mobile width, confirm the button doesn't break the header layout.

---

### Task 4: Tree Sidebar — Sort Order Support

**Files:** `wiki/wiki.js`

#### 4a. Replace `sortDocIds()` with sort_order support

Replace the function starting at line 294:

```js
function sortDocIds(ids, docMap, sortOrder) {
  return [...ids].sort((a, b) => {
    const da = docMap[a];
    const db = docMap[b];
    switch (sortOrder) {
      case "alpha-asc":  return da.title.localeCompare(db.title);
      case "alpha-desc": return db.title.localeCompare(da.title);
      case "date-asc":   return (da.last_updated || "").localeCompare(db.last_updated || "");
      case "date-desc":  return (db.last_updated || "").localeCompare(da.last_updated || "");
      case "sort-order":
      default: {
        const diff = (da.sort_order || 100) - (db.sort_order || 100);
        return diff !== 0 ? diff : da.title.localeCompare(db.title);
      }
    }
  });
}
```

#### 4b. Update tree controls in `initTreeSidebar()` — add "Custom order" as first/default option

In the `controlsHtml` string, replace the `<select class="tree-sort">` block:

```js
<select class="tree-sort">
  <option value="sort-order" selected>Custom order</option>
  <option value="alpha-asc">A\u2013Z</option>
  <option value="alpha-desc">Z\u2013A</option>
  <option value="date-asc">Oldest first</option>
  <option value="date-desc">Newest first</option>
</select>
```

In `updateTree()`, change the fallback default:

```js
const sortOrder = sortSelect?.value || "sort-order";
```

**Verify:** Load wiki. Confirm sidebar uses "Custom order" by default and pages render in `sort_order` ascending order. Siblings with the same `sort_order` fall back to alphabetical. Switching the dropdown to "A–Z" sorts alphabetically; switching back restores sort_order order.

---

### Task 5: Tree Management Page — Drag-to-Reorder + Reparent

**Files:** `wiki/admin/tree.html`
**Depends on:** Task 1 (search_index has `slug` + `sort_order`), Task 2 (admin nav, GitHub token in localStorage)

The page loads `search_index.json`, renders a draggable tree, tracks local `treeState` changes, and batch-commits frontmatter patches via the GitHub Contents API. All dynamic HTML rendered from data uses `escapeHtml()` to prevent XSS.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Tree Manager — {{WIKI_TITLE}}</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, sans-serif; background: #1a1a1a; color: #e0e0e0; padding: 24px; }
    h1 { font-size: 1.3rem; margin-bottom: 16px; }
    #lorengine-nav { margin-bottom: 20px; font-size: 13px; }
    #lorengine-nav a { color: #888; text-decoration: none; margin-right: 12px; }
    #lorengine-nav a:hover { color: #fff; }
    #status { margin: 10px 0; min-height: 22px; font-size: 13px; color: #aaa; }
    #status.error { color: #f66; }
    #status.success { color: #6c6; }
    #save-btn {
      padding: 7px 18px; background: #3b6ff0; border: none; border-radius: 6px;
      color: #fff; font-size: 14px; cursor: pointer; margin-bottom: 16px;
    }
    #save-btn:disabled { opacity: 0.4; cursor: not-allowed; }
    #save-btn:hover:not(:disabled) { background: #2a5cd0; }
    .tree-root, .tree-children { list-style: none; padding: 0; }
    .tree-children { padding-left: 24px; }
    .tree-node { position: relative; margin: 2px 0; }
    .node-row {
      display: flex; align-items: center; gap: 8px;
      padding: 6px 8px; border-radius: 6px; background: #2a2a2a;
      user-select: none; position: relative;
    }
    .node-row.over-before::before {
      content: ''; position: absolute; top: -1px; inset-inline: 0;
      height: 2px; background: #3b6ff0; border-radius: 2px;
    }
    .node-row.over-after::after {
      content: ''; position: absolute; bottom: -1px; inset-inline: 0;
      height: 2px; background: #3b6ff0; border-radius: 2px;
    }
    .node-row.over-child { outline: 2px solid #3b6ff0; background: #1e3a5f; }
    .drag-handle { cursor: grab; color: #555; font-size: 14px; flex-shrink: 0; line-height: 1; }
    .drag-handle:active { cursor: grabbing; }
    .node-title { flex: 1; font-size: 14px; }
    .node-title.changed { color: #f0a500; }
    .node-slug { font-size: 11px; color: #666; }
    .node-order { font-size: 11px; color: #555; width: 28px; text-align: right; flex-shrink: 0; }
    #drop-root {
      margin-top: 10px; padding: 10px; border: 1px dashed #444; border-radius: 6px;
      text-align: center; font-size: 12px; color: #555;
    }
    #drop-root.active { border-color: #3b6ff0; color: #3b6ff0; }
  </style>
</head>
<body>
  <div id="lorengine-nav">
    <a href="../">&#8592; Wiki</a>
    <a href="./">CMS Admin</a>
  </div>
  <h1>Tree Manager</h1>
  <div id="status">Loading...</div>
  <button id="save-btn" disabled>Save Changes</button>
  <div id="tree-container"></div>
  <div id="drop-root">&#x2913; Drop here to make root-level</div>

  <script>
  // ── Helpers ────────────────────────────────────────────────────────────────
  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
  }

  // ── State ──────────────────────────────────────────────────────────────────
  let docMap = {};       // id -> doc entry from search_index
  let slugToId = {};     // slug -> id
  let idToSlug = {};     // id -> slug
  // treeState: id -> { parent: id|null, sort_order: number }
  let treeState = {};
  let changes = new Set();
  let draggedId = null;
  let githubToken = null;
  let githubRepo = null;

  // ── Auth ───────────────────────────────────────────────────────────────────
  function loadGithubAuth() {
    try {
      const raw = localStorage.getItem('netlify-cms-user');
      if (raw) {
        const u = JSON.parse(raw);
        if (u && u.token) return u.token;
      }
    } catch {}
    return null;
  }

  // ── Data loading ───────────────────────────────────────────────────────────
  async function loadData() {
    const base = window.location.pathname.replace(/\/admin\/?.*$/, '');

    // Load search index
    const indexResp = await fetch(`${base}/search_index.json`);
    if (!indexResp.ok) throw new Error('Could not load search_index.json');
    const index = await indexResp.json();

    for (const doc of index) {
      docMap[doc.id] = doc;
      slugToId[doc.slug] = doc.id;
      idToSlug[doc.id] = doc.slug;
      treeState[doc.id] = {
        parent: doc.parent || null,
        sort_order: doc.sort_order || 100
      };
    }

    // Load github repo from admin config
    try {
      const cfgResp = await fetch(`${base}/admin/config.yml`);
      if (cfgResp.ok) {
        const txt = await cfgResp.text();
        const m = txt.match(/repo:\s*["']?([^\s"'\n#]+)["']?/);
        if (m) githubRepo = m[1].trim();
      }
    } catch {}
  }

  // ── Tree helpers ───────────────────────────────────────────────────────────
  function getSortedChildren(parentId) {
    return Object.entries(treeState)
      .filter(([, s]) => s.parent === parentId)
      .sort(([aid, a], [bid, b]) => {
        const diff = a.sort_order - b.sort_order;
        return diff !== 0 ? diff : (docMap[aid]?.title || '').localeCompare(docMap[bid]?.title || '');
      })
      .map(([id]) => id);
  }

  // ── Frontmatter patch (pure string, no innerHTML) ──────────────────────────
  function patchFrontmatterField(text, field, value) {
    if (!text.startsWith('---')) return text;
    const end = text.indexOf('---', 3);
    if (end === -1) return text;
    const fm = text.slice(3, end);
    const body = text.slice(end);
    const pattern = new RegExp(`^(${field.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\s*:).*$`, 'm');
    if (pattern.test(fm)) {
      return '---' + fm.replace(pattern, `$1 ${value}`) + body;
    }
    // Field not present — append before closing ---
    return '---' + fm.trimEnd() + `\n${field}: ${value}\n` + body;
  }

  // ── GitHub API ─────────────────────────────────────────────────────────────
  async function patchPageOnGitHub(id, newParent, newSortOrder) {
    const path = id; // e.g. "pages/slug.md"
    const url = `https://api.github.com/repos/${githubRepo}/contents/${encodeURIComponent(path)}`;
    const headers = {
      Authorization: `token ${githubToken}`,
      Accept: 'application/vnd.github.v3+json',
    };

    // GET current file (need SHA for PUT)
    const getResp = await fetch(url, { headers });
    if (!getResp.ok) throw new Error(`GET ${path} failed: ${getResp.status}`);
    const fileData = await getResp.json();
    const sha = fileData.sha;
    // Decode base64 content (GitHub returns it with newlines every 60 chars)
    let content = decodeURIComponent(
      Array.from(atob(fileData.content.replace(/\n/g, '')))
        .map(c => '%' + c.charCodeAt(0).toString(16).padStart(2, '0'))
        .join('')
    );

    // Apply patches
    const parentSlug = newParent ? (idToSlug[newParent] || '') : '';
    if (parentSlug) {
      content = patchFrontmatterField(content, 'parent', parentSlug);
    } else {
      // Remove the parent field when making root-level
      content = content.replace(/\nparent:[^\n]*/, '');
    }
    content = patchFrontmatterField(content, 'sort_order', String(newSortOrder));

    // Encode back to base64
    const encoded = btoa(
      encodeURIComponent(content).replace(/%([0-9A-F]{2})/g, (_, hex) =>
        String.fromCharCode(parseInt(hex, 16))
      )
    );

    const slug = idToSlug[id] || id;
    const putResp = await fetch(url, {
      method: 'PUT',
      headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: `chore: update tree structure for ${slug}`,
        content: encoded,
        sha,
      }),
    });
    if (!putResp.ok) {
      const err = await putResp.json().catch(() => ({}));
      throw new Error(`PUT ${path} failed: ${err.message || putResp.status}`);
    }
  }

  // ── Drag-and-drop logic ────────────────────────────────────────────────────
  function getDropPosition(e, el) {
    const rect = el.getBoundingClientRect();
    const pct = (e.clientY - rect.top) / rect.height;
    if (pct < 0.25) return 'before';
    if (pct > 0.75) return 'after';
    return 'child';
  }

  function applyDrop(dragId, targetId, position) {
    if (dragId === targetId) return;

    if (position === 'child') {
      treeState[dragId].parent = targetId;
      const childrenOfTarget = getSortedChildren(targetId);
      const maxOrder = childrenOfTarget.reduce((m, id) => Math.max(m, treeState[id].sort_order), 0);
      treeState[dragId].sort_order = maxOrder + 10;
      changes.add(dragId);
    } else {
      // Reorder within same parent
      const newParent = treeState[targetId].parent;
      treeState[dragId].parent = newParent;

      // Get siblings excluding dragged, insert at new position
      const sibs = getSortedChildren(newParent).filter(id => id !== dragId);
      const targetIdx = sibs.indexOf(targetId);
      const insertAt = position === 'after' ? targetIdx + 1 : targetIdx;
      sibs.splice(insertAt, 0, dragId);

      // Assign contiguous sort_orders: 10, 20, 30...
      sibs.forEach((id, i) => {
        treeState[id].sort_order = (i + 1) * 10;
        changes.add(id);
      });
    }
  }

  function applyDropToRoot(dragId) {
    treeState[dragId].parent = null;
    const roots = getSortedChildren(null);
    const maxOrder = roots.filter(id => id !== dragId)
      .reduce((m, id) => Math.max(m, treeState[id].sort_order), 0);
    treeState[dragId].sort_order = maxOrder + 10;
    changes.add(dragId);
  }

  // ── Rendering — builds DOM nodes (no innerHTML with untrusted data) ─────────
  function buildNodeEl(id) {
    const doc = docMap[id];
    if (!doc) return null;

    const li = document.createElement('li');
    li.className = 'tree-node';
    li.dataset.id = id;

    const row = document.createElement('div');
    row.className = 'node-row';
    row.draggable = true;
    row.dataset.id = id;

    // Drag handle
    const handle = document.createElement('span');
    handle.className = 'drag-handle';
    handle.textContent = '\u2807'; // ⠷ braille dots used as handle icon
    handle.setAttribute('aria-hidden', 'true');

    // Title
    const titleEl = document.createElement('span');
    titleEl.className = 'node-title' + (changes.has(id) ? ' changed' : '');
    titleEl.textContent = doc.title;

    // Slug
    const slugEl = document.createElement('span');
    slugEl.className = 'node-slug';
    slugEl.textContent = doc.slug;

    // Sort order
    const orderEl = document.createElement('span');
    orderEl.className = 'node-order';
    orderEl.textContent = treeState[id].sort_order;

    row.appendChild(handle);
    row.appendChild(titleEl);
    row.appendChild(slugEl);
    row.appendChild(orderEl);

    // Drag events on the row
    row.addEventListener('dragstart', e => {
      draggedId = id;
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('text/plain', id);
    });
    row.addEventListener('dragend', () => {
      row.classList.remove('over-before', 'over-after', 'over-child');
    });
    row.addEventListener('dragover', e => {
      if (!draggedId || draggedId === id) return;
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
      const pos = getDropPosition(e, row);
      row.classList.remove('over-before', 'over-after', 'over-child');
      row.classList.add(pos === 'before' ? 'over-before' : pos === 'after' ? 'over-after' : 'over-child');
    });
    row.addEventListener('dragleave', () => {
      row.classList.remove('over-before', 'over-after', 'over-child');
    });
    row.addEventListener('drop', e => {
      e.preventDefault();
      row.classList.remove('over-before', 'over-after', 'over-child');
      if (!draggedId) return;
      const pos = getDropPosition(e, row);
      applyDrop(draggedId, id, pos);
      draggedId = null;
      renderTree();
      document.getElementById('save-btn').disabled = changes.size === 0;
    });

    li.appendChild(row);

    // Children
    const children = getSortedChildren(id);
    if (children.length) {
      const ul = document.createElement('ul');
      ul.className = 'tree-children';
      for (const childId of children) {
        const childEl = buildNodeEl(childId);
        if (childEl) ul.appendChild(childEl);
      }
      li.appendChild(ul);
    }

    return li;
  }

  function renderTree() {
    const container = document.getElementById('tree-container');
    const roots = getSortedChildren(null);
    const ul = document.createElement('ul');
    ul.className = 'tree-root';
    for (const id of roots) {
      const el = buildNodeEl(id);
      if (el) ul.appendChild(el);
    }
    container.textContent = ''; // clear without innerHTML
    container.appendChild(ul);
  }

  // ── Save ───────────────────────────────────────────────────────────────────
  async function saveChanges() {
    const statusEl = document.getElementById('status');
    const saveBtn = document.getElementById('save-btn');
    saveBtn.disabled = true;
    statusEl.textContent = `Saving ${changes.size} page(s) to GitHub...`;
    statusEl.className = 'status';

    const failed = [];
    for (const id of [...changes]) {
      try {
        const s = treeState[id];
        await patchPageOnGitHub(id, s.parent, s.sort_order);
      } catch (e) {
        console.error('Failed to save', id, e);
        failed.push(docMap[id]?.slug || id);
      }
    }

    if (failed.length) {
      statusEl.textContent = `Errors saving: ${failed.join(', ')}. See console for details.`;
      statusEl.className = 'status error';
      saveBtn.disabled = false;
    } else {
      changes.clear();
      statusEl.textContent = 'Saved. GitHub Actions will rebuild the wiki shortly.';
      statusEl.className = 'status success';
    }
  }

  // ── Init ───────────────────────────────────────────────────────────────────
  (async function init() {
    const statusEl = document.getElementById('status');
    const saveBtn = document.getElementById('save-btn');

    githubToken = loadGithubAuth();
    if (!githubToken) {
      statusEl.textContent = 'Not authenticated. Log in via CMS Admin first, then return here.';
      statusEl.className = 'status error';
      return;
    }

    try {
      await loadData();
    } catch (e) {
      statusEl.textContent = `Load error: ${e.message}`;
      statusEl.className = 'status error';
      return;
    }

    if (!githubRepo) {
      statusEl.textContent = 'GitHub repo not configured. Set github.repo in config.yml.';
      statusEl.className = 'status error';
      return;
    }

    const pageCount = Object.keys(docMap).length;
    statusEl.textContent = `${pageCount} pages loaded. Drag to reorder or reparent. Changed items appear in orange.`;

    renderTree();
    saveBtn.disabled = true;
    saveBtn.addEventListener('click', saveChanges);

    // Root drop zone
    const dropRoot = document.getElementById('drop-root');
    dropRoot.addEventListener('dragover', e => {
      e.preventDefault();
      dropRoot.classList.add('active');
    });
    dropRoot.addEventListener('dragleave', () => dropRoot.classList.remove('active'));
    dropRoot.addEventListener('drop', e => {
      e.preventDefault();
      dropRoot.classList.remove('active');
      if (!draggedId) return;
      applyDropToRoot(draggedId);
      draggedId = null;
      renderTree();
      saveBtn.disabled = false;
    });
  })();
  </script>
</body>
</html>
```

**Verify:** Log in to Decap admin. Navigate to `admin/tree.html`. Confirm tree renders all pages in sort_order. Drag a page above a sibling — confirm it moves and turns orange, and its sort_order updates visually. Drag a page onto another node — confirm it becomes a child (indented). Drag a child to the root drop zone — confirm it becomes root-level. Click "Save Changes" — confirm GitHub commits appear in the repo for every changed page. After Actions rebuild, confirm new order reflects in main wiki sidebar.

---

## Self-Review

**Spec coverage:**
- Create page button → Task 3 (New Page in index.html nav)
- Edit page button → Task 3 (Edit Page in page.html nav, links to Decap by slug)
- Decap direct commits → Task 2 (no editorial_workflow in decap.yml)
- Slug immutable after creation → Task 2 (hint text in Decap field, build hard-fails on duplicate)
- Slug uniqueness → Task 1a (build hard exit) + Task 2c (preSave block)
- Slug collision suggestion → Task 2c (suggests `{slug}-2` etc.)
- Duplicate title soft warning → Task 1a (build warn) + Task 2c (orange banner)
- Frontmatter parent slug → Task 1b (compute_hierarchy reads parent_slug, resolves to full id)
- Children computed at build → Task 1b (populates children[] array)
- sort_order frontmatter → Task 1a (extracted into index), Task 4 (used for sidebar sort)
- Auto last-updated on content change → Task 1c (hash comparison + write-back)
- Drag-to-reorder → Task 5 (before/after sibling drop recalculates sort_orders)
- Drag-to-reparent → Task 5 (onto-child drop updates parent field)
- Combined tree/parent edit page → Task 5 (single tree.html page handles both)

**Security:** All dynamic HTML in tree.html is built with `textContent` or `document.createElement` — no `innerHTML` with untrusted data. The `escapeHtml()` helper is available for any string that must go into HTML context. Admin pre-check banner uses `textContent` for the title string.

**Type consistency:** `entry["slug"]`, `entry["sort_order"]`, `entry["parent"]` added in Task 1 and consumed in Tasks 2–5. `treeState[id].parent` in Task 5 always holds a full `id` (or null), never a slug — same convention as `search_index.json`.
