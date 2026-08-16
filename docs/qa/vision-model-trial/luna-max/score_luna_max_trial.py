#!/usr/bin/env python3
import collections
import difflib
import hashlib
import json
import math
import re
import statistics
from pathlib import Path

ROOT = Path('/home/smithers/nemesis-retaliation')
TRIAL = ROOT / 'docs/qa/vision-model-trial/luna-max'
REQUIRED = {
    'orientation', 'componentType', 'title', 'typeLine', 'body', 'footer',
    'standaloneSymbols', 'visibleOtherText', 'layoutNotes', 'categoryProposal',
    'filenameProposal', 'sidecarCandidate', 'uncertainties', 'confidence', 'decision'
}


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def norm(value):
    if value is None:
        return ''
    return re.sub(r'\s+', ' ', str(value)).strip()


def ratio(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def percentile(values, p):
    vals = sorted(values)
    if not vals:
        return 0
    if len(vals) == 1:
        return vals[0]
    pos = (len(vals) - 1) * p
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return vals[lo]
    return vals[lo] * (hi - pos) + vals[hi] * (pos - lo)


def canonical_ids():
    glossary = (ROOT / 'docs/rules/icon-glossary.md').read_text()
    return set(re.findall(r'^- \*\*([A-Za-z][A-Za-z0-9]*)\*\*\s+—', glossary, re.M))


def collect_icons(value, known):
    result = []
    if isinstance(value, dict):
        for v in value.values():
            result.extend(collect_icons(v, known))
    elif isinstance(value, list):
        for v in value:
            result.extend(collect_icons(v, known))
    elif isinstance(value, str):
        if value in known:
            result.append(value)
        result.extend(x for x in re.findall(r'\[([A-Za-z][A-Za-z0-9]*)\]', value) if x in known)
    return result


def multiset_f1(expected, actual):
    e, a = collections.Counter(expected), collections.Counter(actual)
    if not e and not a:
        return 1.0
    overlap = sum((e & a).values())
    precision = overlap / sum(a.values()) if a else 0
    recall = overlap / sum(e.values()) if e else 0
    return 2 * precision * recall / (precision + recall) if precision + recall else 0


def sidecar_score(gold, candidate):
    if not isinstance(candidate, dict):
        return 0.0, {'keyF1': 0, 'valueMean': 0}
    gkeys, akeys = set(gold), set(candidate)
    if not gkeys and not akeys:
        key_f1 = 1.0
    else:
        overlap = len(gkeys & akeys)
        precision = overlap / len(akeys) if akeys else 0
        recall = overlap / len(gkeys) if gkeys else 0
        key_f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
    value_scores = [ratio(gold[k], candidate.get(k)) for k in gold]
    value_mean = statistics.mean(value_scores) if value_scores else 1.0
    return 10 * key_f1 + 10 * value_mean, {'keyF1': key_f1, 'valueMean': value_mean}


def score_card(case, output, known):
    gold_path = ROOT / case['goldSidecar']
    if sha256(gold_path) != case['goldSidecarSha256']:
        raise RuntimeError(f"Gold drift for {case['id']}")
    gold = json.loads(gold_path.read_text())
    schema = 5.0 if REQUIRED.issubset(output) else 0.0
    expected_title = case['expected'].get('title')
    # c06's frozen null means no canonical title gold was available; do not
    # penalize or reward a visible header that is outside the minimal sidecar.
    title = 5.0 if expected_title is None or norm(output.get('title')) == norm(expected_title) else 0.0
    expected_text = '\n'.join(f"{k}:{gold[k]}" for k in ('typeLine', 'body') if k in gold)
    actual_text = '\n'.join(f"{k}:{output.get(k)}" for k in ('typeLine', 'body') if k in gold)
    text_ratio = ratio(expected_text, actual_text)
    text = 40.0 * text_ratio
    expected_icons = collect_icons(gold, known)
    actual_icons = collect_icons({
        'typeLine': output.get('typeLine'),
        'body': output.get('body'),
        'standaloneSymbols': output.get('standaloneSymbols')
    }, known)
    icon_f1 = multiset_f1(expected_icons, actual_icons)
    icons = 20.0 * icon_f1
    sidecar, sidecar_detail = sidecar_score(gold, output.get('sidecarCandidate'))
    decision = 10.0 if output.get('decision') == case['expected']['decision'] else 0.0
    components = {
        'schema': round(schema, 3),
        'title': round(title, 3),
        'text': round(text, 3),
        'icons': round(icons, 3),
        'sidecar': round(sidecar, 3),
        'decision': round(decision, 3),
    }
    return {
        'score': round(sum(components.values()), 3),
        'max': 100,
        'components': components,
        'diagnostics': {
            'textRatio': round(text_ratio, 6),
            'expectedIcons': expected_icons,
            'actualIcons': actual_icons,
            'iconF1': round(icon_f1, 6),
            'sidecarKeyF1': round(sidecar_detail['keyF1'], 6),
            'sidecarValueMean': round(sidecar_detail['valueMean'], 6),
        }
    }


def main():
    sample = json.loads((TRIAL / 'sample.json').read_text())
    manual = json.loads((TRIAL / 'manual-scores.json').read_text())['cases']
    known = canonical_ids()
    case_scores = {}
    latencies = []
    failures = []
    session_ids = []
    for case in sample['cases']:
        source = ROOT / case['source']
        if sha256(source) != case['sourceSha256']:
            raise RuntimeError(f"Source drift for {case['id']}")
        run_path = TRIAL / 'runs' / f"{case['id']}.json"
        if not run_path.exists():
            failures.append({'caseId': case['id'], 'reason': 'missing run'})
            continue
        run = json.loads(run_path.read_text())
        if run.get('provider') != sample['provider'] or run.get('model') != sample['model'] or run.get('reasoning') != sample['reasoning']:
            failures.append({'caseId': case['id'], 'reason': 'route mismatch'})
            continue
        output = run.get('parsedJson')
        if run.get('returnCode') != 0 or not isinstance(output, dict):
            failures.append({'caseId': case['id'], 'reason': 'run or parse failure'})
            continue
        latencies.append(run['durationSeconds'])
        if run.get('sessionId'):
            session_ids.append(run['sessionId'])
        if case['tier'] == 'human-approved-card':
            result = score_card(case, output, known)
            result['scoring'] = 'programmatic'
        else:
            m = manual[case['id']]
            result = {'score': m['score'], 'max': m['max'], 'components': m['criteria'], 'scoring': 'manual'}
            if m.get('criticalFailure'):
                result['criticalFailure'] = m['criticalFailure']
        result['tier'] = case['tier']
        result['durationSeconds'] = run['durationSeconds']
        result['decision'] = output.get('decision')
        result['overallConfidence'] = (output.get('confidence') or {}).get('overall')
        case_scores[case['id']] = result

    scores = [v['score'] for v in case_scores.values()]
    approved = [v['score'] for v in case_scores.values() if v['tier'] == 'human-approved-card']
    summary = {
        'schemaVersion': 1,
        'provider': sample['provider'],
        'model': sample['model'],
        'reasoning': sample['reasoning'],
        'nativeImageAttachment': True,
        'auxiliaryVisionUsed': False,
        'casesRequested': len(sample['cases']),
        'casesScored': len(case_scores),
        'failures': failures,
        'uniqueSessionIds': len(set(session_ids)),
        'caseScores': case_scores,
        'aggregate': {
            'allCasesMean': round(statistics.mean(scores), 3) if scores else None,
            'allCasesMedian': round(statistics.median(scores), 3) if scores else None,
            'humanApprovedCardsMean': round(statistics.mean(approved), 3) if approved else None,
            'humanApprovedCardsMedian': round(statistics.median(approved), 3) if approved else None,
        },
        'latencySeconds': {
            'totalSequentialEquivalent': round(sum(latencies), 3),
            'mean': round(statistics.mean(latencies), 3),
            'median': round(statistics.median(latencies), 3),
            'p95': round(percentile(latencies, 0.95), 3),
            'min': round(min(latencies), 3),
            'max': round(max(latencies), 3),
        } if latencies else {},
        'criticalFailures': [
            {'caseId': cid, 'failure': v['criticalFailure']}
            for cid, v in case_scores.items() if v.get('criticalFailure')
        ],
    }
    (TRIAL / 'scores.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
