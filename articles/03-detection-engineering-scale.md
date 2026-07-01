<!-- STATUS: Planned | Lead: Sigl | Co-author: Theumert | Target: August 2026 Week 3 -->

# Detection Engineering at Scale

*Article 3 of 5 — AI-Augmented Wazuh Operations*

---

## [DRAFT NOTES — remove before publication]

**Core question:** How can AI assist in developing Wazuh detection rules for attack techniques that have not been seen yet?

**Key argument:** A rule you haven't tested is a rule you don't have. AI accelerates the drafting cycle — but the validation bar stays the same.

**Dominik's perspective:** Hands-on detection engineering experience. What it actually takes to write rules that hold up in production. Where AI helps and where it confidently gets things wrong.

**Leitmotiv to include:** "Validation before automation."

**Sections to cover:**
- The detection engineering bottleneck: why coverage lags behind TTPs
- MITRE ATT&CK → Wazuh rule: the translation problem
- Prompt engineering for rule generation: what works, what doesn't
- The Wazuh XML constraints AI consistently misunderstands
- Validation: same bar as Article 1 — test against the real daemon
- Maintaining rules over time: when a TTP evolves, does the rule?
- What AI cannot do: rules without log knowledge

---

## [Article begins here]

<!-- Opening: Start with the gap.
     Detection coverage is always behind the threat landscape.
     The manual rule-writing bottleneck is real. Name it concretely. -->

## The Coverage Problem

<!-- Why detection lags: time to write, test, review, deploy.
     Every new TTP in the wild is a window of undetected activity.
     This is not about talent. It's about throughput. -->

## MITRE ATT&CK to Wazuh: The Translation Problem

<!-- What ATT&CK gives you: technique descriptions, procedure examples.
     What Wazuh needs: specific log fields, field values, rule logic.
     The gap between "this technique uses process injection" and a valid Wazuh rule.
     AI can help bridge this — with significant caveats. -->

## Prompt Engineering for Rule Generation

<!-- What works: providing log samples, naming the specific fields available,
     constraining to known-valid XML patterns.
     What doesn't: asking for rules without log context.
     Example prompt structure. -->

## The XML Constraints AI Gets Wrong

<!-- Recurring failure modes: non-existent elements, invalid attribute combinations,
     if_sid logic errors, missing rule IDs.
     Why: the Wazuh XML schema is underrepresented in training data.
     Mitigation: the verification loop from Article 1 applies here too. -->

## Validation: The Same Bar

<!-- AI-generated detection rules face exactly the same validation requirement
     as suppression rules from Article 1: test against wazuh-analysisd -t.
     No exception because the intent is detection rather than suppression.
     A rule that loads incorrectly doesn't detect anything. -->

## Rules That Age

<!-- Detection rules are not static. TTPs evolve.
     Who owns a rule after it's written? How does it get reviewed?
     AI can help draft. It cannot track whether a procedure example
     from 2023 still reflects current attacker behavior. -->

## What AI Cannot Do Here

<!-- Rules without log knowledge are rules without grounding.
     AI cannot tell you whether a particular field exists in your environment,
     whether the log format matches the assumption, or whether the rule
     fires on the right events. That requires someone who has seen the logs. -->

## Conclusion

<!-- Validation before automation.
     AI compresses the drafting cycle. It does not replace the engineer
     who knows which logs exist and what the rule is actually supposed to catch. -->

---

*Next in this series: [Alert Enrichment and Triage Automation](./04-alert-enrichment-triage.md)*
