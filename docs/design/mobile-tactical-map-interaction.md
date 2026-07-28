# Mobile Tactical Map Interaction

## Status

This document defines the proposed mobile map behavior after the physical-information classification in `mobile-information-classification.md`. It is a design specification, not yet an implementation record.

## Design decision

Use a hybrid camera:

- preserve continuous one-finger pan and two-finger pinch zoom;
- add semantic Room focus as the fastest primary navigation path;
- change rendered information according to each Room's on-screen size, not a device model or raw zoom percentage;
- allow nonessential global chrome to disappear while the player is focused closely on local tactics.

Room focus augments pinch zoom rather than replacing it. Pinch/pan is necessary for a high-interaction tactical surface and for inspecting arbitrary relationships. Room focus provides a predictable one-tap way to reach the useful local view without manually steering the camera.

## Core principles

1. The map is the primary play surface.
2. Zoom changes information density, not merely pixel size.
3. Critical tactical state survives every zoom level.
4. Detailed Room information appears inside the focused Room rather than in a floating overlay.
5. Map-local information stays attached to its Room, Corridor, model, or marker.
6. Global information may collapse at close zoom, but urgent global danger must remain visible.
7. Navigation and action targeting are separate interaction states so a map tap is never ambiguous.
8. Invalid action targets are omitted, not displayed as disabled choices.
9. Camera changes initiated by the game must not repeatedly steal control from a player who is inspecting the map.
10. Detail thresholds derive from rendered geometry and legibility, then are validated in portrait and landscape.

# Semantic map levels

The renderer uses three semantic levels. The camera itself remains continuous; these levels control what is drawn.

Thresholds should be based on the Room's rendered CSS-pixel width. Initial values below are prototype targets, not final constants:

- Overview: Room width below approximately 72 CSS px.
- Neighborhood: Room width approximately 72–150 CSS px.
- Room Detail: Room width above approximately 150 CSS px.

Use hysteresis around thresholds so labels do not flicker while the user pinches near a boundary. For example, require a Room to cross a threshold by 8–12 px before changing level.

The selected/focused Room may enter the next detail level earlier than surrounding Rooms. This keeps the focal Room informative without rendering the entire visible map at maximum density.

## Level 1: Facility Overview

Purpose:

- understand Facility topology and broad danger;
- locate Characters, Intruders, Robot, Fire, security, and damaged/broken components;
- choose where to inspect or act next;
- see legal movement/exploration targets without zooming first.

Must remain visible:

- all discovered Rooms and valid undiscovered Room positions;
- every placed Corridor and unexplored Corridor endpoint;
- Closed/Destroyed Door state;
- Reinforced Corridor state;
- Security: Secure count and permanent Shelter security;
- Fire;
- Room Malfunction/damage;
- Noise in Corridors;
- Character identities/ownership, even when multiple share a Room;
- Robot location and malfunction;
- Intruder type and quantity in Rooms and Corridors;
- Intruder Hits where they remain on the tabletop and Queen identity/state;
- selected/current Room and legal tactical targets.

May be reduced or removed:

- full Room names;
- Room effect text;
- Item and Computer icons unless they remain legible;
- Corridor ID and most numeric labels except Noise value when needed;
- decorative art and texture;
- full model illustrations.

Recommended compression:

- Security: shield icon with 1–3 pips/count; Shelter uses a distinct permanent-security mark.
- Fire: flame icon with an outline/label treatment that remains distinct without relying on color.
- Malfunction/damage: broken-system icon separate from Fire.
- Characters: tiny colored identity rings or portrait pips, never only a total count.
- Robot: unique squared/mechanical silhouette so it cannot be mistaken for a Character.
- Intruders: type silhouette/initial plus quantity; Queen always receives a unique larger mark.
- Hits: small attached hit pips/count on the affected Intruder, not a generic Room-damage value.
- Corridors: continuous topology stroke; Door gate, Reinforced double/armored line, Noise marker, and Intruder markers remain attached to the Corridor.

Overview must prioritize topology and state over Room art. If necessary, remove artwork before removing any required marker.

## Level 2: Tactical Neighborhood

Purpose:

- inspect one Room in relation to every connected Corridor and direct neighbor;
- plan movement, combat, Room use, Search, Robot use, and local support;
- retain enough surrounding context to understand immediate danger.

The focused composition must include:

- the selected Room at a comfortably readable size;
- every connected Corridor from the selected Room, including Door, Noise, Reinforced, Intruder, and value state;
- at least the identifiable edge/name of every connected neighboring Room;
- full neighboring Rooms when the viewport can include them without shrinking the selected Room below the Neighborhood threshold;
- all local Characters, Intruders, Robot, Hits, Fire, Malfunction, and Security;
- legal destinations and targets for the current action.

Focused Room information:

- full Room name;
- Section/type and ID;
- Item icons;
- Computer and special-rule icons;
- concise Room function text;
- current status and occupants;
- whether Use Room, Search, Secure, or other local actions are currently available.

Neighboring Rooms may use Overview or Neighborhood density depending on their own rendered size. The selected Room always gets priority.

A single tap on a Room from Overview should smoothly enter this composition. This is the default semantic Room-focus action.

## Level 3: Room Detail

Purpose:

- show the complete local tabletop information source without requiring a separate Room panel;
- resolve actions involving the Room, its occupants, Items/icons, and connected Corridors.

The focused Room must show:

- complete Room name, type, ID, icons, restrictions, and full function text;
- Fire, Malfunction, Security, and special permanent state;
- each Character identity and relevant local state;
- each Intruder type, count, and Hits;
- Robot identity, malfunction, and locally usable Tactical Gear;
- all connected Corridor exits with Direction, Noise value, Door state, Reinforced state, Noise marker, Corridor Intruders, and adjacent Room identity;
- current legal Room, occupant, and Corridor actions.

The view should include all connected Corridor segments and enough of each neighboring Room to identify the destination. In landscape it may include complete neighbors. In narrow portrait, destination headers/edges may be clipped at the viewport boundary, but their identity and Corridor relationship must remain clear.

Room function and status are rendered as part of the Room surface/layout. Do not place a floating detail card over the map.

Entering Room Detail:

- pinch in from Neighborhood;
- tap the already focused Room;
- or double-tap a Room from Overview/Neighborhood for a direct jump.

The player is not required to enter Room Detail merely to use an action. Neighborhood must already expose the action and its legal targets.

# Adaptive chrome

## Overview chrome

Overview may show the compact global layer defined in the information classification:

- Round/phase;
- Starting/current player;
- actions remaining;
- urgent Facility systems;
- local Health/Oxygen;
- compact Mission Task/Objective cues;
- local hand/action access.

The full Round track should not be drawn into the canvas. It is global UI and should not magnify or pan with the Facility.

## Neighborhood chrome

Collapse or remove:

- expanded Round tracker;
- Mission Task wording;
- full player roster;
- game log;
- zoom percentage and redundant zoom controls.

Retain in a narrow docked status band:

- current turn owner and actions remaining;
- local Health/Oxygen/Suffocating;
- current Section Life Support;
- access to the local hand/actions;
- urgent global conditions such as active Autodestruction, imminent Lander timing, disconnection pause, or a forced decision.

## Room Detail chrome

Remove all nonessential global information, including the ordinary Round display. The map receives the reclaimed space.

Retain only:

- local Health/Oxygen and actions remaining during the local player's turn;
- current player identity when it is someone else's turn;
- current Section Life Support because it directly affects the focused Character;
- urgent global danger/forced-decision indicators;
- the local hand/action dock when the player can act.

These elements must occupy reserved edge space rather than float over the Room.

Urgent global information overrides normal suppression. For example, active Autodestruction remains visible at every zoom level even though the ordinary Round tracker is hidden.

# Interaction model

## Navigation state

- One-finger drag: pan.
- Pinch: continuous zoom anchored beneath the gesture midpoint.
- Tap a Room from Overview: select it and animate to Tactical Neighborhood.
- Tap the focused Room from Neighborhood: enter Room Detail.
- Double-tap a Room: direct Room Detail.
- Tap another Room while focused: transfer focus and recompose around that Room.
- Pinch out: naturally return through Neighborhood to Overview.
- Fit/Facility control in a docked edge location: return to Overview and center the Facility.
- Back action after semantic focus: return to the prior semantic level/camera, not the lobby or browser history.

Semantic focus should animate over roughly 180–250 ms: fast enough to feel direct, slow enough to preserve spatial orientation.

## Action-targeting state

When an action has been chosen:

- only legal targets receive action affordances and target hit areas;
- tapping a legal target executes/confirms that action according to its normal rules;
- tapping an invalid Room/Corridor does not show a disabled target and cannot issue the action;
- pan and pinch remain available so the player can reach an off-screen legal target;
- Room-focus taps are suspended where they would conflict with target selection;
- Cancel returns to the exact prior camera/focus state.

If all legal targets fit inside one semantic neighborhood, the camera may frame them once when targeting begins. It must not continually recenter while the user pans.

## Automatic camera behavior

The camera may automatically move when:

- a player's own turn begins and their Character is off-screen;
- the local Character completes a Move/Explore action;
- the user explicitly selects a Room or target from another UI source;
- a forced local decision cannot be understood without its map location.

The camera should not automatically move for every Event, remote player action, Intruder movement, damage tick, or log entry. Instead, show an edge/location cue for consequential off-screen changes. Tapping the cue focuses the affected location.

Do not interrupt an active pinch, pan, or target-selection gesture with automatic camera motion.

# Detail-selection rules

Information density is selected per object, not globally:

- focused Room: highest eligible level;
- current Character Room: at least Neighborhood cues when visible;
- legal target Room: enough detail to understand the target and risk;
- surrounding Rooms: level derived from rendered width;
- off-focus decorative elements: reduced before gameplay state is reduced.

Text must use a stable minimum CSS-pixel size. Do not scale tiny text below legibility merely because the canvas is zoomed out. Replace it with icons/counts at the lower level.

State changes should preserve object identity across levels. A Fire icon, Security mark, Character ring, Robot symbol, and each Intruder type should use the same visual language at every size, with only detail removed.

# Layout and implementation consequences

1. Remove the Round track and Mission Task panel from `render.js`; they are currently drawn inside the canvas and therefore zoom/pan with the map.
2. Separate camera scale/position from semantic detail selection.
3. Track `focusedRoomId`, semantic focus history, navigation versus action-targeting state, and camera animation state.
4. Compute focus bounds from actual Room/Corridor geometry and viewport dimensions.
5. Determine detail level from `getBoundingClientRect()`-derived Room width in CSS pixels, not canvas backing pixels.
6. Keep hit testing derived from authoritative Room/Corridor geometry after every camera change.
7. Keep CSS authoritative for the reserved chrome dimensions; the camera should size itself from the actual remaining map viewport.
8. Preserve current legal-target filtering and authoritative engine validation.
9. Do not implement Room detail as a modal or floating overlay.

# Acceptance criteria for a prototype

## Overview

- The whole Facility can be fitted and panned without distortion.
- Fire, Security, Malfunction/damage, Characters, Robot, Corridors, Doors, Noise, Intruders, and Hits remain recognizable in portrait and landscape.
- Multiple Characters and multiple Intruder types are not collapsed into an ambiguous generic count.
- Invalid movement/exploration targets are absent.

## Tactical Neighborhood

- One tap from Overview frames the selected Room, every connected Corridor, and identifiable neighbors.
- The selected Room's name, icons, status, function summary, occupants, and available local actions are readable.
- Corridor Door/Noise/Reinforced/Intruder state remains readable.

## Room Detail

- Full Room function and all local statuses are visible without opening a panel.
- Every connected Corridor and destination identity is present.
- The Round tracker, full roster, Mission wording, and log no longer consume the close tactical viewport.
- Local survival/action state and urgent global warnings remain available.

## Interaction

- Pinch and one-finger pan remain continuous at every semantic level.
- Tap-to-focus, direct Room Detail, Fit, and back-to-prior-view preserve spatial orientation.
- Map target coordinates remain correct after pan, pinch, semantic focus animation, orientation change, and chrome collapse.
- Action targeting never conflicts with Room focus.
- Automatic camera changes do not override an active user gesture.

## Accessibility

- No state relies on color alone.
- Minimum readable text size is enforced; lower zoom levels switch to symbols/counts rather than tiny text.
- Icon-only controls and map state have accessible names or equivalent nonvisual descriptions.
- Motion can be reduced or disabled through `prefers-reduced-motion`.