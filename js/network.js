// Nemesis: Retaliation - Multiplayer Networking via PeerJS
// Host-authoritative model: host runs the engine, clients send actions

const NemesisNetwork = {
    peer: null,
    connections: {}, // peerId -> connection
    hostId: null,
    isHost: false,
    playerId: -1,
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
            // Find player by peer ID and handle disconnect
            const state = window.nemesisEngine.getState();
            const player = state?.players?.find(p => p.peerId === peerId);
            if (player) {
                this.broadcastMessage({
                    type: 'playerDisconnected',
                    playerId: player.id
                });
            }
        }
    },

    // === MESSAGE HANDLING ===
    // Host receives messages from clients
    handleHostMessage(conn, data) {
        const engine = window.nemesisEngine;
        if (!engine) return;

        switch(data.type) {
            case 'join':
                // Assign player ID
                const state = engine.getState();
                const playerCount = state.players.length;
                if (playerCount >= state.numPlayers) {
                    conn.send({ type: 'joinRejected', reason: 'Game is full' });
                    return;
                }
                // Assign player to existing slot
                const playerId = playerCount;
                state.players[playerId].name = data.name;
                state.players[playerId].peerId = conn.peer;

                conn.send({
                    type: 'joinAccepted',
                    playerId: playerId,
                    state: this.serializeState(state)
                });

                // Broadcast updated player list
                this.broadcastLobbyState();
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
                    engine.state.players[data.playerId].chosenObjective = data.objectiveId;
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
        const state = this.serializeState(window.nemesisEngine.getState());
        this.broadcastMessage({ type: 'stateUpdate', state: state });
    },

    broadcastLobbyState() {
        if (!this.isHost || !window.nemesisEngine) return;
        const state = window.nemesisEngine.getState();
        if (!state) return;
        const lobbyData = {
            players: state.players.map(p => ({ name: p.name, character: p.character, connected: !!p.peerId || p.id === 0 })),
            numPlayers: state.numPlayers
        };
        this.broadcastMessage({ type: 'lobbyState', lobby: lobbyData });
    },

    serializeState(state) {
        // Deep clone state for transmission
        // In production, could optimize by sending deltas
        return JSON.parse(JSON.stringify(state));
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
            window.nemesisEngine.state.players[this.playerId].chosenObjective = objectiveId;
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
    }
};