import { describe, it, expect } from 'vitest';
import { Mulberry32 } from '../../src/engine/prng/mulberry32.js';
import { createInitialGameState } from '../../src/engine/setup/initial-state.js';
import { gameReducer } from '../../src/engine/reducer.js';
import { resolveNoiseRoll, drawAndResolveBagToken, spawnIntruder } from '../../src/engine/combat/noise.js';

describe('Noise Roll & Bag Spawning System', () => {
  it('places a noise marker when rolling an unassigned adjacent corridor value', () => {
    const prng = new Mulberry32(12345);
    const initial = createInitialGameState({ playerCount: 2, seed: 12345 });
    
    // Draft characters to get into player phase
    let state = gameReducer(initial, {
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

    const res = resolveNoiseRoll(state, 'officer', prng);
    expect(res.state).toBeDefined();
    expect(res.noiseRoll).toBeDefined();
    expect(res.events.length).toBeGreaterThan(0);
  });

  it('draws and resolves a bag token on Hazard result', () => {
    const prng = new Mulberry32(999);
    const initial = createInitialGameState({ playerCount: 2, seed: 999 });
    
    let state = gameReducer(initial, {
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

    const res = drawAndResolveBagToken(state, prng, 'hazard', 'landing-zone');
    expect(res.state).toBeDefined();
    expect(res.events.length).toBeGreaterThan(0);
  });

  it('spawns intruders and respects model limits in supply', () => {
    const initial = createInitialGameState({ playerCount: 1, seed: 42 });
    expect(initial.intruderModelsInSupply.queen).toBe(1);

    const spawn1 = spawnIntruder(initial, 'queen', { kind: 'room', roomId: 'landing-zone' });
    expect(spawn1.instanceId).toBeDefined();
    expect(spawn1.state.intruderModelsInSupply.queen).toBe(0);

    // Second queen spawn should be skipped due to model limit
    const spawn2 = spawnIntruder(spawn1.state, 'queen', { kind: 'room', roomId: 'landing-zone' });
    expect(spawn2.instanceId).toBeUndefined();
    expect(spawn2.events).toContain('No available queen models in supply - spawn skipped.');
  });
});
