# Browser observations — 2026-10-16

Author: automated research session using Docker Playwright, anonymous public browsing. No credentials or paid services used. These observations are qualitative, not archived third-party datasets or benchmark measurements.

| Source | Action | Observed result | Boundary |
| --- | --- | --- | --- |
| BenchLM | Open homepage and inspect controls | Model search, filters, score ordering, pricing/tool navigation rendered | No account-gated data calls or performance tests |
| Harness Bench | Open homepage and inspect categories | Task-family controls, methodology and paper/repository links rendered | No benchmark run |
| llmfit.org | Open seed page | Installation and CLI/API documentation rendered; no interactive controls | Upstream executable not installed or tested; operator identity unresolved |
| Local AI planner | Inspect hardware/context/runtime/cache controls; select custom GPU | Controls and curated GPU options rendered | Attempted manual VRAM fill failed because field was hidden in the UI; no output-accuracy verification claimed |
| Flocci Ask | Submit generic request for private local laptop inference | Explained recommendation cards returned for local-model tools | Response claims about each recommended tool were not independently verified |
| Flocci Stack Builder | Open `/stack` | Stack-request form and sign-in/free-allowance gate displayed | No stack generated; no complete compatibility claim verified |
| PCPartPicker | Open `/list/` | Redirected to login; web retrieval separately returned 403 | Current list/save/share behavior unverified |
| GitHub Project #2 | Anonymous browser visit | Private-project page unavailable | Authenticated API readback used for field/view/relationship verification |

Flocci's static index and rendered navigation gave different catalog totals; do not use those counts as verified adoption. Harness paper and website suite sizes also conflict; see benchmark validation.
