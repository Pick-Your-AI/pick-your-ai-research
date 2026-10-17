# Apple/iOS delivery tracking

[Project #5](https://github.com/orgs/Pick-Your-AI/projects/5) · [Program #163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163) · [Delivery plan](APPLE_DELIVERY_PLAN.md)

Published and read back on 2026-10-16. This index identifies planning issues, not completed implementation. GitHub is authoritative for current status, assignees and dependencies.

Verified: **129 issues: 1 program, 18 epics and 110 features**, 128 native parent-child links, 213 native prerequisite links, 19 Project fields and nine views. All issues were open, Backlog and unassigned at publication. Readiness distinguishes missing owners, prerequisite inputs and conditional scope decisions; dates and estimates were not invented.

Feature issues carry implementation checklists, outcome acceptance, task-specific verification, research sources and Android/website coordination links. Apple tasks in shared workstreams own client requirements, adapters and acceptance. Canonical shared service/data implementation stays with its linked existing issue. Fifteen native cross-project prerequisites identify required shared outputs. Existing issue parents, owners and metadata were not changed.

## Issue index

| Coordinate | Level | Issue |
| --- | --- | --- |
| Program | Program | [#163 — End-to-end Apple/iOS delivery](https://github.com/Pick-Your-AI/pickyour.ai/issues/163) |
| 01 | Epic | [#164 — Product scope and decisions](https://github.com/Pick-Your-AI/pickyour.ai/issues/164) |
| 01.01 | Feature | [#182 — Target users and primary iPhone and iPad journeys](https://github.com/Pick-Your-AI/pickyour.ai/issues/182) |
| 01.02 | Feature | [#183 — MVP scope and phased capabilities](https://github.com/Pick-Your-AI/pickyour.ai/issues/183) |
| 01.03 | Feature | [#184 — Apple platform scope, technology and repository structure](https://github.com/Pick-Your-AI/pickyour.ai/issues/184) |
| 01.04 | Feature | [#185 — Backend architecture and hosting](https://github.com/Pick-Your-AI/pickyour.ai/issues/185) |
| 01.05 | Feature | [#186 — Accounts and monetization decisions](https://github.com/Pick-Your-AI/pickyour.ai/issues/186) |
| 01.06 | Feature | [#187 — Acceptance criteria, ownership and release gates](https://github.com/Pick-Your-AI/pickyour.ai/issues/187) |
| 02 | Epic | [#165 — Apple application foundation](https://github.com/Pick-Your-AI/pickyour.ai/issues/165) |
| 02.01 | Feature | [#188 — Xcode toolchain, dependencies and modules](https://github.com/Pick-Your-AI/pickyour.ai/issues/188) |
| 02.02 | Feature | [#189 — Preview, staging and production environments](https://github.com/Pick-Your-AI/pickyour.ai/issues/189) |
| 02.03 | Feature | [#190 — Navigation, lifecycle and state restoration](https://github.com/Pick-Your-AI/pickyour.ai/issues/190) |
| 02.04 | Feature | [#191 — UI, domain and data boundaries](https://github.com/Pick-Your-AI/pickyour.ai/issues/191) |
| 02.05 | Feature | [#192 — macOS continuous integration and required checks](https://github.com/Pick-Your-AI/pickyour.ai/issues/192) |
| 02.06 | Feature | [#193 — Clearly identified synthetic fixtures](https://github.com/Pick-Your-AI/pickyour.ai/issues/193) |
| 03 | Epic | [#166 — Shared contracts and mobile conformance](https://github.com/Pick-Your-AI/pickyour.ai/issues/166) |
| 03.01 | Feature | [#194 — Adopt versioned contracts and generate models](https://github.com/Pick-Your-AI/pickyour.ai/issues/194) |
| 03.02 | Feature | [#195 — Separate incomplete drafts from saved snapshots](https://github.com/Pick-Your-AI/pickyour.ai/issues/195) |
| 03.03 | Feature | [#196 — Define required versioned API extensions](https://github.com/Pick-Your-AI/pickyour.ai/issues/196) |
| 03.04 | Feature | [#197 — Model component placement and relationships](https://github.com/Pick-Your-AI/pickyour.ai/issues/197) |
| 03.05 | Feature | [#198 — Define evidence, unknowns and rule semantics](https://github.com/Pick-Your-AI/pickyour.ai/issues/198) |
| 03.06 | Feature | [#199 — Cross-client conformance and migration fixtures](https://github.com/Pick-Your-AI/pickyour.ai/issues/199) |
| 04 | Epic | [#167 — Research-to-production catalog pipeline](https://github.com/Pick-Your-AI/pickyour.ai/issues/167) |
| 04.01 | Feature | [#200 — Source access, display and redistribution rights](https://github.com/Pick-Your-AI/pickyour.ai/issues/200) |
| 04.02 | Feature | [#201 — Normalize and validate component facts](https://github.com/Pick-Your-AI/pickyour.ai/issues/201) |
| 04.03 | Feature | [#202 — Evidence review and production approval](https://github.com/Pick-Your-AI/pickyour.ai/issues/202) |
| 04.04 | Feature | [#203 — Publish immutable catalog and rule releases](https://github.com/Pick-Your-AI/pickyour.ai/issues/203) |
| 04.05 | Feature | [#204 — Freshness, corrections and retractions](https://github.com/Pick-Your-AI/pickyour.ai/issues/204) |
| 04.06 | Feature | [#205 — Publish the first complete supported real-data path](https://github.com/Pick-Your-AI/pickyour.ai/issues/205) |
| 05 | Epic | [#168 — Shared application services](https://github.com/Pick-Your-AI/pickyour.ai/issues/168) |
| 05.01 | Feature | [#206 — API foundation, database and migrations](https://github.com/Pick-Your-AI/pickyour.ai/issues/206) |
| 05.02 | Feature | [#207 — Catalog discovery, search and delivery](https://github.com/Pick-Your-AI/pickyour.ai/issues/207) |
| 05.03 | Feature | [#208 — Build creation, revisions, history and deletion](https://github.com/Pick-Your-AI/pickyour.ai/issues/208) |
| 05.04 | Feature | [#209 — Compatibility evaluation and pricing services](https://github.com/Pick-Your-AI/pickyour.ai/issues/209) |
| 05.05 | Feature | [#210 — Share creation, access and revocation](https://github.com/Pick-Your-AI/pickyour.ai/issues/210) |
| 05.06 | Feature | [#211 — Resource estimates and quality evidence](https://github.com/Pick-Your-AI/pickyour.ai/issues/211) |
| 05.07 | Feature | [#212 — Authorization and optional account authentication](https://github.com/Pick-Your-AI/pickyour.ai/issues/212) |
| 05.08 | Feature | [#213 — Limits, auditability, secrets and recovery](https://github.com/Pick-Your-AI/pickyour.ai/issues/213) |
| 05.09 | Feature | [#214 — Integration with the existing website](https://github.com/Pick-Your-AI/pickyour.ai/issues/214) |
| 06 | Epic | [#169 — Mobile experience and design system](https://github.com/Pick-Your-AI/pickyour.ai/issues/169) |
| 06.01 | Feature | [#215 — Information architecture and interaction prototypes](https://github.com/Pick-Your-AI/pickyour.ai/issues/215) |
| 06.02 | Feature | [#216 — Accessible components and design tokens](https://github.com/Pick-Your-AI/pickyour.ai/issues/216) |
| 06.03 | Feature | [#217 — Adaptive iPhone and iPad layouts](https://github.com/Pick-Your-AI/pickyour.ai/issues/217) |
| 06.04 | Feature | [#218 — Builder guidance and understandable status labels](https://github.com/Pick-Your-AI/pickyour.ai/issues/218) |
| 06.05 | Feature | [#219 — Loading, empty, offline and failure states](https://github.com/Pick-Your-AI/pickyour.ai/issues/219) |
| 06.06 | Feature | [#220 — Themes, localization, units and presentation](https://github.com/Pick-Your-AI/pickyour.ai/issues/220) |
| 07 | Epic | [#170 — Component discovery and comparison](https://github.com/Pick-Your-AI/pickyour.ai/issues/170) |
| 07.01 | Feature | [#221 — Browse, search, filter and sort the catalog](https://github.com/Pick-Your-AI/pickyour.ai/issues/221) |
| 07.02 | Feature | [#222 — Compatibility-aware component picker](https://github.com/Pick-Your-AI/pickyour.ai/issues/222) |
| 07.03 | Feature | [#223 — Component details, conditions and evidence](https://github.com/Pick-Your-AI/pickyour.ai/issues/223) |
| 07.04 | Feature | [#224 — Side-by-side component comparison](https://github.com/Pick-Your-AI/pickyour.ai/issues/224) |
| 07.05 | Feature | [#225 — Select components from search and deep links](https://github.com/Pick-Your-AI/pickyour.ai/issues/225) |
| 08 | Epic | [#171 — AI stack builder](https://github.com/Pick-Your-AI/pickyour.ai/issues/171) |
| 08.01 | Feature | [#226 — Workload, constraints and deployment inputs](https://github.com/Pick-Your-AI/pickyour.ai/issues/226) |
| 08.02 | Feature | [#227 — Model and infrastructure selection](https://github.com/Pick-Your-AI/pickyour.ai/issues/227) |
| 08.03 | Feature | [#228 — Enable and disable optional tiers](https://github.com/Pick-Your-AI/pickyour.ai/issues/228) |
| 08.04 | Feature | [#229 — Edit component settings and build objectives](https://github.com/Pick-Your-AI/pickyour.ai/issues/229) |
| 08.05 | Feature | [#230 — Persistent summary and suggested next steps](https://github.com/Pick-Your-AI/pickyour.ai/issues/230) |
| 08.06 | Feature | [#231 — Undo, autosave and revision restoration](https://github.com/Pick-Your-AI/pickyour.ai/issues/231) |
| 09 | Epic | [#172 — Compatibility and capacity](https://github.com/Pick-Your-AI/pickyour.ai/issues/172) |
| 09.01 | Feature | [#232 — Integrate the governed evaluator](https://github.com/Pick-Your-AI/pickyour.ai/issues/232) |
| 09.02 | Feature | [#233 — Recheck affected components after changes](https://github.com/Pick-Your-AI/pickyour.ai/issues/233) |
| 09.03 | Feature | [#234 — Explain findings and possible fixes](https://github.com/Pick-Your-AI/pickyour.ai/issues/234) |
| 09.04 | Feature | [#235 — Consume qualified capacity estimates](https://github.com/Pick-Your-AI/pickyour.ai/issues/235) |
| 09.05 | Feature | [#236 — Suggest alternatives with stated tradeoffs](https://github.com/Pick-Your-AI/pickyour.ai/issues/236) |
| 09.06 | Feature | [#237 — Handle stale and out-of-order results](https://github.com/Pick-Your-AI/pickyour.ai/issues/237) |
| 10 | Epic | [#173 — Cost estimation](https://github.com/Pick-Your-AI/pickyour.ai/issues/173) |
| 10.01 | Feature | [#238 — Select applicable dated rates](https://github.com/Pick-Your-AI/pickyour.ai/issues/238) |
| 10.02 | Feature | [#239 — Calculate costs from explicit usage scenarios](https://github.com/Pick-Your-AI/pickyour.ai/issues/239) |
| 10.03 | Feature | [#240 — Show missing costs, coverage and uncertainty](https://github.com/Pick-Your-AI/pickyour.ai/issues/240) |
| 10.04 | Feature | [#241 — Compare scenarios and preserve price provenance](https://github.com/Pick-Your-AI/pickyour.ai/issues/241) |
| 11 | Epic | [#174 — Saved builds, comparison and sharing](https://github.com/Pick-Your-AI/pickyour.ai/issues/174) |
| 11.01 | Feature | [#242 — Local build library](https://github.com/Pick-Your-AI/pickyour.ai/issues/242) |
| 11.02 | Feature | [#243 — Compare complete builds and revisions](https://github.com/Pick-Your-AI/pickyour.ai/issues/243) |
| 11.03 | Feature | [#244 — Safe import and export](https://github.com/Pick-Your-AI/pickyour.ai/issues/244) |
| 11.04 | Feature | [#245 — Read-only shared builds with pinned evidence](https://github.com/Pick-Your-AI/pickyour.ai/issues/245) |
| 11.05 | Feature | [#246 — Fork builds and optional cross-device continuity](https://github.com/Pick-Your-AI/pickyour.ai/issues/246) |
| 11.06 | Feature | [#247 — Universal Links, associated domains and browser fallback](https://github.com/Pick-Your-AI/pickyour.ai/issues/247) |
| 12 | Epic | [#175 — Offline storage and synchronization](https://github.com/Pick-Your-AI/pickyour.ai/issues/175) |
| 12.01 | Feature | [#248 — Durable local database and migrations](https://github.com/Pick-Your-AI/pickyour.ai/issues/248) |
| 12.02 | Feature | [#249 — Cached catalogs and offline draft editing](https://github.com/Pick-Your-AI/pickyour.ai/issues/249) |
| 12.03 | Feature | [#250 — Atomic refresh and background scheduling](https://github.com/Pick-Your-AI/pickyour.ai/issues/250) |
| 12.04 | Feature | [#251 — Queued writes and retry reconciliation](https://github.com/Pick-Your-AI/pickyour.ai/issues/251) |
| 12.05 | Feature | [#252 — Conflict resolution without lost edits](https://github.com/Pick-Your-AI/pickyour.ai/issues/252) |
| 12.06 | Feature | [#253 — Logout, deletion and unavailable-version handling](https://github.com/Pick-Your-AI/pickyour.ai/issues/253) |
| 13 | Epic | [#176 — Optional tiers and operational capabilities](https://github.com/Pick-Your-AI/pickyour.ai/issues/176) |
| 13.01 | Feature | [#254 — Knowledge and retrieval configuration — T3](https://github.com/Pick-Your-AI/pickyour.ai/issues/254) |
| 13.02 | Feature | [#255 — Agents, tools, MCP and memory — T4](https://github.com/Pick-Your-AI/pickyour.ai/issues/255) |
| 13.03 | Feature | [#256 — Training and fine-tuned models — T5](https://github.com/Pick-Your-AI/pickyour.ai/issues/256) |
| 13.04 | Feature | [#257 — Guardrails and evaluation guidance — T6](https://github.com/Pick-Your-AI/pickyour.ai/issues/257) |
| 13.05 | Feature | [#258 — Deployment plans and monitoring choices — T6](https://github.com/Pick-Your-AI/pickyour.ai/issues/258) |
| 13.06 | Feature | [#259 — Validate supported combinations across tiers](https://github.com/Pick-Your-AI/pickyour.ai/issues/259) |
| 14 | Epic | [#177 — Privacy, security and trust](https://github.com/Pick-Your-AI/pickyour.ai/issues/177) |
| 14.01 | Feature | [#260 — Data inventory and threat model](https://github.com/Pick-Your-AI/pickyour.ai/issues/260) |
| 14.02 | Feature | [#261 — Keychain, data protection and secure networking](https://github.com/Pick-Your-AI/pickyour.ai/issues/261) |
| 14.03 | Feature | [#262 — Account and associated-data lifecycle, if included](https://github.com/Pick-Your-AI/pickyour.ai/issues/262) |
| 14.04 | Feature | [#263 — Privacy disclosures and third-party SDK controls](https://github.com/Pick-Your-AI/pickyour.ai/issues/263) |
| 14.05 | Feature | [#264 — Adversarial testing of sharing, imports and APIs](https://github.com/Pick-Your-AI/pickyour.ai/issues/264) |
| 14.06 | Feature | [#265 — Dependency security and vulnerability response](https://github.com/Pick-Your-AI/pickyour.ai/issues/265) |
| 15 | Epic | [#178 — Quality and performance](https://github.com/Pick-Your-AI/pickyour.ai/issues/178) |
| 15.01 | Feature | [#266 — Contract and domain regression tests](https://github.com/Pick-Your-AI/pickyour.ai/issues/266) |
| 15.02 | Feature | [#267 — Apple UI and accessibility tests](https://github.com/Pick-Your-AI/pickyour.ai/issues/267) |
| 15.03 | Feature | [#268 — Network failure and recovery tests](https://github.com/Pick-Your-AI/pickyour.ai/issues/268) |
| 15.04 | Feature | [#269 — Device, OS and lifecycle test matrix](https://github.com/Pick-Your-AI/pickyour.ai/issues/269) |
| 15.05 | Feature | [#270 — Apple, Android, web and backend conformance tests](https://github.com/Pick-Your-AI/pickyour.ai/issues/270) |
| 15.06 | Feature | [#271 — Measured startup, rendering and resource budgets](https://github.com/Pick-Your-AI/pickyour.ai/issues/271) |
| 15.07 | Feature | [#272 — Security and release-build regression tests](https://github.com/Pick-Your-AI/pickyour.ai/issues/272) |
| 15.08 | Feature | [#273 — Authorized user validation and acceptance](https://github.com/Pick-Your-AI/pickyour.ai/issues/273) |
| 16 | Epic | [#179 — TestFlight, App Store delivery and launch](https://github.com/Pick-Your-AI/pickyour.ai/issues/179) |
| 16.01 | Feature | [#274 — Apple Developer team and App Store Connect identity](https://github.com/Pick-Your-AI/pickyour.ai/issues/274) |
| 16.02 | Feature | [#275 — Platform and store-policy requirements](https://github.com/Pick-Your-AI/pickyour.ai/issues/275) |
| 16.03 | Feature | [#276 — Signing, provisioning, entitlements and key management](https://github.com/Pick-Your-AI/pickyour.ai/issues/276) |
| 16.04 | Feature | [#277 — Internal and external TestFlight testing](https://github.com/Pick-Your-AI/pickyour.ai/issues/277) |
| 16.05 | Feature | [#278 — App Store listing, screenshots and privacy declarations](https://github.com/Pick-Your-AI/pickyour.ai/issues/278) |
| 16.06 | Feature | [#279 — Launch readiness and controlled rollout](https://github.com/Pick-Your-AI/pickyour.ai/issues/279) |
| 16.07 | Feature | [#280 — Verify the installed production release](https://github.com/Pick-Your-AI/pickyour.ai/issues/280) |
| 17 | Epic | [#180 — Product and data operations](https://github.com/Pick-Your-AI/pickyour.ai/issues/180) |
| 17.01 | Feature | [#281 — Application and service monitoring](https://github.com/Pick-Your-AI/pickyour.ai/issues/281) |
| 17.02 | Feature | [#282 — Incident response and restore drills](https://github.com/Pick-Your-AI/pickyour.ai/issues/282) |
| 17.03 | Feature | [#283 — Catalog, evidence and pricing maintenance](https://github.com/Pick-Your-AI/pickyour.ai/issues/283) |
| 17.04 | Feature | [#284 — Support, corrections and contribution workflow](https://github.com/Pick-Your-AI/pickyour.ai/issues/284) |
| 17.05 | Feature | [#285 — Compatibility maintenance and release cadence](https://github.com/Pick-Your-AI/pickyour.ai/issues/285) |
| 18 | Epic | [#181 — Decision-dependent expansion](https://github.com/Pick-Your-AI/pickyour.ai/issues/181) |
| 18.01 | Feature | [#286 — Favorites and price/compatibility alerts](https://github.com/Pick-Your-AI/pickyour.ai/issues/286) |
| 18.02 | Feature | [#287 — Paid plans and entitlements](https://github.com/Pick-Your-AI/pickyour.ai/issues/287) |
| 18.03 | Feature | [#288 — Community build publishing and moderation](https://github.com/Pick-Your-AI/pickyour.ai/issues/288) |
| 18.04 | Feature | [#289 — Advanced recommendations and personalization](https://github.com/Pick-Your-AI/pickyour.ai/issues/289) |
| 18.05 | Feature | [#290 — Actual runtime execution or provisioning](https://github.com/Pick-Your-AI/pickyour.ai/issues/290) |
| 18.06 | Feature | [#291 — Additional markets and platforms](https://github.com/Pick-Your-AI/pickyour.ai/issues/291) |

## Verification boundary

Publication checks verified every live issue marker/title, all seven custom/status field values per item, native parent placement, exact child counts, prerequisite presence, unassigned/open state, and nine configured views. Local dependency traversal checked the Apple prerequisite graph for cycles.

Repository validation covers contract/import integrity and research intake, not the correctness of future application code, source claims, store approval or production behavior. Those remain the issue acceptance gates. Shared-service completion and Apple integration acceptance remain separate outcomes.
