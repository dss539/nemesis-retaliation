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
    // Section A (Left third), Section B (Middle third), Section C (Right third)
    const bounds = this.getBoardWorldBounds();
    const totalW = bounds.maxX - bounds.minX;
    const thirdW = totalW / 3;

    ctx.save();
    // Section A
    ctx.fillStyle = 'rgba(25, 35, 55, 0.4)';
    ctx.fillRect(bounds.minX - 50, bounds.minY - 50, thirdW + 50, bounds.maxY - bounds.minY + 100);

    // Section B
    ctx.fillStyle = 'rgba(35, 45, 35, 0.4)';
    ctx.fillRect(bounds.minX + thirdW, bounds.minY - 50, thirdW, bounds.maxY - bounds.minY + 100);

    // Section C
    ctx.fillStyle = 'rgba(45, 25, 25, 0.4)';
    ctx.fillRect(bounds.minX + thirdW * 2, bounds.minY - 50, thirdW + 100, bounds.maxY - bounds.minY + 100);

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

      ctx.save();
      ctx.beginPath();
      ctx.moveTo(posA.cx, posA.cy);
      ctx.lineTo(posB.cx, posB.cy);
      ctx.lineWidth = 14;
      ctx.strokeStyle = '#2b3342';
      ctx.stroke();

      ctx.lineWidth = 8;
      ctx.strokeStyle = corridor.hasNoise ? '#e5a50a' : '#1b2230';
      ctx.stroke();

      // Door indicator at midpoint
      const midX = (posA.cx + posB.cx) / 2;
      const midY = (posA.cy + posB.cy) / 2;

      if (corridor.doorState === 'closed') {
        ctx.fillStyle = '#dc2626';
        ctx.fillRect(midX - 8, midY - 8, 16, 16);
      } else if (corridor.doorState === 'open') {
        ctx.fillStyle = '#16a34a';
        ctx.fillRect(midX - 6, midY - 6, 12, 12);
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

      // Fill color
      if (isDiscovered) {
        ctx.fillStyle = '#1e293b';
      } else {
        ctx.fillStyle = '#0f172a';
      }
      ctx.fill();

      // Border outline
      if (isSelected) {
        ctx.lineWidth = 4;
        ctx.strokeStyle = '#facc15';
      } else if (isHighlighted) {
        ctx.lineWidth = 3;
        ctx.strokeStyle = '#22c55e';
      } else {
        ctx.lineWidth = 2;
        ctx.strokeStyle = isDiscovered ? '#475569' : '#334155';
      }
      ctx.stroke();

      // Text and badges
      ctx.fillStyle = '#f8fafc';
      ctx.font = 'bold 12px sans-serif';
      ctx.textAlign = 'center';

      if (isDiscovered && room?.tile) {
        ctx.fillText(room.tile.name, cx, cy - 10);

        // Status indicators
        const tokens: string[] = [];
        if (room.fire) tokens.push('🔥 FIRE');
        if (room.malfunction) tokens.push('⚠️ MALF');
        if (room.secureTokens > 0) tokens.push(`🛡️ x${room.secureTokens}`);
        if (room.searchTokens > 0) tokens.push(`🔍 x${room.searchTokens}`);

        ctx.font = '10px sans-serif';
        ctx.fillStyle = '#94a3b8';
        ctx.fillText(tokens.join(' | '), cx, cy + 10);

        // Characters present
        if (room.characterIds.length > 0) {
          ctx.fillStyle = '#38bdf8';
          ctx.fillText(`👥 ${room.characterIds.join(', ')}`, cx, cy + 28);
        }
      } else {
        ctx.fillStyle = '#64748b';
        ctx.fillText(`[${slot.section}] ${slot.slotId}`, cx, cy);
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

  private setupEventListeners(): void {
    let isDragging = false;
    let lastX = 0;
    let lastY = 0;

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
    });

    this.canvas.addEventListener('click', (e: MouseEvent) => {
      const rect = this.canvas.getBoundingClientRect();
      const screenX = e.clientX - rect.left;
      const screenY = e.clientY - rect.top;
      const slot = this.hitTestSlot(screenX, screenY);
      if (slot) {
        this.options.onRoomClick(slot.slotId);
      }
    });
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
