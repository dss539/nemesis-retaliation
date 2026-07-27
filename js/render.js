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
    _suppressClickUntil: 0,

    // Fixed tactical-grid geometry. The 42px void between every 110px room
    // remains visible even where no corridor tile has been discovered.
    ROOM_SIZE: 110,
    CORRIDOR_WIDTH: 42,
    GRID_PADDING_X: 62,
    GRID_PADDING_Y: 70,
    // For a regular octagon in a square: side = size - 2*cut = cut*sqrt(2).
    OCTAGON_CUT: 110 / (2 + Math.SQRT2),

    init(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        GameArt.preload(() => this.render());
        this.canvas.addEventListener('click', (e) => {
            if (Date.now() < this._suppressClickUntil) return;
            this.handleClick(e);
        });
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));

        // Browser-synthesized clicks handle taps. Avoid preventing touchstart:
        // one-finger drags must remain available to pan the overflow canvas.
        const wrapper = document.getElementById('canvas-wrapper');
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
        const wrapper = document.getElementById('canvas-wrapper');
        if (wrapper) {
            wrapper.scrollLeft = 0;
            wrapper.scrollTop = 0;
        }
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
    },

    drawSections(ctx) {
        const baseH = this._baseH || 900;
        const step = this.ROOM_SIZE + this.CORRIDOR_WIDTH;
        const sections = [
            { name: 'SECTOR A', start: 0, columns: 3, color: 'rgba(45,116,93,0.055)' },
            { name: 'SECTOR B', start: 3, columns: 3, color: 'rgba(65,98,145,0.055)' },
            { name: 'SECTOR C', start: 6, columns: 1, color: 'rgba(143,67,67,0.065)' }
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
        const bounds = GAME_DATA.CONFIG.boardBounds;
        const step = this.ROOM_SIZE + this.CORRIDOR_WIDTH;
        ctx.save();
        for (let gy = bounds.minY; gy <= bounds.maxY; gy++) {
            for (let gx = bounds.minX; gx <= bounds.maxX; gx++) {
                const x = this.GRID_PADDING_X + gx * step;
                const y = this.GRID_PADDING_Y + gy * step;

                // Every graph node is visible before exploration. The room itself
                // later replaces this subdued empty-slot floor without moving it.
                this.octagonPath(ctx, x, y, this.ROOM_SIZE);
                ctx.fillStyle = 'rgba(12,25,33,0.68)';
                ctx.fill();
                ctx.strokeStyle = 'rgba(105,150,166,0.36)';
                ctx.lineWidth = 2;
                ctx.setLineDash([6, 6]);
                ctx.stroke();

                this.octagonPath(ctx, x + 6, y + 6, this.ROOM_SIZE - 12);
                ctx.strokeStyle = 'rgba(74,108,121,0.17)';
                ctx.lineWidth = 1;
                ctx.setLineDash([]);
                ctx.stroke();
            }
        }
        ctx.restore();
    },

    roomGeometry(roomOrPosition) {
        const position = roomOrPosition?.position || roomOrPosition;
        if (!position) return null;
        const step = this.ROOM_SIZE + this.CORRIDOR_WIDTH;
        return {
            x: this.GRID_PADDING_X + position.x * step,
            y: this.GRID_PADDING_Y + position.y * step,
            w: this.ROOM_SIZE,
            h: this.ROOM_SIZE,
            cx: this.GRID_PADDING_X + position.x * step + this.ROOM_SIZE / 2,
            cy: this.GRID_PADDING_Y + position.y * step + this.ROOM_SIZE / 2
        };
    },

    regularOctagonCut(size) {
        return size / (2 + Math.SQRT2);
    },

    octagonVertices(x, y, size) {
        const cut = this.regularOctagonCut(size);
        return [
            { x: x + cut, y },
            { x: x + size - cut, y },
            { x: x + size, y: y + cut },
            { x: x + size, y: y + size - cut },
            { x: x + size - cut, y: y + size },
            { x: x + cut, y: y + size },
            { x, y: y + size - cut },
            { x, y: y + cut }
        ];
    },

    octagonPath(ctx, x, y, size) {
        const vertices = this.octagonVertices(x, y, size);
        ctx.beginPath();
        ctx.moveTo(vertices[0].x, vertices[0].y);
        vertices.slice(1).forEach(vertex => ctx.lineTo(vertex.x, vertex.y));
        ctx.closePath();
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
        this.octagonPath(ctx, x, y, w);
        ctx.fillStyle = '#080d12';
        ctx.fill();
        ctx.strokeStyle = edgeColor;
        ctx.lineWidth = isCurrentRoom ? 4 : 3;
        ctx.stroke();

        this.octagonPath(ctx, x + 5, y + 5, w - 10);
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
            this.octagonPath(ctx, x + 3, y + 3, w - 6);
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
            ctx.fillText('FAULT', x + w - 27, y + 19);
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
            this.octagonPath(ctx, x + 3, y + 3, w - 6);
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
        const roomRadius = this.ROOM_SIZE / 2 - 1;
        const x1 = g1.cx + ux * roomRadius;
        const y1 = g1.cy + uy * roomRadius;
        const x2 = g2.cx - ux * roomRadius;
        const y2 = g2.cy - uy * roomRadius;
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
            this.octagonPath(ctx, geometry.x - 4, geometry.y - 4, geometry.w + 8);
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
            if (geometry && this.pointInOctagon(x, y, geometry)) return target;
        }
        return null;
    },

    pointInOctagon(x, y, geometry) {
        const localX = x - geometry.x;
        const localY = y - geometry.y;
        const size = geometry.w;
        const cut = this.regularOctagonCut(size);
        if (localX < 0 || localY < 0 || localX > size || localY > size) return false;
        return localX + localY >= cut &&
            (size - localX) + localY >= cut &&
            localX + (size - localY) >= cut &&
            (size - localX) + (size - localY) >= cut;
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
        this.drawAssetToken(ctx, GameArt.get('character:' + player.character), cx, cy, 18, ring,
            (player.name || '?').charAt(0).toUpperCase(), player.id === this.state.currentPlayer);
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
            if (this.pointInOctagon(x, y, geometry)) {
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