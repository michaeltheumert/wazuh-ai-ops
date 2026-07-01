# Style Guide: AI-Augmented Wazuh Operations

This document defines the shared voice, structure, and editorial rules for all five articles in this series.  
Both authors are expected to follow these guidelines. When in doubt, err toward directness.

---

## Series Voice

**Direct.** Say the thing. No preamble, no throat-clearing.  
**Operational.** Ground every claim in something that can be built, tested, or verified.  
**Honest about limits.** AI has real limits in security contexts. Name them. Don't soften them.  
**No hype.** Words like "revolutionize", "transform", "game-changer" are banned. If you catch yourself writing them, delete the sentence and start over.

---

## Recurring Themes (Use These Deliberately)

Every article should contain at least one of the following — naturally, not as a slogan:

> **"Validation before automation."**

> **"Judgment before delegation."**

These are the two load-bearing ideas of the series. Use them as closing lines, as section openers, or as standalone paragraphs. Never as marketing copy.

The underlying thesis — which Article 5 makes explicit — should be traceable in every article:

> AI does not replace analysts. It reallocates the boundary between routine work and judgment.

In Articles 1–4, this appears implicitly: in the confidence threshold that keeps ambiguous cases out of the pipeline, in the pull request that asks for a review decision rather than original authorship, in the governance controls that answer "may we?" before "can we?". In Article 5, it becomes the main argument.

---

## Structure Rules

### Every article must:

- **Open with a problem from practice** — not a definition, not a statistic, not "In today's rapidly evolving threat landscape"
- **End with a clear boundary** between what AI does and what the analyst decides
- **Include at least one concrete code example or system configuration** (Articles 1–4)
- **Name the limits of the approach** before the conclusion

### Every article must not:

- Open with a dictionary definition
- Use bullet lists as a substitute for argument
- Treat governance as an appendix
- Make claims the implementation doesn't support

---

## Formatting

| Element | Rule |
|---------|------|
| **Length** | 1,200–1,800 words (code blocks excluded) |
| **Language** | English |
| **Headings** | Sentence case, not title case (`## Where AI fits`, not `## Where AI Fits`) |
| **Code blocks** | Always include language tag (` ```python `, ` ```xml `, ` ```bash `) |
| **Emphasis** | Bold for terms introduced for the first time; italics sparingly |
| **Series tag** | Each article opens with: `*Article N of 5 — AI-Augmented Wazuh Operations*` |

---

## What We Do Not Write

| Phrase / Pattern | Why |
|-----------------|-----|
| "In today's rapidly evolving..." | Every article in the world starts this way |
| "Leveraging AI to..." | "Leveraging" is empty |
| "This article will explore..." | Don't announce, do |
| "It is worth noting that..." | If it's worth noting, just note it |
| "Game-changer / revolutionize / transform" | Hype, banned |
| Passive as the main clause of a key argument | Weakens accountability |
| Bullet lists with 1-sentence items that should be prose | Substitutes for thinking |
| Governance mentioned only in a disclaimer at the end | Governance is architecture, not fine print |

---

## Citing Wazuh-Specific Behavior

When describing Wazuh rule behavior, XML schema constraints, or parser behavior:
- Be specific about the Wazuh version tested against
- If a construct is valid in one version but not another, say so
- Do not assert behavior from documentation alone — test it

---

## Collaboration Language

- **Articles:** English
- **Internal communication (GitHub comments, PR reviews, messages):** German, per Du
- **PR review comments:** Concrete and line-specific — "This sentence does X, consider Y" rather than "sounds off"

---

## Series Arc (for reference)

| # | Title | Layer | What it establishes |
|---|-------|-------|---------------------|
| 1 | Taming Alert Fatigue | Improve | The core pattern: AI drafts, system validates, human reviews |
| 2 | Responsible AI in Security Operations | Govern | Governance first, not last — data residency, contractual alignment |
| 3 | Detection Engineering at Scale | Detect | AI-assisted rule creation for techniques not yet seen |
| 4 | Alert Enrichment and Triage Automation | Understand | Context at analyst speed, judgment still human |
| 5 | AI Does Not Replace Analysts | Reflect | The thesis made explicit: reallocating the boundary |

Article 2 at position 2 is deliberate. Governance is not an appendix to this series.
