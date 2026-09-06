/**
 * Deterministic 32-bit PRNG using Mulberry32.
 * Produces reproducible sequences from a numeric seed and supports state export/hydration.
 */

export interface PRNGState {
  seed: number;
  calls: number;
}

export class Mulberry32 {
  private initialSeed: number;
  private state: number;
  private callCount: number;

  constructor(seed: number = Date.now()) {
    this.initialSeed = seed >>> 0;
    this.state = this.initialSeed;
    this.callCount = 0;
  }

  /**
   * Returns a pseudo-random floating point number in [0, 1).
   */
  next(): number {
    this.callCount++;
    let t = (this.state += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  }

  /**
   * Returns a pseudo-random integer between min and max (inclusive).
   */
  nextInt(min: number, max: number): number {
    if (min > max) {
      throw new Error(`min (${min}) cannot be greater than max (${max})`);
    }
    const range = max - min + 1;
    return min + Math.floor(this.next() * range);
  }

  /**
   * Rolls an N-sided die, returning an integer in [1, sides].
   */
  rollDie(sides: number): number {
    if (sides < 1) {
      throw new Error(`sides (${sides}) must be at least 1`);
    }
    return this.nextInt(1, sides);
  }

  /**
   * Deterministically shuffles an array in-place or returns a new shuffled array (Fisher-Yates).
   */
  shuffle<T>(array: readonly T[]): T[] {
    const copy = [...array];
    for (let i = copy.length - 1; i > 0; i--) {
      const j = this.nextInt(0, i);
      const temp = copy[i]!;
      copy[i] = copy[j]!;
      copy[j] = temp;
    }
    return copy;
  }

  /**
   * Draws and removes a random element from an array.
   */
  draw<T>(array: T[]): T | undefined {
    if (array.length === 0) return undefined;
    const index = this.nextInt(0, array.length - 1);
    return array.splice(index, 1)[0];
  }

  /**
   * Draws multiple elements without replacement.
   */
  drawMultiple<T>(array: T[], count: number): T[] {
    const drawn: T[] = [];
    for (let i = 0; i < count && array.length > 0; i++) {
      const item = this.draw(array);
      if (item !== undefined) {
        drawn.push(item);
      }
    }
    return drawn;
  }

  /**
   * Exports PRNG internal state for snapshots and serialization.
   */
  exportState(): PRNGState {
    return {
      seed: this.state,
      calls: this.callCount,
    };
  }

  /**
   * Hydrates PRNG internal state from a snapshot.
   */
  importState(state: PRNGState): void {
    this.state = state.seed >>> 0;
    this.callCount = state.calls;
  }

  getInitialSeed(): number {
    return this.initialSeed;
  }

  getCallCount(): number {
    return this.callCount;
  }
}
