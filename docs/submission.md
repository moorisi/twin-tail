# Ready contribution

**Category:** Builder → Intelligent Contracts

**Contribution date:** 2026-10-22

**Title:** TwinTail: Consensus paired-inference bounds

## Notes / Description (978 characters)

TwinTail is a standalone GenLayer oracle for paired binary experiment reports. A deployment freezes 1–3 endpoints, ordered pair rosters and commit-pinned report URLs/SHA-256 hashes. Leader and validators independently fetch full texts, classify both arms of every pair as PASS, FAIL or UNKNOWN, and audit source-linked quotes with exact label agreement. Dynamic programming retains every possible completion of unknown arms and records sharp exact sign-test p-value bounds with attainable witnesses. Holm correction across the complete family produces SUPPORTED, NOT_ESTABLISHED or REVIEW; a fully observed endpoint can require review because another is unresolved. Gasless StudioNet proofs cover stepdown support, multiplicity rejection, ambiguity propagation and unchanged state on rejected calls. The repo includes 56 direct tests, exhaustive completion oracles and verified receipts. Fixtures are synthetic; consensus does not establish honest sampling or random assignment.

## Evidence links

- [Public repository](https://github.com/moorisi/twin-tail)
- [GenLayer contract source](https://github.com/moorisi/twin-tail/blob/main/contracts/twin_tail.py)
- [Primary contract explorer](https://explorer-studio.genlayer.com/address/0x399C922094A90Aa6a4cF5E28169d9bDCfF59463f)
- [Deployment transaction](https://explorer-studio.genlayer.com/tx/0x707cbd1ed0c07fc47e0b7f0b3f43def38dbfe343721246daf3cbe29977829542)
- [All scenario proofs, transactions and preserved votes](https://github.com/moorisi/twin-tail/blob/main/proofs/README.md)
- [Passing CI](https://github.com/moorisi/twin-tail/actions/runs/39749291981)

## Additional deployed scenarios

- [Multiplicity rejection contract](https://explorer-studio.genlayer.com/address/0xae3004B29fE5396DFD1Bd97244023e36B04d999B)
- [Ambiguity propagation contract](https://explorer-studio.genlayer.com/address/0xCe13Bc11293c097E2bDD6328fb11864F220DF187)

All 24 receipts finalized with MAJORITY_AGREE: 12 successful executions and 12 expected rejections. Fresh source/calldata/votes/full-state verification passed. Four adjudication receipts retain a dissenting vote. Synthetic fixtures demonstrate the mechanism; this is not proof of real experimental validity.
