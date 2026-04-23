---
name: docusaurus-anchor-syntax
description: Docusaurus MDX anchor syntax troubleshooting. Use when resolving broken anchor warnings in Docusaurus builds, fixing MDX heading anchors, or debugging link resolution issues in documentation. Triggers on tasks involving anchor syntax, heading IDs, or Docusaurus build warnings about broken links.
metadata:
  author: fireboss
  version: "1.0.0"
---

# Docusaurus MDX Anchor Syntax Guide

## Problem Statement

When defining custom anchors in Docusaurus MDX files using the `{#anchor-id}` syntax, anchors may not be recognized during build, resulting in broken anchor warnings like:

```
Broken anchor on source page path = /docs/risks/sorr:
   -> linking to /docs/risks/sorr#sorr
```

## Key Discovery: h1 vs h2-h6 Behavior

**Critical Limitation**: Docusaurus's `{#anchor-id}` syntax **only works for h2-h6 heading levels**. **h1 headings ignore this syntax** entirely.

| Heading Level | `{#anchor}` Syntax | Works? |
|--------------|-------------------|--------|
| `# Heading` (h1) | `# Heading {#anchor}` | ❌ No |
| `## Heading` (h2) | `## Heading {#anchor}` | ✅ Yes |
| `### Heading` (h3) | `### Heading {#anchor}` | ✅ Yes |

### Why This Happens

- Docusaurus reserves h1 for page titles (extracted from the first `#` heading)
- The `{#anchor}` syntax is processed during MDX compilation for h2-h6
- h1 is treated specially and the custom anchor suffix is silently ignored

## Diagnosis Method

After building, check the generated HTML to verify if an anchor was properly assigned:

```bash
cd docs
npm run build
grep 'id="your-anchor"' build/路徑/index.html
```

**Valid output** (anchor on the heading element itself):
```html
<h2 id="sorr">報酬序列風險 (SoRR)</h2>
```

**Invalid output** (anchor missing or on wrong element):
```html
<header><h1>第三章：退休者的阿基里斯之腱</h1></header>
<!-- id="sorr" is NOT present -->
```

Or if using HTML anchor syntax incorrectly:
```html
<h1><a id="sorr">...</a>報酬序列風險 (SoRR)</h1>
<!-- Anchor is on inner <a>, not on heading - won't work for hash links -->
```

## Solution Pattern

When you need a custom anchor like `#sorr` on what should be a page title:

**❌ Before (Broken)**:
```markdown
# 報酬序列風險 (SoRR) {#sorr}
```

**✅ After (Fixed)**:
```markdown
## 報酬序列風險 (SoRR) {#sorr}
```

The page title can still display the full text; the anchor itself just needs to be on an h2-h6.

## Alternative: HTML Anchor Syntax

If you must use an h1-like structure, use separate HTML anchor element:

```markdown
<a id="sorr"></a>

## 報酬序列風險 (SoRR) {#sorr}
```

But this is **not recommended** because:
1. Creates extra DOM elements
2. Docusaurus may still not recognize it properly
3. h2 approach is cleaner and more maintainable

## Common Pitfalls

1. **Long Chinese headings with special characters**: Docusaurus converts these to auto-generated IDs that don't match your expected anchor
   ```markdown
   # 第三章：退休者的阿基里斯之腱 {#sorr}  ❌ h1 ignored
   ```

2. **Confusing auto-generated vs custom anchors**: Sometimes Docusaurus generates `id="核心內容報酬序列風險-sorr-的底層恐懼"` but you want just `id="sorr"`
   - Solution: Use shorter heading text with h2 level

3. **HTML anchor inside heading doesn't work for hash links**:
   ```markdown
   # <a id="sorr">Title</a>  ❌ Won't work for /page#sorr
   ```
   The anchor is inside the heading, not on the heading element itself.

## Verification Checklist

After fixing anchors, verify with:

```bash
cd docs
npm run build 2>&1 | grep -E "(Broken anchor|SUCCESS)"
```

- **No "Broken anchor" warnings** = All anchors resolved ✅
- **"[SUCCESS] Generated static files"** = Build successful ✅
- Check `build/路徑/index.html` for `id="your-anchor"` presence

## Related Files

- `docs/docs/AGENTS.md` - Contains anchor syntax rules
- `docs/docs/02_risks/03_sorr.md` - Example of working anchor implementation
- `docs/docs/01_basics/01_intro.md` - Example of `{#p-values}` working on h3

## Quick Reference

| Task | Syntax |
|------|--------|
| Custom anchor on h2-h6 | `## Heading {#anchor}` |
| Auto-generated anchor | `## 名詞解釋` → `#名詞解釋` (auto) |
| HTML anchor (fallback) | `<a id="anchor"></a>` + `## Heading` |
