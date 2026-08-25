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
        self.assertEqual(report['checks']['openReviewGates'], 0)

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
            by_id['tax.rule.mode.deadly']['evidenceTermIds'] = []
            by_id['tax.rule.mode.deadly']['sourceEvidence'] = ['docs/missing-source.md:bogus']
            # Controlled-term and identity coverage drift.
            mappings['controlledTermAssignments'].pop()
            mappings['namedIdentityAssignments'][0]['assignmentKind'] = 'asserts-global-identity'
            # Broken inverse/range/cardinality and premature effect language.
            relation = next(item for item in ontology['relations'] if item['relationId'] == 'rel.part-of')
            relation['inverseRelationId'] = 'rel.missing'
            relation['rangeTaxonIds'] = ['tax.missing']
            relation['cardinalityShape'] = {'bad': {'min': 2, 'max': 1}}
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
            'named identity mapping boundary', 'relation inverse consistency',
            'relation domain/range closure', 'cardinality ordering',
            'premature semantic-effect leakage', 'ontology review gate declaration',
            'hard-coded ontology closure counts',
        }
        self.assertTrue(required.issubset(checks), sorted(checks))


if __name__ == '__main__':
    unittest.main()
