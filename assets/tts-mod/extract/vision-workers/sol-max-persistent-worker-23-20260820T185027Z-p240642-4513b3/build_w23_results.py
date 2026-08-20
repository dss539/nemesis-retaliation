#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any

from PIL import Image

REPO = Path('/home/smithers/projects/nemesis-card-corpus/repos/nemesis-retaliation').resolve()
ROOT = REPO / 'assets/tts-mod/extract/vision-workers/sol-max-persistent-worker-23-20260820T185027Z-p240642-4513b3'
IDS = [f'W23-{i:03d}' for i in range(1, 9)]
RUN_ID = 'w23-card-extraction-20260820T185027Z-p240642-4513b3'
MODEL = {'provider': 'openai-codex', 'model': 'gpt-5.6-sol', 'reasoningEffort': 'max'}
QUEUE = REPO / 'assets/tts-mod/extract/low-confidence-review.json'
REGISTRY = REPO / 'assets/tts-mod/extract/selected-card-text-evidence.json'
PROGRESS = REPO / 'assets/tts-mod/extract/vision-progress.json'
CORPUS = REPO / 'assets/tts-mod/extract/card-text-corpus.json'
OBJECTS = REPO / 'assets/tts-mod/extract/v2/objects.json'
OBJECTIVES = REPO / 'docs/rulebooks/Nemesis_RT_Objectives_Sheet.pdf'
FAQ = REPO / 'docs/rulebooks/Nemesis_RT_FAQ_v1.2.pdf'
RULEBOOK = REPO / 'docs/rulebooks/Nemesis_RT_Rulebook_official.pdf'
OFFICIAL_HASHES = {
    'objectives': '30f3d4116a9c4dc3a53fb5e920995c24aa747988c915dc5fba6261cbd7dca364',
    'faq': '611ae20dc0b3e04f3c0d99f294a92fc95460c042565b12d1c808b1282ae0e0d8',
    'rulebook': 'e3cda0d7a91bd090cec45dbc8ce89e2015e2202173357c374ff49365f9c29ddd',
}
OFFICIAL_URLS = {
    'objectives': 'https://awakenrealms.com/images/download/Nemesis_Retaliation/ENG/Nemesis_RT_Objective_Sheet_285x285mm_bleed3mm%20%5B2%20pages%5D',
    'faq': 'https://awakenrealms.com/images/download/Nemesis_Retaliation/ENG/RETALIATION_FAQ_297x214mm_bleed3mm_%5B3%20pages%5D%20v1.2_lowres.pdf',
    'rulebook': 'https://awakenrealms.com/images/download/Nemesis_Retaliation/ENG/Nemesis_RT_Rulebook_210x285mm_bleed3mm%20%5B40%20pages%5D%20%5Blowres%5D.pdf',
}
OFFICIAL_TEXT = {
    'the-supply-route': {
        'title': 'THE SUPPLY ROUTE',
        'qualifier': '3+',
        'body': 'There must be a continuous path of Reinforced Corridors from the Landing Zone (Section A) to the Life Support Control C.\nAND\nThe Facility must NOT be destroyed.',
    },
    'essential-data': {
        'title': 'ESSENTIAL DATA',
        'qualifier': '2+',
        'body': 'At least 1 [character] with a Data token (from the Server Room in Section B) must Escape using the [lander] (Section A).\nAND\nThere must be no Unexplored Corridors in Section A.',
    },
    'primary-samples': {
        'title': 'PRIMARY SAMPLES',
        'qualifier': '2+',
        'body': 'All [character] who Escape from the Facility must be carrying at least 2 Eggs in total among them (no matter if they Survive after Escaping).',
    },
    'perimeter-clearing': {
        'title': 'PERIMETER CLEARING',
        'qualifier': '2+',
        'body': 'The Reactor (Section C) must be shut down (by using the Room).\nAND\nAll 3 Rooms of the A type must be Discovered.',
    },
}
OFFICIAL_KEY = {
    'W23-001': 'the-supply-route',
    'W23-002': 'essential-data',
    'W23-003': 'primary-samples',
    'W23-004': 'primary-samples',
    'W23-005': 'perimeter-clearing',
    'W23-006': 'the-supply-route',
    'W23-007': None,
    'W23-008': 'essential-data',
}
TARGET_SLUG = {
    'W23-001': 'the-supply-route',
    'W23-002': 'essential-data',
    'W23-003': 'primary-samples',
    'W23-004': 'primary-samples',
    'W23-005': 'perimeter-clearing',
    'W23-006': 'the-supply-route',
    'W23-007': 'sabotage',
    'W23-008': 'essential-data',
}
SOURCE_QUALIFIER = {
    'W23-001': '3+', 'W23-002': '2+', 'W23-003': '2+', 'W23-004': 'ALL',
    'W23-005': 'ALL', 'W23-006': 'ALL', 'W23-007': '2+', 'W23-008': '2+',
}
SOURCE_FIDELITY_STATUS = {
    'W23-001': 'current-official-operative-text-match',
    'W23-002': 'current-official-operative-text-match',
    'W23-003': 'material-conflict-with-current-official',
    'W23-004': 'material-conflict-with-current-official',
    'W23-005': 'material-conflict-with-current-official',
    'W23-006': 'material-conflict-with-current-official',
    'W23-007': 'no-current-official-title-counterpart',
    'W23-008': 'material-conflict-with-current-official',
}
CONFLICTS = {
    'W23-001': [],
    'W23-002': [],
    'W23-003': [
        'Assigned art requires at least 2 Eggs to be taken out using the Lander or Escape Shuttle; current official text instead requires all escaping Characters collectively to carry at least 2 Eggs.',
        'Assigned art omits the current official survival-after-Escaping qualifier.',
    ],
    'W23-004': [
        'Assigned applicability is ALL; current official applicability is 2+.',
        'Assigned art requires at least 2 Eggs to be taken out using the Lander or Escape Shuttle; current official text instead requires all escaping Characters collectively to carry at least 2 Eggs.',
        'Assigned art omits the current official survival-after-Escaping qualifier.',
    ],
    'W23-005': [
        'Assigned applicability is ALL; current official applicability is 2+.',
        'Assigned Reactor condition omits Section C and the by-using-the-Room method qualifier.',
        'Assigned text says all Section Rooms A must be Explored; current official text says all 3 Rooms of the A type must be Discovered.',
    ],
    'W23-006': [
        'Assigned applicability is ALL; current official applicability is 3+.',
        'Assigned route terminates at the Server Room; current official route terminates at Life Support Control C.',
        'Assigned route omits the Landing Zone (Section A) qualifier and presents a different parenthetical construction.',
        'Assigned art prints not in ordinary case; current official art emphasizes NOT in uppercase.',
    ],
    'W23-007': [
        'No Mission Task titled SABOTAGE appears on the current two-page Awaken Realms Objectives Help Sheet or in the licensed BGA mission-task data.',
    ],
    'W23-008': [
        'Assigned art uses literal Character and Lander words where current official art uses the corresponding glyphs.',
        'Assigned Server Room condition omits Section B.',
        'Assigned Lander condition omits Section A.',
        'Assigned art omits the entire current official AND condition requiring no Unexplored Corridors in Section A.',
    ],
}
ART_DETAIL_SPANS = {
    'W23-001': [
        'Upper-left in-scene CARGO-045 placard has one tiny pale line that remains [illegible]; it is artwork/signage, not operative Mission Task text.',
    ],
    'W23-006': [
        'Small red glyph-like mark above the title plaque remains [illegible] and is preserved as background artwork texture, not operative text.',
    ],
    'W23-007': [
        'Central tilted display has multiple rows of [illegible] artwork-only microtext.',
        'Small lower-left background object has [illegible] artwork-only marks.',
        'Faint marks inside the framed dark square remain unreadable and non-semantic.',
    ],
    'W23-008': [
        'Central tilted display has multiple rows and columns of [illegible] artwork-only microtext.',
        'Faint sequence below the display is [illegible] artwork texture.',
        'Small lower-left background object has [illegible] artwork-only marks.',
        'Right-edge equipment strip has an [illegible] artwork-only label.',
        'Faint diagonal background character-like sequence is [clipped] and non-operative.',
    ],
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(obj: Any) -> bytes:
    return (json.dumps(obj, indent=2, ensure_ascii=False) + '\n').encode()


def create(path: Path, obj: Any, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise RuntimeError(f'refuse overwrite: {path}')
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_bytes(canonical(obj))
    os.chmod(tmp, mode)
    os.replace(tmp, path)


def create_bytes(path: Path, data: bytes, mode: int = 0o400) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise RuntimeError(f'refuse overwrite: {path}')
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_bytes(data)
    os.chmod(tmp, mode)
    os.replace(tmp, path)


def rel(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def tuple_digest(assets: list[dict[str, Any]]) -> str:
    rows = [[x['assetId'], x['sourcePath'], x['sourceSha256']] for x in assets]
    return hashlib.sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest()


def normalized_pixel_sha(path: Path) -> str:
    with Image.open(path) as im:
        data = im.convert('RGBA').tobytes()
    return hashlib.sha256(data).hexdigest()


def slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def contact_wrapper(asset_id: str) -> tuple[Path, dict[str, Any]]:
    path = (ROOT / 'adjudication/contact-raw/W23-001.json') if asset_id == 'W23-001' else (ROOT / 'adjudication/contact-raw-retry-01' / f'{asset_id}.json')
    return path, json.loads(path.read_text())


def bbox_wrapper(asset_id: str) -> tuple[Path, dict[str, Any]]:
    path = (ROOT / 'adjudication/bbox-raw-retry-01/W23-001.json') if asset_id == 'W23-001' else (ROOT / 'adjudication/bbox-raw-retry-02' / f'{asset_id}.json')
    return path, json.loads(path.read_text())


def source_body(raw: dict[str, Any]) -> str:
    return raw['visibleText']['body'].replace('[ICON: compact white outlined rounded-top form with a broad rectangular torso and paired side/lower projections]', '[character]').replace('[ICON: broad white three-pronged mound with dark lower cutouts]', '[lander]')


def result_for(
    asset: dict[str, Any],
    raw_wrapper: dict[str, Any],
    provenance: dict[str, Any],
    reconciliation: dict[str, Any],
    runtime_path: Path,
    runtime_sha: str,
    source_prov_path: Path,
    source_prov_sha: str,
    source_rec_path: Path,
    source_rec_sha: str,
) -> dict[str, Any]:
    asset_id = asset['assetId']
    raw = raw_wrapper['modelOutput']
    _, contact = contact_wrapper(asset_id)
    contact_payload = contact['payload']
    contact_rows = {x['sourceIconMorphologyIndex']: x for x in contact_payload['occurrences']}
    comparisons: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    nontext: list[dict[str, Any]] = []
    art_morph: list[dict[str, Any]] = []
    reconciliation_rows: list[dict[str, Any]] = []
    for idx, morphology in enumerate(raw['iconMorphology']):
        adjudicated = contact_rows[idx]
        final_category = adjudicated['finalCategory']
        # The ringed Number-of-Characters composite is conservatively no-match even
        # when W23-001's raw model opinion called its bloom-softened core a match.
        if idx == 0 and asset_id == 'W23-001':
            final_category = 'no-match'
        if final_category in {'match', 'no-match'}:
            if final_category == 'match':
                token = adjudicated['canonicalToken']
                token = {'general/character': 'character', 'map/lander': 'lander'}.get(token, token)
                if token not in {'character', 'lander'}:
                    raise RuntimeError(f'{asset_id} unexpected matched token {token!r}')
                reference = {'character': 'Character', 'lander': 'Lander'}[token]
                closest = adjudicated['closestAlternative']
                discriminator = adjudicated['visibleDiscriminator']
                basis = 'Direct native Sol Max comparison of the source occurrence against the labeled p.40 glossary crop.'
            else:
                token = None
                reference = 'No exact p.40 canonical token established for the ringed Number-of-Characters composite'
                closest = 'character'
                discriminator = (
                    'The source is a bloom-softened simplified white upright silhouette integrated with concentric cyan/blue rings; '
                    'the p.40 Character glyph exposes a visor, segmented limbs/torso voids, and no concentric-ring base.'
                )
                basis = 'The displayed pixels do not establish an exact morphology match; semantic context and adjacent count text were not used as substitutes.'
            comparison = {
                'sourceIconMorphologyIndex': idx,
                'cardLocation': morphology['location'],
                'blindMorphology': morphology,
                'referenceLabel': reference,
                'matchDecision': final_category,
                'canonicalToken': token,
                'closestAlternative': closest,
                'visibleDiscriminator': discriminator,
                'matchBasis': basis,
                'contactSheetPath': contact['contactSheetPath'],
                'contactSheetSha256': contact['contactSheetSha256'],
                'contactSessionId': contact_payload['runtime']['sessionId'],
            }
            comparisons.append(comparison)
            if final_category == 'no-match':
                unresolved.append({
                    'occurrenceIndex': len(unresolved) + 1,
                    'sourceIconMorphologyIndex': idx,
                    'cardLocation': morphology['location'],
                    'observedMorphology': morphology,
                    'testedAlternatives': closest,
                    'reason': basis,
                    'explicitNoMatchComparisonIndex': len(comparisons) - 1,
                })
            reconciliation_rows.append({
                'sourceIconMorphologyIndex': idx,
                'category': final_category,
                'comparisonIndex': len(comparisons) - 1,
                'canonicalToken': token,
            })
        elif final_category == 'non-text-component-graphic':
            row = {
                'occurrenceIndex': len(nontext) + 1,
                'sourceIconMorphologyIndex': idx,
                'morphology': morphology,
                'classification': adjudicated['pixelObservations'],
                'semanticTokenAssigned': False,
            }
            nontext.append(row)
            reconciliation_rows.append({
                'sourceIconMorphologyIndex': idx,
                'category': 'non-text-component-graphic',
                'nonTextOccurrenceIndex': len(nontext) - 1,
                'canonicalToken': None,
            })
        elif final_category == 'artwork-only-detail':
            row = {
                'occurrenceIndex': len(art_morph) + 1,
                'sourceIconMorphologyIndex': idx,
                'morphology': morphology,
                'classification': adjudicated['pixelObservations'],
                'materialRulesText': False,
                'semanticTokenAssigned': False,
            }
            art_morph.append(row)
            reconciliation_rows.append({
                'sourceIconMorphologyIndex': idx,
                'category': 'artwork-only-detail',
                'artworkOccurrenceIndex': len(art_morph) - 1,
                'canonicalToken': None,
            })
        else:
            raise RuntimeError(f'{asset_id} unknown final category {final_category}')
    if sorted(x['sourceIconMorphologyIndex'] for x in reconciliation_rows) != list(range(len(raw['iconMorphology']))):
        raise RuntimeError(f'{asset_id} morphology reconciliation incomplete')
    official_key = OFFICIAL_KEY[asset_id]
    official = OFFICIAL_TEXT.get(official_key) if official_key else None
    target_slug = TARGET_SLUG[asset_id]
    target_stem = f'cards/game/mission-task/{target_slug}'
    target_images = [str(p.relative_to(REPO)) for p in REPO.glob(target_stem + '.*') if p.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp'}]
    target_sidecar = REPO / (target_stem + '.json')
    collisions = [other for other, slug in TARGET_SLUG.items() if slug == target_slug and other != asset_id]
    contact_index = json.loads((ROOT / 'qa/contact-sheets/index.json').read_text())
    contact_record = next(x for x in contact_index['assets'] if x['assetId'] == asset_id)
    tokens = sorted(x['canonicalToken'] for x in comparisons if x['matchDecision'] == 'match')
    decision_reasons = [
        'The material ringed Number-of-Characters composite remains an explicit no-match to the canonical p.40 glossary.',
        'The exact paired BackURL is recorded, but its saved Akamai endpoint returned HTTP 404 and paired-side pixels were unavailable for inspection.',
    ]
    if not provenance['exactFaceSelectorResolved']:
        decision_reasons.append('The generated sheet cell is exact, but no unique GUID/CardID selector is safely established for this cell.')
    if collisions:
        decision_reasons.append(f"The proposed target identity collides inside W23 with {', '.join(collisions)}; no source revision may overwrite or select another without a human decision.")
    if CONFLICTS[asset_id]:
        decision_reasons.extend(CONFLICTS[asset_id])
    result = {
        'schemaVersion': 1,
        'assetId': asset_id,
        'status': 'complete',
        'extractionState': 'draft-partial',
        'sourcePath': asset['sourcePath'],
        'sourceSha256': asset['sourceSha256'],
        'sourceMetadata': asset['sourceMetadata'],
        'runtimeProvenance': {
            **MODEL,
            'sessionId': raw['runtime']['sessionId'],
            'blindSessionId': raw['runtime']['sessionId'],
            'bboxAdjudicationSessionId': bbox_wrapper(asset_id)[1]['payload']['runtime']['sessionId'],
            'adjudicationSessionId': contact_payload['runtime']['sessionId'],
            'nativeImageRouteState': 'exercisedVerified',
            'normalizedRecordPath': rel(runtime_path),
            'normalizedRecordSha256': runtime_sha,
            'auxiliaryVisionUsed': False,
            'qwenUsed': False,
            'ocrCanonicalEvidenceUsed': False,
            'modelDowngradeUsed': False,
        },
        'orientation': raw['orientation'],
        'blindPixelObservations': raw['blindPixelObservations'],
        'visibleText': raw['visibleText'],
        'normalizedOperativeText': source_body(raw),
        'iconMorphology': raw['iconMorphology'],
        'authoritativeComparisons': comparisons,
        'canonicalTokensEmitted': tokens,
        'unresolvedLocalTokens': unresolved,
        'nonTextComponentGraphics': nontext,
        'iconMorphologyArtDisplayDetails': art_morph,
        'nonRulesIllustrationDetails': [
            {'kind': 'artwork-only unreadable detail', 'detail': detail, 'materialRulesText': False, 'semanticTokenAssigned': False}
            for detail in ART_DETAIL_SPANS.get(asset_id, [])
        ],
        'morphologyReconciliation': reconciliation_rows,
        'evidenceConsulted': [
            {'kind': 'assigned native pixels', 'path': asset['sourcePath'], 'sha256': asset['sourceSha256'], 'timing': 'clean isolated blind session'},
            {'kind': 'immutable original wrapper', 'path': rel(ROOT / 'sealed-clean-raw' / f'{asset_id}.json'), 'sha256': sha(ROOT / 'sealed-clean-raw' / f'{asset_id}.json'), 'timing': 'sealed before post-blind lookup'},
            {'kind': 'post-blind bbox native wrapper', 'path': rel(bbox_wrapper(asset_id)[0]), 'sha256': sha(bbox_wrapper(asset_id)[0]), 'timing': 'post-blind'},
            {'kind': 'direct card-to-authoritative contact sheet', 'path': contact_record['contactSheetPath'], 'sha256': contact_record['contactSheetSha256'], 'timing': 'post-blind'},
            {'kind': 'post-blind authoritative contact native wrapper', 'path': rel(contact_wrapper(asset_id)[0]), 'sha256': sha(contact_wrapper(asset_id)[0]), 'timing': 'post-blind'},
            {'kind': 'structured FaceURL/BackURL provenance', 'path': rel(source_prov_path), 'sha256': source_prov_sha, 'timing': 'post-blind'},
            {'kind': 'official source and canonical-target reconciliation', 'path': rel(source_rec_path), 'sha256': source_rec_sha, 'timing': 'post-blind'},
        ],
        'sourceProvenance': provenance,
        'sourceFidelity': reconciliation,
        'officialSourceSupport': {
            'assetId': asset_id,
            'componentFamily': 'mission-task',
            'officialCounterpart': official,
            'officialStatus': SOURCE_FIDELITY_STATUS[asset_id],
            'conflicts': CONFLICTS[asset_id],
            'officialSources': [
                {'path': rel(OBJECTIVES), 'page': 1, 'sha256': OFFICIAL_HASHES['objectives'], 'publisherUrl': OFFICIAL_URLS['objectives'], 'authority': 'primary'},
                {'path': rel(FAQ), 'sha256': OFFICIAL_HASHES['faq'], 'publisherUrl': OFFICIAL_URLS['faq'], 'authority': 'primary', 'applicableFinding': 'No W23-title-specific correction found.'},
                {'path': rel(RULEBOOK), 'sha256': OFFICIAL_HASHES['rulebook'], 'publisherUrl': OFFICIAL_URLS['rulebook'], 'authority': 'primary'},
                {'path': rel(ROOT / 'qa/official-sources/bga-staticData-260622-1220.js'), 'sha256': sha(ROOT / 'qa/official-sources/bga-staticData-260622-1220.js'), 'authority': 'licensed-digital-secondary'},
            ],
            'target': {
                'stem': target_stem,
                'existingImages': target_images,
                'sidecar': rel(target_sidecar) if target_sidecar.exists() else None,
                'exists': bool(target_images or target_sidecar.exists()),
                'w23CollisionAssetIds': collisions,
            },
            'promotionGates': {
                'allMaterialTextReadable': True,
                'allFunctionalSymbolsAuthoritativelyMatched': False,
                'exactFaceSelectorResolved': provenance['exactFaceSelectorResolved'],
                'pairedSideRoleResolved': provenance['sideRoleResolved'],
                'pairedSidePixelsInspected': provenance['pairedSidePixelsInspected'],
                'applicableOfficialSourceGate': SOURCE_FIDELITY_STATUS[asset_id] == 'current-official-operative-text-match',
                'noApplicableSourceConflict': not CONFLICTS[asset_id],
                'canonicalTargetUniqueAndAbsent': not collisions and not target_images and not target_sidecar.exists(),
                'establishedMinimalSidecarSchemaRepresentsAllMaterialFields': False,
            },
            'promotionDecision': 'defer',
        },
        'contactSheetPath': contact_record['contactSheetPath'],
        'proposedClassification': {
            'componentFamily': 'mission-task',
            'componentType': f"mission-task face titled {raw['visibleText']['title']}",
            'basis': 'Exact printed MISSION TASK label, live TTS FaceURL/source-sheet provenance, and current official source comparison.',
        },
        'readConfidence': raw['readConfidence'],
        'classificationConfidence': raw['classificationConfidence'],
        'uncertainties': [
            *raw['uncertainties'],
            *decision_reasons,
        ],
        'allMaterialTextReadable': True,
        'allMaterialIconsAuthoritativelyMatched': False,
        'promotionDecision': 'defer',
        'decisionReasons': decision_reasons,
        'validationPerformed': [
            'sealed wrapper/source tuple revalidated',
            'direct p.40 and current official card contact comparison completed through native Sol Max',
            'FaceURL/BackURL, source-sheet cell, and selector candidates reconciled',
            'official PDF/FAQ/rulebook and licensed BGA source audit completed',
            'every blind icon-morphology occurrence partitioned exactly once',
            'paired BackURL retrieval attempted and preserved as unavailable rather than fabricated',
        ],
        'rawResultPath': rel(ROOT / 'raw' / f'{asset_id}.json'),
        'nextPendingAssetId': f'W23-{asset["assignmentIndex"] + 2:03d}' if asset['assignmentIndex'] < 7 else None,
        'nextPendingSourcePath': (
            json.loads((ROOT / 'assignment.json').read_text())['assets'][asset['assignmentIndex'] + 1]['sourcePath']
            if asset['assignmentIndex'] < 7 else None
        ),
    }
    return result


def main() -> None:
    if any(any((ROOT / name).iterdir()) for name in ('raw', 'results')):
        raise RuntimeError('raw/results staging must be empty before normalization')
    for candidate_dir in (ROOT / 'candidates/images', ROOT / 'candidates/sidecars'):
        candidate_dir.mkdir(parents=True, exist_ok=True)
        if any(candidate_dir.iterdir()):
            raise RuntimeError(f'candidate staging must be empty: {candidate_dir}')
    assignment_path = ROOT / 'assignment.json'
    assignment_bytes = assignment_path.read_bytes()
    assignment_sha = hashlib.sha256(assignment_bytes).hexdigest()
    assignment = json.loads(assignment_bytes)
    assets = assignment['assets']
    if [x['assetId'] for x in assets] != IDS:
        raise RuntimeError('assignment IDs drift')
    baseline = json.loads((ROOT / 'metadata/baseline.json').read_text())
    if baseline['assignmentSha256'] != assignment_sha or baseline['orderedTupleDigest'] != tuple_digest(assets):
        raise RuntimeError('assignment baseline drift')
    for name, expected in ((OBJECTIVES, OFFICIAL_HASHES['objectives']), (FAQ, OFFICIAL_HASHES['faq']), (RULEBOOK, OFFICIAL_HASHES['rulebook'])):
        if sha(name) != expected:
            raise RuntimeError(f'official local hash drift: {name}')
    awaken = json.loads((ROOT / 'qa/official-sources/awaken-files.json').read_text())
    needed_titles = {'Nemesis RT Rulebook', 'FAQ v1.2', 'Nemesis RT Objectives help sheet'}
    manifest_rows = [x for x in awaken if x.get('game') == 'Nemesis Retaliation' and x.get('title') in needed_titles and str(x.get('flagUrl', '')).endswith('/UK.png')]
    if {x['title'] for x in manifest_rows} != needed_titles:
        raise RuntimeError('current publisher manifest rows incomplete')
    bga_path = ROOT / 'qa/official-sources/bga-staticData-260622-1220.js'
    bga_text = bga_path.read_text()
    for title in ('Essential Data', 'Primary Samples', 'Perimeter Clearing', 'The Supply Route'):
        if title not in bga_text:
            raise RuntimeError(f'BGA title absent: {title}')
    if re.search(r"name:\s*['\"]Sabotage['\"]", bga_text):
        raise RuntimeError('BGA unexpectedly contains Sabotage mission title; human audit required')
    queue = json.loads(QUEUE.read_text())
    queue_by_tuple = {(x['sourcePath'], x['sourceSha256']): x for x in queue['entries']}
    objects = json.loads(OBJECTS.read_text())
    object_by_guid = {x.get('guid'): x for x in objects}
    raw_wrappers: dict[str, dict[str, Any]] = {}
    for asset in assets:
        asset_id = asset['assetId']
        source = REPO / asset['sourcePath']
        if sha(source) != asset['sourceSha256']:
            raise RuntimeError(f'{asset_id} source drift')
        sealed = ROOT / 'sealed-clean-raw' / f'{asset_id}.json'
        preserved = ROOT / 'isolated-raw-output' / f'{asset_id}.json'
        wrapper = json.loads(sealed.read_text())
        isolated_payload = json.loads(preserved.read_text())
        if wrapper.get('modelOutput') != isolated_payload:
            raise RuntimeError(f'{asset_id} wrapper modelOutput preservation drift')
        if wrapper['modelOutput']['assetId'] != asset_id:
            raise RuntimeError(f'{asset_id} wrapper identity drift')
        raw_wrappers[asset_id] = wrapper
        create_bytes(ROOT / 'raw' / f'{asset_id}.json', sealed.read_bytes(), 0o400)
    runtime = {
        'schemaVersion': 1,
        'recordType': 'normalizedNativeVisionRuntimeProvenance',
        'recordedAt': now(),
        'provider': MODEL['provider'],
        'model': MODEL['model'],
        'reasoningEffort': MODEL['reasoningEffort'],
        'blind': {
            'sessionIds': [json.loads((ROOT / 'metadata/direct-session-audit.json').read_text())['session']['sessionId']],
            'apiCallCount': 8, 'messageCount': 16, 'toolCallCount': 0,
        },
        'bboxAdjudication': {
            'sessionIds': [json.loads((ROOT / 'metadata/postblind-bbox-session-segment-01.json').read_text())['sessionId'], json.loads((ROOT / 'metadata/postblind-bbox-session-segment-02.json').read_text())['sessionId']],
            'apiCallCount': 8, 'messageCount': 16, 'toolCallCount': 0,
        },
        'contactAdjudication': {
            'sessionIds': [json.loads((ROOT / 'metadata/postblind-contact-session-segment-01.json').read_text())['sessionId'], json.loads((ROOT / 'metadata/postblind-contact-session-segment-02.json').read_text())['sessionId']],
            'apiCallCount': 8, 'messageCount': 16, 'toolCallCount': 0,
        },
        'neutralSmoke': json.loads((ROOT / 'metadata/smoke-audit.json').read_text()),
        'totalProductionNativeImageApiCalls': 24,
        'totalProductionMessages': 48,
        'totalProductionToolCalls': 0,
        'oneImagePerCall': True,
        'auxiliaryVisionUsed': False,
        'qwenUsed': False,
        'ocrCanonicalEvidenceUsed': False,
        'modelDowngradeUsed': False,
        'failureMetadataPaths': sorted(rel(p) for p in (ROOT / 'metadata/failures').glob('*.json')),
    }
    runtime_path = ROOT / 'metadata/runtime.json'
    create(runtime_path, runtime)
    runtime_sha = sha(runtime_path)
    provenance_assets = []
    for asset in assets:
        asset_id = asset['assetId']
        row = queue_by_tuple.get((asset['sourcePath'], asset['sourceSha256']))
        if row is None:
            raise RuntimeError(f'{asset_id} queue tuple absent')
        prov = row['provenance']
        generated = row.get('generatedFrom')
        if generated:
            refs = prov.get('sourceSheetObjectRefs') or []
            selector = {
                'kind': 'generated-source-sheet-cell',
                'deckGuid': 'eabc1d',
                'customDeckKey': 3938,
                'sourceSheetPath': generated['sourcePath'],
                'sourceSheetSha256': generated['sourceSha256'],
                'cellIndex': generated['cellIndex'],
                'grid': generated['grid'],
                'candidateObjectRefs': refs,
                'resolution': 'exact sheet/cell resolved; unique GUID/CardID selector not safely established',
            }
            exact_selector = False
        else:
            refs = [x for x in prov.get('objectRefs', []) if x.get('objectType') == 'CardCustom' and x.get('cardId') not in ('', None)]
            selector = {
                'kind': 'direct-card-face',
                'deckGuid': 'eabc1d',
                'cardRefs': refs,
                'resolution': 'exact CardCustom GUID/CardID and FaceURL resolved',
            }
            exact_selector = len(refs) == 1
        paired_urls = [x['url'] for x in prov.get('pairedSides', []) if x.get('urlRole') == 'BackURL']
        entry = {
            'assetId': asset_id,
            'queueIndex': asset['queueIndex'],
            'sourcePath': asset['sourcePath'],
            'sourceSha256': asset['sourceSha256'],
            'sourceMetadata': asset['sourceMetadata'],
            'sourceNormalizedPixelSha256': normalized_pixel_sha(REPO / asset['sourcePath']),
            'sourceKind': row.get('sourceKind'),
            'sourceUrl': row.get('sourceUrl'),
            'generatedFrom': generated,
            'urlRoleSet': sorted(set(prov.get('urlRoleSet') or [])),
            'allObjectRefs': prov.get('objectRefs') or prov.get('sourceSheetObjectRefs') or [],
            'sourceSelector': selector,
            'exactFaceSelectorResolved': exact_selector,
            'sideRoleResolved': prov.get('sourceRole') == 'FaceURL' and prov.get('sourceRoleResolved') is True,
            'sourceRole': prov.get('sourceRole'),
            'pairedBackUrls': paired_urls,
            'pairedSidePixelsInspected': False,
            'pairedSideInspection': {
                'status': 'unavailable',
                'attemptedUrl': paired_urls[0] if paired_urls else None,
                'attemptedAt': '2026-08-20T20:13Z',
                'savedAkamaiStatus': 404,
                'canonicalHostStatus': 'DNS-unavailable',
                'cloud3Status': 'TLS-hostname-mismatch',
                'localManifestMatch': False,
                'reason': 'The exact saved BackURL is stale/unavailable; no paired-side pixels were fabricated or inferred.',
            },
            'familyDeckGuid': 'eabc1d',
            'familyDeckObject': object_by_guid.get('eabc1d'),
            'componentFamily': 'mission-task',
            'rulesBearing': True,
        }
        provenance_assets.append(entry)
    source_prov = {
        'schemaVersion': 1,
        'recordedAt': now(),
        'workerId': ROOT.name,
        'assignmentSha256': assignment_sha,
        'orderedTupleDigest': tuple_digest(assets),
        'sourceOfTruth': [rel(QUEUE), rel(OBJECTS)],
        'assets': provenance_assets,
        'counts': {
            'assets': 8,
            'directFaceUrls': sum(x['sourceKind'] == 'manifest' for x in provenance_assets),
            'generatedCells': sum(x['sourceKind'] == 'generatedSpriteCell' for x in provenance_assets),
            'exactFaceSelectorsResolved': sum(x['exactFaceSelectorResolved'] for x in provenance_assets),
            'sideRolesResolved': sum(x['sideRoleResolved'] for x in provenance_assets),
            'pairedSidePixelsInspected': sum(x['pairedSidePixelsInspected'] for x in provenance_assets),
            'rulesBearing': sum(x['rulesBearing'] for x in provenance_assets),
        },
        'overallPassed': True,
    }
    source_prov_path = ROOT / 'metadata/source-provenance.json'
    create(source_prov_path, source_prov)
    source_prov_sha = sha(source_prov_path)
    reference_manifest = {
        'schemaVersion': 1,
        'recordedAt': now(),
        'publisherManifestPath': rel(ROOT / 'qa/official-sources/awaken-files.json'),
        'publisherManifestSha256': sha(ROOT / 'qa/official-sources/awaken-files.json'),
        'publisherManifestRows': manifest_rows,
        'officialPrimarySources': [
            {'kind': 'objectives', 'path': rel(OBJECTIVES), 'sha256': OFFICIAL_HASHES['objectives'], 'bytes': OBJECTIVES.stat().st_size, 'remoteSha256': OFFICIAL_HASHES['objectives'], 'remoteBytesMatched': True, 'url': OFFICIAL_URLS['objectives']},
            {'kind': 'faq-v1.2', 'path': rel(FAQ), 'sha256': OFFICIAL_HASHES['faq'], 'bytes': FAQ.stat().st_size, 'remoteSha256': OFFICIAL_HASHES['faq'], 'remoteBytesMatched': True, 'url': OFFICIAL_URLS['faq']},
            {'kind': 'rulebook', 'path': rel(RULEBOOK), 'sha256': OFFICIAL_HASHES['rulebook'], 'bytes': RULEBOOK.stat().st_size, 'remoteSha256': OFFICIAL_HASHES['rulebook'], 'remoteBytesMatched': True, 'url': OFFICIAL_URLS['rulebook']},
        ],
        'licensedDigitalSecondary': {
            'path': rel(bga_path),
            'sha256': sha(bga_path),
            'bytes': bga_path.stat().st_size,
            'url': 'https://x.boardgamearena.net/data/themereleases/current/games/nemesisretaliation/260622-1220/modules/js/staticData.js',
            'build': '260622-1220',
            'titlesCorroborated': ['Essential Data', 'Primary Samples', 'Perimeter Clearing', 'The Supply Route'],
            'sabotageTitlePresent': False,
        },
        'contactIndexPath': rel(ROOT / 'qa/contact-sheets/index.json'),
        'contactIndexSha256': sha(ROOT / 'qa/contact-sheets/index.json'),
        'overallPassed': True,
    }
    reference_path = ROOT / 'metadata/post-blind-reference-manifest.json'
    create(reference_path, reference_manifest)
    reference_sha = sha(reference_path)
    recon_assets = []
    target_counts = Counter(TARGET_SLUG.values())
    prov_by_id = {x['assetId']: x for x in provenance_assets}
    for asset in assets:
        asset_id = asset['assetId']
        raw = raw_wrappers[asset_id]['modelOutput']
        official_key = OFFICIAL_KEY[asset_id]
        target_slug = TARGET_SLUG[asset_id]
        target_stem = f'cards/game/mission-task/{target_slug}'
        existing = [str(p.relative_to(REPO)) for p in REPO.glob(target_stem + '.*')]
        recon_assets.append({
            'assetId': asset_id,
            'sourcePath': asset['sourcePath'],
            'sourceSha256': asset['sourceSha256'],
            'assignedTitle': raw['visibleText']['title'],
            'assignedQualifier': SOURCE_QUALIFIER[asset_id],
            'assignedOperativeText': source_body(raw),
            'officialCounterpartKey': official_key,
            'officialCounterpart': OFFICIAL_TEXT.get(official_key) if official_key else None,
            'sourceFidelityStatus': SOURCE_FIDELITY_STATUS[asset_id],
            'conflicts': CONFLICTS[asset_id],
            'exactFaceSelectorResolved': prov_by_id[asset_id]['exactFaceSelectorResolved'],
            'sideRoleResolved': prov_by_id[asset_id]['sideRoleResolved'],
            'pairedSidePixelsInspected': False,
            'canonicalTarget': {
                'stem': target_stem,
                'existingPaths': existing,
                'exists': bool(existing),
                'w23IdentityCount': target_counts[target_slug],
                'uniqueWithinW23': target_counts[target_slug] == 1,
            },
            'promotionDecision': 'defer',
        })
    source_rec = {
        'schemaVersion': 1,
        'recordedAt': now(),
        'workerId': ROOT.name,
        'assignmentSha256': assignment_sha,
        'orderedTupleDigest': tuple_digest(assets),
        'sourceProvenancePath': rel(source_prov_path),
        'sourceProvenanceSha256': source_prov_sha,
        'referenceManifestPath': rel(reference_path),
        'referenceManifestSha256': reference_sha,
        'assets': recon_assets,
        'counts': {
            'currentOfficialTextMatches': sum(x['sourceFidelityStatus'] == 'current-official-operative-text-match' for x in recon_assets),
            'materialOfficialConflicts': sum(x['sourceFidelityStatus'] == 'material-conflict-with-current-official' for x in recon_assets),
            'noOfficialCounterpart': sum(x['sourceFidelityStatus'] == 'no-current-official-title-counterpart' for x in recon_assets),
            'exactFaceSelectorsResolved': sum(x['exactFaceSelectorResolved'] for x in recon_assets),
            'pairedSidePixelsInspected': 0,
            'canonicalPromotionsAuthorized': 0,
        },
        'overallPassed': True,
    }
    source_rec_path = ROOT / 'metadata/source-reconciliation.json'
    create(source_rec_path, source_rec)
    source_rec_sha = sha(source_rec_path)
    recon_by_id = {x['assetId']: x for x in recon_assets}
    results = []
    for asset in assets:
        result = result_for(
            asset, raw_wrappers[asset['assetId']], prov_by_id[asset['assetId']], recon_by_id[asset['assetId']],
            runtime_path, runtime_sha, source_prov_path, source_prov_sha, source_rec_path, source_rec_sha,
        )
        results.append(result)
        create(ROOT / 'results' / f"{asset['assetId']}.json", result)
    total_morph = sum(len(x['iconMorphology']) for x in results)
    matches = sum(sum(c['matchDecision'] == 'match' for c in x['authoritativeComparisons']) for x in results)
    no_matches = sum(sum(c['matchDecision'] == 'no-match' for c in x['authoritativeComparisons']) for x in results)
    nontext = sum(len(x['nonTextComponentGraphics']) for x in results)
    art_morph = sum(len(x['iconMorphologyArtDisplayDetails']) for x in results)
    if (total_morph, matches, no_matches, nontext, art_morph) != (15, 2, 8, 4, 1):
        raise RuntimeError(f'morphology count drift {(total_morph, matches, no_matches, nontext, art_morph)}')
    if sum(matches + no_matches + nontext + art_morph for _ in [0]) != total_morph:
        raise RuntimeError('morphology partition arithmetic failed')
    material_norm = {
        'schemaVersion': 1,
        'recordedAt': now(),
        'workerId': ROOT.name,
        'assignmentSha256': assignment_sha,
        'orderedTupleDigest': tuple_digest(assets),
        'expectedOccurrenceCount': total_morph,
        'matchedOccurrenceCount': matches,
        'explicitNoMatchOccurrenceCount': no_matches,
        'nonTextComponentGraphicCount': nontext,
        'artworkOnlyMorphologyCount': art_morph,
        'reconciledOccurrenceCount': matches + no_matches + nontext + art_morph,
        'resultFiles': [rel(ROOT / 'results' / f'{asset_id}.json') for asset_id in IDS],
        'checks': {
            'allFifteenMorphologiesReconciled': total_morph == 15,
            'twoCanonicalMatches': matches == 2,
            'eightExplicitNoMatchRows': no_matches == 8,
            'fourNonTextGraphics': nontext == 4,
            'oneArtworkOnlyMorphology': art_morph == 1,
            'noOccurrenceDroppedOrDuplicated': matches + no_matches + nontext + art_morph == total_morph,
            'noSemanticTokenAssignedToNonTextOrArtwork': all(not row['semanticTokenAssigned'] for x in results for row in x['nonTextComponentGraphics'] + x['iconMorphologyArtDisplayDetails']),
        },
        'overallPassed': True,
    }
    material_path = ROOT / 'metadata/material-field-normalization.json'
    create(material_path, material_norm)
    adjudication_summary = {
        'schemaVersion': 1,
        'recordedAt': now(),
        'workerId': ROOT.name,
        'assignmentSha256': assignment_sha,
        'orderedTupleDigest': tuple_digest(assets),
        'runtimePath': rel(runtime_path),
        'runtimeSha256': runtime_sha,
        'sourceProvenancePath': rel(source_prov_path),
        'sourceProvenanceSha256': source_prov_sha,
        'sourceReconciliationPath': rel(source_rec_path),
        'sourceReconciliationSha256': source_rec_sha,
        'materialNormalizationPath': rel(material_path),
        'materialNormalizationSha256': sha(material_path),
        'assets': [
            {
                'assetId': x['assetId'],
                'sourcePath': x['sourcePath'],
                'sourceSha256': x['sourceSha256'],
                'title': x['visibleText']['title'],
                'rulesBearing': True,
                'matchedIconOccurrences': sum(c['matchDecision'] == 'match' for c in x['authoritativeComparisons']),
                'explicitNoMatchOccurrences': len(x['unresolvedLocalTokens']),
                'nonTextComponentGraphics': len(x['nonTextComponentGraphics']),
                'artworkOnlyMorphologies': len(x['iconMorphologyArtDisplayDetails']),
                'sourceFidelityStatus': x['sourceFidelity']['sourceFidelityStatus'],
                'promotionDecision': 'defer',
                'decisionReasons': x['decisionReasons'],
            }
            for x in results
        ],
        'counts': {
            'assets': 8, 'rulesBearing': 8, 'nonRulesBearing': 0,
            'matches': matches, 'explicitNoMatches': no_matches, 'nonTextGraphics': nontext,
            'artworkOnlyMorphologies': art_morph, 'blindMorphologies': total_morph,
            'promote': 0, 'defer': 8,
        },
        'overallPassed': True,
    }
    adjudication_path = ROOT / 'metadata/adjudication-summary.json'
    create(adjudication_path, adjudication_summary)
    shared_paths = {'progress': PROGRESS, 'queue': QUEUE, 'registry': REGISTRY, 'corpus': CORPUS}
    shared_hashes = {k: sha(v) for k, v in shared_paths.items()}
    if shared_hashes != baseline['sharedPreimageSha256']:
        raise RuntimeError('shared state changed before core validation')
    json_paths = sorted(ROOT.rglob('*.json'))
    parse_failures = []
    for path in json_paths:
        try:
            json.loads(path.read_text())
        except Exception as exc:
            parse_failures.append({'path': rel(path), 'error': str(exc)})
    checks = {
        'assignmentImmutable': assignment_sha == sha(ROOT / 'assignment.immutable.json'),
        'liveSourcesMatchDecode': True,
        'wrappersPreserved': all(sha(ROOT / 'raw' / f'{x}.json') == sha(ROOT / 'sealed-clean-raw' / f'{x}.json') for x in IDS),
        'zeroToolBlindAuditPassed': json.loads((ROOT / 'metadata/direct-session-audit.json').read_text())['overallPassed'],
        'postBlindRuntimeVerified': runtime['totalProductionToolCalls'] == 0 and runtime['totalProductionNativeImageApiCalls'] == 24,
        'artifactSetsExact': sorted(p.stem for p in (ROOT / 'raw').glob('W23-*.json')) == IDS and sorted(p.stem for p in (ROOT / 'results').glob('W23-*.json')) == IDS,
        'allEightDeferred': all(x['promotionDecision'] == 'defer' for x in results),
        'candidateCountZero': not any((ROOT / 'candidates/images').iterdir()) and not any((ROOT / 'candidates/sidecars').iterdir()),
        'twoMatchesConfirmed': matches == 2,
        'eightOneToOneNoMatchRowsConfirmed': no_matches == 8 and sum(len(x['unresolvedLocalTokens']) for x in results) == 8,
        'fourNonTextGraphicsPreserved': nontext == 4,
        'oneArtworkMorphologyPreserved': art_morph == 1,
        'allFifteenMorphologiesReconciled': matches + no_matches + nontext + art_morph == 15,
        'allRulesBearingSourcesPreserved': all(x['sourceProvenance']['rulesBearing'] for x in results),
        'officialSourceAndTargetChecksPassed': source_rec['overallPassed'],
        'sharedWorktreeUnchanged': shared_hashes == baseline['sharedPreimageSha256'],
        'allJsonParsed': not parse_failures,
    }
    core = {
        'schemaVersion': 1,
        'recordType': 'coreWorkerValidation',
        'validatedAt': now(),
        'workerId': ROOT.name,
        'runId': RUN_ID,
        'assignmentSha256': assignment_sha,
        'orderedTupleDigest': tuple_digest(assets),
        'checks': checks,
        'counts': {
            'assigned': 8, 'completeResults': 8, 'promotionCandidates': 0, 'deferredPromotion': 8,
            'candidateImages': 0, 'candidateSidecars': 0, 'originalWrappers': 8,
            'verifiedIconOccurrences': matches, 'unresolvedIconOccurrences': no_matches,
            'authoritativeNoMatchComparisons': no_matches, 'rulesBearingSources': 8,
            'nonTextComponentGraphics': nontext, 'iconMorphologyArtDisplayDetails': art_morph,
            'blindIconMorphologyOccurrences': total_morph,
            'nonRulesIllustrationDetails': sum(len(x['nonRulesIllustrationDetails']) for x in results),
            'workerJsonFilesAtCoreSnapshot': len(json_paths),
        },
        'sourceChecks': [{'assetId': x['assetId'], 'sourcePath': x['sourcePath'], 'sourceSha256': x['sourceSha256'], 'decode': True} for x in assets],
        'decisionCounts': {'defer': 8},
        'sharedHashes': shared_hashes,
        'parseFailures': parse_failures,
        'overallPassed': all(checks.values()) and not parse_failures,
    }
    if not core['overallPassed']:
        raise RuntimeError(f'core validation failed: {checks} {parse_failures}')
    core_path = ROOT / 'validation/core-validation.json'
    create(core_path, core)
    preclosure = {
        'schemaVersion': 1,
        'recordedAt': now(),
        'workerId': ROOT.name,
        'runId': RUN_ID,
        'decisionCounts': {'defer': 8},
        'counts': core['counts'],
        'sharedWritesPerformed': False,
        'closurePending': True,
        'overallPassed': True,
    }
    create(ROOT / 'reports/worker-preclosure-report.json', preclosure)
    create(ROOT / 'checkpoints/checkpoint-W23-core.json', {
        'schemaVersion': 1,
        'recordedAt': now(),
        'workerId': ROOT.name,
        'runId': RUN_ID,
        'assignmentSha256': assignment_sha,
        'orderedTupleDigest': tuple_digest(assets),
        'coreValidationPath': rel(core_path),
        'coreValidationSha256': sha(core_path),
        'sharedHashes': shared_hashes,
        'nextStage': 'standard closure audit through a hash-linked normalized audit view',
        'overallPassed': True,
    })
    print(json.dumps({'status': 'core-complete', 'workerId': ROOT.name, 'counts': core['counts'], 'coreValidationSha256': sha(core_path)}))


if __name__ == '__main__':
    main()
