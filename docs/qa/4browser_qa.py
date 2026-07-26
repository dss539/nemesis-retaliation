"""
4-browser QA test: 1 host + 3 clients, play exactly 3 rounds.
Verifies: lobby join, game start, state sync across 4 clients, 
privacy filtering, turn rotation with 4 players, round transitions.
"""
from playwright.sync_api import sync_playwright
import json, time

results = {"rounds": [], "errors": [], "bugs": []}

with sync_playwright() as p:
    browsers = [p.chromium.launch(headless=True) for _ in range(4)]
    pages = [b.new_page() for b in browsers]

    # Collect console errors from all browsers
    def make_handler(name):
        def handler(msg):
            if msg.type == "error":
                results["errors"].append(f"{name}: {msg.text}")
        return handler

    for i, pg in enumerate(pages):
        pg.on("console", make_handler(f"Browser{i}"))

    print("=== SETUP: 4 BROWSERS ===")

    # Browser 0: Host
    pages[0].goto("http://127.0.0.1:8889/?v=4br")
    pages[0].wait_for_load_state("networkidle")
    pages[0].click("text=Host Game")

    # Set player count to 4 BEFORE creating game (select exists in hidden div)
    pages[0].evaluate("""() => {
        document.getElementById('num-players').value = '4';
    }""")

    pages[0].fill("#host-name", "HostP0")
    pages[0].click("text=Create Game")
    pages[0].wait_for_timeout(2000)
    host_code = pages[0].text_content("#host-code")
    print(f"Host code: {host_code}")

    # Browsers 1-3: Join
    for i in range(1, 4):
        pages[i].goto("http://127.0.0.1:8889/?v=4br")
        pages[i].wait_for_load_state("networkidle")
        pages[i].click("text=Join Game")
        pages[i].fill("#join-code", host_code)
        pages[i].fill("#player-name", f"Player{i}")
        pages[i].click("text=Connect")
        pages[i].wait_for_timeout(2000)
        status = pages[i].text_content("#join-status")
        print(f"Browser {i} join: {status}")

    # Wait for all joins to propagate
    pages[0].wait_for_timeout(2000)

    # Check host lobby
    lobby = pages[0].text_content("#lobby-players")
    print(f"Host lobby: {lobby}")

    # Verify all 4 players connected
    state_check = pages[0].evaluate("""() => {
        const s = window.nemesisEngine?.getState();
        return s ? s.players.map(p => ({id: p.id, name: p.name, connected: p.connected})) : null;
    }""")
    print(f"Connected players: {json.dumps(state_check)}")
    results["players_after_join"] = state_check

    # Start game
    print("\n=== STARTING GAME ===")
    pages[0].click("text=Start Game")
    pages[0].wait_for_timeout(3000)

    # Verify all browsers switched to game screen
    for i, pg in enumerate(pages):
        active = pg.evaluate("""() => document.getElementById('game-screen').classList.contains('active')""")
        print(f"Browser {i} on game screen: {active}")
        results[f"browser{i}_on_game_screen"] = active

    # Choose objectives for all players
    for i, pg in enumerate(pages):
        btns = pg.query_selector_all("button")
        for btn in btns:
            if btn.text_content() == "Choose":
                btn.click()
                break
        pg.wait_for_timeout(200)

    # Get initial state from host
    state = pages[0].evaluate("""() => {
        const s = window.nemesisEngine.getState();
        return {
            round: s.round, phase: s.phase, currentPlayer: s.currentPlayer,
            actionsRemaining: s.actionsRemaining,
            players: s.players.map(p => ({
                id: p.id, name: p.name, character: p.character,
                alive: p.alive, connected: p.connected,
                health: p.health, oxygen: p.oxygen, location: p.location,
                hand: p.actionHand.length, chosenObj: p.chosenObjective
            })),
            log: s.log.slice(-5).map(e => e.message)
        };
    }""")
    print(f"\nInitial state: Round {state['round']}, Phase: {state['phase']}")
    print(f"Current player: {state['currentPlayer']} ({state['players'][state['currentPlayer']]['name']})")
    for p in state["players"]:
        print(f"  P{p['id']}: {p['name']} ({p['character']}) alive={p['alive']} connected={p['connected']} hp={p['health']} oxy={p['oxygen']} loc={p['location']} hand={p['hand']}")

    # === PLAY 3 ROUNDS ===
    def get_state():
        return pages[0].evaluate("""() => {
            const s = window.nemesisEngine.getState();
            return {
                round: s.round, phase: s.phase, gameOver: s.gameOver,
                currentPlayer: s.currentPlayer, actionsRemaining: s.actionsRemaining,
                players: s.players.map(p => ({
                    id: p.id, name: p.name, alive: p.alive, connected: p.connected,
                    health: p.health, oxygen: p.oxygen, location: p.location,
                    backpack: p.backpack?.length, hand: p.actionHand?.length,
                    contam: p.contaminationInHand?.length, wounds: p.seriousWounds?.length,
                    larva: p.larva, escaped: p.hasEscaped, hibernated: p.hasHibernated
                })),
                rooms: Object.keys(s.rooms), corridors: s.corridors?.length,
                intruders: s.intruders?.map(i => ({type: i.type, loc: i.location?.id})),
                queen: {inPlay: s.queen?.inPlay, dead: s.queen?.dead},
                nest: {eggs: s.nest?.eggs, destroyed: s.nest?.destroyed},
                log: s.log?.slice(-10).map(e => e.message)
            };
        }""")

    def do_action(browser_idx, player_id, action, params=None):
        return pages[browser_idx].evaluate("""(args) => {
            if (NemesisNetwork.isHost) {
                return window.nemesisEngine.performAction(args.pid, args.act, args.p);
            }
            return NemesisNetwork.sendAction(args.act, args.p);
        }""", {"pid": player_id, "act": action, "p": params or {}})

    def get_client_state(browser_idx):
        """Get state as seen by a client (privacy-filtered)"""
        return pages[browser_idx].evaluate("""() => {
            const s = NemesisNetwork.state || window.nemesisEngine?.getState();
            if (!s) return null;
            return {
                round: s.round, phase: s.phase, currentPlayer: s.currentPlayer,
                players: s.players.map(p => ({
                    id: p.id, name: p.name,
                    hand: Array.isArray(p.actionHand) ? p.actionHand.length : 0,
                    backpack: Array.isArray(p.backpack) ? p.backpack.length : 0,
                    objectives: p.objectives?.map(o => typeof o === 'string' ? o : (o?.name || o?.id || 'hidden')),
                    handVisible: p.actionHand?.[0]?.action || (p.actionHand?.[0] === 'hidden' ? 'hidden' : 'own')
                }))
            };
        }""")

    target_round = 4  # play rounds 1, 2, 3 — stop when we reach round 4
    turn_count = 0

    while True:
        state = get_state()
        if not state:
            results["bugs"].append("Lost engine state")
            break

        if state["round"] >= target_round or state.get("gameOver"):
            break

        cp = state["currentPlayer"]
        player = state["players"][cp]

        # Determine which browser controls this player
        browser_idx = cp  # player 0 = browser 0 (host), player N = browser N

        if not player["alive"] or not player["connected"]:
            # Skip dead/disconnected
            if browser_idx == 0:
                pages[0].evaluate(f"""() => window.nemesisEngine.performAction({cp}, 'pass', {{}})""")
            pages[0].wait_for_timeout(200)
            continue

        turn_count += 1

        # Alternate actions: explore, search, pass
        action = ["search", "pass", "search", "pass"][turn_count % 4]

        if action == "search":
            result = do_action(browser_idx, cp, "search")
        elif action == "pass":
            result = do_action(browser_idx, cp, "pass")
        else:
            result = do_action(browser_idx, cp, "pass")

        pages[0].wait_for_timeout(300)

        # Detect round transitions
        new_state = get_state()
        if new_state and new_state["round"] != state["round"]:
            round_num = state["round"]
            log = new_state.get("log", [])
            events = [l for l in log if l.startswith("--") or l.startswith("Event:") or l.startswith("===")]
            print(f"\n=== Round {round_num} -> {new_state['round']} ===")
            for e in events[-6:]:
                print(f"  {e}")
            for p in new_state["players"]:
                status = "alive" if p["alive"] else "DEAD"
                print(f"  P{p['id']}: {p['name']} {status} hp={p['health']} oxy={p['oxygen']} "
                      f"loc={p['location']} items={p['backpack']} hand={p['hand']} contam={p['contam']}")

            # === PRIVACY CHECK: Compare what each browser sees ===
            print(f"\n  --- Privacy Check (Round {round_num} end) ---")
            for i in range(4):
                cs = get_client_state(i)
                if cs:
                    # Check if browser i can see other players' hand details
                    own_hand = cs["players"][i]["handVisible"] if i < len(cs["players"]) else "?"
                    other_hands = [cs["players"][j]["handVisible"] for j in range(len(cs["players"])) if j != i]
                    other_objs = [cs["players"][j]["objectives"] for j in range(len(cs["players"])) if j != i]
                    print(f"  Browser {i}: own_hand={own_hand} other_hands={other_hands} other_objs={other_objs}")

            results["rounds"].append({
                "round": round_num,
                "events": events[-6:],
                "players": new_state["players"],
                "rooms": new_state["rooms"],
                "corridors": new_state["corridors"],
                "intruders": new_state["intruders"]
            })

    # === FINAL VERIFICATION ===
    print(f"\n=== FINAL STATE (after 3 rounds) ===")
    final = get_state()
    print(f"Round: {final['round']}, Phase: {final['phase']}")
    print(f"Rooms: {final['rooms']}")
    print(f"Corridors: {final['corridors']}")
    print(f"Intruders: {final['intruders']}")
    for p in final["players"]:
        status = "alive" if p["alive"] else "DEAD"
        print(f"  P{p['id']}: {p['name']} {status} hp={p['health']} oxy={p['oxygen']} "
              f"loc={p['location']} items={p['backpack']} hand={p['hand']} contam={p['contam']} wounds={p['wounds']}")

    # Verify all 4 browsers see the same round/phase
    print(f"\n=== CROSS-BROWSER SYNC CHECK ===")
    sync_results = {}
    for i in range(4):
        cs = get_client_state(i)
        if cs:
            sync_results[f"browser{i}"] = {"round": cs["round"], "phase": cs["phase"], "currentPlayer": cs["currentPlayer"]}
            print(f"Browser {i}: Round={cs['round']} Phase={cs['phase']} Turn=P{cs['currentPlayer']}")
        else:
            sync_results[f"browser{i}"] = None
            print(f"Browser {i}: No state")

    # Check sync
    rounds = [s["round"] for s in sync_results.values() if s]
    phases = [s["phase"] for s in sync_results.values() if s]
    all_synced = len(set(rounds)) == 1 and len(set(phases)) == 1
    print(f"All synced: {all_synced}")
    results["sync_check"] = "PASS" if all_synced else "FAIL"
    results["sync_details"] = sync_results

    # Screenshots
    for i, pg in enumerate(pages):
        pg.screenshot(path=f"/home/smithers/nemesis-retaliation/docs/qa/4br-browser{i}.png")

    print(f"\n=== CONSOLE ERRORS ===")
    if results["errors"]:
        for err in results["errors"][:20]:
            print(f"  {err}")
    else:
        print("  None")

    results["final_state"] = final
    results["turn_count"] = turn_count

    for b in browsers:
        b.close()

with open("/home/smithers/nemesis-retaliation/docs/qa/4browser-results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nDone. {turn_count} turns played, {len(results['rounds'])} rounds tracked.")
if results["bugs"]:
    print(f"BUGS: {results['bugs']}")