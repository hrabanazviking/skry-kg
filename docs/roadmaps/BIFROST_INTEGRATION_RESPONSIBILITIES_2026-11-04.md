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


## Superseding 2026-11-19 second-brain roadmap: folders and multimodal lore

The owner-approved newer requirements are detailed in Bifröst's canonical [additive roadmap](https://github.com/hrabanazviking/bifrost-viewer/blob/docs/second-brain-incremental-multimodal-gateway-2026-11-19/docs/roadmaps/SECOND_BRAIN_ADDITIVE_INCREMENTAL_MULTIMODAL_GATEWAY_2026-11-19.md) and [managed raw library / folder dedup plan](https://github.com/hrabanazviking/bifrost-viewer/blob/docs/second-brain-incremental-multimodal-gateway-2026-11-19/docs/roadmaps/SECOND_BRAIN_MANAGED_RAW_LIBRARY_FOLDERS_2026-11-19.md).

**Skry remains strictly read-only** and does not watch files, write source records, compute embeddings for ingestion, or replace the existing API. Bifröst/Ingest track raw file locations, multiple identical copies, document versions and folder category ancestry. Skein computes optional derived changes. Skry should consume only published, versioned, provenance-bearing representations through its documented query-time boundary.

- Allow Bifröst to request read-only category- or folder-aware query results, including direct and descendant matches, stable source IDs and active file locations.
- If two files share content hashes but are in different folders, report all permitted folder associations without inventing two independent content facts.
- If a file moves, return its updated current path/category and optional historical path label without requiring a content re-embedding or unrelated query graph rebuild.
- When chunks change, return only validated current evidence and generation IDs; do not cite stale retracted chunks.
- For image/audio/video, return retrieved multimodal segment/caption/asset references and provenance **only through optional adapter contracts**; do not turn Skry's no-storage/no-generation engine into a vision model, raw-media server or duplicate memory database.
- Keep a read-only, whole-brain retrieval default for authorized Janitor/SillyTavern character gateway clients; folder taxonomy is useful metadata rather than mandatory per-character collection permissions.
- Tests: folder rename, move, duplicate copy, changed version, disconnected root, missing permissions, current-vs-old generation and existing search response compatibility.

**Status:** specification only; neither this note nor the canonical plan proves a deployed feature. Repoint links to the merged main-branch canonical docs after acceptance.

## Three-tier retrieval composition (owner decision 2026-11-19)

[Canonical three-tier memory architecture](https://github.com/hrabanazviking/bifrost-viewer/blob/docs/second-brain-incremental-multimodal-gateway-2026-11-19/docs/roadmaps/SECOND_BRAIN_THREE_TIER_MEMORY_ARCHITECTURE_2026-11-19.md): immutable **long-term** evidence, mutable **medium-term** focus domains, volatile **short-term** session context. Skry remains read-only: it returns stable source evidence IDs, currentness/supersession where available, and version/generation tags; it does not write archive payloads, focus weights, volatile sessions, source locations or derived graphs. Bifröst's Memory Composer may boost Skry's read-only results with current medium focus and immediate short-term question context; these signals must not override accepted long-term facts without provenance or hide the rest of the brain. A character may read all authorized long-term and medium evidence through the universal gateway without per-character collection tuning, while separate conversations have distinct ephemeral buffers. Test read-only boundaries, correction/currentness, focus boost without corpus writes, and empty/expired sessions.

## Immutable long-term commit views and read-only historical queries (2026-11-19)

The owner requires [Git-like journaled long-term memory](https://github.com/hrabanazviking/bifrost-viewer/blob/docs/second-brain-incremental-multimodal-gateway-2026-11-19/docs/roadmaps/SECOND_BRAIN_GITLIKE_JOURNALED_ARCHIVE_2026-11-19.md). Skry should optionally retrieve *published* branch/commit-as-of evidence and the compatible Skein graph-generation ID through strictly read-only versioned APIs. Return original immutable source version IDs, currentness/supersession status, commit provenance and branch labels where available. Bifröst Memory Composer defaults every authorized character to the shared approved main knowledge view with no per-character permissions; unapproved branches and private draft lore are not inadvertently exposed. Comparing as-of views may show a previous interpretation without rewriting the modern original archived record. Medium focus weights stay Bifröst mutable metadata, not archive modifications; ephemeral short-term prompts are excluded from any historical query store. Verify old Skry caller defaults unchanged, staged graph not queryable until published, rollback commit reproducibility and no graph/source writes by readers.
