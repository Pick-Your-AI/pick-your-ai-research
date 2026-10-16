# MR-03: Test direct stack-builder substitutes

Issue: [#66](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/66). Owner: @CompleteDotTech. Status: one browser scenario completed; analysis in review, broader validation incomplete. Readiness: Ready.

## Question
Do Flocci and other guided builders already satisfy the proposed MVP?

## Starting evidence
[competitors.json](competitors.json). This note is not a new canonical component catalog or a completed measurement.

## Protocol and acceptance
- [ ] Run a common public non-sensitive scenario
- [ ] Check constraint handling and explanation quality
- [ ] Inspect saved or exported configuration claims
- [ ] Record counterexamples and pivot recommendation
- [ ] Record exact source/version, conditions, failures and confidence.
- [ ] Obtain affected-owner review and accepted handoff.

## Next action
Execute the documented validation protocol; initial research findings are starting inputs, not completed validation.

## Result
One generated workflow was observed, as described below; no deployed-system validation is claimed. No raw customer data, benchmark artifact or paid API output was collected. Consumers: #2, #40, #42.

## Initial result
A completed free Stack Builder test returned an ordered local PDF RAG workflow for Windows, 16 GB RAM and no GPU. It acknowledged memory/latency uncertainty and suggested reproducibility steps. The visible result named Docling, txtai, Chroma, Ollama, Gemma and Open WebUI. This verifies generated workflow advice, not that the combination runs, preserves privacy or produces an executable export.

Remaining: test contradictory constraints, verify actual deployment and export behavior, compare a second substitute, and obtain owner review.
