// Nemesis: Retaliation - Game Data Definitions
// Based on the official rulebook v1.0

const GAME_DATA = {

// === CHARACTERS ===
// 6 characters, each with unique action deck and abilities
CHARACTERS: {
    contractor: {
        id: 'contractor',
        name: 'Contractor',
        rank: 3,
        health: 9,
        startItems: [], // No support equipment
        actions: ['move','cautiousMove','shoot','burst','melee','useItem','useTacticalGear','useRoom','search','trade','activateRobot','pass'],
        actionDeckSize: 10,
        description: 'Versatile mercenary. No starting Support Equipment but has more flexibility.'
    },
    recon: {
        id: 'recon',
        name: 'Recon',
        rank: 1,
        health: 9,
        startItems: ['reconScanner'],
        actions: ['move','cautiousMove','shoot','burst','melee','useItem','useTacticalGear','useRoom','search','trade','activateRobot','pass','sprint'],
        actionDeckSize: 10,
        description: 'Scout with Sprint ability. Can move twice per action.'
    },
    officer: {
        id: 'officer',
        name: 'Officer',
        rank: 4,
        health: 9,
        startItems: ['officerPistol'],
        actions: ['move','cautiousMove','shoot','burst','melee','useItem','useTacticalGear','useRoom','search','trade','activateRobot','pass','command'],
        actionDeckSize: 10,
        description: 'High rank. Can command lower-rank characters.'
    },
    medicalSupport: {
        id: 'medicalSupport',
        name: 'Medical Support',
        rank: 2,
        health: 9,
        startItems: ['medpackStarter'],
        actions: ['move','cautiousMove','shoot','burst','melee','useItem','useTacticalGear','useRoom','search','trade','activateRobot','pass','rest'],
        actionDeckSize: 10,
        description: 'Can heal. Rest action draws cards and performs infection check.'
    },
    heavyGunOperator: {
        id: 'heavyGunOperator',
        name: 'Heavy Gun Operator',
        rank: 2,
        health: 9,
        startItems: ['automaticShotgun'],
        actions: ['move','cautiousMove','shoot','burst','melee','useItem','useTacticalGear','useRoom','search','trade','activateRobot','pass'],
        actionDeckSize: 10,
        description: 'Heavy weapons specialist. Bonus hit on shooting.'
    },
    combatEngineer: {
        id: 'combatEngineer',
        name: 'Combat Engineer',
        rank: 2,
        health: 9,
        startItems: ['tacticalHatchet'],
        actions: ['move','cautiousMove','shoot','burst','melee','useItem','useTacticalGear','useRoom','search','trade','activateRobot','pass','reinforce','drill'],
        actionDeckSize: 10,
        description: 'Can reinforce corridors and drill new ones.'
    }
},

// Character draft order colors
CHARACTER_COLORS: ['blue','green','red','yellow','purple'],

// === ROOMS ===
// Section Rooms are always present; ? rooms are random
ROOMS: {
    // Section A rooms (3)
    landingZone: { id: 'landingZone', name: 'Landing Zone', type: 'A', section: 'A', itemIcons: ['red','green'], computer: false, cannotSecure: false, cannotBreak: true },
    drillingRoom: { id: 'drillingRoom', name: 'Drilling Room', type: 'A', section: 'A', itemIcons: ['red','yellow'], computer: false },
    lifeSupportControlA: { id: 'lifeSupportControlA', name: 'Life Support Control "A"', type: 'A', section: 'A', itemIcons: ['green','blue'], computer: true },

    // Section B rooms (3)
    hibernatorium: { id: 'hibernatorium', name: 'Hibernatorium', type: 'B', section: 'B', itemIcons: [], computer: false, startsInactive: true, startsUndiscovered: true },
    coolingSystem: { id: 'coolingSystem', name: 'Cooling System', type: 'B', section: 'B', itemIcons: ['yellow'], computer: false },
    lifeSupportControlB: { id: 'lifeSupportControlB', name: 'Life Support Control "B"', type: 'B', section: 'B', itemIcons: ['green','blue'], computer: true },
    serverRoom: { id: 'serverRoom', name: 'Server Room', type: 'B', section: 'B', itemIcons: ['blue','green'], computer: true },

    // Section C rooms (4)
    lifeSupportControlC: { id: 'lifeSupportControlC', name: 'Life Support Control "C"', type: 'C', section: 'C', itemIcons: ['green','blue'], computer: true },
    nest: { id: 'nest', name: 'The Nest', type: 'C', section: 'C', itemIcons: [], computer: false, cannotSecure: true },
    reactor: { id: 'reactor', name: 'Reactor', type: 'C', section: 'C', itemIcons: ['yellow'], computer: false, cannotBreak: true },
    escapeShuttle: { id: 'escapeShuttle', name: 'Escape Shuttle', type: 'C', section: 'C', itemIcons: [], computer: false },

    // Random ? rooms (13)
    armory: { id: 'armory', name: 'Armory', type: '?', itemIcons: ['red','yellow'], computer: false },
    surgeryRoom: { id: 'surgeryRoom', name: 'Surgery Room', type: '?', itemIcons: ['green','blue'], computer: true },
    laboratory: { id: 'laboratory', name: 'Laboratory', type: '?', itemIcons: ['red','green'], computer: true },
    gunneryRoom: { id: 'gunneryRoom', name: 'Gunnery Room', type: '?', itemIcons: ['red','yellow'], computer: false },
    shelter: { id: 'shelter', name: 'Shelter', type: '?', itemIcons: [], computer: false, alwaysSecured: true },
    technicalCorridorEntrance: { id: 'technicalCorridorEntrance', name: 'Technical Corridor Entrance', type: '?', itemIcons: ['blue'], computer: false },
    sprinklersControl: { id: 'sprinklersControl', name: 'Sprinklers Control', type: '?', itemIcons: ['green'], computer: true },
    engineRoom: { id: 'engineRoom', name: 'Engine Room', type: '?', itemIcons: ['yellow'], computer: false },
    storageRoom: { id: 'storageRoom', name: 'Storage Room', type: '?', itemIcons: ['red','green','blue'], computer: false },
    commsRoom: { id: 'commsRoom', name: 'Communications Room', type: '?', itemIcons: ['blue'], computer: true },
    wasteDisposal: { id: 'wasteDisposal', name: 'Waste Disposal', type: '?', itemIcons: ['yellow'], computer: false },
    airlock: { id: 'airlock', name: 'Airlock', type: '?', itemIcons: ['red'], computer: false },
    powerGenerator: { id: 'powerGenerator', name: 'Power Generator', type: '?', itemIcons: ['yellow','blue'], computer: false }
},

// Room effects (what happens when you "Use the Room")
ROOM_EFFECTS: {
    landingZone: 'Gain any number of Tactical Gear tokens from the connected slots. OR Make a Noise roll to get into the Lander.',
    drillingRoom: 'Choose a Corridor adjacent to a Room with a Drill and without a Noise marker. Roll a Burst die and deal Hits equal to the result in that Corridor.',
    lifeSupportControlA: 'Flip an Active/Inactive marker in Section A. OR Discard a Fire marker from any Room in the Facility.',
    hibernatorium: 'Make a Noise roll to Hibernate.',
    coolingSystem: 'Activate the Autodestruction Procedure (place token 5 spaces ahead on Round track).',
    lifeSupportControlB: 'Flip an Active/Inactive marker in Section B. OR Check/swap Anti-Aircraft tokens in secret.',
    serverRoom: 'Use any Discovered Room in the Facility. OR Gain a Data token (if you dont have one).',
    lifeSupportControlC: 'Flip an Active/Inactive marker in Section C. OR Turn on the Hibernatorium.',
    nest: 'Pick up or Destroy 1 Egg (Heavy Item).',
    reactor: 'Shut down the Reactor: Remove all Fire, Malfunction markers, and Anti-Aircraft tokens from the game. Turn off all Life Support permanently.',
    escapeShuttle: 'Make a Noise roll to Escape the Facility.',
    armory: 'Gain any number of Ammo and Grenade tokens.',
    surgeryRoom: 'Discard 1 Serious Wound. OR Discard 1 Larva from your Character board.',
    laboratory: 'Analyze 1 Object (corpse, intruder carcass, or egg) to gain information.',
    gunneryRoom: 'Choose an adjacent Corridor. Deal 1 Hit to each Intruder in that Corridor.',
    shelter: 'No effect (always Secured, safe room).',
    technicalCorridorEntrance: 'Move to any Discovered Room in the Facility via technical corridors (no Noise roll).',
    sprinklersControl: 'Discard all Fire markers from a chosen Section.',
    engineRoom: 'Gain 1 Oxygen token.',
    storageRoom: 'Draw 2 Items of any type, keep 1, discard the other.',
    commsRoom: 'Look at the top Event card. You may place it at the bottom of the deck.',
    wasteDisposal: 'Discard any number of Items to restore 1 Health per item discarded.',
    airlock: 'Repel all Intruders from your Room to adjacent Corridors.',
    powerGenerator: 'Discard 1 Malfunction marker from any Room or Item in the Facility.'
},

// === CORRIDORS ===
// Corridors: values 1-4, 10 of each = 40 total
CORRIDOR_VALUES: [1, 2, 3, 4],
CORRIDORS_PER_VALUE: 10,

// === INTRUDERS ===
INTRUDER_TYPES: {
    drone: { id: 'drone', name: 'Drone', size: 2, corridorHits: 2, roomHits: 1, models: 8 },
    adult: { id: 'adult', name: 'Adult', size: 1, corridorHits: 1, roomHits: 1, models: 16 },
    larva: { id: 'larva', name: 'Larva', size: 1, corridorHits: 1, roomHits: 1, models: 6 },
    queen: { id: 'queen', name: 'Queen', size: 4, corridorHits: 0, roomHits: 0, models: 1, special: true }
},

// Intruder bag tokens
// Blanks return to bag, others are removed when drawn
INTRUDER_BAG: {
    blanks: 16,
    drones: 8,  // 1-3 Drones per token
    adults: 12, // 1-2 Adults per token
    larvae: 6,  // 1 Larva per token
    queen: 3    // Queen activation tokens
},

// === INTRUDER ATTACK CARDS (20) ===
// Each card has effects for DRONE, ADULT, QUEEN
INTRUDER_ATTACKS: [
    { id: 'ia1', name: 'Deadly Claws', drone: { effect: 'lose2hp', text: 'Lose 2 Health. Gain 1 Contamination.' }, adult: { effect: 'lose2hp', text: 'Lose 2 Health. Gain 1 Contamination.' }, queen: { effect: 'lose2hp', text: 'Lose 2 Health. Gain 1 Contamination.' } },
    { id: 'ia2', name: 'Bite', drone: { effect: 'lose2hp_contam', text: 'Lose 2 Health. Gain 1 Contamination.' }, adult: { effect: 'lose2hp_contam', text: 'Lose 2 Health. Gain 1 Contamination.' }, queen: { effect: 'lose2hp_contam', text: 'Lose 2 Health. Gain 1 Contamination.' } },
    { id: 'ia3', name: 'Infecting', drone: { effect: 'infecting', text: 'Gain 1 Contamination. If no Larva, place 1 Larva.' }, adult: { effect: 'infecting', text: 'Gain 1 Contamination. If no Larva, place 1 Larva.' }, queen: { effect: 'infecting', text: 'Gain 1 Contamination. If no Larva, place 1 Larva.' } },
    { id: 'ia4', name: 'Rend', drone: { effect: 'seriousWound', text: 'Heavily Injured: die. Otherwise gain 1 Serious Wound.' }, adult: { effect: 'seriousWound', text: 'Heavily Injured: die. Otherwise gain 1 Serious Wound.' }, queen: { effect: 'seriousWound', text: 'Heavily Injured: die. Otherwise gain 2 Serious Wounds.' } },
    { id: 'ia5', name: 'Crush', drone: { effect: 'lose3hp', text: 'Heavily Injured: die. Otherwise lose 3 Health.' }, adult: { effect: 'lose3hp', text: 'Heavily Injured: die. Otherwise lose 3 Health.' }, queen: { effect: 'lose4hp', text: 'Heavily Injured: die. Otherwise lose 4 Health.' } },
    { id: 'ia6', name: 'Grasp', drone: { effect: 'lose2hp', text: 'Lose 2 Health.' }, adult: { effect: 'lose2hp', text: 'Lose 2 Health.' }, queen: { effect: 'lose3hp', text: 'Lose 3 Health.' } },
    { id: 'ia7', name: 'Slash', drone: { effect: 'lose1hp_contam', text: 'Lose 1 Health. Gain 1 Contamination.' }, adult: { effect: 'lose1hp_contam', text: 'Lose 1 Health. Gain 1 Contamination.' }, queen: { effect: 'lose2hp_contam', text: 'Lose 2 Health. Gain 1 Contamination.' } },
    { id: 'ia8', name: 'Pounce', drone: { effect: 'lose1hp', text: 'Lose 1 Health.' }, adult: { effect: 'lose1hp', text: 'Lose 1 Health.' }, queen: { effect: 'lose2hp', text: 'Lose 2 Health.' } },
    { id: 'ia9', name: 'Tail Whip', drone: { effect: 'lose2hp', text: 'Lose 2 Health.' }, adult: { effect: 'lose2hp', text: 'Lose 2 Health.' }, queen: { effect: 'lose2hp', text: 'Lose 2 Health.' } },
    { id: 'ia10', name: 'Acid Spit', drone: { effect: 'lose1hp_contam', text: 'Lose 1 Health. Gain 1 Contamination.' }, adult: { effect: 'lose1hp_contam', text: 'Lose 1 Health. Gain 1 Contamination.' }, queen: { effect: 'lose2hp_contam', text: 'Lose 2 Health. Gain 1 Contamination.' } },
    { id: 'ia11', name: 'Gnaw', drone: { effect: 'seriousWound_contam', text: 'Gain 1 Serious Wound and 1 Contamination.' }, adult: { effect: 'seriousWound_contam', text: 'Gain 1 Serious Wound and 1 Contamination.' }, queen: { effect: 'seriousWound_contam', text: 'Gain 2 Serious Wounds and 1 Contamination.' } },
    { id: 'ia12', name: 'Charge', drone: { effect: 'lose2hp', text: 'Lose 2 Health.' }, adult: { effect: 'lose2hp', text: 'Lose 2 Health.' }, queen: { effect: 'lose3hp', text: 'Lose 3 Health.' } },
    { id: 'ia13', name: 'Spit', drone: { effect: 'lose1hp', text: 'Lose 1 Health.' }, adult: { effect: 'lose1hp', text: 'Lose 1 Health.' }, queen: { effect: 'lose2hp', text: 'Lose 2 Health.' } },
    { id: 'ia14', name: 'Claw', drone: { effect: 'lose1hp', text: 'Lose 1 Health.' }, adult: { effect: 'lose1hp', text: 'Lose 1 Health.' }, queen: { effect: 'lose2hp', text: 'Lose 2 Health.' } },
    { id: 'ia15', name: 'Punch', drone: { effect: 'lose1hp', text: 'Lose 1 Health.' }, adult: { effect: 'lose1hp', text: 'Lose 1 Health.' }, queen: { effect: 'lose1hp', text: 'Lose 1 Health.' } },
    { id: 'ia16', name: 'Headbutt', drone: { effect: 'lose2hp', text: 'Lose 2 Health.' }, adult: { effect: 'lose2hp', text: 'Lose 2 Health.' }, queen: { effect: 'lose2hp', text: 'Lose 2 Health.' } },
    { id: 'ia17', name: 'Tear', drone: { effect: 'lose1hp_contam', text: 'Lose 1 Health. Gain 1 Contamination.' }, adult: { effect: 'lose1hp_contam', text: 'Lose 1 Health. Gain 1 Contamination.' }, queen: { effect: 'lose2hp_contam', text: 'Lose 2 Health. Gain 1 Contamination.' } },
    { id: 'ia18', name: 'Maul', drone: { effect: 'seriousWound', text: 'Heavily Injured: die. Otherwise gain 1 Serious Wound.' }, adult: { effect: 'seriousWound', text: 'Heavily Injured: die. Otherwise gain 1 Serious Wound.' }, queen: { effect: 'seriousWound', text: 'Heavily Injured: die. Otherwise gain 2 Serious Wounds.' } },
    { id: 'ia19', name: 'Thrash', drone: { effect: 'lose2hp', text: 'Lose 2 Health.' }, adult: { effect: 'lose2hp', text: 'Lose 2 Health.' }, queen: { effect: 'lose3hp', text: 'Lose 3 Health.' } },
    { id: 'ia20', name: 'Venom', drone: { effect: 'lose1hp_contam', text: 'Lose 1 Health. Gain 1 Contamination.' }, adult: { effect: 'lose1hp_contam', text: 'Lose 1 Health. Gain 1 Contamination.' }, queen: { effect: 'lose2hp_contam', text: 'Lose 2 Health. Gain 1 Contamination.' } }
],

// === ITEMS (90: 30 each of red, yellow, green) ===
ITEMS: {
    // Red items (Weapons, 30)
    pistol: { id: 'pistol', name: 'Pistol', type: 'red', traits: ['RANGED WEAPON'], slots: [{type:'ammo'}], text: 'Standard sidearm.' },
    automaticShotgun: { id: 'automaticShotgun', name: 'Automatic Shotgun', type: 'red', traits: ['RANGED WEAPON','HEAVY'], slots: [{type:'ammo'},{type:'ammo'}], text: 'Before Shooting, deal 1 Hit more. Burst: Spend 1 Ammo if able.' },
    sonicGun: { id: 'sonicGun', name: 'Sonic Gun', type: 'red', traits: ['RANGED WEAPON','REQUIRES NO AMMO','HEAVY'], slots: [], text: 'Burst: Treat 3 and 4 as 2 Hits. Repel: Place 1 Intruder in your Room back to Corridor.' },
    grenadeLauncher: { id: 'grenadeLauncher', name: 'Grenade Launcher', type: 'red', traits: ['RANGED WEAPON','HEAVY'], slots: [{type:'ammo'},{type:'grenade'},{type:'grenade'}], text: 'Burst: Use any number of Grenades from this Weapon before or instead of normal Burst.' },
    tacticalHatchet: { id: 'tacticalHatchet', name: 'Tactical Hatchet', type: 'red', traits: ['MELEE WEAPON','HEAVY'], slots: [], text: 'Melee Attack: Deal 1 Hit instead of rolling the Shoot die, and place a Malfunction marker on this Weapon.' },
    militaryTaser: { id: 'militaryTaser', name: 'Military Taser', type: 'red', traits: ['ONE USE ONLY','HEAVY'], slots: [], text: 'Repel 1 Intruder from the Room. OR An Intruder of your choice discards all Hit markers.' },
    rifle: { id: 'rifle', name: 'Assault Rifle', type: 'red', traits: ['RANGED WEAPON','HEAVY'], slots: [{type:'ammo'},{type:'ammo'}], text: 'Shoot: You may spend 1 Ammo to deal 1 additional Hit.' },
    smg: { id: 'smg', name: 'SMG', type: 'red', traits: ['RANGED WEAPON'], slots: [{type:'ammo'}], text: 'Burst: Treat results of 1 as 2 Hits instead.' },
    sniperRifle: { id: 'sniperRifle', name: 'Sniper Rifle', type: 'red', traits: ['RANGED WEAPON','HEAVY'], slots: [{type:'ammo'}], text: 'Shoot: You may Shoot at Intruders in adjacent Rooms through Open Doors.' },
    flamethrower: { id: 'flamethrower', name: 'Flamethrower', type: 'red', traits: ['RANGED WEAPON','HEAVY','REQUIRES NO AMMO'], slots: [], text: 'Shoot: Place 1 Fire marker in the Room. Burst: Place 1 Fire marker in the Corridor instead of dealing Hits.' },
    // Fill remaining red items with generic weapons
    ...generateGenericItems('red', 'Weapon', 20),

    // Yellow items (Heavy/Utility, 30)
    ductTape: { id: 'ductTape', name: 'Duct Tape', type: 'yellow', traits: ['ONE USE ONLY'], slots: [], text: 'Discard a Malfunction marker. OR Place 1 Heavy Item above another Heavy Item in your Hand slot (carry 2 Heavy Items in 1 Hand).' },
    technicalRobot: { id: 'technicalRobot', name: 'Technical Robot', type: 'yellow', traits: ['HEAVY'], slots: [], text: 'Move the Robot up to 2 times. OR Discard a Malfunction marker from the Room with the Robot.' },
    serverRobot: { id: 'serverRobot', name: 'Server Robot', type: 'yellow', traits: ['HEAVY'], slots: [], text: 'Move the Robot up to 3 times. OR If the Robot is in a Computer Room, use that Room (even with Malfunction).' },
    perimeterSecurityDevice: { id: 'perimeterSecurityDevice', name: 'Perimeter Security Device', type: 'yellow', traits: ['HEAVY'], slots: [], text: 'Whenever you Discover a new Room: Ignore Hazard results from all sources.' },
    heavyArmor: { id: 'heavyArmor', name: 'Heavy Armor', type: 'yellow', traits: ['ARMOR'], slots: [], text: 'Whenever you would gain a Serious Wound, you may lose 2 Health instead.' },
    ...generateGenericItems('yellow', 'Utility', 25),

    // Green items (Support/Consumables, 30)
    medpackStarter: { id: 'medpackStarter', name: 'Medpack', type: 'green', traits: [], slots: [], text: 'Restore 2 Health Points.' },
    oxygenTank: { id: 'oxygenTank', name: 'Oxygen Tank', type: 'green', traits: [], slots: [], text: 'Gain 3 Oxygen (max 7).' },
    scanner: { id: 'scanner', name: 'Scanner', type: 'green', traits: [], slots: [], text: 'Scan 1 Contamination card to check if it is Infected.' },
    ...generateGenericItems('green', 'Support', 27)
},

// === SUPPORT EQUIPMENT (24) ===
SUPPORT_EQUIPMENT: {
    reconScanner: { id: 'reconScanner', name: 'Recon Scanner', type: 'support', text: 'Whenever you Discover a new Room, you may place 1 Noise marker in a Corridor adjacent to that Room.' },
    officerPistol: { id: 'officerPistol', name: 'Officer Pistol', type: 'support', traits: ['RANGED WEAPON'], slots: [{type:'ammo'}], text: 'Standard officer sidearm.' },
    medpackStarter: { id: 'medpackStarter', name: 'Field Medkit', type: 'support', text: 'Once per round, you may use this as a Medpack without discarding it.' },
    automaticShotgun: { id: 'automaticShotgun', name: 'Auto Shotgun', type: 'support', traits: ['RANGED WEAPON','HEAVY'], slots: [{type:'ammo'},{type:'ammo'}], text: 'Before Shooting, deal 1 Hit more. Burst: Spend 1 Ammo if able.' },
    tacticalHatchet: { id: 'tacticalHatchet', name: 'Combat Hatchet', type: 'support', traits: ['MELEE WEAPON','HEAVY'], slots: [], text: 'Melee Attack: Deal 1 Hit without rolling, place Malfunction on this Weapon.' },
    // 19 more generic support items
    ...generateGenericItems('support', 'Support Equipment', 19)
},

// === SERIOUS WOUNDS (27) ===
SERIOUS_WOUNDS: [
    { id: 'sw1', name: 'Blindness', text: 'You cannot perform the Search Action.' },
    { id: 'sw2', name: 'Broken Ribs', text: 'You cannot perform the Melee Attack Action.' },
    { id: 'sw3', name: 'Concussion', text: 'When you perform a Move Action, make a Noise roll with 1 additional Noise marker placed.' },
    { id: 'sw4', name: 'Internal Bleeding', text: 'You cannot use the Rest Action.' },
    { id: 'sw5', name: 'Shattered Hand', text: 'You can only use 1 Hand slot.' },
    { id: 'sw6', name: 'Sprained Ankle', text: 'You cannot use the Sprint Action.' },
    { id: 'sw7', name: 'Cracked Skull', text: 'Discard 1 Action card from your hand at the end of each of your Turns.' },
    { id: 'sw8', name: 'Collapsed Lung', text: 'Lose 1 additional Oxygen at the end of each of your Turns.' },
    { id: 'sw9', name: 'Nerve Damage', text: 'You cannot use Tactical Gear tokens.' },
    { id: 'sw10', name: 'Loss of Vision', text: 'You cannot use Room Actions.' },
    { id: 'sw11', name: 'EYES', text: '+1 to all your Shoot results.' },
    { id: 'sw12', name: 'Weak Spot', text: 'Deal 1 Hit to an Intruder. Then Shoot or Melee Attack it.' },
    // Fill with generic wounds
    { id: 'sw13', name: 'Deep Wound', text: 'Lose 1 Health at the start of each of your Turns.' },
    { id: 'sw14', name: 'Fractured Arm', text: 'You cannot use Heavy Items.' },
    { id: 'sw15', name: 'Torn Muscle', text: 'Each Move Action costs 1 additional Action card.' },
    { id: 'sw16', name: 'Severe Burns', text: 'Lose 1 Health whenever you enter a Room with a Fire marker.' },
    { id: 'sw17', name: 'Dislocated Shoulder', text: 'You cannot perform the Burst Action.' },
    { id: 'sw18', name: 'Crushed Fingers', text: 'You cannot perform the Trade Action.' },
    { id: 'sw19', name: 'Ruptured Spleen', text: 'Lose 2 Health at the start of each of your Turns.' },
    { id: 'sw20', name: 'Spinal Injury', text: 'You cannot perform the Activate Robot Action.' },
    { id: 'sw21', name: 'Perforated Eardrum', text: 'Ignore Noise markers in adjacent Corridors.' },
    { id: 'sw22', name: 'Severed Tendon', text: 'You cannot perform the Cautious Move Action.' },
    { id: 'sw23', name: 'Punctured Lung', text: 'Lose 1 Oxygen at the start of each of your Turns.' },
    { id: 'sw24', name: 'Broken Jaw', text: 'You cannot use the Command Action.' },
    { id: 'sw25', name: 'Crushed Windpipe', text: 'Lose 1 additional Oxygen whenever you would lose Oxygen.' },
    { id: 'sw26', name: 'Torn Ligament', text: 'You cannot perform the Drill Action.' },
    { id: 'sw27', name: 'General Trauma', text: 'No special effect.' }
],

// === CONTAMINATION CARDS (27) ===
// Some are INFECTED, most are not
CONTAMINATION_CARDS: (() => {
    const cards = [];
    const infectedIndices = new Set();
    // Randomly assign ~7 infected cards
    while (infectedIndices.size < 7) {
        infectedIndices.add(Math.floor(Math.random() * 27));
    }
    for (let i = 0; i < 27; i++) {
        cards.push({
            id: 'contam_' + i,
            infected: infectedIndices.has(i),
            text: 'Contamination - Cannot be discarded for Actions. You may discard this card when you Pass.'
        });
    }
    return cards;
})(),

// === EVENT CARDS (20) ===
EVENTS: [
    { id: 'ev1', name: 'Reactor Overheating', text: 'All Intruders in each Corridor move. Then, all Intruders in every Room move. If a Fire is in the Cooling System or Reactor, activate Autodestruction. Place 1 Fire in each. Reshuffle Event deck.' },
    { id: 'ev2', name: 'Scent of Prey', text: 'All Intruders in each Corridor move. Then, all Intruders in every Room move. Resolve each Intruder adjacent to a Character. Each Character makes a Noise roll.' },
    { id: 'ev3', name: 'Short Circuit', text: 'All Intruders in each Corridor move. Then, all Intruders in every Room move. In Sections with Inactive Life Support: Place a Malfunction in each Room with a Computer. Each Character in a Room without a Fire resolves a Noise roll.' },
    { id: 'ev4', name: 'Fire Outbreak', text: 'All Intruders in each Corridor move. Then, all Intruders in every Room move. Place 1 Fire marker in 2 random Rooms in the Section with the most Fire markers (or random if tied).' },
    { id: 'ev5', name: 'System Failure', text: 'All Intruders in each Corridor move. Then, all Intruders in every Room move. Place 1 Malfunction marker on a random Heavy Item in each Characters possession.' },
    { id: 'ev6', name: 'Breeding', text: 'All Intruders in each Corridor move. Then, all Intruders in every Room move. Add 1 Larva to each Room with a Character and without a Fire marker.' },
    { id: 'ev7', name: 'Alarm', text: 'All Intruders in each Corridor move. Then, all Intruders in every Room move. Each Character in a Room with a Computer must make a Noise roll.' },
    { id: 'ev8', name: 'Hull Breach', text: 'All Intruders in each Corridor move. Then, all Intruders in every Room move. All Characters lose 1 Oxygen.' },
    { id: 'ev9', name: 'Power Surge', text: 'All Intruders in each Corridor move. Then, all Intruders in every Room move. Flip 1 random Active Life Support to Inactive.' },
    { id: 'ev10', name: 'Nest Awakening', text: 'All Intruders in each Corridor move. Then, all Intruders in every Room move. Add 1 Egg to the Nest (if not destroyed).' },
    { id: 'ev11', name: 'Malfunction', text: 'All Intruders in each Corridor move. Then, all Intruders in every Room move. Place 1 Malfunction marker in each Room with a Computer.' },
    { id: 'ev12', name: 'Infestation', text: 'All Intruders in each Corridor move. Then, all Intruders in every Room move. Draw 2 Intruder tokens from the bag and resolve them in random Corridors.' },
    { id: 'ev13', name: 'Heat Wave', text: 'All Intruders in each Corridor move. Then, all Intruders in every Room move. Place 1 Fire marker in a random Room in each Section.' },
    { id: 'ev14', name: 'Intruder Surge', text: 'All Intruders in each Corridor move. Then, all Intruders in every Room move. Draw 3 Intruder tokens from the bag and resolve them.' },
    { id: 'ev15', name: 'Blocked Passage', text: 'All Intruders in each Corridor move. Then, all Intruders in every Room move. Close 1 random Door in each Section.' },
    { id: 'ev16', name: 'Contamination Leak', text: 'All Intruders in each Corridor move. Then, all Intruders in every Room move. Each Character gains 1 Contamination card.' },
    { id: 'ev17', name: 'Emergency Lighting', text: 'All Intruders in each Corridor move. Then, all Intruders in every Room move. Each Character in a Room with Fire loses 1 Health.' },
    { id: 'ev18', name: 'Tremor', text: 'All Intruders in each Corridor move. Then, all Intruders in every Room move. Each Character makes a Noise roll.' },
    { id: 'ev19', name: 'Nest Defense', text: 'All Intruders in each Corridor move. Then, all Intruders in every Room move. Add 1 Drone to the Nest Room (if not destroyed).' },
    { id: 'ev20', name: 'Queen Awakening', text: 'All Intruders in each Corridor move. Then, all Intruders in every Room move. If the Queen is not in play, place her in the Nest. Otherwise, Queen activates.' }
],

// === EXPLORATION CARDS (12) ===
EXPLORATION_CARDS: [
    { id: 'ex1', roomType: 'A', corridors: { N: true, E: true, S: false, W: false }, entrance: 'closeDoors', text: 'Close all Doors around this Room.' },
    { id: 'ex2', roomType: '?', corridors: { N: true, E: true, S: true, W: false }, entrance: 'noiseRoll', text: 'Make a Noise roll.' },
    { id: 'ex3', roomType: 'B', corridors: { N: false, E: true, S: true, W: true }, entrance: 'noiseRoll', text: 'Make a Noise roll.' },
    { id: 'ex4', roomType: 'C', corridors: { N: true, E: false, S: true, W: true }, entrance: 'noiseRoll', text: 'Make a Noise roll.' },
    { id: 'ex5', roomType: '?', corridors: { N: true, E: true, S: true, W: true }, entrance: 'none', text: 'Standard exploration.' },
    { id: 'ex6', roomType: '?', corridors: { N: true, E: false, S: false, W: true }, entrance: 'closeDoors', text: 'Close all Doors around this Room.' },
    { id: 'ex7', roomType: '?', corridors: { N: false, E: true, S: true, W: false }, entrance: 'noiseRoll', text: 'Make a Noise roll.' },
    { id: 'ex8', roomType: '?', corridors: { N: true, E: true, S: false, W: true }, entrance: 'none', text: 'Standard exploration.' },
    { id: 'ex9', roomType: '?', corridors: { N: false, E: false, S: true, W: true }, entrance: 'noiseRoll', text: 'Make a Noise roll.' },
    { id: 'ex10', roomType: '?', corridors: { N: true, E: true, S: true, W: false }, entrance: 'none', text: 'Standard exploration.' },
    { id: 'ex11', roomType: '?', corridors: { N: false, E: true, S: false, W: true }, entrance: 'closeDoors', text: 'Close all Doors around this Room.' },
    { id: 'ex12', roomType: '?', corridors: { N: true, E: false, S: true, W: false }, entrance: 'noiseRoll', text: 'Make a Noise roll.' }
],

// === MISSION TASKS (8) ===
MISSION_TASKS: [
    { id: 'mt1', name: 'Primary Samples', minPlayers: 2, text: 'All Characters who Escape from the Facility must be carrying at least 2 Eggs in total among them.' },
    { id: 'mt2', name: 'Reconnaissance', minPlayers: 3, text: 'All Rooms of the A, B, and C type must be Discovered.' },
    { id: 'mt3', name: 'Escort Mission', minPlayers: 2, text: 'The Robot must reach the Reactor (Section C) at least once. AND At least 1 Character with a Data token must Escape.' },
    { id: 'mt4', name: 'Perimeter Clearing', minPlayers: 2, text: 'The Reactor (Section C) must be shut down. AND All 3 Rooms of the A type must be Discovered.' },
    { id: 'mt5', name: 'Essential Data', minPlayers: 2, text: 'At least 1 Character with a Data token must Escape using the Lander (Section A). AND There must be no Unexplored Corridors in Section A.' },
    { id: 'mt6', name: 'Facility Restart', minPlayers: 2, text: 'The Hibernatorium must be Activated. AND The Reactor (Section C) must be shut down.' },
    { id: 'mt7', name: 'Eradication', minPlayers: 3, text: 'The Queen must be dead. AND The Facility must NOT be destroyed.' },
    { id: 'mt8', name: 'The Supply Route', minPlayers: 3, text: 'There must be a continuous path of Reinforced Corridors from the Landing Zone to Life Support Control C. AND The Facility must NOT be destroyed.' }
],

// === OBJECTIVES (22: 7 Mission + 15 Private) ===
MISSION_OBJECTIVES: [
    { id: 'mo1', name: 'Official Order', minPlayers: 2, text: 'The Mission Task must be fulfilled.', effect: 'progressObjectiveTrack' },
    { id: 'mo2', name: 'Official Order', minPlayers: 2, text: 'The Mission Task must be fulfilled.', effect: 'progressObjectiveTrack' },
    { id: 'mo3', name: 'Official Order', minPlayers: 2, text: 'The Mission Task must be fulfilled.', effect: 'progressObjectiveTrack' },
    { id: 'mo4', name: 'Official Order', minPlayers: 3, text: 'The Mission Task must be fulfilled.', effect: 'progressObjectiveTrack' },
    { id: 'mo5', name: 'Ulterior Motive', minPlayers: 2, text: 'Mission Task must remain UNFULFILLED.', effect: 'progressObjectiveTrack' },
    { id: 'mo6', name: 'Ulterior Motive', minPlayers: 2, text: 'Mission Task must remain UNFULFILLED.', effect: 'progressObjectiveTrack' },
    { id: 'mo7', name: 'Ulterior Motive', minPlayers: 3, text: 'Mission Task must remain UNFULFILLED.', effect: 'progressObjectiveTrack' }
],

PRIVATE_OBJECTIVES: [
    { id: 'po1', name: 'Self-Serving', minPlayers: 2, text: 'You must be the only Survivor.', effect: 'progressObjectiveTrack' },
    { id: 'po2', name: 'The Great Hunt', minPlayers: 2, text: 'The Queen must be dead.', effect: 'progressObjectiveTrack' },
    { id: 'po3', name: 'Veni, Vidi, Vici', minPlayers: 2, text: 'The Nest (Section C) must be destroyed.', effect: 'progressObjectiveTrack' },
    { id: 'po4', name: 'Clean-Up', minPlayers: 2, text: 'The Nest (Section C) must be destroyed.', effect: 'progressObjectiveTrack' },
    { id: 'po5', name: 'Faceoff', minPlayers: 2, text: 'The Queen must be dead.', effect: 'progressObjectiveTrack' },
    { id: 'po6', name: 'Sabotage', minPlayers: 2, text: 'The Facility must be destroyed.', effect: 'progressObjectiveTrack' },
    { id: 'po7', name: 'Lone Wolf', minPlayers: 2, text: 'You must Escape and at least 1 other Character must die.', effect: 'progressObjectiveTrack' },
    { id: 'po8', name: 'Survivor', minPlayers: 2, text: 'You must Survive and Escape.', effect: 'progressObjectiveTrack' },
    { id: 'po9', name: 'Specimen Collector', minPlayers: 2, text: 'You must Escape carrying 1 Egg.', effect: 'progressObjectiveTrack' },
    { id: 'po10', name: 'Data Thief', minPlayers: 2, text: 'You must Escape with a Data token.', effect: 'progressObjectiveTrack' },
    { id: 'po11', name: 'Firebug', minPlayers: 3, text: 'At least 3 Rooms must have Fire markers at game end.', effect: 'progressObjectiveTrack' },
    { id: 'po12', name: 'Pacifist', minPlayers: 2, text: 'You must Escape without having killed any Intruders.', effect: 'progressObjectiveTrack' },
    { id: 'po13', name: 'Explorer', minPlayers: 3, text: 'All Rooms must be Discovered.', effect: 'progressObjectiveTrack' },
    { id: 'po14', name: 'Tomb Raider', minPlayers: 2, text: 'You must Escape carrying 2 Eggs.', effect: 'progressObjectiveTrack' },
    { id: 'po15', name: 'Last Stand', minPlayers: 3, text: 'All Characters must Escape or die (none Hibernating).', effect: 'progressObjectiveTrack' }
],

// === ROBOT CARDS (6) ===
ROBOTS: [
    { id: 'robot1', name: 'Combat Robot', text: 'The Robot may Attack an Intruder in the same Room (1 Hit).' },
    { id: 'robot2', name: 'Technical Robot', text: 'Move the Robot up to 2 times. OR Discard a Malfunction marker from the Room with the Robot.' },
    { id: 'robot3', name: 'Server Robot', text: 'Move the Robot up to 3 times. OR If the Robot is in a Computer Room, use that Room.' },
    { id: 'robot4', name: 'Exploration Robot', text: 'The Robot may Explore a new Room (Move through Unexplored Corridor). May make a Noise roll.' },
    { id: 'robot5', name: 'Medical Robot', text: 'Any Character in the same Room as the Robot may restore 1 Health.' },
    { id: 'robot6', name: 'Defense Robot', text: 'The Robot places 1 Secure token in its Room each round.' }
],

// === QUEEN HEALTH CARDS (12) ===
QUEEN_HEALTH_CARDS: [
    { id: 'qh1', discard: 1, text: 'Repel the Queen.' },
    { id: 'qh2', discard: 2, text: 'Discard 1 additional card.' },
    { id: 'qh3', discard: 0, text: 'Primeblood: Add all Queen tokens to the bag.' },
    { id: 'qh4', discard: 1, text: 'Repel the Queen.' },
    { id: 'qh5', discard: 2, text: 'Discard 1 additional card.' },
    { id: 'qh6', discard: 0, text: 'Repel the Queen and all Intruders in the same Room.' },
    { id: 'qh7', discard: 1, text: 'Discard 1 additional card.' },
    { id: 'qh8', discard: 2, text: 'Repel the Queen.' },
    { id: 'qh9', discard: 1, text: 'Discard 1 additional card.' },
    { id: 'qh10', discard: 0, text: 'Primeblood: Add all Queen tokens to the bag.' },
    { id: 'qh11', discard: 2, text: 'Discard 1 additional card.' },
    { id: 'qh12', discard: 1, text: 'Repel the Queen.' }
],

// === GAME CONFIG ===
CONFIG: {
    maxRounds: 14,
    maxPlayers: 5,
    // Fixed tactical map. Room slots follow the physical mat's stepped central
    // field rather than filling a rectangular 7×5 grid. A room may connect to
    // an immediately neighboring valid slot through any compass graph edge.
    boardBounds: { minX: 0, maxX: 6, minY: 0, maxY: 4 },
    boardSlots: [
        // The Landing Zone occupies the original upper-left entry bay; the
        // remaining perimeter steps inward rather than forming a full rectangle.
        { x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }, { x: 3, y: 0 }, { x: 4, y: 0 }, { x: 5, y: 0 },
        { x: 0, y: 1 }, { x: 1, y: 1 }, { x: 2, y: 1 }, { x: 3, y: 1 }, { x: 4, y: 1 }, { x: 5, y: 1 }, { x: 6, y: 1 },
        { x: 0, y: 2 }, { x: 1, y: 2 }, { x: 2, y: 2 }, { x: 3, y: 2 }, { x: 4, y: 2 }, { x: 5, y: 2 }, { x: 6, y: 2 },
        { x: 0, y: 3 }, { x: 1, y: 3 }, { x: 2, y: 3 }, { x: 3, y: 3 }, { x: 4, y: 3 }, { x: 5, y: 3 }, { x: 6, y: 3 },
        { x: 1, y: 4 }, { x: 2, y: 4 }, { x: 3, y: 4 }, { x: 4, y: 4 }, { x: 5, y: 4 }
    ],
    // Hex-grid directions. Flat-top hexes have no direct north or south neighbor.
    directions: [
        { id: 'NE', opposite: 'SW' },
        { id: 'E',  opposite: 'W' },
        { id: 'SE', opposite: 'NW' },
        { id: 'SW', opposite: 'NE' },
        { id: 'W',  opposite: 'E' },
        { id: 'NW', opposite: 'SE' }
    ],
    // Odd-row offset coordinates: odd rows are shifted half a cell right in the
    // renderer. This is the sole topology definition used by UI and engine.
    neighborPosition(position, directionId) {
        if (!position || !Number.isInteger(position.x) || !Number.isInteger(position.y)) return null;
        const oddRow = Math.abs(position.y) % 2 === 1;
        const offsets = {
            NE: { x: oddRow ? 1 : 0, y: -1 },
            E:  { x: 1, y: 0 },
            SE: { x: oddRow ? 1 : 0, y: 1 },
            SW: { x: oddRow ? 0 : -1, y: 1 },
            W:  { x: -1, y: 0 },
            NW: { x: oddRow ? 0 : -1, y: -1 }
        };
        const offset = offsets[directionId];
        return offset ? { x: position.x + offset.x, y: position.y + offset.y } : null;
    },
    directionBetween(source, destination) {
        return this.directions.find(direction => {
            const neighbor = this.neighborPosition(source, direction.id);
            return neighbor?.x === destination?.x && neighbor?.y === destination?.y;
        }) || null;
    },
    startingOxygen: 7,
    oxygenSuffocateThreshold: 0,
    corridorMaxIntruders: 6,
    roomMaxSecureTokens: 3,
    handSize: 5,
    actionsPerTurn: 2,
    autodestructionSpaces: 5,
    queenHitsMax: 6,
    nestEggs: 5,
    antiAircraftTokens: 2
}

};

// Helper: generate generic items to fill out the deck
function generateGenericItems(type, category, count) {
    const items = {};
    const names = {
        red: ['Combat Knife','Stun Baton','Pulse Rifle','Plasma Pistol','Combat Shotgun','Heavy Machine Gun','Crossbow','Taser','Flashbang','Smoke Grenade','Frag Grenade','Incendiary Rounds','Armor Piercing Rounds','Combat Machete','Tactical Batons','Speargun','Net Launcher',' Riot Gun','Battle Rifle','Laser Pistol'],
        yellow: ['Tool Kit','Welding Torch','Crowbar','Repair Kit','Med Kit Carrier','Ammo Belt','Grenade Pouch','Utility Belt','Hazmat Suit','Reinforced Gloves','Breach Charge','Thermal Goggles','Motion Detector','Signal Booster','Data Link','Override Key','Power Drill','Sledgehammer','Bolt Cutters','Fire Extinguisher','Insulated Suit','Pressure Suit','Reinforced Boots','Traction Cleats','Spare Parts'],
        green: ['Bandages','Antiseptic','Painkillers','Energy Drink','Adrenaline Shot','Herbal Remedy','Splint','Morphine','First Aid Kit','Emergency Rations','Water Filter','Air Filter','Decontamination Wipes','Antidote','Stim Pack','Vitamins','Disinfectant Spray','Tourniquet','Burn Cream','Antibiotics','Survival Kit','Flare Gun','Emergency Beacon','Signal Mirror','Thermal Blanket','Compass','Emergency Map']
    };
    const nameList = names[type] || ['Generic ' + category];
    for (let i = 0; i < count && i < nameList.length; i++) {
        const id = type + '_gen_' + i;
        items[id] = {
            id: id,
            name: nameList[i],
            type: type,
            traits: type === 'yellow' ? ['HEAVY'] : [],
            slots: [],
            text: category + ' item.'
        };
    }
    // Fill remaining with numbered generics
    for (let i = nameList.length; i < count; i++) {
        const id = type + '_gen_' + i;
        items[id] = {
            id: id,
            name: category + ' ' + (i + 1),
            type: type,
            traits: type === 'yellow' ? ['HEAVY'] : [],
            slots: [],
            text: category + ' item.'
        };
    }
    return items;
}