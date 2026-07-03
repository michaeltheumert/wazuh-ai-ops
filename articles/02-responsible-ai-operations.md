# Responsible AI in Security Operations

*Article 2 of 5 — AI-Augmented Wazuh Operations*

---

## The Alert That Left the Building

An analyst gets a Wazuh alert she doesn't recognize. Unusual process, odd command line, a parent rule she rarely sees fire. She wants to understand it fast, so she copies the alert JSON into a public chatbot and asks what it means. The answer is good. It saves her twenty minutes.

It also just sent an internal hostname, a domain account name, a source IP, and a full command line to a third party — outside any contract, any data processing agreement, any record of what happened. Nobody decided that was acceptable. It simply happened, one paste at a time, because the tool was there and the pressure was real.

This is the uncomfortable part of AI in security operations. The technical integration is the easy problem. The hard problem is the one that gets skipped: **was this data ever allowed to leave in the first place?**

Article 1 built a pipeline that answers "can we automate this?" This article answers the question that has to come first — "may we send this data there at all?" — because getting the order wrong is how well-engineered pipelines become compliance incidents.

---

## The data in your alerts

A Wazuh alert is not an abstract event. It is a structured record of something that happened on a real machine, and it carries the identifying detail that made it useful for detection in the first place.

A single alert routinely contains the agent hostname and its internal IP, the source and destination addresses involved, the username or domain account tied to the event, the full process name and command-line arguments, file paths, and — depending on the decoder — fragments of the log line that triggered the rule. An authentication alert names the account. A suspicious-process alert quotes the command a person actually ran. A file-integrity alert exposes directory structure.

Put differently: a Wazuh alert stream is a running description of your internal network topology, your account namespace, and the behaviour of identifiable people. That is precisely why it is worth sending to an analyst. It is also precisely why sending it anywhere else is a decision, not a convenience.

Name the fields before you decide where they can go. You cannot govern data you have not looked at.

---

## What "processing" actually means

When alert data goes to a public LLM API, "processing" is not a figure of speech. The payload leaves your network boundary, transits a provider's infrastructure, is held in memory for the duration of the request, and may be retained in logs according to terms you probably have not read against this specific use case.

Most providers offer a data processing agreement. Many commit to not training on API inputs. Both matter. Neither is the same as having confirmed that *security telemetry* — a category with its own legal weight — is covered by the agreement you signed for general-purpose use.

There is a gap between "we have a DPA" and "we confirmed this DPA covers sending customer security telemetry to this endpoint." Organisations fall into that gap constantly, because the first statement feels like it implies the second. It does not. A DPA scoped to, say, marketing analytics does not silently extend to intrusion data about a hospital's domain controllers.

The rule is simple and unglamorous: **do not assume coverage. Confirm it, in writing, for this data class.** If that confirmation does not exist, the pipeline is not ready, regardless of how well it runs.

---

## The regulatory landscape, practically

This is not a legal survey. It is the short list of regimes that turn "we sent the alert out" into a reportable problem.

**GDPR.** Security logs are full of personal data. A username is personal data. A source IP tied to an identifiable person is personal data. Sending it to a third-party processor outside the EU — or to any processor without a valid legal basis and agreement — is a transfer that needs a basis. "We were debugging an alert" is not one.

**NIS2.** The directive raises the bar on the security of essential and important entities, and by extension on the security of the tooling those entities operate. A security operations pipeline that quietly exfiltrates telemetry to an ungoverned endpoint is not a strong control. It is a new attack surface and a governance failure wearing an automation costume.

**Customer contracts.** For a managed security provider, this is often the sharpest edge. The clause that says "customer data will be processed only within the following boundaries" was signed by someone, and it rarely anticipated an analyst pasting that customer's alerts into a public model. The contract does not care that the tool was helpful.

The through-line: the sensitivity of the data does not change because an AI is now reading it. The obligations that applied to the alert applied before the LLM existed. The pipeline just made it easy to forget them at scale.

The specific obligations differ by jurisdiction and evolve over time — a regulation cited here may read differently in two years. The architectural principle does not move: sensitive data in, obligations attached, and a decision required about where it is allowed to go. Track the details against your own jurisdiction; the structure of the problem outlasts any particular rule.

---

## Self-hosted models: the architecture of staying in control

The cleanest answer to "may this data leave?" is to make sure it does not.

Running an open-weight model on infrastructure you control keeps alert data inside your network boundary. Inference happens on your hardware, in your data centre or your customer's, under your access controls. The governance question changes shape entirely: instead of "is this cross-border transfer covered?" it becomes "who on our team can reach the inference endpoint?" — a question you were already answering for every other internal system.

This was a deliberate design choice in Article 1, not a happy accident. The pipeline's model dispatch layer is abstracted behind a single interface. Swapping a public API for a locally hosted inference endpoint is a configuration change and a new base URL — not a rewrite. The classification prompt, the rule-authoring loop, the validation against `wazuh-analysisd -t`: none of it knows or cares where the tokens are generated. **Backend-agnostic by design is what makes the governance decision reversible.**

The tradeoff is real and should be named. Self-hosted open-weight models available today are capable but not identical to the strongest hosted frontier models, and running them well costs GPU capacity, operational attention, and someone who owns the deployment. For the classification tier — structured reasoning over a well-defined input — locally hosted models are already more than adequate. For the rule-authoring tier, the quality gap is more noticeable, and the honest answer is that you test it against your own rule corpus before you trust it. Validation before automation applies to the model choice itself.

Capability versus control is a genuine tradeoff. But it is one you get to make deliberately — which is the entire point.

---

## Data residency in practice: the iSecNG approach

*This section reflects Dominik Sigl's operating model at iSecNG and should be read as one concrete implementation of the principles above, not the only valid one.*

Digital sovereignty is easy to say and harder to operate. At iSecNG the commitment is specific: security telemetry from German customers stays in Germany, end to end, including the AI inference layer. That is not a marketing line — it is a set of architectural constraints that rule out certain tools before evaluation even begins.

Operationally it means the inference endpoint sits on infrastructure inside the country, not a hyperscaler region that merely has a local zone but a foreign parent jurisdiction. It means access to that endpoint is inside the same identity and network controls as the SIEM itself. And it means the customer agreement states plainly where the data lives and who can touch it — so that the answer to "where did our alert data go?" is a location, a legal entity, and an access list, not a shrug.

The point is not that every organisation must self-host in-country. The point is that "digital sovereignty" only means something when it survives contact with the inference layer. An AI pipeline that respects data residency everywhere except the model call respects it nowhere.

---

## What needs to be in writing

Before any AI pipeline touches real alert data in production, four things exist as written artifacts — not as intentions, not as Slack messages, but as documents someone signed:

The **data processing agreement is confirmed for security telemetry specifically**, not inherited from generic API terms. The **customer is informed** if their data is in scope, with the AI processing disclosed rather than buried. The **backend decision is documented** — which model, where it runs, why — in a form an auditor can read. And there is a **review cadence**, because the model landscape changes faster than the contract, and a decision that was correct in one quarter can quietly stop being correct in the next.

If any of these four is missing, the pipeline runs in a lab, not in production. This is not bureaucracy. It is the difference between "we made a decision" and "a decision happened to us."

---

## The architecture decision record

The instrument for the third artifact is boring on purpose: an Architecture Decision Record. One page, made once, reviewed on a schedule.

```markdown
# ADR-014: Inference backend for the alert-tuning pipeline

## Status
Accepted — 2026-08-15. Review due 2027-02-15.

## Context
The false-positive tuning pipeline processes live Wazuh alerts containing
personal data (usernames, source IPs) and internal topology (hostnames,
paths). Alert data must not leave the organisation's control without a
confirmed legal basis.

## Decision
Inference runs on a self-hosted open-weight model on internal
infrastructure (site: DE-FRA-01). No alert data is sent to public LLM APIs.
The classification tier and the rule-authoring tier both use the local
endpoint via the pipeline's abstracted dispatch layer.

## Consequences
+ No cross-border transfer of security telemetry. GDPR/NIS2 exposure reduced.
+ Backend is swappable if capability needs change (config, not rewrite).
- Rule-authoring quality is validated against our own rule corpus, not assumed.
- We own GPU capacity and endpoint availability.

## Review triggers
- A materially stronger self-hostable model becomes available.
- Customer contract terms on data residency change.
- Provider terms for any fallback hosted model change.
```

An ADR is not paperwork. It is the record that turns an implicit choice into an accountable one — the thing you point to when someone asks, a year later, why the data flows the way it does. The decision that gets made once and revisited on a date you set in advance.

---

## Conclusion

The pipeline in Article 1 was engineered carefully. But engineering quality is not what determines whether it is safe to run. That is determined by a decision made before the first token is generated: where the data is allowed to go, confirmed in writing, owned by a person.

Governance is not the disclaimer at the end of the deployment. It is the first architectural constraint — the one that decides which architectures are even permitted. "May we?" precedes "can we?", and answering it is not a philosophical exercise. It is the choice of inference backend, the wording of a customer clause, the signature on an ADR. In regulated and managed-security settings, that answer is not a formality tacked onto a working pipeline — it is the thing a customer is actually buying: a security operation that can say where its data went and who decided.

Judgment before delegation. Before you delegate any part of security operations to a model, someone has to have judged where that model is allowed to run — and signed their name to the answer.

---

*Next in this series: [Detection Engineering at Scale](./03-detection-engineering-scale.md)*
