import { describe, it, expect } from 'vitest';
import { generateRoomCode, formatPeerId, parseRoomCode } from '../../src/network/room-code.js';
import { NetworkCoordinator, NetworkTransport } from '../../src/network/coordinator.js';
import { createInitialGameState } from '../../src/engine/setup/initial-state.js';
import { NetworkMessage } from '../../src/network/types.js';

class MockNetworkTransport implements NetworkTransport {
  public peers = new Map<string, NetworkCoordinator>();

  public register(coord: NetworkCoordinator) {
    this.peers.set(coord.peerId, coord);
  }

  public send(targetPeerId: string, message: NetworkMessage): void {
    const target = this.peers.get(targetPeerId);
    if (target) {
      setTimeout(() => target.handleMessage(message), 0);
    }
  }

  public broadcast(message: NetworkMessage): void {
    for (const [id, peer] of this.peers.entries()) {
      if (id !== message.senderPeerId) {
        setTimeout(() => peer.handleMessage(message), 0);
      }
    }
  }
}

describe('WebRTC Networking & Host Coordination Layer', () => {
  it('generates, formats, and parses 4-character room codes', () => {
    const code = generateRoomCode();
    expect(code.length).toBe(4);

    const peerId = formatPeerId(code);
    expect(peerId).toBe(`nemesis-rt-${code}`);

    expect(parseRoomCode(code)).toBe(code);
    expect(parseRoomCode(`nemesis-rt-${code}`)).toBe(code);
    expect(parseRoomCode('INVALID_CODE_123')).toBeNull();
  });

  it('coordinates action proposals, monotonic sequencing, and state synchronization across peers', async () => {
    const transport = new MockNetworkTransport();
    const initialState = createInitialGameState({ playerCount: 2, seed: 1234 });

    const host = new NetworkCoordinator('peer-host', 'Alice', true, initialState, transport);
    const client = new NetworkCoordinator('peer-client', 'Bob', false, initialState, transport);

    transport.register(host);
    transport.register(client);

    // Client requests to join
    client.handleMessage = client.handleMessage.bind(client);
    host.handleMessage = host.handleMessage.bind(host);

    host.handleMessage({
      type: 'join_request',
      senderPeerId: 'peer-client',
      playerName: 'Bob',
    });

    await new Promise(r => setTimeout(r, 10));

    expect(host.peers.has('peer-client')).toBe(true);

    // Host drafts character 1
    host.submitAction({
      type: 'draft_character',
      playerId: 'player-1',
      characterId: 'officer',
    });

    await new Promise(r => setTimeout(r, 10));

    // Client should have received broadcast and updated state
    expect(client.state.lastActionId).toBe(1);
    expect(client.state.characters.officer?.characterId).toBe('officer');
    expect(client.state.characters.officer?.actionsRemaining).toBe(2);

    // Client drafts character 2 via proposal
    client.submitAction({
      type: 'draft_character',
      playerId: 'player-2',
      characterId: 'recon',
    });

    await new Promise(r => setTimeout(r, 10));

    expect(host.state.lastActionId).toBe(2);
    expect(host.state.phase).toBe('player');
    expect(client.state.lastActionId).toBe(2);
    expect(client.state.phase).toBe('player');
  });

  it('triggers automated host failover when host disconnects', () => {
    const transport = new MockNetworkTransport();
    const initialState = createInitialGameState({ playerCount: 2, seed: 5678 });

    const host = new NetworkCoordinator('peer-host', 'Alice', true, initialState, transport);
    const client = new NetworkCoordinator('peer-client', 'Bob', false, initialState, transport);

    transport.register(host);
    transport.register(client);

    // Manually register peer on client
    client.peers.set('peer-host', {
      peerId: 'peer-host',
      playerName: 'Alice',
      isHost: true,
      lastSeenTimestamp: 1000,
    });

    expect(client.isHost).toBe(false);

    // Simulate timeout (now = 20000ms, lastSeen = 1000ms -> >10s)
    client.checkHeartbeats(20000, 10000);

    expect(client.peers.has('peer-host')).toBe(false);
    expect(client.isHost).toBe(true);
  });
});
