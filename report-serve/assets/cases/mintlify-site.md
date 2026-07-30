# Mintlify

[www.mintlify.com/docs](https://www.mintlify.com/docs)

- **Overall score:** 100/100 (Grade A+)
- **Checks passed:** 27 / 30
- **Last computed:** 2026-07-30

## Components

### Content Discoverability

- **Score:** 99/100 · **Status:** partial
- **Summary:** 1 warning across 7 AFDocs checks.
- **Rationale:** Agents need a clear entry point and crawl map before they can reliably discover the right pages.
- **Reference:** [AFDocs reference](https://afdocs.dev)

**Checks**

- ✅ **LLMS TXT Exists** — llms.txt found at https://www.mintlify.com/docs/llms.txt
- ✅ **LLMS TXT Valid** — llms.txt follows the proposed structure (H1, blockquote, heading-delimited link sections)
- ✅ **LLMS TXT Size** — llms.txt is 49,833 characters (under 50,000 threshold)
- ✅ **LLMS TXT Links Resolve** — All 15 same-origin sampled links resolve (226 total links)
- ✅ **LLMS TXT Links Markdown** — 15/15 same-origin sampled links point to markdown content (100%)
- ⚠️ **LLMS TXT Directive Html** — llms.txt directive found in HTML of 14 of 15 sampled pages (1 missing) An llms.txt directive was found in the HTML of some pages but is missing from others, or is buried deep in the page. Ensure the directive appears near the top of every documentation page.
- ✅ **LLMS TXT Directive MD** — llms.txt directive found in markdown of all 14 sampled pages, near the top of content; 1 had no markdown version

### Markdown Availability

- **Score:** 100/100 · **Status:** pass
- **Summary:** 2 AFDocs checks pass.
- **Rationale:** When markdown is available directly, agents spend less effort stripping presentation markup and guessing structure.
- **Reference:** [AFDocs reference](https://afdocs.dev)

**Checks**

- ✅ **Markdown Url Support** — 14/14 sampled pages support .md URLs (100%)
- ✅ **Content Negotiation** — 14/14 sampled pages support content negotiation (100%)

### Page Size and Truncation Risk

- **Score:** 100/100 · **Status:** pass
- **Summary:** 4 AFDocs checks pass.
- **Rationale:** Large pages and delayed primary content increase truncation risk and make retrieval less reliable.
- **Reference:** [AFDocs reference](https://afdocs.dev)

**Checks**

- ✅ **Rendering Strategy** — All 15 sampled pages contain server-rendered content
- ✅ **Page Size Markdown** — All 14 pages under 50K chars (median 5K, max 18K)
- ✅ **Page Size Html** — All 15 sampled pages under 50K chars (median 421K HTML → 14K markdown (90% boilerplate))
- ✅ **Content Start Position** — Content starts within first 10% on all 15 sampled pages (median 1%)

### Content Structure

- **Score:** 100/100 · **Status:** pass
- **Summary:** 3 AFDocs checks pass.
- **Rationale:** Predictable sections, valid code fences, and serialized tabs make the content easier for agents to parse correctly.
- **Reference:** [AFDocs reference](https://afdocs.dev)

**Checks**

- ✅ **Tabbed Content Serialization** — No tabbed content detected across 15 sampled pages
- ✅ **Section Header Quality** — No tabbed content found; header quality check not applicable
- ✅ **Markdown Code Fence Validity** — All 40 code fences properly closed across 15 pages

### URL Stability and Redirects

- **Score:** 100/100 · **Status:** pass
- **Summary:** 2 AFDocs checks pass.
- **Rationale:** Stable URLs and sane redirect behavior prevent retrieval drift and broken tool references.
- **Reference:** [AFDocs reference](https://afdocs.dev)

**Checks**

- ✅ **Http Status Codes** — All 15 sampled pages return proper error codes for bad URLs
- ✅ **Redirect Behavior** — All 1 redirect(s) across 15 sampled pages are same-host HTTP redirects

### Observability and Content Health

- **Score:** 99/100 · **Status:** partial
- **Summary:** 1 warning across 3 AFDocs checks.
- **Rationale:** Coverage, parity, and cache behavior determine whether agents can trust the content they retrieve.
- **Reference:** [AFDocs reference](https://afdocs.dev)

**Checks**

- ✅ **LLMS TXT Coverage** — llms.txt covers 100% of 219 sitemap doc pages; 6 llms.txt links not in sitemap (may indicate stale links or incomplete sitemap)
- ⚠️ **Markdown Content Parity** — 1 of 14 pages have minor content differences between markdown and HTML 1 pages have minor content differences between their markdown and HTML versions. If this is intentional audience segmentation, adjust --parity-pass-threshold and --parity-warn-threshold (set both to 0 for informational mode).
- ✅ **Cache Header Hygiene** — All 16 endpoints have appropriate cache headers

### Authentication and Access

- **Score:** 100/100 · **Status:** partial
- **Summary:** 1 skipped across 2 AFDocs checks.
- **Rationale:** Agents need either public access or a clear alternative path when documentation is gated behind auth.
- **Reference:** [AFDocs reference](https://afdocs.dev)

**Checks**

- ✅ **Auth Gate Detection** — All 15 sampled pages are publicly accessible
- ⏭️ **Auth Alternative Access** — All docs pages are publicly accessible; no alternative access paths needed

### Full Content Discoverability

- **Score:** 100/100 · **Status:** pass
- **Summary:** llms-full.txt passes all checks.
- **Rationale:** A full-document snapshot gives long-context agents a single canonical corpus to ingest without repeated crawling.
- **Reference:** [llms-full.txt guide](https://www.mintlify.com/docs/ai/llmstxt#llms-full-txt)

**Checks**

- ✅ **LLMS Full Exists** — Found llms-full.txt.
- ✅ **LLMS Full Size** — llms-full.txt size is within the expected range.
- ✅ **LLMS Full Valid** — llms-full.txt has a recognizable markdown structure.
- ✅ **LLMS Full Links Resolve** — llms-full.txt links resolve successfully.

### Agent Skills

- **Score:** 100/100 · **Status:** pass
- **Summary:** skill.md passes all checks.
- **Rationale:** Agent skills provide product-specific operating guidance that plain documentation pages do not encode on their own.
- **Reference:** [skill.md guide](https://www.mintlify.com/docs/ai/skillmd)

**Checks**

- ✅ **Skill MD** — Found an agent skill definition.

### MCP Server

- **Score:** 100/100 · **Status:** pass
- **Summary:** MCP passes all checks.
- **Rationale:** A discoverable MCP server lets agents use first-class tools instead of scraping pages and inferring behavior.
- **Reference:** [MCP guide](https://www.mintlify.com/docs/ai/model-context-protocol)

**Checks**

- ✅ **MCP Server Discoverable** — Found an MCP server.
- ✅ **MCP Tool Count** — The MCP server exposes tools.
