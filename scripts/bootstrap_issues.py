"""Idempotently create the AI Builder research issue hierarchy with GitHub CLI.

Run from this repository after publishing it: python scripts/bootstrap_issues.py
Requires `gh` authentication with repository issue write access.
"""

import json
import subprocess
import time


REPO = "CompleteDotTech/pickyour.ai"
WORKSTREAMS = [
    (
        "T0", "Configuration", "CompleteDotTech",
        [
            ("Workload / Use Case", "Define workload taxonomy, modality, quality and latency targets, traffic and concurrency, data sensitivity, budget, and how those inputs filter later options.", "User goals and constraints"),
            ("Deployment Mode (API / Managed / Self-Hosted)", "Compare API, managed deployment, and self-hosted paths; document control, data residency, operations, model access, and cost implications.", "Workload / Use Case"),
        ],
    ),
    (
        "T1", "Model Selection", "zwright8",
        [
            ("Model Provider", "Build a provider catalog with deployment modes, regions, model availability, contractual constraints, data handling, and pricing provenance.", "Deployment Mode [T0]"),
            ("AI Model", "Define a versioned model catalog and selection criteria for modality, capability, licensing, availability, model format, GPU fit, and inference engine support.", "Provider [T1] + GPU [T2] + Inference Engine [T2]"),
            ("Context Window", "Research advertised versus usable context, input/output limits, tokenization, KV-cache memory, latency and price effects by model and provider.", "Model [T1] + Provider [T1] + GPU [T2]"),
        ],
    ),
    (
        "T2", "Infrastructure", "Mattycodes69",
        [
            ("Hosting", "Compare API-adjacent managed hosting, dedicated services, cloud GPUs, and self-hosting; capture region, availability, networking, storage and operations constraints.", "Deployment Mode [T0] + GPU Availability"),
            ("GPU / Compute", "Define capacity estimates for model weights, context/KV cache, precision, fine-tuning, concurrency, throughput, latency and headroom; distinguish measured from estimated.", "AI Model [T1] + Context [T1] + Fine-Tuning [T5] + Concurrency"),
            ("Inference Engine", "Catalog supported model architectures/formats, quantization, hardware, batching, serving features, and deployment constraints including fine-tuned adapters.", "AI Model [T1] + GPU [T2] + Model Format + Fine-Tuned Model [T5]"),
        ],
    ),
    (
        "T3", "Knowledge & Retrieval (Optional)", "zabyxc01",
        [
            ("Knowledge Base", "Define ingestion, data source permissions, parsing, chunking, metadata, freshness, storage, access control, and deletion requirements.", "Data Sources [T4] + Storage"),
            ("Embedding Model", "Compare modality, language, dimension, context, quality, license, hosting, throughput and cost; record reindexing implications.", "Data Type + Hosting [T2]"),
            ("Vector Database", "Evaluate storage and retrieval backends by filtering, hybrid search, scale, tenancy, operations, hosting fit and cost; keep vector DB optional where simpler retrieval suffices.", "Embedding Model [T3] + Hosting [T2]"),
            ("RAG", "Specify retrieval pipeline, citations, relevance evaluation, freshness, permissions, failure modes and compatibility with model context; compare vector and non-vector backends.", "Knowledge Base [T3] + Embeddings [T3] + AI Model [T1] + Retrieval Backend"),
        ],
    ),
    (
        "T4", "Agents & Integrations (Optional)", "CompleteDotTech",
        [
            ("Agent Framework", "Compare orchestration approaches, model/tool support, state, observability, portability, RAG integration and operational complexity.", "AI Model [T1] + RAG [T3] + Tools + Memory"),
            ("Tools & APIs", "Define tool catalog metadata, auth, permissions, rate limits, side effects, failure behavior and approval/guardrail needs.", "Agent Framework [T4] + Guardrails [T6]"),
            ("MCP Servers", "Research MCP transport and tool compatibility, hosting, authentication, trust boundaries and framework support.", "Tool Compatibility + Hosting [T2] + Agent Framework [T4]"),
            ("Memory", "Separate session state, durable user memory and retrieval; define retention, consent, storage, deletion and optional vector search.", "Agent Framework [T4] + Storage [T3] + Vector Database [T3] (Optional)"),
        ],
    ),
    (
        "T5", "Training & Fine-Tuning (Optional)", "appletechie",
        [
            ("Training Framework", "Determine which selected models permit training or adapters and compare supported methods, formats, licenses and export paths.", "AI Model [T1] + Model Access"),
            ("Training Compute", "Estimate hardware memory, time, storage, throughput, distributed needs and total cost under the selected framework and GPU path.", "Framework [T5] + GPU [T2]"),
            ("Training Dataset", "Define source rights, data quality, formatting, split design, privacy, lineage, deduplication and leakage checks.", "Knowledge Sources [T3]"),
            ("Fine-Tuned Model", "Define artifact format, provenance, versioning, evaluation and deployment compatibility; feed its requirements back into inference and evaluation.", "Framework [T5] + Compute [T5] + Dataset [T5]; impacts Inference [T2] + Evaluation [T6]"),
        ],
    ),
    (
        "T6", "Deployment & Operations", "PUSHINGSQUARES",
        [
            ("Guardrails", "Research input/output controls, tool permissions, data boundaries, human review, policy configuration and failure behavior by deployment path.", "Model [T1] + RAG [T3] + Tools [T4]"),
            ("Evaluation", "Define task-specific quality, safety, retrieval, agent and fine-tuning evaluations; include baselines, datasets, regression gates and cost/latency measurement.", "Model [T1] + RAG [T3] + Agents [T4] + Fine-Tuning [T5]"),
            ("Deployment", "Specify packaging, configuration, rollout, rollback, secrets, access control and readiness checks for the selected stack.", "Provider [T1] + Infrastructure [T2] + Knowledge [T3] + Agents [T4] + Guardrails [T6] + Evaluation [T6]"),
            ("Monitoring", "Define health, quality, latency, cost, usage, safety and data freshness signals across active components; include alert thresholds and privacy.", "All Active Components [T1–T5]"),
            ("Cost Estimate", "Build a sourced scenario calculator with token, compute, storage, API and training costs, units, region, currency, assumptions and uncertainty.", "Tokens [T1] + Compute [T2] + Storage [T3] + APIs [T4] + Training [T5]"),
        ],
    ),
]


def gh(*args, input_text=None):
    result = subprocess.run(["gh", *args], input=input_text, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"gh {' '.join(args[:4])} failed: {result.stderr.strip()}")
    return json.loads(result.stdout) if result.stdout.strip() else None


def get_issues():
    return gh("api", f"repos/{REPO}/issues?state=all&per_page=100")


def ensure_issue(title, body, labels, existing):
    if title in existing:
        return existing[title]
    payload = {"title": title, "body": body, "labels": labels}
    issue = gh("api", "-X", "POST", f"repos/{REPO}/issues", "--input", "-", input_text=json.dumps(payload))
    existing[title] = issue
    print(f"Created #{issue['number']}: {title}", flush=True)
    time.sleep(0.7)
    return issue


def ensure_subissue(parent, child):
    children = gh("api", f"repos/{REPO}/issues/{parent['number']}/sub_issues?per_page=100")
    if any(item["id"] == child["id"] for item in children):
        return
    gh("api", "-X", "POST", f"repos/{REPO}/issues/{parent['number']}/sub_issues", "-f", f"sub_issue_id={child['id']}")
    print(f"Linked #{child['number']} under #{parent['number']}", flush=True)
    time.sleep(0.7)


def main():
    labels = [
        ("research", "Evidence gathering and comparison", "1D76DB"),
        ("workstream", "Parent research workstream", "5319E7"),
        ("optional", "Optional builder component", "C5DEF5"),
    ]
    for name, description, color in labels:
        try:
            gh("api", f"repos/{REPO}/labels/{name}")
        except RuntimeError:
            gh("api", "-X", "POST", f"repos/{REPO}/labels", "-f", f"name={name}", "-f", f"description={description}", "-f", f"color={color}")
    existing = {issue["title"]: issue for issue in get_issues() if "pull_request" not in issue}
    for code, name, owner, components in WORKSTREAMS:
        optional = " (Optional)" in name
        title = f"{code}: {name}"
        component_lines = "\n".join(f"- {item[0]}" for item in components)
        parent_body = (
            f"## Goal\nResearch the {name} choices for a PCPartPicker-inspired AI system builder. "
            f"Workstream owner: @{owner}.\n\n## Component research\n{component_lines}\n\n"
            "## Done when\nEach component has a cited decision record, normalized comparison fields, "
            "compatibility rules (hard, warning, unknown), and open questions. Review cross-workstream "
            "assumptions with affected owners. See [research method](../blob/main/docs/RESEARCH_METHOD.md) "
            "and [dependency map](../blob/main/docs/DEPENDENCIES.md).\n"
        )
        parent = ensure_issue(title, parent_body, ["research", "workstream"] + (["optional"] if optional else []), existing)
        for component, prompt, dependencies in components:
            child_title = f"{code}: {component}"
            child_body = (
                f"## Research task\n{prompt}\n\n**Inputs / dependencies:** {dependencies}.\n"
                f"**Workstream owner:** @{owner}.\n\n"
                "## Deliverable\nDocument candidate options, normalized comparison fields, compatibility "
                "rules (hard, warning, unknown), tradeoffs, primary sources with access dates and versions, "
                "and unresolved questions. Numeric claims need their conditions and units.\n\n"
                "## Acceptance criteria\n- [ ] Candidate set and fields are documented\n"
                "- [ ] Compatibility constraints and cross-workstream handoffs are explicit\n"
                "- [ ] Claims have primary-source evidence and dates\n"
                "- [ ] Unknowns and follow-ups are recorded\n"
            )
            child = ensure_issue(child_title, child_body, ["research"] + (["optional"] if optional else []), existing)
            ensure_subissue(parent, child)


if __name__ == "__main__":
    main()
