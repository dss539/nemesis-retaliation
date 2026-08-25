#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DIR = REPO / 'docs/rules/semantics'
VOCAB = REPO / 'docs/rules/vocabulary'
ONTOLOGY = REPO / 'docs/rules/ontology'
EXPECTED = {
    'sources': 9, 'records': 13, 'sourceBacked': 9, 'withOpenQuestion': 4,
    'sourceVariants': 0, 'sourceAssertions': 25, 'conditions': 24,
    'operations': 61, 'decisions': 10, 'informationPolicies': 16,
    'costs': 2, 'targets': 5, 'openQuestionReferences': 5,
    'variantReferences': 2, 'questions': 7, 'openQuestions': 7, 'systems': 9,
    'backlogUnits': 600, 'backlogPilotCovered': 17, 'backlogSourceBlocked': 1,
}
ALLOWED_OPERATIONS = {
    'branch','change-value','choose','draw-random','end-process','evaluate-condition',
    'inspect-private','invoke-process','invoke-selected-process','move-entity','pay-cost','end-action-window',
    'place-component','play-card','remove-component','replace-target','resolve-attacks',
    'reveal','select-target','set-state','transition-zone',
}
ALLOWED_TIMING = {'before-attack-resolution','during','during-event-card-resolution','when-action-card-played','when-triggered'}
ALLOWED_PARTIAL = {'all-or-nothing-selection','if-not-possible-fallback','ordered-complete','per-sentence-continue','replacement-effect','source-conditional-steps'}
FORBIDDEN_IMPLEMENTATION_TEXT = re.compile(r'\b(?:engine\.js|data\.js|network\.js|PeerJS|DOM|WebRTC|serialization|database schema|UI widget)\b', re.IGNORECASE)


class DuplicateJsonKeyError(ValueError):
    pass


def duplicate_rejecting_hook(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonKeyError(f'duplicate JSON object key: {key}')
        result[key] = value
    return result


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=duplicate_rejecting_hook)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence_path(reference: str | None) -> Path | None:
    if not reference:
        return None
    path = reference.split(':', 1)[0]
    if not path.startswith(('docs/', 'assets/')):
        return None
    return REPO / path


def cardinality_valid(value: dict) -> bool:
    if not isinstance(value, dict) or set(value) != {'min', 'max'}:
        return False
    minimum, maximum = value['min'], value['max']
    if not isinstance(minimum, int) or isinstance(minimum, bool) or minimum < 0:
        return False
    if maximum is None:
        return True
    return isinstance(maximum, int) and not isinstance(maximum, bool) and maximum >= minimum


def validate(source_path: Path, schema_path: Path, pilots_path: Path, review_path: Path, coverage_path: Path, backlog_path: Path, *, reproducibility: bool) -> dict:
    failures: list[dict] = []
    sources_data = load(source_path)
    schema = load(schema_path)
    pilots = load(pilots_path)
    review = load(review_path)
    coverage = load(coverage_path)
    backlog = load(backlog_path)
    vocabulary = load(VOCAB / 'canonical-vocabulary.json')
    identities = load(VOCAB / 'named-component-identities.json')
    taxonomy = load(ONTOLOGY / 'taxonomy.json')
    ontology_review = load(ONTOLOGY / 'review-gates.json')

    term_ids = {item['termId'] for item in vocabulary['entries']}
    identity_ids = {item['identityObservationId'] for item in identities['records']}
    taxon_ids = {item['taxonId'] for item in taxonomy['taxa']}
    if ontology_review.get('counts', {}).get('open') != 0:
        failures.append({'check': 'ontology prerequisite gate'})

    source_rows = sources_data.get('sources') or []
    source_ids = [item.get('sourceId') for item in source_rows]
    source_by_id = {item['sourceId']: item for item in source_rows}
    if len(source_ids) != len(set(source_ids)) or any(not re.fullmatch(r'SRC-[A-Z0-9-]+', item or '') for item in source_ids):
        failures.append({'check': 'source registry IDs'})
    if source_ids != sorted(source_ids):
        failures.append({'check': 'source registry ordering'})
    authority_order = sources_data.get('authorityOrder') or []
    if authority_order != ['official-errata','official-primary','official-component-reference','source-bound-component-scan','licensed-digital-secondary','project-interpretation']:
        failures.append({'check': 'authority order'})
    authority_rank = {value: index for index, value in enumerate(authority_order)}
    for source in source_rows:
        path = REPO / source.get('path', '')
        evidence = REPO / source.get('evidenceIndexPath', '')
        if not path.is_file() or sha(path) != source.get('sha256'):
            failures.append({'check': 'source tuple', 'sourceId': source.get('sourceId')})
        if not evidence.exists() or source.get('authority') not in authority_rank:
            failures.append({'check': 'source evidence/authority', 'sourceId': source.get('sourceId')})
    if sources_data.get('counts') != {'sources': len(source_rows)}:
        failures.append({'check': 'source registry declared count'})

    required_fields = schema.get('required') or []
    schema_fields = set((schema.get('properties') or {}).keys())
    if set(required_fields) != schema_fields or schema.get('additionalProperties') is not False:
        failures.append({'check': 'semantic JSON schema closed record shape'})

    records = pilots.get('records') or []
    record_ids = [item.get('ruleId') for item in records]
    record_by_id = {item['ruleId']: item for item in records}
    if len(record_ids) != len(set(record_ids)) or any(not re.fullmatch(r'SEM-[A-Z0-9-]+', item or '') for item in record_ids):
        failures.append({'check': 'semantic rule IDs'})
    if record_ids != sorted(record_ids):
        failures.append({'check': 'semantic rule ordering'})

    question_rows = review.get('questions') or []
    question_ids = {item.get('questionId') for item in question_rows}
    if len(question_ids) != len(question_rows):
        failures.append({'check': 'semantic question IDs'})
    open_question_text = (REPO / 'docs/rules/open-questions.md').read_text(encoding='utf-8')
    for question in question_rows:
        qid = question.get('questionId')
        if not question.get('defaultProhibited') or not question.get('blocksRuleIds'):
            failures.append({'check': 'semantic question no-default/linkage', 'questionId': qid})
        if qid.startswith('OQ-') and f'### {qid} ' not in open_question_text:
            failures.append({'check': 'source open-question reference', 'questionId': qid})
        for blocked in question.get('blocksRuleIds') or []:
            if blocked not in record_by_id and not blocked.startswith('future '):
                failures.append({'check': 'semantic question blocked record', 'questionId': qid, 'blocked': blocked})

    for record in records:
        rule_id = record['ruleId']
        if set(record) != schema_fields:
            failures.append({'check': 'record schema fields', 'ruleId': rule_id, 'missing': sorted(schema_fields - set(record)), 'extra': sorted(set(record) - schema_fields)})
        if record.get('implementationBoundary') != 'implementation-neutral; no engine, UI, network, storage, or serialization mapping':
            failures.append({'check': 'implementation boundary', 'ruleId': rule_id})
        searchable = json.dumps({key:value for key,value in record.items() if key != 'implementationBoundary'}, ensure_ascii=False)
        if FORBIDDEN_IMPLEMENTATION_TEXT.search(searchable):
            failures.append({'check': 'implementation leakage', 'ruleId': rule_id})
        if record.get('termRefs') != sorted(set(record.get('termRefs') or [])) or any(item not in term_ids for item in record.get('termRefs') or []):
            failures.append({'check': 'controlled term references', 'ruleId': rule_id})
        if record.get('taxonRefs') != sorted(set(record.get('taxonRefs') or [])) or any(item not in taxon_ids for item in record.get('taxonRefs') or []):
            failures.append({'check': 'taxon references', 'ruleId': rule_id})
        if record.get('namedIdentityRefs') != sorted(set(record.get('namedIdentityRefs') or [])) or any(item not in identity_ids for item in record.get('namedIdentityRefs') or []):
            failures.append({'check': 'named identity references', 'ruleId': rule_id})

        source_assertions = record.get('sourceAssertions') or []
        assertion_ids = [item.get('assertionId') for item in source_assertions]
        assertion_set = set(assertion_ids)
        if not source_assertions or len(assertion_ids) != len(assertion_set) or any(not re.fullmatch(r'SA-[A-Z0-9-]+', item or '') for item in assertion_ids):
            failures.append({'check': 'source assertion IDs', 'ruleId': rule_id})
        used_authorities = []
        for item in source_assertions:
            source = source_by_id.get(item.get('sourceId'))
            if not source:
                failures.append({'check': 'source assertion source', 'ruleId': rule_id, 'assertionId': item.get('assertionId')})
                continue
            used_authorities.append(source['authority'])
            if not item.get('locator') or not item.get('sourceText') or item.get('textKind') not in {'verbatim','normalized-paraphrase'}:
                failures.append({'check': 'source assertion text/locator', 'ruleId': rule_id, 'assertionId': item.get('assertionId')})
            if not item.get('supportsFields') or any(field not in schema_fields for field in item.get('supportsFields') or []):
                failures.append({'check': 'source assertion supported fields', 'ruleId': rule_id, 'assertionId': item.get('assertionId')})
            evidence = evidence_path(item.get('evidenceRecord'))
            if evidence is None or not evidence.exists():
                failures.append({'check': 'source assertion evidence record', 'ruleId': rule_id, 'assertionId': item.get('assertionId'), 'evidenceRecord': item.get('evidenceRecord')})
        if used_authorities:
            expected_highest = min(used_authorities, key=lambda value: authority_rank[value])
            if record.get('authority', {}).get('highest') != expected_highest:
                failures.append({'check': 'record authority precedence', 'ruleId': rule_id, 'expected': expected_highest, 'actual': record.get('authority', {}).get('highest')})
        if record.get('authority', {}).get('interpretation') not in {'verbatim-structure','source-composed','open-alternatives'}:
            failures.append({'check': 'record interpretation level', 'ruleId': rule_id})

        timing = record.get('timing') or {}
        if timing.get('anchorTaxonId') not in taxon_ids or timing.get('relation') not in ALLOWED_TIMING or not timing.get('windowId') or not timing.get('recurrence'):
            failures.append({'check': 'timing shape', 'ruleId': rule_id})
        participants = record.get('participants') or []
        participant_ids = [item.get('participantId') for item in participants]
        participant_set = set(participant_ids)
        if len(participant_ids) != len(participant_set):
            failures.append({'check': 'participant IDs', 'ruleId': rule_id})
        for item in participants:
            if item.get('taxonId') is not None and item.get('taxonId') not in taxon_ids:
                failures.append({'check': 'participant taxon', 'ruleId': rule_id, 'participantId': item.get('participantId')})

        conditions = record.get('preconditions') or []
        condition_ids = [item.get('conditionId') for item in conditions]
        condition_set = set(condition_ids)
        if len(condition_ids) != len(condition_set):
            failures.append({'check': 'condition IDs', 'ruleId': rule_id})
        for item in conditions:
            if item.get('scope') not in {'record-precondition','operation-guard'} or item.get('expression', {}).get('operator') not in {'predicate','all','any','not','comparison'}:
                failures.append({'check': 'condition shape', 'ruleId': rule_id, 'conditionId': item.get('conditionId')})
            if not item.get('sourceAssertionIds') or any(ref not in assertion_set for ref in item.get('sourceAssertionIds') or []):
                failures.append({'check': 'condition source linkage', 'ruleId': rule_id, 'conditionId': item.get('conditionId')})

        decisions = record.get('decisions') or []
        decision_ids = [item.get('decisionId') for item in decisions]
        decision_set = set(decision_ids)
        if len(decision_ids) != len(decision_set):
            failures.append({'check': 'decision IDs', 'ruleId': rule_id})
        for item in decisions:
            if item.get('ownerRef') not in participant_set or item.get('selectionMode') not in {'player-choice','random','deterministic','unresolved'} or not cardinality_valid(item.get('cardinality')) or not isinstance(item.get('declineAllowed'), bool) or not item.get('visibility') or not item.get('options'):
                failures.append({'check': 'decision completeness', 'ruleId': rule_id, 'decisionId': item.get('decisionId')})

        information = record.get('informationPolicy') or []
        info_ids = [item.get('informationId') for item in information]
        if len(info_ids) != len(set(info_ids)):
            failures.append({'check': 'information policy IDs', 'ruleId': rule_id})
        for item in information:
            if not all(item.get(field) for field in ('subjectRef','audience','revealTrigger','secrecy')):
                failures.append({'check': 'information policy completeness', 'ruleId': rule_id, 'informationId': item.get('informationId')})

        costs = record.get('costs') or []
        cost_ids = [item.get('costId') for item in costs]
        if len(cost_ids) != len(set(cost_ids)):
            failures.append({'check': 'cost IDs', 'ruleId': rule_id})
        for item in costs:
            if item.get('payerRef') not in participant_set or item.get('resourceTermId') not in term_ids or not isinstance(item.get('quantity'), int) or item.get('quantity') < 0 or item.get('selectionDecisionRef') not in decision_set:
                failures.append({'check': 'cost completeness', 'ruleId': rule_id, 'costId': item.get('costId')})

        targets = record.get('targets') or []
        target_ids = [item.get('targetId') for item in targets]
        target_set = set(target_ids)
        if len(target_ids) != len(target_set):
            failures.append({'check': 'target IDs', 'ruleId': rule_id})
        for item in targets:
            if any(taxon not in taxon_ids for taxon in item.get('eligibleTaxonIds') or []) or not cardinality_valid(item.get('cardinality')) or item.get('selectionMode') not in {'player-choice','random','deterministic-turn-order','unresolved-when-multiple'} or not item.get('visibility'):
                failures.append({'check': 'target completeness', 'ruleId': rule_id, 'targetId': item.get('targetId')})
            selector = item.get('selectorRef')
            if selector not in participant_set and selector != 'rules-system' and not str(selector).startswith('unresolved-'):
                failures.append({'check': 'target selector', 'ruleId': rule_id, 'targetId': item.get('targetId'), 'selectorRef': selector})

        operations = record.get('operations') or []
        operation_ids = [item.get('stepId') for item in operations]
        sequences = [item.get('sequence') for item in operations]
        if len(operation_ids) != len(set(operation_ids)) or sequences != list(range(1, len(operations) + 1)) or any(not re.fullmatch(r'S\d{2}', item or '') for item in operation_ids):
            failures.append({'check': 'operation IDs/order', 'ruleId': rule_id})
        for item in operations:
            if item.get('operationType') not in ALLOWED_OPERATIONS or item.get('modality') not in {'must','may','cannot','if-able','mixed'}:
                failures.append({'check': 'operation type/modality', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            if any(ref not in assertion_set for ref in item.get('sourceAssertionIds') or []) or not item.get('sourceAssertionIds'):
                failures.append({'check': 'operation source linkage', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            if any(ref not in condition_set for ref in item.get('conditionRefs') or []):
                failures.append({'check': 'operation condition linkage', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            if item.get('decisionRef') is not None and item.get('decisionRef') not in decision_set:
                failures.append({'check': 'operation decision linkage', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            if item.get('targetRef') is not None and item.get('targetRef') not in target_set:
                failures.append({'check': 'operation target linkage', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            if item.get('invokeRuleId') is not None and item.get('invokeRuleId') not in record_by_id:
                failures.append({'check': 'operation invoked rule linkage', 'ruleId': rule_id, 'stepId': item.get('stepId'), 'invokeRuleId': item.get('invokeRuleId')})
            repeat = item.get('repeat') or {}
            if repeat.get('untilConditionRef') and repeat['untilConditionRef'] not in condition_set:
                failures.append({'check': 'operation repeat condition linkage', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            for transition_key in ('transition','valueChange'):
                payload = item.get(transition_key) or {}
                for value in payload.values():
                    if isinstance(value, str) and value.startswith('tax.') and value not in taxon_ids:
                        failures.append({'check': 'operation ontology reference', 'ruleId': rule_id, 'stepId': item.get('stepId'), 'value': value})

        partial = record.get('partialResolution') or {}
        if partial.get('policy') not in ALLOWED_PARTIAL or not partial.get('unit') or not partial.get('onImpossible'):
            failures.append({'check': 'partial-resolution completeness', 'ruleId': rule_id})
        if not record.get('duration') or not record.get('stacking'):
            failures.append({'check': 'duration/stacking completeness', 'ruleId': rule_id})

        unresolved = record.get('unresolvedQuestionRefs') or []
        if any(item not in question_ids for item in unresolved) or len(unresolved) != len(set(unresolved)):
            failures.append({'check': 'unresolved question linkage', 'ruleId': rule_id})
        if (record.get('status') == 'source-backed-with-open-question') != bool(unresolved):
            failures.append({'check': 'record status/question consistency', 'ruleId': rule_id})
        for variant in record.get('sourceVariants') or []:
            if variant.get('sourceId') not in source_by_id or not all(variant.get(field) for field in ('variantId','difference','resolution')):
                failures.append({'check': 'source variant completeness', 'ruleId': rule_id})

    # High-risk pilot fidelity invariants.
    search = record_by_id.get('SEM-ACT-SEARCH-001') or {}
    search_text = json.dumps(search, ensure_ascii=False)
    if 'bottom of its respective deck' not in search_text or 'unchosen Items must not be revealed' not in search_text:
        failures.append({'check': 'Search bottom/private fidelity'})
    duck = record_by_id.get('SEM-REACTION-DUCK-001') or {}
    if duck.get('ruleKind') != 'reaction' or 'SEM-Q-001' not in duck.get('unresolvedQuestionRefs', []):
        failures.append({'check': 'Reaction replacement ambiguity fidelity'})
    hatching = record_by_id.get('SEM-EVENT-HATCHING-001') or {}
    if hatching.get('partialResolution', {}).get('policy') != 'per-sentence-continue' or 'OQ-009' not in hatching.get('unresolvedQuestionRefs', []):
        failures.append({'check': 'Event partial/Nest ambiguity fidelity'})
    semantic_relation_ids = set(ontology_review.get('deferredSemanticRelationIds') or [])
    if semantic_relation_ids != {'rel.phase-part-of-round','rel.round-has-phase','rel.precedes','rel.follows','rel.turn-occurs-in-phase','rel.phase-has-turn','rel.process-has-timing-window','rel.decision-owned-by','rel.owns-decision','rel.information-visible-to','rel.transition-from','rel.transition-to'}:
        failures.append({'check': 'semantic relation handoff'})

    actual_counts = {
        'sources': len(source_rows), 'records': len(records),
        'sourceBacked': sum(item.get('status') == 'source-backed' for item in records),
        'withOpenQuestion': sum(item.get('status') == 'source-backed-with-open-question' for item in records),
        'sourceVariants': sum(item.get('status') == 'source-variant' for item in records),
        'sourceAssertions': sum(len(item.get('sourceAssertions') or []) for item in records),
        'conditions': sum(len(item.get('preconditions') or []) for item in records),
        'operations': sum(len(item.get('operations') or []) for item in records),
        'decisions': sum(len(item.get('decisions') or []) for item in records),
        'informationPolicies': sum(len(item.get('informationPolicy') or []) for item in records),
        'costs': sum(len(item.get('costs') or []) for item in records),
        'targets': sum(len(item.get('targets') or []) for item in records),
        'openQuestionReferences': sum(len(item.get('unresolvedQuestionRefs') or []) for item in records),
        'variantReferences': sum(len(item.get('sourceVariants') or []) for item in records),
        'questions': len(question_rows), 'openQuestions': review.get('counts', {}).get('open'),
        'systems': len(coverage.get('systems') or []),
        'backlogUnits': len(backlog.get('units') or []),
        'backlogPilotCovered': sum(item.get('status') == 'pilot-covered' for item in backlog.get('units') or []),
        'backlogSourceBlocked': sum(item.get('status') == 'source-blocked' for item in backlog.get('units') or []),
    }
    if actual_counts != EXPECTED:
        failures.append({'check': 'hard-coded semantic pilot counts', 'expected': EXPECTED, 'actual': actual_counts})
    expected_pilot_counts = {key: actual_counts[key] for key in ('records','sourceBacked','withOpenQuestion','sourceVariants','sourceAssertions','conditions','operations','decisions','informationPolicies','costs','targets','openQuestionReferences','variantReferences')}
    if pilots.get('counts') != expected_pilot_counts or sources_data.get('counts') != {'sources': 9} or review.get('counts') != {'questions':7,'officialClarificationPreferred':6,'sourceAmbiguitiesIntroducedByPilot':1,'resolved':0,'open':7} or coverage.get('counts') != {'systems':9,'pilotRecords':13,'fullBaseSemanticCoverageClaimed':False}:
        failures.append({'check': 'declared semantic counts'})
    covered_rule_ids = [rule_id for system in coverage.get('systems') or [] for rule_id in system.get('ruleIds') or []]
    if set(covered_rule_ids) != set(record_ids) or len(covered_rule_ids) != len(set(covered_rule_ids)) or coverage.get('counts', {}).get('fullBaseSemanticCoverageClaimed') is not False:
        failures.append({'check': 'semantic pilot coverage projection'})

    backlog_units = backlog.get('units') or []
    backlog_ids = [item.get('semanticUnitId') for item in backlog_units]
    if len(backlog_ids) != len(set(backlog_ids)) or any(not item for item in backlog_ids):
        failures.append({'check': 'semantic backlog unit IDs'})
    allowed_backlog_status = {'pending','pilot-covered','source-blocked'}
    for item in backlog_units:
        path = REPO / item.get('sourcePath', '')
        if not path.exists() or item.get('status') not in allowed_backlog_status or not item.get('channel') or not item.get('sourceLocator'):
            failures.append({'check': 'semantic backlog source/status', 'semanticUnitId': item.get('semanticUnitId')})
        if any(rule_id not in record_by_id for rule_id in item.get('pilotRuleIds') or []):
            failures.append({'check': 'semantic backlog pilot linkage', 'semanticUnitId': item.get('semanticUnitId')})
        if (item.get('status') == 'pilot-covered') != bool(item.get('pilotRuleIds')):
            failures.append({'check': 'semantic backlog status/link consistency', 'semanticUnitId': item.get('semanticUnitId')})
    blocked_units = [item for item in backlog_units if item.get('status') == 'source-blocked']
    if len(blocked_units) != 1 or not blocked_units[0].get('sourcePath','').endswith('missionTaskDeck-023.png') or 'exact-source-operative-span' not in blocked_units[0].get('blockers',[]):
        failures.append({'check': 'semantic backlog inherited source blocker'})
    expected_backlog_channels = {'card-reference-source-tuple':350,'interpreted-rule-record':54,'intruder-help-instruction':18,'objective-help-unit':45,'official-faq-unit':28,'room-help-entry':25,'rulebook-visual-obligation':80}
    expected_backlog_status = {'pending':582,'pilot-covered':17,'source-blocked':1}
    if backlog.get('counts') != {'units':600,'byChannel':expected_backlog_channels,'byStatus':expected_backlog_status}:
        failures.append({'check': 'semantic backlog declared counts'})

    if reproducibility:
        builds = []
        for seed in ('1','777'):
            with tempfile.TemporaryDirectory(prefix=f'semantic-rebuild-{seed}-') as temp_dir:
                env = {**os.environ, 'LC_ALL':'C', 'TZ':'UTC', 'PYTHONHASHSEED':seed}
                run = subprocess.run(['python3', str(REPO / 'scripts/build_semantic_pilots.py'), '--output-dir', temp_dir], cwd=REPO, env=env, check=False, capture_output=True, text=True)
                if run.returncode != 0:
                    failures.append({'check': 'semantic rebuild execution', 'seed': seed, 'stderr': run.stderr})
                    continue
                backlog_run = subprocess.run(['python3', str(REPO / 'scripts/build_semantic_backlog.py'), '--output', str(Path(temp_dir) / 'backlog.json')], cwd=REPO, env=env, check=False, capture_output=True, text=True)
                if backlog_run.returncode != 0:
                    failures.append({'check': 'semantic backlog rebuild execution', 'seed': seed, 'stderr': backlog_run.stderr})
                    continue
                hashes = {}
                for name, tracked in [('source-registry.json',source_path),('semantic-rule.schema.json',schema_path),('pilots.json',pilots_path),('review-gates.json',review_path),('coverage.json',coverage_path),('backlog.json',backlog_path)]:
                    rebuilt = Path(temp_dir) / name
                    hashes[name] = sha(rebuilt) if rebuilt.is_file() else None
                    if not rebuilt.is_file() or hashes[name] != sha(tracked):
                        failures.append({'check': 'semantic reproducibility', 'seed': seed, 'file': name})
                builds.append(hashes)
        if len(builds) == 2 and builds[0] != builds[1]:
            failures.append({'check': 'semantic hash-seed reproducibility'})

    return {'schemaVersion':1,'passed':not failures,'checks':actual_counts,'failureCount':len(failures),'failures':failures}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-registry', type=Path, default=DIR/'source-registry.json')
    parser.add_argument('--schema', type=Path, default=DIR/'semantic-rule.schema.json')
    parser.add_argument('--pilots', type=Path, default=DIR/'pilots.json')
    parser.add_argument('--review-gates', type=Path, default=DIR/'review-gates.json')
    parser.add_argument('--coverage', type=Path, default=DIR/'coverage.json')
    parser.add_argument('--backlog', type=Path, default=DIR/'backlog.json')
    parser.add_argument('--skip-reproducibility', action='store_true')
    parser.add_argument('--report', action='store_true')
    args = parser.parse_args()
    try:
        report = validate(args.source_registry,args.schema,args.pilots,args.review_gates,args.coverage,args.backlog,reproducibility=not args.skip_reproducibility)
    except (DuplicateJsonKeyError,json.JSONDecodeError) as error:
        report = {'schemaVersion':1,'passed':False,'checks':{},'failureCount':1,'failures':[{'check':'strict JSON parsing','error':str(error)}]}
    if args.report and args.pilots.resolve() == (DIR/'pilots.json').resolve():
        (DIR/'validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
