import { describe, it, expect } from 'vitest';
import { createInitialGameState } from '../../src/engine/setup/initial-state.js';
import { MemoryStorageAdapter } from '../../src/engine/serialization/storage.js';

describe('Storage Persistence Adapters', () => {
  it('saves, loads, lists, and deletes games in MemoryStorageAdapter', async () => {
    const storage = new MemoryStorageAdapter();
    const state = createInitialGameState({ playerCount: 2, seed: 999 });

    await storage.saveGame('game-test-1', state);

    const ids = await storage.listGameIds();
    expect(ids).toEqual(['game-test-1']);

    const loaded = await storage.loadGame('game-test-1');
    expect(loaded).not.toBeNull();
    expect(loaded?.gameId).toBe(state.gameId);
    expect(loaded?.board.rooms['landing-zone']?.isDiscovered).toBe(true);

    await storage.deleteGame('game-test-1');
    const idsAfterDelete = await storage.listGameIds();
    expect(idsAfterDelete).toEqual([]);

    const reloaded = await storage.loadGame('game-test-1');
    expect(reloaded).toBeNull();
  });
});
