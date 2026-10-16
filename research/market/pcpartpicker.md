# PCPartPicker experience transfer

Status: partial evidence; authenticated workflow unverified. Accessed 2026-10-16.

The [requested list URL](https://pcpartpicker.com/list/) returned HTTP 403 in web retrieval. A browser visit redirected to `/accounts/login/?next=/list/`. No account was created, credentials used, access control bypassed or saved build changed. Current filtering, compatibility warnings, price aggregation and sharing behavior could not be directly verified in that session.

The following are original AI UX hypotheses inspired by the user-provided product vision, not observations of PCPartPicker's current interface:

1. Show a component-by-component decision record with optional tiers.
2. Explain a constraint conflict using the two affected selections and the dated rule.
3. Separate a hard incompatibility from unmeasured performance or missing evidence.
4. Preserve a versioned configuration link and show source changes on revisit.
5. Compare total-cost assumptions beside component prices.

The coordinator should arrange an authorized walkthrough and record selection, filter, warning, save/share and pricing steps before accepting MR-04. Findings feed #2, #3, #40 and #42. This access gap does not block independent AI product research.
