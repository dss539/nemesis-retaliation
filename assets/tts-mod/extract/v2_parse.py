#!/usr/bin/env python3
"""
v2 recursive parser for Nemesis: Retaliation TTS save (workshop 3256296893).
Produces: v2/objects.json, v2/lua_script.lua, v2/lua_script_state.lua,
          v2/lua_roles.json, v2/gmnotes_taxonomy.json
Prints: parser sanity stats, top-level layout, Lua deck-role table, GMNotes taxonomy,
        expansion keyword hits in the Lua script.
"""
import struct, json, re, os
from collections import Counter

SAVE = '/home/smithers/tts-extract/nemesis_script_mod.bin'
OUT = '/home/smithers/tts-extract/v2'
URL_KEYS = {'FaceURL','BackURL','ImageURL','ImageSecondaryURL','DiffuseURL','MeshURL',
            'ColliderURL','AssetbundleURL','PDFUrl','AudioURL'}

os.makedirs(OUT, exist_ok=True)
data = open(SAVE,'rb').read()

def parse_key(data, i):
    j = data.find(b'\x00', i)
    if j < 0: raise ValueError(f'unterminated key @ {i}')
    return data[i:j].decode('latin-1','replace'), j+1

def parse_value(data, i, depth=0, content_end=None):
    if content_end is not None and i >= content_end:
        return None, i
    if depth > 300:
        raise ValueError(f'depth exceeded @ {i}')
    marker = data[i]
    if marker == 0x00:
        if content_end is None:
            return None, i  # end of stream
        i += 1
        while i < content_end and data[i] == 0x00:
            i += 1
        if i >= content_end:
            return None, i
        marker = data[i]; i += 1
    else:
        i += 1
    key, i = parse_key(data, i)
    if marker == 0x02:
        length = struct.unpack_from('<I', data, i)[0]; i += 4
        raw = data[i:i+length]
        i += length
        # strip trailing NUL(s) that TTS sometimes includes in the length
        val = raw.rstrip(b'\x00').decode('latin-1','replace')
    elif marker == 0x01:
        val = struct.unpack_from('<d', data, i)[0]; i += 8
    elif marker == 0x08:
        val = bool(data[i]); i += 1
    elif marker == 0x07:
        val = data[i]; i += 1
    elif marker == 0x10:
        val = struct.unpack_from('<i', data, i)[0]; i += 4
    elif marker == 0x12:
        # uint64 (8 bytes) — Steam IDs (OwnerSteamID etc.); undocumented in readme
        val = struct.unpack_from('<Q', data, i)[0]; i += 8
    elif marker in (0x03, 0x04):
        length = struct.unpack_from('<I', data, i)[0]; i += 4
        # TTS quirk: declared length = actual payload + 4 (counts the length field itself).
        # Verified empirically: visibleColor declares 38 (actual 34), TabStates el "0" 109 (105),
        # el "1" 110 (106). Payload includes trailing 0x00 terminator.
        end = i + length - 4
        fields = {}
        while i < end:
            res, i = parse_value(data, i, depth+1, end)
            if res is None: break
            k, v = res
            if k in fields:
                if not isinstance(fields[k], list):
                    fields[k] = [fields[k]]
                fields[k].append(v)
            else:
                fields[k] = v
        val = fields
    else:
        raise ValueError(f'unknown marker 0x{marker:02x} @ {i-1}')
    return (key, val), i

# ---- top-level parse ----
root = {}
i = 4  # skip 4-byte file header (0x20 2d 2e 00)
while i < len(data):
    try:
        res, i = parse_value(data, i, 0, len(data))
    except Exception as e:
        print(f'PARSE ERROR at offset {i}: {e}'); break
    if res is None:
        # skip trailing padding
        while i < len(data) and data[i] == 0x00: i += 1
        if i >= len(data): break
        continue
    k, v = res
    root[k] = v

print('=== TOP-LEVEL LAYOUT ===')
for k, v in root.items():
    if isinstance(v, dict):
        print(f'  {k:20s} object  ({len(v)} fields)')
    elif isinstance(v, str):
        print(f'  {k:20s} string  {len(v)} chars')
    else:
        print(f'  {k:20s} {type(v).__name__}  {v}')

# ---- sanity vs readme ----
os_ = root.get('ObjectStates')
obj_list = list(os_.values()) if isinstance(os_, dict) else []
print(f'\nObjectStates elements: {len(obj_list)}  (readme: ~1804 objects, content 2,214,864 B)')

# ---- recursive object records ----
def extract_urls(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'ContainedObjects':
                # children get their own records; don't attribute their URLs to the container
                continue
            if k in URL_KEYS and isinstance(v, str):
                out.append((k, v))
            else:
                extract_urls(v, out)
    elif isinstance(obj, list):
        for v in obj: extract_urls(v, out)

records = []
def walk(obj, parent_chain):
    rec = {
        'guid': obj.get('GUID') or '',
        'type': obj.get('Name') or '',
        'nickname': obj.get('Nickname') or '',
        'description': obj.get('Description') or '',
        'gmnotes': obj.get('GMNotes') or '',
        'card_id': obj.get('CardID') or '',
        'transform': obj.get('Transform') or {},
        'deck_nums': sorted(obj.get('CustomDeck', {}).keys()) if isinstance(obj.get('CustomDeck'), dict) else [],
        'parent': parent_chain,
        'urls': [],
    }
    extract_urls(obj, rec['urls'])
    # dedupe urls, keep first key
    seen = set(); uniq = []
    for k, u in rec['urls']:
        if u not in seen:
            seen.add(u); uniq.append((k, u))
    rec['urls'] = uniq
    records.append(rec)
    contained = obj.get('ContainedObjects')
    if isinstance(contained, dict):
        for co in contained.values():
            if isinstance(co, dict):
                chain = parent_chain + [(obj.get('Name') or '', obj.get('GUID') or '', obj.get('Nickname') or '')]
                walk(co, chain)

for o in obj_list:
    if isinstance(o, dict):
        walk(o, [])

print(f'Object records (incl. contained): {len(records)}')
top_records = [r for r in records if not r['parent']]
print(f'Top-level objects: {len(top_records)}')

type_counts = Counter(r['type'] for r in records)
print('\n=== OBJECT TYPE COUNTS ===')
for t, n in type_counts.most_common():
    print(f'  {t:24s} {n}')

all_urls = [u for r in records for _, u in r['urls']]
print(f'\nUnique URLs: {len(set(all_urls))}   refs: {len(all_urls)}   (readme: 1079 unique, ~4272 refs)')
urlkey_counts = Counter(k for r in records for k, _ in r['urls'])
print('URL refs by key:', dict(urlkey_counts.most_common()))

# ---- Lua script ----
lua = root.get('LuaScript') or ''
with open(os.path.join(OUT, 'lua_script.lua'), 'w') as f:
    f.write(lua)
state = root.get('LuaScriptState') or ''
with open(os.path.join(OUT, 'lua_script_state.lua'), 'w') as f:
    f.write(state)
print(f'\nLuaScript: {len(lua)} chars (readme: ~770 KB region), LuaScriptState: {len(state)} chars')

# gO definition check
m = re.search(r'[^\n]*gO\s*=\s*[^\n]*', lua)
print('gO definition:', m.group(0)[:120] if m else 'NOT FOUND')

# role assignments:  name = gO('guid')  and  name = getObjectFromGUID('guid')
assign = re.findall(r'([A-Za-z_]\w*)\s*=\s*(?:gO|getObjectFromGUID)\(\s*[\'"]?([0-9a-fA-F]{6})[\'"]?\s*\)', lua)
gocalls = re.findall(r'(?:gO|getObjectFromGUID)\(\s*[\'"]?([0-9a-fA-F]{6})[\'"]?\s*\)', lua)
print(f'Lua role assignments: {len(assign)}, total gO/getObjectFromGUID calls: {len(gocalls)}')

by_guid = {r['guid'].lower(): r for r in records}
rows = []
for var, guid in assign:
    rec = by_guid.get(guid.lower())
    rows.append({
        'role': var, 'guid': guid.lower(),
        'type': rec['type'] if rec else '-',
        'nickname': rec['nickname'] if rec else '-',
        'gmnotes': (rec['gmnotes'][:60] if rec and rec['gmnotes'] else '-'),
        'n_urls': len(rec['urls']) if rec else 0,
        'deck_nums': rec['deck_nums'] if rec else [],
        'contained': 1 if rec else 0,
    })
with open(os.path.join(OUT, 'lua_roles.json'), 'w') as f:
    json.dump(rows, f, indent=1)

print('\n=== LUA DECK/BAG ROLE TABLE (role = gO(\'guid\')) ===')
print(f'{"ROLE":28s} {"GUID":8s} {"TYPE":22s} {"NICKNAME":22s} {"GMNOTES":40s} {"URLS":4s} DECK#')
for r in sorted(rows, key=lambda x: x['role'].lower()):
    print(f'{r["role"][:28]:28s} {r["guid"]:8s} {r["type"][:22]:22s} {r["nickname"][:22]:22s} {r["gmnotes"][:40]:40s} {r["n_urls"]:<4d} {r["deck_nums"]}')

# top-level objects NOT referenced by any gO call
referenced = {g.lower() for g in gocalls}
unref = [r for r in top_records if r['guid'].lower() not in referenced]
print(f'\nTop-level objects NOT referenced by Lua: {len(unref)}')
for r in unref[:60]:
    print(f'  {r["type"][:22]:22s} {r["guid"]:8s} {r["nickname"][:30]:30s} gm={r["gmnotes"][:30]:30s} urls={len(r["urls"])}')

# ---- GMNotes taxonomy ----
gm_counter = Counter(r['gmnotes'] for r in records if r['gmnotes'])
with open(os.path.join(OUT, 'gmnotes_taxonomy.json'), 'w') as f:
    json.dump([{'gmnotes': k, 'count': v} for k, v in gm_counter.most_common()], f, indent=1)
print(f'\n=== GMNOTES TAXONOMY ({len(gm_counter)} distinct values, {sum(gm_counter.values())} objects) ===')
type_by_gm = {}
for r in records:
    if r['gmnotes']:
        type_by_gm.setdefault(r['gmnotes'], Counter())[r['type']] += 1
for v, n in gm_counter.most_common(80):
    t = type_by_gm[v].most_common(3)
    ts = ','.join(f'{x[0]}({x[1]})' for x in t)
    print(f'  {n:4d}  {v[:50]:50s}  {ts[:80]}')

# ---- expansion keyword hits in Lua ----
keywords = ['sangrevore','xyrian','contractor','insider','neoflesh','stretch','primeblood',
            'crimson despot','hunter','janitor','lab rat','medic','pilot','psychologist',
            'scientist','scout','sentry','soldier','survivor','xenobiologist','hacker',
            'mechanic','captain','android','convict','bounty hunter','laika','consultant',
            'uav operator','shambler','fleshbeast','butcher','metagorger','king','motherbrain',
            'cultist','twitchling','firespitter','ironclad','crawlmine','slasher','ghoul',
            'specter','shadow']
print('\n=== EXPANSION KEYWORD HITS IN LuaScript (count, first 2 lines) ===')
for kw in keywords:
    hits = [ln for ln in lua.split('\n') if kw.lower() in ln.lower()]
    if hits:
        print(f'  {kw:16s} {len(hits):4d}  ' + ' | '.join(h[:70] for h in hits[:2]))
    else:
        print(f'  {kw:16s}    0')

# ---- object JSON ----
with open(os.path.join(OUT, 'objects.json'), 'w') as f:
    json.dump(records, f)
print(f'\nWrote: {OUT}/objects.json, lua_script.lua, lua_script_state.lua, lua_roles.json, gmnotes_taxonomy.json')
