# Goose synthetic fixtures

`goose_fixtures.py` creates small SQLite databases with the actual audited Goose
schema-17 column names and synthetic metadata. Sources are pinned in
[the integration guide](../references/goose.md). No user installation, logs,
credentials, provider account, remote server or model request is needed.

`invocation()` writes one native usage row, cumulative session counters and
(optional) matching assistant metadata. It is a fixture builder, not a Goose
exporter or a claim that HTTP retries are one-to-one with these rows. The private
marker `SYNTHETIC_PROMPT_MUST_NOT_BE_COLLECTED` must never enter generated ledger
outputs. Token/category/cost mutations deliberately create invalid or incomplete
records to exercise exclusion evidence. Legacy JSONL begins with native-shaped
session metadata; later conversation content is not read by the native collector.

The hypothetical rates are $2 input, $10 output, $0.20 cache-read, $2.50 5-minute
cache-write and $4 1-hour cache-write per million tokens. They are arithmetic
fixtures, not current marketed model rates or money charged. The first invocation
has 1,000 inclusive input, 50 output, 200 cache-read and 100 cache-write tokens:
1,050 total and a $0.00219 API-equivalent estimate. A second record with 1,500 input
and 100 output yields cumulative 2,650 tokens and $0.00588 at those test rates.
Native cost evidence is intentionally different to prove it does not override
the snapshot estimate.

Run `python -m unittest discover -s tests -p 'test_goose*.py' -v` from the repository
root. E2E cases run the actual scanner pipeline and all three native ledger-store
backends, not mocks of those APIs. WAL tests use SQLite writers, not live model
calls. Windows/macOS/Linux path rules are tested with injected environment data;
the CI matrix also exercises the collector on those real OS runners. A Windows
symlink test may be skipped because creating symlinks needs OS privileges.

On Windows, the existing scoped-report end-to-end checks need IANA timezone
data: run `python -m pip install tzdata` in the test environment first. Native
collection itself has no additional dependency. Fixture SQLite connections are
explicitly closed before temporary-directory cleanup, including concurrent
writers and assertion/error paths.
