# Detection Engineering at Scale

*Article 3 of 5 — AI-Augmented Wazuh Operations*

---

## Two kinds of blind spot

A new application goes live and its logs start arriving a week later. They reach the manager, they get written to disk, and nothing else happens. No decoder claims them, so no fields are extracted, so no rule can match on anything but a raw string. The source is onboarded in the sense that the bytes arrive.

Somewhere else in the same environment, IOCs get published on Monday and by Tuesday someone asks whether you are covered. You are not, because writing that detection means reading the technique, checking the IOCs and working out which log source would even see it, mapping the behaviour onto decoded fields, drafting a rule, testing it, and getting it reviewed.

Same problem at different stages. Detection coverage is rationed by the attention of the people who understand the logs, and those are the people already handling today's alerts. Coverage gets built in four stages: make the source legible, decide what is worth detecting, tune what fires, extend from external reporting. AI compresses part of each, and what it can be trusted with changes stage by stage along with the grounding available to it.

---

## Stage 1: basic coverage with logtest

Before any threat model, an unparsed source needs a decoder and a handful of baseline rules. The goal at this point is to make the source addressable, so that later rules have fields to match on.

`wazuh-logtest` is what makes this tractable with a model in the loop. It pushes one log line through the full pipeline and prints every phase: pre-decoding, decoding, rule matching. That output is the ground truth the model does not have.

```bash
echo '2026-08-04T09:12:44Z appsrv01 acme-portal: auth login_failed user=jdoe src=203.0.113.44 reason=bad_password' \
  | /var/ossec/bin/wazuh-logtest -v
```

```
**Phase 1: Completed pre-decoding.
	timestamp: '2026-08-04T09:12:44Z'
	hostname: 'appsrv01'
	program_name: 'acme-portal'

**Phase 2: Completed decoding.
	No decoder matched.
```

The loop is mechanical. Collect 20 to 50 raw lines covering every message type the application emits, hand them to the model with the phase output above, ask for a decoder and baseline rules, then run every line back through logtest. Phase 2 either shows the fields the model claimed it would extract, or it does not. Iterate on that difference until the two agree.

```xml
<decoder name="acme-portal">
  <program_name>^acme-portal$</program_name>
</decoder>

<decoder name="acme-portal-auth">
  <parent>acme-portal</parent>
  <regex offset="after_parent">^ auth (\S+) user=(\S+) src=(\S+) reason=(\S+)$</regex>
  <order>action, srcuser, srcip, status</order>
</decoder>
```

One instruction belongs in the prompt explicitly: map onto Wazuh's conventional field names (`srcip`, `srcuser`, `dstuser`, `url`) wherever the data fits them. A model left to itself invents readable names like `login_source_address`, which parse without complaint and cut the new source off from every generic correlation and frequency rule that keys on the standard names.

Baseline rules are a level 0 base rule plus one rule per event class:

```xml
<group name="acme-portal,">
  <rule id="100200" level="0">
    <decoded_as>acme-portal</decoded_as>
    <description>acme-portal messages</description>
  </rule>

  <rule id="100201" level="5">
    <if_sid>100200</if_sid>
    <field name="action">^login_failed$</field>
    <description>acme-portal: authentication failure for $(srcuser) from $(srcip)</description>
  </rule>
</group>
```

Collecting every message type assumes you know what the application can emit. In a perfect world you would: the vendor ships a catalogue of every event, every severity, and every field, and one pass covers all of it. In the other 99% of cases no such catalogue exists. You get whatever the log file happened to contain during the window you sampled, which is the subset of behaviour the application produced while nothing was going wrong.

So plan for the gap. Keep the level 0 base rule matching on `decoded_as` alone, then sample the archive periodically for events that hit it and no child rule. Those are the message types nobody has decoded yet, and they surface after version upgrades and the first time something on that host breaks.

This is coverage in the weak sense: the source can be queried and built on, and nothing about a threat has been decided yet. Decoder syntax and field naming vary across Wazuh 4.x releases, so validate against the version you run rather than against what the model has read.

---

## Stage 2: threat modelling produces the backlog

Stage 1 tells you what the source can say. It does not tell you what deserves an alert. Skip the threat model and you get a ruleset that mirrors the log format instead of the threat: an alert per event class the application happens to emit, at levels somebody guessed.

Run the threat model on the asset rather than on its log format. What does this application do, who can reach it, what does an attacker gain, which paths lead there. The output is a short list of concrete attack paths, each resolving into one or more techniques, and each technique into a defensive decision: prevent, detect, or accept. Only the ones marked detect become rules, and each of those needs a log source carrying the evidence.

| Attack path | Technique | Decision | Evidence in the logs |
|---|---|---|---|
| Password spraying against the portal | T1110.003 | Detect | `srcip`, `srcuser`, `action` from stage 1 |
| Session token replayed from elsewhere | T1550.004 | Detect | not available: no session ID or user agent is logged |
| Admin role granted outside change window | T1098 | Detect | `action=role_granted`, `dstuser` |

The third column is where people stop. The fourth decides whether a rule is possible at all, and the second row shows what happens when the answer is no: a logging change request, which has to land before any rule can be written.

### From technique to rule

ATT&CK describes behaviour in prose. A Wazuh rule needs the field holding the evidence, the value separating malicious from routine, and the parent rule to inherit from. None of that lives in the ATT&CK entry.

This is where AI drafting starts paying off, because stage 1 produced what the model was missing: a verified field list and real decoded events.

```python
prompt = f"""You are writing a Wazuh detection rule for Wazuh {wazuh_version}.

TECHNIQUE
{technique_id}: {technique_description}

DETECTION INTENT (from the threat model)
{detection_intent}

DECODED SAMPLE (real event, phase 2 output from wazuh-logtest)
{logtest_phase2}

AVAILABLE FIELDS (verified present; nothing else exists)
{field_list}

PARENT RULE
Inherit from rule {parent_sid} via <if_sid>{parent_sid}</if_sid>.

CONSTRAINTS
- Match only on fields listed above.
- Use <field name="..."> for decoded fields. Do not invent field names.
- Use id="{assigned_sid}" exactly.
- Output only the <rule> block, no commentary.
"""
```

Asking for a rule from the technique description alone produces plausible fiction: field names that sound right for a product like yours and do not exist in your data. Fluency is highest where grounding is weakest.

### What the parser rejects anyway

Even with good grounding, generated rules fail to load in recognisable ways. Wazuh's rule schema is thin in training data, so models reason about it by analogy to XML they have seen more of: `<options>no_alert</options>` appears regularly and does not exist, `<if_sid>` gets used where `<if_matched_sid>` is meant, `<frequency>` arrives without `<timeframe>`, rule IDs collide with something already deployed.

No prompt removes this, because the model holds a distribution over text that resembles rules, with no schema behind it. Some of it is better handled in code: the stage 3 pipeline pre-assigns the rule ID, instructs the model to use exactly that ID, then overwrites the attribute anyway, because the instruction gets ignored often enough that deterministic correction is cheaper than another round trip.

### Two checks, not one

`wazuh-analysisd -t` parses the whole ruleset including the candidate and exits non-zero on any load error. `wazuh-logtest` answers the other question: given this event, does the rule fire, and at what level. A rule can pass the first and match nothing at all, which is the failure that looks like safety. An empty alert queue reads the same whether nothing happened or nothing was watching.

So a detection rule needs both checks, plus known-good events pushed through logtest to confirm it stays quiet on those.

---

## Stage 3: fine-tuning against real alerts

Rules from stage 2 go live and produce volume. Some of that volume is noise, and noise is what trains analysts to close alerts without reading them.

This is where the false positive pipeline from Article 1 attaches. The reference implementation runs two processes. `alert_monitor.py` tails `alerts.json` and turns noise into pull requests. `rule_sync.py` polls the rules repository, copies merged rule files into the Wazuh volume, and runs `wazuh-control reload`. The merge is the deployment trigger, so nothing reaches the manager until someone has approved the diff.

The monitor tails by byte offset rather than inotify, whose events are unreliable on Docker volume paths, and starts at the current end of file so a restart does not reprocess history. For each new alert: skip it if an open PR already exists for that rule ID (the branch convention `tune/rule-<id>-<timestamp>` makes that a cheap check), classify with the fast model, act only above a configurable confidence threshold of 0.8, draft a narrow rule with the stronger model, validate, and open a PR described by the fast model from the classification reasoning.

Narrow is the whole point, because a rule that silences the parent outright hides every future true positive sharing it. Here is one the pipeline produced and a reviewer merged:

```xml
<group name="local,">
  <rule id="110002" level="0">
    <if_sid>92058</if_sid>
    <field name="win.eventdata.image" type="pcre2">(?i)\\\\Windows\\\\System32\\\\sdbinst\.exe$</field>
    <field name="win.eventdata.commandLine" type="pcre2">(?i)sdbinst\.exe\s+-m\s+-bg$</field>
    <field name="win.eventdata.parentImage" type="pcre2">(?i)\\\\Windows\\\\System32\\\\svchost\.exe$</field>
    <field name="win.eventdata.parentCommandLine" type="pcre2">(?i)-s PcaSvc</field>
    <field name="win.eventdata.user" type="pcre2">(?i)^NT AUTHORITY\\\\SYSTEM$</field>
    <description>Suppress sdbinst.exe -m -bg maintenance invocation launched by PcaSvc (legitimate Windows compatibility database maintenance)</description>
  </rule>
</group>
```

Five constrained fields including the parent process and its command line. `sdbinst.exe` run by anything other than `svchost.exe -s PcaSvc`, or with different arguments, still alerts. That specificity is the difference between tuning and blinding, and it is what a reviewer checks first.

Validation runs inside the container: the candidate is base64-piped into a temporary file under `/var/ossec/etc/rules/`, `wazuh-analysisd -t` runs, the file is removed regardless of outcome, and a failure sends the daemon's error text back to the authoring model. Five attempts, then the pipeline logs and gives up rather than opening a PR nobody asked for.

### Working with real alert data

Stages 1 and 2 send samples you chose and can redact. Stage 3 runs continuously against live production alerts: hostnames, domain accounts, source addresses, full command lines, file paths, and whatever else the decoder pulled out of the raw line. The suppression rule above contains a real host's process tree.

Article 2 covers this decision in full and detection engineering gets no discount on it. Confirm the data processing agreement covers security telemetry specifically rather than by inheritance from general API terms, inform the customer if their data is in scope, and record the backend choice in an ADR with a review date. The reference implementation keeps the choice reversible: one dispatch function sends prompts either to a hosted API or to a locally running endpoint, selected by a single environment variable, so moving inference in-house is configuration rather than a rewrite. If those answers are not written down yet, run stage 3 against lab data and keep the production loop manual.

---

## Stage 4: turning CTI into rules

Once the loop runs, external reporting becomes an input instead of a fire drill. A vendor report, a sector advisory, a CVE with exploitation detail: each arrives as prose and has to leave as a rule, a logging gap, or a documented decision to accept. Reading 40 pages and extracting the candidate detections is a task models are good at, and what comes back is two things with different shelf lives.

Observables (hashes, domains, addresses) go stale in weeks. They belong in a CDB list behind one lookup rule. Updating a list means editing a text file; updating values baked into individual rules means touching XML and reloading the ruleset every time a feed refreshes.

```xml
<rule id="100310" level="10">
  <if_sid>100200</if_sid>
  <list field="srcip" lookup="address_match_key">etc/lists/cti-known-c2</list>
  <description>acme-portal: connection from address on CTI watchlist</description>
</rule>
```

Behaviours last longer and justify their own rules, so they go through the stage 2 prompt with the verified field list attached and through both validation checks. The gate is the one from the threat model: whether your logs can see the behaviour at all. A report describing registry manipulation on endpoints where you collect no Sysmon data produces a logging requirement, not a detection.

CTI also feeds backwards. A report showing a technique used against your sector moves an entry in the threat model from accept to detect, which puts stage 2 back in motion and starts the cycle again.

---

## What none of this fixes

Rules decay. Attackers change a flag, switch to a different signed binary, split one step into two, and a rule tuned to last year's procedure example stops matching. It still loads. It still shows green. A model can draft from a 2024 procedure example but cannot tell you whether that example still describes 2026, because it does not watch your environment and has access to nothing except text about it.

So every rule needs a technical owner: someone who revisits it when the technique moves, confirms it fires on current variants, and retires it when the log source goes away. (Who is accountable when a decayed rule misses an intrusion is an organisational question, and Article 5 takes it up.)

The other limit is fixed. The model cannot tell you whether a field exists in your environment, only whether it exists in the sample you showed it. Every stage above is built to hand it that sample and check the output against a system that knows the answer. Take `wazuh-logtest` and `wazuh-analysisd -t` out of the loop and what remains is confident text.

---

## Conclusion

Coverage builds in order. Decode the source before writing rules for it. Model the threat before deciding what deserves an alert. Tune against real alerts before trusting the volume. Consume CTI once the loop can absorb it. AI drafts at every one of those stages and validates at none of them: logtest and analysisd do that, and a person merges the pull request.

The compression is real and it matters when coverage is rationed by attention. What does not compress is knowing which logs exist, what they contain, and whether a rule catches the thing it was written for.

Validation before automation. A rule you have not tested is a rule you do not have, and a rule tested against logs you do not understand is a rule you only think you have.

---

*Next in this series: [Alert Enrichment and Triage Automation](./04-alert-enrichment-triage.md)*
