/**
 * Room code generation and formatting for Nemesis: Retaliation WebRTC peer matching.
 * Uses 4-character unambiguous uppercase codes (nemesis-rt-XXXX).
 */

const UNAMBIGUOUS_CHARSET = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ';

export const ROOM_CODE_PREFIX = 'nemesis-rt-';

/**
 * Generates a random 4-character room code.
 */
export function generateRoomCode(): string {
  let code = '';
  for (let i = 0; i < 4; i++) {
    const idx = Math.floor(Math.random() * UNAMBIGUOUS_CHARSET.length);
    code += UNAMBIGUOUS_CHARSET[idx];
  }
  return code;
}

/**
 * Formats a 4-character code into the canonical PeerJS peer ID.
 */
export function formatPeerId(roomCode: string): string {
  const clean = roomCode.trim().toUpperCase().replace(/[^23456789ABCDEFGHJKLMNPQRSTUVWXYZ]/g, '');
  return `${ROOM_CODE_PREFIX}${clean}`;
}

/**
 * Validates and extracts a 4-character room code from user input.
 */
export function parseRoomCode(input: string): string | null {
  const clean = input.trim().toUpperCase().replace(ROOM_CODE_PREFIX.toUpperCase(), '').replace(/[^23456789ABCDEFGHJKLMNPQRSTUVWXYZ]/g, '');
  if (clean.length === 4) {
    return clean;
  }
  return null;
}
