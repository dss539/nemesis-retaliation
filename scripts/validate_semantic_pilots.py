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
    'sources': 10, 'semanticNodes': 22, 'records': 73, 'sourceBacked': 64, 'withOpenQuestion': 9,
    'sourceVariants': 0, 'sourceAssertions': 155, 'conditions': 221,
    'operations': 281, 'decisions': 48, 'informationPolicies': 80,
    'costs': 3, 'targets': 20, 'openQuestionReferences': 10,
    'variantReferences': 2, 'questions': 11, 'openQuestions': 11, 'systems': 18,
    'conflicts': 8, 'unresolvedConflicts': 4,
    'roomIconDenotations': 112,
    'backlogUnits': 600, 'backlogPilotCovered': 71, 'backlogSourceBlocked': 1,
}
PINNED_HELP_SOURCE_HASHES = {
    'docs/rules/source-extraction/intruder-help-sheet.json': 'e07f2703a6ad1b49c06389f79d3b1ffd6f5fd1d98604bf14b405fee49d9679e6',
    'docs/rules/source-extraction/room-help-sheet.json': 'ad3d6bb66de939fe1036ecca3fc8d8d9b41fe41e1065f7bd9611df8263480177',
    'docs/rules/source-extraction/room-help-sheet-source-fidelity-lock.json': '27c23c1c885e2ab851bef0bfb43b7471ea862af9d0308f9b3e70026320b4d8b4',
}
ALLOWED_OPERATIONS = {
    'branch','change-value','choose','draw-random','end-process','evaluate-condition',
    'inspect-private','invoke-process','invoke-selected-process','move-entity','pay-cost','end-action-window',
    'place-component','play-card','remove-component','replace-target','resolve-attacks',
    'reveal','select-target','set-state','transition-zone','shuffle','resolve-open-alternative',
}
ALLOWED_TIMING = {'before-attack-resolution','during','during-event-card-resolution','when-action-card-played','when-triggered'}
ALLOWED_PARTIAL = {'all-or-nothing-selection','if-not-possible-fallback','ordered-complete','per-sentence-continue','replacement-effect','source-conditional-steps','per-effect-check','source-limited-components'}
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


def validate(source_path: Path, schema_path: Path, semantic_vocabulary_path: Path, room_icon_path: Path, pilots_path: Path, review_path: Path, contradictions_path: Path, coverage_path: Path, backlog_path: Path, *, reproducibility: bool) -> dict:
    failures: list[dict] = []
    sources_data = load(source_path)
    schema = load(schema_path)
    semantic_vocabulary = load(semantic_vocabulary_path)
    room_icon_data = load(room_icon_path)
    pilots = load(pilots_path)
    review = load(review_path)
    contradictions = load(contradictions_path)
    coverage = load(coverage_path)
    backlog = load(backlog_path)
    vocabulary = load(VOCAB / 'canonical-vocabulary.json')
    identities = load(VOCAB / 'named-component-identities.json')
    taxonomy = load(ONTOLOGY / 'taxonomy.json')
    ontology_review = load(ONTOLOGY / 'review-gates.json')

    term_ids = {item['termId'] for item in vocabulary['entries']}
    identity_ids = {item['identityObservationId'] for item in identities['records']}
    taxon_ids = {item['taxonId'] for item in taxonomy['taxa']}
    semantic_node_rows = semantic_vocabulary.get('nodes') or []
    semantic_node_ids = {item.get('semanticNodeId') for item in semantic_node_rows}
    if ontology_review.get('counts', {}).get('open') != 0:
        failures.append({'check': 'ontology prerequisite gate'})
    for relative_path, expected_hash in PINNED_HELP_SOURCE_HASHES.items():
        path = REPO / relative_path
        if not path.is_file() or sha(path) != expected_hash:
            failures.append({'check': 'pinned Help source hash', 'path': relative_path})
    if len(semantic_node_ids) != len(semantic_node_rows) or any(not re.fullmatch(r'sem\.[a-z0-9.-]+', item or '') for item in semantic_node_ids):
        failures.append({'check': 'semantic node IDs'})
    semantic_kind_counts = {kind: sum(item.get('kind') == kind for item in semantic_node_rows) for kind in ('state-value','zone','position','visibility-scope')}
    if semantic_vocabulary.get('counts') != {'nodes':22,'stateValues':15,'zones':2,'positions':2,'visibilityScopes':3} or semantic_kind_counts != {'state-value':15,'zone':2,'position':2,'visibility-scope':3}:
        failures.append({'check': 'semantic node counts'})
    for item in semantic_node_rows:
        if not item.get('label') or not item.get('sourceEvidence') or any((evidence_path(ref) is None or not evidence_path(ref).exists()) for ref in item.get('sourceEvidence') or []):
            failures.append({'check': 'semantic node provenance', 'semanticNodeId': item.get('semanticNodeId')})

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
        if not question.get('defaultProhibited') or not (question.get('blocksRuleIds') or question.get('plannedRuleIds')):
            failures.append({'check': 'semantic question no-default/linkage', 'questionId': qid})
        if qid.startswith('OQ-') and f'### {qid} ' not in open_question_text:
            failures.append({'check': 'source open-question reference', 'questionId': qid})
        for blocked in question.get('blocksRuleIds') or []:
            if blocked not in record_by_id:
                failures.append({'check': 'semantic question blocked record', 'questionId': qid, 'blocked': blocked})
        for planned in question.get('plannedRuleIds') or []:
            if not re.fullmatch(r'SEM-[A-Z0-9-]+', planned) or planned in record_by_id:
                failures.append({'check': 'semantic question planned record', 'questionId': qid, 'planned': planned})
        alternatives = question.get('alternatives') or []
        alternative_ids = [item.get('alternativeId') for item in alternatives]
        if len(alternatives) < 2 or len(alternative_ids) != len(set(alternative_ids)) or any(not item.get('description') or not item.get('support') for item in alternatives):
            failures.append({'check': 'semantic question alternatives', 'questionId': qid})
        for reference in question.get('sourceEvidenceRefs') or []:
            path = evidence_path(reference)
            if path is None or not path.exists():
                failures.append({'check': 'semantic question source evidence', 'questionId': qid, 'reference': reference})

    conflict_rows = contradictions.get('conflicts') or []
    conflict_ids = [item.get('conflictId') for item in conflict_rows]
    if conflict_ids != [f'SC-{index:03d}' for index in range(1, len(conflict_rows) + 1)]:
        failures.append({'check': 'semantic conflict IDs/order'})
    for conflict in conflict_rows:
        status = conflict.get('status')
        question_id = conflict.get('questionId')
        if status not in {'resolved-by-authority','unresolved','preserved-boundary'} or not conflict.get('difference') or not conflict.get('resolution'):
            failures.append({'check': 'semantic conflict shape', 'conflictId': conflict.get('conflictId')})
        if status == 'unresolved' and question_id not in question_ids:
            failures.append({'check': 'semantic conflict question linkage', 'conflictId': conflict.get('conflictId'), 'questionId': question_id})
        if status != 'unresolved' and question_id is not None:
            failures.append({'check': 'semantic conflict resolved question drift', 'conflictId': conflict.get('conflictId')})
        if any(rule_id not in record_by_id for rule_id in conflict.get('affectedRuleIds') or []):
            failures.append({'check': 'semantic conflict rule linkage', 'conflictId': conflict.get('conflictId')})
        for reference in conflict.get('evidenceRefs') or []:
            if reference in source_by_id:
                continue
            path = evidence_path(reference)
            if path is None or not path.exists():
                failures.append({'check': 'semantic conflict evidence', 'conflictId': conflict.get('conflictId'), 'reference': reference})
    if contradictions.get('counts') != {'conflicts':8,'resolvedByAuthority':2,'unresolved':4,'preservedBoundary':2}:
        failures.append({'check': 'semantic conflict declared counts'})

    for record in records:
        rule_id = record['ruleId']
        if set(record) != schema_fields:
            failures.append({'check': 'record schema fields', 'ruleId': rule_id, 'missing': sorted(schema_fields - set(record)), 'extra': sorted(set(record) - schema_fields)})
        if record.get('schemaVersion') != 1 or record.get('recordType') != 'semantic-rule' or not isinstance(record.get('recordRevision'), int) or isinstance(record.get('recordRevision'), bool) or record.get('recordRevision', 0) < 1:
            failures.append({'check': 'record schema/version', 'ruleId': rule_id})
        if record.get('status') not in schema['properties']['status']['enum'] or record.get('ruleKind') not in schema['properties']['ruleKind']['enum'] or record.get('modality') not in {'must','may','cannot'}:
            failures.append({'check': 'record controlled facets', 'ruleId': rule_id})
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
        assertion_by_id = {item.get('assertionId'): item for item in source_assertions}
        if not source_assertions or len(assertion_ids) != len(assertion_set) or any(not re.fullmatch(r'SA-[A-Z0-9-]+', item or '') for item in assertion_ids):
            failures.append({'check': 'source assertion IDs', 'ruleId': rule_id})
        used_authorities = []
        for item in source_assertions:
            source = source_by_id.get(item.get('sourceId'))
            if not source:
                failures.append({'check': 'source assertion source', 'ruleId': rule_id, 'assertionId': item.get('assertionId')})
                continue
            used_authorities.append(source['authority'])
            if any(item.get(field) != source.get(source_field) for field, source_field in (('sourcePath','path'),('sourceSha256','sha256'),('sourceAuthority','authority'),('sourceVersion','version'))):
                failures.append({'check': 'source assertion tuple projection', 'ruleId': rule_id, 'assertionId': item.get('assertionId')})
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
            selection_ref = item.get('selectionDecisionRef')
            if item.get('payerRef') not in participant_set or item.get('resourceTermId') not in term_ids or not isinstance(item.get('quantity'), int) or item.get('quantity') < 0 or (selection_ref is not None and selection_ref not in decision_set):
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
            if any('operations' not in (assertion_by_id.get(ref) or {}).get('supportsFields', []) for ref in item.get('sourceAssertionIds') or []):
                failures.append({'check': 'operation assertion support', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            if any(ref not in condition_set for ref in item.get('conditionRefs') or []):
                failures.append({'check': 'operation condition linkage', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            if item.get('decisionRef') is not None and item.get('decisionRef') not in decision_set:
                failures.append({'check': 'operation decision linkage', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            if item.get('targetRef') is not None and item.get('targetRef') not in target_set:
                failures.append({'check': 'operation target linkage', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            if item.get('invokeRuleId') is not None and item.get('invokeRuleId') not in record_by_id:
                failures.append({'check': 'operation invoked rule linkage', 'ruleId': rule_id, 'stepId': item.get('stepId'), 'invokeRuleId': item.get('invokeRuleId')})
            if any(ref not in record_by_id for ref in item.get('dispatchRuleIds') or []):
                failures.append({'check': 'operation dispatch linkage', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            if item.get('operationType') == 'transition-zone' and (not isinstance(item.get('transition'), dict) or not item['transition'].get('from') or not item['transition'].get('to')):
                failures.append({'check': 'operation transition completeness', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            if item.get('operationType') == 'change-value' and not isinstance(item.get('valueChange'), dict):
                failures.append({'check': 'operation value-change completeness', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            if item.get('operationType') == 'pay-cost' and item.get('objectRef') not in set(cost_ids):
                failures.append({'check': 'operation cost linkage', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            if isinstance(item.get('objectRef'), str) and item['objectRef'].startswith('sem.') and item['objectRef'] not in semantic_node_ids and item['objectRef'] not in question_ids:
                failures.append({'check': 'operation semantic-node reference', 'ruleId': rule_id, 'stepId': item.get('stepId'), 'value': item['objectRef']})
            repeat = item.get('repeat') or {}
            if repeat.get('untilConditionRef') and repeat['untilConditionRef'] not in condition_set:
                failures.append({'check': 'operation repeat condition linkage', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            for transition_key in ('transition','valueChange'):
                payload = item.get(transition_key) or {}
                for value in payload.values():
                    if isinstance(value, str) and value.startswith('tax.') and value not in taxon_ids:
                        failures.append({'check': 'operation ontology reference', 'ruleId': rule_id, 'stepId': item.get('stepId'), 'value': value})
                    if isinstance(value, str) and value.startswith('sem.') and value not in semantic_node_ids:
                        failures.append({'check': 'operation semantic-node reference', 'ruleId': rule_id, 'stepId': item.get('stepId'), 'value': value})
        used_decisions = {item.get('decisionRef') for item in operations if item.get('decisionRef')} | {item.get('selectionDecisionRef') for item in costs if item.get('selectionDecisionRef')}
        if used_decisions != decision_set:
            failures.append({'check': 'decision usage closure', 'ruleId': rule_id, 'unused': sorted(decision_set-used_decisions), 'unknown': sorted(used_decisions-decision_set)})

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
            if variant.get('sourceId') not in source_by_id or variant.get('sourceAssertionId') not in assertion_set or not all(variant.get(field) for field in ('variantId','difference','resolution')):
                failures.append({'check': 'source variant completeness', 'ruleId': rule_id})

    # High-risk pilot fidelity invariants.
    search = record_by_id.get('SEM-ACT-SEARCH-001') or {}
    search_operations = {item.get('stepId'): item for item in search.get('operations') or []}
    search_information = search.get('informationPolicy') or []
    if (search_operations.get('S04', {}).get('transition') or {}).get('to') != 'tax.scaffold.zone.deck' or (search_operations.get('S04', {}).get('transition') or {}).get('positionRef') != 'sem.position.deck-bottom' or not any('unchosen Items must not be revealed' in item.get('secrecy','') for item in search_information):
        failures.append({'check': 'Search bottom/private fidelity'})
    duck = record_by_id.get('SEM-REACTION-DUCK-001') or {}
    if duck.get('ruleKind') != 'reaction' or 'SEM-Q-001' not in duck.get('unresolvedQuestionRefs', []):
        failures.append({'check': 'Reaction replacement ambiguity fidelity'})
    move = record_by_id.get('SEM-ACT-MOVE-001') or {}
    explore = record_by_id.get('SEM-ACT-EXPLORE-001') or {}
    if 'SEM-Q-003' not in move.get('unresolvedQuestionRefs', []) or 'SEM-Q-002' not in explore.get('unresolvedQuestionRefs', []) or not any(item.get('operationType') == 'resolve-open-alternative' for item in explore.get('operations') or []):
        failures.append({'check': 'Movement/Exploration ambiguity fidelity'})
    passing = record_by_id.get('SEM-RT-007') or {}
    if not any(item.get('operationType') == 'end-action-window' for item in passing.get('operations') or []) or any(item.get('operationType') == 'end-process' for item in passing.get('operations') or []):
        failures.append({'check': 'Pass Turn-end effect fidelity'})
    intruder_help = load(REPO/'docs/rules/source-extraction/intruder-help-sheet.json')
    help_rows = {}
    for side in intruder_help['sides']:
        for column in side['columns']:
            for row in column['rows']:
                help_rows[row['occurrenceId']] = (side['sideId'], row['printedInstruction'], column['columnId'])
        row = side['bottomRow']
        help_rows[row['occurrenceId']] = (side['sideId'], row['printedInstruction'], 'bag-development')
    expected_help_rule_ids = {f'SEM-IH-{occurrence_id}' for occurrence_id in help_rows}
    actual_help_rule_ids = {rule_id for rule_id in record_by_id if rule_id.startswith('SEM-IH-')}
    if actual_help_rule_ids != expected_help_rule_ids:
        failures.append({'check': 'Intruder Help semantic closure'})
    for occurrence_id, (side, printed_text, context) in help_rows.items():
        rule_id = f'SEM-IH-{occurrence_id}'
        item = record_by_id.get(rule_id) or {}
        assertions = {row.get('assertionId'): row for row in item.get('sourceAssertions') or []}
        source_assertion = assertions.get(f'SA-{occurrence_id}') or {}
        expected_source = 'SRC-INTRUDER-HELP-QA' if side == 'queen-alive' else 'SRC-INTRUDER-HELP-QD'
        if source_assertion.get('sourceText') != printed_text or source_assertion.get('textKind') != 'verbatim' or source_assertion.get('sourceId') != expected_source:
            failures.append({'check': 'Intruder Help verbatim semantic projection', 'occurrenceId': occurrence_id})
        condition_text = json.dumps(item.get('preconditions') or [], ensure_ascii=False)
        if 'drawn token discriminator is ' not in condition_text:
            failures.append({'check': 'Intruder Help trigger discriminator', 'occurrenceId': occurrence_id})
        operations = item.get('operations') or []
        if context == 'corridor':
            for op in operations:
                if op.get('operationType') == 'place-component' and '6-equivalent Corridor capacity' not in (op.get('notes') or ''):
                    failures.append({'check': 'Intruder Help Corridor capacity', 'occurrenceId': occurrence_id})
                if op.get('operationType') == 'transition-zone' and (op.get('transition') or {}).get('positionRef') is not None:
                    failures.append({'check': 'Intruder Help non-Bag pile ordering', 'occurrenceId': occurrence_id})
        if context == 'room' and occurrence_id.endswith(('R-01','R-02')) and not any(op.get('invokeRuleId') == 'SEM-INT-004' for op in operations):
            failures.append({'check': 'Intruder Help Room Surprise Attack', 'occurrenceId': occurrence_id})
        if occurrence_id in {'QA-C-02','QD-C-02'}:
            placement = next((op for op in operations if op.get('operationType') == 'place-component'), {})
            repeat = placement.get('repeat') or {}
            if set(repeat) < {'adultCount','droneCount','corridorCapacityEquivalentLimit','tokenFaceResolutions'} or repeat.get('tokenFaceResolutions') != {'2':{'adultCount':2,'droneCount':0},'3':{'adultCount':3,'droneCount':0},'4':{'adultCount':4,'droneCount':0},'1+1':{'adultCount':1,'droneCount':1},'2+1':{'adultCount':2,'droneCount':1},'3+1':{'adultCount':3,'droneCount':1}}:
                failures.append({'check': 'Intruder Help token-back count/color', 'occurrenceId': occurrence_id})
    expected_help_dispatch = {'SEM-IH-QA-B-01','SEM-IH-QD-B-01','SEM-IH-QA-B-02','SEM-IH-QD-B-02','SEM-IH-QA-B-03','SEM-IH-QD-B-03','SEM-IH-QA-BOTTOM-01','SEM-IH-QD-BOTTOM-01'}
    bag_dispatch = {op.get('invokeRuleId') for op in (record_by_id.get('SEM-RT-011') or {}).get('operations') or [] if op.get('invokeRuleId')}
    if bag_dispatch != expected_help_dispatch:
        failures.append({'check': 'Bag Development exact Queen-side Help dispatch', 'actual': sorted(bag_dispatch)})
    expected_room_dispatch = {'SEM-IH-QA-R-01','SEM-IH-QA-R-02','SEM-IH-QD-R-01','SEM-IH-QD-R-02'}
    for source_rule in ('SEM-NOISE-001','SEM-ROOM-10'):
        dispatches={ref for op in (record_by_id.get(source_rule) or {}).get('operations') or [] for ref in op.get('dispatchRuleIds') or []}
        if dispatches != expected_room_dispatch:
            failures.append({'check': 'Room-context exact Help dispatch', 'ruleId': source_rule, 'actual': sorted(dispatches)})
    room_help = load(REPO/'docs/rules/source-extraction/room-help-sheet.json')
    def room_key(value):
        return re.sub(r'[^a-z0-9]+','-',value.lower()).strip('-')
    room_identity_by_key = {}
    for identity in identities['records']:
        if 'room-title' in identity.get('observedRoleCounts', {}):
            for label in identity.get('observedLabels') or []:
                room_identity_by_key.setdefault(room_key(label), set()).add(identity['identityObservationId'])
    expected_room_ids = {f'SEM-ROOM-{entry["printedNumber"]}' for entry in room_help['entries']}
    actual_room_ids = {rule_id for rule_id in record_by_id if re.fullmatch(r'SEM-ROOM-\d{2}', rule_id)}
    if actual_room_ids != expected_room_ids or 'SEM-USE-ROOM-001' not in record_by_id:
        failures.append({'check': 'Room Help semantic closure'})
    use_room_text = json.dumps(record_by_id.get('SEM-USE-ROOM-001') or {}, ensure_ascii=False)
    shelter_text = json.dumps(record_by_id.get('SEM-ROOM-02-SECURE') or {}, ensure_ascii=False)
    if 'occupied Room has no Malfunction marker' not in use_room_text or 'sem.state.room.always-secured' not in shelter_text or 'permanent status' not in shelter_text:
        failures.append({'check': 'Use Room/Shelter global constraints'})
    for entry in room_help['entries']:
        number = entry['printedNumber']
        item = record_by_id.get(f'SEM-ROOM-{number}') or {}
        assertion_rows = item.get('sourceAssertions') or []
        effect_id = 'SA-ROOM01-1' if number == '01' else f'SA-ROOM-{number}-E'
        effect_assertion = next((row for row in assertion_rows if row.get('assertionId') == effect_id), {})
        note_texts = [row.get('sourceText') for row in assertion_rows if re.fullmatch(rf'SA-ROOM-{number}-N\d{{2}}', row.get('assertionId',''))]
        if effect_assertion.get('sourceText') != entry['printedEffect'] or effect_assertion.get('textKind') != 'verbatim' or effect_assertion.get('sourceId') != 'SRC-ROOM-HELP':
            failures.append({'check': 'Room Help verbatim effect projection', 'room': number})
        if number != '01' and note_texts != entry['associatedNotes']:
            failures.append({'check': 'Room Help verbatim note projection', 'room': number})
        expected_identity = sorted(room_identity_by_key.get(room_key(entry['printedTitle']), set()))
        if not item.get('operations') or item.get('namedIdentityRefs') != expected_identity or len(expected_identity) != 1:
            failures.append({'check': 'Room Help semantic operation/identity', 'room': number})
    room_occurrences = {occ['occurrenceId']: occ for entry in room_help['entries'] for occ in entry['functionalIconOccurrences']}
    denotation_rows = room_icon_data.get('denotations') or []
    denotation_ids = [row.get('occurrenceId') for row in denotation_rows]
    expected_denotation_counts = {'functionalOccurrences':112,'controlledTermDenotations':107,'semanticNodeDenotations':5,'uniqueSemanticReferences':28}
    if set(denotation_ids) != set(room_occurrences) or len(denotation_ids) != len(set(denotation_ids)) or room_icon_data.get('counts') != expected_denotation_counts:
        failures.append({'check': 'Room Help icon semantic closure'})
    for row in denotation_rows:
        occurrence = room_occurrences.get(row.get('occurrenceId')) or {}
        reference = row.get('semanticReferenceId')
        valid_reference = (row.get('referenceKind') == 'controlled-term' and reference in term_ids) or (row.get('referenceKind') == 'semantic-node' and reference in semantic_node_ids)
        if not valid_reference or row.get('literalAppearance') != occurrence.get('literalAppearance') or row.get('sourceLocation') != occurrence.get('location') or row.get('mappingScope') != 'official Room Help source occurrence only':
            failures.append({'check': 'Room Help icon denotation projection', 'occurrenceId': row.get('occurrenceId')})
    denotation_by_id = {row['occurrenceId']: row['semanticReferenceId'] for row in denotation_rows}
    expected_denotation_by_id = {
        'R01-I04':'icon.fire','R03-I04':'icon.characterHealth','R05-I04':'icon.ammoToken','R05-I05':'icon.grenadeToken','R07-I04':'icon.secure','R07-I05':'icon.robot','R07-I06':'icon.robot','R08-I05':'icon.redItem','R08-I06':'icon.malfunction','R08-I07':'icon.ammoToken','R09-I05':'icon.intruder','R10-I04':'icon.noise','R11-I03':'icon.ammoToken','R13-I04':'icon.actionCard','R13-I05':'icon.oxygen','R13-I06':'icon.oxygen','R14-I01':'icon.ammoSlot','R14-I02':'icon.grenadeSlot','R14-I03':'icon.medpackSlot','R14-I04':'icon.oxygenSlot','R14-I05':'icon.lander','R15-I04':'icon.lifeSupportActive','R15-I05':'icon.lifeSupportInactive','R15-I06':'icon.fire','R16-I04':'icon.actionCard','R17-I05':'icon.robot','R18-I01':'icon.hibernatoriumActive','R18-I02':'icon.hibernatoriumActive','R19-I03':'icon.lifeSupportActive','R19-I04':'icon.lifeSupportInactive','R20-I04':'icon.computer','R20-I05':'icon.malfunction','R22-I03':'icon.lifeSupportActive','R22-I04':'icon.lifeSupportInactive','R22-I05':'icon.hibernatoriumInactive','R22-I06':'icon.hibernatoriumActive','R23-I03':'icon.lifeSupportActive','R23-I04':'icon.lifeSupportInactive','R23-I05':'icon.autodestruction','R23-I06':'icon.lifeSupportInactive','R23-I07':'icon.autodestruction','R23-I08':'icon.lifeSupportInactive','R23-I09':'icon.autodestruction','R02-I03':'sem.state.room.always-secured','R04-I04':'sem.state.room.secure-prohibited','R12-I04':'sem.state.room.secure-prohibited','R25-I01':'sem.state.room.secure-prohibited','R25-I02':'sem.state.room.malfunction-prohibited'}
    literal_expected={'bright green chamfered square containing a centered white plus sign':'icon.greenItem','gold-yellow chamfered square containing a diagonal white wrench silhouette':'icon.yellowItem','red chamfered square containing three upright white cartridge-like shapes':'icon.redItem','small cyan-blue glowing rectangular monitor-like outline with a pale inner screen and short base':'icon.computer'}
    for occurrence_id,occurrence in room_occurrences.items():
        literal_reference=literal_expected.get(occurrence.get('literalAppearance'))
        if literal_reference is not None:
            expected_denotation_by_id.setdefault(occurrence_id,literal_reference)
    if any(expected_denotation_by_id.get(occurrence_id) != reference for occurrence_id,reference in denotation_by_id.items()):
        failures.append({'check': 'independently locked Room icon denotation map'})
    if denotation_by_id.get('R08-I05') != 'icon.redItem' or denotation_by_id.get('R08-I06') != 'icon.malfunction' or denotation_by_id.get('R08-I07') != 'icon.ammoToken':
        failures.append({'check': 'Gunnery Room icon semantics'})
    room04 = record_by_id.get('SEM-ROOM-04') or {}
    if 'SEM-Q-004' not in room04.get('unresolvedQuestionRefs', []) or not any((row.get('transition') or {}).get('to') == 'tax.scaffold.zone.backpack' for row in room04.get('operations') or []):
        failures.append({'check': 'Supply Room ambiguity/storage semantics'})
    room08_text = json.dumps(record_by_id.get('SEM-ROOM-08') or {}, ensure_ascii=False)
    if 'not a Burst Action' not in room08_text or 'no Ammo token is spent' not in room08_text:
        failures.append({'check': 'Gunnery Room non-Burst/Ammo semantics'})
    if not any('kept Support Equipment to Character storage' in row.get('objectRef','') for row in (record_by_id.get('SEM-ROOM-11') or {}).get('operations') or []):
        failures.append({'check': 'Experimental Lab kept Support Equipment transition'})
    if [denotation_by_id.get(f'R14-I0{index}') for index in range(1,5)] != ['icon.ammoSlot','icon.grenadeSlot','icon.medpackSlot','icon.oxygenSlot']:
        failures.append({'check': 'Landing Zone connected-slot semantics'})
    expected_room_states = {'R02-I03':'sem.state.room.always-secured','R04-I04':'sem.state.room.secure-prohibited','R12-I04':'sem.state.room.secure-prohibited','R25-I01':'sem.state.room.secure-prohibited','R25-I02':'sem.state.room.malfunction-prohibited'}
    if any(denotation_by_id.get(occurrence_id) != reference for occurrence_id, reference in expected_room_states.items()) or 'SEM-ROOM-STATIC-PROHIBITIONS' not in record_by_id:
        failures.append({'check': 'Room static-state icon semantics'})
    room12_operations = (record_by_id.get('SEM-ROOM-12') or {}).get('operations') or []
    room12_attack_index = next((index for index,row in enumerate(room12_operations) if row.get('invokeRuleId') == 'SEM-INT-004'), None)
    room12_noise_index = next((index for index,row in enumerate(room12_operations) if row.get('invokeRuleId') == 'SEM-NOISE-001'), None)
    if room12_attack_index is None or room12_noise_index is None or room12_attack_index > room12_noise_index:
        failures.append({'check': 'Technical Corridor Entrance operation order'})
    room12_text = json.dumps(record_by_id.get('SEM-ROOM-12') or {}, ensure_ascii=False)
    if not all(fragment in room12_text for fragment in ('virtual Adult attacker with no miniature','targeting only the moved Character','Secure ignored','may be used in the normal pre-resolution window')):
        failures.append({'check': 'Technical Corridor Entrance Attack parameters/prevention'})
    for robot_room_id in ('SEM-ROOM-07','SEM-ROOM-17'):
        if 'not broken' not in json.dumps(record_by_id.get(robot_room_id) or {}, ensure_ascii=False):
            failures.append({'check': 'Robot-dependent Room broken restriction', 'ruleId': robot_room_id})
    if not (record_by_id.get('SEM-ROOM-20') or {}).get('targets') or not all(rule_id in record_by_id for rule_id in ('SEM-DATA-TOKEN-001','SEM-AUTODESTRUCTION-001','SEM-ROBOT-MALFUNCTION-001')):
        failures.append({'check': 'Server/Data/Autodestruction/Robot semantic dependencies'})
    room19_information = (record_by_id.get('SEM-ROOM-19') or {}).get('informationPolicy') or []
    if not any(row.get('audience') == 'owner-private' and 'need not share' in row.get('secrecy','') for row in room19_information):
        failures.append({'check': 'Life Support B private Anti-Aircraft ordering'})
    qd_c01_types = [row.get('operationType') for row in (record_by_id.get('SEM-IH-QD-C-01') or {}).get('operations') or []]
    if qd_c01_types[:2] != ['place-component','transition-zone']:
        failures.append({'check': 'Queen-Dead Corridor replacement order'})
    hatching = record_by_id.get('SEM-EVENT-HATCHING-001') or {}
    if hatching.get('partialResolution', {}).get('policy') != 'per-sentence-continue' or 'OQ-009' not in hatching.get('unresolvedQuestionRefs', []):
        failures.append({'check': 'Event partial/Nest ambiguity fidelity'})
    semantic_relation_ids = set(ontology_review.get('deferredSemanticRelationIds') or [])
    if semantic_relation_ids != {'rel.phase-part-of-round','rel.round-has-phase','rel.precedes','rel.follows','rel.turn-occurs-in-phase','rel.phase-has-turn','rel.process-has-timing-window','rel.decision-owned-by','rel.owns-decision','rel.information-visible-to','rel.transition-from','rel.transition-to'}:
        failures.append({'check': 'semantic relation handoff'})

    actual_counts = {
        'sources': len(source_rows), 'semanticNodes': len(semantic_node_rows), 'records': len(records),
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
        'conflicts': len(conflict_rows),
        'unresolvedConflicts': sum(item.get('status') == 'unresolved' for item in conflict_rows),
        'roomIconDenotations': len(denotation_rows),
        'backlogUnits': len(backlog.get('units') or []),
        'backlogPilotCovered': sum(item.get('status') == 'pilot-covered' for item in backlog.get('units') or []),
        'backlogSourceBlocked': sum(item.get('status') == 'source-blocked' for item in backlog.get('units') or []),
    }
    if actual_counts != EXPECTED:
        failures.append({'check': 'hard-coded semantic pilot counts', 'expected': EXPECTED, 'actual': actual_counts})
    expected_pilot_counts = {key: actual_counts[key] for key in ('records','sourceBacked','withOpenQuestion','sourceVariants','sourceAssertions','conditions','operations','decisions','informationPolicies','costs','targets','openQuestionReferences','variantReferences')}
    if pilots.get('counts') != expected_pilot_counts or sources_data.get('counts') != {'sources': 10} or review.get('counts') != {'questions':11,'officialClarificationPreferred':6,'sourceAmbiguitiesIntroducedByPilot':5,'resolved':0,'open':11} or coverage.get('counts') != {'systems':18,'pilotRecords':73,'fullBaseSemanticCoverageClaimed':False}:
        failures.append({'check': 'declared semantic counts'})
    covered_rule_ids = [rule_id for system in coverage.get('systems') or [] for rule_id in system.get('ruleIds') or []]
    if set(covered_rule_ids) != set(record_ids) or len(covered_rule_ids) != len(set(covered_rule_ids)) or coverage.get('counts', {}).get('fullBaseSemanticCoverageClaimed') is not False:
        failures.append({'check': 'semantic pilot coverage projection'})

    backlog_units = backlog.get('units') or []
    backlog_ids = [item.get('semanticUnitId') for item in backlog_units]
    if len(backlog_ids) != len(set(backlog_ids)) or any(not item for item in backlog_ids):
        failures.append({'check': 'semantic backlog unit IDs'})
    actual_room_backlog = {item['semanticUnitId'] for item in backlog_units if item.get('channel') == 'room-help-entry'}
    expected_room_backlog = {f'ROOM:{index:02d}' for index in range(1,26)}
    actual_intruder_backlog = {item['semanticUnitId'] for item in backlog_units if item.get('channel') == 'intruder-help-instruction'}
    expected_intruder_backlog = {f'INTR:{occurrence_id}' for occurrence_id in help_rows}
    if actual_room_backlog != expected_room_backlog or actual_intruder_backlog != expected_intruder_backlog:
        failures.append({'check': 'Help semantic backlog exact IDs'})
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
    expected_backlog_status = {'pending':528,'pilot-covered':71,'source-blocked':1}
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
                for name, tracked in [('source-registry.json',source_path),('semantic-rule.schema.json',schema_path),('semantic-vocabulary.json',semantic_vocabulary_path),('room-icon-denotations.json',room_icon_path),('pilots.json',pilots_path),('review-gates.json',review_path),('contradictions.json',contradictions_path),('coverage.json',coverage_path),('backlog.json',backlog_path)]:
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
    parser.add_argument('--semantic-vocabulary', type=Path, default=DIR/'semantic-vocabulary.json')
    parser.add_argument('--room-icon-denotations', type=Path, default=DIR/'room-icon-denotations.json')
    parser.add_argument('--pilots', type=Path, default=DIR/'pilots.json')
    parser.add_argument('--review-gates', type=Path, default=DIR/'review-gates.json')
    parser.add_argument('--contradictions', type=Path, default=DIR/'contradictions.json')
    parser.add_argument('--coverage', type=Path, default=DIR/'coverage.json')
    parser.add_argument('--backlog', type=Path, default=DIR/'backlog.json')
    parser.add_argument('--skip-reproducibility', action='store_true')
    parser.add_argument('--report', action='store_true')
    args = parser.parse_args()
    try:
        report = validate(args.source_registry,args.schema,args.semantic_vocabulary,args.room_icon_denotations,args.pilots,args.review_gates,args.contradictions,args.coverage,args.backlog,reproducibility=not args.skip_reproducibility)
    except (DuplicateJsonKeyError,json.JSONDecodeError) as error:
        report = {'schemaVersion':1,'passed':False,'checks':{},'failureCount':1,'failures':[{'check':'strict JSON parsing','error':str(error)}]}
    if args.report and args.pilots.resolve() == (DIR/'pilots.json').resolve():
        (DIR/'validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
