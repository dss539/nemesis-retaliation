// Nemesis: Retaliation - Core Game Engine
// Authoritative game state machine, runs on host

class NemesisEngine {
    constructor() {
        this.state = null;
        this.listeners = [];
    }

    // === STATE MANAGEMENT ===
    subscribe(callback) { this.listeners.push(callback); }

    notify(event, data) {
        this.listeners.forEach(cb => cb(event, data, this.state));
    }

    getState() { return this.state; }

    // === GAME SETUP ===
    createGame(playerNames, numPlayers) {
        const state = {
            phase: 'setup',
            round: 1,
            maxRounds: GAME_DATA.CONFIG.maxRounds,
            players: [],
            numPlayers: numPlayers,
            startingPlayer: 0,
            currentPlayer: 0,
            turnStep: 'action1', // action1, action2, endTurn
            actionsRemaining: GAME_DATA.CONFIG.actionsPerTurn,

            // Board
            rooms: {}, // roomId -> {id, type, section, discovered, position, markers}
            corridors: [], // [{id, value, position, room1, room2, door, noise, intruders, reinforced}]
            sections: {
                A: { lifeSupport: true, markers: [] },
                B: { lifeSupport: true, markers: [] },
                C: { lifeSupport: true, markers: [] }
            },

            // Decks
            itemDecks: {
                red: shuffle(Object.keys(GAME_DATA.ITEMS).filter(id => GAME_DATA.ITEMS[id].type === 'red')),
                yellow: shuffle(Object.keys(GAME_DATA.ITEMS).filter(id => GAME_DATA.ITEMS[id].type === 'yellow')),
                green: shuffle(Object.keys(GAME_DATA.ITEMS).filter(id => GAME_DATA.ITEMS[id].type === 'green'))
            },
            itemDiscards: { red: [], yellow: [], green: [] },
            eventDeck: shuffle([...GAME_DATA.EVENTS.map(e => e.id)]),
            eventDiscard: [],
            explorationDeck: shuffle([...GAME_DATA.EXPLORATION_CARDS.map(e => e.id)]),
            explorationDiscard: [],
            intruderAttackDeck: shuffle([...GAME_DATA.INTRUDER_ATTACKS.map(a => a.id)]),
            intruderAttackDiscard: [],
            seriousWoundDeck: shuffle([...GAME_DATA.SERIOUS_WOUNDS.map(w => w.id)]),
            seriousWoundDiscard: [],
            queenHealthDeck: shuffle([...GAME_DATA.QUEEN_HEALTH_CARDS.map(c => c.id)]),
            contaminationDeck: shuffle([...GAME_DATA.CONTAMINATION_CARDS.map(c => c.id)]),
            contaminationDiscard: [],

            // Intruder bag
            intruderBag: this.createIntruderBag(),
            intruderPool: { drone: 8, adult: 16, larva: 6, queen: 1 },

            // Intruders on board
            intruders: [], // [{id, type, location: {room/corridor, id}, hits}]

            // Map tokens/markers pool
            tokenPool: {
                noise: 20, fire: 8, malfunction: 8, secure: 12,
                ammo: 12, grenade: 6, oxygen: 8, medpack: 4
            },

            // Queen
            queen: {
                inPlay: false,
                location: null,
                hits: 0,
                dead: false,
                healthCardsRemaining: 12
            },

            // Nest
            nest: { eggs: GAME_DATA.CONFIG.nestEggs, destroyed: false, pendingDrones: 0 },

            // Robot
            robot: {
                card: null, // random robot card id
                revealed: false,
                location: 'hibernatorium',
                malfunction: false
            },

            // Anti-Aircraft
            antiAircraft: {
                tokens: shuffle(['active','inactive']), // top one is checked
                resolved: false,
                lander: { status: 'pending', characters: [] } // pending, landed, destroyed, launched
            },

            // Autodestruction
            autodestruction: { active: false, token: null },

            // Objectives
            missionTask: null,
            objectiveChoiceTrack: 0,

            // Game log
            log: [],

            // Map layout
            mapGrid: {}, // "x,y" -> {type: 'room'/'corridor', id}

            // Available rooms to place
            undiscoveredRooms: {
                // Landing Zone is placed below during setup and must never be drawn again.
                A: ['drillingRoom','lifeSupportControlA'],
                B: ['hibernatorium','coolingSystem','lifeSupportControlB','serverRoom'],
                C: ['lifeSupportControlC','nest','reactor','escapeShuttle'],
                '?': shuffle(['armory','surgeryRoom','laboratory','gunneryRoom','shelter','technicalCorridorEntrance','sprinklersControl','engineRoom','storageRoom','commsRoom','wasteDisposal','airlock','powerGenerator'])
            },

            // Lander position on round track
            landerRound: null,
            gameOver: false,
            paused: false,
            pauseReason: null,
            pausedPlayerId: null,
            winners: []
        };

        // Create host player only — others join via network
        const charIds = Object.keys(GAME_DATA.CHARACTERS);
        const charData = GAME_DATA.CHARACTERS[charIds[0]];
        state.players.push({
            id: 0,
            name: playerNames[0] || 'Host',
            character: charIds[0],
            characterData: charData,
            color: GAME_DATA.CHARACTER_COLORS[0],
            alive: true,
            location: 'landingZone',
            health: charData.health,
            maxHealth: charData.health,
            oxygen: GAME_DATA.CONFIG.startingOxygen,
            suffocating: false,
            actionDeck: this.createActionDeck(charIds[0]),
            actionHand: [],
            actionDiscard: [],
            backpack: [],
            handSlots: [null, null],
            armor: null,
            tacticalBelt: [null, null, null, null],
            seriousWounds: [],
            larva: false,
            hasDataToken: false,
            hasEscaped: false,
            hasHibernated: false,
            inLander: false,
            objectives: [],
            chosenObjective: null,
            passed: false,
            actionCardsDrawn: 0,
            peerId: null,
            connected: true,
            hasJoined: true
        });

        // Reserve remaining slots as placeholders (not yet joined)
        for (let i = 1; i < numPlayers; i++) {
            state.players.push({
                id: i,
                name: null, // null = not yet joined
                character: charIds[i],
                characterData: GAME_DATA.CHARACTERS[charIds[i]],
                color: GAME_DATA.CHARACTER_COLORS[i],
                alive: true, // alive but not connected — will be skipped until joined
                location: 'landingZone',
                health: GAME_DATA.CHARACTERS[charIds[i]].health,
                maxHealth: GAME_DATA.CHARACTERS[charIds[i]].health,
                oxygen: GAME_DATA.CONFIG.startingOxygen,
                suffocating: false,
                actionDeck: this.createActionDeck(charIds[i]),
                actionHand: [],
                actionDiscard: [],
                backpack: [],
                handSlots: [null, null],
                armor: null,
                tacticalBelt: [null, null, null, null],
                seriousWounds: [],
                larva: false,
                hasDataToken: false,
                hasEscaped: false,
                hasHibernated: false,
                inLander: false,
                objectives: [],
                chosenObjective: null,
                passed: false,
                actionCardsDrawn: 0,
                peerId: null,
                connected: false,
                hasJoined: false
            });
        }

        // Draw initial hands and objectives for all players (including unjoined)
        state.players.forEach(p => {
            for (let i = 0; i < GAME_DATA.CONFIG.handSize; i++) {
                this.drawActionCard(p);
            }
        });

        // Draw objectives
        state.players.forEach(p => {
            const missionObj = GAME_DATA.MISSION_OBJECTIVES[Math.floor(Math.random() * GAME_DATA.MISSION_OBJECTIVES.length)];
            const privateObj = GAME_DATA.PRIVATE_OBJECTIVES[Math.floor(Math.random() * GAME_DATA.PRIVATE_OBJECTIVES.length)];
            p.objectives = [missionObj, privateObj];
        });

        // Assign Mission Task
        const validTasks = GAME_DATA.MISSION_TASKS.filter(t => t.minPlayers <= numPlayers);
        state.missionTask = validTasks[Math.floor(Math.random() * validTasks.length)];

        // Assign random robot card
        state.robot.card = GAME_DATA.ROBOTS[Math.floor(Math.random() * GAME_DATA.ROBOTS.length)].id;

        // Set up initial room (Landing Zone is already discovered)
        state.rooms.landingZone = {
            id: 'landingZone',
            type: 'A',
            section: 'A',
            discovered: true,
            position: { x: 0, y: 0 },
            exits: {},
            markers: { fire: false, malfunction: false, secure: [] },
            intruders: []
        };
        state.mapGrid['0,0'] = { type: 'room', id: 'landingZone' };

        // Set Lander round (random between 3-8)
        state.landerRound = 3 + Math.floor(Math.random() * 6);

        this.state = state;
        this.log('Game created with ' + numPlayers + ' players');
        this.log('Mission Task: ' + state.missionTask.name);
        this.notify('gameCreated', state);
        return state;
    }

    createIntruderBag() {
        const bag = [];
        for (let i = 0; i < GAME_DATA.INTRUDER_BAG.blanks; i++) bag.push({ type: 'blank', value: 0 });
        for (let i = 0; i < GAME_DATA.INTRUDER_BAG.drones; i++) bag.push({ type: 'drone', value: 1 + Math.floor(Math.random() * 3) });
        for (let i = 0; i < GAME_DATA.INTRUDER_BAG.adults; i++) bag.push({ type: 'adult', value: 1 + Math.floor(Math.random() * 2) });
        for (let i = 0; i < GAME_DATA.INTRUDER_BAG.larvae; i++) bag.push({ type: 'larva', value: 1 });
        for (let i = 0; i < GAME_DATA.INTRUDER_BAG.queen; i++) bag.push({ type: 'queen', value: 0 });
        return shuffle(bag);
    }

    createActionDeck(charId) {
        // 10 action cards per character - simplified
        const deck = [];
        const actions = ['move','move','move','shoot','search','move','cautiousMove','shoot','useRoom','special'];
        for (let i = 0; i < 10; i++) {
            deck.push({ id: charId + '_action_' + i, type: 'action', action: actions[i] || 'move', character: charId });
        }
        return shuffle(deck);
    }

    // === CARD DRAWING ===
    drawActionCard(player) {
        if (player.actionDeck.length === 0) {
            // Reshuffle discard
            if (player.actionDiscard.length === 0) return;
            player.actionDeck = shuffle([...player.actionDiscard]);
            player.actionDiscard = [];
        }
        const card = player.actionDeck.pop();
        if (card) player.actionHand.push(card);
        return card;
    }

    drawItem(state, type) {
        const deck = state.itemDecks[type];
        if (deck.length === 0) {
            // Reshuffle discards
            if (state.itemDiscards[type].length === 0) return null;
            state.itemDecks[type] = shuffle([...state.itemDiscards[type]]);
            state.itemDiscards[type] = [];
        }
        return deck.pop();
    }

    drawIntruderAttack(state) {
        if (state.intruderAttackDeck.length === 0) {
            state.intruderAttackDeck = shuffle([...state.intruderAttackDiscard]);
            state.intruderAttackDiscard = [];
        }
        return state.intruderAttackDeck.pop();
    }

    drawSeriousWound(state) {
        if (state.seriousWoundDeck.length === 0) {
            state.seriousWoundDeck = shuffle([...state.seriousWoundDiscard]);
            state.seriousWoundDiscard = [];
        }
        return state.seriousWoundDeck.pop();
    }

    drawFromBag(state) {
        if (state.intruderBag.length === 0) return null;
        return state.intruderBag.pop();
    }

    // === GAME ROUND ===
    startRound() {
        const s = this.state;
        if (s.phase === 'setup' && s.players.some(p => !p.connected)) {
            this.log('Cannot start: every configured player slot must be filled');
            return false;
        }
        if (s.paused) return false;
        s.phase = 'playerPhase';
        s.currentPlayer = s.startingPlayer;
        s.actionsRemaining = GAME_DATA.CONFIG.actionsPerTurn;
        s.turnStep = 'action1';

        // Reset passed flags
        s.players.forEach(p => { p.passed = false; });

        this.log('=== Round ' + s.round + ' ===');
        this.notify('roundStart', { round: s.round });
        this.startPlayerTurn();
    }

    startPlayerTurn() {
        const s = this.state;
        if (s.paused) return;
        const player = s.players[s.currentPlayer];

        if (!player.alive || player.hasEscaped || player.hasHibernated || player.inLander) {
            this.nextPlayerOrPhase();
            return;
        }

        s.actionsRemaining = GAME_DATA.CONFIG.actionsPerTurn;
        s.turnStep = 'action1';
        this.log(this.charName(player) + "'s turn begins");
        this.notify('turnStart', { player: s.currentPlayer });
    }

    // === ACTIONS ===
    performAction(playerIndex, actionType, params = {}) {
        const s = this.state;
        const player = s.players[playerIndex];

        if (s.paused) {
            return { success: false, error: s.pauseReason || 'Game is paused while waiting for a player to rejoin' };
        }
        if (s.phase !== 'playerPhase' || s.currentPlayer !== playerIndex || !player.alive) {
            return { success: false, error: 'Not your turn' };
        }

        if (s.actionsRemaining <= 0) {
            return { success: false, error: 'No actions remaining' };
        }

        const actionCosts = { cautiousMove: 2, useRoom: 2 };
        const actionCost = actionType === 'pass' ? 0 : (actionCosts[actionType] || 1);
        const handBeforeAction = player.actionHand.slice();
        const discardBeforeAction = player.actionDiscard.slice();
        if (actionCost > 0) {
            const requested = Array.isArray(params.cardIndices) ? params.cardIndices :
                (params.cardIndex !== undefined ? [params.cardIndex] : []);
            const cardIndices = requested.length ? requested : player.actionHand
                .map((card, index) => ({ card, index }))
                .filter(({ card }) => card.type !== 'contamination')
                .slice(-actionCost)
                .map(({ index }) => index);
            if (cardIndices.length !== actionCost || new Set(cardIndices).size !== actionCost) {
                return { success: false, error: `Select ${actionCost} Action card${actionCost === 1 ? '' : 's'} to pay this action's cost` };
            }
            const cards = cardIndices.map(index => player.actionHand[index]);
            if (cards.some(card => !card || card.type === 'contamination')) {
                return { success: false, error: 'Only Action cards can pay an action cost' };
            }
            cardIndices.slice().sort((a, b) => b - a).forEach(index => {
                player.actionDiscard.push(player.actionHand.splice(index, 1)[0]);
            });
        }

        let result = { success: true };

        switch(actionType) {
            case 'move': result = this.actionMove(player, params); break;
            case 'cautiousMove': result = this.actionMove(player, { ...params, cautious: true }); break;
            case 'shoot': result = this.actionShoot(player, params); break;
            case 'burst': result = this.actionBurst(player, params); break;
            case 'melee': result = this.actionMelee(player, params); break;
            case 'useItem': result = this.actionUseItem(player, params); break;
            case 'useTacticalGear': result = this.actionUseTacticalGear(player, params); break;
            case 'useRoom': result = this.actionUseRoom(player, params); break;
            case 'search': result = this.actionSearch(player); break;
            case 'trade': result = this.actionTrade(player, params); break;
            case 'activateRobot': result = this.actionActivateRobot(player, params); break;
            case 'pass': result = this.actionPass(player, params); break;
            case 'sprint': result = this.actionSprint(player, params); break;
            case 'rest': result = this.actionRest(player); break;
            case 'reinforce': result = this.actionReinforce(player, params); break;
            case 'drill': result = this.actionDrill(player, params); break;
            case 'command': result = this.actionCommand(player, params); break;
            default: return { success: false, error: 'Unknown action' };
        }

        // An illegal/impossible action must not consume its payment. Do not
        // refund an action that resolved far enough to kill its actor.
        if (!result.success && player.alive) {
            player.actionHand = handBeforeAction;
            player.actionDiscard = discardBeforeAction;
        }

        // Opportunity attacks, noise rolls, melee responses, and other action
        // effects can kill the acting player. A dead player cannot take another
        // action or Pass, so relinquish the turn immediately even when the
        // action itself returned a failure.
        if (!player.alive) {
            s.actionsRemaining = 0;
            this.nextPlayerOrPhase();
            return result;
        }

        if (result.success && actionType !== 'pass') {
            s.actionsRemaining--;
        }

        // End of turn checks
        if (s.actionsRemaining <= 0 || actionType === 'pass') {
            this.endPlayerTurn(player);
        } else {
            s.turnStep = s.actionsRemaining === 1 ? 'action2' : 'action1';
            this.notify('actionComplete', { action: actionType, player: playerIndex, remaining: s.actionsRemaining });
        }

        return result;
    }

    endPlayerTurn(player) {
        const s = this.state;

        // Lose oxygen if in section with inactive life support
        const room = s.rooms[player.location];
        if (room) {
            const section = s.sections[room.section];
            if (section && !section.lifeSupport) {
                if (player.oxygen > 0) {
                    player.oxygen--;
                }
                if (player.oxygen === 0 && !player.suffocating) {
                    player.suffocating = true;
                    this.log(this.charName(player) + ' is suffocating!');
                } else if (player.suffocating) {
                    // Already suffocating — next oxygen loss kills
                    this.killPlayer(player, 'suffocation');
                    this.nextPlayerOrPhase();
                    return;
                }
            }
            // Lose health if in room with fire
            if (room.markers.fire) {
                this.damagePlayer(player, 1, 'fire');
                this.log(this.charName(player) + ' loses 1 Health from Fire');
            }
        }

        this.nextPlayerOrPhase();
    }

    nextPlayerOrPhase() {
        const s = this.state;
        if (s.paused) return;

        // Find next player who hasn't passed
        let next = s.currentPlayer;
        let found = false;
        for (let i = 1; i <= s.players.length; i++) {
            next = (s.currentPlayer + i) % s.players.length;
            const p = s.players[next];
            if (p.alive && !p.passed && !p.hasEscaped && !p.hasHibernated && !p.inLander) {
                found = true;
                break;
            }
        }

        if (found) {
            s.currentPlayer = next;
            this.startPlayerTurn();
        } else {
            // All players have acted or passed - go to Intruder Phase
            this.intruderPhase();
        }
    }

    // === INTRUDER PHASE ===
    intruderPhase() {
        const s = this.state;
        this.log('-- Intruder Phase --');
        this.notify('phaseChange', { phase: 'intruder' });

        // 1. Intruders Burning
        this.intrudersBurning();

        // 2. Intruder Attacks
        this.intruderAttacks();

        // Event Phase
        this.eventPhase();
    }

    intrudersBurning() {
        const s = this.state;
        // Each intruder in a room with fire takes 1 hit
        s.intruders.forEach(intruder => {
            if (intruder.location.type === 'room') {
                const room = s.rooms[intruder.location.id];
                if (room && room.markers.fire) {
                    intruder.hits = (intruder.hits || 0) + 1;
                    // Check if intruder dies from fire
                    const intruderData = GAME_DATA.INTRUDER_TYPES[intruder.type];
                    if (intruder.type === 'adult' || intruder.type === 'larva') {
                        if (intruder.hits >= 1) this.killIntruder(s, intruder);
                    } else if (intruder.type === 'drone') {
                        if (intruder.hits >= 2) this.killIntruder(s, intruder);
                    }
                }
            }
        });

        // Fire in Nest destroys 1 egg
        if (s.nest.eggs > 0 && !s.nest.destroyed) {
            const nestRoom = s.rooms.nest;
            if (nestRoom && nestRoom.markers.fire) {
                s.nest.eggs--;
                this.log('Fire discards 1 Egg in the Nest');
                if (s.nest.eggs === 0) {
                    s.nest.destroyed = true;
                    this.log('The Nest is destroyed!');
                }
            }
        }
    }

    intruderAttacks() {
        const s = this.state;
        // Each intruder in a room with a character attacks
        s.intruders.forEach(intruder => {
            if (intruder.location.type === 'room') {
                const room = s.rooms[intruder.location.id];
                if (room) {
                    const charactersInRoom = s.players.filter(p => p.alive && p.location === intruder.location.id);
                    if (charactersInRoom.length > 0) {
                        // Check for secure tokens
                        if (room.markers.secure && room.markers.secure.length > 0) {
                            room.markers.secure.pop();
                            this.log('Secure token prevents Intruder Attack in ' + room.id);
                            return;
                        }
                        // Attack first character in turn order
                        const target = charactersInRoom[0];
                        this.resolveIntruderAttack(s, intruder, target);
                    }
                }
            }
        });
    }

    resolveIntruderAttack(state, intruder, target) {
        // Larva attacks are special
        if (intruder.type === 'larva') {
            this.gainContamination(state, target);
            if (!target.larva) {
                target.larva = true;
                this.log(this.charName(target) + ' is infected with a Larva!');
            }
            return;
        }

        // Draw intruder attack card
        const attackCardId = this.drawIntruderAttack(state);
        const attackCard = GAME_DATA.INTRUDER_ATTACKS.find(a => a.id === attackCardId);
        if (!attackCard) return;

        const attack = attackCard[intruder.type] || attackCard.adult;
        this.log(intruder.type + ' attacks ' + this.charName(target) + ': ' + attack.text);

        // Resolve attack effect
        switch(attack.effect) {
            case 'lose1hp': this.damagePlayer(target, 1, 'intruder'); break;
            case 'lose2hp': this.damagePlayer(target, 2, 'intruder'); break;
            case 'lose3hp': this.damagePlayer(target, 3, 'intruder'); break;
            case 'lose4hp':
                if (this.isHeavilyInjured(target)) { this.killPlayer(target, 'intruder'); }
                else { this.damagePlayer(target, 4, 'intruder'); }
                break;
            case 'lose1hp_contam':
                this.damagePlayer(target, 1, 'intruder');
                this.gainContamination(state, target);
                break;
            case 'lose2hp_contam':
                this.damagePlayer(target, 2, 'intruder');
                this.gainContamination(state, target);
                break;
            case 'seriousWound':
                if (this.isHeavilyInjured(target)) {
                    this.killPlayer(target, 'intruder');
                } else {
                    this.gainSeriousWound(state, target);
                    if (intruder.type === 'queen') this.gainSeriousWound(state, target);
                }
                break;
            case 'seriousWound_contam':
                this.gainSeriousWound(state, target);
                this.gainContamination(state, target);
                if (intruder.type === 'queen') {
                    this.gainSeriousWound(state, target);
                }
                break;
            case 'infecting':
                this.gainContamination(state, target);
                if (!target.larva) {
                    target.larva = true;
                    this.log(this.charName(target) + ' is infected with a Larva!');
                }
                break;
        }

        state.intruderAttackDiscard.push(attackCardId);
    }

    // === EVENT PHASE ===
    eventPhase() {
        const s = this.state;
        this.log('-- Event Phase --');
        this.notify('phaseChange', { phase: 'event' });

        // Lander launch decision
        if (s.antiAircraft.lander.status === 'landed' || s.antiAircraft.lander.characters.length > 0) {
            // Check if anyone wants to launch - for now auto-launch if round >= landerRound
            if (s.round >= s.landerRound && s.antiAircraft.lander.status !== 'launched' && s.antiAircraft.lander.status !== 'destroyed') {
                this.resolveAntiAircraft(s);
            }
        }

        // Draw and resolve event card
        const eventId = s.eventDeck.pop();
        const event = GAME_DATA.EVENTS.find(e => e.id === eventId);
        if (event) {
            this.log('Event: ' + event.name);
            this.resolveEvent(s, event);
            s.eventDiscard.push(eventId);
        }

        // Bag development (add intruder tokens to bag based on round)
        this.bagDevelopment(s);

        // Cleanup phase
        this.cleanupPhase();
    }

    resolveEvent(state, event) {
        // 1. Move intruders in corridors to rooms
        this.moveCorridorIntruders(state);
        // 2. Move intruders in rooms to corridors
        this.moveRoomIntruders(state);

        // Specific event effects
        switch(event.id) {
            case 'ev1': // Reactor Overheating
                if (state.rooms.coolingSystem?.markers.fire || state.rooms.reactor?.markers.fire) {
                    this.activateAutodestruction(state);
                }
                if (state.rooms.coolingSystem) state.rooms.coolingSystem.markers.fire = true;
                if (state.rooms.reactor) state.rooms.reactor.markers.fire = true;
                state.eventDeck = shuffle([...state.eventDeck, ...state.eventDiscard]);
                state.eventDiscard = [];
                break;
            case 'ev8': // Hull Breach
                state.players.forEach(p => { if (p.alive) { if (p.oxygen > 0) p.oxygen--; } });
                break;
            case 'ev9': // Power Surge
                const sections = ['A','B','C'];
                const randSection = sections[Math.floor(Math.random() * 3)];
                if (state.sections[randSection].lifeSupport) {
                    state.sections[randSection].lifeSupport = false;
                    this.log('Life Support in Section ' + randSection + ' turned off');
                }
                break;
            case 'ev10': // Nest Awakening
                if (!state.nest.destroyed) state.nest.eggs = Math.min(state.nest.eggs + 1, 5);
                break;
            case 'ev12': // Infestation
                // Draw 2 intruder tokens and place in random corridors
                for (let i = 0; i < 2; i++) {
                    this.placeRandomIntruder(state);
                }
                break;
            case 'ev14': // Intruder Surge
                // Draw 3 intruder tokens and place them
                for (let i = 0; i < 3; i++) {
                    this.placeRandomIntruder(state);
                }
                break;
            case 'ev16': // Contamination Leak
                state.players.forEach(p => { if (p.alive) this.gainContamination(state, p); });
                break;
            case 'ev19': // Nest Defense
                // The physical game always has a Nest space, but this digital map
                // assigns the Nest to a slot only when it is explored. Reserve the
                // Drone while hidden rather than creating an off-map entity.
                if (!state.nest.destroyed && state.intruderPool.drone > 0) {
                    state.intruderPool.drone--;
                    if (state.rooms.nest) {
                        state.nest.pendingDrones++;
                        this.materializePendingNestOccupants(state);
                    } else {
                        state.nest.pendingDrones++;
                        this.log('A Drone is waiting in the undiscovered Nest');
                    }
                }
                break;
            case 'ev20': // Queen Awakening
                if (!state.queen.inPlay) {
                    state.queen.inPlay = true;
                    state.queen.location = { type: 'pending', id: 'nest' };
                    if (state.rooms.nest) {
                        this.materializePendingNestOccupants(state);
                        this.log('The Queen has awakened in the Nest!');
                    } else {
                        this.log('The Queen awakens in the undiscovered Nest');
                    }
                } else if (state.queen.location?.type === 'pending') {
                    this.log('The Queen remains in the undiscovered Nest');
                } else {
                    this.activateQueen(state);
                }
                break;
            // Other events: just the standard movement already handled
        }
        this.notify('eventResolved', { event: event.id });
    }

    materializePendingNestOccupants(state) {
        if (!state.rooms.nest) return;

        const pendingDrones = state.nest.pendingDrones || 0;
        for (let i = 0; i < pendingDrones; i++) {
            state.intruders.push({
                id: 'intruder_nest_' + Date.now() + '_' + i + '_' + Math.random(),
                type: 'drone',
                location: { type: 'room', id: 'nest' },
                hits: 0
            });
        }
        if (pendingDrones > 0) {
            state.nest.pendingDrones = 0;
            this.log((pendingDrones === 1 ? 'A Drone appears' : pendingDrones + ' Drones appear') + ' in the Nest!');
        }

        const queenPending = state.queen.inPlay && !state.queen.dead &&
            state.queen.location?.type === 'pending';
        if (queenPending) {
            state.queen.location = { type: 'room', id: 'nest' };
            if (!state.intruders.some(intruder => intruder.type === 'queen')) {
                state.intruders.push({
                    id: 'queen_intruder',
                    type: 'queen',
                    location: { type: 'room', id: 'nest' },
                    hits: state.queen.hits || 0
                });
            }
            this.log('The Queen appears in the Nest!');
        }
    }

    // Place a random intruder from the bag into a random corridor or room with a character
    placeRandomIntruder(state) {
        const token = this.drawFromBag(state);
        if (!token) return;
        
        // Try to place in a corridor with noise, or near a character
        const corridorsWithNoise = state.corridors.filter(c => c.noise);
        const roomsWithChars = Object.keys(state.rooms).filter(rid =>
            state.players.some(p => p.alive && p.location === rid)
        );
        
        let location, locationType;
        if (corridorsWithNoise.length > 0) {
            const c = corridorsWithNoise[Math.floor(Math.random() * corridorsWithNoise.length)];
            location = c.id;
            locationType = 'corridor';
            c.noise = false; // Resolve noise marker
            state.tokenPool.noise++;
        } else if (roomsWithChars.length > 0) {
            location = roomsWithChars[Math.floor(Math.random() * roomsWithChars.length)];
            locationType = 'room';
        } else {
            // Place in a random corridor
            if (state.corridors.length > 0) {
                const c = state.corridors[Math.floor(Math.random() * state.corridors.length)];
                location = c.id;
                locationType = 'corridor';
            } else {
                // No corridors yet — place at landing zone
                location = 'landingZone';
                locationType = 'room';
            }
        }
        
        this.resolveIntruderToken(state, token, location, locationType);
    }

    moveCorridorIntruders(state) {
        state.intruders.forEach(intruder => {
            if (intruder.location.type === 'corridor') {
                const corridor = state.corridors.find(c => c.id === intruder.location.id);
                if (corridor) {
                    // Move to adjacent room with closest character
                    const targetRoom = this.findClosestCharacterRoom(state, corridor);
                    if (targetRoom) {
                        intruder.location = { type: 'room', id: targetRoom };
                        intruder.hits = 0; // Clear hits when entering room
                        // Check for surprise attack
                        const charsInRoom = state.players.filter(p => p.alive && p.location === targetRoom);
                        if (charsInRoom.length > 0) {
                            const room = state.rooms[targetRoom];
                            if (room.markers.secure && room.markers.secure.length > 0) {
                                room.markers.secure.pop();
                            } else {
                                this.resolveIntruderAttack(state, intruder, charsInRoom[0]);
                            }
                        }
                    }
                }
            }
        });
    }

    moveRoomIntruders(state) {
        state.intruders.forEach(intruder => {
            if (intruder.location.type === 'room') {
                const room = state.rooms[intruder.location.id];
                if (room) {
                    const charsInRoom = state.players.filter(p => p.alive && p.location === intruder.location.id);
                    // Intruders stay in combat
                    if (charsInRoom.length === 0) {
                        // Move to adjacent corridor toward closest character
                        const targetCorridor = this.findClosestCharacterCorridor(state, room);
                        if (targetCorridor) {
                            intruder.location = { type: 'corridor', id: targetCorridor };
                        }
                    }
                }
            }
        });
    }

    findClosestCharacterRoom(state, corridor) {
        // Simplified: return first adjacent room with a character, else first adjacent room
        if (!corridor.room1 && !corridor.room2) return null;
        const rooms = [corridor.room1, corridor.room2].filter(r => r);
        for (const roomId of rooms) {
            const chars = state.players.filter(p => p.alive && p.location === roomId);
            if (chars.length > 0) return roomId;
        }
        return rooms[0] || null;
    }

    findClosestCharacterCorridor(state, room) {
        // Find adjacent corridors
        const adjacentCorridors = state.corridors.filter(c => c.room1 === room.id || c.room2 === room.id);
        if (adjacentCorridors.length === 0) return null;
        // Prefer corridor with noise or toward closest character
        return adjacentCorridors[0].id;
    }

    bagDevelopment(state) {
        // Add intruder tokens based on round number
        // Rounds 1-4: add 1 adult, 5-9: add 1 adult + 1 drone, 10+: add 2 adults + 1 drone
        const bag = state.intruderBag;
        if (state.round >= 10) {
            bag.push({ type: 'adult', value: 1 });
            bag.push({ type: 'adult', value: 1 });
            bag.push({ type: 'drone', value: 1 });
        } else if (state.round >= 5) {
            bag.push({ type: 'adult', value: 1 });
            bag.push({ type: 'drone', value: 1 });
        } else {
            bag.push({ type: 'adult', value: 1 });
        }
        shuffle(bag);
    }

    // === CLEANUP PHASE ===
    cleanupPhase() {
        const s = this.state;
        if (s.paused) return;
        this.log('-- Cleanup Phase --');
        this.notify('phaseChange', { phase: 'cleanup' });

        // 1. Starting player change
        s.startingPlayer = (s.startingPlayer + 1) % s.players.length;
        // Find next eligible player. A live game cannot advance while a joined
        // player is disconnected, so connectivity is not a turn-order filter.
        let attempts = 0;
        while (!s.players[s.startingPlayer].alive && attempts < s.players.length) {
            s.startingPlayer = (s.startingPlayer + 1) % s.players.length;
            attempts++;
        }

        // 2. Draw action cards — each player draws until they have 5 in hand
        // (rulebook p.15: "Each player draws Action cards from their deck
        //  until they have 5 cards in hand.")
        s.players.forEach(p => {
            if (p.alive && !p.hasEscaped && !p.hasHibernated) {
                while (p.actionHand.length < GAME_DATA.CONFIG.handSize) {
                    this.drawActionCard(p);
                }
            }
        });

        // 3. Time advancement
        s.round++;
        if (s.round > s.maxRounds) {
            this.endGame();
            return;
        }

        // Check autodestruction
        if (s.autodestruction.active && s.round >= s.autodestruction.token) {
            this.destroyFacility();
            return;
        }

        // Check if all players dead/escaped
        const activePlayers = s.players.filter(p => p.alive && !p.hasEscaped && !p.hasHibernated);
        if (activePlayers.length === 0) {
            this.endGame();
            return;
        }

        this.startRound();
    }

    // === ACTION IMPLEMENTATIONS ===
    actionMove(player, params) {
        const s = this.state;
        const targetRoomId = params.targetRoom;
        if (!targetRoomId) return { success: false, error: 'No target room' };

        const currentRoom = s.rooms[player.location];
        if (!currentRoom) return { success: false, error: 'Not in a room' };

        // Check if this is an exploration move (to an undiscovered area)
        const isExploration = params.explore || targetRoomId.startsWith('explore_');

        // Exploration must follow one of the six flat-top hex edges into an
        // empty, valid room bay. The UI filters targets, but the host is authoritative.
        if (isExploration) {
            const position = params.position;
            const isIntegerPosition = Number.isInteger(position?.x) && Number.isInteger(position?.y);
            const isInBounds = isIntegerPosition && GAME_DATA.CONFIG.boardSlots.some(slot =>
                slot.x === position.x && slot.y === position.y
            );
            if (!isInBounds) return { success: false, error: 'Destination is off the board' };

            const direction = GAME_DATA.CONFIG.directionBetween(currentRoom.position, position);
            if (!direction) return { success: false, error: 'Destination is not adjacent' };
            if (params.direction && params.direction !== direction.id) {
                return { success: false, error: 'Exit direction does not match destination' };
            }

            const occupied = Object.values(s.rooms).some(room =>
                room.position?.x === position.x && room.position?.y === position.y
            );
            if (occupied) return { success: false, error: 'Map space is already occupied' };
        }
        
        // For non-exploration moves, check corridor adjacency
        if (!isExploration) {
            const corridor = s.corridors.find(c =>
                (c.room1 === player.location && c.room2 === targetRoomId) ||
                (c.room2 === player.location && c.room1 === targetRoomId)
            );
            if (!corridor && !params.secretPassage) {
                return { success: false, error: 'Rooms not adjacent' };
            }
            // Check for closed doors
            if (corridor && corridor.door === 'closed') {
                return { success: false, error: 'Door is closed' };
            }
        }

        // For exploration, skip opportunity attacks (no corridor exists yet)

        // Resolve opportunity attacks from intruders in current room
        let attacks = 0;
        s.intruders.filter(i => i.location.type === 'room' && i.location.id === player.location).forEach(intruder => {
            if (attacks < 3) {
                this.resolveIntruderAttack(s, intruder, player);
                attacks++;
            }
        });
        // Only check corridor attacks for non-exploration moves
        if (!isExploration) {
            const corridor = s.corridors.find(c =>
                (c.room1 === player.location && c.room2 === targetRoomId) ||
                (c.room2 === player.location && c.room1 === targetRoomId)
            );
            if (corridor) {
                s.intruders.filter(i => i.location.type === 'corridor' && i.location.id === corridor.id).forEach(intruder => {
                    if (attacks < 3) {
                        this.resolveIntruderAttack(s, intruder, player);
                        attacks++;
                    }
                });
            }
        }

        if (!player.alive) return { success: false, error: 'Player died during movement' };

        // Check if target room is discovered
        const targetRoom = s.rooms[targetRoomId];
        if (targetRoom && targetRoom.discovered) {
            // Move to discovered room
            player.location = targetRoomId;
            if (params.cautious) {
                this.placeSecureToken(s, targetRoomId);
            }
            this.makeNoiseRoll(s, player);
        } else {
            // Exploration sequence
            this.explorationSequence(s, player, targetRoomId, params);
        }

        this.log(this.charName(player) + ' moves to ' + (targetRoom ? targetRoom.id || targetRoomId : targetRoomId));
        this.notify('playerMoved', { player: player.id, room: targetRoomId });
        return { success: true };
    }

    explorationSequence(state, player, targetRoomId, params) {
        // Draw exploration card
        const exCardId = state.explorationDeck.pop();
        const exCard = GAME_DATA.EXPLORATION_CARDS.find(e => e.id === exCardId);
        if (!exCard) return;

        // Determine room type based on section
        const section = params.section || this.getSectionForPosition(state, params.position);
        const roomType = exCard.roomType;
        const pool = state.undiscoveredRooms[roomType === '?' ? '?' : section] || state.undiscoveredRooms['?'];
        const newRoomId = pool.length > 0 ? pool.shift() : state.undiscoveredRooms['?'].shift();

        // Place room
        state.rooms[newRoomId] = {
            id: newRoomId,
            type: roomType,
            section: section,
            discovered: true,
            position: params.position || { x: 0, y: 0 },
            exits: {},
            markers: { fire: false, malfunction: false, secure: [] },
            intruders: []
        };
        state.mapGrid[params.position.x + ',' + params.position.y] = { type: 'room', id: newRoomId };
        if (newRoomId === 'nest') {
            this.materializePendingNestOccupants(state);
        }

        // Add a graph edge. Each room records the edge under the compass-facing
        // edge of its hexagon; the corridor preserves both orientations.
        const sourceRoomId = player.location;
        const sourceRoom = state.rooms[sourceRoomId];
        const exitDirection = GAME_DATA.CONFIG.directionBetween(sourceRoom.position, params.position);
        const newCorridor = {
            id: 'corridor_' + Date.now() + '_' + Math.random(),
            value: 1 + Math.floor(Math.random() * 4),
            room1: sourceRoomId,
            room2: newRoomId,
            directionFromRoom1: exitDirection.id,
            directionFromRoom2: exitDirection.opposite,
            door: 'open',
            noise: false,
            intruders: [],
            reinforced: false
        };
        state.corridors.push(newCorridor);
        sourceRoom.exits ||= {};
        sourceRoom.exits[exitDirection.id] = newCorridor.id;
        state.rooms[newRoomId].exits[exitDirection.opposite] = newCorridor.id;

        // Move player
        player.location = newRoomId;
        if (params.cautious) {
            this.placeSecureToken(state, newRoomId);
        }

        // Entrance effect
        if (exCard.entrance === 'noiseRoll') {
            this.makeNoiseRoll(state, player);
        } else if (exCard.entrance === 'closeDoors') {
            // Close all doors around room
            state.corridors.forEach(c => {
                if (c.room1 === newRoomId || c.room2 === newRoomId) {
                    c.door = 'closed';
                }
            });
        }

        // Reveal robot if hibernatorium is connected
        if (newRoomId === 'hibernatorium' && !state.robot.revealed) {
            state.robot.revealed = true;
            this.log('Robot revealed: ' + (GAME_DATA.ROBOTS.find(r => r.id === state.robot.card)?.name || 'Unknown'));
        }

        state.explorationDiscard.push(exCardId);
        this.log(this.charName(player) + ' discovers ' + newRoomId);
        this.notify('roomDiscovered', { room: newRoomId, position: params.position });
    }

    getSectionForPosition(state, position) {
        if (!position) return 'A';
        if (position.x < 3) return 'A';
        if (position.x < 6) return 'B';
        return 'C';
    }

    makeNoiseRoll(state, player) {
        const roll = 1 + Math.floor(Math.random() * 10); // d10
        const room = state.rooms[player.location];
        if (!room) return;

        if (roll <= 4) {
            // Find corridors with this value adjacent to the room
            const matchingCorridors = state.corridors.filter(c =>
                (c.room1 === player.location || c.room2 === player.location) &&
                c.value === roll && !c.reinforced
            );
            matchingCorridors.forEach(corridor => {
                if (corridor.intruders.length > 0) {
                    // Largest intruder moves to player's room
                    const intruder = corridor.intruders
                        .filter(i => i)
                        .sort((a,b) => this.intruderSize(b) - this.intruderSize(a))[0];
                    if (intruder) {
                        intruder.location = { type: 'room', id: player.location };
                        corridor.intruders = corridor.intruders.filter(i => i !== intruder);
                        // Surprise attack
                        this.resolveIntruderAttack(state, intruder, player);
                    }
                } else if (corridor.noise) {
                    // Resolve noise marker
                    this.resolveNoise(state, corridor);
                } else {
                    // Place noise marker
                    if (state.tokenPool.noise > 0) {
                        corridor.noise = true;
                        state.tokenPool.noise--;
                    }
                }
            });
        } else {
            // Hazard result - draw from intruder bag
            const token = this.drawFromBag(state);
            if (token) {
                this.resolveIntruderToken(state, token, player.location, 'room');
            }
        }
        this.notify('noiseRoll', { player: player.id, roll });
    }

    resolveNoise(state, corridor) {
        corridor.noise = false;
        state.tokenPool.noise++;
        const token = this.drawFromBag(state);
        if (token) {
            this.resolveIntruderToken(state, token, corridor.id, 'corridor');
        }
    }

    resolveIntruderToken(state, token, locationId, locationType) {
        if (token.type === 'blank') {
            state.intruderBag.push(token); // Blank goes back
            shuffle(state.intruderBag);
            return;
        }

        if (token.type === 'queen') {
            // Queen activation
            if (!state.queen.inPlay) {
                state.queen.inPlay = true;
                state.queen.location = { type: 'room', id: 'nest' };
                this.log('The Queen appears in the Nest!');
            } else {
                this.activateQueen(state);
            }
            return;
        }

        // Place intruders
        const count = token.value || 1;
        for (let i = 0; i < count; i++) {
            if (state.intruderPool[token.type] > 0) {
                state.intruders.push({
                    id: 'intruder_' + Date.now() + '_' + Math.random(),
                    type: token.type,
                    location: { type: locationType, id: locationId },
                    hits: 0
                });
                state.intruderPool[token.type]--;
            }
        }

        // Surprise attack if placed in room with character
        if (locationType === 'room') {
            const charsInRoom = state.players.filter(p => p.alive && p.location === locationId);
            if (charsInRoom.length > 0) {
                const intruder = state.intruders.find(i => i.location.type === 'room' && i.location.id === locationId);
                if (intruder) {
                    const room = state.rooms[locationId];
                    if (room.markers.secure && room.markers.secure.length > 0) {
                        room.markers.secure.pop();
                    } else {
                        this.resolveIntruderAttack(state, intruder, charsInRoom[0]);
                    }
                }
            }
        }

        this.log(token.type + '(s) appear' + (count > 1 ? ' (' + count + ')' : ''));
        this.notify('intruderPlaced', { type: token.type, count, location: locationId, locationType });
    }

    activateQueen(state) {
        // Ensure Queen is in the intruders array
        let queenIntruder = state.intruders.find(i => i.type === 'queen');
        if (!queenIntruder && state.queen.inPlay) {
            // Place Queen — prefer the Nest room if discovered, else a random discovered room
            let queenRoom = 'nest';
            if (!state.rooms.nest) {
                const discoveredRooms = Object.keys(state.rooms).filter(r => r !== 'landingZone');
                if (discoveredRooms.length > 0) {
                    queenRoom = discoveredRooms[Math.floor(Math.random() * discoveredRooms.length)];
                }
            }
            state.queen.location = { type: 'room', id: queenRoom };
            queenIntruder = {
                id: 'queen_intruder',
                type: 'queen',
                location: { type: 'room', id: queenRoom },
                hits: 0
            };
            state.intruders.push(queenIntruder);
            this.log('The Queen appears in ' + queenRoom + '!');
        }

        if (queenIntruder) {
            // Attack or move
            const charsInRoom = state.players.filter(p => p.alive && p.location === queenIntruder.location.id);
            if (charsInRoom.length > 0 && queenIntruder.location.type === 'room') {
                const room = state.rooms[queenIntruder.location.id];
                if (room && room.markers.secure && room.markers.secure.length > 0) {
                    room.markers.secure.pop();
                    this.log('Secure token prevents Queen Attack');
                } else {
                    this.resolveIntruderAttack(state, queenIntruder, charsInRoom[0]);
                }
            } else {
                // Move toward closest character
                const currentRoom = state.rooms[queenIntruder.location.id];
                if (currentRoom) {
                    const targetCorridor = this.findClosestCharacterCorridor(state, currentRoom);
                    if (targetCorridor) {
                        queenIntruder.location = { type: 'corridor', id: targetCorridor };
                        this.log('The Queen moves toward the crew');
                    }
                }
            }
        }
        this.log('Queen activates!');
    }

    actionShoot(player, params) {
        const s = this.state;
        const weapon = player.handSlots.find(h => h && GAME_DATA.ITEMS[h]?.traits?.includes('RANGED WEAPON'));
        if (!weapon) return { success: false, error: 'No ranged weapon equipped' };

        const targetIntruder = s.intruders.find(i => i.location.type === 'room' && i.location.id === player.location && i.id === params.targetId);
        if (!targetIntruder) return { success: false, error: 'No valid target in room' };

        // Deal 1 hit
        targetIntruder.hits = (targetIntruder.hits || 0) + 1;

        // Roll shoot die (d8)
        const roll = 1 + Math.floor(Math.random() * 8);
        this.log(this.charName(player) + ' shoots! Roll: ' + roll);

        if (roll === 8 || roll <= targetIntruder.hits) {
            // Critical or enough hits
            if (targetIntruder.type === 'drone' && targetIntruder.hits < 2) {
                // Drone needs 2 hits in room
            } else {
                this.killIntruder(s, targetIntruder);
                this.log(targetIntruder.type + ' killed!');
            }
        } else if (roll === 1) {
            // Lost bullets - spend ammo
            this.spendAmmo(player, weapon);
        }

        this.notify('shootResolved', { player: player.id, roll, target: targetIntruder.id });
        return { success: true };
    }

    actionBurst(player, params) {
        const s = this.state;
        const weapon = player.handSlots.find(h => h && GAME_DATA.ITEMS[h]?.traits?.includes('RANGED WEAPON'));
        if (!weapon) return { success: false, error: 'No ranged weapon equipped' };

        const corridor = s.corridors.find(c => c.id === params.corridorId);
        if (!corridor) return { success: false, error: 'No valid corridor' };

        // Must spend ammo
        if (!this.spendAmmo(player, weapon)) {
            return { success: false, error: 'No ammo' };
        }

        // Roll burst die (d6)
        const roll = 1 + Math.floor(Math.random() * 6);
        const hits = roll === 6 ? 4 : roll; // 6 is both 4 hits + special
        this.log(this.charName(player) + ' bursts! Roll: ' + roll + ' (' + hits + ' hits)');

        // Apply hits to intruders in corridor
        const intrudersInCorridor = s.intruders.filter(i => i.location.type === 'corridor' && i.location.id === corridor.id);
        let remainingHits = hits;
        for (const intruder of intrudersInCorridor) {
            if (remainingHits <= 0) break;
            const intruderData = GAME_DATA.INTRUDER_TYPES[intruder.type];
            if (intruder.type === 'adult' || intruder.type === 'larva') {
                this.killIntruder(s, intruder);
                remainingHits--;
            } else if (intruder.type === 'drone') {
                if (remainingHits >= 2) {
                    this.killIntruder(s, intruder);
                    remainingHits -= 2;
                }
            } else if (intruder.type === 'queen') {
                this.damageQueen(s, remainingHits);
                remainingHits = 0;
            }
        }

        this.notify('burstResolved', { player: player.id, roll, corridor: corridor.id });
        return { success: true };
    }

    actionMelee(player, params) {
        const s = this.state;
        const target = s.intruders.find(i => i.location.type === 'room' && i.location.id === player.location && i.id === params.targetId);
        if (!target) return { success: false, error: 'No valid target' };

        // Gain contamination
        this.gainContamination(s, player);

        // Deal 1 hit
        target.hits = (target.hits || 0) + 1;

        // Roll
        const roll = 1 + Math.floor(Math.random() * 8);
        this.log(this.charName(player) + ' melee attacks! Roll: ' + roll);

        if (roll === 8 || (roll >= 2 && roll <= 5 && roll <= target.hits)) {
            if (target.type === 'drone' && target.hits < 2) {
                // Drone needs 2 hits
            } else {
                this.killIntruder(s, target);
                this.log(target.type + ' killed!');
            }
        } else if (roll <= 1) {
            // Ineffective - nothing happens
        }

        // Intruder response if not dead
        if (s.intruders.includes(target)) {
            // Player can prevent by placing malfunction on weapon
            // For now, resolve attack
            this.resolveIntruderAttack(s, target, player);
        }

        return { success: true };
    }

    actionSearch(player) {
        const s = this.state;
        const room = s.rooms[player.location];
        if (!room) return { success: false, error: 'Not in a room' };

        const roomData = GAME_DATA.ROOMS[room.id];
        if (!roomData || !roomData.itemIcons) return { success: false, error: 'No items in this room' };

        // Draw items for each icon (blue items map to support equipment / green deck)
        const drawnItems = [];
        roomData.itemIcons.forEach(type => {
            // 'blue' items are not standard item deck types - skip them in search
            // (they represent support equipment found through other means)
            if (type === 'blue') return;
            const itemId = this.drawItem(s, type);
            if (itemId) drawnItems.push({ id: itemId, type });
        });

        if (drawnItems.length === 0) return { success: false, error: 'No searchable items in this room' };

        // For now, auto-keep the first item (UI should present choice)
        this.notify('searchResult', { player: player.id, items: drawnItems, room: room.id });

        // Auto-pick first for simplicity - UI will handle choice
        const picked = drawnItems[0];
        this.addItemToPlayer(player, picked.id);
        drawnItems.slice(1).forEach(item => {
            s.itemDiscards[item.type].push(item.id);
        });

        this.log(this.charName(player) + ' searches and finds ' + (GAME_DATA.ITEMS[picked.id]?.name || picked.id));
        return { success: true };
    }

    actionUseItem(player, params) {
        const s = this.state;
        const item = player.backpack.find(i => i === params.itemId) ||
                     player.handSlots.find(h => h === params.itemId);
        if (!item) return { success: false, error: 'Item not found' };

        const itemData = GAME_DATA.ITEMS[item];
        if (!itemData) return { success: false, error: 'Unknown item' };

        this.log(this.charName(player) + ' uses ' + itemData.name);
        this.notify('itemUsed', { player: player.id, item: item });

        // Simplified item effects
        if (itemData.name === 'Medpack' || itemData.name === 'Field Medkit') {
            this.healPlayer(player, 2);
        } else if (itemData.name === 'Oxygen Tank') {
            player.oxygen = Math.min(player.oxygen + 3, 7);
        } else if (itemData.name === 'Duct Tape') {
            // Discard malfunction - UI will need to specify where
            this.log(this.charName(player) + ' uses Duct Tape to discard a Malfunction');
        }

        // Discard one-use items
        if (itemData.traits && itemData.traits.includes('ONE USE ONLY')) {
            player.backpack = player.backpack.filter(i => i !== item);
            player.handSlots = player.handSlots.map(h => h === item ? null : h);
            s.itemDiscards[itemData.type].push(item);
        }

        return { success: true };
    }

    actionUseTacticalGear(player, params) {
        const beltIndex = player.tacticalBelt.findIndex(token => token === params.tokenType);
        if (beltIndex === -1) return { success: false, error: 'Tactical Gear token not owned' };
        player.tacticalBelt[beltIndex] = null;
        const s = this.state;
        if (s.tokenPool[params.tokenType] !== undefined) s.tokenPool[params.tokenType]++;
        // Use a tactical gear token
        if (params.tokenType === 'medpack') {
            this.healPlayer(player, 2);
            this.log(this.charName(player) + ' uses Medpack token');
        } else if (params.tokenType === 'oxygen') {
            player.oxygen = Math.min(player.oxygen + 3, 7);
            this.log(this.charName(player) + ' uses Oxygen token');
        } else if (params.tokenType === 'grenade') {
            // Roll burst + 2 on adjacent corridor
            const roll = 1 + Math.floor(Math.random() * 6) + 2;
            this.log(this.charName(player) + ' throws Grenade (' + roll + ' hits)');
            // Apply to corridor (UI will specify)
        }
        return { success: true };
    }

    actionUseRoom(player, params) {
        const s = this.state;
        const room = s.rooms[player.location];
        if (!room) return { success: false, error: 'Not in a room' };

        const roomData = GAME_DATA.ROOMS[room.id];
        if (!roomData) return { success: false, error: 'Unknown room' };

        // Check for malfunction
        if (room.markers.malfunction) {
            return { success: false, error: 'Room has malfunction' };
        }

        // Resolve room effect
        const effect = GAME_DATA.ROOM_EFFECTS[room.id];
        this.log(this.charName(player) + ' uses ' + roomData.name);
        this.notify('roomUsed', { player: player.id, room: room.id });

        // Simplified room effects
        switch(room.id) {
            case 'landingZone':
                if (s.antiAircraft.lander.status === 'landed') {
                    player.inLander = true;
                    s.antiAircraft.lander.characters.push(player.id);
                    this.log(this.charName(player) + ' gets into the Lander');
                } else {
                    // Gain tactical gear tokens
                    if (s.tokenPool.ammo > 0) { this.addTacticalGear(player, 'ammo'); s.tokenPool.ammo--; }
                    if (s.tokenPool.grenade > 0) { this.addTacticalGear(player, 'grenade'); s.tokenPool.grenade--; }
                    this.makeNoiseRoll(s, player);
                }
                break;
            case 'armory':
                if (s.tokenPool.ammo > 0) { this.addTacticalGear(player, 'ammo'); s.tokenPool.ammo--; }
                if (s.tokenPool.grenade > 0) { this.addTacticalGear(player, 'grenade'); s.tokenPool.grenade--; }
                break;
            case 'surgeryRoom':
                if (player.seriousWounds.length > 0) {
                    player.seriousWounds.pop();
                    this.log(this.charName(player) + ' discards a Serious Wound');
                } else if (player.larva) {
                    player.larva = false;
                    this.log(this.charName(player) + ' discards Larva from Character board');
                }
                break;
            case 'lifeSupportControlA':
            case 'lifeSupportControlB':
            case 'lifeSupportControlC':
                const section = room.id.charAt(room.id.length - 1);
                s.sections[section].lifeSupport = !s.sections[section].lifeSupport;
                this.log('Life Support in Section ' + section + ' toggled');
                break;
            case 'serverRoom':
                player.hasDataToken = true;
                this.log(this.charName(player) + ' gains a Data token');
                break;
            case 'nest':
                if (s.nest.eggs > 0 && !s.nest.destroyed) {
                    s.nest.eggs--;
                    this.addItemToPlayer(player, 'egg');
                    this.log(this.charName(player) + ' picks up an Egg');
                    if (s.nest.eggs === 0) {
                        s.nest.destroyed = true;
                        this.log('The Nest is destroyed!');
                    }
                }
                break;
            case 'reactor':
                // Shut down reactor - turn off all life support
                s.sections.A.lifeSupport = false;
                s.sections.B.lifeSupport = false;
                s.sections.C.lifeSupport = false;
                s.autodestruction.active = false;
                s.antiAircraft.resolved = true;
                // Remove all fire and malfunction
                Object.values(s.rooms).forEach(r => { r.markers.fire = false; r.markers.malfunction = false; });
                this.log('Reactor shut down! All systems powered off.');
                break;
            case 'escapeShuttle':
                // Make noise roll, if no intruder in room, escape
                this.makeNoiseRoll(s, player);
                const intrudersInRoom = s.intruders.filter(i => i.location.type === 'room' && i.location.id === 'escapeShuttle');
                if (intrudersInRoom.length === 0) {
                    player.hasEscaped = true;
                    this.log(this.charName(player) + ' escapes via Escape Shuttle!');
                }
                break;
            case 'hibernatorium':
                if (s.sections.B.lifeSupport && s.rooms.hibernatorium && !s.rooms.hibernatorium.markers.malfunction) {
                    this.makeNoiseRoll(s, player);
                    const intruders = s.intruders.filter(i => i.location.type === 'room' && i.location.id === 'hibernatorium');
                    if (intruders.length === 0) {
                        player.hasHibernated = true;
                        this.log(this.charName(player) + ' Hibernates');
                    }
                }
                break;
            case 'coolingSystem':
                this.activateAutodestruction(s);
                break;
            case 'sprinklersControl':
                Object.values(s.rooms).forEach(r => { r.markers.fire = false; });
                this.log('Sprinklers put out all fires');
                break;
            case 'shelter':
                // Per rulebook: Only if you are not infected with a Larva:
                // Take all Contaminations from your hand and remove them
                // from the game without scanning.
                if (!player.larva) {
                    const removed = player.actionHand.filter(c => c.type === 'contamination');
                    player.actionHand = player.actionHand.filter(c => c.type !== 'contamination');
                    // Remove from game — return to the contamination discard
                    // (not the player's discard pile) so they never re-enter
                    // the Action deck.
                    removed.forEach(c => s.contaminationDiscard.push(c.id));
                    if (removed.length > 0) {
                        this.log(this.charName(player) + ' removes ' + removed.length + ' Contamination(s) at the Shelter');
                    }
                }
                break;
        }

        return { success: true };
    }

    actionTrade(player, params) {
        const s = this.state;
        const targetPlayer = s.players[params.targetPlayer];
        if (!targetPlayer || targetPlayer.location !== player.location) {
            return { success: false, error: 'Target not in same room' };
        }
        const itemId = params.itemId;
        const isBackpackItem = player.backpack.includes(itemId);
        const handIndex = player.handSlots.indexOf(itemId);
        if (!isBackpackItem && handIndex === -1) {
            return { success: false, error: 'Item not owned by trading Character' };
        }
        const itemData = GAME_DATA.ITEMS[itemId];
        if (!itemData) return { success: false, error: 'Unknown item' };
        if (isBackpackItem) player.backpack.splice(player.backpack.indexOf(itemId), 1);
        else player.handSlots[handIndex] = null;
        if (!this.addItemToPlayer(targetPlayer, itemId)) {
            if (isBackpackItem) player.backpack.push(itemId);
            else player.handSlots[handIndex] = itemId;
            return { success: false, error: 'Recipient cannot carry that item' };
        }
        this.log(this.charName(player) + ' trades with ' + this.charName(targetPlayer));
        this.notify('tradeCompleted', { player: player.id, target: params.targetPlayer, item: itemId });
        return { success: true };
    }

    actionActivateRobot(player, params) {
        const s = this.state;
        const room = s.rooms[player.location];
        if (!room) return { success: false, error: 'Not in a room' };

        const roomData = GAME_DATA.ROOMS[room.id];
        const hasComputer = roomData?.computer;
        const robotInRoom = s.robot.location === player.location;

        if (!robotInRoom && !hasComputer) {
            return { success: false, error: 'No robot and no computer for remote activation' };
        }

        if (!robotInRoom && hasComputer && !player.hasDataToken) {
            // Need to discard extra card
            if (player.actionHand.length < 2) {
                return { success: false, error: 'Not enough cards for remote activation' };
            }
            const extraCard = player.actionHand.pop();
            player.actionDiscard.push(extraCard);
        }

        if (s.robot.malfunction) return { success: false, error: 'Robot is malfunctioning' };

        // Execute robot action
        const robotCard = GAME_DATA.ROBOTS.find(r => r.id === s.robot.card);
        if (robotCard) {
            this.log(this.charName(player) + ' activates Robot: ' + robotCard.name);
            // Simplified - just move robot or perform effect
            if (params.moveTo) {
                s.robot.location = params.moveTo;
            }
        }
        this.notify('robotActivated', { player: player.id, robot: s.robot.card });
        return { success: true };
    }

    actionPass(player, params = {}) {
        const s = this.state;
        // On Pass, the Character may discard any chosen subset of Action and
        // Contamination cards. Omitted selection means discard none.
        const selected = Array.isArray(params.cardIndices) ? params.cardIndices : [];
        if (new Set(selected).size !== selected.length || selected.some(index => !Number.isInteger(index) || index < 0 || index >= player.actionHand.length)) {
            return { success: false, error: 'Invalid Pass discard selection' };
        }
        player.passed = true;
        selected.slice().sort((a, b) => b - a).forEach(index => {
            player.actionDiscard.push(player.actionHand.splice(index, 1)[0]);
        });
        this.log(this.charName(player) + ' passes');
        this.notify('playerPassed', { player: player.id });
        return { success: true };
    }

    actionSprint(player, params) {
        // Recon ability: Move, then optionally spend 1 oxygen to move again
        const result = this.actionMove(player, params);
        if (result.success && player.oxygen > 0 && params.moveAgain) {
            player.oxygen--;
            this.actionMove(player, { ...params, targetRoom: params.targetRoom2 });
        }
        return result;
    }

    actionRest(player) {
        // Medical Support: Draw cards and infection check
        const s = this.state;
        this.drawActionCard(player);
        this.drawActionCard(player);
        this.log(this.charName(player) + ' rests and draws 2 cards');
        // Infection check
        this.infectionProcedure(s, player);
        return { success: true };
    }

    actionReinforce(player, params) {
        const s = this.state;
        const corridor = s.corridors.find(c => c.id === params.corridorId);
        if (!corridor || corridor.intruders.length > 0) {
            return { success: false, error: 'Corridor not empty' };
        }
        corridor.reinforced = true;
        corridor.value = 0; // Reinforced corridors have value 0
        if (corridor.noise) { corridor.noise = false; s.tokenPool.noise++; }
        this.log(this.charName(player) + ' reinforces an empty Corridor');
        return { success: true };
    }

    actionDrill(player, params) {
        // Combat Engineer: drill a new corridor
        const s = this.state;
        // Simplified - create a new exploration opportunity
        this.log(this.charName(player) + ' drills a new corridor');
        this.notify('drillComplete', { player: player.id });
        return { success: true };
    }

    actionCommand(player, params) {
        // Officer: command a lower-rank character to perform an action
        const s = this.state;
        const target = s.players[params.targetPlayer];
        if (!target || !target.alive) return { success: false, error: 'Invalid target' };

        const targetChar = GAME_DATA.CHARACTERS[target.character];
        if (targetChar.rank >= GAME_DATA.CHARACTERS[player.character].rank) {
            return { success: false, error: 'Target must be lower rank' };
        }
        // Target performs an extra move action
        this.log(this.charName(player) + ' commands ' + this.charName(target) + ' to move');
        this.actionMove(target, { targetRoom: params.targetRoom });
        return { success: true };
    }

    // === HELPER METHODS ===
    placeSecureToken(state, roomId) {
        const room = state.rooms[roomId];
        if (!room) return;
        if (GAME_DATA.ROOMS[roomId]?.cannotSecure) return;
        if (room.markers.secure.length >= 3) return;
        if (state.tokenPool.secure <= 0) return;
        room.markers.secure.push(true);
        state.tokenPool.secure--;
    }

    damagePlayer(player, amount, source) {
        // Check armor
        if (player.armor && amount > 0) {
            const armorData = GAME_DATA.ITEMS[player.armor];
            if (armorData && armorData.traits?.includes('ARMOR')) {
                // Armor absorbs - discard armor and reduce damage
                player.armor = null;
                // Armor prevents damage to the heavily injured section
                this.log(this.charName(player) + "'s armor breaks");
                // Continue applying remaining damage
            }
        }

        player.health -= amount;
        if (player.health <= 0) {
            this.killPlayer(player, source);
        }
        this.notify('playerDamaged', { player: player.id, amount, source });
    }

    healPlayer(player, amount) {
        player.health = Math.min(player.health + amount, player.maxHealth);
        this.notify('playerHealed', { player: player.id, amount });
    }

    killPlayer(player, cause) {
        player.alive = false;
        // Drop all items
        player.backpack = [];
        player.handSlots = [null, null];
        player.armor = null;
        player.tacticalBelt = [null, null, null, null];
        this.log(this.charName(player) + ' dies (' + cause + ')');
        this.notify('playerDied', { player: player.id, cause });
    }

    isHeavilyInjured(player) {
        return player.health <= Math.floor(player.maxHealth / 3);
    }

    isInjured(player) {
        return player.health <= Math.floor(player.maxHealth * 2 / 3);
    }

    gainContamination(state, player) {
        if (state.contaminationDeck.length === 0) {
            state.contaminationDeck = shuffle([...state.contaminationDiscard]);
            state.contaminationDiscard = [];
        }
        const cardId = state.contaminationDeck.pop();
        if (cardId) {
            // Per rulebook p.36: gained Contamination cards are placed in the
            // Character's discard pile. They share the back with Action cards
            // and get shuffled into the Action deck on reshuffle.
            player.actionDiscard.push({ id: cardId, type: 'contamination' });
            this.log(this.charName(player) + ' gains 1 Contamination');
            this.notify('contaminationGained', { player: player.id });
        }
    }

    gainSeriousWound(state, player) {
        const woundId = this.drawSeriousWound(state);
        if (woundId) {
            player.seriousWounds.push(woundId);
            this.log(this.charName(player) + ' gains a Serious Wound');
        }
    }

    killIntruder(state, intruder) {
        state.intruders = state.intruders.filter(i => i !== intruder);
        if (intruder.type === 'queen') {
            state.queen.dead = true;
            this.log('The Queen is dead!');
        } else {
            state.intruderPool[intruder.type]++;
        }
        this.notify('intruderKilled', { type: intruder.type, id: intruder.id });
    }

    damageQueen(state, hits) {
        state.queen.hits += hits;
        this.log('Queen takes ' + hits + ' Hits (total: ' + state.queen.hits + ')');
        while (state.queen.hits >= GAME_DATA.CONFIG.queenHitsMax) {
            state.queen.hits -= GAME_DATA.CONFIG.queenHitsMax;
            // Draw queen health card
            if (state.queenHealthDeck.length === 0) {
                state.queen.dead = true;
                this.log('The Queen is dead!');
                return;
            }
            const qhCardId = state.queenHealthDeck.pop();
            const qhCard = GAME_DATA.QUEEN_HEALTH_CARDS.find(c => c.id === qhCardId);
            if (qhCard) {
                state.queen.healthCardsRemaining--;
                // Discard additional cards
                for (let i = 0; i < qhCard.discard; i++) {
                    if (state.queenHealthDeck.length > 0) {
                        state.queenHealthDeck.pop();
                        state.queen.healthCardsRemaining--;
                    }
                }
                this.log('Queen Health card: ' + qhCard.text);
                if (state.queen.healthCardsRemaining <= 0) {
                    state.queen.dead = true;
                    this.log('The Queen is dead!');
                    return;
                }
            }
        }
    }

    spendAmmo(player, weaponId) {
        // Find ammo on weapon
        const item = GAME_DATA.ITEMS[weaponId];
        if (!item) return false;
        if (item.traits?.includes('REQUIRES NO AMMO')) return true;

        // Check tactical belt and weapon slots
        for (let i = 0; i < player.tacticalBelt.length; i++) {
            if (player.tacticalBelt[i] === 'ammo') {
                // Ammo can be spent twice (full -> half -> gone)
                player.tacticalBelt[i] = 'ammo_half';
                return true;
            } else if (player.tacticalBelt[i] === 'ammo_half') {
                player.tacticalBelt[i] = null;
                return true;
            }
        }
        return false;
    }

    addTacticalGear(player, type) {
        for (let i = 0; i < player.tacticalBelt.length; i++) {
            if (player.tacticalBelt[i] === null) {
                player.tacticalBelt[i] = type;
                return true;
            }
        }
        return false;
    }

    addItemToPlayer(player, itemId) {
        const itemData = GAME_DATA.ITEMS[itemId];
        if (!itemData) return false;

        if (itemData.traits?.includes('HEAVY')) {
            // Place in hand slot
            const emptySlot = player.handSlots.indexOf(null);
            if (emptySlot === -1) {
                return false;
            }
            player.handSlots[emptySlot] = itemId;
        } else if (itemData.traits?.includes('ARMOR')) {
            player.armor = itemId;
        } else {
            // Regular item goes to backpack
            player.backpack.push(itemId);
        }
        return true;
    }

    activateAutodestruction(state) {
        state.autodestruction.active = true;
        state.autodestruction.token = state.round + 5;
        this.log('Autodestruction Procedure activated! Facility will be destroyed in 5 rounds!');
        this.notify('autodestruction', { round: state.autodestruction.token });
    }

    resolveAntiAircraft(state) {
        const token = state.antiAircraft.tokens[state.antiAircraft.tokens.length - 1];
        if (token === 'active') {
            state.antiAircraft.lander.status = 'destroyed';
            this.log('Lander destroyed by Anti-Aircraft system!');
            // Characters in lander go back to landing zone
            state.antiAircraft.lander.characters.forEach(pid => {
                state.players[pid].inLander = false;
                state.players[pid].location = 'landingZone';
            });
            state.antiAircraft.lander.characters = [];
        } else {
            state.antiAircraft.lander.status = 'landed';
            this.log('Lander has landed safely!');
        }
        state.antiAircraft.resolved = true;
        state.antiAircraft.tokens = [];
    }

    destroyFacility() {
        const s = this.state;
        s.gameOver = true;
        s.players.forEach(p => {
            if (!p.hasEscaped) {
                p.alive = false;
                p.hasHibernated = false;
            }
        });
        this.log('Facility destroyed! All characters inside are dead.');
        this.endGame();
    }

    intruderSize(intruder) {
        return GAME_DATA.INTRUDER_TYPES[intruder.type]?.size || 1;
    }

    // === INFECTION / ECLOSION ===
    infectionProcedure(state, player) {
        // Per rulebook p.38: scan all Contamination cards in hand.
        const contaminationInHand = player.actionHand.filter(c => c.type === 'contamination');
        const infected = contaminationInHand.some(card => {
            const cardData = GAME_DATA.CONTAMINATION_CARDS.find(c => c.id === card.id);
            return cardData && cardData.infected;
        });
        if (infected && !player.larva) {
            player.larva = true;
            this.log(this.charName(player) + ' is infected with a Larva!');
        }
        // Place all Contaminations in hand on top of discard pile (p.38 step 3)
        const remaining = [];
        player.actionHand.forEach(c => {
            if (c.type === 'contamination') {
                player.actionDiscard.push(c);
            } else {
                remaining.push(c);
            }
        });
        player.actionHand = remaining;
    }

    eclosionProcedure(state, player) {
        // Draw 4 cards from action deck
        const drawn = [];
        for (let i = 0; i < 4; i++) {
            if (player.actionDeck.length === 0 && player.actionDiscard.length > 0) {
                player.actionDeck = shuffle([...player.actionDiscard]);
                player.actionDiscard = [];
            }
            if (player.actionDeck.length > 0) {
                drawn.push(player.actionDeck.pop());
            }
        }
        // Check if any contamination
        const hasContamination = drawn.some(card => card.type === 'contamination');
        if (hasContamination) {
            this.killPlayer(player, 'eclosion');
            // Place 1 adult in their room
            if (state.intruderPool.adult > 0) {
                state.intruders.push({
                    id: 'intruder_eclosion_' + Date.now(),
                    type: 'adult',
                    location: { type: 'room', id: player.location },
                    hits: 0
                });
                state.intruderPool.adult--;
            }
        }
        // Discard drawn cards
        drawn.forEach(c => player.actionDiscard.push(c));
    }

    // === END GAME ===
    endGame() {
        const s = this.state;
        s.gameOver = true;
        this.log('=== Game Over ===');

        // End of game checks
        s.players.forEach(player => {
            if (!player.alive && !player.hasEscaped) return;

            if (player.hasEscaped || player.hasHibernated) {
                if (!player.larva) {
                    // Step 1: Draw all cards from Action deck and discard pile to hand,
                    // then perform Infection Procedure (rulebook p.39)
                    player.actionDeck.forEach(c => player.actionHand.push(c));
                    player.actionDiscard.forEach(c => player.actionHand.push(c));
                    player.actionDeck = [];
                    player.actionDiscard = [];
                    this.infectionProcedure(s, player);
                } else {
                    // Step 2: Gain 1 Contamination, reshuffle whole deck (including
                    // hand and discard pile), then perform Eclosion Procedure (p.39)
                    this.gainContamination(s, player);
                    player.actionDeck = shuffle([
                        ...player.actionDeck, ...player.actionDiscard, ...player.actionHand
                    ]);
                    player.actionDiscard = [];
                    player.actionHand = [];
                    this.eclosionProcedure(s, player);
                }
            }
        });

        // Check objectives — only for players who are alive, escaped, or hibernated
        s.players.forEach(player => {
            if (!player.chosenObjective) return;
            // Dead players who didn't escape/hibernate cannot win
            if (!player.alive && !player.hasEscaped && !player.hasHibernated) return;
            const obj = [...GAME_DATA.MISSION_OBJECTIVES, ...GAME_DATA.PRIVATE_OBJECTIVES]
                .find(o => o.id === player.chosenObjective);
            if (obj && this.checkObjective(s, player, obj)) {
                s.winners.push(player.id);
                this.log(this.charName(player) + ' wins! Objective: ' + obj.name);
            }
        });

        this.notify('gameOver', { winners: s.winners });
    }

    checkObjective(state, player, objective) {
        // Simplified objective checking
        switch(objective.name) {
            case 'Self-Serving':
                return player.alive && state.players.filter(p => p.alive).length === 1;
            case 'The Great Hunt':
            case 'Faceoff':
                return state.queen.dead;
            case 'Veni, Vidi, Vici':
            case 'Clean-Up':
                return state.nest.destroyed;
            case 'Sabotage':
                return !state.players.some(p => p.alive && !p.hasEscaped) && state.gameOver;
            case 'Survivor':
                return player.hasEscaped;
            case 'Official Order':
                return this.checkMissionTask(state);
            case 'Ulterior Motive':
                return !this.checkMissionTask(state);
            default:
                return false;
        }
    }

    checkMissionTask(state) {
        const task = state.missionTask;
        if (!task) return false;
        switch(task.name) {
            case 'Primary Samples':
                const escapedWithEggs = state.players.filter(p => p.hasEscaped && p.backpack.includes('egg')).length;
                return escapedWithEggs >= 2;
            case 'Reconnaissance':
                return state.undiscoveredRooms.A.length === 0 &&
                       state.undiscoveredRooms.B.length === 0 &&
                       state.undiscoveredRooms.C.length === 0;
            case 'Eradication':
                return state.queen.dead;
            default:
                return false;
        }
    }

    charName(player) {
        const cd = GAME_DATA.CHARACTERS[player.character];
        return cd?.name || player.character || player.name || '?';
    }

    log(message) {
        if (this.state) {
            this.state.log.push({ message, timestamp: Date.now() });
        }
    }
}

// Utility
function shuffle(array) {
    const arr = [...array];
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
}