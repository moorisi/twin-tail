# Boundary and invariants

## Consensus boundary

Caller -> immutable family/source commitments -> contract-side full report fetch -> independent semantic classification of every arm -> exact validator label agreement plus full-source quote/decision audit -> exact partial-outcome inference -> family-wide hypothesis decisions.

A UI may preview a report or calculate statistics but provides no authoritative labels. Sources own the underlying assertions. Validators establish agreement about their contents, not real-world authenticity. An external consumer owns any action it takes after reading `get_state()`; no escrow or external side effect is claimed.

Only two nondeterministic operations occur: acquiring the fixed report and interpreting prose. Their consequential output is the complete PASS/FAIL/UNKNOWN matrix. The leader cannot pick the cohort size, skip an observation, silently treat a missing arm as failure, change the alternative, exclude an inconvenient endpoint or choose an alpha. Validators obtain their own matrix before auditing the leader's complete proposal. Quote wording may differ; exact labels may not.

Both web and LLM data are untrusted. Duplicate JSON keys, wrong source hash, extra schema fields, wrong endpoint/pair order, oversize bodies, malformed model rows and invented quotes fail. Prompt data cannot change the inference or call other methods. A schema-valid label is insufficient: independent rerun and substantive source audit are required. Bounded schema repair does not accept repeated LLM failure. Matching source/transient errors may establish agreement only on a failed call; they never store an assessment.

## Sharp endpoint bounds

Write a completed pair as `(c,t)` with 0=FAIL and 1=PASS. `UNKNOWN` permits either value. Every pair contributes a treatment win, control win or tie. A DP maps reachable `(w,l)` to the lexicographically first binary completion producing it. There are at most 45 count states for eight pairs, even though all-unknown reports admit 65,536 arm completions. Keeping one witness per count state is lossless because the test depends only on those counts.

For `d=w+l` discordant pairs:

```text
p(w,l) = sum(C(d,k), k=w..d) / 2^d
ticks(w,l) = 256 * p(w,l)
```

For d=0 the value is 1, not 0. Taking the minimum and maximum over all reachable states produces attainable extrema; stored witnesses reproduce both. Ties are excluded only after an actual completion makes the arm values equal. Missing observations are never discarded as if tied. Integer ticks are exact because d<=8. No floating point or numerical equivalence tolerance is used.

## Family correction

For ordered raw p-values p(1)<=...<=p(m), Holm adjusted values are the running maximum of `min(1,(m-rank+1)*p(rank))`, mapped back to endpoint order. Endpoint-index tie breaking makes the representation deterministic. The method is monotone in each input. Apply it to the componentwise lower and upper endpoint p bounds:

- adjusted upper <= 1/20: `SUPPORTED` under every admissible completion;
- adjusted lower > 1/20: `NOT_ESTABLISHED` under every admissible completion;
- otherwise `REVIEW`.

These bounding vectors are conservative when extra cross-endpoint constraints exist. The method does not assume independence between endpoints; valid per-endpoint tests are still required. Holm does not repair dishonest sampling or post-hoc experiment selection.

## State

Configuration fixes source repository, family ID, ordered endpoint IDs, pair rosters, source URLs and hashes. Assessments and bounds have one slot per endpoint. An assessment contains full normalized source, exact labels and quotes. Bounds contain exact p extrema, witnesses and counts. The final result contains fixed alpha, denominator, both adjusted vectors and endpoint decisions.

Each endpoint transitions unassessed -> assessed once, in any order. Family result transitions unset -> final once only after every endpoint is assessed. No owner, voting, policy update, proposal graph, consumption ticket or certificate lifecycle exists. Failed calls leave the entire state unchanged. There are at most three evidence acquisitions, 48 interpreted arm decisions, and one family finalization per deployment.

## Validation strategy

Direct tests cover real SDK state changes, failed-call rollback, validator independent disagreement, refetching, audit failures and error classification. Exhaustive tests enumerate all 729 partial three-pair profiles; generated tests cover 96 larger partially observed cohorts. Independent null coin enumeration checks tails and attainable witnesses. Holm rejection-only tests check 1,463 vectors around and away from the threshold. Joint completion tests demonstrate uncertainty propagating to a fully observed endpoint.

Live proofs use three independently deployed families with signed calls from multiple permissionless callers. Each scenario checks exact deployed bytes, finalized receipt outcome, the complete voter set, actual sender and decoded calldata, independent whole-state replay after every call, exact error bytes, and fresh final state. The proof oracle does not import the contract or trust transaction return summaries.
