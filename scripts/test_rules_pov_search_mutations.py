#!/usr/bin/env python3
"""Mutation controls for the preregistered Search implementation pilot."""
from __future__ import annotations
import subprocess
import tempfile
import unittest
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
MODULE = REPO / "scripts/rules_pov_search.mjs"
TEST = REPO / "scripts/test_rules_pov_search.mjs"
MUTATIONS = {
    "M01": (
        "for (const color of next.rooms[roomId].itemIcons) {",
        "for (const color of next.rooms[roomId].itemIcons.slice(0, 1)) {",
    ),
    "M02": (
        """for (const color of next.rooms[roomId].itemIcons) {
    const deck = next.itemDecks[color];
    const itemId = deck.shift();""",
        """for (const color of next.rooms[roomId].itemIcons) {
    const deck = next.itemDecks.green;
    const itemId = deck.shift();""",
    ),
    "M03": (
        "next.itemDecks[color].push(...ordered);",
        "next.itemDiscard.push(...ordered);",
    ),
    "M04": (
        """if (kept) next.publicEvents.push(publicGainEvent(actorId, kept.itemId, plan));""",
        """if (kept) next.publicEvents.push(publicGainEvent(actorId, kept.itemId, plan));
  next.publicEvents.push({ type: 'search-candidates', itemIds: candidates.map(({ itemId }) => itemId) });""",
    ),
    "M05": (
        "candidates.find(({ itemId }) => itemId === keepOccurrenceId)",
        "candidates.find(({ itemId }) => next.items[itemId].title === next.items[keepOccurrenceId].title)",
    ),
    "M06": (
        "if (item.kind === 'regular') return { storage: 'backpack' };",
        """if (item.kind === 'regular') {
    if (actor.backpack.length >= 1) return { gaps: [SEARCH_GAPS.POST_DRAW_STORAGE] };
    return { storage: 'backpack' };
  }""",
    ),
    "M07": (
        "if (plan.storage === 'hand') actor.handSlots[plan.slotIndex] = itemId;",
        "if (plan.storage === 'hand') actor.backpack.push(itemId);",
    ),
    "M08": (
        """if (!input.discardHeldItemId) {
      return { gaps: [SEARCH_GAPS.POST_DRAW_STORAGE] };
    }""",
        """if (!input.discardHeldItemId) {
      return { storage: 'hand', slotIndex: 0, visibility: policies.nonBackpackVisibility };
    }""",
    ),
    "M09": (
        "if (plan.storage === 'armor') actor.armorItemId = itemId;",
        "if (plan.storage === 'armor') actor.backpack.push(itemId);",
    ),
    "M10": (
        "if (item.kind === 'armor' && actor.healthSection === 'heavily-injured') {",
        "if (false) {",
    ),
    "M11": (
        "if (card.notInCombat && actor.inCombat) {",
        "if (false) {",
    ),
    "M12": (
        """const drawCounts = requiredDraws(state.rooms[roomId].itemIcons);
  for (const [color, count] of drawCounts) {
    const deck = state.itemDecks[color];
    if (!deck || deck.length < count) {
      return unresolved(state, [SEARCH_GAPS.EMPTY_ITEM_DECK], `insufficient-${color}-item-cards`);
    }
  }

  const next = structuredClone(state);
  next.publicEvents.push({ type: 'action-card-revealed', actorId, cardId: searchCardId });
  const candidates = [];
  for (const color of next.rooms[roomId].itemIcons) {
    const deck = next.itemDecks[color];
    const itemId = deck.shift();
    candidates.push({ itemId, color });
  }""",
        """const next = structuredClone(state);
  next.publicEvents.push({ type: 'action-card-revealed', actorId, cardId: searchCardId });
  const candidates = [];
  for (const color of next.rooms[roomId].itemIcons) {
    const deck = next.itemDecks[color];
    const itemId = deck.shift();
    if (itemId === undefined) continue;
    candidates.push({ itemId, color });
  }""",
    ),
    "M13": (
        """if (!policies.keepCardinality) {
    return unresolved(state, [SEARCH_GAPS.KEEP_CARDINALITY], 'keep-cardinality-policy-required');
  }""",
        """if (!policies.keepCardinality) {
    policies.keepCardinality = 'zero-or-one';
  }""",
    ),
    "M14": (
        """function applyDiscard(state, itemId) {
  state.itemDiscard.push(itemId);
}""",
        """function applyDiscard(state, itemId) {
  const item = state.items[itemId];
  state.itemDecks[item.color].push(itemId);
}""",
    ),
    "M15": (
        """const allocation = input.tacticalGearAllocation;
  if (!Array.isArray(allocation) || allocation.length !== slots.length) {
    return { gaps: [SEARCH_GAPS.TACTICAL_GEAR_ALLOCATION] };
  }""",
        """const allocation = Array.isArray(input.tacticalGearAllocation)
    ? input.tacticalGearAllocation
    : slots.map((slot) => slot === 'any' ? 'ammo' : slot);""",
    ),
    "M16": (
        "if (slot !== 'any' && slot !== token) {",
        "if (false) {",
    ),
    "M17": (
        "if (!Number.isInteger(remaining[token]) || remaining[token] <= 0) {",
        "if (false) {",
    ),
}
class SearchPilotMutationTests(unittest.TestCase):
    def test_every_preregistered_mutation_is_killed(self) -> None:
        source = MODULE.read_text(encoding="utf-8")
        test_source = TEST.read_text(encoding="utf-8")
        killed: list[str] = []
        for mutation_id, (old, new) in MUTATIONS.items():
            with self.subTest(mutation=mutation_id):
                self.assertEqual(source.count(old), 1, f"{mutation_id} mutation anchor drift")
                with tempfile.TemporaryDirectory(prefix=f"search-pov-{mutation_id.lower()}-") as temporary:
                    root = Path(temporary)
                    (root / MODULE.name).write_text(source.replace(old, new), encoding="utf-8")
                    (root / TEST.name).write_text(test_source, encoding="utf-8")
                    result = subprocess.run(
                        ["node", "--test", str(root / TEST.name)],
                        cwd=root,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        check=False,
                    )
                    self.assertNotEqual(result.returncode, 0, f"{mutation_id} survived\n{result.stdout}")
                    killed.append(mutation_id)
        self.assertEqual(killed, list(MUTATIONS))
if __name__ == "__main__":
    unittest.main(verbosity=2)
