# todos/

Known problems that were found but not fixed yet. One markdown file per problem, so
nothing gets lost when a chat session ends.

**File name:** `NNN-<status>-<priority>-<slug>.md`, e.g. `001-pending-p2-v3-deck-skeleton.md`.
`NNN` is the next free number; it never changes. When the status changes, rename the file
and update the frontmatter to match.

**Frontmatter:**

```yaml
---
status: pending      # pending -> ready -> done (or wontfix)
priority: p2         # p1 = blocks printing/publishing, p2 = should fix, p3 = nice to have
tags: [code, hub]
---
```

**Sections:** Problem (what is wrong and why it matters), Where (files), Proposed fix,
Acceptance (how we know it is done; ideally a test or a command that passes).

Finished a todo? Set `status: done`, rename the file, and mention it in the PR.
