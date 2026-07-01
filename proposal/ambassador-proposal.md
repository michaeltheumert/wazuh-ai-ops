# Proposal: AI-Augmented Wazuh Operations

## Series Overview

Most AI-in-security articles fall into one of two categories: theoretical frameworks that never touch a real SIEM, or automation demos that skip the hard questions about validation and control.

This series is neither.

*AI-Augmented Wazuh Operations* covers how AI can be integrated into Wazuh-based security operations in a way that is practical, verifiable, and auditable. Not AI as a replacement for analysts — AI as a tool that handles the repetitive, well-defined work quickly enough that analysts can spend their time on the cases that actually require judgment.

Each article is grounded in real implementation experience. The code runs. The rules are validated against real Wazuh environments. The governance questions are answered before deployment, not after.

---

## Why This Series

The Wazuh community has strong content on detection engineering, rule development, and incident response. What is largely missing is guidance on where controlled AI integration fits into those workflows — and where it does not belong.

That gap matters. Organizations are actively evaluating LLM-assisted workflows for security operations, often without a clear framework for what "responsible" means in this context: which data can be sent to an external API, how AI-generated rules should be validated, and what decisions must remain with a human analyst.

This series provides that framework, using Wazuh as the implementation environment throughout.

---

## Planned Articles

| # | Article | Core Question |
|---|---------|---------------|
| 1 | **Taming Alert Fatigue** | How can AI reduce false positives without creating new blind spots? |
| 2 | **Responsible AI in Security Operations** | When is AI allowed to process real security telemetry — and what governance controls are required? |
| 3 | **Detection Engineering at Scale** | How can AI assist in developing Wazuh detection rules for attack techniques that have not been seen yet? |
| 4 | **Alert Enrichment and Triage Automation** | How can AI give analysts the contextual understanding that currently requires senior experience? |
| 5 | **AI Does Not Replace Analysts** | Which decisions should stay with a human — and why that is an architectural choice, not a philosophical one? |

The sequence is deliberate. Article 1 establishes a concrete use case. Article 2 addresses governance immediately — before the technical depth of Articles 3 and 4 — because responsible AI integration is not an appendix. Article 5 steps back and draws the boundary that holds the entire framework together.

---

## About the Author

Michael Theumert is Co-Founder of SECaaS.IT (XaaS Enterprise GmbH), a Munich-based cybersecurity company focused on security operations, detection engineering, and AI-assisted security services. He serves as CISO at ValueMiner GmbH and as a Wazuh Ambassador.

His work focuses on building and operating security services in regulated environments, where detection quality, auditability, and operational efficiency must coexist.

---

## Proposed Timeline

| Month | Article |
|-------|---------|
| August 2026 | Taming Alert Fatigue |
| September 2026 | Responsible AI in Security Operations |
| October 2026 | Detection Engineering at Scale |
| November 2026 | Alert Enrichment and Triage Automation |
| December 2026 | AI Does Not Replace Analysts |
