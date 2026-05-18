# Bug 0001: Uppercase Þ (Thorn) excluded from proper-noun regex

**Discovered:** 2026-05-18 by Auditor (Sólrún Hvítmynd)
**Status:** RESOLVED 2026-05-18

---

## Symptom

`_PROPER_RX = re.compile(r"\b[A-ZÀ-Ý][a-zà-ÿ]+(?:[ \-'][A-ZÀ-Ý][a-zà-ÿ]+)*\b")` —
the uppercase range `[A-ZÀ-Ý]` stops at Ý (U+00DD). Þ (U+00DE) is excluded. The lowercase range `[a-zà-ÿ]` includes þ (U+00FE), so partial matches of names beginning with þ in mid-word position can sneak through inconsistently, but **proper nouns starting with Þ** (Þórr, Þrúðr, Þjazi) are silently lost.

For a project literally themed around Norse mythology, this is the most embarrassing kind of bug.

## Expected

Þ-initial names extracted as proper nouns. The full Latin-1 letter range is covered.

## Invariant violated

Implicit honesty: a Norse-themed entity extractor should know about Thorn.

## Fix plan (additive)

Extend the uppercase range to `[A-ZÀ-Þ]` (still ending at Þ but now inclusive). Better: use `[A-ZÀ-Þà-ÿß]` etc., or switch to the Unicode property class via the `regex` library. For now the additive minimal change is the range extension.

After fix:
```python
_PROPER_RX = re.compile(r"\b[A-ZÀ-Þ][a-zà-ÿß]+(?:[ \-'][A-ZÀ-Þ][a-zà-ÿß]+)*\b")
```

## Lessons

When picking character ranges, write down what each endpoint represents and what's between. `À-Ý` excludes the *one* letter the project actually needs.
