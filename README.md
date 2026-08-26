# wazuh-ai-ops

**Controlled AI integration in Wazuh-based security operations — the code, rules, and decision records behind the article series *AI-Augmented Wazuh Operations*.**

Michael Theumert ([SECaaS.IT](https://www.linkedin.com/in/michael-theumert/)) · Dominik Sigl (iSecNG)

---

This repository is the working companion to a five-part series on where AI belongs in a Wazuh operation — and where it does not. The series argues one position throughout:

> **AI does not get its own rulebook. It has to earn its place inside the engineering discipline that already exists.**

That means everything here is held to the standards the discipline already had: rules are validated against a running Wazuh daemon, not asserted from documentation; the choice of where models run is a governance decision recorded in an ADR, not a default; and every pipeline ends at a human who can be held to the decision.

Two principles carry the series, and they shape the code:

- **Validation before automation.** No generated rule reaches a review queue without passing `wazuh-analysisd -t` against a real instance.
- **Judgment before delegation.** No pipeline closes a ticket, merges a rule, or disposes of an alert on its own. The decision stays with a person.

---

## What's here

```
wazuh-ai-ops/
├── articles/          The five articles + series intro (English, Markdown)
├── adr/               Architecture Decision Records — the governance trail
├── assets/
│   └── diagrams/      Architecture diagram; the validation loop explained
├── workflows/         Reference pipeline sketches (e.g. Wazuh + n8n + LLM)
├── proposal/          Wazuh Ambassador Program proposal
├── CONTRIBUTORS.md
├── style-guide.md
└── README.md
```

> **Status:** The articles publish monthly starting August 2026. Code and rule examples land alongside each article. Until an example is marked *validated*, treat it as a reference to test in your own environment — see [Validation](#validation) below.

---

## The articles

| # | Article | Layer | Core question |
|---|---------|-------|---------------|
| 1 | [Taming Alert Fatigue](./articles/01-taming-alert-fatigue.md) | Improve | How can AI reduce false positives without new blind spots? |
| 2 | [Responsible AI in Security Operations](./articles/02-responsible-ai-operations.md) | Govern | When is AI *allowed* to process real security telemetry? |
| 3 | [Detection Engineering at Scale](./articles/03-detection-engineering-scale.md) | Detect | Can AI help write rules for techniques not yet seen? |
| 4 | [Alert Enrichment and Triage Automation](./articles/04-alert-enrichment-triage.md) | Understand | Can AI give analysts senior-level context at speed? |
| 5 | [AI Does Not Replace Analysts](./articles/05-ai-does-not-replace-analysts.md) | Reflect | Which decisions must stay human, and why? |

Start with the article closest to your problem, or read [the series intro](./articles/00-series-intro.md) for the full arc.

---

## The architecture in one paragraph

A new Wazuh alert enters the pipeline. A lightweight model classifies whether it is a false positive and how confident it is; only high-confidence cases proceed. A higher-capability model drafts the narrowest possible suppression or detection rule. That rule is written into a real Wazuh instance and checked with `wazuh-analysisd -t` — if it fails to load, the daemon's error goes back to the model for a bounded number of fix attempts. A rule that passes opens a pull request with a readable, auditable summary. A human reviews and merges. The model dispatch layer is abstracted, so the inference backend — public API or self-hosted — is a configuration choice, not a rewrite. See [`assets/diagrams/architecture.md`](./assets/diagrams/architecture.md) for the full diagram and the reasoning behind each boundary.

---

## Validation

The rules and pipelines here are examples, and the series is explicit that a rule you have not tested is a rule you do not have. Before trusting any rule:

1. Note the Wazuh version you are validating against — the rule schema differs between versions.
2. Write the rule into a non-production Wazuh instance.
3. Run `/var/ossec/bin/wazuh-analysisd -t` and confirm it loads without error.
4. Confirm it fires on the events you expect — and stays quiet on the ones you don't.
5. Do this with `wazuh-logtest`, not by inspection: feed it real or synthetic log lines that should match, and lines that deliberately should not. A rule that loads is a rule that parses — not a rule that matches correctly.

Examples that have been validated against a specific version say so, and name the version. Examples that have not are marked as unvalidated references. We do not assert rule behaviour from documentation alone.

**Written for Wazuh 4.14.x at the time of writing** — the XML constructs and CLI commands referenced here match that release branch's documentation. This note reflects a documentation/construct review, not a confirmed test run against a live 4.14.x instance; update it to "Tested against" only once someone has actually run the examples against that version and can name the result. Validate against your own deployed version before use in any case — the rule schema and available constructs differ between versions.

---

## Data and governance

Several pipelines here process real Wazuh alert data — hostnames, usernames, IPs, command lines. That data is sensitive under GDPR, sectoral rules, and customer contracts. **Do not point these pipelines at a public LLM API with production data before reading [Article 2](./articles/02-responsible-ai-operations.md) and recording the backend decision in an ADR.** The [`adr/`](./adr/) directory holds the template and a worked example. This is not optional fine print; it is the first architectural constraint.

---

## Contributing / questions

The series is authored by two Wazuh practitioners — governance/managed-security (Theumert) and detection engineering/operations (Sigl). Issues and discussion welcome. Internal review happens per the [style guide](./style-guide.md); article content is English.

---

*If this repository is useful, the most useful thing you can do back is tell us where a rule failed to load in your environment, and on which Wazuh version. That is exactly the kind of ground truth the series is built on.*
