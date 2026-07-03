# Detection Engineering at Scale

*Article 3 of 5 — AI-Augmented Wazuh Operations*

---

## A Technique You Read About on Monday

A new technique gets published on Monday. A credible write-up, a proof of concept, maybe a fresh MITRE ATT&CK sub-technique ID. By Tuesday your inbox has three people asking whether you're covered.

You are not, yet. Writing the detection means reading the technique closely, figuring out which of your log sources would even see it, mapping the behaviour to specific fields, drafting a Wazuh rule, testing it against real events, getting it reviewed, and deploying it. Each step is a normal day's work. Done properly, the whole chain takes longer than the gap between disclosure and the first opportunistic scan.

That gap — between a technique existing in the world and a rule existing in your ruleset — is where detection engineering actually lives. And it is a throughput problem long before it is a talent problem.

AI can compress the drafting end of that chain. It cannot compress the part that requires knowing what your logs actually contain. This article is about telling those two apart.

---

## The coverage problem

Detection coverage always lags the threat landscape, and the reason is arithmetic, not skill. Every technique worth detecting needs a rule. Every rule needs someone who understands the log source, the field layout, and the false-positive surface well enough to write something that fires on the right events and stays quiet on the rest. That person is the same person handling today's alerts.

So coverage is rationed by attention. New techniques queue behind operational load. The rule that would have caught something sits half-drafted in a branch while the analyst who started it gets pulled into an incident. Meanwhile the window during which the technique goes undetected stays open.

The bottleneck is not that engineers can't write rules. It is that writing a *correct, tested* rule is slow, and the slowness compounds across every technique nobody has gotten to yet. Speed at the drafting stage is worth real money here — provided it does not come at the cost of correctness.

Validation before automation. In detection engineering that phrase has a specific, unforgiving meaning: a rule you have not tested is a rule you do not have.

---

## MITRE ATT&CK to Wazuh: the translation problem

ATT&CK is a catalogue of adversary behaviour. It tells you that a technique exists, describes how it works in prose, and gives procedure examples. What it does not give you is a Wazuh rule, because it cannot — it does not know which log sources you run, which decoders are active, or what your events look like on the wire.

That is the translation gap. "This technique achieves persistence via a scheduled task" is a sentence. A Wazuh rule needs to know: which log records a scheduled-task creation in your environment, which decoded field holds the task name, what value distinguishes malicious from routine, and which parent rule the new rule should build on. None of that is in the ATT&CK entry. All of it lives in your logs.

AI can help bridge the gap — but only from the side it can see. A model can read the technique description and propose *what to look for*. It cannot tell you *whether your logs contain it*. Hand it the technique alone and it will confidently invent field names that sound right and do not exist in your data. The model's fluency is highest exactly where its grounding is weakest, which is the most dangerous combination detection engineering offers.

---

## Prompt engineering for rule generation

What works is giving the model the half of the problem it cannot see: your logs.

A rule-generation prompt that produces usable drafts includes a real decoded log sample, an explicit list of the fields available and what they mean, the parent rule to inherit from, and a hard constraint to only match on fields that appear in the sample. The technique description is the easy input. The log context is the input that keeps the output honest.

```python
prompt = f"""You are writing a Wazuh detection rule. Target the Wazuh version
you validate against (state it explicitly; the schema differs between versions).

TECHNIQUE
{attack_technique_description}

DECODED LOG SAMPLE (a real event from this environment)
{decoded_sample_json}

AVAILABLE FIELDS (only these exist — do not invent others)
{field_list_with_descriptions}

PARENT RULE
Build on rule id {parent_sid}. Use <if_sid>{parent_sid}</if_sid>.

CONSTRAINTS
- Match ONLY on fields present in the sample above.
- Use <field name="..."> for decoded fields; do not guess field names.
- Do not use elements you are not certain exist in the target Wazuh schema.
- Output only the <rule> block, no commentary.
"""
```

What does not work is asking for a rule from the technique description alone. Without a log sample the model has nothing to ground the field names against, and it fills the vacuum with plausible fiction. The difference between the two prompts is the difference between a draft an engineer can refine and a draft an engineer has to debug from scratch — and debugging invented fields is slower than writing the rule by hand.

---

## The XML constraints AI gets wrong

Even with good grounding, generated rules fail against the Wazuh parser in recognisable ways. The Wazuh rule schema is underrepresented in training data, so models reason about it by analogy to XML they have seen more of — and the analogies break.

The recurring failure modes are consistent enough to anticipate: elements that sound like they should exist but do not (a model may produce a construct like `<options>no_alert</options>`, which the parser rejects); attribute combinations the parser refuses; `<if_sid>` and `<if_matched_sid>` used interchangeably when they mean different things; and rules emitted without a valid `id` or with one that collides with an existing rule. Which specific constructs fail depends on the Wazuh version you validate against — confirm them against yours rather than trusting this list. Each looks correct. Each fails to load.

There is no prompt clever enough to eliminate this reliably, because the model does not have a ground-truth schema — it has a probability distribution over text that resembles rules. The mitigation is not a better prompt. It is the verification loop from Article 1, applied without exception.

---

## Validation: the same bar

An AI-generated detection rule faces exactly the same test as the suppression rules in Article 1: it gets written into a real Wazuh instance and checked with `wazuh-analysisd -t`. The daemon parses every rule file and exits non-zero with an error if anything fails to load. If the candidate rule fails, the error goes back to the model for a fix, and the loop runs a bounded number of times before giving up and logging the failure.

The intent of the rule does not change the bar. A suppression rule that fails to load suppresses nothing. A detection rule that fails to load detects nothing — and unlike a suppression rule, its silence looks exactly like safety. That is the worse failure: a rule that loads incorrectly, or does not load at all, produces the same empty alert queue as a quiet network. You cannot tell "nothing happened" from "nothing was watching" by looking at the dashboard.

So detection rules earn no exemption. If anything they warrant more suspicion, because their failure is invisible where a suppression rule's failure is merely loud.

A note on data flow, since this pipeline reads real logs: the log sample handed to the model is production data, with the same sensitivity as any alert in Article 1 — hostnames, accounts, paths. Everything Article 2 said about where that data is allowed to go applies here unchanged. The generation pipeline is backend-agnostic by the same design; the inference endpoint can and, for real log samples, should be one you control. Detection engineering does not get a governance discount.

---

## Rules that age

A rule is not finished when it loads. Techniques evolve — attackers change a flag, move to a different LOLBin, split one step into two — and a rule tuned to last year's procedure example quietly stops matching. The rule still loads. It still shows green. It just no longer catches the thing it was written for.

This is a maintenance problem, and it is where AI's limits are sharpest. A model can draft a rule from a 2024 procedure example. It cannot tell you whether that example still reflects how the technique is used in 2026, because it does not watch your environment and does not know what changed. Rule decay is measured against reality, and the model has no access to reality — only to text about it.

Someone has to own each rule past its creation: revisit it when the technique it targets shifts, confirm it still fires on current variants, retire it when the log source it depends on goes away. That ownership is a technical discipline — testing, coverage tracking, regression against known-good events. (Who is *accountable* when a decayed rule misses an intrusion is a different question, an organisational one, and Article 5 takes it up. Here the point is narrower: the rule itself needs a technical owner who keeps it alive.)

AI drafts. It does not maintain. Nothing about generating a rule faster changes the fact that a rule is a living thing with an owner.

---

## What AI cannot do here

The hard boundary is grounding. A rule without log knowledge is a rule without grounding, and no amount of model capability substitutes for it.

The model cannot tell you whether a given field exists in your environment, only whether it exists in the sample you showed it. It cannot tell you whether your log format matches the assumption baked into a public procedure example. It cannot tell you whether the rule fires on the events that matter, or merely on the events that happened to be in the sample. Every one of those questions is answered by someone who has read the logs — watched them at volume, seen the routine noise, learned which fields are reliably populated and which are empty half the time.

That is the engineer's contribution, and it is not a formality. It is the part of detection engineering that determines whether a rule works, and it is exactly the part AI cannot see.

---

## Conclusion

AI compresses the drafting cycle in detection engineering, and the compression is real — a grounded prompt plus a hard validation loop turns hours of schema-wrangling into minutes of review. That is worth having when coverage is rationed by attention and every undrafted rule is an open window.

But it compresses only the half of the work the model can see. The other half — knowing which logs exist, what they contain, whether the rule catches the real thing — stays with the engineer who has read them. From a detection-engineering standpoint, that is the whole job: the model proposes what to look for, and only someone who operates the environment can confirm it can see it.

Validation before automation. A rule you have not tested is a rule you do not have — and a rule tested against logs you do not understand is a rule you only think you have.

---

*Next in this series: [Alert Enrichment and Triage Automation](./04-alert-enrichment-triage.md)*
