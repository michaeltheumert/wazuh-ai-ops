# AI-Augmented Wazuh Operations

*A five-part series on controlled AI integration in SIEM environments.*

Michael Theumert (SECaaS.IT) · Dominik Sigl (iSecNG)

---

## Why this series exists

Most writing about AI in security operations falls into one of two camps. One treats AI as a coming wave that will remake the SOC — long on transformation, short on anything you could deploy on Monday. The other is pure demo: a working automation, shown end to end, with the hard questions about validation, data, and accountability left offstage.

This series is neither, because both camps make the same mistake. They treat AI as a new category that needs its own rules. It does not.

The position running through all five articles is simpler and more demanding: **AI has to earn its place inside the engineering discipline that already exists.** A rule an AI drafts faces the same validation as one an engineer wrote by hand. Telemetry an AI processes falls under the same data-governance rules it always did. A decision an AI informs still needs a human who can be held to it. Nothing gets relaxed because the tool is new — and the standards apply hardest exactly where the tool is most impressive, because that is where it is easiest to stop checking.

Two principles carry that position, and they recur deliberately throughout:

> **Validation before automation.**
> **Judgment before delegation.**

Neither is a slogan. They are the order in which the work has to happen: validate, then automate; judge what can be delegated, then delegate it. Put the other way around, they describe most of the ways AI integration in security operations goes wrong.

Wazuh is the environment throughout — a real, open, widely deployed platform, not a hypothetical. Every technical example targets it directly. But the argument is not Wazuh-specific. It is about what responsible AI integration looks like in any detection platform where correctness, auditability, and accountability are not optional.

---

## The arc

The five articles move through the layers of a security operation, and the order is intentional.

| # | Article | Layer | The question it answers |
|---|---------|-------|------------------------|
| 1 | Taming Alert Fatigue | Improve | How can AI reduce false positives without creating new blind spots? |
| 2 | Responsible AI in Security Operations | Govern | When is AI *allowed* to process real security telemetry? |
| 3 | Detection Engineering at Scale | Detect | Can AI help write rules for techniques not yet seen? |
| 4 | Alert Enrichment and Triage Automation | Understand | Can AI give analysts senior-level context at speed? |
| 5 | AI Does Not Replace Analysts | Reflect | Which decisions must stay human, and why? |

Article 1 establishes the core pattern on a concrete, bounded use case: AI drafts, the system validates against the running daemon, a human reviews. Article 2 comes second on purpose — governance is not an appendix to a working pipeline, it is the constraint that decides which pipelines are permitted at all. Articles 3 and 4 go deeper into detection and triage, each carrying the governance question forward rather than leaving it behind. Article 5 makes explicit what the first four demonstrate: the boundary between routine work and human judgment is an architectural decision, not a limitation waiting to be automated away.

---

## The two perspectives

The series is written by two practitioners who operate Wazuh from different ends of the same problem.

**Michael Theumert (SECaaS.IT)** works from the governance and managed-security side: CISO responsibilities, GRC, AI integration in regulated environments — NIS2, KRITIS, healthcare — where detection quality, auditability, and accountability have to coexist under external scrutiny. He set the framing of the series and edits it.

**Dominik Sigl (iSecNG)** works from detection engineering and operations: hands-on rule development, SIEM operation, incident response, and a data-residency practice built on keeping security telemetry inside German infrastructure end to end.

The split is not cosmetic. The governance argument in Article 2 only holds because someone operates it in production; the detection engineering in Article 3 only holds because someone governs it. Where each article names an author's perspective, it is marking whose operational reality the argument is grounded in — not assigning credit. Both names appear on every article.

---

## How to read it

Each article stands on its own — you can start with the one closest to your problem. Read in order, they build a single argument about where controlled AI integration belongs in a Wazuh operation and where it does not.

The code runs. The rules are meant to be validated against a real Wazuh environment before you trust them — the articles say so explicitly, and say where. The governance questions are answered before deployment, not after.

That is the whole point. Not what AI *can* do in security operations, but where it has to prove itself against the standards the discipline already holds.

---

*Series repository: [github.com/michaeltheumert/wazuh-ai-ops](https://github.com/michaeltheumert/wazuh-ai-ops)*
