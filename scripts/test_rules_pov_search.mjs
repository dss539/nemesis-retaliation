import test from 'node:test';
import assert from 'node:assert/strict';
import { resolveSearch, SEARCH_GAPS } from './rules_pov_search.mjs';

function item(id, color, kind = 'regular', title = id, tacticalGearSlots = []) {
  return { id, color, kind, title, tacticalGearSlots };
}

function state(overrides = {}) {
  const base = {
    actionCards: {
      search1: { id: 'search1', effect: 'search', notInCombat: true },
    },
    items: {
      g1: item('g1', 'green', 'regular', 'MEDKIT'),
      g2: item('g2', 'green', 'regular', 'MEDKIT'),
      g3: item('g3', 'green'),
      r1: item('r1', 'red'),
      r2: item('r2', 'red'),
      y1: item('y1', 'yellow'),
      h1: item('h1', 'green', 'heavy', 'HEAVY OXYGEN TANK', ['oxygen', 'any']),
      held1: item('held1', 'red', 'heavy'),
      held2: item('held2', 'yellow', 'heavy'),
      a1: item('a1', 'green', 'armor', 'HEAVY ARMOR', ['any']),
      oldArmor: item('oldArmor', 'red', 'armor'),
    },
    itemDecks: {
      green: ['g1', 'g2', 'g3'],
      red: ['r1', 'r2'],
      yellow: ['y1'],
    },
    itemDiscard: [],
    players: {
      p1: {
        actionHand: ['search1'],
        actionDiscard: [],
        backpack: [],
        handSlots: [null, null],
        armorItemId: null,
        healthSection: 'healthy',
        inCombat: false,
      },
    },
    rooms: {
      room1: { itemIcons: ['green', 'red'] },
    },
    itemRuntime: {},
    tacticalGearPool: { ammo: 4, grenade: 4, oxygen: 4, medpack: 4 },
    publicEvents: [],
    privateEventsByPlayer: { p1: [] },
  };
  return merge(base, overrides);
}

function merge(base, overrides) {
  const result = structuredClone(base);
  for (const [key, value] of Object.entries(overrides)) {
    if (value && typeof value === 'object' && !Array.isArray(value) && result[key]) {
      result[key] = merge(result[key], value);
    } else {
      result[key] = structuredClone(value);
    }
  }
  return result;
}

function run(input = {}, sourceState = state()) {
  return resolveSearch({
    state: sourceState,
    actorId: 'p1',
    roomId: 'room1',
    searchCardId: 'search1',
    keepOccurrenceId: 'g1',
    policies: { keepCardinality: 'exactly-one' },
    ...input,
  });
}

function expectUnchanged(before, result) {
  assert.deepEqual(result.state, before);
  assert.deepEqual(before, structuredClone(before));
}

function publicText(result) {
  return JSON.stringify(result.state.publicEvents);
}

test('draws per icon, keeps exact occurrence, returns each unchosen card to its own deck bottom', () => {
  const result = run();
  assert.equal(result.status, 'resolved');
  assert.deepEqual(result.state.itemDecks.green, ['g2', 'g3']);
  assert.deepEqual(result.state.itemDecks.red, ['r2', 'r1']);
  assert.deepEqual(result.state.players.p1.backpack, ['g1']);
  assert.deepEqual(result.state.players.p1.actionHand, []);
  assert.deepEqual(result.state.players.p1.actionDiscard, ['search1']);
  assert.deepEqual(result.private.candidateOccurrenceIds, ['g1', 'r1']);
  assert.equal(result.state.publicEvents[0].type, 'action-card-revealed');
  assert.equal(result.state.publicEvents[1].type, 'item-gained');
  assert.equal(publicText(result).includes('r1'), false);
  assert.equal(publicText(result).includes('g1'), false);
  assert.deepEqual(result.state.itemRuntime.g1.tacticalGearTokens, []);
  assert.deepEqual(result.interpretations, {
    keepCardinality: 'exactly-one',
    sameDeckReturnOrder: null,
    nonBackpackVisibility: null,
  });
});

test('draws once for each duplicate same-color icon and preserves deck order', () => {
  const source = state({ rooms: { room1: { itemIcons: ['green', 'green'] } } });
  const result = run({ keepOccurrenceId: 'g2' }, source);
  assert.equal(result.status, 'resolved');
  assert.deepEqual(result.private.candidateOccurrenceIds, ['g1', 'g2']);
  assert.deepEqual(result.state.itemDecks.green, ['g3', 'g1']);
  assert.deepEqual(result.state.players.p1.backpack, ['g2']);
});

test('multiple same-deck unchosen returns require an explicit ordering policy', () => {
  const source = state({ rooms: { room1: { itemIcons: ['green', 'green'] } } });
  const result = run({
    keepOccurrenceId: null,
    policies: { keepCardinality: 'zero-or-one' },
  }, source);
  assert.equal(result.status, 'unresolved');
  assert.deepEqual(result.gaps, [SEARCH_GAPS.SAME_DECK_RETURN_ORDER]);
  expectUnchanged(source, result);
});

test('explicit reverse-draw return policy is recorded and applied', () => {
  const source = state({ rooms: { room1: { itemIcons: ['green', 'green'] } } });
  const result = run({
    keepOccurrenceId: null,
    policies: { keepCardinality: 'zero-or-one', sameDeckReturnOrder: 'reverse-draw-order' },
  }, source);
  assert.equal(result.status, 'resolved');
  assert.deepEqual(result.state.itemDecks.green, ['g3', 'g2', 'g1']);
  assert.equal(result.interpretations.sameDeckReturnOrder, 'reverse-draw-order');
});

test('duplicate-title cards remain distinct physical occurrences', () => {
  const source = state({ rooms: { room1: { itemIcons: ['green', 'green'] } } });
  const result = run({ keepOccurrenceId: 'g2' }, source);
  assert.equal(source.items.g1.title, source.items.g2.title);
  assert.deepEqual(result.state.players.p1.backpack, ['g2']);
  assert.deepEqual(result.state.itemDecks.green, ['g3', 'g1']);
});

test('regular Backpack is unlimited and its gained identity stays out of public events', () => {
  const existing = Array.from({ length: 50 }, (_, index) => `existing-${index}`);
  const source = state({ players: { p1: { backpack: existing } } });
  const result = run({}, source);
  assert.equal(result.status, 'resolved');
  assert.equal(result.state.players.p1.backpack.length, 51);
  assert.equal(result.state.players.p1.backpack.at(-1), 'g1');
  assert.equal(publicText(result).includes('g1'), false);
});

test('Heavy Item uses an empty Hand slot when an explicit non-Backpack visibility policy exists', () => {
  const source = state({ itemDecks: { green: ['h1'], red: ['r1', 'r2'] } });
  const result = run({
    keepOccurrenceId: 'h1',
    tacticalGearAllocation: ['oxygen', 'medpack'],
    policies: { keepCardinality: 'exactly-one', nonBackpackVisibility: 'public' },
  }, source);
  assert.equal(result.status, 'resolved');
  assert.deepEqual(result.state.players.p1.handSlots, ['h1', null]);
  assert.deepEqual(result.state.players.p1.backpack, []);
  assert.deepEqual(result.state.itemRuntime.h1.tacticalGearTokens, ['oxygen', 'medpack']);
  assert.equal(result.state.tacticalGearPool.oxygen, 3);
  assert.equal(result.state.tacticalGearPool.medpack, 3);
  assert.equal(publicText(result).includes('h1'), true);
});

test('full Hands require an explicit owner displacement and use the source-defined Items discard pile', () => {
  const source = state({
    itemDecks: { green: ['h1'], red: ['r1', 'r2'] },
    players: { p1: { handSlots: ['held1', 'held2'] } },
  });
  const result = run({
    keepOccurrenceId: 'h1',
    discardHeldItemId: 'held2',
    tacticalGearAllocation: ['oxygen', 'medpack'],
    policies: {
      keepCardinality: 'exactly-one',
      nonBackpackVisibility: 'public',
    },
  }, source);
  assert.equal(result.status, 'resolved');
  assert.deepEqual(result.state.players.p1.handSlots, ['held1', 'h1']);
  assert.deepEqual(result.state.itemDiscard, ['held2']);
});

test('full Hands without an owner displacement do not overwrite state', () => {
  const source = state({
    itemDecks: { green: ['h1'], red: ['r1', 'r2'] },
    players: { p1: { handSlots: ['held1', 'held2'] } },
  });
  const result = run({
    keepOccurrenceId: 'h1',
    policies: { keepCardinality: 'exactly-one', nonBackpackVisibility: 'public' },
  }, source);
  assert.equal(result.status, 'unresolved');
  assert.ok(result.gaps.includes(SEARCH_GAPS.POST_DRAW_STORAGE));
  expectUnchanged(source, result);
});

test('Armor uses the Health-track position and is fully loaded', () => {
  const source = state({ itemDecks: { green: ['a1'], red: ['r1', 'r2'] } });
  const result = run({
    keepOccurrenceId: 'a1',
    tacticalGearAllocation: ['ammo'],
    policies: { keepCardinality: 'exactly-one', nonBackpackVisibility: 'public' },
  }, source);
  assert.equal(result.status, 'resolved');
  assert.equal(result.state.players.p1.armorItemId, 'a1');
  assert.deepEqual(result.state.players.p1.backpack, []);
  assert.deepEqual(result.state.itemRuntime.a1.tacticalGearTokens, ['ammo']);
});

test('existing Armor replacement requires explicit choice and uses the Items discard pile', () => {
  const source = state({
    itemDecks: { green: ['a1'], red: ['r1', 'r2'] },
    players: { p1: { armorItemId: 'oldArmor' } },
  });
  const result = run({
    keepOccurrenceId: 'a1',
    replaceArmor: true,
    tacticalGearAllocation: ['ammo'],
    policies: {
      keepCardinality: 'exactly-one',
      nonBackpackVisibility: 'public',
    },
  }, source);
  assert.equal(result.status, 'resolved');
  assert.equal(result.state.players.p1.armorItemId, 'a1');
  assert.deepEqual(result.state.itemDiscard, ['oldArmor']);
});

test('Armor at Heavily Injured follows the source-defined failed-gain discard path', () => {
  const source = state({
    itemDecks: { green: ['a1'], red: ['r1', 'r2'] },
    players: { p1: { healthSection: 'heavily-injured' } },
  });
  const result = run({
    keepOccurrenceId: 'a1',
    policies: { keepCardinality: 'exactly-one' },
  }, source);
  assert.equal(result.status, 'resolved');
  assert.equal(result.state.players.p1.armorItemId, null);
  assert.deepEqual(result.state.itemDiscard, ['a1']);
  assert.equal(result.state.itemRuntime.a1, undefined);
  assert.deepEqual(result.state.players.p1.actionDiscard, ['search1']);
  assert.equal(publicText(result).includes('a1'), false);
});

test('Not In Combat rejection leaves card and all state untouched', () => {
  const source = state({ players: { p1: { inCombat: true } } });
  const result = run({}, source);
  assert.equal(result.status, 'illegal');
  assert.equal(result.reason, 'not-in-combat');
  assert.deepEqual(result.gaps, []);
  expectUnchanged(source, result);
});

test('empty required Item deck is unresolved rather than silently defaulted', () => {
  const source = state({ itemDecks: { red: [] } });
  const result = run({}, source);
  assert.equal(result.status, 'unresolved');
  assert.deepEqual(result.gaps, [SEARCH_GAPS.EMPTY_ITEM_DECK]);
  expectUnchanged(source, result);
});

test('zero-versus-one keep conflict requires an explicit policy', () => {
  const source = state();
  const result = run({ policies: {} }, source);
  assert.equal(result.status, 'unresolved');
  assert.deepEqual(result.gaps, [SEARCH_GAPS.KEEP_CARDINALITY]);
  expectUnchanged(source, result);
});

test('displaced Items always use the source-defined Items discard pile', () => {
  const source = state({
    itemDecks: { green: ['h1'], red: ['r1', 'r2'] },
    players: { p1: { handSlots: ['held1', 'held2'] } },
  });
  const result = run({
    keepOccurrenceId: 'h1',
    discardHeldItemId: 'held1',
    tacticalGearAllocation: ['oxygen', 'medpack'],
    policies: { keepCardinality: 'exactly-one', nonBackpackVisibility: 'public' },
  }, source);
  assert.equal(result.status, 'resolved');
  assert.deepEqual(result.state.itemDiscard, ['held1']);
  assert.deepEqual(result.state.players.p1.handSlots, ['h1', 'held2']);
});

test('Fully Loaded allocation is unresolved when an Item has slots but no allocation policy', () => {
  const source = state({ itemDecks: { green: ['h1'], red: ['r1', 'r2'] } });
  const result = run({
    keepOccurrenceId: 'h1',
    policies: { keepCardinality: 'exactly-one', nonBackpackVisibility: 'public' },
  }, source);
  assert.equal(result.status, 'unresolved');
  assert.deepEqual(result.gaps, [SEARCH_GAPS.TACTICAL_GEAR_ALLOCATION]);
  expectUnchanged(source, result);
});

test('Fully Loaded rejects a token incompatible with its exact slot', () => {
  const source = state({ itemDecks: { green: ['h1'], red: ['r1', 'r2'] } });
  const result = run({
    keepOccurrenceId: 'h1',
    tacticalGearAllocation: ['grenade', 'medpack'],
    policies: { keepCardinality: 'exactly-one', nonBackpackVisibility: 'public' },
  }, source);
  assert.equal(result.status, 'illegal');
  assert.equal(result.reason, 'incompatible-tactical-gear-token:0');
  expectUnchanged(source, result);
});

test('Fully Loaded does not invent tokens when the finite pool is exhausted', () => {
  const source = state({
    itemDecks: { green: ['h1'], red: ['r1', 'r2'] },
    tacticalGearPool: { oxygen: 0 },
  });
  const result = run({
    keepOccurrenceId: 'h1',
    tacticalGearAllocation: ['oxygen', 'medpack'],
    policies: { keepCardinality: 'exactly-one', nonBackpackVisibility: 'public' },
  }, source);
  assert.equal(result.status, 'unresolved');
  assert.deepEqual(result.gaps, [SEARCH_GAPS.TACTICAL_GEAR_ALLOCATION]);
  expectUnchanged(source, result);
});

test('invalid non-Backpack visibility policies are rejected rather than treated as secret', () => {
  const source = state({ itemDecks: { green: ['h1'], red: ['r1', 'r2'] } });
  const result = run({
    keepOccurrenceId: 'h1',
    policies: { keepCardinality: 'exactly-one', nonBackpackVisibility: 'banana' },
  }, source);
  assert.equal(result.status, 'illegal');
  assert.equal(result.reason, 'unsupported-non-backpack-visibility-policy');
  expectUnchanged(source, result);
});

test('missing Tactical Gear slot data is rejected rather than silently treated as zero', () => {
  const source = state({ items: { g1: { tacticalGearSlots: null } } });
  const result = run({}, source);
  assert.equal(result.status, 'illegal');
  assert.equal(result.reason, 'item-tactical-gear-slots-missing-or-invalid');
  expectUnchanged(source, result);
});

test('non-Backpack chosen Item visibility is a required external policy', () => {
  const source = state({ itemDecks: { green: ['h1'], red: ['r1', 'r2'] } });
  const result = run({
    keepOccurrenceId: 'h1',
    policies: { keepCardinality: 'exactly-one' },
  }, source);
  assert.equal(result.status, 'unresolved');
  assert.deepEqual(result.gaps, [SEARCH_GAPS.NON_BACKPACK_VISIBILITY]);
  expectUnchanged(source, result);
});
