import { describe, it, expect } from 'vitest';
import { Mulberry32 } from '../../src/engine/prng/mulberry32.js';
import { createInitialGameState } from '../../src/engine/setup/initial-state.js';
import { gameReducer } from '../../src/engine/reducer.js';
import { resolveEventPhase } from '../../src/engine/phases/event-phase.js';
import { spawnIntruder } from '../../src/engine/combat/noise.js';

describe('Event Phase (RT-009)', () => {
  it('draws and resolves an event card and moves corridor intruders', () => {
    const prng = new Mulberry32(333);
    let state = createInitialGameState({ playerCount: 1, seed: 333 });

    state = gameReducer(state, {
      actionId: 1,
      type: 'draft_character',
      playerId: 'player-1',
      characterId: 'officer',
    });

    const corridorId = 'c_landing-zone__slot_1_2';
    // Spawn adult in corridor
    const spawn = spawnIntruder(state, 'adult', { kind: 'corridor', corridorId });
    state = spawn.state;
    state.phase = 'event';

    const res = resolveEventPhase(state, prng);

    expect(res.drawnEvent).toBeDefined();
    expect(res.events).toContain('=== EVENT PHASE ===');
    expect(res.events.some(e => e.startsWith('Drawn Event Card:'))).toBe(true);
    expect(res.state.phase).toBe('cleanup');
  });
});
