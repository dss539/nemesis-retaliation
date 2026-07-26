// Nemesis: Retaliation - 2D Canvas Renderer

const Renderer = {
    canvas: null,
    ctx: null,
    state: null,
    hoveredElement: null,
    selectedRoom: null,
    clickHandler: null,

    // Grid layout constants — scaled up for readability
    ROOM_SIZE: 120,
    CORRIDOR_WIDTH: 45,
    GRID_PADDING: 50,

    init(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.canvas.addEventListener('click', (e) => this.handleClick(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));

        // Touch support
        this.canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            const rect = this.canvas.getBoundingClientRect();
            const scaleX = this.canvas.width / rect.width;
            const scaleY = this.canvas.height / rect.height;
            this.handleClick({
                clientX: touch.clientX,
                clientY: touch.clientY
            });
        }, { passive: false });

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

        let displayWidth = wrapperWidth;
        let displayHeight = displayWidth / aspectRatio;

        if (displayHeight > wrapperHeight) {
            displayHeight = wrapperHeight;
            displayWidth = displayHeight * aspectRatio;
        }

        // Set CSS display size
        this.canvas.style.width = Math.floor(displayWidth) + 'px';
        this.canvas.style.height = Math.floor(displayHeight) + 'px';

        // Set internal resolution to match display * devicePixelRatio for crisp text
        const dpr = window.devicePixelRatio || 1;
        this.canvas.width = Math.floor(displayWidth * dpr);
        this.canvas.height = Math.floor(displayHeight * dpr);

        // Scale the drawing context so game coordinates map correctly
        const scaleX = this.canvas.width / BASE_W;
        const scaleY = this.canvas.height / BASE_H;
        this.ctx.setTransform(scaleX, 0, 0, scaleY, 0, 0);

        // Store for click coordinate mapping
        this._displayWidth = displayWidth;
        this._displayHeight = displayHeight;
        this._baseW = BASE_W;
        this._baseH = BASE_H;

        this.render();
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

        // Draw background
        ctx.fillStyle = '#0d1117';
        ctx.fillRect(0, 0, this._baseW || 1200, this._baseH || 900);

        // Draw sections (3 columns: A, B, C)
        this.drawSections(ctx);

        // Draw rooms
        Object.values(this.state.rooms).forEach(room => {
            this.drawRoom(ctx, room);
        });

        // Draw corridors
        this.state.corridors.forEach(corridor => {
            this.drawCorridor(ctx, corridor);
        });

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
        const baseW = this._baseW || 1200;
        const baseH = this._baseH || 900;
        const sections = [
            { name: 'A', x: 0, color: 'rgba(60,80,40,0.15)' },
            { name: 'B', x: baseW / 3, color: 'rgba(60,60,80,0.15)' },
            { name: 'C', x: baseW * 2/3, color: 'rgba(80,40,40,0.15)' }
        ];

        sections.forEach(s => {
            ctx.fillStyle = s.color;
            ctx.fillRect(s.x, 0, baseW / 3, baseH);

            // Section label
            ctx.fillStyle = 'rgba(100,120,140,0.3)';
            ctx.font = '64px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(s.name, s.x + baseW / 6, 55);
        });
    },

    drawRoom(ctx, room) {
        if (!room.position) return;
        const x = this.GRID_PADDING + room.position.x * (this.ROOM_SIZE + this.CORRIDOR_WIDTH);
        const y = this.GRID_PADDING + room.position.y * (this.ROOM_SIZE + this.CORRIDOR_WIDTH);
        const w = this.ROOM_SIZE;
        const h = this.ROOM_SIZE;

        // Room background
        const roomData = GAME_DATA.ROOMS[room.id];
        if (!roomData) return;

        // Color by section
        let bgColor = '#2a3540';
        if (room.section === 'A') bgColor = '#2a3a28';
        if (room.section === 'B') bgColor = '#2a2a38';
        if (room.section === 'C') bgColor = '#3a2828';

        if (this.selectedRoom === room.id) {
            ctx.strokeStyle = '#ff4444';
            ctx.lineWidth = 3;
        } else {
            ctx.strokeStyle = '#3a4550';
            ctx.lineWidth = 1;
        }

        // Draw room
        ctx.fillStyle = bgColor;
        ctx.beginPath();
        ctx.roundRect(x, y, w, h, 6);
        ctx.fill();
        ctx.stroke();

        // Fire marker — icon + label
        if (room.markers?.fire) {
            ctx.fillStyle = 'rgba(255,80,0,0.3)';
            ctx.beginPath();
            ctx.roundRect(x, y, w, h, 8);
            ctx.fill();
            ctx.fillStyle = '#ff6600';
            ctx.font = 'bold 13px sans-serif';
            ctx.textAlign = 'left';
            ctx.fillText('FIRE', x + 6, y + 20);
        }

        // Malfunction marker — icon + label
        if (room.markers?.malfunction) {
            ctx.fillStyle = '#cc8800';
            ctx.font = 'bold 14px sans-serif';
            ctx.textAlign = 'right';
            ctx.fillText('🔧BROKEN', x + w - 6, y + 20);
        }

        // Secure tokens — show count as text
        if (room.markers?.secure?.length > 0) {
            ctx.fillStyle = '#4488cc';
            ctx.font = 'bold 12px sans-serif';
            ctx.textAlign = 'left';
            ctx.fillText('🔒x' + room.markers.secure.length, x + 6, y + h - 8);
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
            ctx.fillStyle = '#49c';
            ctx.font = 'bold 14px sans-serif';
            ctx.textAlign = 'left';
            ctx.fillText('C', x + w - 18, y + 18);
        }

        // Intruder count — text label with type breakdown
        const intrudersInRoom = this.state.intruders.filter(i => i.location.type === 'room' && i.location.id === room.id);
        if (intrudersInRoom.length > 0) {
            ctx.fillStyle = 'rgba(255,50,50,0.15)';
            ctx.beginPath();
            ctx.roundRect(x, y, w, h, 8);
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

        // Characters — show player initials with color
        const playersInRoom = this.state.players.filter(p => p.alive && p.location === room.id);
        if (playersInRoom.length > 0) {
            playersInRoom.forEach((p, i) => {
                const colors = { blue:'#4499cc', green:'#44aa66', red:'#cc4444', yellow:'#daa333', purple:'#9944cc' };
                const cx = x + 8 + i * 22;
                const cy = y + h - 12;
                ctx.fillStyle = colors[p.color] || '#fff';
                ctx.beginPath();
                ctx.arc(cx, cy, 10, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = '#000';
                ctx.lineWidth = 1;
                ctx.stroke();
                // Player initial
                ctx.fillStyle = '#fff';
                ctx.font = 'bold 10px sans-serif';
                ctx.textAlign = 'center';
                const initial = (p.name || '?').charAt(0).toUpperCase();
                ctx.fillText(initial, cx, cy + 4);
            });
        }
    },

    drawCorridor(ctx, corridor) {
        if (!corridor.position) return;
        // Corridors are drawn between rooms - simplified
        const room1 = this.state.rooms[corridor.room1];
        const room2 = this.state.rooms[corridor.room2];
        if (!room1?.position || !room2?.position) return;

        const x1 = this.GRID_PADDING + room1.position.x * (this.ROOM_SIZE + this.CORRIDOR_WIDTH) + this.ROOM_SIZE/2;
        const y1 = this.GRID_PADDING + room1.position.y * (this.ROOM_SIZE + this.CORRIDOR_WIDTH) + this.ROOM_SIZE/2;
        const x2 = this.GRID_PADDING + room2.position.x * (this.ROOM_SIZE + this.CORRIDOR_WIDTH) + this.ROOM_SIZE/2;
        const y2 = this.GRID_PADDING + room2.position.y * (this.ROOM_SIZE + this.CORRIDOR_WIDTH) + this.ROOM_SIZE/2;

        // Draw corridor line
        ctx.strokeStyle = corridor.reinforced ? '#4a8' : '#556';
        ctx.lineWidth = corridor.reinforced ? 6 : 4;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();

        // Noise marker — yellow circle with "!" and label
        if (corridor.noise) {
            const mx = (x1 + x2) / 2;
            const my = (y1 + y2) / 2;
            ctx.fillStyle = '#ffcc00';
            ctx.beginPath();
            ctx.arc(mx, my, 10, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#000';
            ctx.font = 'bold 13px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('!', mx, my + 5);
            // Label below
            ctx.fillStyle = '#ffcc00';
            ctx.font = 'bold 10px sans-serif';
            ctx.fillText('NOISE', mx, my - 14);
        }

        // Door
        if (corridor.door === 'closed') {
            const mx = (x1 + x2) / 2;
            const my = (y1 + y2) / 2;
            ctx.strokeStyle = '#aa4444';
            ctx.lineWidth = 7;
            ctx.beginPath();
            ctx.moveTo(mx - 12, my);
            ctx.lineTo(mx + 12, my);
            ctx.stroke();
        } else if (corridor.door === 'destroyed') {
            const mx = (x1 + x2) / 2;
            const my = (y1 + y2) / 2;
            ctx.strokeStyle = '#666';
            ctx.lineWidth = 3;
            ctx.setLineDash([4, 4]);
            ctx.beginPath();
            ctx.moveTo(mx - 12, my);
            ctx.lineTo(mx + 12, my);
            ctx.stroke();
            ctx.setLineDash([]);
        }

        // Value label
        ctx.fillStyle = '#888';
        ctx.font = '12px sans-serif';
        ctx.textAlign = 'center';
        const mx = (x1 + x2) / 2;
        const my = (y1 + y2) / 2 - 8;
        if (!corridor.reinforced) {
            ctx.fillText(corridor.value || '?', mx, my);
        }

        // Intruders in corridor — colored circles with type labels
        const intrudersInCorridor = this.state.intruders.filter(i => i.location.type === 'corridor' && i.location.id === corridor.id);
        const labels = { drone: 'D', adult: 'A', larva: 'L', queen: 'Q' };
        intrudersInCorridor.forEach((intruder, i) => {
            const colors = { drone:'#cc6600', adult:'#cc3333', larva:'#66cc33', queen:'#ff00ff' };
            ctx.fillStyle = colors[intruder.type] || '#fff';
            const ox = mx - 12 + (i % 4) * 16;
            const oy = my + 16 + Math.floor(i / 4) * 16;
            ctx.beginPath();
            ctx.arc(ox, oy, 8, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = '#000';
            ctx.lineWidth = 1;
            ctx.stroke();
            ctx.fillStyle = '#fff';
            ctx.font = 'bold 9px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(labels[intruder.type] || '?', ox, oy + 3);
        });
    },

    drawIntruder(ctx, intruder) {
        // Intruders are drawn at their room/corridor location
        // Already handled in drawRoom/drawCorridor via indicators
    },

    drawCharacter(ctx, player) {
        // Characters are shown as colored dots in rooms
        // Already handled in drawRoom
    },

    drawRobot(ctx) {
        const robotRoom = this.state.rooms[this.state.robot.location];
        if (!robotRoom?.position) return;
        const x = this.GRID_PADDING + robotRoom.position.x * (this.ROOM_SIZE + this.CORRIDOR_WIDTH) + this.ROOM_SIZE - 18;
        const y = this.GRID_PADDING + robotRoom.position.y * (this.ROOM_SIZE + this.CORRIDOR_WIDTH) + this.ROOM_SIZE - 18;

        ctx.fillStyle = '#88ccff';
        ctx.beginPath();
        ctx.roundRect(x, y, 14, 14, 3);
        ctx.fill();
        ctx.fillStyle = '#000';
        ctx.font = 'bold 11px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('R', x + 7, y + 11);
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
        const room = this.getRoomAtPoint(x, y);

        if (room) {
            this.canvas.style.cursor = 'pointer';
        } else {
            this.canvas.style.cursor = 'default';
        }
    },

    getRoomAtPoint(x, y) {
        if (!this.state) return null;
        for (const room of Object.values(this.state.rooms)) {
            if (!room.position) continue;
            const rx = this.GRID_PADDING + room.position.x * (this.ROOM_SIZE + this.CORRIDOR_WIDTH);
            const ry = this.GRID_PADDING + room.position.y * (this.ROOM_SIZE + this.CORRIDOR_WIDTH);
            if (x >= rx && x <= rx + this.ROOM_SIZE && y >= ry && y <= ry + this.ROOM_SIZE) {
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