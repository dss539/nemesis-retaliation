// Nemesis: Retaliation - Multiplayer Networking via PeerJS
// Host-authoritative model: host runs the engine, clients send actions

const NemesisNetwork = {
    peer: null,
    connections: {}, // peerId -> connection
    hostId: null,
    isHost: false,
    playerId: -1,
    gameCode: null,
    onStateUpdate: null,
    onMessage: null,

    // Generate a short game code
    generateCode() {
        const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
        let code = '';
        for (let i = 0; i < 6; i++) {
            code += chars[Math.floor(Math.random() * chars.length)];
        }
        return code;
    },

    // === HOST ===
    hostGame(playerName, onReady) {
        this.isHost = true;
        this.playerId = 0;
        const code = this.generateCode();
        const peerId = 'nemesis-rt-' + code;
        this.gameCode = code;

        this.peer = new Peer(peerId, { debug: 1 });

        this.peer.on('open', (id) => {
            console.log('Host peer opened with id:', id);
            if (onReady) onReady(code);
        });

        this.peer.on('connection', (conn) => {
            console.log('New connection from:', conn.peer);
            this.setupConnection(conn);
        });

        this.peer.on('error', (err) => {
            console.error('Peer error:', err);
            if (err.type === 'unavailable-id') {
                // Regenerate code
                this.peer.destroy();
                this.hostGame(playerName, onReady);
            }
        });
    },

    // === JOIN ===
    joinGame(code, playerName, onConnected, onError) {
        this.isHost = false;
        this.gameCode = code.toUpperCase();
        this.hostId = 'nemesis-rt-' + code.toUpperCase();
        const myId = 'nemesis-rt-' + code.toUpperCase() + '-' + Math.random().toString(36).substr(2, 6);

        this.peer = new Peer(myId, { debug: 1 });

        this.peer.on('open', (id) => {
            console.log('Client peer opened, connecting to host:', this.hostId);
            const conn = this.peer.connect(this.hostId, { reliable: true });

            conn.on('open', () => {
                console.log('Connected to host');
                this.connections[this.hostId] = conn;
                conn.send({
                    type: 'join',
                    name: playerName,
                    peerId: id
                });
                if (onConnected) onConnected();
            });

            conn.on('data', (data) => {
                this.handleMessage(data);
            });

            conn.on('close', () => {
                console.log('Disconnected from host');
                if (onError) onError('Disconnected from host');
            });
        });

        this.peer.on('error', (err) => {
            console.error('Peer error:', err);
            if (onError) onError(err.type + ': ' + err.message);
        });
    },

    // === CONNECTION MANAGEMENT ===
    setupConnection(conn) {
        conn.on('open', () => {
            console.log('Connection opened with', conn.peer);
            this.connections[conn.peer] = conn;
        });

        conn.on('data', (data) => {
            this.handleHostMessage(conn, data);
        });

        conn.on('close', () => {
            console.log('Connection closed:', conn.peer);
            delete this.connections[conn.peer];
            this.handleDisconnect(conn.peer);
        });
    },

    handleDisconnect(peerId) {
        if (this.isHost && window.nemesisEngine) {
            // Find player by peer ID and mark as disconnected
            const state = window.nemesisEngine.getState();
            const player = state?.players?.find(p => p.peerId === peerId);
            if (player) {
                player.connected = false;
                player.peerId = null;
                state.paused = true;
                state.pausedPlayerId = player.id;
                state.pauseReason = `Waiting for ${player.name || 'a player'} to rejoin`;
                window.nemesisEngine.log(`${player.name || 'Player'} disconnected — game paused until their slot is reclaimed`);
                this.broadcastState();
            }
        }
    },

    log(msg) {
        console.log('[Network] ' + msg);
    },

    // === MESSAGE HANDLING ===
    // Host receives messages from clients
    handleHostMessage(conn, data) {
        const engine = window.nemesisEngine;
        if (!engine) return;

        switch(data.type) {
            case 'join':
                const state = engine.getState();
                // Reclaim a dropped player's seat before assigning an unjoined
                // lobby slot. Reclaiming preserves the character and all state.
                const reclaimSlot = state.players.findIndex(p => p.hasJoined && !p.connected);
                const openLobbySlot = state.phase === 'setup'
                    ? state.players.findIndex(p => !p.hasJoined)
                    : -1;
                const slot = reclaimSlot !== -1 ? reclaimSlot : openLobbySlot;
                if (slot === -1) {
                    conn.send({ type: 'joinRejected', reason: 'Game is full' });
                    return;
                }
                const joiningPlayer = state.players[slot];
                joiningPlayer.name = data.name || joiningPlayer.name;
                joiningPlayer.peerId = conn.peer;
                joiningPlayer.connected = true;
                joiningPlayer.hasJoined = true;

                const disconnectedJoinedPlayers = state.players.filter(p => p.hasJoined && !p.connected);
                if (state.paused && disconnectedJoinedPlayers.length === 0) {
                    state.paused = false;
                    state.pauseReason = null;
                    state.pausedPlayerId = null;
                    engine.log(`${joiningPlayer.name || 'Player'} filled the disconnected seat — game resumed`);
                }

                // Build lobby data once and include it in the joinAccepted message
                // so the joining client can render the guest lobby immediately.
                const lobbyData = {
                    players: state.players.filter(p => p.hasJoined).map(p => ({ name: p.name, character: p.character, connected: p.connected })),
                    numPlayers: state.numPlayers
                };
                const gameCode = this.gameCode || '';
                conn.send({
                    type: 'joinAccepted',
                    playerId: slot,
                    state: this.serializeState(state),
                    lobby: lobbyData,
                    gameCode: gameCode
                });

                // Update host's own lobby UI
                if (typeof updateLobbyPlayers === 'function') {
                    updateLobbyPlayers(lobbyData);
                }

                // Broadcast updated player list to all clients
                this.broadcastLobbyState();
                this.broadcastState();
                break;

            case 'action':
                // Client wants to perform an action
                const result = engine.performAction(data.playerId, data.actionType, data.params);
                conn.send({
                    type: 'actionResult',
                    requestId: data.requestId,
                    result: result
                });
                // Broadcast new state to all
                this.broadcastState();
                break;

            case 'chooseObjective':
                if (data.playerId !== undefined && engine.state) {
                    const result = engine.chooseObjective(data.playerId, data.objectiveId);
                    conn.send({ type: 'actionResult', requestId: data.requestId, result });
                    this.broadcastState();
                }
                break;

            case 'lobbyUpdate':
                this.broadcastLobbyState();
                break;
        }
    },

    // Client receives messages from host
    handleMessage(data) {
        switch(data.type) {
            case 'joinAccepted':
                this.playerId = data.playerId;
                if (data.gameCode) this.gameCode = data.gameCode;
                if (this.onMessage) this.onMessage('joinAccepted', data);
                if (this.onStateUpdate) this.onStateUpdate(data.state);
                break;

            case 'joinRejected':
                if (this.onMessage) this.onMessage('joinRejected', data);
                break;

            case 'stateUpdate':
                if (this.onStateUpdate) this.onStateUpdate(data.state);
                break;

            case 'actionResult':
                if (this.onMessage) this.onMessage('actionResult', data);
                break;

            case 'lobbyState':
                if (this.onMessage) this.onMessage('lobbyState', data);
                break;

            case 'playerDisconnected':
                if (this.onMessage) this.onMessage('playerDisconnected', data);
                break;

            case 'gameEvent':
                if (this.onMessage) this.onMessage('gameEvent', data);
                break;
        }
    },

    // === BROADCASTING (host only) ===
    broadcastMessage(message) {
        Object.values(this.connections).forEach(conn => {
            if (conn.open) {
                conn.send(message);
            }
        });
    },

    broadcastState() {
        if (!this.isHost || !window.nemesisEngine) return;
        const state = window.nemesisEngine.getState();
        
        // Host gets full state (needed for engine)
        if (typeof UI !== 'undefined' && UI.updateState) {
            UI.updateState(state);
        }
        
        // Send full state to each connected client — privacy is handled in UI rendering
        Object.entries(this.connections).forEach(([peerId, conn]) => {
            if (!conn.open) return;
            conn.send({ type: 'stateUpdate', state: this.serializeState(state) });
        });
    },

    broadcastLobbyState() {
        if (!this.isHost || !window.nemesisEngine) return;
        const state = window.nemesisEngine.getState();
        if (!state) return;
        const lobbyData = {
            players: state.players.filter(p => p.hasJoined).map(p => ({ name: p.name, character: p.character, connected: p.connected })),
            numPlayers: state.numPlayers
        };
        this.broadcastMessage({ type: 'lobbyState', lobby: lobbyData });
    },

    serializeState(state) {
        // Deep clone state for transmission
        return JSON.parse(JSON.stringify(state));
    },

    // Serialize state for a specific player, hiding other players' private info
    serializeStateForPlayer(state, playerId) {
        const cloned = JSON.parse(JSON.stringify(state));
        
        // Hide private info from other players
        if (cloned.players) {
            cloned.players.forEach((p, i) => {
                if (i !== playerId) {
                    // Hide objectives, hand, backpack details
                    p.objectives = p.chosenObjective ? [{ id: p.chosenObjective }] : [];
                    p.actionHand = p.actionHand ? new Array(p.actionHand.length).fill({ type: 'hidden' }) : [];
                    p.backpack = p.backpack ? new Array(p.backpack.length).fill('hidden') : [];
                    p.handSlots = p.handSlots ? p.handSlots.map(h => h ? 'hidden' : null) : [];
                    p.tacticalBelt = p.tacticalBelt ? p.tacticalBelt.map(t => t ? 'hidden' : null) : [];
                    p.seriousWounds = p.seriousWounds ? p.seriousWounds.map(() => 'hidden') : [];
                }
            });
        }
        
        // Hide contamination card infected status (only visible when scanned)
        if (cloned.contaminationDeck) {
            cloned.contaminationDeck = cloned.contaminationDeck.map(() => 'hidden');
        }
        
        // Hide event deck top card (only visible when resolved)
        if (cloned.eventDeck) {
            cloned.eventDeck = cloned.eventDeck.map(() => 'hidden');
        }
        
        // Hide intruder attack deck
        if (cloned.intruderAttackDeck) {
            cloned.intruderAttackDeck = cloned.intruderAttackDeck.map(() => 'hidden');
        }
        
        // Hide serious wound deck
        if (cloned.seriousWoundDeck) {
            cloned.seriousWoundDeck = cloned.seriousWoundDeck.map(() => 'hidden');
        }
        
        // Hide queen health deck
        if (cloned.queenHealthDeck) {
            cloned.queenHealthDeck = cloned.queenHealthDeck.map(() => 'hidden');
        }
        
        // Hide intruder bag contents (players shouldn't know what's coming)
        if (cloned.intruderBag) {
            cloned.intruderBag = cloned.intruderBag.map(() => ({ type: 'hidden' }));
        }
        
        // Hide item decks
        if (cloned.itemDecks) {
            cloned.itemDecks = {
                red: cloned.itemDecks.red ? new Array(cloned.itemDecks.red.length).fill('hidden') : [],
                yellow: cloned.itemDecks.yellow ? new Array(cloned.itemDecks.yellow.length).fill('hidden') : [],
                green: cloned.itemDecks.green ? new Array(cloned.itemDecks.green.length).fill('hidden') : []
            };
        }
        
        // Hide anti-aircraft token order (secret until resolved)
        if (cloned.antiAircraft && cloned.antiAircraft.tokens) {
            cloned.antiAircraft.tokens = cloned.antiAircraft.tokens.map(() => 'hidden');
        }
        
        // Hide robot card (secret until revealed)
        if (cloned.robot && !cloned.robot.revealed) {
            cloned.robot.card = 'hidden';
        }
        
        return cloned;
    },

    // === SENDING ACTIONS (client to host) ===
    sendAction(actionType, params) {
        if (this.isHost) {
            // Local execution
            const engine = window.nemesisEngine;
            return engine.performAction(this.playerId, actionType, params);
        }

        const requestId = Date.now() + '-' + Math.random();
        const conn = this.connections[this.hostId];
        if (conn && conn.open) {
            conn.send({
                type: 'action',
                playerId: this.playerId,
                actionType: actionType,
                params: params,
                requestId: requestId
            });
        }
    },

    sendChooseObjective(objectiveId) {
        if (this.isHost) {
            window.nemesisEngine.chooseObjective(this.playerId, objectiveId);
            this.broadcastState();
        } else {
            const conn = this.connections[this.hostId];
            if (conn && conn.open) {
                conn.send({
                    type: 'chooseObjective',
                    playerId: this.playerId,
                    objectiveId: objectiveId
                });
            }
        }
    },

    // === CLEANUP ===
    disconnect() {
        Object.values(this.connections).forEach(conn => conn.close());
        if (this.peer) this.peer.destroy();
        this.connections = {};
        this.peer = null;
        this.isHost = false;
        this.playerId = -1;
        this.gameCode = null;
    }
};