// Original production-safe game art registry and semantic icon layer.
// Generated SVG files are reproducible with scripts/generate_game_art.py.
const GameArt = {
    base: 'assets/generated',
    images: new Map(),
    loading: false,
    loaded: false,
    callbacks: [],

    roomIds: [
        'landingZone','drillingRoom','lifeSupportControlA','hibernatorium','coolingSystem',
        'lifeSupportControlB','serverRoom','lifeSupportControlC','nest','reactor',
        'escapeShuttle','armory','surgeryRoom','laboratory','gunneryRoom','shelter',
        'technicalCorridorEntrance','sprinklersControl','engineRoom','storageRoom',
        'commsRoom','wasteDisposal','airlock','powerGenerator'
    ],
    characterIds: ['contractor','recon','officer','medicalSupport','heavyGunOperator','combatEngineer'],
    intruderIds: ['larva','drone','adult','queen'],

    characterColors: {
        contractor: '#d89248', recon: '#54b9b0', officer: '#cf6a76',
        medicalSupport: '#73bd8a', heavyGunOperator: '#b49ad7', combatEngineer: '#d6b95d'
    },
    intruderColors: { larva: '#99c45a', drone: '#cf8245', adult: '#cc4e56', queen: '#d65ac8' },
    playerColors: { blue:'#4da3d0', green:'#52b878', red:'#d75a61', yellow:'#d5b24d', purple:'#a875cf' },

    preload(callback) {
        if (callback) this.callbacks.push(callback);
        if (this.loaded) {
            this.flushCallbacks();
            return;
        }
        if (this.loading) return;
        this.loading = true;

        const manifest = [
            ['board', `${this.base}/board/facility-playmat.svg`],
            ...this.roomIds.map(id => [`room:${id}`, `${this.base}/rooms/${id}.svg`]),
            ...this.characterIds.map(id => [`character:${id}`, `${this.base}/characters/${id}.svg`]),
            ...this.intruderIds.map(id => [`intruder:${id}`, `${this.base}/intruders/${id}.svg`])
        ];
        let remaining = manifest.length;
        const done = () => {
            remaining -= 1;
            if (remaining > 0) return;
            this.loading = false;
            this.loaded = true;
            this.flushCallbacks();
        };
        manifest.forEach(([key, url]) => {
            const image = new Image();
            image.decoding = 'async';
            image.onload = done;
            image.onerror = () => {
                console.warn(`Game art failed to load: ${url}`);
                done();
            };
            image.src = url;
            this.images.set(key, image);
        });
    },

    flushCallbacks() {
        const callbacks = this.callbacks.splice(0);
        callbacks.forEach(callback => callback());
    },

    get(key) {
        const image = this.images.get(key);
        return image?.complete && image.naturalWidth > 0 ? image : null;
    },

    url(kind, id) {
        if (kind === 'character') return `${this.base}/characters/${id}.svg`;
        if (kind === 'intruder') return `${this.base}/intruders/${id}.svg`;
        if (kind === 'room') return `${this.base}/rooms/${id}.svg`;
        return '';
    },

    iconMarkup(icon, className = '') {
        const safeIcon = String(icon || 'item').replace(/[^a-z-]/g, '');
        const safeClass = String(className || '').replace(/[^a-z0-9 _-]/gi, '');
        return `<svg class="game-icon ${safeClass}" aria-hidden="true" focusable="false"><use href="${this.base}/ui-symbols.svg#i-${safeIcon}"></use></svg>`;
    },

    actionIcon(action) {
        return ({
            move:'move', cautiousMove:'cautious', shoot:'shoot', burst:'burst', melee:'melee',
            useItem:'item', useTacticalGear:'gear', useRoom:'room', search:'search', trade:'trade',
            activateRobot:'robot', pass:'pass', sprint:'sprint', rest:'rest', reinforce:'reinforce',
            drill:'drill', command:'command'
        })[action] || 'gear';
    },

    itemIcon(item) {
        if (!item) return 'item';
        const traits = item.traits || [];
        if (traits.some(trait => trait.includes('WEAPON'))) return 'shoot';
        if (item.name?.toLowerCase().includes('grenade')) return 'grenade';
        if (item.name?.toLowerCase().includes('ammo')) return 'ammo';
        if (item.name?.toLowerCase().includes('robot')) return 'robot';
        if (item.type === 'green' || item.name?.toLowerCase().includes('med')) return 'health';
        return item.type === 'support' ? 'gear' : 'item';
    },

    cardArtwork(icon, label, variant = 'neutral') {
        return `<div class="card-art card-art-${variant}">${this.iconMarkup(icon)}<span>${label}</span></div>`;
    },

    drawCanvasIcon(ctx, icon, cx, cy, size, color = '#e8f0f2') {
        const s = size / 24;
        ctx.save();
        ctx.translate(cx - size / 2, cy - size / 2);
        ctx.scale(s, s);
        ctx.strokeStyle = color;
        ctx.fillStyle = color;
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.beginPath();
        if (icon === 'fire') {
            ctx.moveTo(13, 2); ctx.bezierCurveTo(16, 7, 13, 10, 13, 10);
            ctx.bezierCurveTo(18, 8, 21, 12, 19, 17); ctx.bezierCurveTo(17, 22, 7, 23, 5, 16);
            ctx.bezierCurveTo(4, 12, 7, 9, 9, 7); ctx.bezierCurveTo(9, 11, 11, 12, 12, 12);
            ctx.bezierCurveTo(15, 8, 15, 5, 13, 2); ctx.stroke();
        } else if (icon === 'malfunction') {
            ctx.moveTo(13,2); ctx.lineTo(4,14); ctx.lineTo(11,14); ctx.lineTo(10,22); ctx.lineTo(20,9); ctx.lineTo(13,9); ctx.closePath(); ctx.stroke();
        } else if (icon === 'secure') {
            ctx.roundRect(5,10,14,11,2); ctx.stroke();
            ctx.moveTo(8,10); ctx.lineTo(8,7); ctx.bezierCurveTo(8,2,16,2,16,7); ctx.lineTo(16,10); ctx.stroke();
            ctx.beginPath(); ctx.arc(12,15,1.5,0,Math.PI*2); ctx.fill();
        } else if (icon === 'computer') {
            ctx.roundRect(3,4,18,13,2); ctx.stroke(); ctx.moveTo(8,21); ctx.lineTo(16,21); ctx.moveTo(12,17); ctx.lineTo(12,21); ctx.stroke();
        } else if (icon === 'noise') {
            ctx.moveTo(4,9); ctx.lineTo(8,9); ctx.lineTo(13,5); ctx.lineTo(13,19); ctx.lineTo(8,15); ctx.lineTo(4,15); ctx.closePath(); ctx.stroke();
            ctx.beginPath(); ctx.arc(13,12,6,-0.75,0.75); ctx.stroke(); ctx.beginPath(); ctx.arc(13,12,9,-0.75,0.75); ctx.stroke();
        } else if (icon === 'robot') {
            ctx.roundRect(4,6,16,14,3); ctx.stroke(); ctx.moveTo(12,2); ctx.lineTo(12,6); ctx.stroke();
            ctx.beginPath(); ctx.arc(8,12,1,0,Math.PI*2); ctx.arc(16,12,1,0,Math.PI*2); ctx.fill();
            ctx.beginPath(); ctx.moveTo(8,17); ctx.lineTo(16,17); ctx.stroke();
        } else {
            ctx.arc(12,12,8,0,Math.PI*2); ctx.stroke();
        }
        ctx.restore();
    }
};
