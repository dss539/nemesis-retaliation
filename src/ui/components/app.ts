/**
 * Client Application Orchestrator for Nemesis: Retaliation.
 * Binds TacticalRenderer, GameState, user interactions, and WebRTC coordinator into a cohesive web experience.
 */

import { GameState } from '../../engine/types/state.js';
import { GameAction } from '../../engine/types/actions.js';
import { createInitialGameState } from '../../engine/setup/initial-state.js';
import { gameReducer } from '../../engine/reducer.js';
import { TacticalRenderer } from '../canvas/tactical-renderer.js';
import { NetworkCoordinator, NetworkTransport } from '../../network/coordinator.js';
import { generateRoomCode, formatPeerId } from '../../network/room-code.js';
import { NetworkMessage } from '../../network/types.js';

class BrowserDummyTransport implements NetworkTransport {
  send(_target: string, _msg: NetworkMessage) {}
  broadcast(_msg: NetworkMessage) {}
}

export class NemesisApp {
  public state: GameState;
  public renderer: TacticalRenderer;
  public coordinator: NetworkCoordinator;
  public roomCode: string;
  public container: HTMLElement;

  constructor(container: HTMLElement, canvas: HTMLCanvasElement) {
    this.container = container;
    this.roomCode = generateRoomCode();
    this.state = createInitialGameState({ playerCount: 2, seed: Date.now() });

    const transport = new BrowserDummyTransport();
    this.coordinator = new NetworkCoordinator(
      formatPeerId(this.roomCode),
      'Player 1',
      true,
      this.state,
      transport,
    );

    this.renderer = new TacticalRenderer(canvas, {
      selectedRoomId: 'landing-zone',
      onRoomClick: (roomId) => this.handleRoomClick(roomId),
    });

    this.renderer.setState(this.state);
    this.renderUI();
  }

  public dispatchAction(action: GameAction): void {
    try {
      this.state = gameReducer(this.state, action);
      this.renderer.setState(this.state);
      this.renderUI();
    } catch (err: any) {
      alert(`Action error: ${err.message}`);
    }
  }

  private handleRoomClick(roomId: string): void {
    this.renderer.options.selectedRoomId = roomId;
    this.renderUI();
  }

  public renderUI(): void {
    let uiOverlay = document.getElementById('nemesis-ui-overlay');
    if (!uiOverlay) {
      uiOverlay = document.createElement('div');
      uiOverlay.id = 'nemesis-ui-overlay';
      uiOverlay.style.position = 'absolute';
      uiOverlay.style.top = '0';
      uiOverlay.style.left = '0';
      uiOverlay.style.width = '100%';
      uiOverlay.style.height = '100%';
      uiOverlay.style.pointerEvents = 'none';
      this.container.appendChild(uiOverlay);
    }

    const activePlayer = this.state.players[this.state.activePlayerIndex];
    const activeChar = activePlayer?.characterId ? this.state.characters[activePlayer.characterId] : null;
    const playerInCombat = Boolean(
      activeChar &&
      this.state.board.rooms[activeChar.currentRoomId] &&
      this.state.board.rooms[activeChar.currentRoomId]!.intruderIds.length > 0
    );

    uiOverlay.innerHTML = `
      <div style="pointer-events: auto; background: rgba(15, 23, 42, 0.9); padding: 12px 20px; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; color: #f8fafc; font-family: sans-serif;">
        <div>
          <span style="font-weight: bold; font-size: 16px; color: #facc15;">NEMESIS: RETALIATION</span>
          <span style="margin-left: 16px; padding: 4px 8px; background: #1e293b; border-radius: 4px; font-size: 12px;">Round: ${this.state.round} / 15</span>
          <span style="margin-left: 8px; padding: 4px 8px; background: #1e293b; border-radius: 4px; font-size: 12px; text-transform: uppercase;">Phase: ${this.state.phase}</span>
          <span style="margin-left: 8px; font-size: 12px; color: #94a3b8;">Room Code: <b>${this.roomCode}</b></span>
        </div>
        <div style="font-size: 13px;">
          <span>Life Support: </span>
          <span style="color: ${this.state.lifeSupport.A ? '#22c55e' : '#ef4444'};">Sec A: ${this.state.lifeSupport.A ? 'ON' : 'OFF'}</span> |
          <span style="color: ${this.state.lifeSupport.B ? '#22c55e' : '#ef4444'};">Sec B: ${this.state.lifeSupport.B ? 'ON' : 'OFF'}</span> |
          <span style="color: ${this.state.lifeSupport.C ? '#22c55e' : '#ef4444'};">Sec C: ${this.state.lifeSupport.C ? 'ON' : 'OFF'}</span>
        </div>
      </div>

      <div style="pointer-events: auto; position: absolute; bottom: 0; left: 0; width: 100%; background: rgba(15, 23, 42, 0.95); border-top: 1px solid #334155; padding: 12px 20px; box-sizing: border-box; color: #f8fafc; font-family: sans-serif;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <div>
            <b>Active:</b> ${activePlayer?.name ?? 'None'} ${activeChar ? `(${activeChar.name})` : ''} — 
            <span>Actions Remaining: <b>${activeChar?.actionsRemaining ?? 0}</b></span>
            ${activeChar ? ` | HP: ${activeChar.health}/${activeChar.maxHealth} | O2: ${activeChar.oxygen}` : ''}
            ${playerInCombat ? ' | <span style="background: #991b1b; color: #fee2e2; padding: 2px 6px; border-radius: 3px; font-weight: bold; font-size: 11px;">⚔️ IN COMBAT</span>' : ' | <span style="color: #4ade80; font-size: 11px;">🛡️ Safe</span>'}
          </div>
          <div>
            <button id="btn-pass" style="background: #e11d48; color: white; border: none; padding: 6px 14px; border-radius: 4px; cursor: pointer; font-weight: bold;">PASS TURN</button>
          </div>
        </div>

        ${activeChar ? `
        <div style="display: flex; gap: 8px; overflow-x: auto; padding: 4px 0;">
          ${activeChar.hand.map(card => {
            const isPlayable = !playerInCombat || card.usableInCombat;
            return `
            <div style="background: ${isPlayable ? '#1e293b' : '#1e1b24'}; border: 1px solid ${isPlayable ? '#475569' : '#7f1d1d'}; border-radius: 6px; padding: 8px; min-width: 140px; font-size: 11px; opacity: ${isPlayable ? '1.0' : '0.6'};">
              <div style="font-weight: bold; margin-bottom: 4px; color: ${isPlayable ? '#38bdf8' : '#94a3b8'};">${card.title}</div>
              <div style="font-size: 10px; margin-top: 4px;">
                ${card.usableInCombat 
                  ? '<span style="color: #4ade80;">⚔️ Playable in Combat</span>' 
                  : '<span style="color: #f87171;">⚠️ Out-of-Combat Only</span>'}
              </div>
            </div>
            `;
          }).join('')}
        </div>
        ` : ''}
      </div>
    `;

    document.getElementById('btn-pass')?.addEventListener('click', () => {
      if (activeChar) {
        this.dispatchAction({
          actionId: this.state.lastActionId + 1,
          type: 'pass',
          characterId: activeChar.characterId,
        });
      }
    });

    this.renderer.render();
  }
}
