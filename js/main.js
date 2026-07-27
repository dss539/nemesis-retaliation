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
        renderJoinQrCode(code);

        // Create engine and game state (lobby state)
        engine = new NemesisEngine();
        const numPlayers = parseInt(document.getElementById('num-players').value);
        const names = [name];
        for (let i = 1; i < numPlayers; i++) names.push('Player ' + (i + 1));
        engine.createGame(names, numPlayers);
        engine.state.players[0].name = name;
        window.nemesisEngine = engine;

        // Subscribe to engine events (host only broadcasts, doesn't update UI here
        // — broadcastState handles host UI update)
        engine.subscribe((event, data, state) => {
            NemesisNetwork.broadcastState();
        });

        // Set up state update handler for client messages
        NemesisNetwork.onStateUpdate = (state) => {
            UI.updateState(state);
            // Auto-switch to game screen when game starts
            if (state.phase && state.phase !== 'setup' && !NemesisNetwork.isHost) {
                if (!document.getElementById('game-screen').classList.contains('active')) {
                    switchToGameScreen();
                }
            }
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
        NemesisNetwork.state = state; // Store for switchToGameScreen
        UI.updateState(state);
        if (state.phase && state.phase !== 'setup') {
            if (!document.getElementById('game-screen').classList.contains('active')) {
                switchToGameScreen();
            }
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
    const missingPlayers = engine.state.players.filter(p => !p.connected);
    if (missingPlayers.length > 0) {
        alert('All player slots must be filled before the game can begin.');
        return;
    }
    // Start the first round
    engine.startRound();
    switchToGameScreen();
}

function switchToGameScreen() {
    document.getElementById('lobby-screen').classList.remove('active');
    document.getElementById('game-screen').classList.add('active');
    Renderer.init('game-canvas');
    
    // Use full state everywhere — privacy is handled in UI rendering
    const stateSource = engine ? engine.getState() : NemesisNetwork.state || { players: [], log: [], round: 1, maxRounds: 14, currentPlayer: 0, actionsRemaining: 2, phase: 'setup' };
    UI.updateState(stateSource);

    // Route tactical board interactions through the UI controller.
    Renderer.setClickHandler((click) => {
        UI.handleBoardClick(click);
    });

    // Resize canvas to fit screen and detect mobile
    Renderer.resizeCanvas();

    // On mobile, start on board tab
    if (window.innerWidth <= 900) {
        UI.switchTab('board');
    }
}

function copyGameCode() {
    const code = document.getElementById('host-code').textContent;
    if (!code || code === 'Generating...') return;

    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(code).then(() => {
            const btn = document.getElementById('copy-code-btn');
            const orig = btn.textContent;
            btn.textContent = '✓ Copied!';
            setTimeout(() => { btn.textContent = orig; }, 2000);
        }).catch(() => {
            fallbackCopy(code);
        });
    } else {
        fallbackCopy(code);
    }
}

function fallbackCopy(text) {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try {
        document.execCommand('copy');
        const btn = document.getElementById('copy-code-btn');
        if (btn) {
            const orig = btn.textContent;
            btn.textContent = '✓ Copied!';
            setTimeout(() => { btn.textContent = orig; }, 2000);
        }
    } catch (e) {}
    document.body.removeChild(ta);
}

function gameJoinUrl(code) {
    const url = new URL(window.location.href);
    url.search = '';
    url.searchParams.set('code', code);
    return url.toString();
}

function renderJoinQrCode(code) {
    const target = document.getElementById('join-qr-code');
    if (!target) return;
    target.replaceChildren();
    if (typeof QRCode === 'undefined') {
        target.textContent = 'QR code unavailable';
        return;
    }
    new QRCode(target, {
        text: gameJoinUrl(code),
        width: 176,
        height: 176,
        colorDark: '#e7edf2',
        colorLight: '#0b1117',
        correctLevel: QRCode.CorrectLevel.M
    });
}

// === INITIALIZATION ===
window.addEventListener('DOMContentLoaded', () => {
    console.log('Nemesis: Retaliation - Digital Edition loaded');
    const code = new URLSearchParams(window.location.search).get('code')?.trim().toUpperCase();
    if (code) {
        showJoinPanel();
        document.getElementById('join-code').value = code;
        document.getElementById('player-name').focus();
    }
});