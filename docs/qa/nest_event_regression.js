const fs = require('fs');
const vm = require('vm');
const assert = require('assert');

const context = vm.createContext({
    console,
    Date,
    Math: Object.create(Math),
    setTimeout,
    clearTimeout
});
vm.runInContext(
    fs.readFileSync('js/data.js', 'utf8') + '\nthis.GAME_DATA = GAME_DATA;',
    context
);
vm.runInContext(
    fs.readFileSync('js/engine.js', 'utf8') + '\nthis.NemesisEngine = NemesisEngine;',
    context
);

const engine = new context.NemesisEngine();
const state = engine.createGame(['Alpha', 'Bravo'], 2);
assert(!state.rooms.nest, 'Nest must begin undiscovered for regression');

const dronesBefore = state.intruderPool.drone;
engine.resolveEvent(state, { id: 'ev19' });
assert.strictEqual(state.intruders.length, 0, 'hidden Nest must not create an off-map intruder');
assert.strictEqual(state.nest.pendingDrones, 1, 'Drone must be reserved for hidden Nest');
assert.strictEqual(state.intruderPool.drone, dronesBefore - 1, 'reserved Drone must leave pool');

engine.resolveEvent(state, { id: 'ev20' });
assert.strictEqual(state.queen.inPlay, true, 'Queen awakening must be remembered');
assert.strictEqual(state.queen.location.type, 'pending', 'hidden Queen must not claim a nonexistent room');

state.explorationDeck = ['ex4'];
state.undiscoveredRooms.C = ['nest'];
state.currentPlayer = 0;
state.phase = 'playerPhase';
state.actionsRemaining = 2;
const result = engine.performAction(0, 'move', {
    targetRoom: 'explore_nest_regression',
    explore: true,
    position: { x: 1, y: 0 },
    direction: 'E',
    section: 'C'
});
assert.strictEqual(result.success, true);
assert(state.rooms.nest, 'Nest must be discovered');
assert.strictEqual(state.nest.pendingDrones, 0, 'pending Drone must materialize');

const drone = state.intruders.find(intruder => intruder.type === 'drone');
assert.deepStrictEqual(
    JSON.parse(JSON.stringify(drone.location)),
    { type: 'room', id: 'nest' }
);
const queen = state.intruders.find(intruder => intruder.type === 'queen');
assert(queen, 'pending Queen must materialize as an intruder');
assert.deepStrictEqual(
    JSON.parse(JSON.stringify(queen.location)),
    { type: 'room', id: 'nest' }
);
assert.deepStrictEqual(
    JSON.parse(JSON.stringify(state.queen.location)),
    { type: 'room', id: 'nest' }
);
console.log('hidden Nest event regression passed');
