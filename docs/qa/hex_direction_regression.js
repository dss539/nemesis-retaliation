// Hex-topology regression: six flat-top directions, odd-row offsets, and engine enforcement.
const fs = require('fs');
const vm = require('vm');

vm.runInThisContext(fs.readFileSync('js/data.js', 'utf8') + ';globalThis.GAME_DATA = GAME_DATA;');
vm.runInThisContext(fs.readFileSync('js/engine.js', 'utf8') + ';globalThis.NemesisEngine = NemesisEngine;');
vm.runInThisContext(fs.readFileSync('js/render.js', 'utf8') + ';globalThis.Renderer = Renderer;');

const expectedDirections = ['NE', 'E', 'SE', 'SW', 'W', 'NW'];
const directions = GAME_DATA.CONFIG.directions.map(direction => direction.id);
if (JSON.stringify(directions) !== JSON.stringify(expectedDirections)) {
    throw new Error('Expected only six hex directions; got ' + JSON.stringify(directions));
}

const expectedNeighbors = {
    '3,2': { NE: [3, 1], E: [4, 2], SE: [3, 3], SW: [2, 3], W: [2, 2], NW: [2, 1] },
    '3,3': { NE: [4, 2], E: [4, 3], SE: [4, 4], SW: [3, 4], W: [2, 3], NW: [3, 2] }
};
for (const [key, expectations] of Object.entries(expectedNeighbors)) {
    const [x, y] = key.split(',').map(Number);
    for (const direction of GAME_DATA.CONFIG.directions) {
        const neighbor = GAME_DATA.CONFIG.neighborPosition({ x, y }, direction.id);
        const expected = expectations[direction.id];
        if (!expected || neighbor.x !== expected[0] || neighbor.y !== expected[1]) {
            throw new Error(`Wrong ${direction.id} neighbor from ${key}: ${JSON.stringify(neighbor)}`);
        }
        const reverse = GAME_DATA.CONFIG.directionBetween(neighbor, { x, y });
        if (reverse?.id !== direction.opposite) {
            throw new Error(`Missing reciprocal ${direction.opposite} edge from ${JSON.stringify(neighbor)} to ${key}`);
        }
    }
}

const engine = new NemesisEngine();
engine.createGame(['Hex QA', 'Scout'], 2);
const player = engine.state.players[0];
const rejectedSouth = engine.actionMove(player, {
    targetRoom: 'explore_invalid_s', explore: true, position: { x: 0, y: 1 }, direction: 'S'
});
if (rejectedSouth.success || !rejectedSouth.error?.includes('direction')) {
    throw new Error('Deprecated S direction was not rejected: ' + JSON.stringify(rejectedSouth));
}
const acceptedSE = engine.actionMove(player, {
    targetRoom: 'explore_valid_se', explore: true, position: { x: 0, y: 1 }, direction: 'SE'
});
if (!acceptedSE.success) throw new Error('Valid SE exploration failed: ' + JSON.stringify(acceptedSE));

const source = { id: 'source', position: { x: 3, y: 2 } };
const ne = { id: 'ne', position: GAME_DATA.CONFIG.neighborPosition(source.position, 'NE') };
const east = { id: 'east', position: GAME_DATA.CONFIG.neighborPosition(source.position, 'E') };
Renderer.state = { rooms: { source, ne, east } };
for (const corridor of [
    { room1: 'source', room2: 'ne' },
    { room1: 'source', room2: 'east' }
]) {
    const geometry = Renderer.corridorGeometry(corridor);
    const startRoom = Renderer.roomGeometry(source);
    const endRoom = Renderer.roomGeometry(Renderer.state.rooms[corridor.room2]);
    if (!Renderer.pointInHexagon(geometry.x1 - geometry.ux * 0.1, geometry.y1 - geometry.uy * 0.1, startRoom) ||
        Renderer.pointInHexagon(geometry.x1 + geometry.ux, geometry.y1 + geometry.uy, startRoom) ||
        !Renderer.pointInHexagon(geometry.x2 + geometry.ux * 0.1, geometry.y2 + geometry.uy * 0.1, endRoom) ||
        Renderer.pointInHexagon(geometry.x2 - geometry.ux, geometry.y2 - geometry.uy, endRoom)) {
        throw new Error('Corridor does not terminate at its hex boundaries: ' + JSON.stringify(geometry));
    }
}

console.log('hex direction regression passed');
