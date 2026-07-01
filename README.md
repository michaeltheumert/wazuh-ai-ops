# AI-Augmented Wazuh Operations

A five-part article series on controlled AI integration in Wazuh-based security environments.  
Published as part of the [Wazuh Ambassadors Program](https://wazuh.com/community/ambassador-program/).

> *Validation before automation. Judgment before delegation.*

---

## About This Series

Most AI-in-security articles fall into one of two categories: theoretical frameworks that never touch a real SIEM, or automation demos that skip the hard questions about validation and control.

This series is neither.

*AI-Augmented Wazuh Operations* covers how AI can be integrated into Wazuh-based security operations in a way that is practical, verifiable, and auditable — using Wazuh as the implementation environment throughout. Not AI as a replacement for analysts, but as a tool that handles the repetitive, well-defined work quickly enough that analysts can focus on the decisions that actually require judgment.

Each article is grounded in real implementation experience. The code runs. The rules are validated against real Wazuh environments. The governance questions are answered before deployment, not after.

---

## Articles

| # | Title | Framework Layer | Lead Author | Status |
|---|-------|----------------|-------------|--------|
| 1 | [Taming Alert Fatigue](./articles/01-taming-alert-fatigue.md) | Improve | Theumert | ✅ Ready |
| 2 | [Responsible AI in Security Operations](./articles/02-responsible-ai-operations.md) | Govern | Theumert + Sigl | 🔄 In Progress |
| 3 | [Detection Engineering at Scale](./articles/03-detection-engineering-scale.md) | Detect | Sigl | 📋 Planned |
| 4 | [Alert Enrichment and Triage Automation](./articles/04-alert-enrichment-triage.md) | Understand | Sigl | 📋 Planned |
| 5 | [AI Does Not Replace Analysts](./articles/05-ai-does-not-replace-analysts.md) | Reflect | Theumert | 📋 Planned |

**Publication schedule:** Weekly, starting August 2026.

---

## Authors

**Michael Theumert**  
Co-Founder, SECaaS.IT (XaaS Enterprise GmbH) · CISO, ValueMiner GmbH · Wazuh Ambassador  
[LinkedIn](https://www.linkedin.com/in/michael-theumert/) · [SECaaS.IT](https://secaas.it)

**Dominik Sigl**  
Co-Founder, iSecNG GmbH · Wazuh Community  
[LinkedIn](https://www.linkedin.com/in/dominik-sigl/) · [iSecNG](https://www.isecng.de)

---

## Repository Structure

```
wazuh-ai-ops/
├── README.md                             ← You are here
├── style-guide.md                        ← Writing rules, voice, recurring themes
├── CONTRIBUTORS.md                       ← Collaboration guidelines
├── proposal/
│   └── ambassador-proposal.md            ← Wazuh Ambassador Program proposal
├── articles/
│   ├── 01-taming-alert-fatigue.md
│   ├── 02-responsible-ai-operations.md
│   ├── 03-detection-engineering-scale.md
│   ├── 04-alert-enrichment-triage.md
│   └── 05-ai-does-not-replace-analysts.md
└── assets/
    └── diagrams/                         ← SVG/PNG illustrations for articles
```

## Workflow

- Each article lives in a feature branch: `article/01-taming-alert-fatigue`
- Pull Request per article → review → merge to `main` after mutual sign-off
- `main` contains only published or fully approved content

See [CONTRIBUTORS.md](./CONTRIBUTORS.md) for details.

---

## License

Articles in this repository are published under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).  
Code samples are published under [MIT License](https://opensource.org/licenses/MIT).
