# Taming Alert Fatigue: How AI Can Reduce the False Positive Burden in SIEM Operations

*Article 1 of 5 — AI-Augmented Wazuh Operations*

---

## The Real Cost of Noise

At some point, most SOC analysts stop being surprised by false positives. They know which rule IDs fire on routine admin activity, which alerts arrive every morning with a backup job, and which patterns belong to tools everyone already trusts. The alerts still arrive. They just get closed faster.

That adaptation is the problem.

Once noise becomes familiar, triage changes with it. Analysts spend less attention on patterns they have already learned to dismiss, and that shortcut works until a real threat happens to look similar. The alert may still be there; what changes is how seriously it gets read.

False-positive tuning is therefore not just housekeeping. It is part of maintaining detection quality.

The standard fix is manual rule tuning. An analyst spots a recurring false positive, writes a suppression rule, tests it, gets it reviewed, deploys it. Each step is manageable. Across dozens of rule IDs, rotating on-call schedules, and deployment pipelines, the combined overhead still means that plenty of false positives go unaddressed for weeks. The noise stays in the queue, and the shortcut becomes habitual.

AI tooling can compress that cycle significantly if it is applied where it actually helps and kept out of decisions that require judgment.

---

## Where AI Fits in the Tuning Workflow

Tuning a false positive involves four steps, each with different requirements:

1. **Deciding** whether an alert is actually a false positive
2. **Authoring** a suppression rule that is as narrow as possible
3. **Verifying** that the rule is syntactically and semantically correct
4. **Documenting** the change for review and audit purposes

Steps one, two, and four involve reading context, applying domain knowledge, and producing structured text. Those are useful places for LLM assistance. Step three is different: the rule either loads and behaves as intended, or it does not. A good pipeline uses AI where it helps and relies on hard verification where correctness is non-negotiable.

Validation before automation. That principle shapes every design decision in the pipeline described here.

The pipeline targets Wazuh, but the approach applies to any rule-based detection platform.

---

## A Tiered Model Strategy

Not every task in the pipeline needs the same model. Routing all calls through the most capable available model would be slower and more expensive than necessary, so the pipeline assigns models by task tier.

**Classification and documentation** run on a **fast, cost-efficient model**. These tasks involve structured reasoning over a well-defined input, run at high frequency, and do not require deep specialization. Speed and cost efficiency matter here.

**Rule authoring and refinement** run on a **stronger reasoning model**. Writing a correct, narrowly scoped Wazuh rule requires understanding the rule inheritance model, knowing which XML elements are valid, and making judgment calls about which alert fields to match on. This is where quality most directly determines whether the output is usable.

The reference implementation paired a lightweight reasoning model for the first tier with a higher-capability one for the second.[^models] The split is what matters, not the specific products — any capable provider can offer an equivalent pairing, and the choice will age faster than the pattern. The practical distinction is between high-volume classification/documentation work and the lower-volume task where rule quality carries the most risk.

---

## Classification: Deciding What Is Noise

The first AI step is false positive classification. For each new alert, the pipeline sends the alert JSON to the fast classification model and asks for a boolean verdict, a confidence score between 0.0 and 1.0, and a short explanation of the reasoning.

```python
prompt = f"""You are a Wazuh SIEM analyst. Examine the following Wazuh alert and determine
whether it is a false positive.

Return a JSON object with exactly these fields:
- "is_false_positive": boolean
- "confidence": float between 0.0 and 1.0 (1.0 = certain false positive)
- "reasoning": string (one concise paragraph explaining your conclusion)

Alert:
{alert_summary}

Respond ONLY with valid JSON, no markdown fences."""
```

The confidence score acts as a gate. Only alerts where the model is at least 80% confident — configurable — move forward. It is better to miss an occasional tuning opportunity than to suppress alerts that are borderline or context-dependent.

That threshold is a routing heuristic, not a calibrated probability of correctness. A model's self-reported confidence does not automatically correspond to its actual accuracy. Before relying on 80% — or any other number — as a gate, calibrate it against a labelled set of historical alerts: check precision and recall at that threshold, and specifically the false-suppression rate, since that is the failure mode this gate exists to prevent. Different rule families may warrant different thresholds once you have that data.

The reasoning string travels through the rest of the pipeline and ends up in the pull request description, so the reviewer can see why the model flagged the alert. That traceability makes the pipeline auditable rather than leaving the classification as an unexplained model output.

One important constraint: this classification step is not a general-purpose SOC triage mechanism. It is a narrow filter for rule creation decisions. Using it as a primary alert disposition tool for an incident response workflow would be a misapplication — and a dangerous one.

---

## Rule Authoring and the Refinement Loop

Once an alert clears the confidence threshold, the stronger reasoning model drafts the suppression rule. The prompt pushes toward the narrowest possible match — targeting specific users, program names, source IPs, or command patterns — rather than silencing the parent rule entirely.

A broad suppression rule is its own security risk. It can hide future real alerts that share the same parent rule ID. Narrow rules are harder to write, but they are the only kind worth writing.

The harder problem is what happens when the rule is wrong. Wazuh's rule XML format has constraints that are not always obvious from documentation. Certain elements do not exist, attribute combinations are restricted, and the inheritance model requires careful use of `<if_sid>` and `<if_matched_sid>`. LLMs will sometimes produce rule constructs that look correct but are rejected by the Wazuh parser.

The fix is a verification loop grounded in the actual system.

---

## Verification Against a Real Wazuh Environment

Rather than trying to replicate Wazuh's validation logic in Python, the pipeline hands the job to Wazuh itself. A candidate rule is written into a non-production Wazuh container, checked with `wazuh-analysisd -t`, and then exercised with `wazuh-logtest` against positive and negative fixture events.

The repository includes [`workflows/validate-wazuh-rule.py`](../workflows/validate-wazuh-rule.py), which enforces both checks in one command:

```bash
python3 workflows/validate-wazuh-rule.py \
  --container wazuh-manager \
  --rule-file ./candidate-rule.xml \
  --expected-rule-id 100500 \
  --positive ./positive.log \
  --negative ./negative.log
```

The helper copies the candidate XML into the container under a temporary filename and runs `/var/ossec/bin/wazuh-analysisd -t`. If the daemon rejects the rule, the command returns the parser output to the orchestration layer, which can feed that error back to the authoring model for a bounded refinement attempt.

A rule that loads then has to prove its behaviour. Each non-empty line in the positive fixture file is sent through `/var/ossec/bin/wazuh-logtest` and must reach the expected candidate rule ID. Each negative fixture is tested the same way and must avoid that rule ID. A negative event is allowed to match some other legitimate Wazuh rule; what matters is that the candidate suppression rule does not catch it.

The loop can still run up to five authoring attempts. If the rule cannot pass the parser check and the positive/negative match checks within that bound, the pipeline logs the failure and no pull request is created. The temporary candidate rule is removed from the container after every run.

Loading is not the same as matching. `wazuh-analysisd -t` proves the rule parses; `wazuh-logtest` is what tests whether the candidate fires on the events it should and stays silent on the ones it should not. The two checks answer different questions, and both are required before a generated rule is ready for review.

This is where the approach delivers practical value. A human going through the same edit-test-fix cycle would spend several minutes per iteration. The automated loop can run the mechanical checks in seconds, while keeping the actual suppression decision for review.

AI-generated rules therefore face the same validation bar as hand-written ones. That requirement is what makes the automation defensible.

---

## From Validation to Review

A rule that passes validation is not deployed automatically. The pipeline opens a GitHub pull request, with the documentation model writing a Markdown description covering the original alert, the false positive reasoning, the rule change, the fixture results, and relevant caveats. The reviewer gets a complete, readable summary without having to reconstruct context from logs or tickets.

A duplicate check at the start of the pipeline prevents multiple PRs from being opened for the same Wazuh rule ID. If an open PR already exists for that rule, the alert is skipped. This keeps the review queue manageable during periods of sustained false positive activity.

What arrives in the reviewer's queue is a validated rule and a readable explanation — asking for a review decision, not original authorship. The operational gain is the reduced amount of mechanical work required before that decision can be made.

---

## What This Changes for Analysts

Classification, rule drafting, and initial verification previously required an analyst to notice the pattern, open a rule editor, look up the Wazuh XML schema, test the rule manually, and write up the change. The pipeline handles that preparation. The analyst reviews the result.

Operationally, that can turn a recurring false positive from a tuning task that waits for spare time into a reviewed change that is ready while the context is still fresh.

But analyst involvement still matters — and not just formally. The confidence threshold keeps ambiguous cases out of the queue. The parser and fixture checks catch mechanical failures before review. What the pipeline cannot do is assess whether suppressing a particular alert might hide a threat pattern that emerges later under different conditions. That judgment belongs with a human.

AI in this workflow is not making better decisions than analysts. It is handling routine, well-defined work quickly enough that analysts can focus on the decisions that require their experience.

Judgment before delegation. The pipeline is built around that order, not the reverse.

---

## Before You Run This: Data Confidentiality and Model Selection

There is one decision that comes before any of the engineering above, and it does not belong in a footnote.

The pipeline described here sends Wazuh alert data to an inference endpoint — hostnames, usernames, source IP addresses, process names, command-line arguments. In the examples used while developing this article, publicly hosted models were tested only with synthetic or fully anonymised data. That is not a recommendation to send production telemetry to a public API.

Every alert used in the examples above is synthetic or fully anonymised — no customer or production telemetry was sent to a public API at any point while writing this series. That is deliberate: it is the same boundary ADR-001 draws for production use, applied to how this series itself was built.

Wazuh alerts regularly contain information that is sensitive under GDPR, HIPAA, or customer contracts: internal network topology, account names, file paths, details about ongoing incidents. Sending that data to a public cloud API means it leaves the organisation's control — regardless of whether the provider offers a data processing agreement or commits to not using inputs for training.

Before running a pipeline like this in production, two things require written answers, not assumptions:

**Self-hosting is usually the stronger option for staying in control of the data — not automatically the "safer" one in every sense.** Running an open-weight model on internal infrastructure keeps alert data within the organisation's network, but it also transfers operational responsibility — model supply chain, endpoint hardening, patching — onto you. Article 2 weighs that tradeoff in full; here, the point is narrower: the pipeline's model dispatch layer is abstracted, so switching from a public API to a locally hosted inference endpoint is a configuration change, not a rewrite.

**Customer and contractual alignment is required if self-hosting is not feasible.** Using a public LLM API to process customer security telemetry must be covered by applicable data processing agreements and disclosed to the customer. Assuming that general-purpose API terms cover security telemetry is not sufficient. This needs to be confirmed in writing before going live.

In managed-security work with regulated organisations, this is rarely the blocker people expect it to be. The self-hosted path is usually the one that survives a customer's procurement review, and building the pipeline backend-agnostic from the start means that choice stays open rather than becoming a rewrite later. The architectural pattern works regardless of the inference backend. Choosing that backend is a data governance decision — and Article 2 of this series addresses it in full.

---

## Conclusion

False positive management is a good fit for AI assistance because the workflow is repetitive, the inputs are structured, and the output can be verified against a hard standard. Using lighter models for high-frequency classification and documentation while reserving more capable models for rule authoring keeps the approach practical at scale.

From a managed-security and governance standpoint, the point of a pipeline like this is not that AI can assist Wazuh operations. It is where validation and human accountability are enforced while it does. The goal is to reduce the distance between a false positive being observed and a reviewed suppression rule being ready to deploy, while keeping every step that requires judgment firmly in human hands.

[^models]: The reference implementation used Anthropic's Claude Sonnet (classification and documentation) and Claude Opus (rule authoring) at the time of writing, tested exclusively against synthetic and anonymised alert data — see the data-handling note above and ADR-001. Model names date quickly; treat these as an example of the two-tier split, not a recommendation.
