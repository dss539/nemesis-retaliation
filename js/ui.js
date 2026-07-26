// Nemesis: Retaliation - UI Management

const UI = {
    state: null,
    selectedCard: null,

    updateState(state) {
        this.state = state;
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

            div.innerHTML = `
                <div class="char-name">${player.name} - ${charData.name || '?'}</div>
                <div class="stat-row"><span>HP: ${player.health}/${player.maxHealth}</span><span>O2: ${player.oxygen}</span></div>
                <div class="health-bar"><div class="health-fill ${healthClass}" style="width:${healthPercent}%"></div></div>
                <div class="stat-row">
                    <span>Cards: ${player.actionHand.length}</span>
                    <span>Contam: ${player.contaminationInHand.length}</span>
                </div>
                <div class="stat-row">
                    <span>Wounds: ${player.seriousWounds.length}</span>
                    <span>Larva: ${player.larva ? 'Yes' : 'No'}</span>
                </div>
                <div class="stat-row">
                    <span>Items: ${player.backpack.length}</span>
                    <span>${player.hasEscaped ? 'Escaped' : player.hasHibernated ? 'Hibernating' : player.alive ? 'Active' : 'Dead'}</span>
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
            cardDiv.className = 'hand-card action-card';
            if (this.selectedCard === i) cardDiv.classList.add('selected');
            cardDiv.textContent = card.action || 'Action';
            cardDiv.onclick = () => {
                this.selectedCard = i;
                this.renderCardArea();
            };
            handCards.appendChild(cardDiv);
        });

        // Contamination cards
        myPlayer.contaminationInHand.forEach((card, i) => {
            const cardDiv = document.createElement('div');
            cardDiv.className = 'hand-card contamination-card';
            cardDiv.textContent = 'Contam';
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
                    <div class="card-name">${this.state.missionTask.name}</div>
                    <div class="card-type">Mission Task</div>
                    <div style="margin-top:4px">${this.state.missionTask.text}</div>
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
                    <div class="card-name">${obj.name}</div>
                    <div class="card-type">${i === 0 ? 'Mission' : 'Private'} Objective</div>
                    <div style="margin-top:4px">${obj.text}</div>
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
                div.innerHTML = `<div class="card-name">${itemData?.name || itemId}</div><div class="card-type">Hand ${i+1}</div>`;
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
                div.innerHTML = `<div class="card-name">${itemData?.name || itemId}</div>`;
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
            <div><span class="label">Turn:</span><span class="value">${this.state.players[this.state.currentPlayer]?.name || '-'}</span></div>
            <div><span class="label">Actions:</span><span class="value">${this.state.actionsRemaining}</span></div>
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
            { id: 'move', label: 'Move', icon: '↗' },
            { id: 'cautiousMove', label: 'Cautious Move', icon: '↗+' },
            { id: 'shoot', label: 'Shoot', icon: '🎯' },
            { id: 'burst', label: 'Burst', icon: '💥' },
            { id: 'melee', label: 'Melee', icon: '⚔' },
            { id: 'useItem', label: 'Use Item', icon: '📦' },
            { id: 'useTacticalGear', label: 'Use Gear', icon: '⚙' },
            { id: 'useRoom', label: 'Use Room', icon: '🏠' },
            { id: 'search', label: 'Search', icon: '🔍' },
            { id: 'trade', label: 'Trade', icon: '🤝' },
            { id: 'activateRobot', label: 'Robot', icon: '🤖' },
            { id: 'pass', label: 'Pass', icon: '⏭' }
        ];

        // Character-specific actions
        if (myPlayer.character === 'recon') actions.push({ id: 'sprint', label: 'Sprint', icon: '🏃' });
        if (myPlayer.character === 'medicalSupport') actions.push({ id: 'rest', label: 'Rest', icon: '💤' });
        if (myPlayer.character === 'combatEngineer') {
            actions.push({ id: 'reinforce', label: 'Reinforce', icon: '🛡' });
            actions.push({ id: 'drill', label: 'Drill', icon: '⛏' });
        }
        if (myPlayer.character === 'officer') actions.push({ id: 'command', label: 'Command', icon: '📢' });

        actions.forEach(action => {
            const btn = document.createElement('button');
            btn.className = 'action-btn';
            btn.textContent = action.icon + ' ' + action.label;
            btn.disabled = !isMyTurn || this.state.actionsRemaining <= 0;
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
        if (!currentRoom) return;

        // Find adjacent rooms (simplified - show all discovered rooms and undiscovered directions)
        const adjacentCorridors = state.corridors.filter(c => c.room1 === myPlayer.location || c.room2 === myPlayer.location);
        const adjacentRooms = adjacentCorridors.map(c => c.room1 === myPlayer.location ? c.room2 : c.room1).filter(r => r);

        // Also show unexplored directions (from current room)
        // For now, allow exploring in 4 directions
        const directions = ['North', 'East', 'South', 'West'];

        let content = '<h2>Move</h2>';
        if (cautious) content += '<p>Cautious movement: places a Secure token in the destination room.</p>';

        content += '<div class="modal-card-list">';
        adjacentRooms.forEach(roomId => {
            const room = state.rooms[roomId];
            const roomData = GAME_DATA.ROOMS[roomId] || {};
            content += `
                <div class="modal-card" onclick="UI.executeMove('${roomId}', ${cautious})">
                    <div class="mc-name">${roomData.name || roomId}</div>
                    <div class="mc-text">${room?.discovered ? 'Discovered' : 'Undiscovered'}</div>
                </div>
            `;
        });

        // Exploration directions
        content += '<div style="margin-top:12px;font-size:0.85em;color:#8899aa">Explore new direction:</div>';
        directions.forEach((dir, i) => {
            content += `
                <div class="modal-card" onclick="UI.executeExplore(${i}, ${cautious})">
                    <div class="mc-name">${dir}</div>
                    <div class="mc-text">Unexplored</div>
                </div>
            `;
        });
        content += '</div>';

        content += '<button class="btn btn-secondary" style="margin-top:12px" onclick="UI.closeModal()">Cancel</button>';

        this.showModal(content);
    },

    executeMove(roomId, cautious) {
        const action = cautious ? 'cautiousMove' : 'move';
        NemesisNetwork.sendAction(action, { targetRoom: roomId });
        this.closeModal();
    },

    executeExplore(direction, cautious) {
        const myPlayer = this.state.players[NemesisNetwork.playerId];
        const currentRoom = this.state.rooms[myPlayer.location];
        const newPos = {
            x: (currentRoom.position?.x || 0) + (direction === 1 ? 1 : direction === 3 ? -1 : 0),
            y: (currentRoom.position?.y || 0) + (direction === 2 ? 1 : direction === 0 ? -1 : 0)
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

        let content = '<h2>Burst Fire</h2>';
        content += '<p>Choose a corridor to burst at:</p>';
        content += '<div class="modal-card-list">';
        adjacentCorridors.forEach(c => {
            const intruderCount = state.intruders.filter(i => i.location.type === 'corridor' && i.location.id === c.id).length;
            content += `
                <div class="modal-card" onclick="UI.executeBurst('${c.id}')">
                    <div class="mc-name">Corridor (Value: ${c.value})</div>
                    <div class="mc-text">${intruderCount} intruder(s) ${c.noise ? '| Noise!' : ''}</div>
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

        let content = '<h2>Trade</h2>';
        if (playersInRoom.length === 0) {
            content += '<p>No other players in your room.</p>';
        } else {
            content += '<div class="modal-card-list">';
            playersInRoom.forEach(p => {
                content += `
                    <div class="modal-card" onclick="UI.executeTrade(${p.id})">
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

    executeTrade(targetPlayer) {
        NemesisNetwork.sendAction('trade', { targetPlayer });
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

        let content = '<h2>Reinforce Corridor</h2>';
        if (adjacentCorridors.length === 0) {
            content += '<p>No corridors available to reinforce.</p>';
        } else {
            content += '<div class="modal-card-list">';
            adjacentCorridors.forEach(c => {
                content += `
                    <div class="modal-card" onclick="UI.executeReinforce('${c.id}')">
                        <div class="mc-name">Corridor (Value: ${c.value})</div>
                        <div class="mc-text">${c.noise ? 'Has noise' : 'Empty'}</div>
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
            content += '<p>No lower-rank players to command.</p>';
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