<!-- STATUS: Planned | Lead: Sigl | Co-author: Theumert | Target: August 2026 Week 4 -->

# Alert Enrichment and Triage Automation

*Article 4 of 5 — AI-Augmented Wazuh Operations*

---

## [DRAFT NOTES — remove before publication]

**Core question:** How can AI give analysts the contextual understanding that currently requires senior experience?

**Key argument:** Triage quality is a function of context, not just data. AI can assemble context faster than a Tier-1 analyst — but the disposition decision stays human.

**Dominik's perspective:** SOC operations, what Tier-1 analysts actually struggle with, where time is lost in triage.

**Leitmotiv to include:** "Judgment before delegation."

**Sections to cover:**
- What triage actually costs: not time per alert, but time per correct decision
- The context problem: what an experienced analyst brings that the alert doesn't contain
- Enrichment sources: IP reputation, asset context, user profile, historical activity
- AI as summarizer: "what happened here, in three sentences"
- Wazuh + n8n + LLM: a concrete pipeline sketch
- Escalation: what the AI surfaces, what the analyst decides
- Why this is not SOAR — and why that's not a contradiction

---

## [Article begins here]

<!-- Opening: A Tier-1 analyst looking at an alert.
     The alert is technically complete. The context is missing.
     What does it take to make a good triage decision?
     Name the gap between "the data is there" and "the decision is easy". -->

## What Triage Actually Costs

<!-- It's not time per alert. It's time per correct decision.
     False negatives are invisible. False positives accumulate into fatigue.
     The bottleneck is not processing speed — it's contextual judgment at volume. -->

## The Context an Alert Doesn't Contain

<!-- What an experienced analyst brings to a Wazuh alert:
     - Is this host normally noisy?
     - Is this user on a business trip?
     - Did this IP appear in three other alerts this week?
     - Is this process expected on this asset class?
     None of this is in the alert. It has to be assembled. -->

## Enrichment: Assembling the Picture

<!-- IP reputation (external feeds), asset context (CMDB),
     user profile (directory / HR system), historical alert frequency.
     What can be automated, what requires a human data source.
     Practical: which enrichment sources are available in a typical Wazuh deployment. -->

## AI as Analyst Assistant

<!-- The summarization task: given alert + enrichment data,
     produce a three-sentence triage brief.
     Not a disposition. A brief.
     Prompt structure. Example output. What it gets wrong. -->

## A Concrete Pipeline: Wazuh + n8n + LLM

<!-- Architecture sketch: Wazuh webhook → n8n → enrichment APIs → LLM → analyst dashboard.
     What n8n handles, what the LLM handles, what stays with the analyst.
     Data flow: what leaves the pipeline boundary (and the governance implications from Article 2). -->

## Escalation: AI Surfaces, Analyst Decides

<!-- The pipeline's output is a prioritized brief, not a verdict.
     What "escalate" means in this context.
     Why the AI should never close a ticket unilaterally.
     The accountability chain: who made the decision, and when. -->

## This Is Not SOAR — And That's Not a Contradiction

<!-- SOAR automates response actions. This pipeline enriches triage input.
     They are complementary, not competing.
     Where this pipeline ends and SOAR begins.
     Why conflating them is an architectural mistake. -->

## Conclusion

<!-- Judgment before delegation.
     AI can assemble context at analyst speed.
     It cannot evaluate whether the context it assembled is complete,
     or whether the pattern it summarized matters in this specific environment.
     That call stays human. -->

---

*Next in this series: [AI Does Not Replace Analysts](./05-ai-does-not-replace-analysts.md)*
