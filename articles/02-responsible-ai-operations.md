<!-- STATUS: In Progress | Lead: Theumert | Co-author: Sigl | Target: August 2026 Week 2 -->

# Responsible AI in Security Operations

*Article 2 of 5 — AI-Augmented Wazuh Operations*

---

## [DRAFT NOTES — remove before publication]

**Core question:** When is AI allowed to process real security telemetry — and what governance controls are required?

**Key argument:** Governance is not an appendix. It is architecture. The question "may we?" precedes "can we?" — and answering it requires written decisions, not assumptions.

**Dominik's contribution:** Section on data residency in German-regulated environments — the "100% Deutschland" approach as a concrete implementation of the principles described here.

**Leitmotiv to include:** "Validation before automation." / "Judgment before delegation."

**Sections to cover:**
- What Wazuh alerts actually contain (and why it matters)
- The public API problem: what leaves the organization when you send alert data out
- GDPR, HIPAA, NIS2: the regulatory reality for security telemetry
- Self-hosted models: the architecture of staying in control
- Data residency in practice: the iSecNG approach (Sigl)
- What to put in writing before going live
- The ADR template: documenting the backend decision

---

## [Article begins here]

<!-- Opening: Start with a concrete scenario, not a definition.
     Example angle: An analyst pastes an alert into ChatGPT to understand it faster.
     It works. Nobody thought about what just left the building. -->

## The Data in Your Alerts

<!-- What Wazuh alerts actually contain: hostnames, usernames, source IPs, process names,
     command-line arguments, file paths, incident details.
     This is not abstract. Name the fields. -->

## What Leaves the Building

<!-- Public LLM APIs: what "processing" means in terms of data flow.
     The gap between "we have a DPA" and "we confirmed this covers security telemetry".
     Don't assume. Confirm in writing. -->

## The Regulatory Landscape

<!-- GDPR: personal data in security logs (usernames, IPs).
     NIS2: security of security tooling.
     Customer contracts: the clause that nobody read.
     This section should be practical, not a legal survey. -->

## Self-Hosted Models: Staying in Control

<!-- Architecture: what changes when the inference endpoint is internal.
     The pipeline from Article 1 is backend-agnostic by design — that was intentional.
     Open-weight models: what's available, what works for this use case.
     Tradeoffs: capability vs. control. -->

## Data Residency in Practice

<!-- Dominik Sigl, iSecNG: the 100% Germany approach.
     What "digital sovereignty" means operationally, not philosophically.
     Concrete: where does the data sit, who has access, what does the customer agreement say. -->

## What Needs to Be in Writing

<!-- Before going live with any AI pipeline that processes real alert data:
     - Data processing agreement confirmed for security telemetry (not just generic coverage)
     - Customer disclosure (if processing customer data)
     - Backend decision documented (ADR or equivalent)
     - Review cadence for the decision as models and providers change -->

## The Architecture Decision Record

<!-- Template: a minimal ADR for the "which inference backend" decision.
     Not bureaucracy — accountability.
     The decision that gets made once and reviewed annually. -->

## Conclusion

<!-- Judgment before delegation applies here too:
     The choice of inference backend is not a technical afterthought.
     It is the decision that determines whether the pipeline is trustworthy. -->

---

*Next in this series: [Detection Engineering at Scale](./03-detection-engineering-scale.md)*
