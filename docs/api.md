# Contract API

## Constructor

```python
TwinTail(repository, family, endpoints, pairs, urls, hashes)
```

| Argument | Meaning |
|---|---|
| `repository: str` | Fixed `owner/repository` for every source |
| `family: str` | Lowercase family ID, 3–40 characters |
| `endpoints: list[str]` | 1–3 unique endpoint IDs, in output order |
| `pairs: list[list[str]]` | Ordered, unique pair IDs for each endpoint; 3–8 per endpoint |
| `urls: list[str]` | One `https://raw.githubusercontent.com/owner/repository/<40-char-commit>/fixtures/<slug>.json` per endpoint |
| `hashes: list[str]` | Lowercase SHA-256 of exact UTF-8 response bytes, one per URL |

Endpoint and pair IDs use lowercase letters, digits and hyphens, 3–40 characters, starting with a letter or digit. URL query strings, branch names, alternate hosts, unpinned revisions and arbitrary path traversal are rejected. Alpha is always 1/20; the alternative is always treatment superiority for the fixed completion-without-intervention endpoint.

Each committed JSON report has exactly these keys:

```json
{
  "family": "example-family",
  "endpoint": "archive-export",
  "pairs": [
    {
      "pair": "pair-one",
      "control": "Full narrative observation for the control arm, 20–800 characters.",
      "treatment": "Full narrative observation for the treatment arm, 20–800 characters."
    }
  ]
}
```

The displayed row is a schema example; a valid report needs the complete 3–8-row constructor roster. Do not pre-classify the arm using a JSON status field. The contract interprets actual prose, and requires correct source scope, complete ordered roster and exact schema. Byte commitments include whitespace and line endings.

## Writes

`adjudicate(index: int) -> None`: permissionless. Fetch and interpret exactly one unassessed endpoint, run substantive validator consensus, then atomically store its full source, observations and p bounds. Other endpoints remain unchanged. Index is zero-based. A network, source or unresolved model error changes no state. A genuine `UNKNOWN` observation is a successful interpretation, not an execution error.

`finalize() -> None`: permissionless. Requires all endpoints assessed and no existing final result. Stores multiplicity-adjusted bounds and decisions once. Finalizing a partial family is forbidden even if its first endpoint looks significant.

There are no report updates, owner overrides, optional exclusions, reassessments, new endpoints or threshold changes. Deploy a new instance to define a different analysis; it must not be represented as a continuation of this frozen family.

## Read

`get_state() -> dict` returns the complete immutable configuration, one nullable assessment and bounds entry per endpoint, and a nullable final family result. `assessments[i].observations.rows[j]` identifies the pair, both labels and both verbatim quotes. An endpoint bound includes:

```text
lower_ticks, upper_ticks       # raw p-value extrema, divide by 256
lower_witness, upper_witness   # [control_bit,treatment_bit] per ordered pair
lower_counts, upper_counts    # [treatment_wins,control_wins] at the witnesses
reachable_counts              # number of attainable (wins,losses) states
```

Final `result` contains `status`, `denominator=256`, `alpha=[1,20]`, `lower_adjusted_ticks`, `upper_adjusted_ticks`, and `decisions`, in constructor endpoint order. Consumers should use these family decisions, not apply an uncorrected cutoff to one selected raw endpoint. `REVIEW` can arise for a fully observed endpoint due to uncertainty elsewhere in the family. A missing result means the family has not been finalized, not that the null was accepted.

Example read through another GenLayer contract:

```python
state = gl.get_contract_at(Address(oracle_address)).view().get_state()
result = state['result']
# Apply the consuming contract's explicit rules only after checking its expected
# configuration, final result, and the desired endpoint's family decision.
```

Calling wallets are not owners of the oracle. Disposable proof accounts can disappear without taking away anyone else's ability to adjudicate or finalize an unfinished instance.
