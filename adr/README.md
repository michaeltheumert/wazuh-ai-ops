# Architecture Decision Records

This directory holds the governance trail for the pipelines in this repository. An ADR records a decision that has consequences — most importantly, *where the inference backend runs and why* — in a form an auditor or a customer can read.

The point is not bureaucracy. It is that when someone asks, a year later, why alert data flows the way it does, the answer is a document with a name and a date on it, not a shrug. See [Article 2](../articles/02-responsible-ai-operations.md) for the full argument.

## Files

- [`TEMPLATE.md`](./TEMPLATE.md) — copy this for a new decision
- [`ADR-001-inference-backend.md`](./ADR-001-inference-backend.md) — worked example: choosing the inference backend for the alert-tuning pipeline

## Conventions

- One decision per file, numbered sequentially: `ADR-NNN-short-slug.md`
- Status is one of: `Proposed`, `Accepted`, `Superseded by ADR-NNN`
- Every accepted ADR has a **review date**. Decisions about AI backends age fast; an unreviewed ADR is a decision that quietly stopped being current.
- ADRs are append-only. To change a decision, write a new ADR that supersedes the old one — do not edit history.
