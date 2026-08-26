#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
import unittest

REPO = Path(__file__).resolve().parents[1]
DIR = REPO / 'docs/rules/ontology'
VALIDATOR = REPO / 'scripts/validate_taxonomy_ontology.py'
FILES = ('taxonomy.json', 'mappings.json', 'ontology.json', 'review-gates.json')


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


class TaxonomyOntologyTests(unittest.TestCase):
    def run_validator(self, root: Path | None = None, *, skip_reproducibility: bool = False):
        base = root or DIR
        command = [
            'python3', str(VALIDATOR),
            '--taxonomy', str(base / 'taxonomy.json'),
            '--mappings', str(base / 'mappings.json'),
            '--ontology', str(base / 'ontology.json'),
            '--review-gates', str(base / 'review-gates.json'),
        ]
        if skip_reproducibility:
            command.append('--skip-reproducibility')
        run = subprocess.run(command, cwd=REPO, check=False, capture_output=True, text=True, timeout=300)
        return run, json.loads(run.stdout)

    def test_current_proposal_passes_and_rebuilds_byte_identically(self):
        run, report = self.run_validator()
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertTrue(report['passed'])
        self.assertEqual(report['checks']['controlledTerms'], 167)
        self.assertEqual(report['checks']['namedIdentities'], 501)
        self.assertEqual(report['checks']['acceptedAliases'], 8)
        self.assertEqual(report['checks']['openReviewGates'], 0)

    def test_high_risk_classification_boundaries(self):
        taxonomy = load(DIR / 'taxonomy.json')
        mappings = load(DIR / 'mappings.json')
        ontology = load(DIR / 'ontology.json')
        review = load(DIR / 'review-gates.json')
        parents = {item['taxonId']: item['parentTaxonIds'] for item in taxonomy['taxa']}
        by_taxon = {item['taxonId']: item for item in taxonomy['taxa']}

        def ancestors(taxon_id):
            result = set()
            stack = list(parents[taxon_id])
            while stack:
                parent = stack.pop()
                if parent in result:
                    continue
                result.add(parent)
                stack.extend(parents[parent])
            return result

        self.assertNotIn('tax.process.action', ancestors('tax.process.card-effect.reaction'))
        self.assertNotIn('tax.process.action', ancestors('tax.process.attack'))
        self.assertNotIn('tax.process.action', ancestors('tax.process.attack.opportunity'))
        self.assertIn('tax.process.action', ancestors('tax.process.action.attack.shoot'))
        self.assertIn('tax.process.attack', ancestors('tax.process.action.attack.shoot'))
        self.assertNotIn('tax.process.action', ancestors('tax.process.card-effect.search'))
        self.assertEqual(by_taxon['tax.state.corridor.empty']['definitionBoundary'], 'Corridor containing no Intruders; a Corridor with a Noise marker is still Empty.')
        self.assertEqual(by_taxon['tax.entity.spatial.section.a']['ontologicalKind'], 'identity-kind')
        self.assertEqual(by_taxon['tax.entity.spatial.room.nest']['ontologicalKind'], 'identity-kind')
        self.assertTrue({'tax.identity.source-occurrence', 'tax.entity.information.component-definition', 'tax.entity.component'}.issubset(by_taxon))
        self.assertEqual(len(mappings['acceptedAliasMappings']), 8)
        relation_ids = {item['relationId'] for item in ontology['relations']}
        required_static = {
            'rel.map-depicts-facility', 'rel.section-part-of-facility',
            'rel.corridor-located-in-section', 'rel.door-bounds-room',
            'rel.source-occurrence-documents-definition',
            'rel.component-copy-realizes-definition',
            'rel.component-copy-member-of-set',
            'rel.help-entry-describes-room-definition',
            'rel.action-deck-for-character-role',
            'rel.icon-occurrence-appears-on-definition',
            'rel.room-definition-designated-for-section',
        }
        self.assertTrue(required_static.issubset(relation_ids))
        self.assertTrue(set(review['deferredSemanticRelationIds']).isdisjoint(relation_ids))
        self.assertEqual(
            [(item['questionId'],item['sourceQuestionId']) for item in review['deferredNonBlockingQuestions']],
            [('ONTO-DQ-001','OQ-001'),('ONTO-DQ-003','OQ-003'),('ONTO-DQ-004','OQ-004'),('ONTO-DQ-005','OQ-007'),('ONTO-DQ-006','OQ-009')],
        )

    def test_structural_and_phase_boundary_corruptions_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix='ontology-negative-control-') as temp_dir:
            root = Path(temp_dir)
            for name in FILES:
                (root / name).write_text((DIR / name).read_text(encoding='utf-8'), encoding='utf-8')
            taxonomy = load(root / 'taxonomy.json')
            mappings = load(root / 'mappings.json')
            ontology = load(root / 'ontology.json')
            review = load(root / 'review-gates.json')

            # Cycle and missing provenance.
            by_id = {item['taxonId']: item for item in taxonomy['taxa']}
            by_id['tax.entity']['parentTaxonIds'] = ['tax.entity.agent']
            by_id['tax.entity.agent']['parentTaxonIds'] = ['tax.entity', 'tax.entity']
            by_id['tax.rule.mode.deadly']['evidenceTermIds'] = []
            by_id['tax.rule.mode.deadly']['sourceEvidence'] = ['docs/missing-source.md:bogus']
            # Controlled-term and identity coverage drift.
            mappings['controlledTermAssignments'].pop()
            mappings['controlledTermAssignments'][0]['canonicalLabel'] = 'CORRUPTED LABEL'
            mappings['namedIdentityAssignments'][0]['assignmentKind'] = 'asserts-global-identity'
            mappings['namedIdentityAssignments'][1]['normalizedExactStringKey'] = 'corrupted-key'
            mappings['acceptedAliasMappings'].pop()
            # Broken inverse/range/cardinality and premature effect language.
            relation = next(item for item in ontology['relations'] if item['relationId'] == 'rel.part-of')
            relation['inverseRelationId'] = 'rel.missing'
            relation['rangeTaxonIds'] = ['tax.missing']
            relation['cardinalityShape'] = {'bad': {'min': 2, 'max': 1}}
            ontology['relations'][1]['cardinalityShape'] = {'bad': -1}
            ontology['relations'].append({
                'relationId': 'rel.precedes', 'label': 'premature',
                'domainTaxonIds': ['tax.process'], 'rangeTaxonIds': ['tax.process'],
                'inverseRelationId': None, 'symmetric': False, 'transitive': True,
                'cardinalityShape': {}, 'sourceEvidence': ['docs/rules/01-round-and-turns.md'],
                'semanticBoundary': 'should have remained deferred',
            })
            ontology['staticAssertions'][0]['orderedSteps'] = ['invented semantic step']
            # Invent an owner gate while declared counts remain closed.
            review['gates'] = [{'reviewGateId': 'ONTO-FAKE', 'status': 'open'}]

            for name, data in [('taxonomy.json', taxonomy), ('mappings.json', mappings), ('ontology.json', ontology), ('review-gates.json', review)]:
                (root / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

            run, report = self.run_validator(root, skip_reproducibility=True)

        self.assertNotEqual(run.returncode, 0)
        self.assertFalse(report['passed'])
        checks = {item['check'] for item in report['failures']}
        required = {
            'taxonomy cycle', 'taxon source path', 'controlled term mapping closure',
            'taxon parent ordering/uniqueness', 'controlled term label projection',
            'named identity mapping boundary', 'named identity projection',
            'accepted alias mapping closure', 'relation inverse consistency',
            'relation domain/range closure', 'cardinality ordering',
            'cardinality shape', 'deferred semantic relation boundary',
            'premature semantic-effect leakage', 'ontology review gate declaration',
            'hard-coded ontology closure counts',
        }
        self.assertTrue(required.issubset(checks), sorted(checks))

    def test_duplicate_json_object_keys_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix='ontology-duplicate-json-') as temp_dir:
            root = Path(temp_dir)
            for name in FILES:
                text = (DIR / name).read_text(encoding='utf-8')
                if name == 'taxonomy.json':
                    text = text.replace('"schemaVersion": 1,', '"schemaVersion": 1,\n  "schemaVersion": 1,', 1)
                (root / name).write_text(text, encoding='utf-8')
            run, report = self.run_validator(root, skip_reproducibility=True)
        self.assertNotEqual(run.returncode, 0)
        self.assertFalse(report['passed'])
        self.assertEqual(report['failures'][0]['check'], 'strict JSON parsing')


if __name__ == '__main__':
    unittest.main()
