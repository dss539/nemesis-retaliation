#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import analyze_unresolved_symbols as backlog
import build_card_text_corpus as corpus
import vision_batch


class SemanticIconResolutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = corpus.build_payload()
        cls.rows = {row["sourcePath"]: row for row in cls.payload["records"]}

    def test_registry_is_source_scoped_and_uses_known_tokens(self):
        known = corpus.glossary_ids()
        registry, index = corpus.semantic_icon_resolution_index(known)
        self.assertEqual(registry["schemaVersion"], 1)
        self.assertEqual(len(index), 8)
        self.assertEqual(sum(len(items) for items in index.values()), 12)
        self.assertEqual(self.payload["generatedFrom"]["semanticIconResolutionSourceCount"], 8)
        self.assertEqual(self.payload["generatedFrom"]["semanticIconResolutionCount"], 12)
        self.assertTrue(all(item["canonicalToken"] in known for items in index.values() for item in items))

    def test_reviewed_plasma_uses_canonical_semantics_and_keeps_resolution_evidence(self):
        path = "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-11.png"
        row = self.rows[path]
        body = row["printedData"]["body"]
        self.assertIn("[burstDieAdditionalEffects], [shootDieAmmoLoss]:", body)
        self.assertNotIn("[ICON:", body)
        self.assertEqual(row["symbols"]["unresolvedOrLocalTokens"], [])
        ids = {item["resolutionId"] for item in row["evidence"]["semanticIconResolutions"]}
        self.assertEqual(ids, {
            "legacy-purple-exclamation-is-burst-additional-effects",
            "legacy-red-magazine-triangle-is-shoot-ammo-loss",
        })

    def test_all_approved_legacy_weapon_results_are_normalized(self):
        expected = {
            "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-025.png": "burstDieAdditionalEffects",
            "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-131.png": "burstDieAdditionalEffects",
            "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-05.png": "burstDieAdditionalEffects",
            "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-06.png": "burstDieAdditionalEffects",
            "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-09.png": "shootDieAmmoLoss",
            "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-11.png": "shootDieAmmoLoss",
            "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-17.png": "shootDieAmmoLoss",
        }
        for path, token in expected.items():
            with self.subTest(path=path, token=token):
                self.assertIn(f"[{token}]", self.rows[path]["printedData"]["body"])

    def test_backlog_excludes_semantically_resolved_raw_no_matches(self):
        for path in (
            "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-131.png",
            "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-06.png",
            "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-09.png",
            "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-11.png",
            "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-17.png",
        ):
            with self.subTest(path=path):
                self.assertEqual(backlog.unresolved_occurrences(self.rows[path]), [])
        flame = self.rows["assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-05.png"]
        remaining = backlog.unresolved_occurrences(flame)
        self.assertEqual(len(remaining), 1)
        self.assertIn("rounded lobes", remaining[0]["token"])


    def test_vision_helpers_resolve_the_active_worktree(self):
        expected = Path(__file__).resolve().parents[3]
        self.assertEqual(vision_batch.REPO, expected)


    def test_reviewed_wrong_call_uses_number_of_characters_metadata(self):
        path = "assets/tts-mod/extract/v2-dl/tree/cards/game/objectivePersonalDeck-161.jpg"
        row = self.rows[path]
        self.assertIn("numberOfCharacters", corpus.glossary_ids())
        section = next(item for item in row["printedData"]["sections"] if item["panelId"] == "P2")
        self.assertEqual(section["text"], "[numberOfCharacters] 10+")
        self.assertIn("numberOfCharacters", row["symbols"]["canonicalGlossaryTokens"])
        self.assertEqual(row["evidence"]["manualReview"]["verdict"], "C")
        ids = {item["resolutionId"] for item in row["evidence"]["semanticIconResolutions"]}
        self.assertEqual(ids, {"official-number-of-characters-objective-metadata"})
        remaining = backlog.unresolved_occurrences(row)
        self.assertEqual(len(remaining), 1)
        self.assertIn("OR", remaining[0]["token"])


    def test_reviewed_leg_excludes_scan_overlay_from_rules_data(self):
        path = "assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-04.png"
        row = self.rows[path]
        self.assertEqual(row["extractionState"], "draft-full")
        self.assertEqual(row["rulesInformationReadiness"], "draft-text-complete")
        self.assertEqual(row["symbols"]["canonicalGlossaryTokens"], ["actionCard", "intruder"])
        self.assertEqual(row["symbols"]["unresolvedOrLocalTokens"], [])
        self.assertEqual(row["evidence"]["manualReview"]["verdict"], "P")
        self.assertNotIn("P3", {item["panelId"] for item in row["printedData"]["sections"]})
        self.assertEqual(row["printedData"]["illegibleSpans"], [])
        self.assertEqual(backlog.unresolved_occurrences(row), [])
        selected_p3 = next(item for item in row["selectedExtraction"]["visibleText"]["sections"] if item["panelId"] == "P3")
        self.assertIn("[illegible]", selected_p3["text"])
        self.assertEqual(row["ledgerStatus"], "deferred")


if __name__ == "__main__":
    unittest.main()
