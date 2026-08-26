#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_DIR = REPO / 'docs/rules/ontology'
VOCAB_DIR = REPO / 'docs/rules/vocabulary'
EXPECTED = {
    'taxa': 211,
    'rootTaxa': 9,
    'controlledTerms': 167,
    'namedIdentities': 501,
    'symbolDenotations': 50,
    'acceptedAliases': 8,
    'relations': 55,
    'inversePairs': 27,
    'staticAssertions': 14,
    'semanticScaffoldTaxa': 15,
    'openReviewGates': 0,
}
EXPECTED_KINDS = {
    'class': 97, 'identity-kind': 16, 'meta-rule': 9, 'process-type': 43,
    'role': 3, 'schema-class': 15, 'state-value': 19, 'symbol-kind': 9,
}
EXPECTED_ROOTS = {
    'tax.entity', 'tax.identity', 'tax.process', 'tax.role', 'tax.rule',
    'tax.scaffold', 'tax.state', 'tax.symbol', 'tax.value',
}
EXPECTED_DEFERRED_RELATIONS = {
    'rel.phase-part-of-round', 'rel.round-has-phase', 'rel.precedes', 'rel.follows',
    'rel.turn-occurs-in-phase', 'rel.phase-has-turn', 'rel.process-has-timing-window',
    'rel.decision-owned-by', 'rel.owns-decision', 'rel.information-visible-to',
    'rel.transition-from', 'rel.transition-to',
}
EXPECTED_IDENTITY_TAXA = {
    'tax.identity.card-face': 199, 'tax.identity.game-term-label': 7,
    'tax.identity.room': 25, 'tax.identity.structured-key': 270,
}
FORBIDDEN_SEMANTIC_KEYS = {
    'trigger', 'triggers', 'orderedSteps', 'steps', 'costValue', 'targetSelection',
    'legalTargets', 'mutations', 'effectInstances', 'replacementEffect',
    'preventionEffect', 'resolutionAlgorithm', 'conditionExpression',
}


class DuplicateJsonKeyError(ValueError):
    pass


def reject_duplicate_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonKeyError(f'duplicate JSON object key: {key}')
        result[key] = value
    return result


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=reject_duplicate_pairs)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_path(reference: str) -> Path | None:
    if not isinstance(reference, str) or not reference:
        return None
    relative = reference.split(':', 1)[0]
    if not relative.startswith(('docs/', 'assets/')):
        return None
    return REPO / relative


def scan_forbidden(value, path: str, found: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_SEMANTIC_KEYS:
                found.append(f'{path}.{key}')
            scan_forbidden(child, f'{path}.{key}', found)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            scan_forbidden(child, f'{path}[{index}]', found)


def validate(taxonomy_path: Path, mappings_path: Path, ontology_path: Path, review_path: Path, *, check_reproducibility: bool) -> dict:
    failures: list[dict] = []
    taxonomy = load(taxonomy_path)
    mappings = load(mappings_path)
    ontology = load(ontology_path)
    review = load(review_path)
    vocabulary = load(VOCAB_DIR / 'canonical-vocabulary.json')
    identities = load(VOCAB_DIR / 'named-component-identities.json')
    aliases = load(VOCAB_DIR / 'alias-registry.json')
    vocab_review = load(VOCAB_DIR / 'vocabulary-review-gates.json')

    if vocab_review.get('counts', {}).get('open') != 0 or aliases.get('counts', {}).get('proposedReviewAliases') != 0:
        failures.append({'check': 'vocabulary prerequisite gate'})

    taxa = taxonomy.get('taxa') or []
    taxon_ids = [item.get('taxonId') for item in taxa]
    taxon_set = set(taxon_ids)
    if len(taxon_ids) != len(taxon_set) or any(not re.fullmatch(r'tax\.[a-z0-9.-]+', item or '') for item in taxon_ids):
        failures.append({'check': 'taxon ID uniqueness/format'})
    roots = [item for item in taxa if not item.get('parentTaxonIds')]
    if {item['taxonId'] for item in roots} != EXPECTED_ROOTS:
        failures.append({'check': 'independently locked root set', 'expected': sorted(EXPECTED_ROOTS), 'actual': sorted(item['taxonId'] for item in roots)})
    for item in taxa:
        parents = item.get('parentTaxonIds') or []
        if parents != sorted(set(parents)):
            failures.append({'check': 'taxon parent ordering/uniqueness', 'taxonId': item.get('taxonId'), 'parents': parents})
        if item.get('taxonId') in parents:
            failures.append({'check': 'taxon self parent', 'taxonId': item.get('taxonId')})
        missing = sorted(set(item.get('parentTaxonIds') or []) - taxon_set)
        if missing:
            failures.append({'check': 'taxon parent closure', 'taxonId': item.get('taxonId'), 'missing': missing})
        for term_id in item.get('evidenceTermIds') or []:
            if term_id not in {entry['termId'] for entry in vocabulary['entries']}:
                failures.append({'check': 'taxon evidence term', 'taxonId': item.get('taxonId'), 'termId': term_id})
        evidence = item.get('sourceEvidence') or []
        if not item.get('evidenceTermIds') and not evidence:
            failures.append({'check': 'taxon provenance missing', 'taxonId': item.get('taxonId')})
        for reference in evidence:
            path = source_path(reference)
            if path is None or not path.exists():
                failures.append({'check': 'taxon source path', 'taxonId': item.get('taxonId'), 'reference': reference})
        for other in item.get('disjointWithTaxonIds') or []:
            if other not in taxon_set or other == item.get('taxonId'):
                failures.append({'check': 'disjoint target', 'taxonId': item.get('taxonId'), 'target': other})
            elif item.get('taxonId') not in next(candidate for candidate in taxa if candidate['taxonId'] == other).get('disjointWithTaxonIds', []):
                failures.append({'check': 'disjoint symmetry', 'taxonId': item.get('taxonId'), 'target': other})

    # Acyclic parent graph.
    graph = {item['taxonId']: item.get('parentTaxonIds') or [] for item in taxa}
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(node_id: str, stack: list[str]) -> None:
        if node_id in visiting:
            failures.append({'check': 'taxonomy cycle', 'cycle': stack + [node_id]})
            return
        if node_id in visited:
            return
        visiting.add(node_id)
        for parent in graph.get(node_id, []):
            visit(parent, stack + [node_id])
        visiting.remove(node_id)
        visited.add(node_id)
    for node_id in graph:
        visit(node_id, [])

    term_rows = mappings.get('controlledTermAssignments') or []
    expected_term_ids = {entry['termId'] for entry in vocabulary['entries']}
    vocabulary_by_id = {entry['termId']: entry for entry in vocabulary['entries']}
    actual_term_ids = [row.get('termId') for row in term_rows]
    if len(actual_term_ids) != len(set(actual_term_ids)) or set(actual_term_ids) != expected_term_ids:
        failures.append({'check': 'controlled term mapping closure', 'missing': sorted(expected_term_ids - set(actual_term_ids)), 'extra': sorted(set(actual_term_ids) - expected_term_ids)})
    for row in term_rows:
        if row.get('canonicalLabel') != vocabulary_by_id.get(row.get('termId'), {}).get('canonicalLabel'):
            failures.append({'check': 'controlled term label projection', 'termId': row.get('termId'), 'actual': row.get('canonicalLabel')})
        targets = [row.get('primaryTaxonId'), *(row.get('alsoDenotesTaxonIds') or [])]
        if len(targets) != len(set(targets)):
            failures.append({'check': 'controlled term target uniqueness', 'termId': row.get('termId'), 'targets': targets})
        if any(target not in taxon_set for target in targets):
            failures.append({'check': 'controlled term taxon target', 'termId': row.get('termId'), 'targets': targets})
    icon_term_ids = {entry['termId'] for entry in vocabulary['entries'] if entry['termId'].startswith('icon.')}
    symbol_term_ids = {row['termId'] for row in term_rows if row.get('assignmentKind') == 'symbol-denotation'}
    if symbol_term_ids != icon_term_ids:
        failures.append({'check': 'icon symbol-denotation closure', 'missing': sorted(icon_term_ids - symbol_term_ids), 'extra': sorted(symbol_term_ids - icon_term_ids)})

    identity_rows = mappings.get('namedIdentityAssignments') or []
    expected_identity_ids = {entry['identityObservationId'] for entry in identities['records']}
    identity_by_id = {entry['identityObservationId']: entry for entry in identities['records']}
    actual_identity_ids = [row.get('identityObservationId') for row in identity_rows]
    if len(actual_identity_ids) != len(set(actual_identity_ids)) or set(actual_identity_ids) != expected_identity_ids:
        failures.append({'check': 'named identity mapping closure'})
    for row in identity_rows:
        source_identity = identity_by_id.get(row.get('identityObservationId')) or {}
        if row.get('normalizedExactStringKey') != source_identity.get('normalizedExactStringKey') or row.get('sourceOccurrenceCount') != len(source_identity.get('sourceOccurrences') or []):
            failures.append({'check': 'named identity projection', 'identityObservationId': row.get('identityObservationId')})
        if row.get('primaryTaxonId') not in taxon_set or row.get('assignmentKind') != 'classifies-source-identity-only':
            failures.append({'check': 'named identity mapping boundary', 'identityObservationId': row.get('identityObservationId')})

    accepted_alias_rows = [item for item in aliases.get('aliases') or [] if item.get('status', '').startswith('accepted-')]
    alias_mapping_rows = mappings.get('acceptedAliasMappings') or []
    if {item.get('aliasId') for item in alias_mapping_rows} != {item.get('aliasId') for item in accepted_alias_rows} or len(alias_mapping_rows) != len(accepted_alias_rows):
        failures.append({'check': 'accepted alias mapping closure'})
    alias_by_id = {item['aliasId']: item for item in accepted_alias_rows}
    term_assignment_by_id = {item['termId']: item for item in term_rows}
    identity_assignment_by_id = {item['identityObservationId']: item for item in identity_rows}
    for row in alias_mapping_rows:
        source_alias = alias_by_id.get(row.get('aliasId')) or {}
        if any(row.get(key) != source_alias.get(key) for key in ('aliasText', 'status', 'scope', 'targetTermId', 'targetNamedIdentityId')):
            failures.append({'check': 'accepted alias projection', 'aliasId': row.get('aliasId')})
        target_term = source_alias.get('targetTermId')
        target_identity = source_alias.get('targetNamedIdentityId')
        if bool(target_term) == bool(target_identity):
            failures.append({'check': 'accepted alias target cardinality', 'aliasId': row.get('aliasId')})
            continue
        if target_term:
            assignment = term_assignment_by_id.get(target_term) or {}
            expected_targets = sorted(set([assignment.get('primaryTaxonId'), *(assignment.get('alsoDenotesTaxonIds') or [])]))
        else:
            expected_targets = [identity_assignment_by_id.get(target_identity, {}).get('primaryTaxonId')]
        if row.get('targetTaxonIds') != expected_targets or row.get('sourceTupleCount') != len(source_alias.get('sourceTuples') or []):
            failures.append({'check': 'accepted alias target projection', 'aliasId': row.get('aliasId'), 'expectedTargets': expected_targets, 'actualTargets': row.get('targetTaxonIds')})

    relations = ontology.get('relations') or []
    relation_ids = [item.get('relationId') for item in relations]
    relation_by_id = {item['relationId']: item for item in relations}
    if len(relation_ids) != len(set(relation_ids)) or any(not re.fullmatch(r'rel\.[a-z0-9.-]+', item or '') for item in relation_ids):
        failures.append({'check': 'relation ID uniqueness/format'})
    deferred_relations = set(review.get('deferredSemanticRelationIds') or [])
    if deferred_relations != EXPECTED_DEFERRED_RELATIONS or deferred_relations & set(relation_ids):
        failures.append({'check': 'deferred semantic relation boundary', 'expected': sorted(EXPECTED_DEFERRED_RELATIONS), 'actual': sorted(deferred_relations), 'encodedDespiteDeferral': sorted(deferred_relations & set(relation_ids))})
    for item in relations:
        for field in ('domainTaxonIds', 'rangeTaxonIds'):
            if item.get(field) != sorted(set(item.get(field) or [])):
                failures.append({'check': 'relation domain/range ordering/uniqueness', 'relationId': item.get('relationId'), 'field': field})
            if not item.get(field) or any(target not in taxon_set for target in item.get(field) or []):
                failures.append({'check': 'relation domain/range closure', 'relationId': item.get('relationId'), 'field': field})
        inverse = item.get('inverseRelationId')
        if inverse:
            target = relation_by_id.get(inverse)
            if target is None or target.get('inverseRelationId') != item.get('relationId'):
                failures.append({'check': 'relation inverse consistency', 'relationId': item.get('relationId'), 'inverse': inverse})
            elif set(item.get('domainTaxonIds') or []) != set(target.get('rangeTaxonIds') or []) or set(item.get('rangeTaxonIds') or []) != set(target.get('domainTaxonIds') or []):
                failures.append({'check': 'relation inverse domain/range', 'relationId': item.get('relationId'), 'inverse': inverse})
            elif item.get('transitive') != target.get('transitive'):
                failures.append({'check': 'relation inverse transitivity', 'relationId': item.get('relationId'), 'inverse': inverse})
        if item.get('symmetric') and (set(item.get('domainTaxonIds') or []) != set(item.get('rangeTaxonIds') or []) or item.get('inverseRelationId') is not None):
            failures.append({'check': 'symmetric relation shape', 'relationId': item.get('relationId')})
        if not item.get('semanticBoundary'):
            failures.append({'check': 'relation semantic boundary', 'relationId': item.get('relationId')})
        for reference in item.get('sourceEvidence') or []:
            path = source_path(reference)
            if path is None or not path.exists():
                failures.append({'check': 'relation source path', 'relationId': item.get('relationId'), 'reference': reference})
        def inspect_cardinality(value, path):
            if not isinstance(value, dict):
                failures.append({'check': 'cardinality shape', 'relationId': item.get('relationId'), 'path': path, 'value': value})
                return
            if 'min' in value or 'max' in value:
                if set(value) != {'min', 'max'} or not all(isinstance(value[key], int) and not isinstance(value[key], bool) and value[key] >= 0 for key in ('min', 'max')):
                    failures.append({'check': 'cardinality shape', 'relationId': item.get('relationId'), 'path': path, 'value': value})
                elif value['min'] > value['max']:
                    failures.append({'check': 'cardinality ordering', 'relationId': item.get('relationId'), 'path': path})
                return
            for key, child in value.items():
                if not re.fullmatch(r'[A-Za-z][A-Za-z0-9]*', key):
                    failures.append({'check': 'cardinality scope key', 'relationId': item.get('relationId'), 'path': f'{path}.{key}'})
                inspect_cardinality(child, f'{path}.{key}')
        inspect_cardinality(item.get('cardinalityShape') or {}, 'cardinalityShape')

    assertions = ontology.get('staticAssertions') or []
    assertion_ids = [item.get('assertionId') for item in assertions]
    if len(assertion_ids) != len(set(assertion_ids)) or any(not re.fullmatch(r'AS-\d{3}', item or '') for item in assertion_ids):
        failures.append({'check': 'assertion ID uniqueness/format'})
    taxon_reference_keys = {'subjectTaxonId', 'targetTaxonId'}
    taxon_reference_list_keys = {'memberTaxonIds', 'allowedLocationTaxonIds', 'forbiddenLocationTaxonIds', 'taxonIds', 'stateTaxonIds'}
    for item in assertions:
        for key in taxon_reference_keys:
            if key in item and item[key] not in taxon_set:
                failures.append({'check': 'assertion taxon reference', 'assertionId': item.get('assertionId'), 'key': key, 'value': item[key]})
        for key in taxon_reference_list_keys:
            if key in item and any(target not in taxon_set for target in item[key]):
                failures.append({'check': 'assertion taxon reference', 'assertionId': item.get('assertionId'), 'key': key})
        for target in (item.get('weightByTaxonId') or {}):
            if target not in taxon_set:
                failures.append({'check': 'assertion weighted taxon', 'assertionId': item.get('assertionId'), 'target': target})
        if item.get('targetNamedIdentityId') and item['targetNamedIdentityId'] not in expected_identity_ids:
            failures.append({'check': 'assertion named identity reference', 'assertionId': item.get('assertionId'), 'target': item['targetNamedIdentityId']})
        if item.get('targetTermId') and item['targetTermId'] not in expected_term_ids:
            failures.append({'check': 'assertion controlled term reference', 'assertionId': item.get('assertionId'), 'target': item['targetTermId']})
        for reference in item.get('sourceEvidence') or []:
            path = source_path(reference)
            if path is None or not path.exists():
                failures.append({'check': 'assertion source path', 'assertionId': item.get('assertionId'), 'reference': reference})

    forbidden: list[str] = []
    scan_forbidden(taxonomy, 'taxonomy', forbidden)
    scan_forbidden(mappings, 'mappings', forbidden)
    scan_forbidden(ontology, 'ontology', forbidden)
    if forbidden:
        failures.append({'check': 'premature semantic-effect leakage', 'paths': forbidden})

    review_counts = review.get('counts') or {}
    if review_counts != {'reviewGates': 0, 'resolved': 0, 'open': 0} or review.get('gates') != []:
        failures.append({'check': 'ontology review gate declaration'})
    deferred = review.get('deferredNonBlockingQuestions') or []
    expected_deferred = [
        {'questionId':'ONTO-DQ-001','sourceQuestionId':'OQ-001','classification':'semantic-procedure ambiguity','reason':'Eclosion existing-hand scope does not alter static classes or relations.'},
        {'questionId':'ONTO-DQ-003','sourceQuestionId':'OQ-003','classification':'semantic role-transfer ambiguity','reason':'Starting Player eligibility/transfer algorithm is not needed to define Player, role, or token classes.'},
        {'questionId':'ONTO-DQ-004','sourceQuestionId':'OQ-004','classification':'semantic timing ambiguity','reason':'Mid-Turn death advancement belongs to turn-resolution semantics.'},
        {'questionId':'ONTO-DQ-005','sourceQuestionId':'OQ-007','classification':'semantic cardinality-per-event ambiguity','reason':'Secure consumption during simultaneous entry is effect resolution, not static component cardinality.'},
        {'questionId':'ONTO-DQ-006','sourceQuestionId':'OQ-009','classification':'semantic placement ambiguity','reason':'Nest event before discovery concerns effect timing/placement.'},
    ]
    if deferred != expected_deferred:
        failures.append({'check': 'deferred question ledger'})
    audit = review.get('independentAudit') or {}
    if audit.get('delegationId') != 'deleg_0cdda6e9' or audit.get('workstreams') != 4 or len(audit.get('incorporatedFindings') or []) != 7 or not review.get('status', '').startswith('independent taxonomy'):
        failures.append({'check': 'independent audit incorporation'})

    actual_counts = {
        'taxa': len(taxa), 'rootTaxa': len(roots), 'controlledTerms': len(term_rows),
        'namedIdentities': len(identity_rows),
        'symbolDenotations': sum(row.get('assignmentKind') == 'symbol-denotation' for row in term_rows),
        'acceptedAliases': len(alias_mapping_rows),
        'relations': len(relations),
        'inversePairs': sum(bool(item.get('inverseRelationId')) for item in relations) // 2,
        'staticAssertions': len(assertions),
        'semanticScaffoldTaxa': sum(item.get('taxonId', '').startswith('tax.scaffold') for item in taxa),
        'openReviewGates': review_counts.get('open'),
    }
    if actual_counts != EXPECTED:
        failures.append({'check': 'hard-coded ontology closure counts', 'expected': EXPECTED, 'actual': actual_counts})
    actual_kind_counts = dict(sorted(collections.Counter(item.get('ontologicalKind') for item in taxa).items()))
    actual_identity_taxa = dict(sorted(collections.Counter(item.get('primaryTaxonId') for item in identity_rows).items()))
    if actual_kind_counts != EXPECTED_KINDS or taxonomy.get('counts', {}).get('byOntologicalKind') != EXPECTED_KINDS:
        failures.append({'check': 'hard-coded ontological kind counts', 'expected': EXPECTED_KINDS, 'actual': actual_kind_counts})
    if actual_identity_taxa != EXPECTED_IDENTITY_TAXA or taxonomy.get('counts', {}).get('namedIdentityAssignmentsByTaxon') != EXPECTED_IDENTITY_TAXA:
        failures.append({'check': 'hard-coded named identity taxon counts', 'expected': EXPECTED_IDENTITY_TAXA, 'actual': actual_identity_taxa})
    if taxonomy.get('counts', {}).get('taxa') != EXPECTED['taxa'] or mappings.get('counts') != {'controlledTerms': 167, 'namedIdentities': 501, 'symbolDenotations': 50, 'acceptedAliases': 8} or ontology.get('counts') != {'relations': 55, 'inversePairs': 27, 'staticAssertions': 14, 'semanticScaffoldTaxa': 15}:
        failures.append({'check': 'declared ontology counts'})

    if check_reproducibility:
        rebuild_hash_sets = []
        for seed in ('1', '777'):
            with tempfile.TemporaryDirectory(prefix=f'ontology-rebuild-{seed}-') as temp_dir:
                environment = {'LC_ALL': 'C', 'TZ': 'UTC', 'PYTHONHASHSEED': seed}
                run = subprocess.run(['python3', str(REPO / 'scripts/build_taxonomy_ontology.py'), '--output-dir', temp_dir], cwd=REPO, check=False, capture_output=True, text=True, env={**__import__('os').environ, **environment})
                if run.returncode != 0:
                    failures.append({'check': 'ontology rebuild execution', 'seed': seed, 'stderr': run.stderr})
                    continue
                hashes = {}
                for name, tracked in [('taxonomy.json', taxonomy_path), ('mappings.json', mappings_path), ('ontology.json', ontology_path), ('review-gates.json', review_path)]:
                    rebuilt = Path(temp_dir) / name
                    hashes[name] = sha(rebuilt) if rebuilt.is_file() else None
                    if not rebuilt.is_file() or hashes[name] != sha(tracked):
                        failures.append({'check': 'ontology reproducibility', 'seed': seed, 'file': name})
                rebuild_hash_sets.append(hashes)
        if len(rebuild_hash_sets) == 2 and rebuild_hash_sets[0] != rebuild_hash_sets[1]:
            failures.append({'check': 'ontology hash-seed reproducibility', 'builds': rebuild_hash_sets})

    report = {'schemaVersion': 1, 'passed': not failures, 'checks': actual_counts, 'failureCount': len(failures), 'failures': failures}
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--taxonomy', type=Path, default=DEFAULT_DIR / 'taxonomy.json')
    parser.add_argument('--mappings', type=Path, default=DEFAULT_DIR / 'mappings.json')
    parser.add_argument('--ontology', type=Path, default=DEFAULT_DIR / 'ontology.json')
    parser.add_argument('--review-gates', type=Path, default=DEFAULT_DIR / 'review-gates.json')
    parser.add_argument('--skip-reproducibility', action='store_true')
    parser.add_argument('--report', action='store_true', help='write docs/rules/ontology/validation.json for the default artifact set')
    args = parser.parse_args()
    try:
        report = validate(args.taxonomy, args.mappings, args.ontology, args.review_gates, check_reproducibility=not args.skip_reproducibility)
    except (DuplicateJsonKeyError, json.JSONDecodeError) as error:
        report = {'schemaVersion': 1, 'passed': False, 'checks': {}, 'failureCount': 1, 'failures': [{'check': 'strict JSON parsing', 'error': str(error)}]}
    if args.report and args.taxonomy.resolve() == (DEFAULT_DIR / 'taxonomy.json').resolve():
        (DEFAULT_DIR / 'validation.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
