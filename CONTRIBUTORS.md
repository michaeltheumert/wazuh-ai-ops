# Contributors

## Authors

| Name | Role | Organization | Contact |
|------|------|-------------|---------|
| **Michael Theumert** | Lead Author, Series Editor | SECaaS.IT / XaaS Enterprise GmbH | [LinkedIn](https://www.linkedin.com/in/michael-theumert/) |
| **Dominik Sigl** | Co-Author | iSecNG GmbH | dominik.sigl@isecng.de |

---

## Article Responsibilities

| Article | Lead Author | Co-Author Contribution |
|---------|-------------|----------------------|
| 01 – Taming Alert Fatigue | Theumert | Review, sign-off |
| 02 – Responsible AI in Security Operations | Theumert | Data residency / digital sovereignty section, review |
| 03 – Detection Engineering at Scale | Sigl | Governance perspective, review |
| 04 – Alert Enrichment and Triage Automation | Sigl | AI pipeline architecture, review |
| 05 – AI Does Not Replace Analysts | Theumert | SOC practice input, review |

---

## Workflow

### Branches

Each article lives in its own feature branch:

```
article/01-taming-alert-fatigue
article/02-responsible-ai-operations
article/03-detection-engineering-scale
article/04-alert-enrichment-triage
article/05-ai-does-not-replace-analysts
```

`main` contains only content that has been mutually approved and is ready for publication.

### Review Process

1. Lead author opens a Pull Request from the article branch to `main`
2. Co-author reviews — comments are line-specific (GitHub review mode)
3. Lead author addresses feedback, marks threads resolved
4. The non-authoring co-author explicitly approves (GitHub "Approve" review) — the lead author cannot approve their own PR
5. Lead author merges — then submits to Wazuh Ambassador Program

### Review Language

Internal communication, PR comments, and review notes: **German, per Du**.  
All article content: **English**.

### Publication order

Articles are written and reviewed in numeric order (01 → 05); each is merged to `main` only once mutually approved. Actual publication dates are tracked in the LinkedIn content package, not here, so this document doesn't go stale every time a date shifts.

### Submission

After merge to `main`, the lead author submits to the Wazuh Ambassador Program.  
Both author names appear on every article in the series.

---

## Style

See [style-guide.md](./style-guide.md) for writing rules, voice, and recurring themes.
