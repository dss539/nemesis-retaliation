import { describe, it, expect } from 'vitest';
import { Camera2D } from '../../src/ui/canvas/camera.js';

describe('Camera2D Viewport & Coordinate Projections', () => {
  it('correctly projects screen to world and world to screen', () => {
    const cam = new Camera2D({ x: 100, y: 50, zoom: 2 });

    const world = cam.screenToWorld(200, 150);
    expect(world).toEqual({ x: 50, y: 50 });

    const screen = cam.worldToScreen(50, 50);
    expect(screen).toEqual({ x: 200, y: 150 });
  });

  it('pans smoothly by screen deltas', () => {
    const cam = new Camera2D({ x: 0, y: 0, zoom: 1 });
    cam.pan(25, -15);
    expect(cam.transform.x).toBe(25);
    expect(cam.transform.y).toBe(-15);
  });

  it('zooms anchored around a specific screen point', () => {
    const cam = new Camera2D({ x: 0, y: 0, zoom: 1 });
    const anchorX = 400;
    const anchorY = 300;

    const worldBefore = cam.screenToWorld(anchorX, anchorY);
    cam.zoomAt(anchorX, anchorY, 1.5);
    const worldAfter = cam.screenToWorld(anchorX, anchorY);

    expect(cam.transform.zoom).toBe(1.5);
    expect(worldAfter.x).toBeCloseTo(worldBefore.x);
    expect(worldAfter.y).toBeCloseTo(worldBefore.y);
  });

  it('fits world bounds inside screen dimensions', () => {
    const cam = new Camera2D();
    const bounds = { minX: 0, minY: 0, maxX: 1000, maxY: 800 };
    cam.fitToBounds(bounds, 1200, 900, 20);

    expect(cam.transform.zoom).toBeGreaterThan(0.5);
    expect(cam.transform.zoom).toBeLessThanOrEqual(cam.maxZoom);
  });
});
