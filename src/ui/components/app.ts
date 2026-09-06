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
import { BOARD_SLOTS } from '../../engine/spatial/hex.js';
import { RoomId } from '../../engine/types/primitives.js';

export class NemesisApp {
  public state: GameState;
  public renderer: TacticalRenderer;
  public coordinator: NetworkCoordinator;
  public roomCode: string;
  public container: HTMLElement;
  public isDebugOpen: boolean = false;
  public transport: NetworkTransport;
  public selectedRoomId: string | null = 'landing-zone';
  public selectedCardId: string | null = null;
  public toastMessage: { text: string; isError: boolean } | null = null;

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

  public showToast(text: string, isError = false): void {
    this.toastMessage = { text, isError };
    this.renderUI();
    setTimeout(() => {
      if (this.toastMessage?.text === text) {
        this.toastMessage = null;
        this.renderUI();
      }
    }, 4000);
  }

  public dispatchAction(action: GameAction): void {
    try {
      this.coordinator.submitAction(action);
      this.selectedCardId = null;
    } catch (err: any) {
      this.showToast(err.message, true);
    }
  }

  private handleRoomClick(roomId: string): void {
    this.selectedRoomId = roomId;
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

        .nemesis-action-dock {
          background: rgba(15, 23, 42, 0.95);
          border: 1px solid #334155;
          border-radius: 6px;
          padding: 8px 12px;
          margin-bottom: 8px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 8px;
        }
        .nemesis-btn-action {
          padding: 6px 12px;
          border-radius: 4px;
          border: none;
          font-size: 11px;
          font-weight: bold;
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          gap: 6px;
          color: white;
          white-space: nowrap;
          transition: transform 0.1s ease, filter 0.15s ease;
        }
        .nemesis-btn-action:hover {
          transform: translateY(-1px);
          filter: brightness(1.15);
        }
        .nemesis-btn-action.move {
          background: #0284c7;
        }
        .nemesis-btn-action.cautious {
          background: #d97706;
        }
        .nemesis-btn-action.search {
          background: #059669;
        }
        .nemesis-btn-action.combat {
          background: #dc2626;
        }
        .nemesis-phase-banner {
          padding: 10px 14px;
          border-radius: 6px;
          margin-bottom: 8px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 10px;
        }
        .nemesis-toast {
          position: fixed;
          top: 55px;
          left: 50%;
          transform: translateX(-50%);
          z-index: 10000;
          padding: 8px 16px;
          border-radius: 6px;
          font-size: 12px;
          font-weight: bold;
          pointer-events: auto;
          box-shadow: 0 4px 15px rgba(0,0,0,0.5);
          color: white;
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
    const currentRoomId = activeChar?.currentRoomId;

    // Calculate legal move destinations from current room via open corridors
    const connectedCorridors = currentRoomId
      ? Object.values(this.state.board.corridors).filter(
          c => (c.slotA === currentRoomId || c.slotB === currentRoomId) && c.doorState !== 'closed'
        )
      : [];
    const legalMoveRoomIds = connectedCorridors.map(c =>
      c.slotA === currentRoomId ? c.slotB : c.slotA
    );

    // Update tactical renderer highlights
    this.renderer.options.highlightedRoomIds = legalMoveRoomIds;
    this.renderer.options.selectedRoomId = this.selectedRoomId;

    const selectedSlot = this.selectedRoomId ? BOARD_SLOTS.find(s => s.slotId === this.selectedRoomId) : null;
    const selectedRoom = this.selectedRoomId ? this.state.board.rooms[this.selectedRoomId] : null;
    const isSelectedCurrent = Boolean(this.selectedRoomId && this.selectedRoomId === currentRoomId);
    const isSelectedAdjacent = Boolean(this.selectedRoomId && legalMoveRoomIds.includes(this.selectedRoomId));

    const playerInCombat = Boolean(
      activeChar &&
      this.state.board.rooms[activeChar.currentRoomId] &&
      this.state.board.rooms[activeChar.currentRoomId]!.intruderIds.length > 0
    );

    // Selected room name and details
    let selectedRoomLabel = 'None';
    if (selectedRoom?.tile) {
      selectedRoomLabel = `${selectedRoom.tile.name} (${selectedRoom.slotId})`;
    } else if (selectedSlot) {
      selectedRoomLabel = `Section ${selectedSlot.section} — Socket ${selectedSlot.slotId.replace('slot_', '')}`;
    }

    uiOverlay.innerHTML = `
      ${this.toastMessage ? `
        <div class="nemesis-toast" style="background: ${this.toastMessage.isError ? '#dc2626' : '#0284c7'};">
          ${this.toastMessage.isError ? '⚠️' : 'ℹ️'} ${this.toastMessage.text}
        </div>
      ` : ''}

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
        ${this.state.phase === 'intruder' ? `
          <div class="nemesis-phase-banner" style="background: rgba(153, 27, 27, 0.95); border: 1px solid #ef4444;">
            <div>
              <b style="color: #fee2e2;">⚠️ INTRUDER PHASE READY</b>
              <div style="font-size: 11px; color: #fca5a5;">All players passed. Resolve intruder attacks and movements.</div>
            </div>
            <button id="btn-resolve-intruder" class="nemesis-btn-action combat" style="padding: 8px 16px; font-size: 12px;">
              ⚡ RESOLVE INTRUDER PHASE
            </button>
          </div>
        ` : ''}

        ${this.state.phase === 'event' ? `
          <div class="nemesis-phase-banner" style="background: rgba(180, 83, 9, 0.95); border: 1px solid #f59e0b;">
            <div>
              <b style="color: #fef3c7;">📜 EVENT PHASE READY</b>
              <div style="font-size: 11px; color: #fde68a;">Draw and execute facility Event card.</div>
            </div>
            <button id="btn-resolve-event" class="nemesis-btn-action cautious" style="padding: 8px 16px; font-size: 12px;">
              🎲 DRAW EVENT CARD
            </button>
          </div>
        ` : ''}

        ${this.state.phase === 'cleanup' ? `
          <div class="nemesis-phase-banner" style="background: rgba(21, 128, 61, 0.95); border: 1px solid #22c55e;">
            <div>
              <b style="color: #dcfce7;">🔄 CLEANUP PHASE READY</b>
              <div style="font-size: 11px; color: #bbf7d0;">Restore oxygen, replenish hands, and advance round.</div>
            </div>
            <button id="btn-resolve-cleanup" class="nemesis-btn-action search" style="padding: 8px 16px; font-size: 12px;">
              ▶ START ROUND ${this.state.round + 1}
            </button>
          </div>
        ` : ''}

        ${this.state.phase === 'player' && this.selectedRoomId ? `
          <div class="nemesis-action-dock">
            <div style="font-size: 12px;">
              <span style="color: #94a3b8;">Target:</span>
              <b style="color: #38bdf8; margin-left: 4px;">${selectedRoomLabel}</b>
              ${isSelectedCurrent ? '<span style="background: #1e293b; color: #a5f3fc; padding: 2px 6px; border-radius: 3px; font-size: 10px; margin-left: 6px;">📍 YOU ARE HERE</span>' : ''}
              ${isSelectedAdjacent ? '<span style="background: #064e3b; color: #6ee7b7; padding: 2px 6px; border-radius: 3px; font-size: 10px; margin-left: 6px;">🎯 ADJACENT</span>' : ''}
              ${selectedRoom?.fire ? '<span style="color: #f97316; margin-left: 6px;">🔥 Fire</span>' : ''}
              ${selectedRoom?.malfunction ? '<span style="color: #eab308; margin-left: 6px;">⚠️ Malfunction</span>' : ''}
              ${selectedRoom && selectedRoom.searchTokens > 0 ? `<span style="color: #34d399; margin-left: 6px;">🔍 Items (${selectedRoom.searchTokens})</span>` : ''}
            </div>

            <div style="display: flex; gap: 6px; flex-wrap: wrap;">
              ${isSelectedAdjacent ? `
                <button id="btn-act-move" class="nemesis-btn-action move">
                  🚶 MOVE (1 Card)
                </button>
                <button id="btn-act-move-cautious" class="nemesis-btn-action cautious">
                  🛡️ CAUTIOUS (2 Cards)
                </button>
              ` : ''}

              ${isSelectedCurrent && selectedRoom && selectedRoom.searchTokens > 0 ? `
                <button id="btn-act-search" class="nemesis-btn-action search">
                  🔍 SEARCH (1 Card)
                </button>
              ` : ''}

              ${isSelectedCurrent && selectedRoom && selectedRoom.intruderIds.length > 0 ? `
                <button id="btn-act-melee" class="nemesis-btn-action combat">
                  ⚔️ MELEE ATTACK
                </button>
              ` : ''}
            </div>
          </div>
        ` : ''}

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
            const isSelectedCard = this.selectedCardId === card.id;
            return `
            <div class="nemesis-card card-item" data-card-id="${card.id}" style="background: ${isSelectedCard ? '#0e2a47' : (isPlayable ? '#1e293b' : '#1e1b24')}; border: 1.5px solid ${isSelectedCard ? '#38bdf8' : (isPlayable ? '#475569' : '#7f1d1d')}; opacity: ${isPlayable ? '1.0' : '0.6'}; cursor: pointer;">
              ${isSelectedCard ? '<div style="font-size: 9px; font-weight: bold; color: #38bdf8; margin-bottom: 2px;">✓ SELECTED COST</div>' : ''}
              <div style="font-weight: bold; margin-bottom: 4px; color: ${isPlayable ? '#38bdf8' : '#94a3b8'};">${card.title}</div>
              <div style="font-size: 9px; color: #94a3b8; line-height: 1.2; margin-bottom: 4px; flex-grow: 1;">
                ${card.rulesText ? card.rulesText.slice(0, 60) + '...' : ''}
              </div>
              <div style="font-size: 10px; margin-top: auto;">
                ${card.usableInCombat 
                  ? '<span style="color: #4ade80;">⚔️ In Combat</span>' 
                  : '<span style="color: #f87171;">⚠️ Out of Combat</span>'}
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

    // Bind card selection clicks
    document.querySelectorAll('.card-item').forEach(cardEl => {
      cardEl.addEventListener('click', () => {
        const cardId = cardEl.getAttribute('data-card-id');
        if (cardId) {
          this.selectedCardId = (this.selectedCardId === cardId) ? null : cardId;
          this.renderUI();
        }
      });
    });

    // Action Dock: Move
    document.getElementById('btn-act-move')?.addEventListener('click', () => {
      if (!activeChar || !this.selectedRoomId) return;
      const costCardId = this.selectedCardId || activeChar.hand[0]?.id;
      if (!costCardId) {
        this.showToast('No cards in hand to pay Movement cost', true);
        return;
      }
      this.dispatchAction({
        actionId: this.state.lastActionId + 1,
        type: 'move',
        characterId: activeChar.characterId,
        targetRoomId: this.selectedRoomId as RoomId,
        discardCardIds: [costCardId],
      });
    });

    // Action Dock: Cautious Move
    document.getElementById('btn-act-move-cautious')?.addEventListener('click', () => {
      if (!activeChar || !this.selectedRoomId) return;
      if (activeChar.hand.length < 2) {
        this.showToast('Cautious movement requires 2 cards in hand', true);
        return;
      }
      const c1 = activeChar.hand[0]?.id;
      const c2 = activeChar.hand[1]?.id;
      if (!c1 || !c2) return;
      this.dispatchAction({
        actionId: this.state.lastActionId + 1,
        type: 'move_cautiously',
        characterId: activeChar.characterId,
        targetRoomId: this.selectedRoomId as RoomId,
        discardCardIds: [c1, c2],
      });
    });

    // Action Dock: Search
    document.getElementById('btn-act-search')?.addEventListener('click', () => {
      if (!activeChar) return;
      const costCardId = this.selectedCardId || activeChar.hand[0]?.id;
      if (!costCardId) {
        this.showToast('No cards in hand to pay Search cost', true);
        return;
      }
      this.dispatchAction({
        actionId: this.state.lastActionId + 1,
        type: 'search',
        characterId: activeChar.characterId,
        discardCardIds: [costCardId],
      });
    });

    // Action Dock: Melee Attack
    document.getElementById('btn-act-melee')?.addEventListener('click', () => {
      if (!activeChar) return;
      const room = this.state.board.rooms[activeChar.currentRoomId];
      const targetIntruderId = room?.intruderIds[0];
      if (!targetIntruderId) return;
      const costCardId = this.selectedCardId || activeChar.hand[0]?.id;
      if (!costCardId) {
        this.showToast('No cards in hand to pay Melee cost', true);
        return;
      }
      this.dispatchAction({
        actionId: this.state.lastActionId + 1,
        type: 'melee',
        characterId: activeChar.characterId,
        targetIntruderId,
        discardCardIds: [costCardId],
      });
    });

    // Phase Transitions
    document.getElementById('btn-resolve-intruder')?.addEventListener('click', () => {
      this.dispatchAction({
        actionId: this.state.lastActionId + 1,
        type: 'resolve_intruder_phase',
      });
    });

    document.getElementById('btn-resolve-event')?.addEventListener('click', () => {
      this.dispatchAction({
        actionId: this.state.lastActionId + 1,
        type: 'resolve_event_phase',
      });
    });

    document.getElementById('btn-resolve-cleanup')?.addEventListener('click', () => {
      this.dispatchAction({
        actionId: this.state.lastActionId + 1,
        type: 'resolve_cleanup_phase',
      });
    });

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
