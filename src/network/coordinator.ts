/**
 * WebRTC action coordinator and virtual host synchronization engine.
 * Ensures monotonic sequence numbering, action broadcasting, state replication, and host failover.
 */

import { GameState } from '../engine/types/state.js';
import { GameAction } from '../engine/types/actions.js';
import { gameReducer } from '../engine/reducer.js';
import { ActionProposal, NetworkMessage, PeerInfo } from './types.js';
import { PlayerId } from '../engine/types/primitives.js';

export interface NetworkTransport {
  send(targetPeerId: string, message: NetworkMessage): void;
  broadcast(message: NetworkMessage): void;
}

export class NetworkCoordinator {
  public peerId: string;
  public playerName: string;
  public isHost: boolean;
  public state: GameState;
  public peers: Map<string, PeerInfo> = new Map();
  public transport: NetworkTransport;
  public onStateUpdate?: (state: GameState, lastAction: GameAction) => void;
  public onPeerChange?: (peers: PeerInfo[]) => void;
  public onError?: (error: string) => void;

  constructor(
    peerId: string,
    playerName: string,
    isHost: boolean,
    initialState: GameState,
    transport: NetworkTransport,
  ) {
    this.peerId = peerId;
    this.playerName = playerName;
    this.isHost = isHost;
    this.state = initialState;
    this.transport = transport;

    // Register self
    this.peers.set(peerId, {
      peerId,
      playerName,
      isHost,
      lastSeenTimestamp: Date.now(),
    });
  }

  /**
   * Submits a player action.
   * If host: sequences immediately and broadcasts.
   * If client: sends proposal to host.
   */
  public submitAction(actionProposal: ActionProposal): void {
    if (this.isHost) {
      const nextActionId = this.state.lastActionId + 1;
      const fullAction: GameAction = {
        ...actionProposal,
        actionId: nextActionId,
        timestamp: Date.now(),
      } as GameAction;

      try {
        const nextState = gameReducer(this.state, fullAction);
        this.state = nextState;

        // Authoritative broadcast to all peers
        this.transport.broadcast({
          type: 'action_broadcast',
          senderPeerId: this.peerId,
          action: fullAction,
        });

        this.onStateUpdate?.(this.state, fullAction);
      } catch (err: any) {
        this.onError?.(`Host action execution rejected: ${err.message}`);
      }
    } else {
      // Find host
      const host = Array.from(this.peers.values()).find(p => p.isHost);
      if (!host) {
        this.onError?.('Cannot submit action: No host connected');
        return;
      }

      this.transport.send(host.peerId, {
        type: 'action_proposal',
        senderPeerId: this.peerId,
        action: actionProposal,
      });
    }
  }

  /**
   * Handles incoming network message from transport.
   */
  public handleMessage(message: NetworkMessage): void {
    // Update peer last seen
    const existingPeer = this.peers.get(message.senderPeerId);
    if (existingPeer) {
      existingPeer.lastSeenTimestamp = Date.now();
    }

    switch (message.type) {
      case 'join_request': {
        if (!this.isHost) return;

        // Find next open player slot
        const existingPlayer = this.state.players.find(p => p.name === message.playerName);
        let assignedId: PlayerId = existingPlayer ? existingPlayer.playerId : `player-${this.peers.size}`;

        this.peers.set(message.senderPeerId, {
          peerId: message.senderPeerId,
          playerName: message.playerName,
          playerId: assignedId,
          isHost: false,
          lastSeenTimestamp: Date.now(),
        });

        this.transport.send(message.senderPeerId, {
          type: 'join_accepted',
          senderPeerId: this.peerId,
          assignedPlayerId: assignedId,
          initialState: this.state,
          peers: Array.from(this.peers.values()),
        });

        this.onPeerChange?.(Array.from(this.peers.values()));
        break;
      }

      case 'join_accepted': {
        this.state = message.initialState;
        this.peers.clear();
        for (const p of message.peers) {
          this.peers.set(p.peerId, p);
        }
        this.onPeerChange?.(Array.from(this.peers.values()));
        this.onStateUpdate?.(this.state, {} as any);
        break;
      }

      case 'action_proposal': {
        if (!this.isHost) return;
        this.submitAction(message.action);
        break;
      }

      case 'action_broadcast': {
        if (this.isHost) return; // Host already processed it

        const expectedActionId = this.state.lastActionId + 1;
        if (message.action.actionId === expectedActionId) {
          try {
            this.state = gameReducer(this.state, message.action);
            this.onStateUpdate?.(this.state, message.action);
          } catch (err: any) {
            this.onError?.(`Client failed to apply action ${message.action.actionId}: ${err.message}`);
          }
        } else if (message.action.actionId > expectedActionId) {
          // Out of order or dropped packet -> request sync catch-up
          this.transport.send(message.senderPeerId, {
            type: 'sync_request',
            senderPeerId: this.peerId,
            fromActionId: expectedActionId,
          });
        }
        break;
      }

      case 'sync_request': {
        if (!this.isHost) return;
        const missing = this.state.actionHistory.slice(message.fromActionId - 1);
        this.transport.send(message.senderPeerId, {
          type: 'sync_response',
          senderPeerId: this.peerId,
          snapshot: this.state,
          recentActions: missing,
        });
        break;
      }

      case 'sync_response': {
        this.state = message.snapshot;
        this.onStateUpdate?.(this.state, {} as any);
        break;
      }

      case 'heartbeat': {
        // Peer heartbeat updated above
        break;
      }

      case 'host_migration_start': {
        const newHost = this.peers.get(message.newHostPeerId);
        if (newHost) {
          // Demote former host
          for (const p of this.peers.values()) {
            p.isHost = p.peerId === message.newHostPeerId;
          }
          if (message.newHostPeerId === this.peerId) {
            this.isHost = true;
          }
          this.onPeerChange?.(Array.from(this.peers.values()));
        }
        break;
      }
    }
  }

  /**
   * Heartbeat monitor check.
   * Detects peer timeouts and triggers host failover if host goes offline.
   */
  public checkHeartbeats(now: number = Date.now(), timeoutMs: number = 10000): void {
    let hostDropped = false;

    for (const [id, peer] of this.peers.entries()) {
      if (id === this.peerId) continue;
      if (now - peer.lastSeenTimestamp > timeoutMs) {
        if (peer.isHost) {
          hostDropped = true;
        }
        this.peers.delete(id);
      }
    }

    if (hostDropped) {
      // Automated failover: lowest-alphabetical active peer becomes the new host
      const remainingPeers = Array.from(this.peers.values()).sort((a, b) => a.peerId.localeCompare(b.peerId));
      if (remainingPeers[0]) {
        const electedHostId = remainingPeers[0].peerId;
        this.handleMessage({
          type: 'host_migration_start',
          senderPeerId: this.peerId,
          newHostPeerId: electedHostId,
          lastConfirmedActionId: this.state.lastActionId,
        });
        this.transport.broadcast({
          type: 'host_migration_start',
          senderPeerId: this.peerId,
          newHostPeerId: electedHostId,
          lastConfirmedActionId: this.state.lastActionId,
        });
      }
    }
  }
}
