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
        document.querySelector('.lobby-container')?.classList.add('host-active');
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

        // Wire lobby controls
        const hostCodeEl = document.getElementById('host-code');
        hostCodeEl.onclick = () => copyGameCode();
        document.getElementById('num-players').onchange = updateHostPlayerCount;

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
            // Connected to host — keep the join panel visible (showing
            // "Connected! Waiting for host...") until joinAccepted arrives
            // with the lobby data, at which point we switch to the guest lobby.
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
            // Switch from the join form to the read-only guest lobby view.
            showGuestLobby(data.lobby, data.gameCode || code);
        } else if (type === 'joinRejected') {
            document.getElementById('join-status').innerHTML = '<p style="color:#ff4444">' + data.reason + '</p>';
        } else if (type === 'lobbyState') {
            // Live-update the guest lobby roster while waiting for the host.
            updateGuestLobbyPlayers(data.lobby);
        }
    };
}

// Render the read-only guest lobby panel (no start button, no player-count
// selector). Mirrors the host lobby layout using the same CSS classes.
function showGuestLobby(lobbyData, gameCode) {
    const joinPanel = document.getElementById('join-panel');
    if (joinPanel) joinPanel.classList.add('hidden');

    // Widen the lobby container to match the host layout
    document.querySelector('.lobby-container')?.classList.add('host-active');

    const guestPanel = document.getElementById('guest-lobby-panel');
    if (guestPanel) guestPanel.classList.remove('hidden');

    const codeEl = document.getElementById('guest-code');
    if (codeEl) codeEl.textContent = gameCode || '';

    if (lobbyData) updateGuestLobbyPlayers(lobbyData);
}

// Update the guest lobby player roster (read-only). Reuses the same roster
// styling as the host lobby but targets the guest-specific element IDs.
function updateGuestLobbyPlayers(lobby) {
    if (!lobby) return;
    const list = document.getElementById('guest-lobby-players');
    if (!list) return;

    list.innerHTML = '';
    const count = lobby.players.length;
    const total = lobby.numPlayers;

    const rosterCount = document.getElementById('guest-roster-count');
    if (rosterCount) rosterCount.textContent = `${count}/${total}`;

    lobby.players.forEach((player, index) => {
        const li = document.createElement('li');
        const characterName = player.character ? (GAME_DATA.CHARACTERS[player.character]?.name || player.character) : '';
        const details = [characterName, index === 0 ? 'Host' : ''].filter(Boolean).join(' · ');
        li.innerHTML = `<span><strong>${escapeLobbyText(player.name)}</strong>${details ? `<small>${escapeLobbyText(details)}</small>` : ''}</span>`;
        list.appendChild(li);
    });

    for (let index = count; index < total; index++) {
        const li = document.createElement('li');
        li.className = 'empty-slot';
        li.textContent = 'Waiting…';
        list.appendChild(li);
    }
}

function updateHostPlayerCount() {
    if (!engine || engine.state.phase !== 'setup') return;
    const joinedPlayers = engine.state.players.filter(player => player.hasJoined);
    const select = document.getElementById('num-players');
    if (joinedPlayers.length > 1) {
        select.value = String(engine.state.numPlayers);
        return;
    }

    const numPlayers = Number(select.value);
    const hostName = engine.state.players[0].name;
    engine.createGame([hostName], numPlayers);
    updateLobbyPlayers({
        players: [{ name: hostName, character: engine.state.players[0].character, connected: true }],
        numPlayers
    });
    NemesisNetwork.broadcastLobbyState();
}

function updateLobbyPlayers(lobby) {
    const list = document.getElementById('lobby-players');
    if (!list) return;
    list.innerHTML = '';
    const count = lobby.players.length;
    const total = lobby.numPlayers;
    const rosterCount = document.getElementById('roster-count');
    const playerCountSelect = document.getElementById('num-players');
    if (rosterCount) rosterCount.textContent = `${count}/${total}`;
    if (playerCountSelect) playerCountSelect.disabled = count > 1;

    lobby.players.forEach((player, index) => {
        const li = document.createElement('li');
        const characterName = player.character ? (GAME_DATA.CHARACTERS[player.character]?.name || player.character) : '';
        const details = [characterName, index === 0 ? 'Host' : ''].filter(Boolean).join(' · ');
        li.innerHTML = `<span><strong>${escapeLobbyText(player.name)}</strong>${details ? `<small>${escapeLobbyText(details)}</small>` : ''}</span>`;
        list.appendChild(li);
    });

    for (let index = count; index < total; index++) {
        const li = document.createElement('li');
        li.className = 'empty-slot';
        li.textContent = 'Waiting…';
        list.appendChild(li);
    }

    const startBtn = document.getElementById('host-start-btn');
    if (startBtn) {
        const waiting = count < total;
        startBtn.disabled = waiting;
        startBtn.classList.toggle('waiting', waiting);
        startBtn.textContent = 'Start Game';
    }
}

function escapeLobbyText(value) {
    const span = document.createElement('span');
    span.textContent = String(value ?? '');
    return span.innerHTML;
}

function startGame() {
    if (!engine) return;
    const missingPlayers = engine.state.players.filter(p => !p.connected);
    if (missingPlayers.length > 0) {
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
            btn.textContent = '✓';
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
            btn.textContent = '✓';
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

    const urlLink = document.getElementById('join-url');
    if (urlLink) {
        const url = gameJoinUrl(code);
        urlLink.textContent = url;
        urlLink.href = url;
    }
}

function copyJoinUrl() {
    const urlLink = document.getElementById('join-url');
    if (!urlLink || !urlLink.textContent) return;
    const url = urlLink.textContent;
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(() => {
            const btn = document.getElementById('copy-url-btn');
            const orig = btn.textContent;
            btn.textContent = '✓';
            setTimeout(() => { btn.textContent = orig; }, 2000);
        }).catch(() => { fallbackCopy(url); });
    } else {
        fallbackCopy(url);
    }
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