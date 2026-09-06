/**
 * Nemesis: Retaliation — Field Manual & Quick Reference
 * Interactive logic: tab navigation, searchable room database, and global search.
 */

// Official 25 Facility Rooms Dataset
const ROOMS_DATA = [
  {
    number: "01",
    section: "?",
    name: "SPRINKLERS CONTROL",
    items: ["green", "yellow"],
    hasComputer: true,
    effect: "Discard all Fire markers from a chosen Section.",
    notes: "Affects every Room in the designated Section. Does not remove fire from Corridors (fire does not stay in open corridors)."
  },
  {
    number: "02",
    section: "?",
    name: "SHELTER",
    items: ["green", "red"],
    hasComputer: false,
    effect: "Only if you are not infected with a Larva: Take all Contaminations from your hand and remove them from the game without scanning.",
    notes: "Shelter is permanently secured (prevents entry attacks, cannot be lost). Additional Secure tokens may be placed here up to 3."
  },
  {
    number: "03",
    section: "?",
    name: "EMERGENCY ROOM",
    items: ["green"],
    hasComputer: false,
    effect: "Restore 2 Health Points. OR Discard 1 Serious Wound of your choice.",
    notes: "Health restoration moves your marker left. Discarding a wound slides remaining wounds left."
  },
  {
    number: "04",
    section: "?",
    name: "SUPPLY ROOM",
    items: ["green", "red", "yellow"],
    hasComputer: false,
    effect: "Draw 1 Green, 1 Red, and 1 Yellow Item card. You may keep up to 2 of them and discard the rest.",
    notes: "Discarded items go to the bottoms of their respective decks. Keep cards secret until used."
  },
  {
    number: "05",
    section: "?",
    name: "ARMORY",
    items: ["red"],
    hasComputer: false,
    effect: "Gain any number of Ammo and Grenade tokens to fill empty slots.",
    notes: "All gained tokens must fit in empty Tactical Gear slots. You may discard existing tokens once, before or during this action, to make room."
  },
  {
    number: "06",
    section: "?",
    name: "DOOR CONTROL ROOM",
    items: ["red", "yellow"],
    hasComputer: true,
    effect: "Open and/or Close any number of Doors in a chosen Section.",
    notes: "Doors may be closed only on valid Door slots. Destroyed doors cannot be closed."
  },
  {
    number: "07",
    section: "?",
    name: "SECURITY ROBOT ROOM",
    items: ["yellow"],
    hasComputer: true,
    effect: "Place 1 Secure Token in the Room with the Robot. OR Reinforce an empty Corridor adjacent to the Room with the Robot.",
    notes: "Can be used even if the Robot is in another section, provided you have room access."
  },
  {
    number: "08",
    section: "?",
    name: "GUNNERY ROOM",
    items: ["red"],
    hasComputer: false,
    effect: "Choose a Corridor adjacent to a Room with a Red Item Icon and without a Malfunction. Roll a Burst die and deal Hits equal to the result in that Corridor.",
    notes: "Rolling the Burst die here is a room action, NOT a Burst Action, so it does not spend an Ammo token."
  },
  {
    number: "09",
    section: "?",
    name: "PRESSURE CONTROL",
    items: ["yellow"],
    hasComputer: true,
    effect: "Move 1 Intruder anywhere in the Facility to an adjacent space.",
    notes: "The Intruder may be moved in any direction (Room to Corridor or Corridor to Room). Moving into an occupied room triggers an attack."
  },
  {
    number: "10",
    section: "?",
    name: "ALARM ROOM",
    items: ["yellow"],
    hasComputer: true,
    effect: "Resolve or discard a Noise Marker from a chosen Corridor in the Facility.",
    notes: "Resolving noise draws an Intruder token; discarding noise simply cleans the corridor safely."
  },
  {
    number: "11",
    section: "?",
    name: "EXPERIMENTAL MILITARY LAB",
    items: ["red", "green"],
    hasComputer: false,
    effect: "Gain any number of Ammo tokens. OR Draw 2 random Support Equipment cards, keep 1, discard the other.",
    notes: "Allows acquiring powerful high-tier support equipment during mid-game."
  },
  {
    number: "12",
    section: "?",
    name: "TECHNICAL CORRIDOR ENTRANCE",
    items: ["yellow"],
    hasComputer: false,
    effect: "Move to any Room in the Facility. Resolve an Adult Intruder Attack against yourself.",
    notes: "Draw an Intruder Attack card as an Adult attack. Do not place a physical miniature. Secure tokens do not prevent this attack. Then roll Noise as normal."
  },
  {
    number: "13",
    section: "?",
    name: "DECONTAMINATION ROOM",
    items: ["green", "yellow"],
    hasComputer: false,
    effect: "Discard all Action Cards in hand and spend 2 Oxygen to purge all Contaminations from your deck and discard pile without scanning.",
    notes: "Cannot be performed if you have 1 O₂ or fewer (cannot induce suffocation)."
  },
  {
    number: "14",
    section: "A",
    name: "LANDING ZONE",
    items: [],
    hasComputer: false,
    effect: "Gain any number of Tactical Gear tokens from connected supply slots. OR Make a Noise roll to board the Lander.",
    notes: "Starting room. Operatives board the Lander here. If an Intruder enters after your noise roll, boarding fails. Health is immune while inside Lander."
  },
  {
    number: "15",
    section: "A",
    name: "LIFE SUPPORT CONTROL 'A'",
    items: ["green", "yellow"],
    hasComputer: true,
    effect: "Flip the Life Support token in Section A (Active / Inactive). OR Discard 1 Fire marker from any Room in the Facility.",
    notes: "Essential for restoring breathable atmosphere in Section A."
  },
  {
    number: "16",
    section: "A",
    name: "SURGERY ROOM",
    items: ["green"],
    hasComputer: false,
    effect: "Discard all Action cards in hand to remove a Larva from your Character board and scan all Contaminations in deck/discard (remove Infected ones). OR Discard 1 Serious Wound.",
    notes: "The primary medical haven for extracting chest parasites before eclosion kills you."
  },
  {
    number: "17",
    section: "A",
    name: "DRILLING STATION",
    items: ["yellow"],
    hasComputer: true,
    effect: "Place a new Corridor leading from the Room with the Robot.",
    notes: "Can connect to a Discovered or Undiscovered Room. Cannot be used if the Robot has a Malfunction."
  },
  {
    number: "18",
    section: "B",
    name: "HIBERNATORIUM",
    items: [],
    hasComputer: false,
    effect: "Make a Noise roll to Hibernate.",
    notes: "Must be Activated first (via Life Support Control C). If an Intruder enters after noise roll, action fails. Hibernated characters survive unless the facility explodes."
  },
  {
    number: "19",
    section: "B",
    name: "LIFE SUPPORT CONTROL 'B'",
    items: ["green", "yellow"],
    hasComputer: true,
    effect: "Flip Life Support token in Section B. OR Secretly inspect both Anti-Aircraft tokens and arrange them in any order.",
    notes: "Critical tactical room: ensures the AA system will not shoot down the Lander upon arrival. You may lie about the AA token faces."
  },
  {
    number: "20",
    section: "B",
    name: "SERVER ROOM",
    items: ["yellow"],
    hasComputer: true,
    effect: "Use any Discovered Computer Room in the Facility (without malfunction). OR Gain 1 Data Token.",
    notes: "Data tokens cannot be traded or stolen once gained and are vital for specific mission objectives."
  },
  {
    number: "21",
    section: "B",
    name: "COOLING SYSTEM",
    items: ["yellow"],
    hasComputer: true,
    effect: "Activate the Autodestruction Procedure.",
    notes: "Places Autodestruction token 5 spaces ahead on the Round track. Detonation destroys the entire facility and kills all remaining non-escaped operatives."
  },
  {
    number: "22",
    section: "C",
    name: "LIFE SUPPORT CONTROL 'C'",
    items: ["green", "yellow"],
    hasComputer: true,
    effect: "Flip Life Support token in Section C. OR Activate the Hibernatorium.",
    notes: "The only room capable of powering up the Hibernatorium pod systems."
  },
  {
    number: "23",
    section: "C",
    name: "REACTOR",
    items: ["yellow"],
    hasComputer: true,
    effect: "Remove all Life Support, Hibernatorium, and Anti-Aircraft tokens from the game. Facility power is permanently dead.",
    notes: "Also permanently cancels pending Autodestruction. All sections become permanently unpowered."
  },
  {
    number: "24",
    section: "C",
    name: "ESCAPE SHUTTLE",
    items: [],
    hasComputer: false,
    effect: "Make a Noise roll to launch the Escape Shuttle.",
    notes: "Single-occupant emergency pod. One use per game. Immune to Anti-Aircraft fire."
  },
  {
    number: "25",
    section: "C",
    name: "NEST",
    items: [],
    hasComputer: false,
    effect: "Take or Destroy 1 Intruder Egg and make a Noise roll.",
    notes: "Eggs count as Heavy Items (must occupy a Hand slot). When all eggs are gone, place a marker: the Nest is permanently Destroyed."
  }
];

// Search index database
const SEARCH_INDEX = [
  ...ROOMS_DATA.map(r => ({
    category: `Facility Room [${r.section}]`,
    title: `Room ${r.number}: ${r.name}`,
    snippet: `${r.effect} — ${r.notes}`,
    targetTab: "rooms-dir",
    action: () => filterRoomsByQuery(r.name)
  })),
  {
    category: "Turn Structure",
    title: "Player Phase (2 Actions per turn)",
    snippet: "Clockwise turn order, 2 actions per turn. Passing discards cards and requires oxygen check in unpowered sections.",
    targetTab: "quick-ref"
  },
  {
    category: "Turn Structure",
    title: "Event Phase (5 Steps)",
    snippet: "1) Lander Escape, 2) Fire Damage, 3) Intruder Attacks, 4) Event Card & Intruder Movement, 5) Bag Development.",
    targetTab: "quick-ref"
  },
  {
    category: "Combat",
    title: "Shooting with Ranged Weapons",
    snippet: "Deal 1 hit + roll Shoot die. 8 sides. Critical skull kills. Ammo is only spent if you roll the ammo-loss icon.",
    targetTab: "core-rules"
  },
  {
    category: "Combat",
    title: "Burst Suppressive Corridor Fire",
    snippet: "Spend 1 Ammo immediately. Roll 6-sided Burst die. Deal rolled hits to intruders in corridor. Adults die in 1 hit.",
    targetTab: "core-rules"
  },
  {
    category: "Hazards",
    title: "Noise Roll Procedure (10-sided die)",
    snippet: "Numbered result checks matching corridors. Hazard result spawns surprise Intruder in your room.",
    targetTab: "quick-ref"
  },
  {
    category: "Medical",
    title: "Serious Wounds (9 Types)",
    snippet: "Arm, Bleeding, Body, Eyes, Guts, Hand, Knee, Leg, Lungs. Treated in Surgery or Emergency Room.",
    targetTab: "quick-ref"
  },
  {
    category: "Alien",
    title: "Intruder Castes & Durability",
    snippet: "Larva (1 hit), Drone (2 hits in corridor), Adult (1 hit in corridor), Queen (Queen Health deck).",
    targetTab: "intruders"
  },
  {
    category: "Survival",
    title: "Contamination & Eclosion Test",
    snippet: "Red decoder scans cards for INFECTED. Eclosion draws 4 cards: if any Contamination in hand, operative dies.",
    targetTab: "core-rules"
  },
  {
    category: "Systems",
    title: "Anti-Aircraft & Lander Escape",
    snippet: "If AA tokens are Active when Lander lands, Lander is destroyed. Inspect and set to Inactive in Life Support B.",
    targetTab: "core-rules"
  },
  {
    category: "Systems",
    title: "Autodestruction Sequence",
    snippet: "Armed in Cooling System (Room 21). Placed 5 rounds ahead on track. Reactor shutdown cancels it.",
    targetTab: "core-rules"
  }
];

// Document Ready Initialization
document.addEventListener("DOMContentLoaded", () => {
  setupTabs();
  renderRooms(ROOMS_DATA);
  setupRoomFilters();
  setupGlobalSearch();
});

// Setup Main Navigation Tabs
function setupTabs() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const targetId = `tab-${tab.dataset.tab}`;
      
      // Update tab buttons
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      // Update tab panes
      document.querySelectorAll(".tab-pane").forEach(pane => {
        pane.classList.remove("active");
      });
      const targetPane = document.getElementById(targetId);
      if (targetPane) {
        targetPane.classList.add("active");
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
    });
  });
}

function switchToTab(tabName) {
  const tabButton = document.querySelector(`.nav-tab[data-tab="${tabName}"]`);
  if (tabButton) {
    tabButton.click();
  }
}

// Render Room Cards into Grid
function renderRooms(rooms) {
  const container = document.getElementById("rooms-grid");
  if (!container) return;

  container.innerHTML = rooms.map(room => {
    const sectionClass = room.section === "?" ? "sec-random" : `sec-${room.section}`;
    const compBadge = room.hasComputer ? `<span class="badge-comp" title="Computer Terminal Access">💻 Computer</span>` : "";
    
    const itemsHtml = room.items.map(color => {
      return `<span class="item-chip ${color}">${color} item</span>`;
    }).join("");

    return `
      <div class="room-card" data-section="${room.section}" data-computer="${room.hasComputer}">
        <div class="room-header">
          <div class="room-title-group">
            <span class="room-number">#${room.number}</span>
            <span class="room-name">${room.name}</span>
          </div>
          <div class="room-tags">
            ${compBadge}
            <span class="badge-section ${sectionClass}">Section ${room.section}</span>
          </div>
        </div>
        <div class="room-body">
          ${itemsHtml ? `<div class="room-items-bar">${itemsHtml}</div>` : ""}
          <div class="room-effect">
            <strong>Action:</strong> ${room.effect}
          </div>
          ${room.notes ? `<div class="room-notes"><strong>Note:</strong> ${room.notes}</div>` : ""}
        </div>
      </div>
    `;
  }).join("");
}

// Room Section Filters
function setupRoomFilters() {
  const buttons = document.querySelectorAll(".filter-btn");
  buttons.forEach(btn => {
    btn.addEventListener("click", () => {
      buttons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      const filter = btn.dataset.filter;
      if (filter === "all") {
        renderRooms(ROOMS_DATA);
      } else if (filter === "comp") {
        renderRooms(ROOMS_DATA.filter(r => r.hasComputer));
      } else {
        renderRooms(ROOMS_DATA.filter(r => r.section === filter));
      }
    });
  });
}

function filterRoomsByQuery(query) {
  const filtered = ROOMS_DATA.filter(r => 
    r.name.toLowerCase().includes(query.toLowerCase()) ||
    r.effect.toLowerCase().includes(query.toLowerCase())
  );
  renderRooms(filtered);
}

// Global Live Search System
function setupGlobalSearch() {
  const searchInput = document.getElementById("global-search");
  const clearBtn = document.getElementById("clear-search");
  const resultsPanel = document.getElementById("search-results-panel");
  const matchesList = document.getElementById("search-matches");
  const queryText = document.getElementById("search-query-text");
  const closeBtn = document.getElementById("close-search-panel");

  if (!searchInput) return;

  searchInput.addEventListener("input", () => {
    const q = searchInput.value.trim().toLowerCase();
    if (!q) {
      resultsPanel.classList.add("hidden");
      clearBtn.style.display = "none";
      return;
    }

    clearBtn.style.display = "block";
    queryText.textContent = `"${searchInput.value}"`;

    const matches = SEARCH_INDEX.filter(item => {
      return item.title.toLowerCase().includes(q) ||
             item.snippet.toLowerCase().includes(q) ||
             item.category.toLowerCase().includes(q);
    });

    if (matches.length === 0) {
      matchesList.innerHTML = `<div class="p-3 text-muted">No rules or rooms matched your search. Try keywords like "noise", "burst", "wound", "door", "queen", or a room name.</div>`;
    } else {
      matchesList.innerHTML = matches.map(m => `
        <div class="search-match-item" data-tab="${m.targetTab}" data-title="${encodeURIComponent(m.title)}">
          <div class="match-category">${m.category}</div>
          <div class="match-title">${m.title}</div>
          <div class="match-snippet">${m.snippet}</div>
        </div>
      `).join("");

      // Attach click events to jump to matched topics
      matchesList.querySelectorAll(".search-match-item").forEach(item => {
        item.addEventListener("click", () => {
          const tab = item.dataset.tab;
          switchToTab(tab);
          resultsPanel.classList.add("hidden");
        });
      });
    }

    resultsPanel.classList.remove("hidden");
  });

  clearBtn.addEventListener("click", () => {
    searchInput.value = "";
    resultsPanel.classList.add("hidden");
    clearBtn.style.display = "none";
    searchInput.focus();
  });

  closeBtn.addEventListener("click", () => {
    resultsPanel.classList.add("hidden");
  });
}
