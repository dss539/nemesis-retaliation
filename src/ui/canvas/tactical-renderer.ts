/**
 * Tactical Canvas 2D Renderer for Nemesis: Retaliation.
 * High-performance pointy-top hex rendering, corridor network, doors, tokens, and targeting overlays.
 */

import { GameState } from '../../engine/types/state.js';
import { BoardSlotDefinition, BOARD_SLOTS } from '../../engine/spatial/hex.js';
import { Camera2D } from './camera.js';
import { RoomId } from '../../engine/types/primitives.js';

export interface RendererOptions {
  hexWidth?: number;
  highlightedRoomIds?: string[];
  highlightedCorridorIds?: string[];
  selectedRoomId?: string | null;
  onRoomClick?: (roomId: RoomId) => void;
}

export class TacticalRenderer {
  public canvas: HTMLCanvasElement;
  public ctx: CanvasRenderingContext2D;
  public camera: Camera2D;
  public options: Required<RendererOptions>;
  public state: GameState | null = null;

  // Geometry
  public hexW: number;
  public hexH: number;
  public stepX: number;
  public stepY: number;

  private animFrameId: number | null = null;
  private isRunning = false;

  constructor(canvas: HTMLCanvasElement, options: RendererOptions = {}) {
    this.canvas = canvas;
    const ctx = canvas.getContext('2d');
    if (!ctx) throw new Error('Could not get 2D context from canvas');
    this.ctx = ctx;
    this.camera = new Camera2D();

    this.hexW = options.hexWidth ?? 140;
    this.hexH = (this.hexW * 2) / Math.sqrt(3);
    this.stepX = this.hexW * 1.68;
    this.stepY = (this.stepX * Math.sqrt(3)) / 2;

    this.options = {
      hexWidth: this.hexW,
      highlightedRoomIds: options.highlightedRoomIds ?? [],
      highlightedCorridorIds: options.highlightedCorridorIds ?? [],
      selectedRoomId: options.selectedRoomId ?? null,
      onRoomClick: options.onRoomClick ?? (() => {}),
    };

    this.setupEventListeners();
  }

  public setState(state: GameState): void {
    this.state = state;
  }

  /**
   * Computes the world center (cx, cy) for a given grid slot (x, y).
   */
  public getSlotCenter(x: number, y: number): { cx: number; cy: number } {
    const odd = y % 2 !== 0;
    const cx = x * this.stepX + (odd ? 0.5 * this.stepX : 0) + this.hexW;
    const cy = y * this.stepY + this.hexH;
    return { cx, cy };
  }

  /**
   * Computes the 6 vertices of a pointy-top hexagon centered at (cx, cy).
   */
  public getHexVertices(cx: number, cy: number): [number, number][] {
    const w = this.hexW;
    const h = this.hexH;
    return [
      [cx, cy - h / 2],
      [cx + w / 2, cy - h / 4],
      [cx + w / 2, cy + h / 4],
      [cx, cy + h / 2],
      [cx - w / 2, cy + h / 4],
      [cx - w / 2, cy - h / 4],
    ];
  }

  /**
   * Checks if world coordinate (px, py) is inside the pointy-top hex centered at (cx, cy).
   */
  public isPointInHex(px: number, py: number, cx: number, cy: number): boolean {
    const dx = Math.abs(px - cx);
    const dy = Math.abs(py - cy);
    const w = this.hexW / 2;
    const h = this.hexH / 2;

    if (dx > w || dy > h) return false;
    // Slanted top and bottom corners
    return (h * 0.5) * w - (h * 0.5) * dx - w * (dy - h * 0.5) >= 0;
  }

  /**
   * Hit-tests screen coordinates to find the clicked board slot.
   */
  public hitTestSlot(screenX: number, screenY: number): BoardSlotDefinition | null {
    const world = this.camera.screenToWorld(screenX, screenY);
    for (const slot of BOARD_SLOTS) {
      const { cx, cy } = this.getSlotCenter(slot.x, slot.y);
      if (this.isPointInHex(world.x, world.y, cx, cy)) {
        return slot;
      }
    }
    return null;
  }

  /**
   * Renders a complete frame.
   */
  public render(): void {
    const { ctx, canvas } = this;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.save();
    ctx.translate(this.camera.transform.x, this.camera.transform.y);
    ctx.scale(this.camera.transform.zoom, this.camera.transform.zoom);

    this.renderSectionBands();
    this.renderCorridors();
    this.renderRoomSlots();

    ctx.restore();
  }

  private renderSectionBands(): void {
    const { ctx } = this;
    const bounds = this.getBoardWorldBounds();
    const padY = 60;
    const topY = bounds.minY - padY;
    const bottomY = bounds.maxY + padY;

    // Seam lines separating A/B and B/C (FND-005, play-area-design.md, render.js)
    // Seams sit midway through the corridor spaces at effective-column boundaries:
    // A/B seam: hexW / 2 + 1.25 * stepX
    // B/C seam: hexW / 2 + 2.75 * stepX
    const seamAB = this.hexW / 2 + 1.25 * this.stepX + this.hexW;
    const seamBC = this.hexW / 2 + 2.75 * this.stepX + this.hexW;

    ctx.save();

    // Section Labels at top
    ctx.font = 'bold 12px monospace';
    ctx.textAlign = 'center';

    // Section A watermark
    ctx.fillStyle = '#38bdf8';
    ctx.fillText('◄ SECTION A · WEST ◄', (bounds.minX + seamAB) / 2, topY + 18);

    // Section B watermark
    ctx.fillStyle = '#4ade80';
    ctx.fillText('◆ SECTION B · FACILITY CORE ◆', (seamAB + seamBC) / 2, topY + 18);

    // Section C watermark
    ctx.fillStyle = '#f87171';
    ctx.fillText('► SECTION C · EAST ►', (seamBC + bounds.maxX) / 2, topY + 18);

    // Two bright continuous vertical seam lines (playmat design fidelity)
    const drawSeam = (x: number, label: string) => {
      ctx.beginPath();
      ctx.setLineDash([10, 6]);
      ctx.moveTo(x, topY + 28);
      ctx.lineTo(x, bottomY - 10);
      ctx.lineWidth = 2;
      ctx.strokeStyle = 'rgba(207, 232, 239, 0.45)';
      ctx.stroke();
      ctx.setLineDash([]);

      ctx.fillStyle = 'rgba(207, 232, 239, 0.7)';
      ctx.font = 'bold 10px monospace';
      ctx.fillText(`SEAM ${label}`, x, bottomY);
    };

    drawSeam(seamAB, 'A / B');
    drawSeam(seamBC, 'B / C');

    ctx.restore();
  }

  private renderCorridors(): void {
    if (!this.state) return;
    const { ctx } = this;

    for (const corridor of Object.values(this.state.board.corridors)) {
      const slotA = BOARD_SLOTS.find(s => s.slotId === corridor.slotA);
      const slotB = BOARD_SLOTS.find(s => s.slotId === corridor.slotB);
      if (!slotA || !slotB) continue;

      const posA = this.getSlotCenter(slotA.x, slotA.y);
      const posB = this.getSlotCenter(slotB.x, slotB.y);

      const dx = posB.cx - posA.cx;
      const dy = posB.cy - posA.cy;
      const dist = Math.hypot(dx, dy);
      if (dist === 0) continue;

      const ux = dx / dist;
      const uy = dy / dist;

      // Span strictly from edge of Room A to edge of Room B (FND-005)
      const r = this.hexW * 0.48;
      const startX = posA.cx + ux * r;
      const startY = posA.cy + uy * r;
      const endX = posB.cx - ux * r;
      const endY = posB.cy - uy * r;

      ctx.save();

      // Corridor outer walls (steel structure)
      ctx.beginPath();
      ctx.moveTo(startX, startY);
      ctx.lineTo(endX, endY);
      ctx.lineWidth = 26;
      ctx.strokeStyle = '#1e293b';
      ctx.lineCap = 'butt';
      ctx.stroke();

      // Corridor inner floor walkway
      ctx.lineWidth = 18;
      ctx.strokeStyle = corridor.hasNoise ? '#78350f' : '#090d16';
      ctx.stroke();

      // Midpoint for Doors & Noise
      const midX = (startX + endX) / 2;
      const midY = (startY + endY) / 2;

      // Door rendering
      if (corridor.doorState === 'closed') {
        ctx.save();
        ctx.translate(midX, midY);
        const angle = Math.atan2(dy, dx);
        ctx.rotate(angle + Math.PI / 2);

        // Bulkhead door barrier
        ctx.fillStyle = '#ef4444';
        ctx.fillRect(-12, -3, 24, 6);
        ctx.strokeStyle = '#7f1d1d';
        ctx.lineWidth = 1;
        ctx.strokeRect(-12, -3, 24, 6);

        ctx.restore();
      } else if (corridor.doorState === 'open') {
        ctx.save();
        ctx.translate(midX, midY);
        const angle = Math.atan2(dy, dx);
        ctx.rotate(angle + Math.PI / 2);

        // Retracted door tracks
        ctx.fillStyle = '#22c55e';
        ctx.fillRect(-12, -2, 6, 4);
        ctx.fillRect(6, -2, 6, 4);

        ctx.restore();
      }

      // Noise marker
      if (corridor.hasNoise) {
        ctx.fillStyle = '#f59e0b';
        ctx.beginPath();
        ctx.arc(midX + (corridor.doorState === 'closed' || corridor.doorState === 'open' ? 12 : 0), midY, 5, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 1;
        ctx.stroke();
      }

      ctx.restore();
    }
  }

  private renderRoomSlots(): void {
    const { ctx } = this;
    const state = this.state;

    for (const slot of BOARD_SLOTS) {
      const { cx, cy } = this.getSlotCenter(slot.x, slot.y);
      const vertices = this.getHexVertices(cx, cy);
      const room = state?.board.rooms[slot.slotId];
      const isDiscovered = room?.isDiscovered ?? false;
      const isSelected = this.options.selectedRoomId === slot.slotId;
      const isHighlighted = this.options.highlightedRoomIds.includes(slot.slotId);

      ctx.save();
      ctx.beginPath();
      ctx.moveTo(vertices[0]![0], vertices[0]![1]);
      for (let i = 1; i < vertices.length; i++) {
        ctx.lineTo(vertices[i]![0], vertices[i]![1]);
      }
      ctx.closePath();

      // Background Fill
      if (isDiscovered) {
        ctx.fillStyle = '#0f172a';
      } else {
        ctx.fillStyle = '#070b14';
      }
      ctx.fill();

      // Outer Border
      if (isSelected) {
        ctx.lineWidth = 3.5;
        ctx.strokeStyle = '#facc15';
      } else if (isHighlighted) {
        ctx.lineWidth = 3;
        ctx.strokeStyle = '#22c55e';
      } else if (isDiscovered) {
        ctx.lineWidth = 2.5;
        ctx.strokeStyle = slot.isLandingZone ? '#f59e0b' : '#38bdf8';
      } else {
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = '#1e293b';
      }
      ctx.stroke();

      // Subtle inner hex chamfer for tactical socket look
      ctx.beginPath();
      const innerScale = 0.88;
      for (let i = 0; i < vertices.length; i++) {
        const vx = cx + (vertices[i]![0] - cx) * innerScale;
        const vy = cy + (vertices[i]![1] - cy) * innerScale;
        if (i === 0) ctx.moveTo(vx, vy);
        else ctx.lineTo(vx, vy);
      }
      ctx.closePath();
      ctx.strokeStyle = isDiscovered ? 'rgba(56, 189, 248, 0.15)' : 'rgba(30, 41, 59, 0.4)';
      ctx.lineWidth = 1;
      ctx.stroke();

      // Content inside the room
      if (isDiscovered && room?.tile) {
        // Room Name
        ctx.fillStyle = '#f8fafc';
        ctx.font = 'bold 13px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(room.tile.name, cx, cy - 14);

        // Status indicators
        const tokens: string[] = [];
        if (room.fire) tokens.push('🔥 FIRE');
        if (room.malfunction) tokens.push('⚠️ MALF');
        if (room.secureTokens > 0) tokens.push(`🛡️ x${room.secureTokens}`);
        if (room.searchTokens > 0) tokens.push(`🔍 x${room.searchTokens}`);

        if (tokens.length > 0) {
          ctx.font = 'bold 10px sans-serif';
          ctx.fillStyle = '#fbbf24';
          ctx.fillText(tokens.join(' · '), cx, cy + 4);
        }

        // Characters present
        if (room.characterIds.length > 0) {
          const names = room.characterIds.map(id => this.state?.characters[id]?.name ?? id);
          const label = names.length > 1 ? `👥 ${names.length} Crew (${names.join(', ')})` : `👥 ${names[0] ?? ''}`;

          // Badge pill behind crew
          ctx.font = 'bold 11px sans-serif';
          const textW = ctx.measureText(label).width;
          const badgeW = Math.min(this.hexW - 16, textW + 16);

          ctx.fillStyle = 'rgba(2, 132, 199, 0.35)';
          ctx.fillRect(cx - badgeW / 2, cy + 14, badgeW, 20);
          ctx.strokeStyle = '#0284c7';
          ctx.lineWidth = 1.5;
          ctx.strokeRect(cx - badgeW / 2, cy + 14, badgeW, 20);

          ctx.fillStyle = '#38bdf8';
          ctx.fillText(label, cx, cy + 28);
        }
      } else {
        // Unexplored socket indicator
        ctx.textAlign = 'center';
        ctx.font = 'bold 11px monospace';
        ctx.fillStyle = '#7dd3fc';
        ctx.fillText(`[SEC ${slot.section}]`, cx, cy - 8);

        ctx.font = 'bold 10px monospace';
        ctx.fillStyle = '#94a3b8';
        ctx.fillText(slot.slotId.replace('slot_', ''), cx, cy + 9);
      }

      ctx.restore();
    }
  }

  public getBoardWorldBounds(): { minX: number; minY: number; maxX: number; maxY: number } {
    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;

    for (const slot of BOARD_SLOTS) {
      const { cx, cy } = this.getSlotCenter(slot.x, slot.y);
      minX = Math.min(minX, cx - this.hexW / 2);
      minY = Math.min(minY, cy - this.hexH / 2);
      maxX = Math.max(maxX, cx + this.hexW / 2);
      maxY = Math.max(maxY, cy + this.hexH / 2);
    }

    return { minX, minY, maxX, maxY };
  }

  public focusRoom(roomId: string, zoom = 1.2): void {
    const slot = BOARD_SLOTS.find(s => s.slotId === roomId);
    if (!slot) return;
    const { cx, cy } = this.getSlotCenter(slot.x, slot.y);

    const topBar = document.querySelector('.nemesis-top-bar') as HTMLElement | null;
    const bottomBar = document.querySelector('.nemesis-bottom-bar') as HTMLElement | null;
    const topInset = topBar ? topBar.offsetHeight : 50;
    const bottomInset = bottomBar ? bottomBar.offsetHeight : 140;

    const screenCenterY = topInset + (this.canvas.height - topInset - bottomInset) / 2;

    this.camera.transform.zoom = zoom;
    this.camera.transform.x = this.canvas.width / 2 - cx * zoom;
    this.camera.transform.y = screenCenterY - cy * zoom;
    this.render();
  }

  public zoomIn(): void {
    const topBar = document.querySelector('.nemesis-top-bar') as HTMLElement | null;
    const bottomBar = document.querySelector('.nemesis-bottom-bar') as HTMLElement | null;
    const topInset = topBar ? topBar.offsetHeight : 50;
    const bottomInset = bottomBar ? bottomBar.offsetHeight : 140;
    const centerY = topInset + (this.canvas.height - topInset - bottomInset) / 2;
    this.camera.zoomAt(this.canvas.width / 2, centerY, 1.25);
    this.render();
  }

  public zoomOut(): void {
    const topBar = document.querySelector('.nemesis-top-bar') as HTMLElement | null;
    const bottomBar = document.querySelector('.nemesis-bottom-bar') as HTMLElement | null;
    const topInset = topBar ? topBar.offsetHeight : 50;
    const bottomInset = bottomBar ? bottomBar.offsetHeight : 140;
    const centerY = topInset + (this.canvas.height - topInset - bottomInset) / 2;
    this.camera.zoomAt(this.canvas.width / 2, centerY, 0.8);
    this.render();
  }

  public fitToScreen(padding = 16): void {
    const bounds = this.getBoardWorldBounds();
    const topBar = document.querySelector('.nemesis-top-bar') as HTMLElement | null;
    const bottomBar = document.querySelector('.nemesis-bottom-bar') as HTMLElement | null;

    const topInset = topBar ? topBar.offsetHeight : 50;
    const bottomInset = bottomBar ? bottomBar.offsetHeight : 140;

    this.camera.fitToBounds(
      bounds,
      this.canvas.width,
      this.canvas.height,
      padding,
      topInset,
      bottomInset
    );
    this.render();
  }

  private setupEventListeners(): void {
    let isDragging = false;
    let lastX = 0;
    let lastY = 0;

    // Mouse Controls
    this.canvas.addEventListener('mousedown', (e: MouseEvent) => {
      isDragging = true;
      lastX = e.clientX;
      lastY = e.clientY;
    });

    window.addEventListener('mousemove', (e: MouseEvent) => {
      if (!isDragging) return;
      const dx = e.clientX - lastX;
      const dy = e.clientY - lastY;
      lastX = e.clientX;
      lastY = e.clientY;
      this.camera.pan(dx, dy);
      this.render();
    });

    window.addEventListener('mouseup', () => {
      isDragging = false;
    });

    this.canvas.addEventListener('wheel', (e: WheelEvent) => {
      e.preventDefault();
      const rect = this.canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;
      const factor = e.deltaY < 0 ? 1.1 : 0.9;
      this.camera.zoomAt(mouseX, mouseY, factor);
      this.render();
    }, { passive: false });

    this.canvas.addEventListener('click', (e: MouseEvent) => {
      const rect = this.canvas.getBoundingClientRect();
      const screenX = e.clientX - rect.left;
      const screenY = e.clientY - rect.top;
      const slot = this.hitTestSlot(screenX, screenY);
      if (slot) {
        this.options.onRoomClick(slot.slotId);
      }
    });

    // Touch Controls (Mobile & Tablet: single-touch pan, pinch-to-zoom with seamless finger-lift)
    let isPinching = false;
    let initialPinchDistance = 0;
    let lastTouchX = 0;
    let lastTouchY = 0;

    this.canvas.addEventListener('touchstart', (e: TouchEvent) => {
      if (e.touches.length === 1) {
        isPinching = false;
        const touch = e.touches[0]!;
        lastTouchX = touch.clientX;
        lastTouchY = touch.clientY;
      } else if (e.touches.length === 2) {
        isPinching = true;
        const t1 = e.touches[0]!;
        const t2 = e.touches[1]!;
        initialPinchDistance = Math.hypot(t2.clientX - t1.clientX, t2.clientY - t1.clientY);
      }
    }, { passive: true });

    this.canvas.addEventListener('touchmove', (e: TouchEvent) => {
      if (e.touches.length === 1) {
        const touch = e.touches[0]!;
        // If we were pinching and lifted one finger, re-anchor coordinates to prevent jumping
        if (isPinching) {
          isPinching = false;
          lastTouchX = touch.clientX;
          lastTouchY = touch.clientY;
          return;
        }

        const dx = touch.clientX - lastTouchX;
        const dy = touch.clientY - lastTouchY;
        lastTouchX = touch.clientX;
        lastTouchY = touch.clientY;
        this.camera.pan(dx, dy);
        this.render();
      } else if (e.touches.length === 2) {
        isPinching = true;
        const t1 = e.touches[0]!;
        const t2 = e.touches[1]!;
        const currentDist = Math.hypot(t2.clientX - t1.clientX, t2.clientY - t1.clientY);
        if (initialPinchDistance > 0 && currentDist > 0) {
          const factor = currentDist / initialPinchDistance;
          const midX = (t1.clientX + t2.clientX) / 2;
          const midY = (t1.clientY + t2.clientY) / 2;
          const rect = this.canvas.getBoundingClientRect();
          this.camera.zoomAt(midX - rect.left, midY - rect.top, factor);
          initialPinchDistance = currentDist;
          this.render();
        }
      }
    }, { passive: true });

    const handleTouchEnd = (e: TouchEvent) => {
      if (e.touches.length === 1) {
        // One finger still touching: re-anchor coordinates to prevent jump on subsequent moves
        const touch = e.touches[0]!;
        lastTouchX = touch.clientX;
        lastTouchY = touch.clientY;
        isPinching = false;
        initialPinchDistance = 0;
      } else if (e.touches.length === 0) {
        isPinching = false;
        initialPinchDistance = 0;
      }
    };

    this.canvas.addEventListener('touchend', handleTouchEnd, { passive: true });
    this.canvas.addEventListener('touchcancel', handleTouchEnd, { passive: true });
  }

  public startAnimationLoop(): void {
    if (this.isRunning) return;
    this.isRunning = true;
    const loop = () => {
      if (!this.isRunning) return;
      this.render();
      this.animFrameId = requestAnimationFrame(loop);
    };
    loop();
  }

  public stopAnimationLoop(): void {
    this.isRunning = false;
    if (this.animFrameId !== null) {
      cancelAnimationFrame(this.animFrameId);
      this.animFrameId = null;
    }
  }
}
