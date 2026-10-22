# TwinTail

A standalone GenLayer oracle for **paired binary experiment inference under incomplete prose observations**. It freezes a family of endpoints, independently adjudicates every control/treatment observation, computes sharp per-endpoint p-value bounds over every compatible completion, and applies Holm correction to the entire family.

The difficult case is a partially documented experiment. Dropping missing pairs can manufacture significance. Testing each endpoint independently can also manufacture a family finding. TwinTail exposes both problems: one unresolved endpoint can make a fully observed endpoint's multiplicity-adjusted decision unresolved.

**Deployed and verified on gasless StudioNet:** [primary contract](https://explorer-studio.genlayer.com/address/0x399C922094A90Aa6a4cF5E28169d9bDCfF59463f), [24 finalized scenario receipts](proofs/README.md), [ready contribution text](docs/submission.md). All three families match independent exhaustive oracles and fresh onchain reads. Lint, 56 direct tests and seven transport tests pass. Twelve receipts are expected rejected calls with unchanged state; four adjudications preserve a dissenting vote.

## Mechanism

1. Deploy with 1–3 immutable endpoint IDs, 3–8 ordered matched-pair IDs per endpoint, commit-pinned raw GitHub URLs and SHA-256 hashes. The family threshold is fixed at **1/20**. There is no administrator or replacement endpoint.
2. Anyone calls `adjudicate(index)`. The leader fetches the entire committed report. A language model classifies both arms of every pair as `PASS`, `FAIL` or `UNKNOWN`, with verbatim supporting excerpts. The fixed endpoint is **designated task completed within its observation window without manual intervention**.
3. Validators independently re-fetch the full report, verify its exact commitment and roster, independently classify all observations, compare every consequential label exactly, and audit both labels and quotes against the complete text. Missingness is an independently verified decision.
4. Deterministic dynamic programming retains every reachable `(treatment_wins, control_wins)` under every binary completion of unknown arms. Ties contribute no discordant trial. Exact one-sided conditional sign/McNemar tails use integers on a denominator of 256. The ledger records minimum and maximum p-values, attainable binary witnesses, counts and state-space size.
5. `finalize()` requires all endpoints. Holm-adjusted lower and upper vectors yield `SUPPORTED`, `NOT_ESTABLISHED` or `REVIEW` for every endpoint. Repeated adjudication/finalization and premature finalization fail without changing state. Other contracts can read the resulting oracle state; it does not award a service certificate or move funds.

## Examples

| Family | Raw p-values | Holm-adjusted bounds | Result |
|---|---|---|---|
| stepdown | 2/256, 8/256 | 4/256, 8/256 | Both supported; the second endpoint benefits from stepdown |
| multiplicity | 8/256, 256/256 | 16/256, 256/256 | Neither established; the first would pass an uncorrected test |
| ambiguity | [1,37]/256, 8/256 | [2,37]/256, [8,16]/256 | Both require review, although the second endpoint is fully observed |

These are synthetic software-run reports. Fixtures include withdrawn drafts, forecasts, manual rescue, late retries, truncated logs and conflicting final reports. They demonstrate the mechanism rather than real experiments.

## Statistical scope

The conditional one-sided sign test assumes independent matched pairs whose discordant signs are fair under the null (for example a suitable randomized matched-pair design). The alternative is treatment superiority. **TwinTail cannot verify random assignment, collection honesty, representative sampling or absence of selective reporting.** A deployer can commit cherry-picked historical reports or deploy multiple families; the contract does not prevent that. The family is fixed before onchain adjudication, which is not proof of preregistration before data collection. A hash binds bytes, not truth or authorship.

Unknown observations range freely over binary completions; no missing-at-random assumption is used for these bounds. Per-endpoint p extrema are sharp in that completion model, and each has an explicit witness. Holm endpoint bounds are conservative; they do not model additional cross-endpoint logical constraints. `NOT_ESTABLISHED` does not prove equality or inferiority, and `SUPPORTED` is a hypothesis-test decision, not a probability that a claim is true. The statistical guarantees remain conditional on valid underlying experiments and correct interpretation.

The exact binomial tail and Holm procedure are established methods, not new statistical discoveries. References: [R exact binomial test](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/binom.test.html), [R Holm adjustment and Holm (1979)](https://stat.ethz.ch/R-manual/R-patched/library/stats/html/p.adjust.html).

## Reproduce

Use Python 3.13 and Node 24:

```sh
python -m venv .venv
# Activate .venv for your shell.
pip install -r requirements-dev.txt
genvm-lint download --version v0.2.16
genvm-lint check contracts/twin_tail.py --json
python -m pytest tests/direct -q
node --test tests/rpc-preflight.test.cjs
npm ci --no-audit --no-fund
```

Direct tests execute the pinned SDK and explicit validator callbacks. An independent oracle enumerates binary completions and null coin assignments, rather than copying the contract's DP/binomial computation. Coverage includes every three-pair partial profile, generated larger cohorts, Holm stepdown comparisons, witness attainability, source failures, exact validator disagreement and complete rollback. Direct mocks do not establish live model reliability.

Run the public `StudioNet paired inference proofs` workflow with `stepdown`, `multiplicity` or `ambiguity`. Each run deploys through the CLI on gasless **StudioNet, chain 61999**, then checks every signed call against a separate exhaustive JavaScript oracle. A finalized deployment alone is not a scenario pass. Native CLI tooling is locked, including `viem@2.56.3`, to avoid an unavailable upstream tarball.

Local fresh verification needs an existing CLI account for read-only calls:

```sh
# Set GENLAYER_CLI_PATH to the absolute local genlayer/dist/index.js path.
# Set TWIN_ACCOUNT to an existing CLI account name; no key export is needed.
node scripts/verify-proofs.cjs --offline
node scripts/verify-proofs.cjs
```

Proof workflows use disposable encrypted caller accounts and discard their keys. All methods are permissionless, so those wallets do not control the deployed oracle. Reports and plans are immutable. A changed report, endpoint, cohort or retry strategy requires a separate deployment, not a rewrite of an existing result.

## Repository

- [Contract](contracts/twin_tail.py)
- [Consensus and inference design](docs/design.md)
- [Constructor, report schema and consumer API](docs/api.md)
- [Direct tests](tests/direct/test_inference.py)
- [Live proof plan and independent oracle](scripts/scenario.cjs)
- [Proof receipts](proofs/README.md)

The TwinTail contract, fixtures, inference oracle and tests are new. Generic CLI transport, receipt verification, Windows test fixture and workflow scaffolding derive from the MIT-licensed [FaultWeave](https://github.com/moorisi/fault-weave) tooling. This project has no quorum synthesis, signer proposals, endorsement lifecycle or native register.
