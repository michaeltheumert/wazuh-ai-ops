# Reference workflows

Pipeline sketches referenced by the articles. These are reference implementations to adapt, not drop-in production configs — the governance and validation caveats in the articles apply.

## Planned

- **`enrichment-triage.n8n.json`** *(Article 4)* — Wazuh webhook → n8n → parallel enrichment (IP reputation, asset context, user profile, historical frequency) → LLM triage brief → analyst dashboard. n8n orchestrates, the model summarises, the analyst decides. The exported workflow lands here alongside Article 4.

## Before you run any of these

The triage pipeline sends alert data plus enrichment to a model. Enrichment often makes the payload *more* sensitive, not less — it pulls in threat-intel and directory data. Point it at a self-hosted endpoint unless the backend decision in [ADR-001](../adr/ADR-001-inference-backend.md) says otherwise, and read [Article 2](../articles/02-responsible-ai-operations.md) first.
