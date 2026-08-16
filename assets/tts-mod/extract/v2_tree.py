#!/usr/bin/env python3
"""Build v2 categorized tree from downloaded files + object records + roles.
Output: v2-dl/tree/... with CATALOG.md + manifest.json. Human-readable names."""
import json, os, re, shutil
from collections import defaultdict

V2 = '/home/smithers/tts-extract/v2'
DL = '/home/smithers/tts-extract/v2-dl'
TREE = os.path.join(DL, 'tree')

recs = json.load(open(os.path.join(V2, 'classification.json')))
roles = json.load(open(os.path.join(V2, 'lua_roles.json')))
mani = json.load(open(os.path.join(DL, 'manifest.json')))

# url -> list of object records
url_recs = defaultdict(list)
for r in recs:
    for k, u in r['urls']:
        if u:
            url_recs[u].append(r)

# role name for an object guid (prefer non-mechanical role)
role_by_guid = defaultdict(list)
for r in roles:
    role_by_guid[r['guid']].append(r['role'])

# category helpers
BASE_TAGS = {'action','event','attack','exploration','yellowitem','reditem','greenitem','wound'}
TOKEN_TAGS = {'oxygen','ammo','grenade','medpack','secure'}
KIT_NAMES = {'officer','medical support','heavy gun operator','combat engineer','recon','contractor'}

def slug(s):
    s = re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
    return s[:40] or 'unnamed'

def kit_of(rec):
    """return (kitname, kitguid) if record is inside a character kit bag, else None"""
    for p in rec['parent']:
        pn = (p[2] or '').strip().lower()
        if pn in KIT_NAMES or pn in ('captain','pilot','scout','mechanic','soldier','scientist',
                                     'sentry','hacker','lab rat','janitor','survivor','xenobiologist',
                                     'ceo','android','bounty hunter','medic','convict','psychologist',
                                     'hunter','sharpshooter','bioenhancment expert','uav operator'):
            return (p[2], p[1])
    return None

def room_bag_of(rec):
    """return role name if inside a room/corridor bag, else None"""
    for p in rec['parent']:
        pn = (p[2] or '').lower()
        if pn in ('roomiabag','roomibbag','roomicbag','roomiibag','corridorbag'):
            return pn.replace('bag','')
    return None

def category_for(rec, key):
    """returns (subdir, filename-stem) for a url field on a record"""
    t = rec['type']
    nick = rec['nickname'] or ''
    gm = rec['gmnotes'] or ''
    g = rec['guid'].lower()
    roles_here = role_by_guid.get(g, [])
    role = roles_here[0] if roles_here else ''
    gl = gm.lower()
    kit = kit_of(rec)
    roombag = room_bag_of(rec)

    if key == 'PDFUrl' or t == 'Custom_PDF':
        return ('rulebooks', slug(nick) if nick else (role or 'rulebook'))

    # 3D model / texture assets
    if key in ('MeshURL', 'AssetbundleURL', 'ColliderURL', 'DiffuseURL'):
        if t == 'Custom_Model':
            # room/corridor tiles carry numeric room-sequence gmnotes
            if gl.isdigit() and (roombag or ' room' in nick.lower() or nick.isupper()):
                sub = 'tiles/room'
                stem = roombag if roombag else slug(nick)
                return (sub, stem)
            if kit:
                return ('models/character', slug(kit[0]))
            if gl in ('adult','breeder','queen','larvae','creeper'):
                return ('models/intruder', gl)
            if gl == 'playerhealth':
                return ('models', 'player-health')
            return ('models', slug(nick) if nick else (role or 'model'))
        # bag textures (ImageURL/DiffuseURL of bags)
        if t in ('Bag','Custom_Model_Bag','Custom_Model_Infinite_Bag','Custom_Assetbundle_Bag'):
            stem = slug(nick) if nick else (role or 'bag')
            return ('bags', stem)
        return ('models', slug(nick) if nick else (role or slug(t)))

    # figure images
    if t == 'Figurine_Custom':
        stem = slug(nick) if nick else (kit[0] if kit else (role or 'figure'))
        return ('figures', stem)

    # CARDS — character kits first
    if t in ('Card','CardCustom'):
        if kit:
            return ('cards/character', slug(kit[0]))
        if gl in BASE_TAGS:
            return ('cards/game', gl)
        if gl in ('actiondiscard','eventdiscard','attackdiscard','explorationdiscard',
                  'yellowitemdiscard','reditemdiscard','greenitemdiscard','seriouswounddiscard'):
            return ('cards/game', gl.replace('discard','') + '-discard')
        if role in ('characterDraftDeck','startItemDeck','greenItemsDeck','redItemsDeck',
                    'yellowItemsDeck','seriouswoundDeck','missionTaskDeck','objectiveCoopDeck',
                    'objectiveMissonDeck','objectivePersonalDeck','objectiveCoopCustomDeck','robotDeck'):
            return ('cards/game', role.replace('Deck',''))
        if nick:
            return ('cards/character', slug(nick))
        return ('cards/game', 'card')

    # DECKS
    if t in ('Deck','DeckCustom'):
        if kit:
            return ('cards/character', slug(kit[0]))
        if gl in ('actiondiscard','eventdiscard','attackdiscard','explorationdiscard',
                  'yellowitemdiscard','reditemdiscard','greenitemdiscard','seriouswounddiscard'):
            return ('cards/game', gl.replace('discard','') + '-discard')
        if gl in BASE_TAGS:
            return ('cards/game', gl)
        stem = slug(nick) if nick else (role or 'deck')
        return ('cards/game', stem)

    # TOKENS
    if t == 'Custom_Token':
        if kit and not gl:
            return ('tokens/character', slug(kit[0]))
        if gl in TOKEN_TAGS:
            return ('tokens', gl)
        if gl in ('adulttoken','breedertoken','queentoken','larvatoken','creepertoken'):
            return ('tokens/intruder', gl.replace('token',''))
        if gl == 'hibernatoriumoff':
            return ('tokens/status', 'hibernatorium-off')
        return ('tokens', slug(nick) if nick else (role or 'token'))

    # TILES
    if t == 'Custom_Tile':
        if gl in ('adulttoken','breedertoken','queentoken','larvatoken','creepertoken'):
            return ('tokens/intruder', gl.replace('token',''))
        if gl in TOKEN_TAGS:
            return ('tokens', gl)
        if role in ('drawTile','autoEventTile','burstTile','roundTile','numpadSetTile',
                    'exploreNoiseTile','boarderTile','bagDevTile','weaponColTile','actColTile',
                    'centerCube','queenActivateTile','soundTile','rollAnimationTile','rollModeTile'):
            return ('tiles/table', role)
        if gl == 'active' or gl == 'inactive':
            return ('tiles/table', f'peek-{gl}')
        return ('tiles', slug(nick) if nick else (role or 'tile'))

    # BAGS
    if t in ('Bag','Custom_Model_Bag','Custom_Model_Infinite_Bag','Custom_Assetbundle_Bag'):
        stem = slug(nick) if nick else (role or 'bag')
        if gl in TOKEN_TAGS:
            return ('tokens', gl)
        if gl == 'enemybag':
            return ('tokens/intruder', stem)
        if roombag:
            return ('tiles/room', roombag)
        if role in ('roomIABag','roomIBBag','roomICBag','roomIIBag','corridorBag','doorBag'):
            return ('tiles/room', role.replace('Bag',''))
        return ('bags', stem)

    if t in ('3DText','Chinese_Checkers_Piece','HandTrigger','FogOfWarTrigger','Bowl'):
        return ('table', slug(t))
    if t == 'Custom_Dice':
        return ('tokens/table', 'dice')
    if t == 'Custom_Model':
        # room/corridor tile images on bare models
        if gl.isdigit():
            return ('tiles/room', roombag or 'room')
        return ('models', slug(nick) if nick else (role or 'model'))

    return ('misc', slug(t) if t else 'unknown')

# assign each manifest file
moved = []
counts = defaultdict(int)
for m in mani:
    url = m['url']
    recs_for_url = url_recs.get(url, [])
    fname = os.path.basename(m['file'])
    if not recs_for_url:
        # unsorted dir already; leave as is
        moved.append((os.path.join(DL, m['file']), os.path.join(TREE, m['file']), url))
        continue
    # choose primary record: top-level base > base Card/CardCustom (carries kit context) > other base
    prim = None
    for r in recs_for_url:
        if r['verdict'] == 'base' and not r['parent']:
            prim = r; break
    if prim is None:
        for r in recs_for_url:
            if r['verdict'] == 'base' and r['type'] in ('Card','CardCustom'):
                prim = r; break
    if prim is None:
        for r in recs_for_url:
            if r['verdict'] == 'base':
                prim = r; break
    if prim is None:
        prim = recs_for_url[0]
    key = next((k for k, u in prim['urls'] if u == url), 'ImageURL')
    sub, stem = category_for(prim, key)
    ext = os.path.splitext(fname)[1]
    counts[sub] += 1
    seq = counts[sub]
    newname = f'{stem}-{seq:03d}{ext}'
    dest_dir = os.path.join(TREE, sub)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, newname)
    # handle dupes
    n = 1
    while os.path.exists(dest):
        newname = f'{stem}-{seq:03d}-{n}{ext}'
        dest = os.path.join(dest_dir, newname)
        n += 1
    moved.append((os.path.join(DL, m['file']), dest, url))

for src, dst, url in moved:
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)

# manifest for tree
tree_mani = []
for src, dst, url in moved:
    tree_mani.append({'url': url, 'file': os.path.relpath(dst, TREE), 'size': os.path.getsize(dst)})
with open(os.path.join(TREE, 'manifest.json'), 'w') as f:
    json.dump(tree_mani, f, indent=1)

# catalog
lines = ['# Nemesis: Retaliation TTS Mod — v2 Base-Game Asset Tree',
         f'Source: workshop 3256296893 (save {"/home/smithers/tts-extract/nemesis_script_mod.bin"})',
         f'Files: {len(tree_mani)}   Size: {sum(m["size"] for m in tree_mani)/1e9:.2f} GB',
         'Classification: Lua role table + bag membership + GMNotes (base only; expansion/junk excluded).',
         '']
dirs = defaultdict(list)
for m in tree_mani:
    d = os.path.dirname(m['file'])
    dirs[d].append(os.path.basename(m['file']))
for d in sorted(dirs):
    lines.append(f'## {d} ({len(dirs[d])} files)')
    for fn in sorted(dirs[d])[:5]:
        lines.append(f'  - {fn}')
    if len(dirs[d]) > 5:
        lines.append(f'  - ... and {len(dirs[d])-5} more')
with open(os.path.join(TREE, 'CATALOG.md'), 'w') as f:
    f.write('\n'.join(lines))

print(f'tree files: {len(tree_mani)}')
from collections import Counter
dirc = Counter(os.path.dirname(m['file']) for m in tree_mani)
for d, n in sorted(dirc.items()):
    print(f'  {d:50s} {n}')
