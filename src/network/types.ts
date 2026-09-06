/**
 * P2P Network protocol types for Nemesis: Retaliation WebRTC synchronization.
 */

import { GameAction } from '../engine/types/actions.js';
import { GameState } from '../engine/types/state.js';
import { PlayerId } from '../engine/types/primitives.js';

export interface PeerInfo {
  peerId: string;
  playerId?: PlayerId | undefined;
  playerName: string;
  isHost: boolean;
  lastSeenTimestamp: number;
}

export type DistributiveOmit<T, K extends keyof any> = T extends any ? Omit<T, K> : never;

export type ActionProposal = DistributiveOmit<GameAction, 'actionId' | 'timestamp'>;

export type NetworkMessage =
  | {
      type: 'join_request';
      senderPeerId: string;
      playerName: string;
    }
  | {
      type: 'join_accepted';
      senderPeerId: string;
      assignedPlayerId: PlayerId;
      initialState: GameState;
      peers: PeerInfo[];
    }
  | {
      type: 'join_rejected';
      senderPeerId: string;
      reason: string;
    }
  | {
      type: 'action_proposal';
      senderPeerId: string;
      action: ActionProposal;
    }
  | {
      type: 'action_broadcast';
      senderPeerId: string;
      action: GameAction;
    }
  | {
      type: 'heartbeat';
      senderPeerId: string;
      timestamp: number;
    }
  | {
      type: 'sync_request';
      senderPeerId: string;
      fromActionId: number;
    }
  | {
      type: 'sync_response';
      senderPeerId: string;
      snapshot: GameState;
      recentActions: GameAction[];
    }
  | {
      type: 'host_migration_start';
      senderPeerId: string;
      newHostPeerId: string;
      lastConfirmedActionId: number;
    }
  | {
      type: 'host_migration_confirm';
      senderPeerId: string;
      newHostPeerId: string;
    };
