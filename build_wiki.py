#!/usr/bin/env python3
"""Lorengine build script — generates search_index.json and assembles _site/.

Stdlib only (Python 3.11+). No pip dependencies.
"""

import json
import os
import re
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Minimal YAML parser (2-level deep, simple scalars/lists only)
# ---------------------------------------------------------------------------

def parse_yaml(text):
    """Parse a simple 2-level YAML structure into a dict of dicts.

    Handles: strings (quoted or unquoted), integers, booleans,
    inline lists like ["a", "b"], and empty strings.
    """
    result = {}
    current_section = None

    for line in text.splitlines():
        # Skip blank lines and comments
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Top-level key (no leading whitespace)
        if not line[0].isspace() and ":" in line:
            key = stripped.split(":")[0].strip()
            value_part = stripped[len(key) + 1:].strip()
            if not value_part:
                # Section header
                current_section = key
                result[current_section] = {}
            else:
                result[key] = _parse_value(value_part)
            continue

        # Indented key (child of current section)
        if current_section is not None and ":" in stripped:
            key = stripped.split(":")[0].strip()
            value_part = stripped[len(key) + 1:].strip()
            result[current_section][key] = _parse_value(value_part)

    return result


def _parse_value(raw):
    """Convert a raw YAML value string to a Python type."""
    if not raw:
        return ""

    # Strip inline comments (but not inside quotes)
    if not raw.startswith('"') and not raw.startswith("'") and not raw.startswith("["):
        comment_pos = raw.find(" #")
        if comment_pos != -1:
            raw = raw[:comment_pos].strip()

    # Booleans
    if raw.lower() in ("true", "yes"):
        return True
    if raw.lower() in ("false", "no"):
        return False

    # Integers
    try:
        return int(raw)
    except ValueError:
        pass

    # Quoted strings
    if (raw.startswith('"') and raw.endswith('"')) or \
       (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]

    # Inline list: ["a", "b", "c"]
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        items = []
        for item in inner.split(","):
            item = item.strip().strip('"').strip("'")
            if item:
                items.append(item)
        return items

    return raw


# ---------------------------------------------------------------------------
# Frontmatter parser
# ---------------------------------------------------------------------------

def parse_frontmatter(text):
    """Extract YAML frontmatter and body from a markdown file.

    Returns (metadata_dict, body_string). If no valid frontmatter found,
    returns (None, text).
    """
    if not text.startswith("---"):
        return None, text

    # Find the closing ---
    end = text.find("---", 3)
    if end == -1:
        return None, text

    fm_text = text[3:end].strip()
    body = text[end + 3:].strip()

    metadata = {}
    for line in fm_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key = line.split(":")[0].strip()
        value_part = line[len(key) + 1:].strip()
        metadata[key] = _parse_value(value_part)

    return metadata, body


# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------

def extract_headings(body):
    """Extract ## and ### headings from markdown body."""
    headings = []
    for line in body.splitlines():
        m = re.match(r"^#{2,3}\s+(.+)$", line)
        if m:
            headings.append(m.group(1).strip())
    return headings


def strip_markdown(text):
    """Strip common markdown syntax to produce plain text."""
    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`[^`]+`", "", text)
    # Remove headings markers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Remove bold/italic
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}([^_]+)_{1,3}", r"\1", text)
    # Remove links but keep text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Remove images
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Collapse whitespace
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def load_config(root):
    """Load config.yml and return parsed dict with defaults."""
    config_path = root / "config.yml"
    defaults = {
        "wiki": {
            "title": "My Wiki",
            "description": "A Lorengine-powered wiki",
            "accent_color": "#7F77DD",
        },
        "ai": {
            "model": "claude-sonnet-4-6",
            "system_prompt_file": "CLAUDE.local.md",
            "max_tokens": 1024,
            "enable_prompt_caching": True,
        },
        "search": {
            "max_results": 20,
            "excerpt_length": 160,
        },
        "github_pages": {
            "base_url": "",
        },
    }

    if not config_path.exists():
        print("Warning: config.yml not found, using defaults")
        return defaults

    raw = config_path.read_text(encoding="utf-8")
    parsed = parse_yaml(raw)

    # Merge parsed over defaults
    for section, section_defaults in defaults.items():
        if section not in parsed:
            parsed[section] = section_defaults
        elif isinstance(section_defaults, dict):
            for key, val in section_defaults.items():
                if key not in parsed[section]:
                    parsed[section][key] = val

    return parsed


# ---------------------------------------------------------------------------
# Search index generation
# ---------------------------------------------------------------------------

def build_search_index(root):
    """Walk docs/ and build the search index entries."""
    docs_dir = root / "docs"
    if not docs_dir.exists():
        print("Warning: docs/ directory not found")
        return []

    entries = []
    for md_path in sorted(docs_dir.rglob("*.md")):
        rel_path = md_path.relative_to(root).as_posix()
        text = md_path.read_text(encoding="utf-8")

        metadata, body = parse_frontmatter(text)
        if metadata is None or "title" not in metadata:
            print(f"Warning: skipping {rel_path} — missing title in frontmatter")
            continue

        headings = extract_headings(body)
        plain_body = strip_markdown(body)
        excerpt = plain_body[:300]

        entry = {
            "id": rel_path,
            "title": metadata.get("title", ""),
            "tags": metadata.get("tags", []),
            "status": metadata.get("status", "draft"),
            "last_updated": str(metadata.get("last-updated", "")),
            "headings": headings,
            "excerpt": excerpt,
            "body": plain_body,
        }
        entries.append(entry)

    return entries


# ---------------------------------------------------------------------------
# Site assembly
# ---------------------------------------------------------------------------

def assemble_site(root, config, search_index):
    """Copy wiki templates + docs into _site/, inject config values."""
    site_dir = root / "_site"

    # Clean previous build
    if site_dir.exists():
        shutil.rmtree(site_dir)
    site_dir.mkdir()

    wiki_dir = root / "wiki"
    docs_dir = root / "docs"

    # Copy wiki files into _site/
    if wiki_dir.exists():
        for f in wiki_dir.iterdir():
            if f.is_file():
                shutil.copy2(f, site_dir / f.name)

    # Copy docs/ into _site/docs/
    if docs_dir.exists():
        shutil.copytree(docs_dir, site_dir / "docs")

    # Write search_index.json into _site/
    index_path = site_dir / "search_index.json"
    index_path.write_text(
        json.dumps(search_index, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Build replacement map from config
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    replacements = {
        "{{WIKI_TITLE}}": str(config["wiki"]["title"]),
        "{{WIKI_DESCRIPTION}}": str(config["wiki"]["description"]),
        "{{ACCENT_COLOR}}": str(config["wiki"]["accent_color"]),
        "{{AI_MODEL}}": str(config["ai"]["model"]),
        "{{AI_MAX_TOKENS}}": str(config["ai"]["max_tokens"]),
        "{{AI_SYSTEM_PROMPT_FILE}}": str(config["ai"]["system_prompt_file"]),
        "{{AI_ENABLE_PROMPT_CACHING}}": str(config["ai"]["enable_prompt_caching"]).lower(),
        "{{BASE_URL}}": str(config["github_pages"]["base_url"]),
        "{{SEARCH_MAX_RESULTS}}": str(config["search"]["max_results"]),
        "{{SEARCH_EXCERPT_LENGTH}}": str(config["search"]["excerpt_length"]),
        "{{ANTHROPIC_API_KEY}}": api_key,
    }

    # Inject into HTML and JS files
    for f in site_dir.iterdir():
        if f.is_file() and f.suffix in (".html", ".js", ".css"):
            content = f.read_text(encoding="utf-8")
            for placeholder, value in replacements.items():
                content = content.replace(placeholder, value)
            f.write_text(content, encoding="utf-8")

    return site_dir


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    root = Path(__file__).resolve().parent

    print("Lorengine build starting...")

    # 1. Load config
    config = load_config(root)
    print(f"  Wiki: {config['wiki']['title']}")

    # 2. Build search index
    search_index = build_search_index(root)
    print(f"  Indexed {len(search_index)} document(s)")

    # 3. Write search_index.json to repo root (committed artifact)
    index_path = root / "search_index.json"
    index_path.write_text(
        json.dumps(search_index, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"  Wrote {index_path}")

    # 4. Assemble _site/
    site_dir = assemble_site(root, config, search_index)
    print(f"  Assembled site in {site_dir}")

    print("Build complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
