# MR-09: Validate GPU sizing against pinned runtime measurements

Issue: [#61](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61). Owner: @Mattycodes69. Status: protocol only; validation has not been completed. Readiness: Ready.

## Question
Where do planning estimates fail under real runtime conditions?

## Starting evidence
[technical-feasibility.md](technical-feasibility.md). This note is not a new canonical component catalog or a completed measurement.

## Protocol and acceptance
- [ ] Design dense and MoE measurement matrix
- [ ] Vary context cache precision and concurrency
- [ ] Measure peak allocated and reserved memory
- [ ] Report error bounds and failures without universal fit claims
- [ ] Record exact source/version, conditions, failures and confidence.
- [ ] Obtain affected-owner review and accepted handoff.

## Next action
Execute the documented validation protocol; initial research findings are starting inputs, not completed validation.

## Result
No completed independent validation is claimed. No raw customer data, benchmark artifact or paid API output was collected. Consumers: #7, #10, #11.
