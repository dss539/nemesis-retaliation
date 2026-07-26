"""Four-browser full-game QA trace for Nemesis: Retaliation.

Creates a real four-player PeerJS lobby, runs the host-authoritative engine to a
real game-over state, verifies all clients after every action, and writes a
per-action JSON/Markdown log plus representative screenshots.
"""
from __future__ import annotations

import json
import math
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

ROOT = Path(__file__).resolve().parents[2]
QA = ROOT / "docs" / "qa"
URL = "http://127.0.0.1:8890/?qa=full-game-trace-v1"
NAMES = ["Alpha", "Bravo", "Charlie", "Delta"]
DIRECTIONS = [
    ("N", 0, -1, "S"), ("NE", 1, -1, "SW"),
    ("E", 1, 0, "W"), ("SE", 1, 1, "NW"),
    ("S", 0, 1, "N"), ("SW", -1, 1, "NE"),
    ("W", -1, 0, "E"), ("NW", -1, -1, "SE"),
]
DIR_BY_ID = {d[0]: d for d in DIRECTIONS}
RESULT_JSON = QA / "full-game-action-log.json"
RESULT_MD = QA / "full-game-action-log.md"
SCREENSHOTS = {
    "initial": QA / "full-game-initial.png",
    "midgame": QA / "full-game-midgame.png",
    "crisis": QA / "full-game-crisis.png",
    "final": QA / "full-game-final.png",
    "client_final": QA / "full-game-client-final.png",
}


def state(page):
    return page.evaluate("""() => {
        const networkState = typeof NemesisNetwork !== 'undefined' ? NemesisNetwork.state : null;
        const s = window.nemesisEngine?.getState?.() || networkState;
        return s ? JSON.parse(JSON.stringify(s)) : null;
    }""")


def messages(s):
    out = []
    for entry in (s or {}).get("log", []):
        out.append(entry.get("message", "") if isinstance(entry, dict) else str(entry))
    return out


def player_summary(p):
    return {
        "id": p.get("id"), "name": p.get("name"), "character": p.get("character"),
        "alive": p.get("alive"), "health": p.get("health"), "oxygen": p.get("oxygen"),
        "location": p.get("location"), "cards": len(p.get("actionHand", [])),
        "backpack": list(p.get("backpack", [])),
        "gear": list(p.get("tacticalBelt", [])),
        "contamination": len(p.get("contaminationInHand", [])),
        "seriousWounds": len(p.get("seriousWounds", [])),
        "larva": p.get("larva"), "escaped": p.get("hasEscaped"),
        "hibernated": p.get("hasHibernated"), "inLander": p.get("inLander"),
        "objective": p.get("chosenObjective"), "objectiveComplete": p.get("objectiveComplete"),
    }


def summary(s):
    return {
        "round": s.get("round"), "phase": s.get("phase"),
        "currentPlayer": s.get("currentPlayer"),
        "actionsRemaining": s.get("actionsRemaining"),
        "gameOver": s.get("gameOver"), "winners": s.get("winners", []),
        "rooms": len(s.get("rooms", {})), "corridors": len(s.get("corridors", [])),
        "intruders": len(s.get("intruders", [])),
        "intruderTypes": dict(Counter(i.get("type") for i in s.get("intruders", []))),
        "queen": s.get("queen"), "nest": s.get("nest"),
        "autodestruction": s.get("autodestruction"),
        "lifeSupport": {k: v.get("lifeSupport") for k, v in s.get("sections", {}).items()},
        "players": [player_summary(p) for p in s.get("players", [])],
    }


def public_fingerprint(s):
    """State that must be identical on all browsers after each authoritative update."""
    return {
        "round": s.get("round"), "phase": s.get("phase"),
        "currentPlayer": s.get("currentPlayer"), "actionsRemaining": s.get("actionsRemaining"),
        "gameOver": s.get("gameOver"), "winners": s.get("winners", []),
        "rooms": s.get("rooms"), "corridors": s.get("corridors"),
        "intruders": s.get("intruders"), "players": s.get("players"),
        "queen": s.get("queen"), "nest": s.get("nest"),
        "sections": s.get("sections"), "autodestruction": s.get("autodestruction"),
        "logLength": len(s.get("log", [])),
    }


def topology_errors(s):
    errors = []
    bounds = {"minX": 0, "maxX": 6, "minY": 0, "maxY": 4}
    rooms = s.get("rooms", {})
    positions = {}
    for rid, room in rooms.items():
        pos = room.get("position")
        if not isinstance(pos, dict) or not isinstance(pos.get("x"), int) or not isinstance(pos.get("y"), int):
            errors.append(f"room {rid} has invalid position {pos}")
            continue
        key = (pos["x"], pos["y"])
        if key in positions:
            errors.append(f"rooms {positions[key]} and {rid} overlap at {key}")
        positions[key] = rid
        if not (bounds["minX"] <= key[0] <= bounds["maxX"] and bounds["minY"] <= key[1] <= bounds["maxY"]):
            errors.append(f"room {rid} is off board at {key}")
    corridor_ids = set()
    for corridor in s.get("corridors", []):
        cid = corridor.get("id")
        if cid in corridor_ids:
            errors.append(f"duplicate corridor id {cid}")
        corridor_ids.add(cid)
        r1, r2 = corridor.get("room1"), corridor.get("room2")
        if r1 == r2:
            errors.append(f"corridor {cid} is a self-loop")
        if r1 not in rooms or r2 not in rooms:
            errors.append(f"corridor {cid} references missing room")
            continue
        p1, p2 = rooms[r1]["position"], rooms[r2]["position"]
        dx, dy = p2["x"] - p1["x"], p2["y"] - p1["y"]
        d1 = corridor.get("directionFromRoom1")
        d2 = corridor.get("directionFromRoom2")
        expected = next((d for d in DIRECTIONS if d[1] == dx and d[2] == dy), None)
        if not expected:
            errors.append(f"corridor {cid} joins non-neighbors ({dx},{dy})")
        elif d1 != expected[0] or d2 != expected[3]:
            errors.append(f"corridor {cid} direction mismatch {d1}/{d2}, expected {expected[0]}/{expected[3]}")
        if rooms[r1].get("exits", {}).get(d1) != cid:
            errors.append(f"room {r1} missing {d1} exit for {cid}")
        if rooms[r2].get("exits", {}).get(d2) != cid:
            errors.append(f"room {r2} missing {d2} exit for {cid}")
    corridor_set = set(corridor_ids)
    for rid, room in rooms.items():
        for direction, cid in room.get("exits", {}).items():
            if direction not in DIR_BY_ID:
                errors.append(f"room {rid} has unknown exit {direction}")
            if cid not in corridor_set:
                errors.append(f"room {rid} exit {direction} references missing corridor {cid}")
    room_ids = set(rooms)
    for p in s.get("players", []):
        if p.get("location") not in room_ids:
            errors.append(f"player {p.get('name')} has missing location {p.get('location')}")
    valid_locations = room_ids | corridor_set
    for intruder in s.get("intruders", []):
        loc = intruder.get("location", {})
        if loc.get("id") not in valid_locations:
            errors.append(f"intruder {intruder.get('id')} has missing location {loc}")
    if not 0 <= (s.get("actionsRemaining") or 0) <= 2:
        errors.append(f"invalid actionsRemaining {s.get('actionsRemaining')}")
    return errors


def has_ranged_weapon(player, item_data):
    for item in player.get("handSlots", []):
        if item and "RANGED WEAPON" in item_data.get(item, {}).get("traits", []):
            return True
    return False


def empty_neighbors(s, room_id):
    room = s["rooms"].get(room_id)
    if not room:
        return []
    occupied = {(r["position"]["x"], r["position"]["y"]) for r in s["rooms"].values()}
    x, y = room["position"]["x"], room["position"]["y"]
    result = []
    for direction, dx, dy, _opposite in DIRECTIONS:
        nx, ny = x + dx, y + dy
        if 0 <= nx <= 6 and 0 <= ny <= 4 and (nx, ny) not in occupied:
            result.append((direction, nx, ny))
    return result


def adjacent_open_rooms(s, room_id):
    result = []
    for corridor in s.get("corridors", []):
        if corridor.get("door") == "closed":
            continue
        if corridor.get("room1") == room_id:
            result.append(corridor.get("room2"))
        elif corridor.get("room2") == room_id:
            result.append(corridor.get("room1"))
    return [rid for rid in result if rid in s.get("rooms", {})]


def choose_action(s, room_data, item_data, tracker, sequence):
    pid = s["currentPlayer"]
    p = s["players"][pid]
    room_id = p["location"]
    round_no = s["round"]

    if not p.get("alive") or p.get("hasEscaped") or p.get("hasHibernated") or p.get("inLander"):
        return "pass", {}, "inactive player safeguard"
    if not p.get("actionHand"):
        return "pass", {}, "no action cards"

    intruders_here = [i for i in s.get("intruders", []) if i.get("location") == {"type": "room", "id": room_id}]
    if intruders_here:
        target = intruders_here[0]
        if has_ranged_weapon(p, item_data):
            return "shoot", {"targetId": target["id"]}, f"combat: shoot {target['type']} in room"
        return "melee", {"targetId": target["id"]}, f"combat: melee {target['type']} in room"

    for item_id in list(p.get("backpack", [])) + [i for i in p.get("handSlots", []) if i]:
        name = item_data.get(item_id, {}).get("name")
        if name in ("Medpack", "Field Medkit") and p.get("health", 10) <= 6:
            return "useItem", {"itemId": item_id}, f"heal with {name}"
        if name == "Oxygen Tank" and p.get("oxygen", 7) <= 3:
            return "useItem", {"itemId": item_id}, "restore oxygen"

    # Exercise the Medical Support action and keep one character active longer.
    rest_key = (round_no, pid)
    if p.get("character") == "medicalSupport" and len(p.get("actionHand", [])) <= 2 and rest_key not in tracker["rested"]:
        tracker["rested"].add(rest_key)
        return "rest", {}, "Medical Support rest/infection procedure"

    search_key = (pid, room_id)
    icons = room_data.get(room_id, {}).get("itemIcons", [])
    searchable = any(icon != "blue" and s.get("itemDecks", {}).get(icon) for icon in icons)
    if searchable and search_key not in tracker["searched"]:
        tracker["searched"].add(search_key)
        return "search", {}, f"first search by player in {room_id}"

    can_explore = bool(s.get("explorationDeck")) and any(s.get("undiscoveredRooms", {}).get(k) for k in ("A", "B", "C", "?"))
    candidates = empty_neighbors(s, room_id) if can_explore else []
    if candidates:
        # Rotate compass preference to guarantee cardinal and diagonal coverage.
        preference = ["SE", "E", "S", "NE", "SW", "N", "W", "NW"]
        shift = (pid + round_no + sequence) % len(preference)
        ordered = preference[shift:] + preference[:shift]
        candidates.sort(key=lambda c: ordered.index(c[0]))
        direction, x, y = candidates[0]
        action = "cautiousMove" if (sequence + pid) % 4 == 0 else "move"
        return action, {
            "targetRoom": f"explore_trace_{sequence:03d}", "explore": True,
            "position": {"x": x, "y": y}, "direction": direction,
        }, f"explore legal {direction} slot ({x},{y})"

    use_key = (pid, room_id)
    if room_id in room_data and use_key not in tracker["used_rooms"]:
        tracker["used_rooms"].add(use_key)
        return "useRoom", {}, f"exercise {room_id} room effect"

    adjacent = adjacent_open_rooms(s, room_id)
    if adjacent:
        visited = tracker["visited"][pid]
        adjacent.sort(key=lambda rid: (
            -len(empty_neighbors(s, rid)),
            rid in visited,
            rid,
        ))
        target = adjacent[0]
        visited.add(target)
        return "move", {"targetRoom": target}, f"move through open graph edge to {target}"

    return "pass", {}, "no additional legal or useful action"


def wait_for_sync(pages, expected, timeout_ms=5000):
    expected_fp = public_fingerprint(expected)
    deadline = time.monotonic() + timeout_ms / 1000
    last = []
    while time.monotonic() < deadline:
        states = [state(page) for page in pages]
        if all(s and public_fingerprint(s) == expected_fp for s in states):
            return True, states
        last = states
        pages[0].wait_for_timeout(100)
    return False, last


def md_escape(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_markdown(report):
    lines = [
        "# Full-game QA action log", "",
        f"Run status: **{report['status']}**  ",
        f"Seed: `{report['seed']}`  ",
        f"Players: {', '.join(NAMES)}  ",
        f"Recorded actions: {len(report['actions'])}  ",
        f"Synchronization checks: {report['syncChecks']}  ",
        f"Topology checks: {report['topologyChecks']}  ",
        "",
        "## Setup", "",
    ]
    for event in report.get("setup", []):
        lines.append(f"- {event}")
    lines += ["", "## Every action and result", "",
              "| # | Round | Actor | Action | Result | State result | Engine log delta |",
              "|---:|---:|---|---|---|---|---|"]
    for a in report["actions"]:
        result = "success" if a["result"].get("success") else f"FAILED: {a['result'].get('error')}"
        after = a["after"]
        state_result = (f"R{after['round']} {after['phase']}; next P{after['currentPlayer']}; "
                        f"actions={after['actionsRemaining']}; rooms={after['rooms']}; "
                        f"corridors={after['corridors']}; intruders={after['intruders']}; "
                        f"gameOver={after['gameOver']}")
        action_text = f"{a['action']} — {a['reason']}"
        delta = "; ".join(a.get("engineLogDelta", [])) or "(none)"
        lines.append("| " + " | ".join(md_escape(v) for v in (
            a["sequence"], a["before"]["round"], a["actor"], action_text,
            result, state_result, delta,
        )) + " |")
    lines += ["", "## Final state", "", "```json",
              json.dumps(report.get("finalState"), indent=2), "```", "",
              "## Runtime failures", ""]
    if report.get("showstoppers"):
        lines.extend(f"- {e}" for e in report["showstoppers"])
    else:
        lines.append("- None detected.")
    lines += ["", "## Browser errors", ""]
    if report.get("browserErrors"):
        lines.extend(f"- {e}" for e in report["browserErrors"])
    else:
        lines.append("- None detected.")
    RESULT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run():
    seed = "browser-native (realized outcomes recorded in full trace)"
    report = {
        "schemaVersion": 1, "seed": seed, "status": "running", "setup": [],
        "actions": [], "showstoppers": [], "browserErrors": [], "pageErrors": [],
        "syncChecks": 0, "topologyChecks": 0, "screenshots": {k: str(v.relative_to(ROOT)) for k, v in SCREENSHOTS.items()},
    }
    tracker = {
        "searched": set(), "used_rooms": set(), "rested": set(),
        "visited": {i: {"landingZone"} for i in range(4)},
    }
    captured = set()

    with sync_playwright() as pw:
        browsers = [pw.chromium.launch(headless=True) for _ in range(4)]
        pages = [b.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=1) for b in browsers]
        host = pages[0]
        for idx, page in enumerate(pages):
            page.on("console", lambda msg, idx=idx: report["browserErrors"].append(f"browser {idx}: {msg.text}") if msg.type == "error" else None)
            page.on("pageerror", lambda error, idx=idx: report["pageErrors"].append(f"browser {idx}: {error}"))

        try:
            page_player_ids = [0]
            for page in pages:
                page.goto(URL, wait_until="domcontentloaded", timeout=30000)

            host.click("#btn-host")
            host.fill("#host-name", NAMES[0])
            # The player-count selector is in the next (still hidden) lobby panel.
            # Set its real DOM value before createHost() reads it.
            host.evaluate("document.querySelector('#num-players').value = '4'")
            host.get_by_role("button", name="Create Game", exact=True).click()
            host.wait_for_function("/^[A-Z2-9]{6}$/.test(document.querySelector('#host-code').textContent.trim())", timeout=15000)
            code = host.locator("#host-code").inner_text().strip()
            report["setup"].append(f"Host created deterministic four-player lobby {code}.")

            for idx in range(1, 4):
                page = pages[idx]
                page.click("#btn-join")
                page.fill("#join-code", code)
                page.fill("#player-name", NAMES[idx])
                page.get_by_role("button", name="Connect", exact=True).click()
                page.wait_for_timeout(3000)
                join_probe = page.evaluate("""() => ({
                    playerId: NemesisNetwork.playerId,
                    peerId: NemesisNetwork.peer?.id,
                    peerOpen: NemesisNetwork.peer?.open,
                    hostId: NemesisNetwork.hostId,
                    status: document.querySelector('#join-status')?.innerText,
                })""")
                if join_probe["playerId"] < 1:
                    host_probe = host.evaluate("""() => ({
                        peerId: NemesisNetwork.peer?.id,
                        peerOpen: NemesisNetwork.peer?.open,
                        connections: Object.keys(NemesisNetwork.connections),
                        players: nemesisEngine.state.players.map(p => ({
                            id: p.id, name: p.name, connected: p.connected, peerId: p.peerId,
                        })),
                    })""")
                    raise RuntimeError(f"join assignment failed for browser {idx}: client={join_probe}; host={host_probe}")
                assigned_id = join_probe["playerId"]
                page_player_ids.append(assigned_id)
                host.wait_for_function(
                    "playerId => window.nemesisEngine?.state?.players?.[playerId]?.connected === true",
                    arg=assigned_id,
                    timeout=15000,
                )
                report["setup"].append(f"{NAMES[idx]} joined as authoritative player {assigned_id}.")

            host.get_by_role("button", name="Start Game", exact=True).click()
            for page in pages:
                page.wait_for_function("document.querySelector('#game-screen').classList.contains('active')", timeout=15000)
            initial = state(host)
            item_data = host.evaluate("JSON.parse(JSON.stringify(GAME_DATA.ITEMS))")
            room_data = host.evaluate("JSON.parse(JSON.stringify(GAME_DATA.ROOMS))")

            # Choose each player's first dealt objective through that player's network client.
            for idx, page in enumerate(pages):
                player_id = page_player_ids[idx]
                objective_entry = initial["players"][player_id]["objectives"][0]
                objective = objective_entry["id"] if isinstance(objective_entry, dict) else objective_entry
                page.evaluate("objective => NemesisNetwork.sendChooseObjective(objective)", objective)
                host.wait_for_function(
                    "playerId => window.nemesisEngine.state.players[playerId].chosenObjective !== null",
                    arg=player_id,
                    timeout=5000,
                )
                report["setup"].append(f"{NAMES[idx]} chose {objective}.")
            host.evaluate("NemesisNetwork.broadcastState()")
            initial = state(host)
            synced, initial_client_states = wait_for_sync(pages, initial)
            if not synced:
                probes = []
                for browser_index, browser_state in enumerate(initial_client_states):
                    probes.append({
                        "browser": browser_index,
                        "summary": summary(browser_state) if browser_state else None,
                        "logLength": len(browser_state.get("log", [])) if browser_state else None,
                        "players": [{
                            "id": p.get("id"), "name": p.get("name"),
                            "connected": p.get("connected"),
                            "objective": p.get("chosenObjective"),
                            "cards": len(p.get("actionHand", [])),
                        } for p in browser_state.get("players", [])] if browser_state else None,
                    })
                raise RuntimeError("initial four-browser state did not synchronize: " + json.dumps(probes))
            report["syncChecks"] += 1
            initial_errors = topology_errors(initial)
            report["topologyChecks"] += 1
            if initial_errors:
                raise RuntimeError("initial topology invalid: " + "; ".join(initial_errors))
            report["initialState"] = summary(initial)
            host.screenshot(path=str(SCREENSHOTS["initial"]), full_page=True)
            captured.add("initial")

            no_progress = 0
            previous_progress = None
            max_actions = 260
            for sequence in range(1, max_actions + 1):
                before_state = state(host)
                if before_state.get("gameOver"):
                    break
                if before_state.get("phase") != "playerPhase":
                    raise RuntimeError(f"stalled outside player phase: {before_state.get('phase')}")
                pid = before_state["currentPlayer"]
                before = summary(before_state)
                before_messages = messages(before_state)
                action, params, reason = choose_action(before_state, room_data, item_data, tracker, sequence)

                result = host.evaluate(
                    "payload => window.nemesisEngine.performAction(payload.player, payload.action, payload.params)",
                    {"player": pid, "action": action, "params": params},
                )
                after_state = state(host)
                after = summary(after_state)
                delta = messages(after_state)[len(before_messages):]
                record = {
                    "sequence": sequence, "actorId": pid, "actor": before_state["players"][pid]["name"],
                    "action": action, "params": params, "reason": reason, "result": result,
                    "before": before, "after": after, "engineLogDelta": delta,
                }
                report["actions"].append(record)

                errors = topology_errors(after_state)
                report["topologyChecks"] += 1
                if errors:
                    raise RuntimeError(f"topology invariant failed after action {sequence}: " + "; ".join(errors))

                synced, client_states = wait_for_sync(pages, after_state)
                report["syncChecks"] += 1
                if not synced:
                    details = [summary(s) if s else None for s in client_states]
                    raise RuntimeError(f"state desynchronization after action {sequence}: {details}")

                progress = (after_state.get("round"), after_state.get("currentPlayer"), after_state.get("actionsRemaining"), len(after_state.get("log", [])))
                if progress == previous_progress:
                    no_progress += 1
                else:
                    no_progress = 0
                previous_progress = progress
                if no_progress >= 3:
                    raise RuntimeError(f"turn stalled for three actions at action {sequence}")

                if "midgame" not in captured and (after_state.get("round", 1) >= 5 or len(after_state.get("rooms", {})) >= 10):
                    host.screenshot(path=str(SCREENSHOTS["midgame"]), full_page=True)
                    captured.add("midgame")
                crisis = (after_state.get("queen", {}).get("inPlay") or
                          len(after_state.get("intruders", [])) >= 5 or
                          any(p.get("health", 10) <= 5 for p in after_state.get("players", [])))
                if "crisis" not in captured and crisis:
                    pages[2].screenshot(path=str(SCREENSHOTS["crisis"]), full_page=True)
                    captured.add("crisis")

                if after_state.get("gameOver"):
                    break
            else:
                raise RuntimeError(f"game failed to end within {max_actions} actions")

            final = state(host)
            if not final.get("gameOver"):
                raise RuntimeError("runner stopped without a real game-over condition")
            if final.get("round", 0) <= 1:
                raise RuntimeError("game ended before completing a meaningful round")
            report["finalState"] = summary(final)
            report["fullEngineLog"] = messages(final)
            host.screenshot(path=str(SCREENSHOTS["final"]), full_page=True)
            pages[3].screenshot(path=str(SCREENSHOTS["client_final"]), full_page=True)
            captured.update(("final", "client_final"))
            if "midgame" not in captured:
                host.screenshot(path=str(SCREENSHOTS["midgame"]), full_page=True)
                captured.add("midgame")
            if "crisis" not in captured:
                pages[2].screenshot(path=str(SCREENSHOTS["crisis"]), full_page=True)
                captured.add("crisis")

            # Disconnect before assessing runtime errors to avoid expected Peer teardown noise.
            report["status"] = "passed"
        except Exception as exc:
            report["showstoppers"].append(f"{type(exc).__name__}: {exc}")
            report["status"] = "failed"
        finally:
            report["browserErrors"] = list(dict.fromkeys(report["browserErrors"]))
            report["pageErrors"] = list(dict.fromkeys(report["pageErrors"]))
            report["capturedScreenshots"] = sorted(captured)
            for browser in browsers:
                browser.close()

    if report["browserErrors"] or report["pageErrors"]:
        report["status"] = "failed"
        report["showstoppers"].append("browser/page errors occurred during the run")
    RESULT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_markdown(report)
    print(json.dumps({
        "status": report["status"], "actions": len(report["actions"]),
        "round": report.get("finalState", {}).get("round"),
        "showstoppers": report["showstoppers"],
        "browserErrors": report["browserErrors"],
        "pageErrors": report["pageErrors"],
        "screenshots": report["capturedScreenshots"],
    }, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(run())
