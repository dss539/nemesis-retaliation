// Nemesis: Retaliation - 2D Canvas Renderer

const Renderer = {
    canvas: null,
    ctx: null,
    state: null,
    hoveredElement: null,
    selectedRoom: null,
    clickHandler: null,
    movementTargets: [],
    movementTargetHandler: null,
    mapZoom: 1,
    MIN_MAP_ZOOM: 0.5,
    MAX_MAP_ZOOM: 3,
    MAP_ZOOM_STEP: 0.1,
    _pinchGesture: null,
    _mousePan: null,
    _mapViewInitialized: false,
    _suppressClickUntil: 0,

    // Fixed mat-derived geometry. Pointy-top hexes have vertical E/W sides,
    // matching the NE/E/SE/SW/W/NW movement topology. The 5/4/5/4/5 field
    // fills the canvas height while retaining 42px corridor gaps.
    ROOM_SIZE: 160,
    ROOM_HEIGHT: 2 * 160 / Math.sqrt(3),
    CORRIDOR_WIDTH: 42,
    ROW_STEP_Y: Math.sqrt(3) / 2 * (160 + 42),
    GRID_PADDING_X: (1200 - (5 * 160 + 4 * 42)) / 2,
    GRID_PADDING_Y: (900 - (2 * 160 / Math.sqrt(3) + 4 * (Math.sqrt(3) / 2 * (160 + 42)))) / 2,

    init(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this._mapViewInitialized = false;
        GameArt.preload(() => this.render());
        this.canvas.addEventListener('click', (e) => {
            if (Date.now() < this._suppressClickUntil) return;
            this.handleClick(e);
        });
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));

        // Touch tap detection: distinguish a tap (select target) from a pan
        // (scroll the board). The browser's synthesized click is unreliable
        // when touch-action allows panning — we detect taps manually.
        const wrapper = document.getElementById('canvas-wrapper');
        this._touchSession = null;
        this._lastTapTime = 0;
        this._lastTapPos = null;

        const onTouchStart = (e) => {
            if (e.touches.length !== 1) {
                this._touchSession = null;
                return;
            }
            const t = e.touches[0];
            this._touchSession = {
                startX: t.clientX,
                startY: t.clientY,
                startScrollX: wrapper.scrollLeft,
                startScrollY: wrapper.scrollTop,
                moved: false,
                startTime: Date.now()
            };
        };

        const onTouchMove = (e) => {
            if (!this._touchSession || e.touches.length !== 1) return;
            const t = e.touches[0];
            const dx = t.clientX - this._touchSession.startX;
            const dy = t.clientY - this._touchSession.startY;
            if (Math.hypot(dx, dy) >= 8) {
                this._touchSession.moved = true;
            }
        };

        const onTouchEnd = (e) => {
            if (!this._touchSession) return;
            const session = this._touchSession;
            this._touchSession = null;

            // If the finger moved >8px it was a pan, not a tap
            if (session.moved) return;
            // If too much time elapsed, it was a long-press, not a tap
            if (Date.now() - session.startTime > 400) return;

            // Double-tap detection (within 300ms and 40px of last tap)
            const now = Date.now();
            if (this._lastTapPos && now - this._lastTapTime < 300 &&
                Math.hypot(session.startX - this._lastTapPos.x,
                           session.startY - this._lastTapPos.y) < 40) {
                // Double tap — zoom in
                this._lastTapTime = 0;
                this._lastTapPos = null;
                this._handleDoubleTap(session.startX, session.startY);
                this._suppressClickUntil = Date.now() + 500;
                return;
            }

            // Single tap — process immediately. Double-tap zoom is handled
            // separately and cancels the single-tap effect if it fires within
            // 300ms by re-zooming (which visually overrides the selection).
            this._lastTapTime = now;
            this._lastTapPos = { x: session.startX, y: session.startY };
            this._handleTap(session.startX, session.startY);

            // Suppress the browser-synthesized click
            this._suppressClickUntil = Date.now() + 500;
        };

        this.canvas.addEventListener('touchstart', onTouchStart, { passive: true });
        this.canvas.addEventListener('touchmove', onTouchMove, { passive: true });
        this.canvas.addEventListener('touchend', onTouchEnd, { passive: true });
        this.canvas.addEventListener('touchcancel', () => { this._touchSession = null; }, { passive: true });

        wrapper?.addEventListener('wheel', (e) => {
            e.preventDefault();
            this.adjustMapZoom(e.deltaY < 0 ? this.MAP_ZOOM_STEP : -this.MAP_ZOOM_STEP);
        }, { passive: false });

        wrapper?.addEventListener('mousedown', (e) => {
            if (e.button !== 0) return;
            this._mousePan = {
                startX: e.clientX,
                startY: e.clientY,
                scrollLeft: wrapper.scrollLeft,
                scrollTop: wrapper.scrollTop,
                moved: false
            };
            wrapper.classList.add('is-mouse-panning');
            e.preventDefault();
        });

        window.addEventListener('mousemove', (e) => {
            if (!this._mousePan) return;
            const deltaX = e.clientX - this._mousePan.startX;
            const deltaY = e.clientY - this._mousePan.startY;
            if (Math.hypot(deltaX, deltaY) >= 4) this._mousePan.moved = true;
            if (!this._mousePan.moved) return;

            wrapper.scrollLeft = this._mousePan.scrollLeft - deltaX;
            wrapper.scrollTop = this._mousePan.scrollTop - deltaY;
            this._suppressClickUntil = Date.now() + 500;
            e.preventDefault();
        });

        window.addEventListener('mouseup', (e) => {
            if (e.button !== 0 || !this._mousePan) return;
            if (this._mousePan.moved) this._suppressClickUntil = Date.now() + 500;
            this._mousePan = null;
            wrapper.classList.remove('is-mouse-panning');
        });

        const touchDistance = (touches) => Math.hypot(
            touches[1].clientX - touches[0].clientX,
            touches[1].clientY - touches[0].clientY
        );
        const touchMidpoint = (touches) => ({
            x: (touches[0].clientX + touches[1].clientX) / 2,
            y: (touches[0].clientY + touches[1].clientY) / 2
        });

        wrapper?.addEventListener('touchstart', (e) => {
            if (e.touches.length !== 2) return;
            // Cancel any pending touch session when pinch starts
            this._touchSession = null;
            const midpoint = touchMidpoint(e.touches);
            const canvasRect = this.canvas.getBoundingClientRect();
            const distance = touchDistance(e.touches);
            if (!distance || !canvasRect.width || !canvasRect.height) return;

            this._pinchGesture = {
                startDistance: distance,
                startZoom: this.mapZoom,
                canvasX: Math.max(0, Math.min(1, (midpoint.x - canvasRect.left) / canvasRect.width)),
                canvasY: Math.max(0, Math.min(1, (midpoint.y - canvasRect.top) / canvasRect.height))
            };
            this._suppressClickUntil = Date.now() + 500;
            e.preventDefault();
        }, { passive: false });

        wrapper?.addEventListener('touchmove', (e) => {
            if (!this._pinchGesture || e.touches.length !== 2) return;
            const midpoint = touchMidpoint(e.touches);
            const wrapperRect = wrapper.getBoundingClientRect();
            const scale = touchDistance(e.touches) / this._pinchGesture.startDistance;

            this.setMapZoomAt(this._pinchGesture.startZoom * scale, {
                canvasX: this._pinchGesture.canvasX,
                canvasY: this._pinchGesture.canvasY,
                localX: midpoint.x - wrapperRect.left,
                localY: midpoint.y - wrapperRect.top
            });
            this._suppressClickUntil = Date.now() + 500;
            e.preventDefault();
        }, { passive: false });

        const finishPinch = (e) => {
            if (!this._pinchGesture || e.touches.length >= 2) return;
            this._pinchGesture = null;
            this._suppressClickUntil = Date.now() + 500;
            e.preventDefault();
        };
        wrapper?.addEventListener('touchend', finishPinch, { passive: false });
        wrapper?.addEventListener('touchcancel', finishPinch, { passive: false });

        // Responsive resize
        window.addEventListener('resize', () => this.resizeCanvas());
        window.addEventListener('orientationchange', () => setTimeout(() => this.resizeCanvas(), 200));
    },

    // Handle a single tap on the canvas at screen coordinates (clientX, clientY)
    _handleTap(clientX, clientY) {
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = (this._baseW || 1200) / rect.width;
        const scaleY = (this._baseH || 900) / rect.height;
        const x = (clientX - rect.left) * scaleX;
        const y = (clientY - rect.top) * scaleY;

        // Check movement targets first (same as handleClick)
        const movementTarget = this.getMovementTargetAtPoint(x, y);
        if (movementTarget && this.movementTargetHandler) {
            this.movementTargetHandler(movementTarget);
            return;
        }

        // Room selection
        const room = this.getRoomAtPoint(x, y);
        if (room) {
            if (this.clickHandler) this.clickHandler({ type: 'room', room: room.id, x, y });
            this.selectedRoom = room.id;
        }
        this.render();
    },

    // Handle double-tap: zoom in centered on tap location
    _handleDoubleTap(clientX, clientY) {
        const wrapper = document.getElementById('canvas-wrapper');
        if (!wrapper || !this.canvas) return;

        // Cycle zoom: if at or below 1x, go to 2x; if above 1x, go to 1x
        const targetZoom = this.mapZoom <= 1.0 ? 2.0 : 1.0;
        const rect = this.canvas.getBoundingClientRect();
        const canvasX = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
        const canvasY = Math.max(0, Math.min(1, (clientY - rect.top) / rect.height));
        const wrapperRect = wrapper.getBoundingClientRect();

        this.setMapZoomAt(targetZoom, {
            canvasX,
            canvasY,
            localX: clientX - wrapperRect.left,
            localY: clientY - wrapperRect.top
        });
    },

    resizeCanvas() {
        if (!this.canvas) return;
        const wrapper = document.getElementById('canvas-wrapper');
        if (!wrapper) return;

        const wrapperWidth = wrapper.clientWidth;
        const wrapperHeight = wrapper.clientHeight;

        // Base virtual size — the coordinate system the game uses
        const BASE_W = 1200;
        const BASE_H = 900;
        const aspectRatio = BASE_W / BASE_H;

        let fitWidth = wrapperWidth;
        let fitHeight = fitWidth / aspectRatio;

        if (fitHeight > wrapperHeight) {
            fitHeight = wrapperHeight;
            fitWidth = fitHeight * aspectRatio;
        }

        const displayWidth = Math.max(1, fitWidth * this.mapZoom);
        const displayHeight = Math.max(1, fitHeight * this.mapZoom);

        // Map zoom changes CSS size, making the wrapper a native pan surface.
        this.canvas.style.width = Math.floor(displayWidth) + 'px';
        this.canvas.style.height = Math.floor(displayHeight) + 'px';

        // Give the camera room to travel beyond every board edge while keeping
        // a recovery strip visible at the most distant legal scroll position.
        const panSurface = document.getElementById('map-pan-surface');
        if (panSurface) {
            const recoveryX = Math.min(96, Math.max(56, wrapperWidth * 0.18));
            const recoveryY = Math.min(96, Math.max(56, wrapperHeight * 0.18));
            const gutterX = Math.max(0, wrapperWidth - recoveryX);
            const gutterY = Math.max(0, wrapperHeight - recoveryY);
            this.canvas.style.left = Math.floor(gutterX) + 'px';
            this.canvas.style.top = Math.floor(gutterY) + 'px';
            panSurface.style.width = Math.ceil(displayWidth + gutterX * 2) + 'px';
            panSurface.style.height = Math.ceil(displayHeight + gutterY * 2) + 'px';
        }

        // Render sharply without allowing large desktop zooms to allocate an
        // unbounded bitmap.
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        const resolutionScale = Math.min(dpr, 4096 / displayWidth, 4096 / displayHeight);
        this.canvas.width = Math.max(1, Math.floor(displayWidth * resolutionScale));
        this.canvas.height = Math.max(1, Math.floor(displayHeight * resolutionScale));

        // Scale the drawing context so game coordinates map correctly.
        const scaleX = this.canvas.width / BASE_W;
        const scaleY = this.canvas.height / BASE_H;
        this.ctx.setTransform(scaleX, 0, 0, scaleY, 0, 0);

        // Store for click coordinate mapping.
        this._displayWidth = displayWidth;
        this._displayHeight = displayHeight;
        this._baseW = BASE_W;
        this._baseH = BASE_H;

        this.updateMapZoomControls();
        this.render();
        if (!this._mapViewInitialized) {
            this.centerMap();
            this._mapViewInitialized = true;
        }
    },

    centerMap() {
        const wrapper = document.getElementById('canvas-wrapper');
        if (!wrapper || !this.canvas) return;
        const center = () => {
            wrapper.scrollLeft = this.canvas.offsetLeft
                + this.canvas.offsetWidth / 2 - wrapper.clientWidth / 2;
            wrapper.scrollTop = this.canvas.offsetTop
                + this.canvas.offsetHeight / 2 - wrapper.clientHeight / 2;
        };
        center();
        // The initial flex layout can finalize after the canvas is resized.
        // Repeat on the next frame so Fit cannot strand the board in a gutter.
        requestAnimationFrame(center);
    },

    adjustMapZoom(delta) {
        this.setMapZoom(this.mapZoom + delta);
    },

    normalizeMapZoom(nextZoom) {
        const stepped = Math.round(nextZoom / this.MAP_ZOOM_STEP) * this.MAP_ZOOM_STEP;
        const clamped = Math.max(this.MIN_MAP_ZOOM, Math.min(this.MAX_MAP_ZOOM, stepped));
        return Number(clamped.toFixed(2));
    },

    setMapZoom(nextZoom) {
        const wrapper = document.getElementById('canvas-wrapper');
        if (!wrapper || !this.canvas) return;

        const oldScrollWidth = Math.max(wrapper.scrollWidth, 1);
        const oldScrollHeight = Math.max(wrapper.scrollHeight, 1);
        const centerX = (wrapper.scrollLeft + wrapper.clientWidth / 2) / oldScrollWidth;
        const centerY = (wrapper.scrollTop + wrapper.clientHeight / 2) / oldScrollHeight;

        this.mapZoom = this.normalizeMapZoom(nextZoom);
        this.resizeCanvas();

        wrapper.scrollLeft = centerX * wrapper.scrollWidth - wrapper.clientWidth / 2;
        wrapper.scrollTop = centerY * wrapper.scrollHeight - wrapper.clientHeight / 2;
        this.updateMapZoomControls();
    },

    setMapZoomAt(nextZoom, anchor) {
        const wrapper = document.getElementById('canvas-wrapper');
        if (!wrapper || !this.canvas) return;

        // Pinch zoom follows finger distance continuously; discrete controls
        // use setMapZoom(), which snaps to MAP_ZOOM_STEP.
        this.mapZoom = Math.max(this.MIN_MAP_ZOOM, Math.min(this.MAX_MAP_ZOOM, nextZoom));
        this.resizeCanvas();

        wrapper.scrollLeft = this.canvas.offsetLeft
            + anchor.canvasX * this.canvas.offsetWidth - anchor.localX;
        wrapper.scrollTop = this.canvas.offsetTop
            + anchor.canvasY * this.canvas.offsetHeight - anchor.localY;
        this.updateMapZoomControls();
    },

    resetMapView() {
        this.mapZoom = 1;
        this.resizeCanvas();
        this.centerMap();
        this.updateMapZoomControls();
    },

    updateMapZoomControls() {
        const level = document.getElementById('map-zoom-level');
        const zoomIn = document.querySelector('[data-map-zoom="in"]');
        const zoomOut = document.querySelector('[data-map-zoom="out"]');
        if (level) level.textContent = Math.round(this.mapZoom * 100) + '%';
        if (zoomIn) zoomIn.disabled = this.mapZoom >= this.MAX_MAP_ZOOM;
        if (zoomOut) zoomOut.disabled = this.mapZoom <= this.MIN_MAP_ZOOM;
    },

    setState(state) {
        this.state = state;
        this.render();
    },

    render() {
        if (!this.ctx || !this.state) return;
        const ctx = this.ctx;
        // Clear in base coordinate space
        ctx.clearRect(0, 0, this._baseW || 1200, this._baseH || 900);

        // Original generated facility surface. A flat fill remains as a robust
        // fallback while SVG assets load or if an asset request fails.
        const boardArt = GameArt.get('board');
        ctx.fillStyle = '#0d1117';
        ctx.fillRect(0, 0, this._baseW || 1200, this._baseH || 900);
        if (boardArt) ctx.drawImage(boardArt, 0, 0, this._baseW || 1200, this._baseH || 900);

        // Draw a low-contrast tactical floor plan beneath placed tiles.
        this.drawSections(ctx);
        this.drawGrid(ctx);

        // Corridor tiles sit in the reserved gaps and never pass through rooms.
        this.state.corridors.forEach(corridor => {
            this.drawCorridor(ctx, corridor);
        });

        // Draw rooms above corridor thresholds.
        Object.values(this.state.rooms).forEach(room => {
            this.drawRoom(ctx, room);
        });

        // Draw legal tactical destinations last so they read like XCOM targets.
        this.drawMovementTargets(ctx);

        // Draw intruders
        this.state.intruders.forEach(intruder => {
            this.drawIntruder(ctx, intruder);
        });

        // Draw characters
        this.state.players.forEach(player => {
            if (player.alive) {
                this.drawCharacter(ctx, player);
            }
        });

        // Draw robot
        if (this.state.robot.revealed) {
            this.drawRobot(ctx);
        }

        // Draw round track
        this.drawRoundTrack(ctx);

        // Draw objective panel
        this.drawObjective(ctx);
    },

    drawSections(ctx) {
        const baseH = this._baseH || 900;
        const step = this.ROOM_SIZE + this.CORRIDOR_WIDTH;
        const sections = [
            { name: 'SECTION A', start: 0, columns: 2, color: 'rgba(45,116,93,0.055)' },
            { name: 'SECTION B', start: 2, columns: 2, color: 'rgba(65,98,145,0.055)' },
            { name: 'SECTION C', start: 4, columns: 1, color: 'rgba(143,67,67,0.065)' }
        ];

        sections.forEach(section => {
            const x = this.GRID_PADDING_X + section.start * step - this.CORRIDOR_WIDTH / 2;
            const width = section.columns * step;
            ctx.fillStyle = section.color;
            ctx.fillRect(x, 42, width, baseH - 105);
            ctx.fillStyle = 'rgba(154,184,202,0.32)';
            ctx.font = '600 13px sans-serif';
            ctx.textAlign = 'left';
            ctx.fillText(section.name, x + 10, 58);
        });
    },

    drawGrid(ctx) {
        ctx.save();
        GAME_DATA.CONFIG.boardSlots.forEach(slot => {
                const geometry = this.roomGeometry(slot);
                const { x, y } = geometry;

                // Every Room slot is visible before exploration. The room itself
                // later replaces this subdued empty-slot floor without moving it.
                this.hexagonPath(ctx, x, y, this.ROOM_SIZE);
                ctx.fillStyle = 'rgba(12,25,33,0.68)';
                ctx.fill();
                ctx.strokeStyle = 'rgba(105,150,166,0.36)';
                ctx.lineWidth = 2;
                ctx.setLineDash([6, 6]);
                ctx.stroke();

                this.hexagonPath(ctx, x + 6, y + 6, this.ROOM_SIZE - 12);
                ctx.strokeStyle = 'rgba(74,108,121,0.17)';
                ctx.lineWidth = 1;
                ctx.setLineDash([]);
                ctx.stroke();
        });
        ctx.restore();
    },

    roomGeometry(roomOrPosition) {
        const position = roomOrPosition?.position || roomOrPosition;
        if (!position) return null;
        const stepX = this.ROOM_SIZE + this.CORRIDOR_WIDTH;
        const stepY = this.ROW_STEP_Y;
        const rowOffsetX = Math.abs(position.y) % 2 === 1 ? stepX / 2 : 0;
        return {
            x: this.GRID_PADDING_X + position.x * stepX + rowOffsetX,
            y: this.GRID_PADDING_Y + position.y * stepY,
            w: this.ROOM_SIZE,
            h: this.ROOM_HEIGHT,
            cx: this.GRID_PADDING_X + position.x * stepX + rowOffsetX + this.ROOM_SIZE / 2,
            cy: this.GRID_PADDING_Y + position.y * stepY + this.ROOM_HEIGHT / 2
        };
    },

    hexagonVertices(x, y, width, height = 2 * width / Math.sqrt(3)) {
        return [
            { x: x + width / 2, y },
            { x: x + width, y: y + height / 4 },
            { x: x + width, y: y + height * 3 / 4 },
            { x: x + width / 2, y: y + height },
            { x, y: y + height * 3 / 4 },
            { x, y: y + height / 4 }
        ];
    },

    hexagonPath(ctx, x, y, width, height = 2 * width / Math.sqrt(3)) {
        const vertices = this.hexagonVertices(x, y, width, height);
        ctx.beginPath();
        ctx.moveTo(vertices[0].x, vertices[0].y);
        vertices.slice(1).forEach(vertex => ctx.lineTo(vertex.x, vertex.y));
        ctx.closePath();
    },

    hexBoundaryDistance(geometry, ux, uy) {
        const center = { x: geometry.cx, y: geometry.cy };
        const vertices = this.hexagonVertices(geometry.x, geometry.y, geometry.w, geometry.h);
        let nearest = Infinity;
        const cross = (ax, ay, bx, by) => ax * by - ay * bx;
        for (let index = 0; index < vertices.length; index++) {
            const start = vertices[index];
            const end = vertices[(index + 1) % vertices.length];
            const edgeX = end.x - start.x;
            const edgeY = end.y - start.y;
            const fromCenterX = start.x - center.x;
            const fromCenterY = start.y - center.y;
            const denominator = cross(ux, uy, edgeX, edgeY);
            if (Math.abs(denominator) < 1e-8) continue;
            const distance = cross(fromCenterX, fromCenterY, edgeX, edgeY) / denominator;
            const alongEdge = cross(fromCenterX, fromCenterY, ux, uy) / denominator;
            if (distance >= 0 && alongEdge >= 0 && alongEdge <= 1) nearest = Math.min(nearest, distance);
        }
        return Number.isFinite(nearest) ? nearest : 0;
    },

    drawRoom(ctx, room) {
        if (!room.position) return;
        const geometry = this.roomGeometry(room);
        const { x, y, w, h } = geometry;

        const roomData = GAME_DATA.ROOMS[room.id];
        if (!roomData) return;

        // Section-tinted tactical flooring.
        let bgColor = '#17242a';
        let edgeColor = '#4b6a73';
        if (room.section === 'A') { bgColor = '#172a27'; edgeColor = '#3f7568'; }
        if (room.section === 'B') { bgColor = '#182530'; edgeColor = '#426b88'; }
        if (room.section === 'C') { bgColor = '#2b1d22'; edgeColor = '#86505c'; }

        const isCurrentRoom = this.state.players.some((player, index) =>
            index === this.state.currentPlayer && player.alive && player.location === room.id
        );
        if (this.selectedRoom === room.id) edgeColor = '#f36b5e';
        if (isCurrentRoom) edgeColor = '#64d8e8';

        // Heavy outer wall, inner bevel, then a faint floor grid.
        ctx.save();
        this.hexagonPath(ctx, x, y, w, h);
        ctx.fillStyle = '#080d12';
        ctx.fill();
        ctx.strokeStyle = edgeColor;
        ctx.lineWidth = isCurrentRoom ? 4 : 3;
        ctx.stroke();

        this.hexagonPath(ctx, x + 5, y + 5, w - 10, h - 10);
        ctx.fillStyle = bgColor;
        ctx.fill();
        ctx.strokeStyle = 'rgba(185,216,224,0.18)';
        ctx.lineWidth = 1;
        ctx.stroke();
        ctx.clip();
        const roomArt = GameArt.get('room:' + room.id);
        if (roomArt) {
            ctx.globalAlpha = 0.68;
            ctx.drawImage(roomArt, x + 4, y + 4, w - 8, h - 8);
            ctx.globalAlpha = 1;
        } else {
            ctx.strokeStyle = 'rgba(135,174,185,0.07)';
            for (let line = 18; line < w; line += 18) {
                ctx.beginPath();
                ctx.moveTo(x + line, y + 5);
                ctx.lineTo(x + line, y + h - 5);
                ctx.stroke();
                ctx.beginPath();
                ctx.moveTo(x + 5, y + line);
                ctx.lineTo(x + w - 5, y + line);
                ctx.stroke();
            }
        }
        ctx.restore();

        // Fire marker — icon + label
        if (room.markers?.fire) {
            ctx.fillStyle = 'rgba(255,80,0,0.28)';
            this.hexagonPath(ctx, x + 3, y + 3, w - 6, h - 6);
            ctx.fill();
            GameArt.drawCanvasIcon(ctx, 'fire', x + 15, y + 15, 18, '#ff7a3d');
            ctx.fillStyle = '#ff9a62';
            ctx.font = 'bold 11px sans-serif';
            ctx.textAlign = 'left';
            ctx.fillText('FIRE', x + 27, y + 19);
        }

        // Malfunction marker — icon + label
        if (room.markers?.malfunction) {
            GameArt.drawCanvasIcon(ctx, 'malfunction', x + w - 16, y + 15, 18, '#f0b94e');
            ctx.fillStyle = '#f0c66d';
            ctx.font = 'bold 10px sans-serif';
            ctx.textAlign = 'right';
            ctx.fillText('MALT', x + w - 27, y + 19);
        }

        // Secure tokens — show count as text
        if (room.markers?.secure?.length > 0) {
            GameArt.drawCanvasIcon(ctx, 'secure', x + 15, y + h - 15, 17, '#5fa6dc');
            ctx.fillStyle = '#8ac5ed';
            ctx.font = 'bold 12px sans-serif';
            ctx.textAlign = 'left';
            ctx.fillText('x' + room.markers.secure.length, x + 27, y + h - 11);
        }

        // Room name
        ctx.fillStyle = '#e0e6ed';
        ctx.font = 'bold 14px sans-serif';
        ctx.textAlign = 'center';
        const name = roomData.name || room.id;
        ctx.fillText(this.truncate(name, 14), x + w/2, y + h/2 - 8);

        // Room type badge
        if (roomData.type && roomData.type !== '?') {
            ctx.fillStyle = '#ff4444';
            ctx.font = 'bold 12px sans-serif';
            ctx.fillText('[' + roomData.type + ']', x + w/2, y + h/2 + 12);
        }

        // Item icons
        if (roomData.itemIcons) {
            const colors = { red: '#e44', yellow: '#da3', green: '#4a9', blue: '#49c' };
            roomData.itemIcons.forEach((type, i) => {
                ctx.fillStyle = colors[type] || '#888';
                ctx.beginPath();
                ctx.arc(x + 12 + i * 14, y + 12, 6, 0, Math.PI * 2);
                ctx.fill();
            });
        }

        // Computer icon
        if (roomData.computer) {
            GameArt.drawCanvasIcon(ctx, 'computer', x + w - 15, y + h - 15, 18, '#65b8df');
        }

        // Intruder count — text label with type breakdown
        const intrudersInRoom = this.state.intruders.filter(i => i.location.type === 'room' && i.location.id === room.id);
        if (intrudersInRoom.length > 0) {
            ctx.fillStyle = 'rgba(255,50,50,0.14)';
            this.hexagonPath(ctx, x + 3, y + 3, w - 6, h - 6);
            ctx.fill();
            // Label with intruder types
            const typeCounts = {};
            intrudersInRoom.forEach(i => { typeCounts[i.type] = (typeCounts[i.type] || 0) + 1; });
            const label = Object.entries(typeCounts).map(([t, c]) => c > 1 ? c + 'x' + t : t).join(' ');
            ctx.fillStyle = '#ff4444';
            ctx.font = 'bold 11px sans-serif';
            ctx.textAlign = 'right';
            ctx.fillText(label, x + w - 6, y + h - 8);
        }

    },

    corridorGeometry(corridor) {
        const room1 = this.state.rooms[corridor.room1];
        const room2 = this.state.rooms[corridor.room2];
        if (!room1?.position || !room2?.position) return null;
        const g1 = this.roomGeometry(room1);
        const g2 = this.roomGeometry(room2);
        const deltaX = g2.cx - g1.cx;
        const deltaY = g2.cy - g1.cy;
        const length = Math.hypot(deltaX, deltaY) || 1;
        const ux = deltaX / length;
        const uy = deltaY / length;
        const room1Boundary = this.hexBoundaryDistance(g1, ux, uy);
        const room2Boundary = this.hexBoundaryDistance(g2, -ux, -uy);
        const x1 = g1.cx + ux * room1Boundary;
        const y1 = g1.cy + uy * room1Boundary;
        const x2 = g2.cx - ux * room2Boundary;
        const y2 = g2.cy - uy * room2Boundary;
        return { x1, y1, x2, y2, mx:(x1+x2)/2, my:(y1+y2)/2, ux, uy, px:-uy, py:ux };
    },

    drawCorridor(ctx, corridor) {
        const geometry = this.corridorGeometry(corridor);
        if (!geometry) return;
        const { x1, y1, x2, y2, mx, my, px, py } = geometry;

        // A proper corridor floor tile occupies only the reserved gap.
        ctx.save();
        ctx.lineCap = 'butt';
        ctx.strokeStyle = corridor.reinforced ? '#315b58' : '#0a1117';
        ctx.lineWidth = 36;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();

        ctx.strokeStyle = corridor.reinforced ? '#3d7770' : '#253943';
        ctx.lineWidth = 28;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();

        ctx.strokeStyle = corridor.reinforced ? 'rgba(117,220,199,0.55)' : 'rgba(130,170,184,0.32)';
        ctx.lineWidth = 1;
        ctx.setLineDash([7, 5]);
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.restore();

        // Noise marker — yellow circle with "!" and label
        if (corridor.noise) {
            ctx.fillStyle = '#ffcc00';
            ctx.beginPath();
            ctx.arc(mx, my, 10, 0, Math.PI * 2);
            ctx.fill();
            GameArt.drawCanvasIcon(ctx, 'noise', mx, my, 15, '#111820');
            // Label below
            ctx.fillStyle = '#ffcc00';
            ctx.font = 'bold 10px sans-serif';
            ctx.fillText('NOISE', mx, my - 14);
        }

        // Door bulkhead spans the corridor perpendicular to travel.
        if (corridor.door === 'closed') {
            ctx.strokeStyle = '#dc5a54';
            ctx.lineWidth = 7;
            ctx.beginPath();
            ctx.moveTo(mx - px * 15, my - py * 15);
            ctx.lineTo(mx + px * 15, my + py * 15);
            ctx.stroke();
        } else if (corridor.door === 'destroyed') {
            ctx.strokeStyle = '#778088';
            ctx.lineWidth = 3;
            ctx.setLineDash([4, 4]);
            ctx.beginPath();
            ctx.moveTo(mx - px * 15, my - py * 15);
            ctx.lineTo(mx + px * 15, my + py * 15);
            ctx.stroke();
            ctx.setLineDash([]);
        }

        // Value label
        ctx.fillStyle = '#a9bec7';
        ctx.font = 'bold 11px sans-serif';
        ctx.textAlign = 'center';
        if (!corridor.reinforced) {
            ctx.fillText(corridor.value || '?', mx, my - 9);
        }

    },

    drawMovementTargets(ctx) {
        if (!this.movementTargets.length) return;
        this.movementTargets.forEach(target => {
            const geometry = target.kind === 'room'
                ? this.roomGeometry(this.state.rooms[target.roomId])
                : this.roomGeometry(target.position);
            if (!geometry) return;
            const color = target.kind === 'room' ? '#78e6a2' : '#66d9ef';

            ctx.save();
            this.hexagonPath(ctx, geometry.x - 4, geometry.y - 4, geometry.w + 8, geometry.h + 8);
            ctx.fillStyle = target.kind === 'room' ? 'rgba(72,210,126,0.10)' : 'rgba(70,194,224,0.13)';
            ctx.fill();
            ctx.strokeStyle = color;
            ctx.lineWidth = 4;
            ctx.setLineDash(target.kind === 'explore' ? [9, 5] : []);
            ctx.stroke();
            ctx.setLineDash([]);

            const label = target.kind === 'room' ? 'MOVE' : 'EXPLORE';
            ctx.font = 'bold 11px sans-serif';
            const labelWidth = ctx.measureText(label).width + 18;
            const labelX = geometry.cx - labelWidth / 2;
            const labelY = geometry.y + geometry.h - 25;
            ctx.fillStyle = '#071014';
            ctx.fillRect(labelX, labelY, labelWidth, 20);
            ctx.strokeStyle = color;
            ctx.lineWidth = 1;
            ctx.strokeRect(labelX, labelY, labelWidth, 20);
            ctx.fillStyle = color;
            ctx.textAlign = 'center';
            ctx.fillText(label, geometry.cx, labelY + 14);
            ctx.restore();
        });
    },

    setMovementTargets(targets, handler) {
        this.movementTargets = targets || [];
        this.movementTargetHandler = handler || null;
        this.render();
    },

    clearMovementTargets() {
        this.movementTargets = [];
        this.movementTargetHandler = null;
        this.render();
    },

    getMovementTargetAtPoint(x, y) {
        for (const target of this.movementTargets) {
            const geometry = target.kind === 'room'
                ? this.roomGeometry(this.state.rooms[target.roomId])
                : this.roomGeometry(target.position);
            if (geometry && this.pointInHexagon(x, y, geometry)) return target;
        }
        return null;
    },

    pointInHexagon(x, y, geometry) {
        const vertices = this.hexagonVertices(geometry.x, geometry.y, geometry.w, geometry.h);
        let inside = false;
        for (let index = 0, previous = vertices.length - 1; index < vertices.length; previous = index++) {
            const current = vertices[index];
            const prior = vertices[previous];
            if ((current.y > y) !== (prior.y > y) &&
                x < (prior.x - current.x) * (y - current.y) / (prior.y - current.y) + current.x) inside = !inside;
        }
        return inside;
    },

    drawIntruder(ctx, intruder) {
        let cx, cy;
        const sameLocation = this.state.intruders.filter(candidate =>
            candidate.location?.type === intruder.location?.type && candidate.location?.id === intruder.location?.id
        );
        const index = Math.max(0, sameLocation.findIndex(candidate => candidate.id === intruder.id));
        if (intruder.location?.type === 'room') {
            const room = this.state.rooms[intruder.location.id];
            const geometry = this.roomGeometry(room);
            if (!geometry) return;
            cx = geometry.x + geometry.w - 21 - (index % 3) * 23;
            cy = geometry.y + 23 + Math.floor(index / 3) * 23;
        } else if (intruder.location?.type === 'corridor') {
            const corridor = this.state.corridors.find(candidate => candidate.id === intruder.location.id);
            const geometry = corridor && this.corridorGeometry(corridor);
            if (!geometry) return;
            cx = geometry.mx + geometry.px * (16 + Math.floor(index / 3) * 15) + geometry.ux * ((index % 3) - 1) * 16;
            cy = geometry.my + geometry.py * (16 + Math.floor(index / 3) * 15) + geometry.uy * ((index % 3) - 1) * 16;
        } else return;
        const radius = intruder.type === 'queen' ? 23 : intruder.type === 'drone' ? 17 : 15;
        this.drawAssetToken(ctx, GameArt.get('intruder:' + intruder.type), cx, cy, radius,
            GameArt.intruderColors[intruder.type] || '#d65a61', (intruder.type || '?').charAt(0).toUpperCase());
    },

    drawCharacter(ctx, player) {
        const room = this.state.rooms[player.location];
        const geometry = this.roomGeometry(room);
        if (!geometry) return;
        const players = this.state.players.filter(candidate => candidate.alive && candidate.location === player.location);
        const index = Math.max(0, players.findIndex(candidate => candidate.id === player.id));
        const cx = geometry.x + 20 + (index % 4) * 23;
        const cy = geometry.y + geometry.h - 21 - Math.floor(index / 4) * 23;
        const ring = GameArt.playerColors[player.color] || GameArt.characterColors[player.character] || '#dbe9ec';
        const charData = GAME_DATA.CHARACTERS[player.character];
        this.drawAssetToken(ctx, GameArt.get('character:' + player.character), cx, cy, 18, ring,
            (charData?.name || player.character || '?').charAt(0).toUpperCase(), player.id === this.state.currentPlayer);
    },

    drawAssetToken(ctx, image, cx, cy, radius, ringColor, label, active = false) {
        ctx.save();
        if (active) {
            ctx.shadowColor = ringColor;
            ctx.shadowBlur = 12;
        }
        ctx.fillStyle = '#071015';
        ctx.beginPath();
        ctx.arc(cx, cy, radius + 2, 0, Math.PI * 2);
        ctx.fill();
        if (image) {
            ctx.drawImage(image, cx - radius, cy - radius, radius * 2, radius * 2);
        } else {
            ctx.fillStyle = ringColor;
            ctx.beginPath();
            ctx.arc(cx, cy, radius - 2, 0, Math.PI * 2);
            ctx.fill();
        }
        ctx.shadowBlur = 0;
        ctx.strokeStyle = ringColor;
        ctx.lineWidth = active ? 4 : 2;
        ctx.beginPath();
        ctx.arc(cx, cy, radius + 1, 0, Math.PI * 2);
        ctx.stroke();
        ctx.fillStyle = '#061014';
        ctx.beginPath();
        ctx.arc(cx + radius * 0.72, cy + radius * 0.72, 7, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = ringColor;
        ctx.lineWidth = 1;
        ctx.stroke();
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 8px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(label || '?', cx + radius * 0.72, cy + radius * 0.72 + 3);
        ctx.restore();
    },

    drawRobot(ctx) {
        const robotRoom = this.state.rooms[this.state.robot.location];
        if (!robotRoom?.position) return;
        const geometry = this.roomGeometry(robotRoom);
        const x = geometry.x + geometry.w - 24;
        const y = geometry.y + geometry.h - 24;

        ctx.fillStyle = '#071015';
        ctx.beginPath();
        ctx.arc(x + 7, y + 7, 11, 0, Math.PI * 2);
        ctx.fill();
        GameArt.drawCanvasIcon(ctx, 'robot', x + 7, y + 7, 18, '#88ccff');
    },

    drawRoundTrack(ctx) {
        // Draw at bottom of canvas in base coordinate space
        const baseH = this._baseH || 900;
        const y = baseH - 35;
        const startX = 30;
        const spacing = 44;

        ctx.fillStyle = '#1a2030';
        ctx.fillRect(15, y - 8, 14 * spacing + 15, 28);
        ctx.strokeStyle = '#3a4550';
        ctx.lineWidth = 1;
        ctx.strokeRect(15, y - 8, 14 * spacing + 15, 28);

        for (let i = 1; i <= 14; i++) {
            const x = startX + (i - 1) * spacing + 7;

            // Round marker
            if (i === this.state.round) {
                ctx.fillStyle = '#ff4444';
                ctx.beginPath();
                ctx.arc(x, y + 7, 11, 0, Math.PI * 2);
                ctx.fill();
            }

            // Autodestruction token
            if (this.state.autodestruction.active && i === this.state.autodestruction.token) {
                ctx.fillStyle = '#ff8800';
                ctx.beginPath();
                ctx.arc(x, y + 7, 8, 0, Math.PI * 2);
                ctx.fill();
            }

            // Lander token
            if (i === this.state.landerRound) {
                ctx.fillStyle = '#44cc44';
                ctx.beginPath();
                ctx.arc(x, y + 7, 7, 0, Math.PI * 2);
                ctx.fill();
            }

            // Round number
            ctx.fillStyle = '#666';
            ctx.font = '11px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(i, x, y + 25);
        }
    },

    drawObjective(ctx) {
        const baseH = this._baseH || 900;
        const panelX = 15;
        const panelY = baseH - 120;
        const panelW = 280;
        const panelH = 95;

        // Dark background panel with border (consistent with drawRoundTrack styling)
        ctx.fillStyle = '#1a2030';
        ctx.fillRect(panelX, panelY, panelW, panelH);
        ctx.strokeStyle = '#3a4550';
        ctx.lineWidth = 1;
        ctx.strokeRect(panelX, panelY, panelW, panelH);

        const task = this.state.missionTask;
        if (!task) return;

        // Mission task name in accent color
        ctx.fillStyle = '#c56069';
        ctx.font = '700 13px sans-serif';
        ctx.textAlign = 'left';
        ctx.fillText(task.name, panelX + 10, panelY + 20);

        // Mission task text in secondary text color (truncated)
        ctx.fillStyle = '#8899aa';
        ctx.font = '11px sans-serif';
        const maxTextWidth = panelW - 20;
        let text = task.text || '';
        if (ctx.measureText(text).width > maxTextWidth) {
            while (text.length > 0 && ctx.measureText(text + '…').width > maxTextWidth) {
                text = text.slice(0, -1);
            }
            text += '…';
        }
        // Wrap text across up to 3 lines
        const words = text.split(' ');
        const lines = [];
        let line = '';
        for (const word of words) {
            const test = line ? line + ' ' + word : word;
            if (ctx.measureText(test).width > maxTextWidth && line) {
                lines.push(line);
                line = word;
            } else {
                line = test;
            }
        }
        if (line) lines.push(line);
        const maxLines = 3;
        const displayLines = lines.length > maxLines ? lines.slice(0, maxLines) : lines;
        displayLines.forEach((l, i) => {
            ctx.fillText(l, panelX + 10, panelY + 38 + i * 14);
        });

        // Objective Discard Track
        const trackY = panelY + panelH - 18;
        ctx.fillStyle = '#667788';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'left';
        ctx.fillText('Discard Track: ' + (this.state.objectiveChoiceTrack || 0), panelX + 10, trackY);

        // Visual row of small circles
        const trackVal = this.state.objectiveChoiceTrack || 0;
        const pipStartX = panelX + 120;
        const pipSpacing = 14;
        const maxPips = 10;
        for (let i = 0; i < maxPips; i++) {
            const px = pipStartX + i * pipSpacing;
            const py = trackY - 4;
            ctx.beginPath();
            ctx.arc(px, py, 4, 0, Math.PI * 2);
            if (i < trackVal) {
                ctx.fillStyle = '#c56069';
                ctx.fill();
            } else {
                ctx.fillStyle = '#1a2030';
                ctx.fill();
                ctx.strokeStyle = '#445566';
                ctx.lineWidth = 1;
                ctx.stroke();
            }
        }
    },

    // === INTERACTION ===
    handleClick(e) {
        const rect = this.canvas.getBoundingClientRect();
        // Map screen coordinates to base coordinate space
        const scaleX = (this._baseW || 1200) / rect.width;
        const scaleY = (this._baseH || 900) / rect.height;
        const x = (e.clientX - rect.left) * scaleX;
        const y = (e.clientY - rect.top) * scaleY;

        // Tactical actions consume only highlighted legal targets.
        const movementTarget = this.getMovementTargetAtPoint(x, y);
        if (movementTarget && this.movementTargetHandler) {
            this.movementTargetHandler(movementTarget);
            return;
        }

        // Find clicked room
        const room = this.getRoomAtPoint(x, y);
        if (room) {
            if (this.clickHandler) this.clickHandler({ type: 'room', room: room.id, x, y });
            this.selectedRoom = room.id;
        } else {
            // Check corridors
            const corridor = this.getCorridorAtPoint(x, y);
            if (corridor && this.clickHandler) {
                this.clickHandler({ type: 'corridor', corridor: corridor.id, x, y });
            }
            this.selectedRoom = null;
        }
        this.render();
    },

    handleMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = (this._baseW || 1200) / rect.width;
        const scaleY = (this._baseH || 900) / rect.height;
        const x = (e.clientX - rect.left) * scaleX;
        const y = (e.clientY - rect.top) * scaleY;
        const movementTarget = this.getMovementTargetAtPoint(x, y);
        const room = this.getRoomAtPoint(x, y);

        if (movementTarget || room) {
            this.canvas.style.cursor = 'pointer';
        } else {
            this.canvas.style.cursor = 'default';
        }
    },

    getRoomAtPoint(x, y) {
        if (!this.state) return null;
        for (const room of Object.values(this.state.rooms)) {
            if (!room.position) continue;
            const geometry = this.roomGeometry(room);
            if (this.pointInHexagon(x, y, geometry)) {
                return room;
            }
        }
        return null;
    },

    getCorridorAtPoint(x, y) {
        // Check if near a corridor line
        return null; // Simplified
    },

    setClickHandler(handler) {
        this.clickHandler = handler;
    },

    truncate(str, len) {
        if (str.length <= len) return str;
        return str.substr(0, len - 1) + '...';
    }
};