# Customers and jobs to be done

Status: desk-research hypotheses, not validated personas. Access date: 2026-10-16.

The [2026 Stack Overflow knowledge survey](https://survey.stackoverflow.co/2026/knowledge) reports strong demand for source attribution in AI answers. Its [trust question](https://survey.stackoverflow.co/2026/ai/data/ai-trust) shows conditional trust when output is verifiable. This supports testing evidence visibility, not a claim that respondents want this product or will pay. The sample is self-selected developers; do not extrapolate to every enterprise buyer.

| Segment | Decision/job hypothesis | Current alternative evidenced in catalog | What must be learned |
| --- | --- | --- | --- |
| Local AI enthusiasts | What runs on my existing hardware? | llmfit, ModelFit, CanRun | Is uncertainty or installation the real bottleneck? |
| Individual developers | Which model/provider fits this workload? | OpenRouter, Artificial Analysis | Frequency of comparison and switching cost |
| AI application developers | Assemble a workable RAG/agent stack | Dify, Langflow, Flowise | Whether pre-build planning saves measurable effort |
| ML engineers | Match model, quantization and serving runtime | Hugging Face, llmfit | Required fidelity versus own scripts |
| Infrastructure engineers | Capacity, reliability and cost at concurrency | SkyPilot, Runpod, Vast | Capacity procurement and operational constraints |
| Startup founders | Cheapest adequate stack | Aggregators and managed builders | Who owns budget and purchasing authority? |
| Enterprise architects | Explainable compatible choices with provenance | Existing vendor/platform evaluation | Procurement, residency and policy requirements |
| IT administrators | Deploy/manage permitted local or hosted tools | Ollama and managed services | Installation rights, support and fleet needs |
| AI researchers | Reproducible system comparison | Harness Bench, lm-evaluation-harness | Which versions and traces make a result reusable? |
| AI consultancies | Compare and share client configurations | Documents, calculators and workflow platforms | Recurring projects, collaboration and export needs |

These alternatives' existence is evidenced by [the catalog](competitors.json); usage by each segment is a hypothesis. No interviews, customer identities or private content were collected.

## Interview protocol

Ask about the last real selection decision, its trigger, tools, time spent, failure consequences, spend authority and alternatives. Ask the participant to reconstruct a recent configuration before showing any concept. Then compare a baseline workflow with a prototype decision record. Measure task completion, unsupported assumptions, time and desire to reuse; collect reasons for rejecting it. Ask about existing spend before presenting hypothetical price points. Separate user from buyer.

Initial sampling proposal: seek coverage across local enthusiasts, application developers and infrastructure/consultancy buyers, then expand only if material new jobs appear. This is a recruitment design, not a completed sample or a statistical power claim. The coordinator must approve recruitment channels, informed consent, retention and anonymized reporting before outreach. No conversion rate or willingness-to-pay result exists yet.
