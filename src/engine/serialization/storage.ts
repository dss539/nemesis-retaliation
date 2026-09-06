/**
 * Game state persistence adapter for Nemesis: Retaliation.
 * Supports IndexedDB, localStorage, and memory store with graceful fallbacks.
 */

import { GameState } from '../types/state.js';
import { StateSerializer } from './state-serializer.js';

export interface GameStorageAdapter {
  saveGame(gameId: string, state: GameState): Promise<void>;
  loadGame(gameId: string): Promise<GameState | null>;
  listGameIds(): Promise<string[]>;
  deleteGame(gameId: string): Promise<void>;
  clear(): Promise<void>;
}

export class MemoryStorageAdapter implements GameStorageAdapter {
  private storage = new Map<string, string>();

  async saveGame(gameId: string, state: GameState): Promise<void> {
    const json = StateSerializer.serialize(state);
    this.storage.set(gameId, json);
  }

  async loadGame(gameId: string): Promise<GameState | null> {
    const json = this.storage.get(gameId);
    if (!json) return null;
    return StateSerializer.deserialize(json);
  }

  async listGameIds(): Promise<string[]> {
    return Array.from(this.storage.keys());
  }

  async deleteGame(gameId: string): Promise<void> {
    this.storage.delete(gameId);
  }

  async clear(): Promise<void> {
    this.storage.clear();
  }
}

export class BrowserLocalStorageAdapter implements GameStorageAdapter {
  private prefix = 'nemesis_retaliation_save_';

  async saveGame(gameId: string, state: GameState): Promise<void> {
    if (typeof localStorage === 'undefined') return;
    const json = StateSerializer.serialize(state);
    localStorage.setItem(this.prefix + gameId, json);
  }

  async loadGame(gameId: string): Promise<GameState | null> {
    if (typeof localStorage === 'undefined') return null;
    const json = localStorage.getItem(this.prefix + gameId);
    if (!json) return null;
    return StateSerializer.deserialize(json);
  }

  async listGameIds(): Promise<string[]> {
    if (typeof localStorage === 'undefined') return [];
    const keys: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i);
      if (k && k.startsWith(this.prefix)) {
        keys.push(k.slice(this.prefix.length));
      }
    }
    return keys;
  }

  async deleteGame(gameId: string): Promise<void> {
    if (typeof localStorage === 'undefined') return;
    localStorage.removeItem(this.prefix + gameId);
  }

  async clear(): Promise<void> {
    if (typeof localStorage === 'undefined') return;
    const keys = await this.listGameIds();
    for (const id of keys) {
      localStorage.removeItem(this.prefix + id);
    }
  }
}
