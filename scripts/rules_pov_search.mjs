// Disposable executable contract for the preregistered Search pilot.
// Source: official rulebook lines 2871-2875, 3177-3179, 3188-3191,
// 3543-3548, 3665-3673, 4849-4865, 4899-4910, 4933-4948, 5024-5057,
// plus the exact Search Action-card face. It deliberately imports no semantic data.
export const SEARCH_GAPS = Object.freeze({
  EMPTY_ITEM_DECK: 'A-1',
  POST_DRAW_STORAGE: 'A-2/A-3',
  CANDIDATE_VISIBILITY: 'A-4',
  NON_BACKPACK_VISIBILITY: 'A-5',
  KEEP_CARDINALITY: 'A-7',
  SAME_DECK_RETURN_ORDER: 'A-9',
  TACTICAL_GEAR_ALLOCATION: 'A-10',
});
function unchangedResult(state, status, details = {}) {
  return { status, state: structuredClone(state), ...details };
}
function unresolved(state, gaps, reason) {
  return unchangedResult(state, 'unresolved', { gaps: [...new Set(gaps)], reason });
}
function invalid(state, reason, gaps = []) {
  return unchangedResult(state, 'illegal', { reason, gaps });
}
function validateInput(state, actorId, roomId, searchCardId) {
  const actor = state.players?.[actorId];
  const room = state.rooms?.[roomId];
  const card = state.actionCards?.[searchCardId];
  if (!actor || !room || !card) return 'missing-actor-room-or-card';
  if (!actor.actionHand.includes(searchCardId)) return 'search-card-not-in-hand';
  if (card.effect !== 'search') return 'card-is-not-search';
  if (!Array.isArray(room.itemIcons) || room.itemIcons.length === 0) return 'room-has-no-item-icons';
  return null;
}
function requiredDraws(itemIcons) {
  const counts = new Map();
  for (const color of itemIcons) {
    counts.set(color, (counts.get(color) ?? 0) + 1);
  }
  return counts;
}

function applyDiscard(state, itemId) {
  state.itemDiscard.push(itemId);
}

function planStorage(original, itemId, actorId, input, policies) {
  const actor = original.players[actorId];
  const item = original.items[itemId];
  if (!item) return { illegal: 'chosen-item-definition-missing' };
  if (!Array.isArray(item.tacticalGearSlots)) {
    return { illegal: 'item-tactical-gear-slots-missing-or-invalid' };
  }

  if (item.kind === 'regular') return { storage: 'backpack' };

  if (item.kind === 'armor' && actor.healthSection === 'heavily-injured') {
    return { storage: 'item-discard' };
  }

  if (!policies.nonBackpackVisibility) {
    return { gaps: [SEARCH_GAPS.NON_BACKPACK_VISIBILITY] };
  }

  if (item.kind === 'heavy') {
    const emptyIndex = actor.handSlots.indexOf(null);
    if (emptyIndex >= 0) {
      return { storage: 'hand', slotIndex: emptyIndex, visibility: policies.nonBackpackVisibility };
    }
    if (!input.discardHeldItemId) {
      return { gaps: [SEARCH_GAPS.POST_DRAW_STORAGE] };
    }
    const slotIndex = actor.handSlots.indexOf(input.discardHeldItemId);
    if (slotIndex < 0) return { illegal: 'displaced-item-is-not-in-a-hand-slot' };
    return {
      storage: 'hand',
      slotIndex,
      discardItemId: input.discardHeldItemId,
      visibility: policies.nonBackpackVisibility,
    };
  }

  if (item.kind === 'armor') {
    if (!actor.armorItemId) {
      return { storage: 'armor', visibility: policies.nonBackpackVisibility };
    }
    if (input.replaceArmor !== true) {
      return { gaps: [SEARCH_GAPS.POST_DRAW_STORAGE] };
    }
    return {
      storage: 'armor',
      discardItemId: actor.armorItemId,
      visibility: policies.nonBackpackVisibility,
    };
  }

  return { illegal: `unsupported-item-kind:${item.kind}` };
}

function planTacticalGear(original, itemId, storagePlan, input) {
  if (storagePlan.storage === 'item-discard') return { tokens: [] };
  const item = original.items[itemId];
  const slots = item.tacticalGearSlots;
  if (slots.length === 0) return { tokens: [] };

  const allocation = input.tacticalGearAllocation;
  if (!Array.isArray(allocation) || allocation.length !== slots.length) {
    return { gaps: [SEARCH_GAPS.TACTICAL_GEAR_ALLOCATION] };
  }

  const remaining = { ...original.tacticalGearPool };
  for (let index = 0; index < slots.length; index += 1) {
    const slot = slots[index];
    const token = allocation[index];
    if (slot !== 'any' && slot !== token) {
      return { illegal: `incompatible-tactical-gear-token:${index}` };
    }
    if (!Number.isInteger(remaining[token]) || remaining[token] <= 0) {
      return { gaps: [SEARCH_GAPS.TACTICAL_GEAR_ALLOCATION] };
    }
    remaining[token] -= 1;
  }
  return { tokens: [...allocation] };
}

function applyStorage(state, actorId, itemId, plan) {
  const actor = state.players[actorId];
  if (plan.discardItemId) applyDiscard(state, plan.discardItemId);
  if (plan.storage === 'item-discard') applyDiscard(state, itemId);
  if (plan.storage === 'backpack') actor.backpack.push(itemId);
  if (plan.storage === 'hand') actor.handSlots[plan.slotIndex] = itemId;
  if (plan.storage === 'armor') actor.armorItemId = itemId;

  if (plan.storage !== 'item-discard') {
    for (const token of plan.tacticalGearTokens) state.tacticalGearPool[token] -= 1;
    state.itemRuntime[itemId] = {
      tacticalGearTokens: [...plan.tacticalGearTokens],
    };
  }
}

function publicGainEvent(actorId, itemId, plan) {
  const event = {
    type: plan.storage === 'item-discard' ? 'item-gain-failed' : 'item-gained',
    actorId,
    storage: plan.storage,
  };
  if (plan.storage !== 'backpack' && plan.visibility === 'public') {
    event.itemId = itemId;
  }
  return event;
}

export function resolveSearch(input) {
  const {
    state,
    actorId,
    roomId,
    searchCardId,
    keepOccurrenceId = null,
    policies = {},
  } = input;

  const invalidReason = validateInput(state, actorId, roomId, searchCardId);
  if (invalidReason) return invalid(state, invalidReason);

  const actor = state.players[actorId];
  const card = state.actionCards[searchCardId];
  if (card.notInCombat && actor.inCombat) {
    return invalid(state, 'not-in-combat');
  }

  if (!policies.keepCardinality) {
    return unresolved(state, [SEARCH_GAPS.KEEP_CARDINALITY], 'keep-cardinality-policy-required');
  }
  if (!['exactly-one', 'zero-or-one'].includes(policies.keepCardinality)) {
    return invalid(state, 'unsupported-keep-cardinality-policy');
  }
  if (policies.nonBackpackVisibility
      && !['public', 'owner-private'].includes(policies.nonBackpackVisibility)) {
    return invalid(state, 'unsupported-non-backpack-visibility-policy');
  }
  if (policies.sameDeckReturnOrder
      && !['draw-order', 'reverse-draw-order'].includes(policies.sameDeckReturnOrder)) {
    return invalid(state, 'unsupported-same-deck-return-order-policy');
  }
  if (policies.keepCardinality === 'exactly-one' && keepOccurrenceId === null) {
    return invalid(state, 'exactly-one-policy-requires-a-kept-occurrence');
  }

  const drawCounts = requiredDraws(state.rooms[roomId].itemIcons);
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
  }

  const kept = keepOccurrenceId === null
    ? null
    : candidates.find(({ itemId }) => itemId === keepOccurrenceId);
  if (keepOccurrenceId !== null && !kept) {
    return invalid(state, 'kept-occurrence-was-not-drawn');
  }

  let plan = null;
  if (kept) {
    plan = planStorage(state, kept.itemId, actorId, input, policies);
    if (plan.illegal) return invalid(state, plan.illegal);
    if (plan.gaps) return unresolved(state, plan.gaps, 'selected-item-storage-policy-unresolved');
    const tacticalGearPlan = planTacticalGear(state, kept.itemId, plan, input);
    if (tacticalGearPlan.illegal) return invalid(state, tacticalGearPlan.illegal);
    if (tacticalGearPlan.gaps) {
      return unresolved(state, tacticalGearPlan.gaps, 'fully-loaded-allocation-policy-unresolved');
    }
    plan.tacticalGearTokens = tacticalGearPlan.tokens;
  }

  const unchosenByColor = new Map();
  for (const candidate of candidates) {
    if (kept && candidate.itemId === kept.itemId) continue;
    if (!unchosenByColor.has(candidate.color)) unchosenByColor.set(candidate.color, []);
    unchosenByColor.get(candidate.color).push(candidate.itemId);
  }
  for (const [color, itemIds] of unchosenByColor) {
    if (itemIds.length > 1 && !policies.sameDeckReturnOrder) {
      return unresolved(state, [SEARCH_GAPS.SAME_DECK_RETURN_ORDER], 'same-deck-bottom-order-policy-required');
    }
    const ordered = policies.sameDeckReturnOrder === 'reverse-draw-order'
      ? [...itemIds].reverse()
      : itemIds;
    next.itemDecks[color].push(...ordered);
  }

  if (kept) applyStorage(next, actorId, kept.itemId, plan);

  const actionIndex = next.players[actorId].actionHand.indexOf(searchCardId);
  next.players[actorId].actionHand.splice(actionIndex, 1);
  next.players[actorId].actionDiscard.unshift(searchCardId);
  if (kept) next.publicEvents.push(publicGainEvent(actorId, kept.itemId, plan));

  const privateEvent = {
    type: 'search-candidates',
    candidateOccurrenceIds: candidates.map(({ itemId }) => itemId),
    keptOccurrenceId: kept?.itemId ?? null,
  };
  next.privateEventsByPlayer[actorId].push(privateEvent);

  return {
    status: 'resolved',
    state: next,
    private: privateEvent,
    interpretations: {
      keepCardinality: policies.keepCardinality,
      sameDeckReturnOrder: policies.sameDeckReturnOrder ?? null,
      nonBackpackVisibility: plan?.storage === 'hand' || plan?.storage === 'armor'
        ? policies.nonBackpackVisibility
        : null,
    },
    sourceBasis: {
      applied: [
        'RB:2871-2875',
        'RB:3177-3179',
        'RB:3188-3191',
        'RB:3665-3673',
        'RB:4849-4865',
        'RB:4899-4910',
        'RB:4933-4948',
        'RB:5024-5057',
        'RB:5058-5078',
        'CARD:SEARCH',
      ],
      consultedForGaps: ['RB:3543-3548'],
    },
  };
}
