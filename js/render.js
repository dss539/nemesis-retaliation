// Nemesis: Retaliation - 2D Canvas Renderer

const Renderer = {
    canvas: null,
    ctx: null,
    state: null,
    hoveredElement: null,
    selectedRoom: null,
    clickHandler: null,

    // Grid layout constants
    ROOM_SIZE: 80,
    CORRIDOR_WIDTH: 30,
    GRID_PADDING: 40,

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

        // Maintain aspect ratio but fit within wrapper
        const aspectRatio = 800 / 600; // original canvas aspect
        let width = wrapperWidth;
        let height = width / aspectRatio;

        if (height > wrapperHeight) {
            height = wrapperHeight;
            width = height * aspectRatio;
        }

        // Only update CSS dimensions, keep internal resolution at 800x600
        this.canvas.style.width = Math.floor(width) + 'px';
        this.canvas.style.height = Math.floor(height) + 'px';

        this.render();
    },

    setState(state) {
        this.state = state;
        this.render();
    },

    render() {
        if (!this.ctx || !this.state) return;
        const ctx = this.ctx;
        ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw background
        ctx.fillStyle = '#0d1117';
        ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

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
        const sections = [
            { name: 'A', x: 0, color: 'rgba(60,80,40,0.15)' },
            { name: 'B', x: this.canvas.width / 3, color: 'rgba(60,60,80,0.15)' },
            { name: 'C', x: this.canvas.width * 2/3, color: 'rgba(80,40,40,0.15)' }
        ];

        sections.forEach(s => {
            ctx.fillStyle = s.color;
            ctx.fillRect(s.x, 0, this.canvas.width / 3, this.canvas.height);

            // Section label
            ctx.fillStyle = 'rgba(100,120,140,0.3)';
            ctx.font = '48px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(s.name, s.x + this.canvas.width / 6, 40);
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

        // Fire marker
        if (room.markers?.fire) {
            ctx.fillStyle = 'rgba(255,80,0,0.4)';
            ctx.beginPath();
            ctx.roundRect(x, y, w, h, 6);
            ctx.fill();
        }

        // Malfunction marker
        if (room.markers?.malfunction) {
            ctx.fillStyle = '#cc8800';
            ctx.font = '14px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('M', x + w - 10, y + 14);
        }

        // Secure tokens
        if (room.markers?.secure?.length > 0) {
            ctx.fillStyle = '#4488cc';
            for (let i = 0; i < room.markers.secure.length; i++) {
                ctx.beginPath();
                ctx.arc(x + 8 + i * 12, y + h - 8, 5, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // Room name
        ctx.fillStyle = '#e0e6ed';
        ctx.font = 'bold 10px sans-serif';
        ctx.textAlign = 'center';
        const name = roomData.name || room.id;
        ctx.fillText(this.truncate(name, 12), x + w/2, y + h/2 - 5);

        // Room type badge
        if (roomData.type && roomData.type !== '?') {
            ctx.fillStyle = '#ff4444';
            ctx.font = 'bold 9px sans-serif';
            ctx.fillText('[' + roomData.type + ']', x + w/2, y + h/2 + 10);
        }

        // Item icons
        if (roomData.itemIcons) {
            const colors = { red: '#e44', yellow: '#da3', green: '#4a9', blue: '#49c' };
            roomData.itemIcons.forEach((type, i) => {
                ctx.fillStyle = colors[type] || '#888';
                ctx.beginPath();
                ctx.arc(x + 8 + i * 10, y + 8, 4, 0, Math.PI * 2);
                ctx.fill();
            });
        }

        // Computer icon
        if (roomData.computer) {
            ctx.fillStyle = '#49c';
            ctx.font = '10px sans-serif';
            ctx.textAlign = 'left';
            ctx.fillText('C', x + w - 12, y + 12);
        }

        // Intruder count indicator
        const intrudersInRoom = this.state.intruders.filter(i => i.location.type === 'room' && i.location.id === room.id);
        if (intrudersInRoom.length > 0) {
            ctx.fillStyle = 'rgba(255,50,50,0.2)';
            ctx.beginPath();
            ctx.roundRect(x, y, w, h, 6);
            ctx.fill();
        }

        // Characters indicator
        const playersInRoom = this.state.players.filter(p => p.alive && p.location === room.id);
        if (playersInRoom.length > 0) {
            // Draw colored dots for each player
            playersInRoom.forEach((p, i) => {
                const colors = { blue:'#4499cc', green:'#44aa66', red:'#cc4444', yellow:'#daa333', purple:'#9944cc' };
                ctx.fillStyle = colors[p.color] || '#fff';
                ctx.beginPath();
                ctx.arc(x + w/2 - 15 + i * 10, y + h - 8, 5, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = '#000';
                ctx.lineWidth = 1;
                ctx.stroke();
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
        ctx.lineWidth = corridor.reinforced ? 4 : 3;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();

        // Noise marker
        if (corridor.noise) {
            const mx = (x1 + x2) / 2;
            const my = (y1 + y2) / 2;
            ctx.fillStyle = '#ffcc00';
            ctx.beginPath();
            ctx.arc(mx, my, 6, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#000';
            ctx.font = 'bold 8px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('!', mx, my + 3);
        }

        // Door
        if (corridor.door === 'closed') {
            const mx = (x1 + x2) / 2;
            const my = (y1 + y2) / 2;
            ctx.strokeStyle = '#aa4444';
            ctx.lineWidth = 5;
            ctx.beginPath();
            ctx.moveTo(mx - 8, my);
            ctx.lineTo(mx + 8, my);
            ctx.stroke();
        } else if (corridor.door === 'destroyed') {
            const mx = (x1 + x2) / 2;
            const my = (y1 + y2) / 2;
            ctx.strokeStyle = '#666';
            ctx.lineWidth = 2;
            ctx.setLineDash([3, 3]);
            ctx.beginPath();
            ctx.moveTo(mx - 8, my);
            ctx.lineTo(mx + 8, my);
            ctx.stroke();
            ctx.setLineDash([]);
        }

        // Value label
        ctx.fillStyle = '#888';
        ctx.font = '9px sans-serif';
        ctx.textAlign = 'center';
        const mx = (x1 + x2) / 2;
        const my = (y1 + y2) / 2 - 8;
        if (!corridor.reinforced) {
            ctx.fillText(corridor.value || '?', mx, my);
        }

        // Intruders in corridor
        const intrudersInCorridor = this.state.intruders.filter(i => i.location.type === 'corridor' && i.location.id === corridor.id);
        intrudersInCorridor.forEach((intruder, i) => {
            const colors = { drone:'#cc6600', adult:'#cc3333', larva:'#66cc33', queen:'#ff00ff' };
            ctx.fillStyle = colors[intruder.type] || '#fff';
            const ox = mx - 5 + (i % 3) * 8;
            const oy = my + 8 + Math.floor(i / 3) * 8;
            ctx.beginPath();
            ctx.arc(ox, oy, 4, 0, Math.PI * 2);
            ctx.fill();
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
        const x = this.GRID_PADDING + robotRoom.position.x * (this.ROOM_SIZE + this.CORRIDOR_WIDTH) + this.ROOM_SIZE - 12;
        const y = this.GRID_PADDING + robotRoom.position.y * (this.ROOM_SIZE + this.CORRIDOR_WIDTH) + this.ROOM_SIZE - 12;

        ctx.fillStyle = '#88ccff';
        ctx.beginPath();
        ctx.roundRect(x, y, 10, 10, 2);
        ctx.fill();
        ctx.fillStyle = '#000';
        ctx.font = '8px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('R', x + 5, y + 8);
    },

    drawRoundTrack(ctx) {
        // Draw at bottom of canvas
        const y = this.canvas.height - 25;
        const startX = 20;
        const spacing = 30;

        ctx.fillStyle = '#1a2030';
        ctx.fillRect(10, y - 5, 14 * spacing + 10, 20);
        ctx.strokeStyle = '#3a4550';
        ctx.lineWidth = 1;
        ctx.strokeRect(10, y - 5, 14 * spacing + 10, 20);

        for (let i = 1; i <= 14; i++) {
            const x = startX + (i - 1) * spacing + 5;

            // Round marker
            if (i === this.state.round) {
                ctx.fillStyle = '#ff4444';
                ctx.beginPath();
                ctx.arc(x, y + 5, 8, 0, Math.PI * 2);
                ctx.fill();
            }

            // Autodestruction token
            if (this.state.autodestruction.active && i === this.state.autodestruction.token) {
                ctx.fillStyle = '#ff8800';
                ctx.beginPath();
                ctx.arc(x, y + 5, 6, 0, Math.PI * 2);
                ctx.fill();
            }

            // Lander token
            if (i === this.state.landerRound) {
                ctx.fillStyle = '#44cc44';
                ctx.beginPath();
                ctx.arc(x, y + 5, 5, 0, Math.PI * 2);
                ctx.fill();
            }

            // Round number
            ctx.fillStyle = '#666';
            ctx.font = '8px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(i, x, y + 18);
        }
    },

    // === INTERACTION ===
    handleClick(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

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
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
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