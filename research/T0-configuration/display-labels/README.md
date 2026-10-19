# Component display labels

Refs research #40 and [website #18](https://github.com/Pick-Your-AI/pick-your-ai-website/issues/18).

## Accepted English sidecar: 1.0.0

[v1.0.0.json](v1.0.0.json) is the English presentation sidecar selected by the
[2026-10-19 central engineering decision](../component-schema-compatibility.md#display-label-sidecar-decision--2026-10-19).
Its 29 names exactly preserve the original proposal and the website's existing
names at the immutable `source_url` in the accepted file. They include distinct
names for the four pairs that share research issues. These are project
presentation names, not researched vendor claims or compatibility policy.

The artifact stays outside frozen `contracts/v1/`. `sidecar_version` identifies
this presentation release; it is independent of `registry_version` and does not
release a successor schema or API. `registry_sha256` binds the exact registry
bytes. Keys remain canonical identifiers. Never persist labels as IDs, infer
capability or activation from a name, or replace the registry with this file.
Tier titles, summaries, slugs and grammatical helpers remain consumer code.

## Consumer handoff

1. Pin the accepted artifact's exact Git commit, path and SHA-256 in the receiving repository. Import its bytes unchanged; no runtime download or publication service is required or implied.
2. Check `status: accepted`, `registry_version`, the SHA-256 of the actual registry bytes, exact kind-key coverage, nonempty/distinct text, locale `en` and supported `sidecar_version: 1.0.0`. Reject an unsupported locale/version, a proposal or a registry mismatch; do not silently choose a fallback contract.
3. Keep the verification in normal client checks and run the existing application tests. Website #18 requires an actual import and removal of its duplicated kind-label table and `labels.ts` module. Consumer-only tier labels/helpers can move to a separate module.
4. Record actual receiving receipts separately for website, Android and Apple. The central decision accepts the shared artifact; it does not claim any client has imported, tested or delivered it.

Changes to the canonical kind set require a registry contract first. Corrections
or translations require a new immutable sidecar revision and consumer review;
never silently overwrite an accepted revision. This English release establishes
no locale fallback and changes none of the frozen versioning or identifier rules.

## Preserved proposal

[v0.1.0.json](v0.1.0.json) remains byte-for-byte the 2026-10-18 proposal, including
its `status: proposed`, independent version and original source URL. It is not
retroactively accepted. The new decision and release above are separately dated.

Run `python -m unittest discover -s tests -p test_component_display_labels.py -v`.
These structural checks verify both registry bindings, complete/distinct names,
version/status boundaries and unchanged names. They do not supply an independent
review, client integration or vendor evidence.
