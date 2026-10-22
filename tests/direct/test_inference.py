import ast
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import re
import subprocess
from fractions import Fraction
import pytest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'contracts/twin_tail.py'
REPO = 'moorisi/twin-tail'
LABELS = ['FAIL', 'PASS', 'UNKNOWN']


def functions():
    names = {'integer', 'possible_arms', 'tail_ticks', 'endpoint_bounds', 'holm_adjust', 'family_result', 'valid_observations'}
    tree = ast.parse(SOURCE.read_text())
    ns = {'math': math}
    exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name in names], type_ignores=[]), str(SOURCE), 'exec'), ns)
    return ns


F = functions()


def statuses(case, endpoint):
    if endpoint == 1:
        return [('PASS', 'FAIL')] * 3 + [('FAIL', 'FAIL')] * 5 if case == 'multiplicity' else [('FAIL', 'PASS')] * 5 + [('PASS', 'PASS')] * 3
    if case == 'stepdown': return [('FAIL', 'PASS')] * 7 + [('PASS', 'PASS')]
    if case == 'multiplicity': return [('FAIL', 'PASS')] * 5 + [('PASS', 'PASS')] * 3
    return [('FAIL', 'PASS')] * 6 + [('UNKNOWN', 'UNKNOWN')] * 2


def record(case, index):
    raw = (ROOT / 'fixtures' / f'{case}-{index}.json').read_bytes()
    return f'https://raw.githubusercontent.com/{REPO}/' + 'a' * 40 + f'/fixtures/{case}-{index}.json', hashlib.sha256(raw).hexdigest(), raw


def answer(case='stepdown', index=0):
    source = json.loads(record(case, index)[2])
    return {'rows': [dict(pair=row['pair'], control=s[0], treatment=s[1], control_quote=row['control'], treatment_quote=row['treatment']) for row, s in zip(source['pairs'], statuses(case, index))]}


def deploy(factory, case='stepdown', bodies=None, **kwargs):
    records = [record(case, i) for i in range(2)]
    args = dict(repository=REPO, family=case + '-family', endpoints=['archive-export', 'report-import'], pairs=[[f'pair-{i+1}' for i in range(8)]] * 2, urls=[x[0] for x in records], hashes=[hashlib.sha256(bodies[i]).hexdigest() if bodies is not None else x[1] for i, x in enumerate(records)])
    args.update(kwargs)
    return factory(str(SOURCE), **args)


def mocks(vm, case='stepdown', index=0, proposed=None, audit=None, body=None, status=200):
    vm.clear_mocks()
    url, _, raw = record(case, index)
    vm.mock_web(re.escape(url), {'status': status, 'body': raw if body is None else body})
    vm.mock_llm(r'.*TWINTAIL-EXTRACT.*', json.dumps(answer(case, index) if proposed is None else proposed))
    vm.mock_llm(r'.*TWINTAIL-AUDIT.*', json.dumps({'rows': [True] * 8} if audit is None else audit))


def adjudicate(c, vm, case, index):
    mocks(vm, case, index)
    c.adjudicate(index)
    assert vm.run_validator() is True


def enumerated(rows):
    # Independent oracle enumerates ALL binary completions and ALL null coin
    # assignments, using Fraction. No dynamic programming or binomial coefficient.
    domains = [[(c, t) for c in ([0, 1] if row['control'] == 'UNKNOWN' else [int(row['control'] == 'PASS')]) for t in ([0, 1] if row['treatment'] == 'UNKNOWN' else [int(row['treatment'] == 'PASS')])] for row in rows]
    found = {}
    for completion in itertools.product(*domains):
        wins = sum(t > c for c, t in completion)
        losses = sum(c > t for c, t in completion)
        n = wins + losses
        tail = Fraction(sum(sum(coins) >= wins for coins in itertools.product([0, 1], repeat=n)), 2 ** n)
        witness = [list(x) for x in completion]
        if (wins, losses) not in found or witness < found[wins, losses][1]: found[wins, losses] = (tail, witness)
    low = min(found, key=lambda k: found[k])
    high = min(found, key=lambda k: (-found[k][0], found[k][1]))
    return {'lower_ticks': int(found[low][0] * 256), 'upper_ticks': int(found[high][0] * 256), 'lower_witness': found[low][1], 'upper_witness': found[high][1], 'lower_counts': list(low), 'upper_counts': list(high), 'reachable_counts': len(found)}


def stepdown_rejections(ticks):
    # Independent rejection-only implementation, no adjusted p-value algorithm.
    order = sorted(range(len(ticks)), key=lambda i: (ticks[i], i))
    rejected = [False] * len(ticks)
    for rank, i in enumerate(order):
        if Fraction(ticks[i], 256) > Fraction(1, 20 * (len(ticks) - rank)): break
        rejected[i] = True
    return rejected


@pytest.mark.parametrize('case,decisions', [('stepdown', ['SUPPORTED', 'SUPPORTED']), ('multiplicity', ['NOT_ESTABLISHED', 'NOT_ESTABLISHED']), ('ambiguity', ['REVIEW', 'REVIEW'])])
def test_whole_family_and_permissionless_order(direct_deploy, direct_vm, direct_accounts, case, decisions):
    c = deploy(direct_deploy, case)
    before = c.get_state()
    with direct_vm.expect_revert('Every endpoint required'): c.finalize()
    assert c.get_state() == before
    direct_vm.sender = direct_accounts[3]
    adjudicate(c, direct_vm, case, 1)
    middle = c.get_state()
    with direct_vm.expect_revert('Every endpoint required'): c.finalize()
    assert c.get_state() == middle
    direct_vm.sender = direct_accounts[4]
    adjudicate(c, direct_vm, case, 0)
    c.finalize()
    state = c.get_state()
    assert state['result']['decisions'] == decisions
    assert state['bounds'] == [enumerated(answer(case, i)['rows']) for i in range(2)]
    for i in range(2):
        with direct_vm.expect_revert('Endpoint already adjudicated'): c.adjudicate(i)
        assert c.get_state() == state
    with direct_vm.expect_revert('Family already finalized'): c.finalize()
    assert c.get_state() == state


def test_missing_arm_cannot_be_deleted_as_a_tie():
    rows = answer('ambiguity', 0)['rows']
    bounds = F['endpoint_bounds'](rows)
    assert (bounds['lower_ticks'], bounds['upper_ticks']) == (1, 37)
    assert bounds['lower_counts'] == [8, 0] and bounds['upper_counts'] == [6, 2]
    assert F['tail_ticks'](6, 0) == 4  # Dropping two pairs would falsely support.
    result = F['family_result']([bounds, F['endpoint_bounds'](answer('ambiguity', 1)['rows'])])
    assert result['lower_adjusted_ticks'] == [2, 8]
    assert result['upper_adjusted_ticks'] == [37, 16]
    assert result['decisions'] == ['REVIEW', 'REVIEW']


@pytest.mark.parametrize('arm,label', [('control', 'PASS'), ('control', 'UNKNOWN'), ('treatment', 'FAIL'), ('treatment', 'UNKNOWN')])
def test_validator_requires_exact_consequential_decisions(direct_deploy, direct_vm, arm, label):
    c = deploy(direct_deploy); adjudicate(c, direct_vm, 'stepdown', 0)
    other = answer(); other['rows'][0][arm] = label
    mocks(direct_vm, proposed=other)
    assert direct_vm.run_validator() is False


@pytest.mark.parametrize('audit', [{'rows': [False] + [True] * 7}, {'rows': [True] * 7}, {'rows': [1] * 8}, {'rows': [True] * 8, 'extra': True}])
def test_substantive_audit_cannot_be_bypassed(direct_deploy, direct_vm, audit):
    c = deploy(direct_deploy); adjudicate(c, direct_vm, 'stepdown', 0)
    mocks(direct_vm, audit=audit)
    assert direct_vm.run_validator() is False


def test_validators_refetch_full_report(direct_deploy, direct_vm):
    c = deploy(direct_deploy); adjudicate(c, direct_vm, 'stepdown', 0)
    mocks(direct_vm, body=b'{}')
    assert direct_vm.run_validator() is False


@pytest.mark.parametrize('change', ['missing-row', 'swapped-pairs', 'invented-quote', 'wrong-arm-quote', 'bool-label', 'null-label', 'extra-key', 'short-quote'])
def test_malformed_extraction_rolls_back(direct_deploy, direct_vm, change):
    c = deploy(direct_deploy); a = answer()
    if change == 'missing-row': a['rows'].pop()
    elif change == 'swapped-pairs': a['rows'].reverse()
    elif change == 'invented-quote': a['rows'][0]['control_quote'] = 'Fabricated direct observation of success.'
    elif change == 'wrong-arm-quote': a['rows'][0]['control_quote'] = a['rows'][0]['treatment_quote']
    elif change == 'bool-label': a['rows'][0]['control'] = True
    elif change == 'null-label': a['rows'][0]['treatment'] = None
    elif change == 'extra-key': a['confidence'] = 0.99
    else: a['rows'][0]['control_quote'] = 'The'
    mocks(direct_vm, proposed=a); before = c.get_state()
    with direct_vm.expect_revert('Invalid complete observations'): c.adjudicate(0)
    assert c.get_state() == before


@pytest.mark.parametrize('change', ['scope', 'endpoint', 'roster', 'duplicate', 'oversized', 'invalid-json'])
def test_committed_bad_source_is_rejected(direct_deploy, direct_vm, change):
    source = json.loads(record('stepdown', 0)[2])
    if change == 'scope': source['family'] = 'other-family'
    elif change == 'endpoint': source['endpoint'] = 'other-endpoint'
    elif change == 'roster': source['pairs'][0]['pair'] = 'pair-99'
    elif change == 'oversized': source['pairs'][0]['control'] = 'x' * 18001
    raw = json.dumps(source).encode()
    if change == 'duplicate': raw = b'{"family":"stepdown-family","family":"other"}'
    if change == 'invalid-json': raw = b'{'
    c = deploy(direct_deploy, bodies=[raw, record('stepdown', 1)[2]])
    mocks(direct_vm, body=raw); before = c.get_state()
    with direct_vm.expect_revert('[EXTERNAL]'): c.adjudicate(0)
    assert c.get_state() == before


@pytest.mark.parametrize('status', [404, 500])
def test_external_failure_never_stores_inference(direct_deploy, direct_vm, status):
    c = deploy(direct_deploy); mocks(direct_vm, status=status); before = c.get_state()
    with direct_vm.expect_revert('[EXTERNAL]' if status == 404 else '[TRANSIENT]'): c.adjudicate(0)
    assert c.get_state() == before


@pytest.mark.parametrize('mode,expected', [('matching-external', True), ('wrong-external', False), ('matching-transient', True), ('llm', False), ('leader-only', False)])
def test_validator_error_classification(direct_deploy, direct_vm, mode, expected):
    c = deploy(direct_deploy); adjudicate(c, direct_vm, 'stepdown', 0)
    if mode in ['matching-external', 'wrong-external']:
        mocks(direct_vm, body=b'{}')
        message = '[EXTERNAL] Report commitment mismatch' if mode == 'matching-external' else '[EXTERNAL] Wrong report scope or schema'
    elif mode == 'matching-transient':
        mocks(direct_vm, status=500); message = '[TRANSIENT] Report unavailable'
    elif mode == 'llm':
        mocks(direct_vm, proposed={}); message = '[LLM_ERROR] Invalid complete observations'
    else:
        mocks(direct_vm); message = '[TRANSIENT] Report unavailable'
    assert direct_vm.run_validator(leader_error=Exception(message)) is expected


@pytest.mark.parametrize('proposal', [None, {}, {'source': {}, 'observations': {}}, {'rows': []}])
def test_validator_rejects_forged_leader_payload(direct_deploy, direct_vm, proposal):
    c = deploy(direct_deploy); adjudicate(c, direct_vm, 'stepdown', 0)
    assert direct_vm.run_validator(leader_result=proposal) is False


@pytest.mark.parametrize('changes', [dict(endpoints=[]), dict(endpoints=['same', 'same']), dict(pairs=[['one']]*2), dict(repository='other/../repo'), dict(family='bad scope'), dict(urls=['https://evil.example/report']*2), dict(hashes=['g'*64]*2), dict(endpoints=['one','two','three','four'])])
def test_invalid_constructor(direct_deploy, direct_vm, changes):
    with direct_vm.expect_revert('[EXPECTED]'): deploy(direct_deploy, **changes)


@pytest.mark.parametrize('index', [-1, 2, 999])
def test_invalid_endpoint_rolls_back(direct_deploy, direct_vm, index):
    c = deploy(direct_deploy); before = c.get_state()
    with direct_vm.expect_revert('Unknown endpoint'): c.adjudicate(index)
    assert c.get_state() == before


def test_all_three_pair_partial_profiles_against_full_enumeration():
    for profile in itertools.product(LABELS, repeat=6):
        rows = [dict(control=profile[2*i], treatment=profile[2*i+1]) for i in range(3)]
        assert F['endpoint_bounds'](rows) == enumerated(rows)


def test_generated_larger_partial_profiles_and_witnesses():
    rng = random.Random(8128)
    for _ in range(96):
        n = rng.randrange(4, 9)
        labels = [rng.choice(LABELS[:2]) for _ in range(2*n)]
        for index in rng.sample(range(2*n), rng.randrange(0, 7)): labels[index] = 'UNKNOWN'
        rows = [dict(control=labels[2*i], treatment=labels[2*i+1]) for i in range(n)]
        assert F['endpoint_bounds'](rows) == enumerated(rows)


def test_complete_null_distributions_up_to_eight_pairs():
    for n in range(9):
        for wins in range(n+1):
            oracle = Fraction(sum(sum(coins) >= wins for coins in itertools.product([0,1], repeat=n)), 2**n)
            assert F['tail_ticks'](wins,n-wins) == oracle*256


def test_holm_decisions_all_bounded_family_vectors():
    grid = [1,2,4,8,12,13,16,32,64,128,256]
    for m in [1,2,3]:
        for ticks in itertools.product(grid, repeat=m):
            assert [x*20 <= 256 for x in F['holm_adjust'](ticks)] == stepdown_rejections(ticks)


def test_holm_bounds_cover_all_joint_completions():
    profiles = [answer('ambiguity',0)['rows'], answer('ambiguity',1)['rows']]
    bounds = [enumerated(rows) for rows in profiles]
    result = F['family_result'](bounds)
    # All attainable p-values from the four unknown arms, with the fully observed
    # second endpoint held fixed. Both final classifications must remain REVIEW.
    outcomes = [set(),set()]
    for bits in itertools.product(['FAIL','PASS'],repeat=4):
        rows = copy.deepcopy(profiles[0])
        for i in range(2): rows[6+i].update(control=bits[2*i],treatment=bits[2*i+1])
        p = enumerated(rows)['lower_ticks']
        for i,rejected in enumerate(stepdown_rejections([p,8])): outcomes[i].add(rejected)
    assert outcomes == [{False,True},{False,True}]
    assert result['decisions'] == ['REVIEW','REVIEW']


def test_all_unknown_maximum_size_stays_bounded():
    bounds = F['endpoint_bounds']([dict(control='UNKNOWN',treatment='UNKNOWN')]*8)
    assert bounds['reachable_counts'] == 45
    assert (bounds['lower_ticks'],bounds['upper_ticks']) == (1,256)


def test_live_proof_oracle_matches_exact_independent_tests():
    program = "const s=require('./scripts/scenario.cjs');console.log(JSON.stringify(Object.keys(s.cases).map(id=>{const bounds=[0,1].map(i=>s.oracle(s.statuses(id,i)));return {id,bounds,result:s.familyOracle(bounds)}})))"
    records = json.loads(subprocess.check_output(['node','-e',program],cwd=ROOT,text=True))
    for record in records:
        bounds = [enumerated(answer(record['id'],i)['rows']) for i in range(2)]
        assert record['bounds'] == bounds
        assert record['result'] == F['family_result'](bounds)
