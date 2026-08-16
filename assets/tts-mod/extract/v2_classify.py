#!/usr/bin/env python3
"""
v2 classifier v2: Lua-authoritative base/expansion split.
Primary: GUIDs named in recallNeoflesh/recallSangrevores/recallCarnomorph = expansion;
base role GUIDs (attacksDeck/eventDeck/explorationDeck/queenHealthDeck/intruder bags
as first-assigned) = base. Heuristics (gmnotes/nickname/type) as fallback.
Output: v2/classification.json with per-object verdict + per-URL verdict.
"""
import json, re
from collections import Counter

recs = json.load(open('/home/smithers/tts-extract/v2/objects.json'))
roles = json.load(open('/home/smithers/tts-extract/v2/lua_roles.json'))
lua = open('/home/smithers/tts-extract/v2/lua_script.lua', encoding='latin-1').read()

by_guid = {r['guid'].lower(): r for r in recs}

# ---- 1. Lua-authoritative expansion GUIDs ----
# every object the expansion recall functions wire up
exp_guid_sets = {
    'Neoflesh': ['a24dc8','61a87c','abbdd0','99e2ce','595bcc','ecc8e6','f31180',
                 'a00d06','c36ee8','fd7091','e0feed','1ca1ec','84381e','f6fec4','63aef2'],
    'Sangrevores': ['dd1eda','3a25fc','58aa1c','3b65b3','d181aa','405099','37f835',
                    'f7fd5f','a0f2a3','4abca0','aff77d','7347e2','ebef8b','7cb24e'],
    'Carnomorph': ['2e8e9d','9aefbc','0da709','6963a5','c2c9ea','81dd12','4b660f',
                   'c13884','231d79','47fde0','3be840','db891d','c74454','a1a031'],
}
expansion_guids = set()
for v in exp_guid_sets.values():
    expansion_guids.update(v)

# xyrian/insider/contractors expansions from role table
extra_exp_roles = ['xyrianActivationDeck','xyrianAllegiance','xyrianAllegianceToken',
                   'xyrianEventDeck','xyrianExplorationDeck','xyrianFBag','xyrianInjuryBag',
                   'xyrianPhase','xyrianStatusBag','xyrianTracerBag',
                   'insiderCard','insiderDeck','insiderFig','insiderHealth','insiderRunaway',
                   'pickContractorsDeck','pickCustomContractorsDeck']
for r in roles:
    if r['role'] in extra_exp_roles:
        expansion_guids.add(r['guid'])

# additional Lua-derived GUID sets (verified against lua_script.lua)
expansion_guids.update(['347097','9fad4f','17d7ea'])          # xyrian hide-list group
expansion_guids.update(['d06e50','c7c3ee','5187fe','623fca','0f95fb','eef078'])  # carnomorph "Body" models
expansion_guids.update(['164dc0','dcaac4','3edcd3','d63508'])  # expansion storage boxes: Carnomorph, InsiderExpansion, SangrevoresExpansion, NeofleshExpansion

# gameBox is the base storage box but CONTAINS expansion boxes — neutral ancestor:
# children must self-classify rather than inherit "base" from it
neutral_ancestors = {'a64f43'}

junk_nicks = {'trashbag','prototo','other','prototype stuff'}

# ---- 2. Base role GUIDs (first assignment per role, minus expansion) ----
base_roles = ['attacksDeck','eventDeck','explorationDeck','queenHealthDeck',
              'larvaeBag','adultBag','breederBag','queenBag','larvaeFBag','adultFBag',
              'breederFBag','queenFBag','nestBag','eggBag','intruderBag']
base_guids = set()
for r in roles:
    if r['role'] in base_roles:
        base_guids.add(r['guid'])
base_guids -= expansion_guids

# additional Lua-derived base GUID sets (verified against lua_script.lua)
base_guids.update(['0a9555','c31c41','c8758b','54f2f8','22147f','657f92','79e72b','7563b9','491d11','76301e'])  # player boards
base_guids.update(['733f1e','f05941','ae6191','863a00','ce0e9f','390db1','d78290','0cdfcc','d13ff6','1d51f6'])  # player health
base_guids.update(['89a391','536804','a7ddb5','a457a5'])      # hiddenCorridorsGUID
base_guids.update(['6c75b4','0b3190'])                        # antiAircraftGUIDTable
base_guids.update(['dc15cb','b97889'])                        # turnTiles
base_guids.update(['afc863','c8edca','393bf7','12c65e','f938a2','9f95fd','35b95f','5af8f2','4ee1f2'])  # unnamed table UI
base_guids.update(['8bd555','cb2d64','3253d4'])              # rulebook PDFs
base_guids.update(['de16dc'])                                # mod credit tile
base_guids.update(['d21df3'])                                # hibernatorium state token
base_guids.update(['0e8d84'])                                # Exploring Drone figurine (base mechanic)
base_guids.update(['f1f48c'])                                # Primebloods marker bag (base lifeform)
base_guids.update(['6855bb'])                                # Shared Contractor deck (base Contractor shared actions)

# ---- 3. mechanical/tabletop base objects (from role table) ----
mech_roles = ['corridorBag','roomIABag','roomIBBag','roomICBag','roomIIBag',
              'doorBag','fireBag','malfunctionBag','secureBag','healthBag',
              'ammoBag','grenadeBag','medpackBag','oxygenBag','dataTokenBag',
              'trapBag','carcassBag','scanner','firstPlayerToken','turnMarker',
              'autoDestructionToken','airlockToken','robot','robotDeck','robotToken',
              'shuttleFigure','landingZone','hibUnexplored','hiddenRoom','boarderTile',
              'gameBox','playerHelpBag','intruderHelp','characterDraftDeck',
              'startItemDeck','greenItemsDeck','redItemsDeck','yellowItemsDeck',
              'seriouswoundDeck','missionTaskDeck','objectiveCoopDeck',
              'objectiveMissonDeck','objectivePersonalDeck','objectiveCoopCustomDeck',
              'noiseBag','burstRollDice','shootRollDice','noiseRollDice','rollBowl',
              'rollAnimationTile','rollModeTile','roundTile','soundTile','numpadSetTile',
              'drawTile','bagDevTile','autoEventTile','burstTile','weaponColTile',
              'actColTile','centerCube','queenActivateTile','exploreNoiseTile',
              'zoneHide','locTableControl','soundboard1','soundboard2','soundboard3',
              'soundboard4','soundboard5','soundboard6','landerPilotSoundBoard',
              'mutationMarker','mutationDeck','taintedDeck','contaminationDeck']
for r in roles:
    if r['role'] in mech_roles:
        base_guids.add(r['guid'])
base_guids -= expansion_guids  # mech_roles may have re-added expansion GUIDs; subtract again

# ---- 4. classification ----
def gm_base(g):
    return g in ('action','event','attack','exploration','yellowitem','reditem','greenitem',
                 'wound','oxygen','ammo','grenade','medpack','secure','malfunction','fire',
                 'playerhealth','adulttoken','breedertoken','queentoken','larvae','creeper',
                 'adult','breeder','queen','noise','trap','carcass','seriouswound','dog',
                 'actiondiscard','eventdiscard','attackdiscard','explorationdiscard',
                 'yellowitemdiscard','reditemdiscard','greenitemdiscard','seriouswounddiscard',
                 'shadowdiscard') and not g.startswith('xyrian')

def gm_exp(g):
    g2 = g.lower()
    return g2.startswith('xyrian') or g2 in ('shadow','tainted','mutation','crawlmine',
        'crawlminebuff','slasher','slasherbuff','cultistbuff','twitchlingbuff',
        'firespitterbuff','ironcladbuff','firespitter','ironclad','slashertoken')

base_char_names = {'officer','medical support','heavy gun operator','combat engineer','recon','contractor'}
exp_char_names = {'captain','pilot','scout','mechanic','soldier','scientist','sentry','hacker',
    'lab rat','janitor','survivor','xenobiologist','ceo','android','bounty hunter','medic',
    'convict','psychologist','hunter','sharpshooter','bioenhancment expert','uav operator',
    'laika','consultant'}
base_intruder_nicks = {'larva','larvae','adult','breeder','queen','egg tokens'}
exp_intruder_nicks = {'shamblerbag','shamblerfbag','fleshbeastbag','fleshbeastfbag','butcherbag',
    'butcherfbag','metagorgerbag','metagorgerfbag','kingbag','kingtokenbag','kinghealth',
    'motherbrainbag','cultistbag','cultistdeadbag','twitchlingbag','twitchlingtokenbag',
    'firespitterbag','firespitterfbag','ironcladbag','crawlminebag','slasherbag','slashertokenbag',
    'ghoulbag','ghoultokenbag','specterbag','spectertokenbag','shadowbag'}

# propagate group verdict to contained objects (fallback for records whose parent
# chain contains an unclassified group)
def ancestor_verdict(r):
    for p in reversed(r['parent']):
        pr = by_guid.get(p[1].lower())
        if pr is None:
            continue
        if pr['guid'].lower() in neutral_ancestors:
            continue  # gameBox: don't stamp children with its verdict
        if pr.get('verdict') in ('base','expansion','junk'):
            return pr['verdict'], (pr['nickname'] or pr['type'] or pr['guid'], pr['reason'])
    return None, None

for r in recs:
    g = r['guid'].lower()
    nick = (r['nickname'] or '').lower()
    r['verdict'] = 'unknown'
    r['reason'] = ''
    r['group'] = None
    if nick in junk_nicks:
        r['verdict'] = 'junk'; r['reason'] = f'junk bag: {r["nickname"]}'
    # 1) GUID-level (Lua authority)
    elif g in expansion_guids:
        r['verdict'] = 'expansion'; r['reason'] = 'Lua expansion GUID'
    elif g in base_guids:
        r['verdict'] = 'base'; r['reason'] = 'Lua base/mech GUID'
    else:
        # 2) ancestor group verdict (bags/decks carry their content's verdict)
        av, ar = ancestor_verdict(r) if r['parent'] else (None, None)
        if av:
            r['verdict'] = av
            r['reason'] = f"contained in {ar[0]}: {ar[1]}"
        # 3) group nicknames (any level — kits/bags inside gameBox self-classify)
        elif nick in exp_intruder_nicks or nick in exp_char_names or 'insider' in nick or 'xyrian' in nick:
            r['verdict'] = 'expansion'; r['reason'] = f'expansion nickname: {r["nickname"]}'
        elif nick in base_intruder_nicks or nick in base_char_names:
            r['verdict'] = 'base'; r['reason'] = f'base nickname: {r["nickname"]}'
        elif nick in ('neoflesh','sangrevores','carnomorph','insiderexpansion',
                      'neofleshexpansion','sangrevoresexpansion'):
            r['verdict'] = 'expansion'; r['reason'] = f'expansion box: {r["nickname"]}'
        # 4) GMNotes fallback (only reached when no ancestor verdict)
        elif gm_exp(r['gmnotes']):
            r['verdict'] = 'expansion'; r['reason'] = f'expansion GMNotes: {r["gmnotes"]}'
        elif gm_base(r['gmnotes']):
            r['verdict'] = 'base'; r['reason'] = f'base GMNotes: {r["gmnotes"]}'
        # 5) unnamed table props w/ 0 urls -> base (they're UI/mechanics)
        elif not r['urls'] and r['type'] in ('HandTrigger','FogOfWarTrigger','3DText'):
            r['verdict'] = 'base'; r['reason'] = 'UI/table prop'

for r in recs:
    if r['verdict'] == 'unknown' and r['parent']:
        av, ar = ancestor_verdict(r)
        if av:
            r['verdict'] = av
            r['reason'] = f"contained in {ar[0]}: {ar[1]}"

# ---- 5. stats ----
vc = Counter(r['verdict'] for r in recs)
print('=== VERDICT COUNTS (1800 records) ===')
for v, n in vc.most_common():
    print(f'  {v:12s} {n}')

unknown = [r for r in recs if r['verdict'] == 'unknown']
print(f'\n=== UNKNOWN ({len(unknown)}) ===')
for r in unknown:
    print(f'  {r["type"][:22]:22s} {r["guid"]:8s} nick={r["nickname"][:26]:26s} gm={r["gmnotes"][:24]:24s} urls={len(r["urls"])}')

# ---- 6. per-URL verdict ----
url_verdict = {}   # url -> set of verdicts
for r in recs:
    for k, u in r['urls']:
        url_verdict.setdefault(u, set()).add(r['verdict'])

incl = [u for u, vs in url_verdict.items() if 'base' in vs]
excl = [u for u, vs in url_verdict.items() if vs == {'expansion'}]
print(f'\n=== URL VERDICTS ===')
print(f'  total unique: {len(url_verdict)}')
print(f'  include (base ref): {len(incl)}')
print(f'  expansion-only (exclude): {len(excl)}')
print(f'  unknown-only: {len([u for u,vs in url_verdict.items() if vs == {"unknown"}])}')

# how many unique urls does each expansion lifeform exclusively own?
for name, guids in exp_guid_sets.items():
    urls = set()
    for g in guids:
        r = by_guid.get(g)
        if r:
            for k, u in r['urls']:
                urls.add(u)
    shared = {u for u in urls if u in incl}
    print(f'  {name:12s} guid-set urls: {len(urls):4d}  (shared w/ base: {len(shared)})')

# save url verdicts
with open('/home/smithers/tts-extract/v2/url_verdicts.json', 'w') as f:
    json.dump({'include': sorted(incl), 'exclude': sorted(excl),
               'unknown': sorted(u for u, vs in url_verdict.items() if vs == {'unknown'})}, f, indent=1)
with open('/home/smithers/tts-extract/v2/classification.json', 'w') as f:
    json.dump(recs, f, indent=1)
print('\nWrote v2/classification.json + v2/url_verdicts.json')
