import { describe, it, expect } from 'vitest';
import { DoorStateMachine } from '../../src/engine/spatial/doors.js';

describe('Door State Machine', () => {
  it('correctly assesses passage for door states', () => {
    expect(DoorStateMachine.allowsPassage('open')).toBe(true);
    expect(DoorStateMachine.allowsPassage('destroyed')).toBe(true);
    expect(DoorStateMachine.allowsPassage('closed')).toBe(false);
  });

  it('handles open and close transitions', () => {
    expect(DoorStateMachine.open('closed')).toBe('open');
    expect(DoorStateMachine.close('open')).toBe('closed');
  });

  it('handles destroyed doors permanently', () => {
    expect(DoorStateMachine.destroy('closed')).toBe('destroyed');
    expect(DoorStateMachine.open('destroyed')).toBe('destroyed');
    expect(() => DoorStateMachine.close('destroyed')).toThrow('destroyed door cannot be closed');
  });

  it('only allows closed doors to be destroyed', () => {
    expect(() => DoorStateMachine.destroy('open')).toThrow('Only a closed door can be destroyed');
  });
});
