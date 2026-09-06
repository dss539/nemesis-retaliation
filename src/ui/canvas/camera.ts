/**
 * 2D Camera transformation and viewport management for the Tactical Canvas.
 * Supports smooth pan, zoom around cursor, pinch-to-zoom, and screen-to-world coordinate mapping.
 */

export interface ViewportTransform {
  x: number; // Pan offset X
  y: number; // Pan offset Y
  zoom: number; // Scale factor (e.g. 0.5 to 3.0)
}

export class Camera2D {
  public transform: ViewportTransform;
  public minZoom = 0.3;
  public maxZoom = 3.5;

  constructor(initial: Partial<ViewportTransform> = {}) {
    this.transform = {
      x: initial.x ?? 0,
      y: initial.y ?? 0,
      zoom: initial.zoom ?? 1,
    };
  }

  /**
   * Translates screen pixel coordinates to world gameboard coordinates.
   */
  public screenToWorld(screenX: number, screenY: number): { x: number; y: number } {
    return {
      x: (screenX - this.transform.x) / this.transform.zoom,
      y: (screenY - this.transform.y) / this.transform.zoom,
    };
  }

  /**
   * Translates world gameboard coordinates to screen pixel coordinates.
   */
  public worldToScreen(worldX: number, worldY: number): { x: number; y: number } {
    return {
      x: worldX * this.transform.zoom + this.transform.x,
      y: worldY * this.transform.zoom + this.transform.y,
    };
  }

  /**
   * Pans the camera by screen delta.
   */
  public pan(deltaScreenX: number, deltaScreenY: number): void {
    this.transform.x += deltaScreenX;
    this.transform.y += deltaScreenY;
  }

  /**
   * Zooms in or out centered at a specific screen anchor point (e.g. mouse pointer or pinch centroid).
   */
  public zoomAt(screenAnchorX: number, screenAnchorY: number, factor: number): void {
    const worldBefore = this.screenToWorld(screenAnchorX, screenAnchorY);
    const newZoom = Math.min(this.maxZoom, Math.max(this.minZoom, this.transform.zoom * factor));
    this.transform.zoom = newZoom;

    // Adjust pan so the world point remains under the screen anchor
    this.transform.x = screenAnchorX - worldBefore.x * newZoom;
    this.transform.y = screenAnchorY - worldBefore.y * newZoom;
  }

  /**
   * Centers the camera on a specific world bounding box given screen dimensions.
   */
  public fitToBounds(
    bounds: { minX: number; minY: number; maxX: number; maxY: number },
    screenWidth: number,
    screenHeight: number,
    padding: number = 40,
  ): void {
    const worldW = bounds.maxX - bounds.minX;
    const worldH = bounds.maxY - bounds.minY;
    if (worldW <= 0 || worldH <= 0) return;

    const availableW = Math.max(100, screenWidth - padding * 2);
    const availableH = Math.max(100, screenHeight - padding * 2);

    const fitZoom = Math.min(availableW / worldW, availableH / worldH);
    this.transform.zoom = Math.min(this.maxZoom, Math.max(this.minZoom, fitZoom));

    const worldCenterX = (bounds.minX + bounds.maxX) / 2;
    const worldCenterY = (bounds.minY + bounds.maxY) / 2;

    this.transform.x = screenWidth / 2 - worldCenterX * this.transform.zoom;
    this.transform.y = screenHeight / 2 - worldCenterY * this.transform.zoom;
  }
}
