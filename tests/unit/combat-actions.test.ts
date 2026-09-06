import { describe, it, expect } from 'vitest';
import { Mulberry32 } from '../../src/engine/prng/mulberry32.js';
import { createInitialGameState } from '../../src/engine/setup/initial-state.js';
import { gameReducer } from '../../src/engine/reducer.js';
import { executeBurst, executeMelee, executeShoot, executeTrade } from '../../src/engine/actions/combat-actions.js';
import { spawnIntruder } from '../../src/engine/combat/noise.js';

describe('Combat Actions System (Shoot, Burst, Melee, Trade)', () => {
  it('executes Shoot action dealing hits and rolling shoot die', () => {
    const prng = new Mulberry32(123);
    let state = createInitialGameState({ playerCount: 1, seed: 123 });

    state = gameReducer(state, {
      actionId: 1,
      type: 'draft_character',
      playerId: 'player-1',
      characterId: 'officer',
    });

    // Spawn an adult in Landing Zone
    const spawnRes = spawnIntruder(state, 'adult', { kind: 'room', roomId: 'landing-zone' });
    state = spawnRes.state;
    const intruderId = spawnRes.instanceId!;

    const officer = state.characters.officer!;
    const weaponId = officer.inventory.equippedWeapon!.id;

    const shootRes = executeShoot(state, 'officer', intruderId, weaponId, prng);

    expect(shootRes.state).toBeDefined();
    expect(shootRes.events.length).toBeGreaterThan(0);
    expect(shootRes.dieRoll).toBeDefined();
  });

  it('executes Burst action dealing hits in an adjacent corridor', () => {
    const prng = new Mulberry32(456);
    let state = createInitialGameState({ playerCount: 1, seed: 456 });

    state = gameReducer(state, {
      actionId: 1,
      type: 'draft_character',
      playerId: 'player-1',
      characterId: 'officer',
    });

    const corridorId = 'c_landing-zone__slot_1_2';
    // Spawn an adult in the corridor
    const spawnRes = spawnIntruder(state, 'adult', { kind: 'corridor', corridorId });
    state = spawnRes.state;

    const officer = state.characters.officer!;
    const weaponId = officer.inventory.equippedWeapon!.id;

    const burstRes = executeBurst(state, 'officer', corridorId, weaponId, prng);

    expect(burstRes.state).toBeDefined();
    expect(burstRes.events.length).toBeGreaterThan(0);
    expect(burstRes.dieRoll).toBeDefined();
  });

  it('executes Melee action with intruder counter-attack on survival', () => {
    const prng = new Mulberry32(789);
    let state = createInitialGameState({ playerCount: 1, seed: 789 });

    state = gameReducer(state, {
      actionId: 1,
      type: 'draft_character',
      playerId: 'player-1',
      characterId: 'officer',
    });

    const spawnRes = spawnIntruder(state, 'adult', { kind: 'room', roomId: 'landing-zone' });
    state = spawnRes.state;
    const intruderId = spawnRes.instanceId!;

    const meleeRes = executeMelee(state, 'officer', intruderId, prng);

    expect(meleeRes.state).toBeDefined();
    expect(meleeRes.events.length).toBeGreaterThan(0);
  });

  it('trades items between two characters in the same room', () => {
    let state = createInitialGameState({ playerCount: 2, seed: 10 });

    state = gameReducer(state, {
      actionId: 1,
      type: 'draft_character',
      playerId: 'player-1',
      characterId: 'officer',
    });
    state = gameReducer(state, {
      actionId: 2,
      type: 'draft_character',
      playerId: 'player-2',
      characterId: 'recon',
    });

    // Give an item to officer
    const sampleItem = {
      id: 'item-test-1',
      title: 'Adrenaline Injection',
      category: 'green' as const,
      isHeavy: false,
      isWeapon: false,
      rulesText: 'Test item',
    };

    state = {
      ...state,
      characters: {
        ...state.characters,
        officer: {
          ...state.characters.officer!,
          inventory: {
            ...state.characters.officer!.inventory,
            backpack: [sampleItem],
          },
        },
      },
    };

    const tradeRes = executeTrade(state, 'officer', 'recon', 'item-test-1', undefined);

    expect(tradeRes.state.characters.officer?.inventory.backpack.length).toBe(0);
    expect(tradeRes.state.characters.recon?.inventory.backpack.length).toBe(1);
    expect(tradeRes.state.characters.recon?.inventory.backpack[0]?.title).toBe('Adrenaline Injection');
  });
});
