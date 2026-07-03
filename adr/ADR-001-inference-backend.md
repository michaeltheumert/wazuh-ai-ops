# ADR-001: Inference backend for the alert-tuning pipeline

## Status
Accepted — 2026-08-15
Review due: 2027-02-15

## Context
The false-positive tuning pipeline (see Article 1) processes live Wazuh alerts. Those alerts contain personal data under GDPR — usernames, source IP addresses tied to identifiable people — and internal topology: hostnames, file paths, process command lines. Under the applicable customer agreements, this telemetry must not leave defined processing boundaries without a confirmed legal basis.

The pipeline needs an LLM for two tiers of work: high-frequency classification and documentation, and lower-frequency rule authoring. The question is where that inference runs.

A public LLM API is operationally simplest and offers the strongest models. But sending this data class to a public endpoint constitutes a transfer that the existing agreements do not clearly cover, and confirming coverage in writing for security telemetry specifically was not achievable within scope.

## Decision
Inference runs on a self-hosted open-weight model on internal infrastructure. No alert data is sent to public LLM APIs. Both tiers use the local endpoint through the pipeline's abstracted model-dispatch layer. The classification tier uses a lightweight model; the authoring tier uses a higher-capability one, both self-hosted.

## Consequences
+ No cross-border or out-of-boundary transfer of security telemetry. GDPR and contractual exposure materially reduced.
+ The answer to "where did our alert data go?" is a location, a legal entity, and an access list — not a shrug.
+ Backend is swappable if capability needs change: config and base URL, not a rewrite.
- Rule-authoring quality is validated against our own rule corpus rather than assumed. Self-hosted authoring is measurably behind the strongest hosted models on complex rules.
- We own GPU capacity, endpoint availability, and the operational attention that comes with them.

## Review triggers
- A materially stronger self-hostable model becomes available for the authoring tier.
- Customer contract terms on data residency change.
- A regulatory change alters what constitutes a valid basis for processing this data class.
- Provider terms for any fallback hosted model change in a way that would make it viable.
