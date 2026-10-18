# Bounded raw-text token estimation study

Issue: [#7](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/7).
Measured 2026-10-18 UTC (October 17, 2026, America/New_York).
Status: original local software observations for independent review.

## Question and scope

Can an uncalibrated four-characters-per-token estimate supply a safe input-budget
verdict for the pinned Qwen3 tokenizer? This study compares
`ceil(Unicode code points / 4)` with that encoder's actual output length.

The [14 project-authored synthetic fixtures](../../tests/fixtures/token-count-panel.json)
cover English, code, JSON text, Chinese, Arabic, emoji sequences, composed and
decomposed accents, whitespace, digits, and a base string before/after adding
synthetic memory text. They are a convenience/adversarial panel, not a sampled
user population. No confidence interval, quantile estimate, population accuracy,
unseen-input error bound or cross-tokenizer transfer is established.

The observations measure **raw text only**. They exclude chat-template/role
markers, tool serialization, media processing, hidden provider tokens, output and
thinking reservations, runtime admission, KV memory, latency and quality. JSON
here is text in a fixture, not an executed tool call. The memory example is text
assembly, not a retrieval experiment.

## Identity and method

- Model repository revision: `Qwen/Qwen3-8B@b968826d9c46dd6066d109eabc6255188de91218`.
- Tokenizer bytes: [external manifest](../../evidence/t1-qwen3-8b-tokenizer.json),
  SHA-256 `aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4`.
- Encoder: `tokenizers==0.23.3`; input parsing: `pydantic==2.12.5`;
  original execution: Python 3.12.12. The [runner](../../scripts/token_count_experiment.py)
  pins its dependencies using inline metadata.
- Disable truncation and padding, and call `encode(..., add_special_tokens=False)`.
  This disables postprocessor-added tokens; it does not claim to implement a
  serving chat template or change the tokenizer's vocabulary.
- Measure the complete fixture string. Count Python Unicode code points and UTF-8
  bytes separately. Neither is a user-perceived grapheme count or JavaScript
  UTF-16 length.
- Signed residual is `observed_tokens - ceil_codepoints_div_4`: positive means
  underestimation. The [observation file](token-count-observations.json) binds
  the fixture bytes and tokenizer hash and records the environment.

These are local software measurements on synthetic inputs, offered for independent
review/reproduction. The heuristic values are estimates. They do not award a
verified grade to vendor capabilities or qualify a ResourceEstimate or
QualityEvaluationRun.

## Observed results

| Fixture | Code points | UTF-8 bytes | Observed tokens | Estimate | Signed residual |
| --- | ---: | ---: | ---: | ---: | ---: |
| empty | 0 | 0 | 0 | 0 | 0 |
| ascii_greeting | 12 | 12 | 3 | 3 | 0 |
| english_prose | 139 | 139 | 21 | 35 | -14 |
| python_code | 85 | 85 | 21 | 22 | -1 |
| tool_json | 111 | 111 | 26 | 28 | -2 |
| cjk_repeated | 114 | 342 | 66 | 29 | +37 |
| arabic_prose | 192 | 354 | 75 | 48 | +27 |
| emoji_sequences | 156 | 456 | 216 | 39 | +177 |
| composed_accents | 180 | 220 | 62 | 45 | +17 |
| decomposed_accents | 220 | 260 | 62 | 55 | +7 |
| spaces | 128 | 128 | 1 | 32 | -31 |
| digits | 160 | 160 | 160 | 40 | +120 |
| base_input | 83 | 83 | 15 | 21 | -6 |
| input_with_memory | 583 | 583 | 101 | 146 | -45 |

The residuals span **-45 to +177 tokens in this panel only**. Their extrema are not
a safety envelope for future inputs. Composed/decomposed examples produce the
same token count despite different code-point/byte lengths. Adding the synthetic
memory changes the complete raw-text count from 15 to 101 tokens; the original
count cannot be reused after that edit.

For the **synthetic 32-token raw-text budget** recorded in the fixture file,
`cjk_repeated` has estimate 29 but observed count 66: a false fit from the point
estimate. `english_prose` has estimate 35 but observed count 21: the opposite
misclassification. This budget is an illustrative experiment input, not a Qwen
model limit, published provider cap or measured admission result.

## Decision for the existing context record

Retain #7's existing recommendation: use a matching request counter or a fully
specified local tokenizer/template on the assembled request. A four-code-point
ratio may label a planning estimate, but its unknown error bound cannot prove
fit. This experiment adds evidence for that restriction; it does not invent a
replacement ratio, confidence margin or universal bound.

Exact local text counts still require the matching serving serialization.
Provider-specific overhead, future tool results, output reservation and non-text
processing need their own evidence. #10 owns resource/KV methodology; #16/#28 own
assembly and content preservation; #39 owns billing-count interpretation; #40
retains any contract/rule change. Their existing handoff and independent-review
gates remain open.

## Reproduce without model weights

Download only the pinned tokenizer, outside the repository:

```bash
curl --fail --location \
  'https://huggingface.co/Qwen/Qwen3-8B/resolve/b968826d9c46dd6066d109eabc6255188de91218/tokenizer.json' \
  --output /tmp/qwen3-tokenizer.json
uv run --python 3.12 scripts/token_count_experiment.py \
  /tmp/qwen3-tokenizer.json \
  tests/fixtures/token-count-panel.json \
  /tmp/token-count-observations.json
```

The runner checks the artifact hash and unique fixture IDs before writing output.
Compare observation rows and artifact/fixture hashes with the committed record;
the execution timestamp may differ. Keep the 11,422,654-byte tokenizer outside
Git. No model weights, model inference, GPU, paid API or personal data is required.
Dependency installation and the explicit download use the network; the runner
does no network I/O after its environment is installed.

## Sources and validation limits

- [Pinned tokenizer](https://huggingface.co/Qwen/Qwen3-8B/blob/b968826d9c46dd6066d109eabc6255188de91218/tokenizer.json)
  and [publisher LICENSE](https://huggingface.co/Qwen/Qwen3-8B/blob/b968826d9c46dd6066d109eabc6255188de91218/LICENSE),
  accessed 2026-10-18 UTC. LICENSE contains Apache License 2.0. Only metadata and
  project-authored fixtures/results are submitted; upstream tokenizer bytes are
  not redistributed. The manifest records the source/use boundary.
- [Hugging Face Tokenizers quicktour](https://huggingface.co/docs/tokenizers/quicktour),
  accessed 2026-10-18 UTC, describes loading an artifact and obtaining encoded IDs.
  The executed, pinned library and bytes determine the counts here; mutable docs
  do not pin an experimental result.

CI checks fixture/artifact bindings and local arithmetic, in addition to the
repository workflow. It does not download the tokenizer or independently recompute
the encoded counts. Independent evidence review must rerun the pinned encoder,
inspect the fixture scope and retain the limitations above. The experiment is
a partial contribution; it supplies no missing owner acceptance or issue closure.
