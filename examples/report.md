# PFMEA ↔ Control Plan Validation Report

- **Generated:** 2026-06-20 13:47 UTC
- **PFMEA:** `pfmea.xlsx` (4 rows)
- **Control Plan:** `control-plan.xlsx` (3 rows)

## Summary

- **Score:** 43 / 100
- **Verdict:** FAIL
- **Critical findings:** 3
- **Warnings:** 3

## Findings

| # | Type | Level | Operation | Detail |
|---|------|-------|-----------|--------|
| 1 | UNMATCHED_PROCESS_STEP | 🟡 warning | 40 | PFMEA operation 40 has no matching row in the Control Plan. |
| 2 | SPECIAL_CHARACTERISTIC_NOT_CONTROLLED | 🔴 critical | 20 | Operation 20 is flagged as a special characteristic in the PFMEA but is not marked/controlled as special in the Control Plan. |
| 3 | MISSING_REACTION_PLAN | 🔴 critical | 20 | Operation 20 has a high-severity failure mode (S=9) but the Control Plan control has no reaction plan. |
| 4 | WEAK_DETECTION_METHOD | 🟡 warning | 20 | Operation 20 relies on a weak detection method (Visual inspection). |
| 5 | HIGH_SEVERITY_WEAK_CONTROL | 🟡 warning | 20 | Operation 20 has a high-severity failure mode (S=9) paired with a weak control method. |
| 6 | MISSING_CONTROL | 🔴 critical | 30 | Operation 30 has PFMEA failure mode(s) but no control method in the Control Plan. |

> ⚠️ These are **potential** findings to support human review. quality-docs-validator is **not a substitute for human technical judgement** and makes no regulatory or normative conformance claim.
