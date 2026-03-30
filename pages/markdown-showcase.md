---
title: "Markdown Showcase"
tags: ["docs", "reference", "markdown"]
status: final
last-updated: 2026-03-30
sort_order: 2
---

## About This Section

This section is a **live reference** for every markdown feature supported in this wiki. Each page demonstrates real syntax with rendered output — use it to look up how to write something, or copy blocks directly into your own pages.

The wiki renders markdown using **marked.js** with syntax highlighting via **highlight.js**.

## Subsections

### → [Text Formatting](markdown-showcase/text-formatting.md)

Bold, italic, strikethrough, inline code, superscript, subscript, horizontal rules, and escape sequences.

### → [Tables & Lists](markdown-showcase/tables-and-lists.md)

All list variants (ordered, unordered, nested, task lists) and tables with column alignment.

### → [Code & Blocks](markdown-showcase/code-and-blocks.md)

Fenced code blocks with syntax highlighting, inline code, blockquotes (single and nested), and preformatted text.

### → [Links & Cross-References](markdown-showcase/links-and-cross-references.md)

Internal wiki page links, external links, anchor links within a page, and reference-style links.

---

## Markdown Quick-Reference

| Element | Syntax | Notes |
|---------|--------|-------|
| **Bold** | `**text**` | |
| *Italic* | `*text*` or `_text_` | |
| ~~Strikethrough~~ | `~~text~~` | |
| `Inline code` | `` `code` `` | |
| Blockquote | `> text` | |
| H2 heading | `## Heading` | Use H2 as top-level |
| H3 heading | `### Heading` | |
| Ordered list | `1. item` | Numbers auto-increment |
| Unordered list | `- item` | Or `*` or `+` |
| Table | `\| col \| col \|` + separator row | |
| Code block | ` ```language ` | Language name enables syntax highlight |
| Horizontal rule | `---` | Three or more dashes |
| Internal link | `[Text](slug.md)` | Relative path from current page |
| External link | `[Text](https://...)` | Full URL |

> **H1 is reserved:** The wiki automatically displays your `title` frontmatter field as the page's H1. Don't use `#` in your page body — start at `##`.

