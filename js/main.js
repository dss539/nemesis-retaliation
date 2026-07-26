// Nemesis: Retaliation - Main Entry Point

let engine = null;

// === LOBBY ===
function showHostPanel() {
    document.getElementById('btn-host').classList.add('hidden');
    document.getElementById('btn-join').classList.add('hidden');
    document.getElementById('host-name-panel').classList.remove('hidden');
}

function showJoinPanel() {
    document.getElementById('btn-host').classList.add('hidden');
    document.getElementById('btn-join').classList.add('hidden');
    document.getElementById('join-panel').classList.remove('hidden');
}

function createHost() {
    const name = document.getElementById('host-name').value.trim() || 'Host';
    NemesisNetwork.hostGame(name, (code) => {
        document.getElementById('host-name-panel').classList.add('hidden');
        document.getElementById('host-panel').classList.remove('hidden');
        document.getElementById('host-code').textContent = code;

        // Create engine and game state (lobby state)
        engine = new NemesisEngine();
        const numPlayers = parseInt(document.getElementById('num-players').value);
        const names = [name];
        for (let i = 1; i < numPlayers; i++) names.push('Player ' + (i + 1));
        engine.createGame(names, numPlayers);
        engine.state.players[0].name = name;
        window.nemesisEngine = engine;

        // Subscribe to engine events
        engine.subscribe((event, data, state) => {
            NemesisNetwork.broadcastState();
            UI.updateState(state);
        });

        // Set up state update handler for client messages
        NemesisNetwork.onStateUpdate = (state) => {
            UI.updateState(state);
        };

        NemesisNetwork.onMessage = (type, data) => {
            console.log('Message:', type, data);
            if (type === 'lobbyState') {
                updateLobbyPlayers(data.lobby);
            }
        };

        updateLobbyPlayers({
            players: [{ name: name, character: engine.state.players[0].character, connected: true }],
            numPlayers: numPlayers
        });
    });
}

function joinGame() {
    const code = document.getElementById('join-code').value.trim().toUpperCase();
    const name = document.getElementById('player-name').value.trim() || 'Player';
    if (!code) {
        document.getElementById('join-status').innerHTML = '<p style="color:#ff4444">Enter a game code</p>';
        return;
    }

    document.getElementById('join-status').innerHTML = '<p>Connecting...</p>';

    NemesisNetwork.joinGame(code, name,
        () => {
            // Connected
            document.getElementById('join-status').innerHTML = '<p style="color:#4a9">Connected! Waiting for host...</p>';
        },
        (error) => {
            document.getElementById('join-status').innerHTML = '<p style="color:#ff4444">Error: ' + error + '</p>';
        }
    );

    NemesisNetwork.onStateUpdate = (state) => {
        UI.updateState(state);
        if (state.phase !== 'setup') {
            switchToGameScreen();
        }
    };

    NemesisNetwork.onMessage = (type, data) => {
        console.log('Message:', type, data);
        if (type === 'joinAccepted') {
            document.getElementById('join-status').innerHTML = '<p style="color:#4a9">Joined game as Player ' + (data.playerId + 1) + '</p>';
        } else if (type === 'joinRejected') {
            document.getElementById('join-status').innerHTML = '<p style="color:#ff4444">' + data.reason + '</p>';
        } else if (type === 'lobbyState') {
            updateLobbyPlayers(data.lobby);
        }
    };
}

function updateLobbyPlayers(lobby) {
    const list = document.getElementById('lobby-players');
    if (!list) return;
    list.innerHTML = '';
    const count = lobby.players.length;
    document.getElementById('player-list').querySelector('h3').textContent = `Players (${count}/${lobby.numPlayers})`;
    lobby.players.forEach(p => {
        const li = document.createElement('li');
        li.textContent = p.name + (p.character ? ' - ' + (GAME_DATA.CHARACTERS[p.character]?.name || p.character) : '');
        list.appendChild(li);
    });
}

function startGame() {
    if (!engine) return;
    // Start the first round
    engine.startRound();
    switchToGameScreen();
}

function switchToGameScreen() {
    document.getElementById('lobby-screen').classList.remove('active');
    document.getElementById('game-screen').classList.add('active');
    Renderer.init('game-canvas');
    UI.updateState(engine ? engine.getState() : NemesisNetwork.state || { players: [], log: [], round: 1, maxRounds: 14, currentPlayer: 0, actionsRemaining: 2, phase: 'setup' });

    // Set up canvas click handler
    Renderer.setClickHandler((click) => {
        console.log('Canvas click:', click);
    });
}

// === INITIALIZATION ===
window.addEventListener('DOMContentLoaded', () => {
    console.log('Nemesis: Retaliation - Digital Edition loaded');
    // Entry point
});