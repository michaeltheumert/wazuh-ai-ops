# Detection Engineering at Scale

*Article 3 of 5 — AI-Augmented Wazuh Operations*

---

## Two Kinds of Blind Spot

A new application goes live and its logs start arriving a week later. They reach the Wazuh manager, they are written to disk, and little else happens. No useful decoder claims the payload, no dependable fields are extracted, and every downstream detection idea is forced to work against raw text.

Elsewhere in the same environment, a vendor publishes a new attack technique or a sector advisory. By the next morning somebody asks whether you are covered. The answer is not a property of the advisory. It depends on whether your telemetry can see the behaviour, whether the relevant fields are decoded, whether a rule exists, and whether that rule has been tested against events that should and should not trigger it.

These look like different problems, but they are stages of the same coverage problem. Detection engineering is constrained by the attention of people who understand both the threat and the logs, and those are often the same people already handling today's alerts.

AI can compress parts of that work. What it can safely do changes with the amount of grounding available. The useful way to think about AI-assisted detection engineering is therefore not "generate me a rule", but a four-stage loop:

1. make the source legible;
2. decide what is worth detecting;
3. tune what fires against real operational data;
4. turn external threat intelligence into maintainable coverage.

At every stage the model proposes. Wazuh and a reviewer validate.

---

## Stage 1: Make the Log Source Legible

Before threat modelling, an unparsed source needs a decoder and a small set of baseline rules. The goal is not yet to decide what is malicious. The goal is to make the source addressable so later rules can match on stable fields rather than brittle raw strings.

`wazuh-logtest` is the grounding mechanism for this step. It pushes a sample through Wazuh's pre-decoding, decoding, and rule-matching pipeline and shows what Wazuh itself sees.

```bash
echo '2026-08-04T09:12:44Z appsrv01 acme-portal: auth login_failed user=jdoe src=203.0.113.44 reason=bad_password' \
  | /var/ossec/bin/wazuh-logtest -v
```

An unhandled source may stop at something like:

```text
**Phase 1: Completed pre-decoding.
        timestamp: '2026-08-04T09:12:44Z'
        hostname: 'appsrv01'
        program_name: 'acme-portal'

**Phase 2: Completed decoding.
        No decoder matched.
```

That output is more useful to a model than a product name and a vague request for a decoder. Give the model representative raw samples and the actual logtest output, ask it to propose a decoder, then run every sample back through logtest. If Phase 2 does not expose the fields the model claimed it would extract, the draft is wrong.

A practical sample set should include normal traffic, failures, administrative actions, edge cases, and malformed or partial records. Twenty to fifty lines can be enough to start, but the number matters less than message-type coverage. A random slice of a quiet Tuesday is not a specification for everything the application can emit.

Prefer Wazuh's conventional static field names where the semantics fit: `srcip`, `dstip`, `srcuser`, `dstuser`, `url`, `action`, and `status`. Wazuh's decoder schema explicitly supports these fields, and using them keeps the new source compatible with rules and correlations that already expect those names. Dynamic fields remain appropriate for application-specific data that does not map cleanly onto the static vocabulary.

A decoder draft might look like this conceptually:

```xml
<decoder name="acme-portal">
  <program_name>^acme-portal$</program_name>
</decoder>

<decoder name="acme-portal-auth">
  <parent>acme-portal</parent>
  <regex>^auth (\S+) user=(\S+) src=(\S+) reason=(\S+)$</regex>
  <order>action,srcuser,srcip,status</order>
</decoder>
```

Do not treat that XML as correct merely because it looks plausible. Decoder behaviour depends on the exact input after pre-decoding and on the regex semantics Wazuh applies. Save the candidate in the test environment and verify it with `wazuh-logtest` against the real samples.

Baseline rules should be deliberately boring: enough structure to identify event classes and support later child rules, without pretending that every log message deserves an alert. Custom rule IDs should also follow the range recommended by the Wazuh version you run; current Wazuh documentation recommends `100000` to `120000` for custom rules.

The blind spot at this stage is completeness. You rarely know every message type on day one. Keep a process for sampling decoded-but-unclassified events and revisit the source after upgrades, incidents, and new feature rollouts. Coverage begins as an inventory and improves over time.

---

## Stage 2: Threat Modelling Produces the Detection Backlog

Stage 1 tells you what the source can say. It does not tell you what deserves an alert.

If you skip threat modelling, your ruleset tends to mirror the log format: one rule for login failures, one for configuration changes, one for role updates, all with severity levels somebody guessed. That creates activity coverage, not threat coverage.

Threat-model the asset instead. What does it do? Who can reach it? What would an attacker gain? Which attack paths matter in this environment? For each path, make an explicit decision: prevent, detect, or accept. Only the ones marked detect become detection requirements.

| Attack path | Technique | Decision | Evidence available? |
|---|---|---|---|
| Password spraying against the portal | T1110.003 | Detect | Yes: `srcip`, `srcuser`, `action` |
| Session token replayed from elsewhere | T1550.004 | Detect | No: no session identifier or user-agent telemetry |
| Admin role granted outside change window | T1098 | Detect | Yes: `action=role_granted`, `dstuser` |

The final column is the one that prevents imaginary detections. If the required evidence is absent, the output is a logging requirement, not an AI-generated rule.

This is where model-assisted drafting starts paying off, because Stage 1 produced the grounding the model was missing: real decoded events and a verified field list.

```python
prompt = f"""You are writing a Wazuh detection rule for Wazuh {wazuh_version}.

TECHNIQUE
{technique_id}: {technique_description}

DETECTION INTENT
{detection_intent}

DECODED SAMPLE
{logtest_phase2}

AVAILABLE FIELDS
{field_list}

PARENT RULE
Use rule {parent_sid} via <if_sid>{parent_sid}</if_sid>.

CONSTRAINTS
- Match only on fields listed above.
- Do not invent field names.
- Use rule id="{assigned_sid}" exactly.
- Prefer the narrowest condition that expresses the detection intent.
- Output only the <rule> block.
"""
```

The model should not be allowed to allocate its own rule ID in a shared repository. Assign it deterministically in the pipeline, check for collisions, instruct the model to use it, and enforce the value again before validation. Deterministic correction is cheaper and safer than trusting a probabilistic system with namespace management.

### The XML Failure Modes That Still Matter

Grounding reduces hallucinations; it does not give the model a Wazuh schema.

Common failures include invented option values, incorrect inheritance, incompatible combinations of correlation elements, and IDs that collide with deployed rules. One especially useful distinction is between `<if_sid>` and `<if_matched_sid>`: the first builds on a rule matched in the same event-processing chain; the second is designed for temporal correlation and is used with `frequency` and `timeframe`.

Another recurring mistake is plausible-but-invalid XML such as `<options>no_alert</options>`. Current Wazuh rules support the `noalert` attribute on `<rule>` and a defined set of `<options>` values such as `no_log`; `no_alert` is not one of them.

No prompt eliminates these mistakes reliably. The answer is system validation.

---

## Two Checks, Not One

A generated detection needs two different tests because "loads" and "works" are different claims.

First, run:

```bash
/var/ossec/bin/wazuh-analysisd -t
```

The `-t` mode tests the Wazuh configuration. In the workflow from Article 1, the candidate rule is placed temporarily under `/var/ossec/etc/rules/`, the command is executed, the file is removed regardless of outcome, and any error output is fed back into a bounded refinement loop.

Second, use `wazuh-logtest` with fixtures that express expected behaviour:

- at least one event that **must trigger** the candidate;
- one or more near-misses that **must not trigger** it;
- for frequency/correlation rules, enough events in one logtest session to exercise the counter and timeframe semantics.

`wazuh-logtest` is specifically intended for testing decoders and rules against supplied samples and reports which decoder fields and alerts match. That makes it the behavioural test that `wazuh-analysisd -t` is not.

This distinction matters more for detections than suppressions. A broken suppression is usually noisy. A broken detection can be perfectly silent. An empty alert queue looks the same whether nothing happened or nothing was watching.

The same standard applies to hand-written rules. AI does not create a new validation category; it simply makes it easier to generate more candidates, which makes hard validation more important rather than less.

---

## Stage 3: Tune Against Real Alerts Without Blinding the Ruleset

Rules from Stage 2 eventually meet production. Some produce useful signal. Others expose the assumptions the threat model and test fixtures did not capture.

This is where the false-positive workflow from Article 1 attaches. A model can classify recurring noise, draft a narrow suppression rule, and open a pull request. The important constraint is narrowness: suppress the known-good behaviour, not the parent rule that also catches malicious variants.

A safe tuning rule normally constrains several independent attributes when the telemetry supports them: process image, command line, parent image, parent command line, user, host role, or another stable property of the legitimate behaviour. The reviewer should be able to answer one question from the diff: *what maliciously interesting variation would still alert?*

Model confidence is not proof here. Article 1 uses an 80% threshold as a routing heuristic and explicitly notes that such a number must be calibrated against labelled historical alerts. The relevant metric is not generic accuracy. It is the rate at which true threats would be incorrectly suppressed.

The pipeline should also refuse duplicate work. If an open tuning PR already exists for a rule family or target rule ID, skip the new proposal or append evidence to the existing review context instead of flooding the queue.

### Deployment Is a Separate Gate

Passing validation is not deployment. Merge approval is the human gate, and applying the merged files is an operational action with its own failure modes.

For current Wazuh releases, saved rule and decoder changes can be tested with `wazuh-logtest`, but the Wazuh documentation instructs operators to restart the manager for the changes to generate production alerts. `wazuh-control reload` exists, but the Wazuh documentation recommends `systemctl` or the platform service command for service lifecycle operations to avoid status inconsistencies.

That means a deployment pipeline should make the restart strategy explicit rather than hiding it behind an ambiguous "reload" step. In a clustered or highly available environment, the exact rollout procedure deserves the same care as any other security-control deployment.

---

## Working With Real Alert Data

Stages 1 and 2 can often use curated or synthetic samples. Stage 3 operates on production alerts and therefore sees the data Article 2 treats as sensitive: hostnames, accounts, source addresses, file paths, command lines, internal topology, and potentially incident details.

The model boundary is consequently part of the detection architecture.

Do not assume a general API agreement covers security telemetry. Confirm the applicable processing terms, customer commitments, retention behaviour, and regional requirements. Where possible, minimise the payload before inference and keep the dispatch layer backend-agnostic so moving from a hosted model to an internally operated endpoint does not require redesigning the pipeline.

The same principle used throughout this series applies: judgment before delegation. A model should receive only the data needed for the task and only after the organisation has decided where that data is allowed to go.

---

## Stage 4: Turn CTI Into Maintainable Coverage

Once the earlier stages are working, external reporting becomes an input instead of a fire drill. A vendor report, sector advisory, or exploitation write-up arrives as prose. The detection-engineering job is to turn it into one of three outputs:

- a detection candidate;
- a logging gap;
- a documented decision not to detect.

Models are useful at extracting candidate observables and behaviours from long reports, but those outputs have different shelf lives.

**Observables** such as hashes, domains, and IP addresses decay quickly. Where Wazuh CDB lists fit the use case, keep the volatile values in the list and reference it from a stable rule:

```xml
<rule id="100310" level="10">
  <if_sid>100200</if_sid>
  <list field="srcip" lookup="address_match_key">etc/lists/cti-known-c2</list>
  <description>acme-portal: source address appears on the CTI watchlist</description>
</rule>
```

For IP fields, `address_match_key` is the documented lookup mode. The list must be declared in the Wazuh ruleset configuration. A critical operational detail is that CDB lists are built and loaded when the analysis engine starts; current Wazuh documentation therefore requires a manager restart after adding or modifying a CDB list. Treat feed refresh as a controlled deployment event, not merely a text-file edit.

**Behaviours** generally age more slowly and justify dedicated rules. Feed them back through Stage 2 with the verified field inventory attached, then through both validation checks. If a report describes evidence you do not collect, the correct result is still a telemetry requirement rather than a fabricated approximation.

CTI can also change the threat model itself. A technique previously accepted as low priority may become relevant when a campaign begins targeting your sector. That moves the entry from accept to detect and starts the cycle again.

---

## What None of This Fixes

Rules decay.

Attackers change flags, switch binaries, alter parent-child relationships, or split one procedure into several steps. A rule written against last year's procedure example can continue to load successfully while no longer matching the behaviour it was created for.

That is why every detection needs a technical owner and a review trigger. Revisit rules when the associated technique changes, when the log source changes schema, after major application upgrades, and when incidents expose missed variants. Keep positive and negative fixtures beside the rule where practical so regression tests survive longer than the memory of the engineer who wrote it.

AI does not maintain a rule merely because it generated the first draft. It has no independent view of your environment, no knowledge of which fields are intermittently empty, and no way to infer that a silent rule has become obsolete unless you provide evidence.

The hard boundary is grounding. The model knows only what you show it. `wazuh-logtest`, `wazuh-analysisd -t`, operational telemetry, and human review are what connect generated text back to reality.

---

## Conclusion

Coverage builds in order. Decode the source before writing rules for it. Model the threat before deciding what deserves an alert. Validate both configuration and behaviour before review. Tune against real alerts without suppressing the signal you still need. Consume CTI only through a pipeline that can distinguish volatile observables from durable behaviours and can deploy changes safely.

AI can compress work at every stage: decoder drafting, field mapping, rule authoring, false-positive analysis, documentation, and CTI extraction. What it does not compress is the need to know what your logs contain and to prove that the resulting control behaves as intended.

Validation before automation. A rule you have not tested is a rule you do not have — and a rule tested against logs you do not understand is a rule you only think you have.

---

*Technical note: the Wazuh-specific syntax and operational statements in this revision were checked against the current Wazuh 4.14 documentation in August 2026. Production environments should validate against the exact version they run.*

*Next in this series: [Alert Enrichment and Triage Automation](./04-alert-enrichment-triage.md)*
