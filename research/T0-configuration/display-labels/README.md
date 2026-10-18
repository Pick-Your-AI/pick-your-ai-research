# Component display labels proposal

Refs research #40 and [website #18](https://github.com/Pick-Your-AI/pickyour.ai/issues/18). Status: proposed; #40 owner agreement and consumer acceptance remain pending.

[v0.1.0.json](v0.1.0.json) supplies distinct English display names for all 29 canonical kinds, including the four pairs that share research issues. It retains the website's existing kind names at the immutable `source_url` recorded in the file, inspected 2026-10-18, to avoid an incidental naming change while moving the data to shared ownership. The names are project presentation text, not researched vendor claims.

The sidecar is outside frozen v1. Its version is independent of `registry_version`; `registry_sha256` binds the exact registry bytes. Keys are canonical kind identifiers. Values are display text only: never persist labels as IDs, derive capability/activation from a label, or replace the registry with this file. Tier titles, summaries, slugs and grammatical helpers remain consumer presentation code; they are not hidden in the kind-label map.

## Consumer handoff

1. #40 owners @tynamite/@zwright8 review the label set and sidecar/version policy; affected consumers confirm their naming needs. A passing coverage test does not establish this acceptance.
2. Once accepted, publish a new accepted sidecar revision with its decision receipt and pin its Git commit and SHA-256 in the consuming repository. Keep the proposal revision available as history. No runtime download URL or publication service is implied.
3. A consumer importing the accepted artifact checks `registry_version`, `registry_sha256`, exact kind-key coverage, locale and sidecar version before replacing its local kind-label table. Its existing application tests still run. Unknown locale/version or registry mismatch must not silently substitute a different naming contract.
4. Record separate receiving receipts for website, Android and Apple. Website #18 still needs the actual import and removal of the duplicated `KIND_LABELS` table. A proposal merge does not satisfy that criterion. Consumer-only tier labels/helpers can remain even if the kind table moves to the sidecar; the website owner decides module layout.

Additions/removals of canonical kinds need a new registry contract first. Corrections or translations use a new sidecar revision; an accepted revision must not be silently overwritten. This proposed English artifact makes no locale fallback choice.

Run `python -m unittest discover -s tests -p test_component_display_labels.py -v`. The test checks registry identity, complete/distinct labels and the explicit proposal boundary. It does not certify owner acceptance or a client integration.
