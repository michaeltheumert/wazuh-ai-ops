# Taming Alert Fatigue: How AI Can Reduce the False Positive Burden in SIEM Operations

*Article 1 of 5 — AI-Augmented Wazuh Operations*

---

## The Real Cost of Noise

At some point, most SOC analysts stop being surprised by false positives. They learn which rule IDs fire on routine admin activity, which alerts appear every morning because of a scheduled backup job, which patterns belong to a known-good tool that nobody has bothered to suppress yet. The alerts still arrive. They just get closed faster.

That adaptation is the actual problem.

When analysts expect noise, they develop a filtering habit — and filtering habits have blind spots. A real threat that shares the surface characteristics of a familiar false positive gets processed with the same low-attention triage. The alert existed. The response never happened.

False positives are not just a productivity problem. They are a detection quality problem dressed up as an operational one.

The standard fix is manual rule tuning. An analyst spots a recurring false positive, writes a suppression rule, tests it, gets it reviewed, deploys it. Each step is manageable. But the combined overhead across dozens of rule IDs, rotating on-call schedules, and deployment pipelines means plenty of false positives go unaddressed for weeks. The noise sticks around. The filtering habit deepens.

AI tooling can compress that cycle significantly — if it is applied where it actually helps and kept out of decisions that require judgment.

---

## Where AI Fits in the Tuning Workflow

Tuning a false positive involves four steps, each with different requirements:

1. **Deciding** whether an alert is actually a false positive
2. **Authoring** a suppression rule that is as narrow as possible
3. **Verifying** that the rule is syntactically and semantically correct
4. **Documenting** the change for review and audit purposes

Steps one, two, and four involve reading context, applying domain knowledge, and producing structured text. Modern LLMs handle these well. Step three is binary: the rule either loads or it does not. A good pipeline uses AI where it helps and relies on hard verification where correctness is non-negotiable.

Validation before automation. That principle shapes every design decision in the pipeline described here.

The pipeline targets Wazuh, but the approach applies to any rule-based detection platform.

---

## A Tiered Model Strategy

Not every task in the pipeline needs the same model. Routing all calls through the most capable available model would be slower and more expensive than necessary, so the pipeline assigns models by task:

**Classification and documentation** use Claude Sonnet. These tasks involve structured reasoning over a well-defined input, run at high frequency, and do not require deep specialization. Speed and cost efficiency matter here.

**Rule authoring and refinement** use Claude Opus. Writing a correct, narrowly scoped Wazuh rule requires understanding the rule inheritance model, knowing which XML elements are valid, and making judgment calls about which alert fields to match on. This is where quality most directly determines whether the output is usable.

The split mirrors how a human team might divide the work: one person triages and documents, a more experienced engineer writes the actual rule.

---

## Classification: Deciding What Is Noise

The first AI step is false positive classification. For each new alert, the pipeline sends the alert JSON to Claude Sonnet and asks for a boolean verdict, a confidence score between 0.0 and 1.0, and a short explanation of the reasoning.

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

The reasoning string travels through the rest of the pipeline and ends up in the pull request description, so the reviewer can see why the model flagged the alert. That traceability is not optional. It is what makes the pipeline auditable.

One important constraint: this classification step is not a general-purpose SOC triage mechanism. It is a narrow filter for rule creation decisions. Using it as a primary alert disposition tool for an incident response workflow would be a misapplication — and a dangerous one.

---

## Rule Authoring and the Refinement Loop

Once an alert clears the confidence threshold, Claude Opus drafts the suppression rule. The prompt pushes toward the narrowest possible match — targeting specific users, program names, source IPs, or command patterns — rather than silencing the parent rule entirely.

A broad suppression rule is its own security risk. It can hide future real alerts that share the same parent rule ID. Narrow rules are harder to write. They are also the only kind worth writing.

The harder problem is what happens when the rule is wrong. Wazuh's rule XML format has constraints that are not always obvious from documentation. Certain elements do not exist, attribute combinations are restricted, and the inheritance model requires careful use of `<if_sid>` and `<if_matched_sid>`. LLMs will sometimes produce rule constructs that look correct but are rejected by the Wazuh parser.

The fix is a verification loop grounded in the actual system.

---

## Verification Against a Real Wazuh Environment

Rather than trying to replicate Wazuh's rule validation logic in Python, the pipeline hands the job to Wazuh itself. The candidate rule file is written into the Docker container running Wazuh, and `wazuh-analysisd -t` is run in test mode. The daemon parses every rule file, including the new one, and exits with a non-zero code and an error message if anything fails to load.

```python
cmd = [
    "docker", "exec", WAZUH_CONTAINER,
    "bash", "-c",
    (
        f"echo '{rule_b64}' | base64 -d > /var/ossec/etc/rules/_test_rule.xml && "
        f"/var/ossec/bin/wazuh-analysisd -t 2>&1; "
        f"rc=$?; rm -f /var/ossec/etc/rules/_test_rule.xml; exit $rc"
    ),
]
```

The temporary file is removed after the test regardless of outcome. If validation fails, the daemon's error output is passed back to Claude Opus with a request to fix the rule. The loop runs up to five times. If the rule still fails after that, the pipeline logs an error and no pull request is created.

This is where the approach delivers its most practical value. A human going through the same edit-test-fix cycle would spend several minutes per iteration. The automated loop finishes in seconds — and the refinement prompts can include knowledge of failure patterns encountered before, such as the non-existent `<options>no_alert</options>` element that the model occasionally produces without explicit instruction to avoid it.

AI-generated rules face the same validation bar as hand-written ones. That is not a detail. It is the condition under which the pipeline is trustworthy at all.

---

## From Validation to Review

A rule that passes validation is not deployed automatically. The pipeline opens a GitHub pull request, with Claude Sonnet writing a Markdown description covering the original alert, the false positive reasoning, the rule change, and relevant caveats. The reviewer gets a complete, readable summary without having to reconstruct context from logs or tickets.

A duplicate check at the start of the pipeline prevents multiple PRs from being opened for the same Wazuh rule ID. If an open PR already exists for that rule, the alert is skipped. This keeps the review queue manageable during periods of sustained false positive activity.

What arrives in the reviewer's queue is a validated rule and a readable explanation — asking for a review decision, not original authorship. That shift in what analysts are asked to do is the actual output of the pipeline.

---

## What This Changes for Analysts

Classification, rule drafting, and initial verification previously required an analyst to notice the pattern, open a rule editor, look up the Wazuh XML schema, test the rule manually, and write up the change. The pipeline handles all of that. The analyst reviews the result.

That is not a small change. It is the difference between a false positive that gets addressed in minutes and one that waits three weeks for someone to have the time.

But analyst involvement still matters — and not just formally. The confidence threshold keeps ambiguous cases out of the queue. The live validation loop ensures syntactic correctness before review. What the pipeline cannot do is assess whether suppressing a particular alert might hide a threat pattern that emerges later under different conditions. That judgment belongs with a human.

AI in this workflow is not making better decisions than analysts. It is handling the routine, well-defined work quickly enough that analysts can focus on the decisions that actually require their experience.

Judgment before delegation. The pipeline is built around that order, not the reverse.

---

## Conclusion

False positive management is a good fit for AI assistance because the workflow is repetitive, the inputs are structured, and the output can be verified against a hard standard. Using lighter models for high-frequency classification and documentation while reserving more capable models for rule authoring keeps the approach practical at scale.

The goal is not to remove humans from the loop. It is to reduce the distance between a false positive being observed and a reviewed suppression rule being ready to deploy — while keeping every step that requires judgment firmly in human hands.

---

## On Data Confidentiality and Model Selection

The pipeline described here sends real Wazuh alert data to external LLM APIs — hostnames, usernames, source IP addresses, process names, command-line arguments. In the examples above, those APIs are publicly hosted Anthropic models. This is a deliberate architectural choice made for demonstration purposes. It is not a recommendation for production use.

Wazuh alerts regularly contain information that is sensitive under GDPR, HIPAA, or customer contracts: internal network topology, account names, file paths, details about ongoing incidents. Sending that data to a public cloud API means it leaves the organisation's control — regardless of whether the provider offers a data processing agreement or commits to not using inputs for training.

Before running a pipeline like this in production, two questions require written answers, not assumptions:

**Self-hosted models are the safer option.** Running an open-weight model on internal infrastructure keeps alert data within the organisation's network. The pipeline's model dispatch layer is abstracted, so switching from a public API to a locally hosted inference endpoint is a configuration change, not a rewrite.

**Customer and contractual alignment is required if self-hosting is not feasible.** Using a public LLM API to process customer security telemetry must be covered by applicable data processing agreements and disclosed to the customer. Assuming that general-purpose API terms cover security telemetry is not sufficient. This needs to be confirmed in writing before going live.

The architectural pattern works regardless of the inference backend. Choosing that backend is a data governance decision. Article 2 of this series addresses that decision in full.
