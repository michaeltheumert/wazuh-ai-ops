# Alert Enrichment and Triage Automation

*Article 4 of 5 — AI-Augmented Wazuh Operations*

---

## The Alert That Tells You Nothing

A Tier-1 analyst opens the next alert in the queue. Failed logins followed by a success, from an IP she doesn't recognise, against an account she's never heard of. The alert is technically complete: rule ID, timestamp, source address, username, the decoded fields all present. Nothing is missing.

And she still can't triage it, because everything that would make the decision easy is somewhere else. Is that IP a VPN egress the sales team uses? Is that account a service principal that logs in oddly by design? Did the same address show up in four other alerts this week? Is this host normally this noisy? The alert answers none of that. It just tells her something happened.

Good triage is not a function of the data in the alert. It is a function of the context around it — and assembling that context is where a Tier-1 shift actually goes. AI can assemble it fast. What AI does with it afterward is where the discipline has to hold.

---

## What triage actually costs

The instinct is to measure triage in time per alert. That is the wrong denominator. What matters is time per *correct decision* — and the two come apart quickly.

Closing an alert fast is easy. Closing it correctly means having gathered enough context to know that "benign" is actually true and not just convenient. When context is expensive to assemble, analysts economise, and the economising is invisible until it isn't: a false negative closed in nine seconds looks identical to a true benign closed in nine seconds, right up until the incident review. False positives at least announce themselves as fatigue. False negatives just accumulate silently.

So the bottleneck in triage is not processing speed. It is contextual judgment at volume — the analyst's ability to gather and weigh the surrounding facts fast enough to decide correctly, alert after alert, through a full shift. Speed helps only if it is speed at assembling context, not speed at closing tickets. Those are different things, and conflating them is how a SOC gets faster and worse at the same time.

---

## The context an alert doesn't contain

Watch an experienced analyst triage the login alert above and most of what they do is retrieval, not reasoning. They already know the questions; the work is answering them.

Is this host normally noisy, or is this out of character? Is the user travelling this week, which would explain the unfamiliar source? Has this IP appeared in other alerts recently, suggesting a pattern rather than an isolated event? Is this process expected on this class of asset, or does it belong to a server that should never run it? None of these answers is in the alert. Each lives in a different system — asset inventory, directory, HR calendar, the SIEM's own history, a threat-intel feed — and the senior analyst's real advantage is knowing which system holds which answer and how to get it quickly.

That knowledge is exactly what a Tier-1 analyst is still building, and it is exactly the kind of retrieval-and-assembly work a machine does well. The gap between "the data exists" and "the decision is easy" is an assembly gap. Closing it is where AI earns its place in triage.

---

## Enrichment: assembling the picture

Enrichment is the automatable half. Each context question maps to a source that can be queried without a human in the loop.

IP reputation comes from external threat-intel feeds. Asset context — owner, class, expected software — comes from a CMDB or asset inventory. User profile — role, department, normal login geography — comes from the directory, sometimes an HR system. Historical alert frequency comes from Wazuh's own indexer: how often has this rule fired for this host, this IP, this user, over the last week. In a typical Wazuh deployment, most of this is reachable via API, and none of it requires judgment to *fetch*.

Some enrichment stays human, and it is worth being honest about which. "Is this user actually travelling" may live in a system no API reaches, or in a Slack message to the user's manager. Enrichment automates the sources that are queryable and flags the ones that are not — it does not pretend the un-queryable context does not exist. A brief that silently omits what it couldn't reach is worse than one that says "travel status unconfirmed," because the first hides its own blind spot.

---

## AI as analyst assistant

Once the context is assembled, the model's job is narrow and specific: turn a pile of enrichment data into a short, readable triage brief. Not a verdict — a brief.

The distinction is the whole point. The prompt asks for a summary of what the enrichment shows and which facts a human should weigh, explicitly not for a disposition:

```python
prompt = f"""You are assisting a SOC analyst with triage. Summarise the
alert and its enrichment context in three sentences. State what is known,
what is missing, and which facts most warrant analyst attention.

Do NOT output a disposition (benign / malicious / escalate). That decision
belongs to the analyst. If the enrichment is incomplete, say what is missing.

ALERT
{alert_json}

ENRICHMENT
{enrichment_data}
"""
```

A good brief reads like the two sentences a senior analyst would say leaning over a junior's shoulder: "The source IP is a known Tor exit and this account has never logged in from outside Germany before — but the account is a test service principal, and travel status is unconfirmed. Worth a look before you close it." What the model gets wrong is instructive: it will sometimes state a missing fact with the same confidence as a known one, or imply a disposition it was told not to make. The brief is an input to judgment, not a substitute for it, and it has to be read as one.

---

## Telemetry is evidence, never instruction

Everything this pipeline hands to the model — the alert JSON, the enrichment payloads, the threat-intel record, the command line a host actually ran — originates outside anyone's control. A compromised endpoint can produce a process name or a log line deliberately crafted to look like an instruction rather than data. Once a pipeline lets a model call tools or take the next step based on what it read, that crafted line is no longer a curiosity — it is an attack surface.

The mitigation is architectural, not a smarter prompt:

- Never derive system instructions from telemetry content — telemetry fills a data field, never the instruction itself.
- Treat structured fields (hostname, user, command line) as data, not as text to be interpreted as directives, even inside the prompt.
- Allowlist tool permissions explicitly; do not let a model's output decide which tool runs next.
- Never execute model output directly as a shell, XML, or API command — the validation loop in Article 1 exists precisely so nothing the model writes reaches the system unchecked.
- Mark enrichment from sources you do not control as untrusted, and say so in the brief.
- Keep credential boundaries between the orchestrator and the model — the model should never hold or see credentials it does not need for the current step.

None of this is exotic once it is named. It is the same discipline as validating a suppression rule before it loads: assume the input can be adversarial, and design so that assumption costs nothing when it turns out to be true.

---

## A concrete pipeline: Wazuh + n8n + LLM

The pieces fit together without custom glue code. Wazuh fires an alert to a webhook. An n8n workflow catches it, calls the enrichment sources in parallel, hands the assembled context to the model for a brief, and posts the result to wherever the analyst already works — a dashboard, a ticket, a channel.

The division of labour is clean and worth stating explicitly. **n8n orchestrates**: it receives the webhook, fans out the enrichment API calls, handles retries and timeouts, and routes the output. **The model summarises**: it turns assembled context into a brief and nothing more. **The analyst decides**: the brief lands in front of a person who makes the call. Each layer does the thing it is good at and none reaches into the next.

Two boundaries in this architecture are not optional. First, the pipeline output is a prioritised brief, never a closed ticket — the model does not dispose of alerts. Second, the moment the alert and its enrichment reach the model, everything from Article 2 applies: this is production security telemetry crossing a boundary. If that model call goes to a public API, hostnames, accounts, and IPs go with it. The enrichment step, which pulls in threat-intel and directory data, often makes the payload *more* sensitive, not less. The inference endpoint belongs inside your control for exactly the reasons Article 2 laid out — enrichment does not change the governance answer, it raises the stakes of getting it wrong.

---

## Escalation: AI surfaces, analyst decides

The pipeline's output is a surfaced fact set, ranked. "Escalate" in this context does not mean the AI escalated — it means the AI made escalation-worthy facts visible fast enough that the analyst could decide to escalate. The verb stays with the person.

This is why the model must never close a ticket on its own. Not because it would always be wrong — it would often be right — but because a closed ticket is a decision, and decisions need an owner who can be asked, later, why. An alert auto-closed by a model has no one who decided it. When the incident review asks "who looked at this and judged it benign," the answer cannot be "the pipeline." The accountability chain has to terminate in a person, and it only does that if a person is the one who acts.

Judgment before delegation. The pipeline delegates retrieval and summarisation freely. It delegates the decision to no one.

---

## This is not SOAR — and that's not a contradiction

It is tempting to call this SOAR, and worth resisting, because the confusion leads to real architectural mistakes.

SOAR automates *response*: it takes actions — isolate the host, disable the account, block the IP — according to a playbook. This pipeline automates *triage input*: it assembles the context a human needs to decide whether any action is warranted at all. One acts on the world; the other prepares a person to. They sit on opposite sides of the decision, and the decision is the human's.

They are complementary, not competing. A mature SOC might well run both: this pipeline enriches and briefs, the analyst decides, and *then* a SOAR playbook executes the response the analyst approved. The mistake is letting the enrichment pipeline drift across the line into taking actions, because it was never designed with the safeguards a response-automation tool needs. Enrichment that quietly starts disposing of alerts is a SOAR system that nobody threat-modelled. Knowing where this pipeline ends is what keeps it safe.

---

## Conclusion

AI can assemble context at a speed no analyst can match — querying five systems in parallel and handing back a readable brief before a human has finished reading the alert. For a Tier-1 queue rationed by the cost of context, that is a real gain, and it makes junior analysts meaningfully faster at the part of the job that used to require seniority.

But assembling context is not the same as judging it. The model cannot tell whether the picture it assembled is complete, whether the missing fact is the one that mattered, or whether this pattern is dangerous in *this* environment. In day-to-day SOC operations that gap is the whole difference between a fast queue and a well-run one. It surfaces. The analyst decides.

Judgment before delegation. The pipeline hands the analyst everything except the one thing that has to stay theirs.

---

*Next in this series: [AI Does Not Replace Analysts](./05-ai-does-not-replace-analysts.md)*
