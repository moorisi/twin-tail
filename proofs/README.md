# StudioNet scenario proofs

**Verified 2026-10-22.** Gasless StudioNet, chain **61999**, RPC `https://studio.genlayer.com/api`. These are test-network deployments, not mainnet.

**24 distinct finalized `MAJORITY_AGREE` receipts:** 12 successful executions (3 deployments, 6 nondeterministic endpoint adjudications, 3 family finalizations), plus 12 expected business-error executions. Every rejected call preserves the complete preceding state. Three hosted JUnit reports each record 56 direct tests, zero failures, errors or skips; seven transport tests also pass.

Fresh verification completed at **2026-10-22T08:52:20.002Z**. Contract bytes, calldata, targets, actual signing callers, complete vote sets, exact rejection bytes, every intermediate whole-state replay and fresh final onchain reads passed. [Combined verification](verification.json), [receipt journal](transactions.json), [workflow provenance](provenance.json), [deployment arguments](suite.json).

- Contract source SHA-256: `b7f9c0422a03317995da7343e15b8a06d63d7cfc25192bb18c6dcdd0f9ac8c92`.
- Source/tooling revision deployed: `d0ef6fbf4bf58f84e1b16bd0f79b5d388fa40b65`.
- Commit-pinned fixture revision: `f5f631f7c9a9c6640741e5fdc59cbd953d42e81c`.
- [Passing CI](https://github.com/moorisi/twin-tail/actions/runs/39749291981).

## Deployed families

| Family | Contract explorer | Final decisions | Finalization transaction |
|---|---|---|---|
| stepdown | [`0x399C922094A90Aa6a4cF5E28169d9bDCfF59463f`](https://explorer-studio.genlayer.com/address/0x399C922094A90Aa6a4cF5E28169d9bDCfF59463f) | SUPPORTED, SUPPORTED | [finalize](https://explorer-studio.genlayer.com/tx/0xc79ec3789c5677187c667e6abe36a3d77d1d11aa146467763345cea7ad54ab22) |
| multiplicity | [`0xae3004B29fE5396DFD1Bd97244023e36B04d999B`](https://explorer-studio.genlayer.com/address/0xae3004B29fE5396DFD1Bd97244023e36B04d999B) | NOT_ESTABLISHED, NOT_ESTABLISHED | [finalize](https://explorer-studio.genlayer.com/tx/0x407582791b84c2cf12ffbabaed3bb02df0fc132b6828d70257147e8e6b60b03a) |
| ambiguity | [`0xCe13Bc11293c097E2bDD6328fb11864F220DF187`](https://explorer-studio.genlayer.com/address/0xCe13Bc11293c097E2bDD6328fb11864F220DF187) | REVIEW, REVIEW | [finalize](https://explorer-studio.genlayer.com/tx/0x05edf0b0cadf9fc2cd5db768de9098c4af0afcfc8219ca70bae35eab50542566) |

### Stepdown support

Raw p-values are 2/256 and 8/256. Holm adjusts them to 4/256 and 8/256: both endpoints are `SUPPORTED`. The second endpoint would fail a plain two-test Bonferroni cutoff but passes the precommitted family's stepdown procedure. [State](stepdown-final-state.json), [complete call trace](stepdown-trace.json), [hosted tests](stepdown-direct-tests.xml), [workflow](https://github.com/moorisi/twin-tail/actions/runs/39749358961).

### Multiplicity rejection

Raw p-values are 8/256 and 256/256. The first would pass an uncorrected 1/20 test; Holm produces 16/256 and 256/256, so neither endpoint is established. The first endpoint cannot be finalized while the second is missing. [State](multiplicity-final-state.json), [complete call trace](multiplicity-trace.json), [hosted tests](multiplicity-direct-tests.xml), [workflow](https://github.com/moorisi/twin-tail/actions/runs/39749364396).

### Missing-outcome propagation

Six pairs favor treatment; two pairs have both arms unresolved. The first endpoint's attainable p-value bounds are [1,37]/256, witnessed by completions with [8 wins,0 losses] and [6 wins,2 losses]. The second endpoint is fully observed at 8/256. Holm-adjusted bounds are [2,37]/256 and [8,16]/256, so **both endpoints are `REVIEW`**. Dropping the unknown pairs would falsely establish a finding. [State](ambiguity-final-state.json), [complete call trace](ambiguity-trace.json), [hosted tests](ambiguity-direct-tests.xml), [workflow](https://github.com/moorisi/twin-tail/actions/runs/39749369053).

## Every transaction

`A/D/I` lists every recorded agree/disagree/idle vote, including the leader. Strict majority is checked against the full recorded voter count, not just responding validators. Four adjudications have a dissenting vote; this proof set does not claim unanimity. All stored dissent and idle votes are preserved.

| Call | Execution | A/D/I | Explorer | Receipt |
|---|---|---|---|---|
| stepdown-deployment | SUCCESS | 5/0/0 | [transaction](https://explorer-studio.genlayer.com/tx/0x707cbd1ed0c07fc47e0b7f0b3f43def38dbfe343721246daf3cbe29977829542) | [JSON](stepdown-deployment-receipt.json) |
| stepdown-reject-empty-family | expected ERROR | 5/0/0 | [transaction](https://explorer-studio.genlayer.com/tx/0xaf6b7ed04f03e9bb467c6921a3889d42a05224ad7de468cf2ade524b890e9120) | [JSON](stepdown-reject-empty-family-receipt.json) |
| stepdown-adjudicate-second | SUCCESS | 3/0/2 | [transaction](https://explorer-studio.genlayer.com/tx/0xf1b809df018a14a6d5ce21b3a7a76e31f4aceb427f46df63f13f6716a27e4674) | [JSON](stepdown-adjudicate-second-receipt.json) |
| stepdown-reject-partial-family | expected ERROR | 5/0/0 | [transaction](https://explorer-studio.genlayer.com/tx/0x2b8fd1e7147e6832b21cbfc3f0dd933bb7af80f6d73eb555d781e6ca2dc73147) | [JSON](stepdown-reject-partial-family-receipt.json) |
| stepdown-adjudicate-first | SUCCESS | 3/1/1 | [transaction](https://explorer-studio.genlayer.com/tx/0x14b0ce5929c77f2b2e7eb3798ec74e9fb5fa92591c0919fa4d5cad16e4d8fa78) | [JSON](stepdown-adjudicate-first-receipt.json) |
| stepdown-finalize | SUCCESS | 3/0/2 | [transaction](https://explorer-studio.genlayer.com/tx/0xc79ec3789c5677187c667e6abe36a3d77d1d11aa146467763345cea7ad54ab22) | [JSON](stepdown-finalize-receipt.json) |
| stepdown-reject-repeat-endpoint | expected ERROR | 3/0/2 | [transaction](https://explorer-studio.genlayer.com/tx/0xf46fa137556f3155b4e0002f8f6f0a7a9cbb22ad80989d4944d16bea4a607c88) | [JSON](stepdown-reject-repeat-endpoint-receipt.json) |
| stepdown-reject-repeat-finalize | expected ERROR | 3/0/2 | [transaction](https://explorer-studio.genlayer.com/tx/0x6ff3ae0d8e873a7b00992d6c0ea9a693a5b9aad0cbed84ba9eeba517709fbf79) | [JSON](stepdown-reject-repeat-finalize-receipt.json) |
| multiplicity-deployment | SUCCESS | 5/0/0 | [transaction](https://explorer-studio.genlayer.com/tx/0xc55d6fb337042b4685d7a11101437867b6c40ea0fd797a589a7faafad757f67c) | [JSON](multiplicity-deployment-receipt.json) |
| multiplicity-reject-empty-family | expected ERROR | 3/0/2 | [transaction](https://explorer-studio.genlayer.com/tx/0xe1e3a6045523b62a49df73e11e9e449069be4784e7c44eceaea534b68efc2c82) | [JSON](multiplicity-reject-empty-family-receipt.json) |
| multiplicity-adjudicate-second | SUCCESS | 3/0/2 | [transaction](https://explorer-studio.genlayer.com/tx/0x1d0183169937ac3a255182e4055b7f4184d50469e44d48d5a747943e2a5a4043) | [JSON](multiplicity-adjudicate-second-receipt.json) |
| multiplicity-reject-partial-family | expected ERROR | 5/0/0 | [transaction](https://explorer-studio.genlayer.com/tx/0xb15ddb3642b2f44ee5768c84b597da6118c83e0e6d53f7f57a77cd187b5dc474) | [JSON](multiplicity-reject-partial-family-receipt.json) |
| multiplicity-adjudicate-first | SUCCESS | 3/1/1 | [transaction](https://explorer-studio.genlayer.com/tx/0x6a750a69973c82ee3ff194ea263d71e29858d305625e12c00f16435223920339) | [JSON](multiplicity-adjudicate-first-receipt.json) |
| multiplicity-finalize | SUCCESS | 5/0/0 | [transaction](https://explorer-studio.genlayer.com/tx/0x407582791b84c2cf12ffbabaed3bb02df0fc132b6828d70257147e8e6b60b03a) | [JSON](multiplicity-finalize-receipt.json) |
| multiplicity-reject-repeat-endpoint | expected ERROR | 5/0/0 | [transaction](https://explorer-studio.genlayer.com/tx/0x743c69f64287cc5dec628cf8387edb77ea6dbe3fff07a92284958bc86ee57d67) | [JSON](multiplicity-reject-repeat-endpoint-receipt.json) |
| multiplicity-reject-repeat-finalize | expected ERROR | 3/0/2 | [transaction](https://explorer-studio.genlayer.com/tx/0x58aec9564f28cd4a2ee1be0d3f327f6e099b99717222befcba51556d43bf64df) | [JSON](multiplicity-reject-repeat-finalize-receipt.json) |
| ambiguity-deployment | SUCCESS | 5/0/0 | [transaction](https://explorer-studio.genlayer.com/tx/0x67186a8e22053e53ddd95f4127f7c238de0cd9811fd4f2f8c5f528dbf0160116) | [JSON](ambiguity-deployment-receipt.json) |
| ambiguity-reject-empty-family | expected ERROR | 5/0/0 | [transaction](https://explorer-studio.genlayer.com/tx/0x065d80b27bc9ca8f2b560094103379ac3bbef44b0fd795f560dd2a8efdd4cfe2) | [JSON](ambiguity-reject-empty-family-receipt.json) |
| ambiguity-adjudicate-second | SUCCESS | 3/1/1 | [transaction](https://explorer-studio.genlayer.com/tx/0x38112153ad31630627544202b252f52deb7522b6cd282be20662babc744e165c) | [JSON](ambiguity-adjudicate-second-receipt.json) |
| ambiguity-reject-partial-family | expected ERROR | 3/0/2 | [transaction](https://explorer-studio.genlayer.com/tx/0x7d79db8d059f78c2ceed5e5d550b20b2b387008dd06c215a0c26e42e5846fec8) | [JSON](ambiguity-reject-partial-family-receipt.json) |
| ambiguity-adjudicate-first | SUCCESS | 3/1/1 | [transaction](https://explorer-studio.genlayer.com/tx/0xf9539cf1a9af83ce82f10edebecbd2891fb8caed80925f4e4d9e5fa4c252b81b) | [JSON](ambiguity-adjudicate-first-receipt.json) |
| ambiguity-finalize | SUCCESS | 5/0/0 | [transaction](https://explorer-studio.genlayer.com/tx/0x05edf0b0cadf9fc2cd5db768de9098c4af0afcfc8219ca70bae35eab50542566) | [JSON](ambiguity-finalize-receipt.json) |
| ambiguity-reject-repeat-endpoint | expected ERROR | 5/0/0 | [transaction](https://explorer-studio.genlayer.com/tx/0x233e36125a535cd0bfe249e136cb39c0a87cf52a5efcb3ff2eb67a080f0dc3c6) | [JSON](ambiguity-reject-repeat-endpoint-receipt.json) |
| ambiguity-reject-repeat-finalize | expected ERROR | 3/0/2 | [transaction](https://explorer-studio.genlayer.com/tx/0xed0e378c67fe65d10bebd1ffeb4286fd498b805ef4c71d49eb0b72f9e227198d) | [JSON](ambiguity-reject-repeat-finalize-receipt.json) |

## Reproduce verification

Merge separately downloaded artifacts in stepdown, multiplicity, ambiguity order with `scripts/merge-proofs.cjs`. Set `GENLAYER_CLI_PATH` and an existing `TWIN_ACCOUNT` for read-only CLI state calls. Run `node scripts/verify-proofs.cjs --offline`, then `node scripts/verify-proofs.cjs` for independent fresh receipt/code/state verification. Neither command sends a transaction. Re-running a live proof deploys a new instance; it does not overwrite these results.

The fixtures are synthetic. They test narrative interpretation, unknown-outcome handling, exact inference, family coupling and fail-closed lifecycle rules. Source consensus does not establish collection honesty, random assignment or absence of selection bias. A frozen onchain plan is not proof of preregistration before outcome collection. See [statistical assumptions](../README.md#statistical-scope).

Proof wallets were created on disposable runners and their keys were discarded. The oracle has no owner or signing threshold: its writes are permissionless, and losing a caller key confers no administrative lock. These three instances are already fully finalized and immutable.
