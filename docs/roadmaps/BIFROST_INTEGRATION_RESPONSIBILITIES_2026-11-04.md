# Skry: Query-Time Knowledge and Evidence

**Date:** 2026-11-04  
**Repository:** `hrabanazviking/skry-kg`  
**Implementation status:** Roadmap only; no application code modified.

## Relationship to the master roadmap

- **Canonical roadmap:** https://github.com/hrabanazviking/bifrost-viewer/blob/main/docs/roadmaps/BIFROST_SECOND_BRAIN_MASTER_EXPANSION_ROADMAP_2026-11-04.md
- **Local full copy:** [BIFROST_SECOND_BRAIN_MASTER_EXPANSION_ROADMAP_2026-11-04.md](BIFROST_SECOND_BRAIN_MASTER_EXPANSION_ROADMAP_2026-11-04.md)
- **Status:** Proposed work, not existing functionality. Confirm actual current installed state and protect existing data before writing code.
- **Ownership:** Bifröst Viewer coordinates the Second Brain. Skein and Skry own their APIs. Integrations must use documented, authenticated contracts and cannot assume direct PostgreSQL access.
- **Security:** Public Markdown only. No actual keys, OAuth client secrets, vault values, database passwords, user documents, personal account identifiers, logs, private state paths or private URLs.
- **Compatibility:** Preserve existing code behavior, published interfaces, licenses and attribution. Changes should be opt-in, reversible and regression-tested.

## Goal

Remain fast and read-only while consuming versioned Skein graph generations and exposing well-validated evidence-bearing query results to Bifröst and other authorized applications.

## Repository-specific engineering responsibilities

1. Keep Skry read-only: no canonical source modifications, ingestion, graph rebuilds or credential management.
2. Extend the public query contract with optional graph generation selection and vocabulary freshness metadata.
3. Offer open-vocabulary fallback when latest Skein vocabulary is stale or missing, and visibly distinguish fallback quality.
4. Support evidence chunk IDs, source version, freshness, scope and partial-result warnings.
5. Provide bounded query fanout, timeouts, cached metadata and batch query endpoints for authorized apps without global graph recomputation.
6. Add user-visible query diagnostics for the Skry Observatory: extraction mode, candidate counts, source coverage and timing.
7. Version search/embedding compatibility and protect against cross-corpus data leaks.

## Engineering and security gates

- [ ] New source chunks are searchable before a new Skein build if allowed by existing indices.
- [ ] No Skry method writes derived or canonical tables.
- [ ] A stale known-vocabulary graph is never represented as complete and fresh.
- [ ] Authorized app sees only corpus and passages permitted by its scope.

## Delivery sequence

1. Read this repository's own architectural rules, domain boundaries and current source before editing.
2. Audit installed and unpublished development work; never assume a feature is absent simply because it is missing from the current public default branch.
3. Design a versioned optional integration through published API contracts; preserve baseline behavior.
4. Implement synthetic fixtures, unit tests, integration tests, timeouts and permission checks.
5. Test disconnection, false/stale results, recovery and security canaries.
6. Document capability level and deployment directions without secrets; require owner approval before live rollout.

**Canonical authority:** The primary Bifröst Viewer roadmap above resolves conflicts; individual source code and verified deployed evidence establish what is actually implemented.

