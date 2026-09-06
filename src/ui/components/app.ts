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
import { BroadcastChannelTransport } from '../../network/broadcast-transport.js';

export class NemesisApp {
  public state: GameState;
  public renderer: TacticalRenderer;
  public coordinator: NetworkCoordinator;
  public roomCode: string;
  public container: HTMLElement;
  public isDebugOpen: boolean = false;
  public transport: NetworkTransport;

  constructor(container: HTMLElement, canvas: HTMLCanvasElement) {
    this.container = container;

    const urlParams = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : new URLSearchParams();
    this.roomCode = urlParams.get('room') || generateRoomCode();
    const isHost = urlParams.get('host') !== 'false' && !urlParams.get('join');
    const playerName = urlParams.get('player') ? `Player ${urlParams.get('player')}` : (isHost ? 'Player 1' : 'Player 2');

    let initialState = createInitialGameState({ playerCount: 2, seed: 12345 });

    // Draft default characters for players so game begins ready for gameplay in player phase
    const charactersToDraft = [...initialState.characterDraftPool].slice(0, 2);
    if (charactersToDraft[0]) {
      initialState = gameReducer(initialState, {
        actionId: 1,
        type: 'draft_character',
        playerId: 'player-1',
        characterId: charactersToDraft[0],
      });
    }
    if (charactersToDraft[1]) {
      initialState = gameReducer(initialState, {
        actionId: 2,
        type: 'draft_character',
        playerId: 'player-2',
        characterId: charactersToDraft[1],
      });
    }

    this.state = initialState;

    const bct = new BroadcastChannelTransport(`nemesis-rt-${this.roomCode}`);
    this.transport = bct;

    this.coordinator = new NetworkCoordinator(
      formatPeerId(this.roomCode) + (isHost ? '-host' : `-${Date.now()}`),
      playerName,
      isHost,
      this.state,
      bct,
    );

    bct.onMessage = (msg: NetworkMessage) => {
      this.coordinator.handleMessage(msg);
    };

    this.coordinator.onStateUpdate = (newState: GameState) => {
      this.state = newState;
      this.renderer.setState(this.state);
      this.renderUI();
    };

    this.renderer = new TacticalRenderer(canvas, {
      selectedRoomId: 'landing-zone',
      onRoomClick: (roomId) => this.handleRoomClick(roomId),
    });

    this.renderer.setState(this.state);
    this.renderUI();

    if (!isHost) {
      setTimeout(() => {
        bct.broadcast({
          type: 'join_request',
          senderPeerId: this.coordinator.peerId,
          playerName: this.coordinator.playerName,
        });
      }, 50);
    }
  }

  public dispatchAction(action: GameAction): void {
    try {
      this.coordinator.submitAction(action);
    } catch (err: any) {
      alert(`Action error: ${err.message}`);
    }
  }

  private handleRoomClick(roomId: string): void {
    this.renderer.options.selectedRoomId = roomId;
    this.renderUI();
  }

  public renderUI(): void {
    let uiStyles = document.getElementById('nemesis-responsive-styles');
    if (!uiStyles) {
      uiStyles = document.createElement('style');
      uiStyles.id = 'nemesis-responsive-styles';
      uiStyles.textContent = `
        #nemesis-ui-overlay {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          pointer-events: none;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        .nemesis-top-bar {
          pointer-events: auto;
          background: rgba(15, 23, 42, 0.94);
          backdrop-filter: blur(8px);
          border-bottom: 1px solid #334155;
          padding: 8px 14px;
          display: flex;
          flex-wrap: wrap;
          justify-content: space-between;
          align-items: center;
          gap: 6px 12px;
          color: #f8fafc;
        }

        .nemesis-top-left {
          display: flex;
          align-items: center;
          flex-wrap: wrap;
          gap: 6px 10px;
        }

        .nemesis-brand {
          font-weight: 800;
          font-size: 14px;
          letter-spacing: 0.5px;
          color: #facc15;
          white-space: nowrap;
        }

        .nemesis-pills-group {
          display: flex;
          align-items: center;
          flex-wrap: wrap;
          gap: 6px;
        }

        .nemesis-badge {
          padding: 2px 6px;
          background: #1e293b;
          border: 1px solid #334155;
          border-radius: 4px;
          font-size: 11px;
          font-weight: 600;
          white-space: nowrap;
        }

        .nemesis-life-support {
          display: flex;
          align-items: center;
          flex-wrap: wrap;
          gap: 4px 6px;
          font-size: 11px;
          font-weight: 500;
          white-space: nowrap;
        }

        .nemesis-bottom-bar {
          pointer-events: auto;
          background: rgba(15, 23, 42, 0.96);
          backdrop-filter: blur(10px);
          border-top: 1px solid #334155;
          padding: 8px 12px max(8px, env(safe-area-inset-bottom));
          box-sizing: border-box;
          color: #f8fafc;
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .nemesis-player-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 6px 10px;
        }

        .nemesis-player-info {
          display: flex;
          align-items: center;
          flex-wrap: wrap;
          gap: 6px;
          font-size: 12px;
        }

        .nemesis-stat-pill {
          padding: 2px 6px;
          border-radius: 4px;
          font-size: 11px;
          font-weight: 600;
          background: #1e293b;
          border: 1px solid #334155;
          display: inline-flex;
          align-items: center;
          gap: 4px;
          white-space: nowrap;
        }

        .nemesis-hand-drawer {
          display: flex;
          gap: 8px;
          overflow-x: auto;
          padding: 2px 0 4px 0;
          -webkit-overflow-scrolling: touch;
          scroll-snap-type: x mandatory;
        }

        .nemesis-card {
          scroll-snap-align: start;
          flex-shrink: 0;
          width: 130px;
          border-radius: 6px;
          padding: 7px;
          font-size: 11px;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          box-sizing: border-box;
          user-select: none;
        }

        .nemesis-debug-toggle {
          position: fixed;
          top: 50px;
          right: 12px;
          z-index: 9999;
          background: rgba(15, 23, 42, 0.85);
          color: #38bdf8;
          border: 1px solid #0284c7;
          border-radius: 4px;
          padding: 4px 8px;
          font-size: 11px;
          font-weight: bold;
          cursor: pointer;
          pointer-events: auto;
          backdrop-filter: blur(4px);
        }
        .nemesis-debug-panel {
          position: fixed;
          top: 80px;
          right: 12px;
          max-width: calc(100vw - 24px);
          width: 320px;
          z-index: 9999;
          background: rgba(15, 23, 42, 0.95);
          color: #f1f5f9;
          border: 1px solid #38bdf8;
          border-radius: 6px;
          padding: 10px;
          font-size: 11px;
          font-family: monospace;
          box-shadow: 0 4px 20px rgba(0,0,0,0.6);
          pointer-events: auto;
          backdrop-filter: blur(8px);
        }
        .nemesis-debug-panel textarea {
          width: 100%;
          height: 120px;
          background: #0b0f19;
          color: #a5f3fc;
          border: 1px solid #334155;
          border-radius: 4px;
          font-family: monospace;
          font-size: 10px;
          padding: 6px;
          resize: none;
          box-sizing: border-box;
        }
        .nemesis-debug-copy-btn {
          background: #0284c7;
          color: white;
          border: none;
          border-radius: 4px;
          padding: 4px 10px;
          font-size: 11px;
          font-weight: bold;
          cursor: pointer;
          margin-top: 6px;
          width: 100%;
        }

        .nemesis-cam-controls {
          position: fixed;
          left: 14px;
          top: 60px;
          display: flex;
          flex-direction: column;
          gap: 6px;
          z-index: 999;
          pointer-events: auto;
        }
        .nemesis-cam-btn {
          width: 34px;
          height: 34px;
          background: rgba(15, 23, 42, 0.85);
          border: 1px solid #334155;
          color: #f8fafc;
          border-radius: 6px;
          font-size: 15px;
          font-weight: bold;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          backdrop-filter: blur(6px);
          user-select: none;
          transition: all 0.15s ease;
        }
        .nemesis-cam-btn:hover {
          background: #1e293b;
          border-color: #38bdf8;
          color: #38bdf8;
        }

        @media (max-width: 600px) {
          .nemesis-brand {
            font-size: 12px;
          }
          .nemesis-badge, .nemesis-stat-pill {
            font-size: 10px;
            padding: 2px 5px;
          }
          .nemesis-card {
            width: 115px;
            padding: 6px;
          }
          #btn-pass {
            padding: 5px 10px !important;
            font-size: 11px !important;
          }
        }
      `;
      document.head.appendChild(uiStyles);
    }

    let uiOverlay = document.getElementById('nemesis-ui-overlay');
    if (!uiOverlay) {
      uiOverlay = document.createElement('div');
      uiOverlay.id = 'nemesis-ui-overlay';
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
      <div class="nemesis-top-bar">
        <div class="nemesis-top-left">
          <span class="nemesis-brand">NEMESIS: RETALIATION</span>
          <div class="nemesis-pills-group">
            <span class="nemesis-badge">Round: ${this.state.round} / 15</span>
            <span class="nemesis-badge" style="text-transform: uppercase;">Phase: ${this.state.phase}</span>
            <span class="nemesis-badge" style="color: #94a3b8;">Room Code: <b style="color: #f8fafc;">${this.roomCode}</b></span>
          </div>
        </div>
        <div class="nemesis-life-support">
          <span style="color: #94a3b8;">Life Support:</span>
          <span class="nemesis-badge" style="color: ${this.state.lifeSupport.A ? '#22c55e' : '#ef4444'};">Sec A: ${this.state.lifeSupport.A ? 'ON' : 'OFF'}</span>
          <span class="nemesis-badge" style="color: ${this.state.lifeSupport.B ? '#22c55e' : '#ef4444'};">Sec B: ${this.state.lifeSupport.B ? 'ON' : 'OFF'}</span>
          <span class="nemesis-badge" style="color: ${this.state.lifeSupport.C ? '#22c55e' : '#ef4444'};">Sec C: ${this.state.lifeSupport.C ? 'ON' : 'OFF'}</span>
        </div>
      </div>

      <div class="nemesis-bottom-bar">
        <div class="nemesis-player-row">
          <div class="nemesis-player-info">
            <b>Active:</b> <span>${activePlayer?.name ?? 'None'} ${activeChar ? `(${activeChar.name})` : ''}</span>
            <span class="nemesis-stat-pill">Actions Remaining: <b>${activeChar?.actionsRemaining ?? 0}</b></span>
            ${activeChar ? `
              <span class="nemesis-stat-pill">HP: <b>${activeChar.health}/${activeChar.maxHealth}</b></span>
              <span class="nemesis-stat-pill">O2: <b>${activeChar.oxygen}</b></span>
            ` : ''}
            ${playerInCombat 
              ? '<span class="nemesis-stat-pill" style="background: #991b1b; color: #fee2e2; border-color: #ef4444;">⚔️ IN COMBAT</span>' 
              : '<span class="nemesis-stat-pill" style="color: #4ade80;">🛡️ Safe</span>'}
          </div>
          <div>
            <button id="btn-pass" style="background: #e11d48; color: white; border: none; padding: 6px 14px; border-radius: 4px; cursor: pointer; font-weight: bold; white-space: nowrap;">PASS TURN</button>
          </div>
        </div>

        ${activeChar ? `
        <div class="nemesis-hand-drawer">
          ${activeChar.hand.map(card => {
            const isPlayable = !playerInCombat || card.usableInCombat;
            return `
            <div class="nemesis-card" style="background: ${isPlayable ? '#1e293b' : '#1e1b24'}; border: 1px solid ${isPlayable ? '#475569' : '#7f1d1d'}; opacity: ${isPlayable ? '1.0' : '0.6'};">
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

      <div class="nemesis-cam-controls">
        <button id="btn-cam-zoomin" class="nemesis-cam-btn" title="Zoom In">+</button>
        <button id="btn-cam-zoomout" class="nemesis-cam-btn" title="Zoom Out">−</button>
        <button id="btn-cam-focus" class="nemesis-cam-btn" title="Focus Crew">🎯</button>
        <button id="btn-cam-reset" class="nemesis-cam-btn" title="Reset View">⟲</button>
      </div>

      <button id="btn-toggle-debug" class="nemesis-debug-toggle">
        ${this.isDebugOpen ? '✕ CLOSE DEBUG' : '🔍 VIEWPORT'}
      </button>

      ${this.isDebugOpen ? `
        <div class="nemesis-debug-panel" id="nemesis-debug-box">
          <div style="font-weight: bold; margin-bottom: 6px; color: #38bdf8; display: flex; justify-content: space-between;">
            <span>VIEWPORT DIAGNOSTICS</span>
            <span style="font-size: 10px; color: #94a3b8;">${window.innerWidth}×${window.innerHeight}</span>
          </div>
          <textarea readonly id="nemesis-debug-textarea">${JSON.stringify({
            window: {
              innerWidth: window.innerWidth,
              innerHeight: window.innerHeight,
              devicePixelRatio: window.devicePixelRatio,
            },
            visualViewport: window.visualViewport ? {
              width: Math.round(window.visualViewport.width),
              height: Math.round(window.visualViewport.height),
              scale: window.visualViewport.scale,
            } : null,
            screen: {
              width: window.screen.width,
              height: window.screen.height,
              orientation: window.screen.orientation?.type ?? 'unknown',
            },
            canvas: {
              width: this.renderer.canvas.width,
              height: this.renderer.canvas.height,
              clientWidth: this.renderer.canvas.clientWidth,
              clientHeight: this.renderer.canvas.clientHeight,
            },
            camera: {
              x: Math.round(this.renderer.camera.transform.x),
              y: Math.round(this.renderer.camera.transform.y),
              zoom: Number(this.renderer.camera.transform.zoom.toFixed(3)),
            },
            userAgent: navigator.userAgent,
          }, null, 2)}</textarea>
          <button id="btn-copy-debug" class="nemesis-debug-copy-btn">📋 COPY TO CLIPBOARD</button>
        </div>
      ` : ''}
    `;

    document.getElementById('btn-toggle-debug')?.addEventListener('click', () => {
      this.isDebugOpen = !this.isDebugOpen;
      this.renderUI();
    });

    document.getElementById('btn-copy-debug')?.addEventListener('click', () => {
      const textarea = document.getElementById('nemesis-debug-textarea') as HTMLTextAreaElement | null;
      if (textarea) {
        textarea.select();
        navigator.clipboard?.writeText(textarea.value).catch(() => {
          document.execCommand('copy');
        });
        const btn = document.getElementById('btn-copy-debug');
        if (btn) btn.textContent = '✓ COPIED TO CLIPBOARD!';
      }
    });

    // Camera Controls
    document.getElementById('btn-cam-zoomin')?.addEventListener('click', () => {
      this.renderer.zoomIn();
    });
    document.getElementById('btn-cam-zoomout')?.addEventListener('click', () => {
      this.renderer.zoomOut();
    });
    document.getElementById('btn-cam-focus')?.addEventListener('click', () => {
      if (activeChar) {
        this.renderer.focusRoom(activeChar.currentRoomId, 1.25);
      } else {
        this.renderer.focusRoom('landing-zone', 1.25);
      }
    });
    document.getElementById('btn-cam-reset')?.addEventListener('click', () => {
      this.renderer.fitToScreen(16);
    });

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
