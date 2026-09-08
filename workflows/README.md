# Reference workflows

Pipeline sketches referenced by the articles. These are reference implementations to adapt, not drop-in production configs — the governance and validation caveats in the articles apply.

## Available

- **[`validate-wazuh-rule.py`](./validate-wazuh-rule.py)** *(Article 1)* — temporary candidate-rule validation against a non-production Wazuh Docker container. It first runs `wazuh-analysisd -t`, then feeds positive and negative fixture events through `wazuh-logtest`. The command returns success only when every positive fixture matches the expected rule ID and every negative fixture avoids it. This closes the parser-versus-match-behaviour gap described in Article 1; it still does not turn an unexecuted example into a validated one. Record the Wazuh version and actual run result before claiming validation.
- **[`enrichment-triage.n8n.json`](./enrichment-triage.n8n.json)** *(Article 4)* — Wazuh webhook → n8n → parallel enrichment (IP reputation, asset context, user profile, historical frequency) → LLM triage brief → analyst dashboard. n8n orchestrates, the model summarises, the analyst decides. All enrichment and inference endpoints in the export are placeholders (`*.internal.example`); point them at infrastructure you control before running it, per [ADR-001](../adr/ADR-001-inference-backend.md). Authenticated calls use n8n's own credential system (Header Auth placeholders) — no token lives in this JSON. The pipeline never sets a disposition — that field stays `null` until a human sets it.
- **[`enrichment-triage.test.n8n.json`](./enrichment-triage.test.n8n.json)** — a test harness for the workflow above. It replaces the four live enrichment calls with the mock data from [`fixtures/enrichment-triage.fixture.json`](./fixtures/enrichment-triage.fixture.json), mirrored by hand into the harness rather than read from the file at runtime (the two must be kept in sync manually — the harness file says so at the top). It runs the assembly → LLM-brief → dashboard-payload logic against that mock data, then checks the structural guarantees (disposition/disposed_by stay `null`, status is correct, unresolved facts like travel status surface rather than get guessed) — those checks run regardless of the LLM step. Run "Run Positive Case" and "Run Negative Case" separately. The negative case feeds in a telemetry field crafted to look like an instruction — see "Telemetry is evidence, never instruction" in Article 4 — and asserts the pipeline's *output fields* are unaffected by it; whether the model's *brief text* handled it well still needs a human read, which the harness surfaces rather than auto-grades. The LLM call itself still needs a real self-hosted inference endpoint to execute end to end; without one, n8n's "Pin Data" feature can stub that response to test the assertions in isolation.

## Article 1 rule-validation usage

Provide one candidate XML rule, the rule ID you expect it to produce, and two fixture files with one log event per non-empty line:

```bash
python3 workflows/validate-wazuh-rule.py \
  --container wazuh-manager \
  --rule-file ./candidate-rule.xml \
  --expected-rule-id 100500 \
  --positive ./positive.log \
  --negative ./negative.log
```

Comments beginning with `#` and blank lines in fixture files are ignored. A positive event must reach the expected rule ID in `wazuh-logtest`; a negative event may match other legitimate Wazuh rules, but it must not match the candidate rule ID. The candidate XML is copied into the container under a temporary filename and removed after the run.

The script deliberately does not ship a pretend "known-good" fixture set. Match behaviour depends on the candidate rule, its parent rules, enabled decoders and the Wazuh version under test. The caller must provide fixtures that represent the actual behaviour being reviewed.

## Before you run any of these

Run the rule validator only against a non-production Wazuh manager. The triage pipeline sends alert data plus enrichment to a model. Enrichment often makes the payload *more* sensitive, not less — it pulls in threat-intel and directory data. Point it at a self-hosted endpoint unless the backend decision in [ADR-001](../adr/ADR-001-inference-backend.md) says otherwise, and read [Article 2](../articles/02-responsible-ai-operations.md) first.
