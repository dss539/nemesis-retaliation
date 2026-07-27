// Nemesis: Retaliation - UI Management

const UI = {
    state: null,
    selectedCard: null,
    currentTab: 'board',
    movementMode: null,

    switchTab(tab) {
        this.currentTab = tab;
        const leftPanel = document.getElementById('left-panel');
        const rightPanel = document.getElementById('right-panel');
        const centerPanel = document.getElementById('center-panel');
        const navBtns = document.querySelectorAll('.mobile-nav-btn');

        // Hide all
        leftPanel?.classList.remove('mobile-active');
        rightPanel?.classList.remove('mobile-active');
        centerPanel?.classList.remove('mobile-active');

        // Deactivate all nav buttons
        navBtns.forEach(btn => btn.classList.remove('active'));

        // Show selected
        switch(tab) {
            case 'board':
                centerPanel?.classList.add('mobile-active');
                navBtns[0]?.classList.add('active');
                break;
            case 'players':
                leftPanel?.classList.add('mobile-active');
                navBtns[1]?.classList.add('active');
                break;
            case 'cards':
                rightPanel?.classList.add('mobile-active');
                navBtns[2]?.classList.add('active');
                if (rightPanel) rightPanel.scrollTop = 0;
                break;
            case 'log':
                rightPanel?.classList.add('mobile-active');
                navBtns[3]?.classList.add('active');
                // Scroll within the tab panel rather than moving the fixed page.
                const log = document.getElementById('game-log');
                if (rightPanel && log) rightPanel.scrollTop = log.offsetTop - 10;
                break;
        }

        // Resize canvas after tab switch
        setTimeout(() => Renderer.resizeCanvas(), 100);
    },

    updateState(state) {
        this.state = state;
        if (this.movementMode && (
            NemesisNetwork.playerId !== state.currentPlayer ||
            state.actionsRemaining <= 0 ||
            !state.players[NemesisNetwork.playerId]?.alive ||
            state.paused
        )) {
            this.cancelTacticalAction(false);
        }
        this.renderPlayerBoards();
        this.renderCardArea();
        this.renderGameInfo();
        this.renderActionBar();
        this.renderGameLog();
        Renderer.setState(state);
    },

    renderPlayerBoards() {
        const container = document.getElementById('player-boards');
        if (!container || !this.state) return;
        container.innerHTML = '';

        this.state.players.forEach((player, i) => {
            const div = document.createElement('div');
            div.className = 'player-board-mini';
            if (i === this.state.currentPlayer && player.alive) div.classList.add('current-player');
            if (!player.alive) div.classList.add('dead');

            const healthPercent = (player.health / player.maxHealth) * 100;
            const healthClass = this.isHeavilyInjured(player) ? 'heavily-injured' :
                               this.isInjured(player) ? 'injured' : '';

            const charData = GAME_DATA.CHARACTERS[player.character] || {};
            const characterColor = GameArt.characterColors[player.character] || '#d65a61';

            div.innerHTML = `
                <div class="player-identity" style="--character-color:${characterColor}">
                    <img class="character-portrait" src="${GameArt.url('character', player.character)}" alt="">
                    <div><div class="player-name">${player.name}</div><div class="character-name">${charData.name || '?'}</div></div>
                </div>
                <div class="stat-row icon-stat"><span>${GameArt.iconMarkup('health')} HP ${player.health}/${player.maxHealth}</span><span>${GameArt.iconMarkup('oxygen')} O₂ ${player.oxygen}</span></div>
                <div class="health-bar"><div class="health-fill ${healthClass}" style="width:${healthPercent}%"></div></div>
                <div class="stat-row icon-stat">
                    <span>${GameArt.iconMarkup('cards')} ${player.actionHand.filter(c => c.type !== 'contamination').length}</span>
                    <span>${GameArt.iconMarkup('contamination')} ${player.actionHand.filter(c => c.type === 'contamination').length}</span>
                </div>
                <div class="stat-row icon-stat">
                    <span>${GameArt.iconMarkup('wound')} ${player.seriousWounds.length}</span>
                    <span>${GameArt.iconMarkup('larva')} ${player.larva ? 'INFECTED' : 'Clear'}</span>
                </div>
                <div class="stat-row">
                    <span>Items: ${player.backpack.length}</span>
                    <span>${player.hasEscaped ? 'Escaped' : player.hasHibernated ? 'Hibernated' : player.alive ? 'Active' : 'Dead'}</span>
                </div>
            `;
            container.appendChild(div);
        });
    },

    renderCardArea() {
        const container = document.getElementById('card-area');
        if (!container || !this.state) return;
        container.innerHTML = '';

        const myPlayer = this.state.players[NemesisNetwork.playerId] || this.state.players[0];
        if (!myPlayer) return;

        // Hand cards
        const handDiv = document.createElement('div');
        handDiv.innerHTML = '<div style="font-size:0.8em;color:#8899aa;margin-bottom:4px">Your Hand (' + myPlayer.actionHand.length + '):</div>';
        const handCards = document.createElement('div');
        handCards.id = 'hand-cards';

        myPlayer.actionHand.forEach((card, i) => {
            const cardDiv = document.createElement('div');
            const isContamination = card.type === 'contamination';
            cardDiv.className = isContamination ? 'hand-card contamination-card' : 'hand-card action-card';
            if (this.selectedCard === i) cardDiv.classList.add('selected');
            if (isContamination) {
                cardDiv.innerHTML = `${GameArt.cardArtwork('contamination', 'CONTAMINATION', 'contamination')}<span class="hand-card-title">Contamination</span>`;
                cardDiv.setAttribute('aria-label', 'Contamination card — cannot be used for Actions');
            } else {
                const actionName = card.action || 'Action';
                cardDiv.innerHTML = `${GameArt.cardArtwork(GameArt.actionIcon(card.action), 'ACTION', 'action')}<span class="hand-card-title">${actionName}</span>`;
                cardDiv.setAttribute('aria-label', actionName + ' action card');
                cardDiv.onclick = () => {
                    this.selectedCard = i;
                    this.renderCardArea();
                };
            }
            handCards.appendChild(cardDiv);
        });

        handDiv.appendChild(handCards);
        container.appendChild(handDiv);

        // Objectives
        if (myPlayer.objectives && myPlayer.objectives.length > 0) {
            const objDiv = document.createElement('div');
            objDiv.style.marginTop = '12px';
            objDiv.innerHTML = '<div style="font-size:0.8em;color:#8899aa;margin-bottom:4px">Objectives:</div>';

            // Mission Task
            if (this.state.missionTask) {
                const mtDiv = document.createElement('div');
                mtDiv.className = 'card-display';
                mtDiv.innerHTML = `
                    ${GameArt.cardArtwork('objective', 'MISSION', 'objective')}
                    <div class="card-copy"><div class="card-name">${this.state.missionTask.name}</div>
                    <div class="card-type">Mission Task</div>
                    <div class="card-text">${this.state.missionTask.text}</div></div>
                `;
                objDiv.appendChild(mtDiv);
            }

            // Player objectives
            myPlayer.objectives.forEach((obj, i) => {
                const oDiv = document.createElement('div');
                oDiv.className = 'card-display';
                const isSelected = myPlayer.chosenObjective === obj.id;
                if (isSelected) oDiv.style.borderColor = '#ff4444';
                oDiv.innerHTML = `
                    ${GameArt.cardArtwork('objective', i === 0 ? 'MISSION' : 'PRIVATE', 'objective')}
                    <div class="card-copy"><div class="card-name">${obj.name}</div>
                    <div class="card-type">${i === 0 ? 'Mission' : 'Private'} Objective</div>
                    <div class="card-text">${obj.text}</div></div>
                    ${!myPlayer.chosenObjective ? `<button class="action-btn" style="margin-top:4px;width:100%" onclick="UI.chooseObjective('${obj.id}')">Choose</button>` : ''}
                `;
                objDiv.appendChild(oDiv);
            });

            container.appendChild(objDiv);
        }

        // Items in hand slots
        if (myPlayer.handSlots && myPlayer.handSlots.some(h => h)) {
            const itemsDiv = document.createElement('div');
            itemsDiv.style.marginTop = '12px';
            itemsDiv.innerHTML = '<div style="font-size:0.8em;color:#8899aa;margin-bottom:4px">Equipped:</div>';
            myPlayer.handSlots.forEach((itemId, i) => {
                if (!itemId) return;
                const itemData = GAME_DATA.ITEMS[itemId];
                const div = document.createElement('div');
                div.className = 'card-display';
                const itemVariant = itemData?.type || 'neutral';
                div.innerHTML = `${GameArt.cardArtwork(GameArt.itemIcon(itemData), 'EQUIPPED', itemVariant)}<div class="card-copy"><div class="card-name">${itemData?.name || itemId}</div><div class="card-type">Hand ${i+1}</div></div>`;
                itemsDiv.appendChild(div);
            });
            container.appendChild(itemsDiv);
        }

        // Backpack
        if (myPlayer.backpack && myPlayer.backpack.length > 0) {
            const bpDiv = document.createElement('div');
            bpDiv.style.marginTop = '12px';
            bpDiv.innerHTML = '<div style="font-size:0.8em;color:#8899aa;margin-bottom:4px">Backpack (' + myPlayer.backpack.length + '):</div>';
            myPlayer.backpack.forEach(itemId => {
                const itemData = GAME_DATA.ITEMS[itemId];
                const div = document.createElement('div');
                div.className = 'card-display';
                const itemVariant = itemData?.type || 'neutral';
                div.innerHTML = `${GameArt.cardArtwork(GameArt.itemIcon(itemData), 'PACK', itemVariant)}<div class="card-copy"><div class="card-name">${itemData?.name || itemId}</div></div>`;
                bpDiv.appendChild(div);
            });
            container.appendChild(bpDiv);
        }
    },

    renderGameInfo() {
        const infoBar = document.getElementById('game-info-bar');
        if (!infoBar || !this.state) return;
        infoBar.innerHTML = `
            <div><span class="label">Round:</span><span class="value">${this.state.round}/${this.state.maxRounds}</span></div>
            <div><span class="label">Phase:</span><span class="value">${this.state.phase}</span></div>
            <div><span class="label">Turn:</span><span class="value">${GAME_DATA.CHARACTERS[this.state.players[this.state.currentPlayer]?.character]?.name || '-'}</span></div>
            <div><span class="label">Actions:</span><span class="value">${this.state.actionsRemaining}</span></div>
            ${this.state.paused ? `<div><span class="label">Status:</span><span class="value">PAUSED — ${this.state.pauseReason || 'Waiting for a player'}</span></div>` : ''}
        `;
    },

    renderActionBar() {
        const container = document.getElementById('action-bar');
        if (!container || !this.state) return;
        container.innerHTML = '';

        const isMyTurn = NemesisNetwork.playerId === this.state.currentPlayer;
        const myPlayer = this.state.players[NemesisNetwork.playerId];
        if (!myPlayer || !myPlayer.alive) return;

        const actions = [
            { id: 'move', label: 'Move' },
            { id: 'cautiousMove', label: 'Cautious Move' },
            { id: 'shoot', label: 'Shoot' },
            { id: 'burst', label: 'Burst' },
            { id: 'melee', label: 'Melee' },
            { id: 'useItem', label: 'Use Item' },
            { id: 'useTacticalGear', label: 'Use Gear' },
            { id: 'useRoom', label: 'Use Room' },
            { id: 'search', label: 'Search' },
            { id: 'trade', label: 'Trade' },
            { id: 'activateRobot', label: 'Robot' },
            { id: 'pass', label: 'Pass' }
        ];

        // Character-specific actions
        if (myPlayer.character === 'recon') actions.push({ id: 'sprint', label: 'Sprint' });
        if (myPlayer.character === 'medicalSupport') actions.push({ id: 'rest', label: 'Rest' });
        if (myPlayer.character === 'combatEngineer') {
            actions.push({ id: 'reinforce', label: 'Reinforce' });
            actions.push({ id: 'drill', label: 'Drill' });
        }
        if (myPlayer.character === 'officer') actions.push({ id: 'command', label: 'Command' });

        actions.forEach(action => {
            const btn = document.createElement('button');
            btn.className = 'action-btn';
            if (this.movementMode?.action === action.id) btn.classList.add('active');
            btn.innerHTML = GameArt.iconMarkup(GameArt.actionIcon(action.id)) + `<span>${action.label}</span>`;
            btn.setAttribute('aria-label', action.label);
            btn.disabled = this.state.paused || !isMyTurn || this.state.actionsRemaining <= 0;
            btn.onclick = () => this.handleActionClick(action.id);
            container.appendChild(btn);
        });
    },

    renderGameLog() {
        const container = document.getElementById('game-log');
        if (!container || !this.state) return;
        container.innerHTML = '';

        const logs = this.state.log.slice(-30);
        logs.forEach(entry => {
            const div = document.createElement('div');
            div.className = 'log-entry';
            if (entry.message.startsWith('===')) div.classList.add('highlight');
            if (entry.message.startsWith('--')) div.classList.add('system');
            div.textContent = entry.message;
            container.appendChild(div);
        });
        container.scrollTop = container.scrollHeight;
    },

    // === ACTION HANDLING ===
    handleActionClick(actionId) {
        switch(actionId) {
            case 'move':
            case 'cautiousMove':
                this.showMoveModal(actionId === 'cautiousMove');
                break;
            case 'shoot':
            case 'melee':
                this.showTargetModal(actionId);
                break;
            case 'burst':
                this.showBurstModal();
                break;
            case 'search':
                NemesisNetwork.sendAction('search', {});
                break;
            case 'useRoom':
                NemesisNetwork.sendAction('useRoom', {});
                break;
            case 'useItem':
                this.showItemModal();
                break;
            case 'useTacticalGear':
                this.showTacticalGearModal();
                break;
            case 'trade':
                this.showTradeModal();
                break;
            case 'activateRobot':
                this.showRobotModal();
                break;
            case 'pass':
                NemesisNetwork.sendAction('pass', {});
                break;
            case 'sprint':
                this.showMoveModal(false, true);
                break;
            case 'rest':
                NemesisNetwork.sendAction('rest', {});
                break;
            case 'reinforce':
                this.showReinforceModal();
                break;
            case 'drill':
                NemesisNetwork.sendAction('drill', {});
                break;
            case 'command':
                this.showCommandModal();
                break;
            default:
                NemesisNetwork.sendAction(actionId, {});
        }
    },

    showMoveModal(cautious, sprint) {
        const state = this.state;
        const myPlayer = state.players[NemesisNetwork.playerId];
        const currentRoom = state.rooms[myPlayer.location];
        if (!currentRoom?.position) return;

        const action = sprint ? 'sprint' : cautious ? 'cautiousMove' : 'move';
        if (this.movementMode?.action === action) {
            this.cancelTacticalAction();
            return;
        }

        // Discovered destinations are legal only through open adjacent corridors.
        const connectedTargets = state.corridors
            .filter(corridor =>
                (corridor.room1 === myPlayer.location || corridor.room2 === myPlayer.location) &&
                corridor.door !== 'closed'
            )
            .map(corridor => {
                const roomId = corridor.room1 === myPlayer.location ? corridor.room2 : corridor.room1;
                return state.rooms[roomId] ? { kind: 'room', roomId, corridorId: corridor.id } : null;
            })
            .filter(Boolean);

        // Empty nodes in all eight compass directions become exploration targets.
        // Off-board and occupied slots are omitted rather than shown as disabled.
        // slots are omitted completely rather than shown as disabled choices.
        const directions = GAME_DATA.CONFIG.directions;
        const explorationTargets = directions.map(direction => ({
            kind: 'explore',
            direction: direction.id,
            position: {
                x: currentRoom.position.x + direction.dx,
                y: currentRoom.position.y + direction.dy
            }
        })).filter(target => {
            const { x, y } = target.position;
            if (!GAME_DATA.CONFIG.boardSlots.some(slot => slot.x === x && slot.y === y)) return false;
            return !Object.values(state.rooms).some(room => room.position?.x === x && room.position?.y === y);
        });

        const targets = [...connectedTargets, ...explorationTargets];
        if (targets.length === 0) {
            this.showModal('<h2>No Legal Moves</h2><p>There are no open Corridors or empty Room slots adjacent to this Room.</p><button class="btn btn-secondary" onclick="UI.closeModal()">OK</button>');
            return;
        }

        this.movementMode = { action, cautious: !!cautious, sprint: !!sprint };
        Renderer.setMovementTargets(targets, target => this.executeTacticalMove(target));
        const prompt = document.getElementById('tactical-prompt');
        if (prompt) {
            prompt.classList.remove('hidden');
            prompt.innerHTML = `<span><strong>${cautious ? 'CAUTIOUS MOVE' : sprint ? 'SPRINT' : 'MOVE'}</strong> — Select a highlighted destination</span><button onclick="UI.cancelTacticalAction()">Cancel</button>`;
        }
        this.renderActionBar();
    },

    executeTacticalMove(target) {
        if (!this.movementMode) return;
        const action = this.movementMode.action;
        const params = target.kind === 'room'
            ? { targetRoom: target.roomId }
            : {
                targetRoom: 'explore_' + Date.now(),
                position: target.position,
                explore: true,
                direction: target.direction
            };
        this.cancelTacticalAction();
        NemesisNetwork.sendAction(action, params);
    },

    cancelTacticalAction(renderActions = true) {
        this.movementMode = null;
        Renderer.clearMovementTargets();
        const prompt = document.getElementById('tactical-prompt');
        if (prompt) {
            prompt.classList.add('hidden');
            prompt.innerHTML = '';
        }
        if (renderActions && this.state) this.renderActionBar();
    },

    handleBoardClick(click) {
        // Room selection remains available for inspection; tactical actions are
        // handled directly by Renderer and accept highlighted targets only.
        if (click.type === 'room') Renderer.selectedRoom = click.room;
    },

    executeMove(roomId, cautious) {
        const action = cautious ? 'cautiousMove' : 'move';
        NemesisNetwork.sendAction(action, { targetRoom: roomId });
        this.closeModal();
    },

    executeExplore(direction, cautious) {
        const myPlayer = this.state.players[NemesisNetwork.playerId];
        const currentRoom = this.state.rooms[myPlayer.location];
        const offset = GAME_DATA.CONFIG.directions.find(candidate => candidate.id === direction);
        if (!offset || !currentRoom?.position) return;
        const newPos = {
            x: currentRoom.position.x + offset.dx,
            y: currentRoom.position.y + offset.dy
        };
        const action = cautious ? 'cautiousMove' : 'move';
        NemesisNetwork.sendAction(action, {
            targetRoom: 'explore_' + Date.now(),
            position: newPos,
            explore: true,
            direction: direction
        });
        this.closeModal();
    },

    showTargetModal(actionId) {
        const state = this.state;
        const myPlayer = state.players[NemesisNetwork.playerId];
        const intrudersInRoom = state.intruders.filter(i => i.location.type === 'room' && i.location.id === myPlayer.location);

        if (intrudersInRoom.length === 0) {
            this.showModal('<h2>No Targets</h2><p>No intruders in your room.</p><button class="btn btn-secondary" onclick="UI.closeModal()">OK</button>');
            return;
        }

        let content = '<h2>' + (actionId === 'shoot' ? 'Shoot' : 'Melee Attack') + '</h2>';
        content += '<div class="modal-card-list">';
        intrudersInRoom.forEach(intruder => {
            const colors = { drone:'#cc6600', adult:'#cc3333', larva:'#66cc33', queen:'#ff00ff' };
            content += `
                <div class="modal-card" onclick="UI.executeAttack('${actionId}','${intruder.id}')">
                    <div class="mc-name" style="color:${colors[intruder.type]}">${intruder.type.toUpperCase()}</div>
                    <div class="mc-text">Hits: ${intruder.hits || 0}</div>
                </div>
            `;
        });
        content += '</div>';
        content += '<button class="btn btn-secondary" style="margin-top:12px" onclick="UI.closeModal()">Cancel</button>';
        this.showModal(content);
    },

    executeAttack(actionId, targetId) {
        NemesisNetwork.sendAction(actionId, { targetId });
        this.closeModal();
    },

    showBurstModal() {
        const state = this.state;
        const myPlayer = state.players[NemesisNetwork.playerId];
        const adjacentCorridors = state.corridors.filter(c => c.room1 === myPlayer.location || c.room2 === myPlayer.location);

        let content = '<h2>Burst</h2>';
        content += '<p>Choose a corridor to burst at:</p>';
        content += '<div class="modal-card-list">';
        adjacentCorridors.forEach(c => {
            const intruderCount = state.intruders.filter(i => i.location.type === 'corridor' && i.location.id === c.id).length;
            content += `
                <div class="modal-card" onclick="UI.executeBurst('${c.id}')">
                    <div class="mc-name">Corridor (Noise Value: ${c.value})</div>
                    <div class="mc-text">${intruderCount} Intruder(s) ${c.noise ? '| Noise marker' : ''}</div>
                </div>
            `;
        });
        content += '</div>';
        content += '<button class="btn btn-secondary" style="margin-top:12px" onclick="UI.closeModal()">Cancel</button>';
        this.showModal(content);
    },

    executeBurst(corridorId) {
        NemesisNetwork.sendAction('burst', { corridorId });
        this.closeModal();
    },

    showItemModal() {
        const myPlayer = this.state.players[NemesisNetwork.playerId];
        let content = '<h2>Use Item</h2>';

        const items = [...myPlayer.backpack, ...myPlayer.handSlots.filter(h => h)];
        if (items.length === 0) {
            content += '<p>No items available.</p>';
        } else {
            content += '<div class="modal-card-list">';
            items.forEach(itemId => {
                const itemData = GAME_DATA.ITEMS[itemId];
                if (!itemData) return;
                content += `
                    <div class="modal-card" onclick="UI.executeUseItem('${itemId}')">
                        <div class="mc-name">${itemData.name}</div>
                        <div class="mc-text">${itemData.text}</div>
                    </div>
                `;
            });
            content += '</div>';
        }
        content += '<button class="btn btn-secondary" style="margin-top:12px" onclick="UI.closeModal()">Cancel</button>';
        this.showModal(content);
    },

    executeUseItem(itemId) {
        NemesisNetwork.sendAction('useItem', { itemId });
        this.closeModal();
    },

    showTacticalGearModal() {
        const myPlayer = this.state.players[NemesisNetwork.playerId];
        let content = '<h2>Use Tactical Gear</h2>';

        const gear = myPlayer.tacticalBelt.filter(g => g);
        if (gear.length === 0) {
            content += '<p>No tactical gear available.</p>';
        } else {
            content += '<div class="modal-card-list">';
            gear.forEach((tokenType, i) => {
                const names = { ammo: 'Ammo', grenade: 'Grenade', oxygen: 'Oxygen', medpack: 'Medpack', ammo_half: 'Ammo (half)' };
                content += `
                    <div class="modal-card" onclick="UI.executeUseGear('${tokenType}')">
                        <div class="mc-name">${names[tokenType] || tokenType}</div>
                        <div class="mc-text">Tactical Gear</div>
                    </div>
                `;
            });
            content += '</div>';
        }
        content += '<button class="btn btn-secondary" style="margin-top:12px" onclick="UI.closeModal()">Cancel</button>';
        this.showModal(content);
    },

    executeUseGear(tokenType) {
        NemesisNetwork.sendAction('useTacticalGear', { tokenType });
        this.closeModal();
    },

    showTradeModal() {
        const state = this.state;
        const myPlayer = state.players[NemesisNetwork.playerId];
        const playersInRoom = state.players.filter(p => p.id !== NemesisNetwork.playerId && p.alive && p.location === myPlayer.location);
        const items = [...myPlayer.backpack, ...myPlayer.handSlots.filter(Boolean)];

        let content = '<h2>Trade</h2>';
        if (playersInRoom.length === 0 || items.length === 0) {
            content += `<p>${playersInRoom.length === 0 ? 'No other Characters in your Room.' : 'No items available to trade.'}</p>`;
        } else {
            content += '<div class="modal-card-list">';
            items.forEach(itemId => {
                const item = GAME_DATA.ITEMS[itemId];
                if (!item) return;
                content += `
                    <div class="modal-card" onclick="UI.showTradeRecipientModal('${itemId}')">
                        <div class="mc-name">${item.name}</div>
                        <div class="mc-text">Choose recipient</div>
                    </div>
                `;
            });
            content += '</div>';
        }
        content += '<button class="btn btn-secondary" style="margin-top:12px" onclick="UI.closeModal()">Cancel</button>';
        this.showModal(content);
    },

    showTradeRecipientModal(itemId) {
        const state = this.state;
        const myPlayer = state.players[NemesisNetwork.playerId];
        const playersInRoom = state.players.filter(p => p.id !== NemesisNetwork.playerId && p.alive && p.location === myPlayer.location);
        let content = '<h2>Give item to</h2><div class="modal-card-list">';
        playersInRoom.forEach(p => {
            content += `<div class="modal-card" onclick="UI.executeTrade(${p.id}, '${itemId}')"><div class="mc-name">${p.name}</div><div class="mc-text">${GAME_DATA.CHARACTERS[p.character]?.name || ''}</div></div>`;
        });
        content += '</div><button class="btn btn-secondary" style="margin-top:12px" onclick="UI.showTradeModal()">Back</button>';
        this.showModal(content);
    },

    executeTrade(targetPlayer, itemId) {
        NemesisNetwork.sendAction('trade', { targetPlayer, itemId });
        this.closeModal();
    },

    showRobotModal() {
        let content = '<h2>Activate Robot</h2>';
        const robot = this.state.robot;
        if (!robot.revealed) {
            content += '<p>Robot not yet revealed (connect Hibernatorium).</p>';
        } else if (robot.malfunction) {
            content += '<p>Robot is malfunctioning.</p>';
        } else {
            const robotCard = GAME_DATA.ROBOTS.find(r => r.id === robot.card);
            content += `<p>Robot: ${robotCard?.name || 'Unknown'}</p>`;
            content += `<p>${robotCard?.text || ''}</p>`;
            content += `<button class="btn btn-primary" onclick="UI.executeRobot()">Activate</button>`;
        }
        content += '<button class="btn btn-secondary" style="margin-top:12px" onclick="UI.closeModal()">Cancel</button>';
        this.showModal(content);
    },

    executeRobot() {
        NemesisNetwork.sendAction('activateRobot', {});
        this.closeModal();
    },

    showReinforceModal() {
        const state = this.state;
        const myPlayer = state.players[NemesisNetwork.playerId];
        const adjacentCorridors = state.corridors.filter(c =>
            (c.room1 === myPlayer.location || c.room2 === myPlayer.location) &&
            !c.reinforced &&
            c.intruders.filter(i => i).length === 0
        );

        let content = '<h2>Reinforce an Empty Corridor</h2>';
        if (adjacentCorridors.length === 0) {
            content += '<p>No corridors available to reinforce.</p>';
        } else {
            content += '<div class="modal-card-list">';
            adjacentCorridors.forEach(c => {
                content += `
                    <div class="modal-card" onclick="UI.executeReinforce('${c.id}')">
                        <div class="mc-name">Corridor (Noise Value: ${c.value})</div>
                        <div class="mc-text">${c.noise ? 'Has Noise marker' : 'Empty Corridor'}</div>
                    </div>
                `;
            });
            content += '</div>';
        }
        content += '<button class="btn btn-secondary" style="margin-top:12px" onclick="UI.closeModal()">Cancel</button>';
        this.showModal(content);
    },

    executeReinforce(corridorId) {
        NemesisNetwork.sendAction('reinforce', { corridorId });
        this.closeModal();
    },

    showCommandModal() {
        const state = this.state;
        const myPlayer = state.players[NemesisNetwork.playerId];
        const lowerRank = state.players.filter(p => p.alive &&
            (GAME_DATA.CHARACTERS[p.character]?.rank || 0) < (GAME_DATA.CHARACTERS[myPlayer.character]?.rank || 0));

        let content = '<h2>Command</h2>';
        if (lowerRank.length === 0) {
            content += '<p>No lower-rank Characters to command.</p>';
        } else {
            content += '<div class="modal-card-list">';
            lowerRank.forEach(p => {
                content += `
                    <div class="modal-card" onclick="UI.executeCommand(${p.id})">
                        <div class="mc-name">${p.name}</div>
                        <div class="mc-text">${GAME_DATA.CHARACTERS[p.character]?.name || ''}</div>
                    </div>
                `;
            });
            content += '</div>';
        }
        content += '<button class="btn btn-secondary" style="margin-top:12px" onclick="UI.closeModal()">Cancel</button>';
        this.showModal(content);
    },

    executeCommand(targetPlayer) {
        // For now, just command them to move to our room
        NemesisNetwork.sendAction('command', { targetPlayer, targetRoom: this.state.players[NemesisNetwork.playerId].location });
        this.closeModal();
    },

    chooseObjective(objectiveId) {
        NemesisNetwork.sendChooseObjective(objectiveId);
    },

    // === MODAL ===
    showModal(content) {
        const overlay = document.getElementById('modal-overlay');
        const modal = document.getElementById('modal-content');
        modal.innerHTML = content;
        overlay.classList.remove('hidden');
    },

    closeModal() {
        const overlay = document.getElementById('modal-overlay');
        overlay.classList.add('hidden');
    },

    // === HELPERS ===
    isHeavilyInjured(player) {
        return player.health <= Math.floor(player.maxHealth / 3);
    },

    isInjured(player) {
        return player.health <= Math.floor(player.maxHealth * 2 / 3);
    }
};