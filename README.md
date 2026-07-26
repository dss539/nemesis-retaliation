# Nemesis: Retaliation - Digital Edition

A faithful digital adaptation of the board game **Nemesis: Retaliation** by Awaken Realms. Web-based, peer-to-peer multiplayer, no server required.

## How to Play

1. One player clicks **Host Game** and shares the 6-character code
2. Other players click **Join Game** and enter the code
3. Host clicks **Start Game** when everyone has joined
4. Play the game!

## Features

- Faithful reproduction of Nemesis: Retaliation base game rules
- 1-5 players (semi-cooperative)
- 6 unique characters with different abilities
- Full intruder AI system (bag-building, noise rolls, intruder attacks)
- All 14 rounds with event cards, intruder phase, cleanup
- Escape/Hibernation/Autodestruction endgame
- Mission Tasks and Private Objectives
- WebRTC peer-to-peer networking (no server needed)
- 2D top-down board rendering with canvas

## Tech Stack

- Vanilla JavaScript (no build step, no dependencies)
- PeerJS for WebRTC networking
- HTML5 Canvas for board rendering
- CSS for UI panels
- Deployable to GitHub Pages (static files)

## Development

```bash
# Run locally
python3 -m http.server 8888
# Open http://localhost:8888
```

## Files

```
index.html      - Entry point
css/style.css   - All styling
js/data.js      - Game data definitions (rooms, items, events, etc.)
js/engine.js    - Core game rules engine
js/network.js   - PeerJS multiplayer networking
js/render.js    - 2D Canvas board renderer
js/ui.js        - UI panels and modals
js/main.js      - Main entry point / lobby
```

## Game Rules

This is based on the official Nemesis: Retaliation rulebook. The game is a semi-cooperative sci-fi survival game where 1-5 players are elite marines infiltrating an alien nest. Each player has hidden objectives, and you may not know who you can trust.

For the full rules, see the [official rulebook](https://awakenrealms.com/download).

## Disclaimer

This is a fan-made digital adaptation. Nemesis: Retaliation is designed by Adam Kwapiński and published by Awaken Realms. All game content belongs to them.