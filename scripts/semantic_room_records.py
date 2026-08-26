from __future__ import annotations
import json,re


def _norm(value):
    return re.sub(r'[^a-z0-9]+','-',value.lower()).strip('-')


def build_room_records(repo, record, assertion, timing, participant, condition, decision, operation):
    room_source=json.loads((repo/'docs/rules/source-extraction/room-help-sheet.json').read_text())
    identities=json.loads((repo/'docs/rules/vocabulary/named-component-identities.json').read_text())
    identity_by_title={}
    for item in identities['records']:
        if 'room-title' in item.get('observedRoleCounts',{}):
            for label in item.get('observedLabels',[]): identity_by_title.setdefault(_norm(label),[]).append(item['identityObservationId'])
    entries={item['printedNumber']:item for item in room_source['entries']}
    assert set(entries)=={f'{i:02d}' for i in range(1,26)}
    records=[]

    def source_assertions(number):
        entry=entries[number]
        rows=[]
        effect=assertion(f'SA-ROOM-{number}-E','SRC-ROOM-HELP',f'entry {number} {entry["printedTitle"]} / printedEffect',['preconditions','decisions','informationPolicy','costs','targets','operations'],entry['printedEffect'],f'docs/rules/source-extraction/room-help-sheet.json:{number}.printedEffect')
        effect['textKind']='verbatim'; rows.append(effect)
        for index,note in enumerate(entry['associatedNotes'],1):
            item=assertion(f'SA-ROOM-{number}-N{index:02d}','SRC-ROOM-HELP',f'entry {number} {entry["printedTitle"]} / associatedNotes[{index-1}]',['preconditions','decisions','informationPolicy','costs','targets','operations'],note,f'docs/rules/source-extraction/room-help-sheet.json:{number}.associatedNotes[{index-1}]')
            item['textKind']='verbatim'; rows.append(item)
        return rows

    def add(number, term_refs, taxon_refs, decisions, information, costs, targets, operations, partial='all-or-nothing-selection', unresolved=None):
        entry=entries[number]
        identity_candidates=sorted(set(identity_by_title.get(_norm(entry['printedTitle']),[])))
        assert len(identity_candidates)==1,(number,entry['printedTitle'],identity_candidates)
        status='source-backed-with-open-question' if unresolved else 'source-backed'
        interpretation='open-alternatives' if unresolved else 'verbatim-structure'
        assertions=source_assertions(number)
        records.append(record(
            f'SEM-ROOM-{number}',f'{entry["printedTitle"].title()} Room effect',status,'component-effect','official-component-reference',interpretation,
            assertions,['term.room',*term_refs],['tax.entity.spatial.room',*taxon_refs],identity_candidates,
            timing(f'TW-ROOM-{number}','tax.process.action.use-room','when-triggered',f'per-invoked-Room-{number}-effect'),[participant('P-PLAYER','decision-owner','tax.entity.agent.player'),participant('P-CHARACTER','actor','tax.entity.agent.character'),participant('P-RULES','rules-system')],'must',
            [condition(f'C-ROOM-{number}','predicate',[{'predicate':f'Room {number} effect was invoked by a legal source (including Use the Room or another Room/effect) and selected branch is fully resolvable'}],[assertions[0]['assertionId']])],decisions,
            information or [{'informationId':f'I-ROOM-{number}','subjectRef':'declared choices and public board changes','audience':'public','revealTrigger':'declaration/resolution','secrecy':'none'}],costs,targets,operations,
            {'policy':partial,'unit':f'Room {number} selected effect/branch','onImpossible':'invocation must satisfy the applicable whole-effect legality; a parent Use Room Action may be selected only when this branch resolves entirely; source-specific shortfall notes still apply'}, {'kind':'instantaneous-room-effect'}, {'policy':'repeatable only through distinct legal invocations; invocation source controls any Action cost'}, [], unresolved or [], []))

    # 02 Shelter
    add('02',['term.contamination-card','term.larva'],['tax.entity.component.card.contamination','tax.entity.agent.intruder.larva'],[],[{'informationId':'I-ROOM-02','subjectRef':'Contamination card identities; hidden INFECTED text is not scanned','audience':'owner-private','revealTrigger':'removal of card components only','secrecy':'hidden text remains unread'}],[],[],[
        operation('S01',1,'evaluate-condition','must','P-RULES','Character has no Larva',['SA-ROOM-02-E']),operation('S02',2,'transition-zone','must','P-PLAYER','all Contamination cards in hand without scanning',['SA-ROOM-02-E'],transition={'from':'tax.scaffold.zone.hand','to':'tax.scaffold.zone.removed-from-game'})])

    # 03 Emergency Room
    add('03',['term.serious-wound-card','term.character-health'],['tax.entity.component.card.serious-wound','tax.state.health'],[
        decision('D-ROOM-03-BRANCH','P-PLAYER','player-choice',1,1,False,'public-on-declaration',['restore up to 2 Health','discard 1 Serious Wound']),decision('D-ROOM-03-HEALTH','P-PLAYER','player-choice',0,2,True,'public-on-declaration',['0, 1, or 2 Health points']),decision('D-ROOM-03-WOUND','P-PLAYER','player-choice',1,1,False,'public-on-declaration',['owned Serious Wound to discard'])],None,[],[],[
        operation('S01',1,'change-value','may','P-PLAYER','restore chosen amount up to 2 Character Health',['SA-ROOM-03-E'],conditions=['restore Health branch'],decision_ref='D-ROOM-03-HEALTH',value_change={'amount':'player-chosen-0-to-2','value':'Health damage'}),operation('S02',2,'remove-component','must','P-RULES','selected Serious Wound',['SA-ROOM-03-E'],conditions=['discard Wound branch'],decision_ref='D-ROOM-03-WOUND')])

    # 04 Supply Room
    add('04',['term.item','term.regular-item','icon.greenItem','icon.redItem','icon.yellowItem','icon.secure'],['tax.entity.component.card.item','tax.entity.component.card.item.regular','tax.entity.component.token.secure'],[
        decision('D-ROOM-04-KEEP','P-PLAYER','unresolved',0,2,True,'source-unspecified',['exactly 2 if choosing to keep','any subset up to 2'])],
        [{'informationId':'I-ROOM-04','subjectRef':'three drawn Item identities and keep choice','audience':'source-unspecified-during-choice','revealTrigger':'kept Item placement/use as source requires','secrecy':'Room Help text does not state whether candidates/unchosen Items are shown'},{'informationId':'I-ROOM-04-KEPT','subjectRef':'kept Regular Item in Backpack','audience':'owner-private','revealTrigger':'source-defined use or reveal','secrecy':'Backpack placement does not itself reveal the Item'}],[],[],[
        operation('S01',1,'draw-random','must','P-RULES','1 Green, 1 Red, and 1 Yellow Item',['SA-ROOM-04-E']),operation('S02',2,'resolve-open-alternative','must','P-PLAYER','SEM-Q-004 Supply Room keep cardinality',['SA-ROOM-04-E'],decision_ref='D-ROOM-04-KEEP'),operation('S03',3,'transition-zone','must','P-RULES','kept Regular Items to Backpack',['SA-ROOM-04-E'],decision_ref='D-ROOM-04-KEEP',transition={'from':'drawn candidate set','to':'tax.scaffold.zone.backpack'}),operation('S04',4,'transition-zone','must','P-RULES','all unkept Items to their discard destinations',['SA-ROOM-04-E'],transition={'from':'drawn candidate set','to':'tax.scaffold.zone.discard-pile'})],unresolved=['SEM-Q-004'])

    # 05 Armory
    add('05',['term.tactical-gear-token','icon.ammoToken','icon.grenadeToken'],['tax.entity.component.token.tactical-gear'],[
        decision('D-ROOM-05-GAIN','P-PLAYER','player-choice',0,None,True,'public-on-placement',['available Ammo and Grenade tokens']),decision('D-ROOM-05-DISCARD','P-PLAYER','player-choice',0,None,True,'public-on-discard',['owned Tactical Gear tokens to discard once'])],None,[],[{'targetId':'T-ROOM-05-SLOTS','selectorRef':'P-PLAYER','eligibleTaxonIds':['tax.entity.component.slot.tactical-gear'],'cardinality':{'min':0,'max':None},'selectionMode':'player-choice','visibility':'public'}],[
        operation('S01',1,'choose','may','P-PLAYER','any owned Tactical Gear tokens to discard once before/during Action',['SA-ROOM-05-N01'],decision_ref='D-ROOM-05-DISCARD'),operation('S02',2,'remove-component','if-able','P-RULES','selected discarded Tactical Gear',['SA-ROOM-05-N01'],decision_ref='D-ROOM-05-DISCARD',notes='Return discarded tokens to their finite supply.'),operation('S03',3,'choose','may','P-PLAYER','any number of available Ammo/Grenade tokens',['SA-ROOM-05-E'],decision_ref='D-ROOM-05-GAIN',conditions=['all selected tokens have compatible empty slots and are available']),operation('S04',4,'place-component','if-able','P-RULES','selected tokens in compatible empty slots',['SA-ROOM-05-E','SA-ROOM-05-N01'],decision_ref='D-ROOM-05-GAIN',target_ref='T-ROOM-05-SLOTS',invoke='SEM-ITM-005')],'source-limited-components')

    # 06 Door Control
    add('06',['term.door','term.section','term.opened','term.closed'],['tax.entity.spatial.door','tax.entity.spatial.section','tax.state.opened','tax.state.closed'],[
        decision('D-ROOM-06-SECTION','P-PLAYER','player-choice',1,1,False,'public-on-declaration',['Section A','Section B','Section C']),decision('D-ROOM-06-DOORS','P-PLAYER','player-choice',0,None,True,'public-on-declaration',['Doors in selected Section and Open/Close state for each'])],None,[],[],[
        operation('S01',1,'choose','must','P-PLAYER','one Section',['SA-ROOM-06-E'],decision_ref='D-ROOM-06-SECTION'),operation('S02',2,'choose','may','P-PLAYER','any Doors and desired Open/Closed states',['SA-ROOM-06-E'],decision_ref='D-ROOM-06-DOORS'),operation('S03',3,'set-state','if-able','P-RULES','selected Door states',['SA-ROOM-06-E','SA-ROOM-06-N01'],decision_ref='D-ROOM-06-DOORS',conditions=['Closed state only where a Door slot exists'])])

    # 07 Security Robot Room
    room07_decisions=[decision('D-ROOM-07-BRANCH','P-PLAYER','player-choice',1,1,False,'public-on-declaration',['place Secure with Robot','reinforce adjacent Empty Corridor']),decision('D-ROOM-07-CORRIDOR','P-PLAYER','player-choice',1,1,False,'public-on-declaration',['eligible adjacent Empty Corridor'])]
    room07_targets=[{'targetId':'T-ROOM-07-CORRIDOR','selectorRef':'P-PLAYER','eligibleTaxonIds':['tax.entity.spatial.corridor'],'cardinality':{'min':1,'max':1},'selectionMode':'player-choice','visibility':'public'}]
    room07_ops=[operation('S01',1,'place-component','must','P-RULES','1 Secure token in Room containing Robot',['SA-ROOM-07-E'],conditions=['Secure branch'],notes='Target is deterministic: the Room containing the sole Robot; no player target choice.'),operation('S02',2,'set-state','must','P-RULES','selected adjacent Empty Corridor becomes Reinforced',['SA-ROOM-07-E'],conditions=['Reinforce branch','Corridor adjacent to Room containing Robot','Corridor does not lead to Hibernatorium','no Closed Door blocks the effect'],decision_ref='D-ROOM-07-CORRIDOR',target_ref='T-ROOM-07-CORRIDOR',notes='Discard any Noise marker on the Corridor before flipping it to Reinforced.')]
    add('07',['icon.secure','icon.robot','term.reinforced-corridor'],['tax.entity.component.token.secure','tax.entity.agent.robot','tax.state.corridor.reinforced'],room07_decisions,None,[],room07_targets,room07_ops)

    # 08 Gunnery Room
    add('08',['term.corridor','icon.redItem','icon.malfunction','icon.ammoToken','term.hit'],['tax.entity.spatial.corridor','tax.entity.component.card.item','tax.entity.component.marker.malfunction','tax.process.operation.hit','tax.symbol.die-result'],[
        decision('D-ROOM-08-CORRIDOR','P-PLAYER','player-choice',1,1,False,'public-on-declaration',['Corridor adjacent to a Room with a Red Item icon and without Malfunction'])],None,[],[
        {'targetId':'T-ROOM-08-CORRIDOR','selectorRef':'P-PLAYER','eligibleTaxonIds':['tax.entity.spatial.corridor'],'cardinality':{'min':1,'max':1},'selectionMode':'player-choice','visibility':'public'},{'targetId':'T-ROOM-08-INTRUDERS','selectorRef':'P-PLAYER','eligibleTaxonIds':['tax.entity.agent.intruder'],'cardinality':{'min':0,'max':None},'selectionMode':'player-choice','visibility':'public'}],[
        operation('S01',1,'select-target','must','P-PLAYER','eligible Corridor',['SA-ROOM-08-E'],decision_ref='D-ROOM-08-CORRIDOR',target_ref='T-ROOM-08-CORRIDOR'),operation('S02',2,'draw-random','must','P-RULES','Burst die result, as a die roll only and not a Burst Action',['SA-ROOM-08-E'],notes='No Burst Action is performed and no Ammo token is spent.'),operation('S03',3,'change-value','must','P-PLAYER','deal Hits equal to the die result among eligible Intruders in target Corridor',['SA-ROOM-08-E'],target_ref='T-ROOM-08-INTRUDERS',value_change={'amount':'Burst die result','valueTaxonId':'tax.process.operation.hit'},notes='Apply standard Hit allocation and finite Intruder/model limits; source does not provide a new target tie-break.'),operation('S04',4,'evaluate-condition','must','P-RULES','no Ammo token is spent because this is not a Burst Action',['SA-ROOM-08-N01'])])

    # 09 Pressure Control
    add('09',['icon.intruder'],['tax.entity.agent.intruder'],[
        decision('D-ROOM-09-INTRUDER','P-PLAYER','player-choice',1,1,False,'public-on-declaration',['one Intruder anywhere']),decision('D-ROOM-09-DIRECTION','P-PLAYER','player-choice',1,1,False,'public-on-declaration',['adjacent Room/Corridor destination'])],None,[],[{'targetId':'T-ROOM-09-INTRUDER','selectorRef':'P-PLAYER','eligibleTaxonIds':['tax.entity.agent.intruder'],'cardinality':{'min':1,'max':1},'selectionMode':'player-choice','visibility':'public'}],[
        operation('S01',1,'select-target','must','P-PLAYER','one Intruder anywhere in Facility',['SA-ROOM-09-E'],decision_ref='D-ROOM-09-INTRUDER',target_ref='T-ROOM-09-INTRUDER'),operation('S02',2,'move-entity','must','selected Intruder','adjacent location in chosen direction',['SA-ROOM-09-E','SA-ROOM-09-N01'],decision_ref='D-ROOM-09-DIRECTION',notes='Apply ordinary movement consequences: Closed Door blocks/destroys as source-defined, Noise is discarded when entering a Corridor, Corridor capacity applies, and entry into a Room with a Character causes an immediate Attack.'),operation('S03',3,'invoke-process','if-able','moved Intruder','immediate Intruder Attack when destination Room contains a Character',['SA-ROOM-09-E'],conditions=['destination Room contains a Character'],invoke='SEM-INT-004')])

    # 10 Alarm Room
    add('10',['term.corridor','icon.noise'],['tax.entity.spatial.corridor','tax.entity.component.marker.noise'],[
        decision('D-ROOM-10-CORRIDOR','P-PLAYER','player-choice',1,1,False,'public-on-declaration',['Corridor with Noise marker']),decision('D-ROOM-10-MODE','P-PLAYER','player-choice',1,1,False,'public-on-declaration',['resolve Noise marker','discard Noise marker'])],None,[],[],[
        operation('S01',1,'select-target','must','P-PLAYER','chosen Corridor Noise marker',['SA-ROOM-10-E'],decision_ref='D-ROOM-10-CORRIDOR'),operation('S02',2,'invoke-process','must','P-RULES','resolve selected Noise marker',['SA-ROOM-10-E'],conditions=['resolve mode'],decision_ref='D-ROOM-10-MODE'),operation('S03',3,'remove-component','must','P-RULES','selected Noise marker',['SA-ROOM-10-E'],conditions=['discard mode'],decision_ref='D-ROOM-10-MODE')])

    room11_decisions=[decision('D-ROOM-11-BRANCH','P-PLAYER','player-choice',1,1,False,'public-on-declaration',['gain Tactical Gear','draw Support Equipment']),decision('D-ROOM-11-GEAR','P-PLAYER','player-choice',0,None,True,'public-on-placement',['available Ammo tokens']),decision('D-ROOM-11-KEEP','P-PLAYER','player-choice',0,1,True,'source-unspecified',['keep 1 drawn Support Equipment','keep none']),decision('D-ROOM-11-DISCARD','P-PLAYER','player-choice',0,None,True,'public-on-discard',['owned Tactical Gear tokens to discard once before/during Action'])]
    room11_information=[{'informationId':'I-ROOM-11','subjectRef':'drawn Support Equipment candidates','audience':'source-unspecified-during-choice','revealTrigger':'kept card placement/use','secrecy':'Room Help text does not state whether candidates/discarded card are shown'},{'informationId':'I-ROOM-11-KEPT','subjectRef':'kept Support Equipment in class-appropriate Character storage','audience':'owner-private','revealTrigger':'source-defined use or reveal','secrecy':'storage placement does not itself reveal a private card'}]
    room11_operations=[operation('S01',1,'choose','may','P-PLAYER','any owned Tactical Gear tokens to discard once before/during Action',['SA-ROOM-11-N01'],decision_ref='D-ROOM-11-DISCARD'),operation('S02',2,'remove-component','if-able','P-RULES','selected discarded Tactical Gear',['SA-ROOM-11-N01'],decision_ref='D-ROOM-11-DISCARD',notes='Return discarded tokens to their finite supply.'),operation('S03',3,'place-component','if-able','P-RULES','selected available Ammo tokens in empty compatible slots',['SA-ROOM-11-E','SA-ROOM-11-N01'],conditions=['Tactical Gear branch'],decision_ref='D-ROOM-11-GEAR',invoke='SEM-ITM-005'),operation('S04',4,'draw-random','must','P-RULES','2 Support Equipment cards excluding Setup-used cards',['SA-ROOM-11-E','SA-ROOM-11-N02'],conditions=['Support Equipment branch']),operation('S05',5,'choose','may','P-PLAYER','keep 1 drawn Support Equipment or keep none',['SA-ROOM-11-E'],conditions=['Support Equipment branch'],decision_ref='D-ROOM-11-KEEP'),operation('S06',6,'transition-zone','may','P-RULES','kept Support Equipment to Character storage by Item class',['SA-ROOM-11-E'],conditions=['Support Equipment branch','one card kept'],decision_ref='D-ROOM-11-KEEP',transition={'from':'drawn candidate set','to':'Backpack, Hand slot, or Armor position by Item class'}),operation('S07',7,'transition-zone','must','P-RULES','all unkept Support Equipment to discard',['SA-ROOM-11-E'],conditions=['Support Equipment branch'],transition={'from':'drawn candidate set','to':'tax.scaffold.zone.discard-pile'})]
    add('11',['term.tactical-gear-token','term.support-equipment'],['tax.entity.component.token.tactical-gear','tax.entity.component.card.item.support'],room11_decisions,room11_information,[],[],room11_operations,'source-limited-components')

    # 12 Technical Corridor Entrance
    add('12',['term.room','term.attack','term.adult','term.noise-roll','icon.secure'],['tax.entity.spatial.room','tax.process.attack','tax.entity.agent.intruder.adult','tax.process.sequence.noise-roll','tax.entity.component.token.secure'],[
        decision('D-ROOM-12-DEST','P-PLAYER','player-choice',1,1,False,'public-on-declaration',['any placed Room in Facility'])],None,[],[{'targetId':'T-ROOM-12-DEST','selectorRef':'P-PLAYER','eligibleTaxonIds':['tax.entity.spatial.room'],'cardinality':{'min':1,'max':1},'selectionMode':'player-choice','visibility':'public'}],[
        operation('S01',1,'move-entity','must','P-CHARACTER','chosen placed Room anywhere in Facility',['SA-ROOM-12-E'],decision_ref='D-ROOM-12-DEST',target_ref='T-ROOM-12-DEST',notes='Source-specific remote movement ignores ordinary distance but still chooses an existing Room.'),operation('S02',2,'invoke-process','must','virtual Adult attacker with no miniature','Adult Intruder Attack targeting only the moved Character; Secure ignored',['SA-ROOM-12-E','SA-ROOM-12-N01','SA-ROOM-12-N02'],invoke='SEM-INT-004',notes='Treat as Adult; do not place an Intruder; target is the Character who moved; Secure tokens do not apply.'),operation('S03',3,'invoke-process','must','P-CHARACTER','Noise Roll after the Adult Attack',['SA-ROOM-12-N03'],invoke='SEM-NOISE-001')])

    # 13 Decontamination Room
    add('13',['term.contamination-card','icon.actionCard','icon.oxygen'],['tax.entity.component.card.contamination','tax.entity.component.card.action'],[],
        [{'informationId':'I-ROOM-13','subjectRef':'Contamination identities in deck/discard; hidden text not scanned','audience':'owner-private','revealTrigger':'component removal only','secrecy':'hidden text remains unread'}],
        [{'costId':'COST-ROOM-13-OXYGEN','payerRef':'P-CHARACTER','resourceTermId':'icon.oxygen','quantity':2,'selectionDecisionRef':None,'transition':{'from':'Character Oxygen supply','to':'spent'}}],[],[
        operation('S01',1,'evaluate-condition','must','P-RULES','Character has at least 2 Oxygen before selecting the Room Action',['SA-ROOM-13-N01']),operation('S02',2,'transition-zone','must','P-RULES','all Action cards in hand to discard',['SA-ROOM-13-E'],transition={'from':'tax.scaffold.zone.hand','to':'tax.scaffold.zone.discard-pile'}),operation('S03',3,'pay-cost','must','P-CHARACTER','COST-ROOM-13-OXYGEN',['SA-ROOM-13-E'],notes='Intrinsic Room cost; do not apply a second independent Oxygen change.'),operation('S04',4,'transition-zone','must','P-RULES','all Contaminations in deck/discard to removed from game without scanning',['SA-ROOM-13-E'],transition={'from':'Action deck and discard pile','to':'tax.scaffold.zone.removed-from-game'})])

    # 14 Landing Zone
    add('14',['term.tactical-gear-token','term.noise-roll','icon.lander'],['tax.entity.component.token.tactical-gear','tax.process.sequence.noise-roll','tax.entity.component.token.lander'],[
        decision('D-ROOM-14-BRANCH','P-PLAYER','player-choice',1,1,False,'public-on-declaration',['gain connected-slot Tactical Gear','try to enter Lander']),decision('D-ROOM-14-GEAR','P-PLAYER','player-choice',0,None,True,'public-on-placement',['available tokens from connected slots']),decision('D-ROOM-14-DISCARD','P-PLAYER','player-choice',0,None,True,'public-on-discard',['owned Tactical Gear tokens to discard once before/during Action'])],None,[],[],[
        operation('S01',1,'place-component','if-able','P-RULES','selected connected-slot Tactical Gear in compatible empty slots',['SA-ROOM-14-E','SA-ROOM-14-N01'],conditions=['Tactical Gear branch'],decision_ref='D-ROOM-14-GEAR'),operation('S02',2,'evaluate-condition','must','P-RULES','Lander token is in Landing Zone',['SA-ROOM-14-N02'],conditions=['Lander branch']),operation('S03',3,'invoke-process','must','P-CHARACTER','Noise Roll',['SA-ROOM-14-E'],conditions=['Lander branch'],invoke='SEM-NOISE-001'),operation('S04',4,'set-state','if-able','P-CHARACTER','sem.state.participation.in-lander',['SA-ROOM-14-N03'],conditions=['Lander branch','no Intruder in Room after Noise Roll']),operation('S05',5,'remove-component','may','P-RULES','selected owned Tactical Gear tokens once before/during Action',['SA-ROOM-14-N01'],decision_ref='D-ROOM-14-DISCARD',notes='Discarded tokens return to their finite supply and this choice may occur before or during the Action.')])

    # 15 Life Support Control A
    add('15',['term.section-a','icon.fire'],['tax.entity.spatial.section.a','tax.entity.component.marker.fire'],[
        decision('D-ROOM-15-BRANCH','P-PLAYER','player-choice',1,1,False,'public-on-declaration',['flip Section A Life Support','discard Fire anywhere']),decision('D-ROOM-15-FIRE','P-PLAYER','player-choice',1,1,False,'public-on-declaration',['Fire marker in any Room'])],None,[],[],[
        operation('S01',1,'set-state','must','P-RULES','Section A Life Support flips active/inactive',['SA-ROOM-15-E','SA-ROOM-15-N01'],conditions=['Life Support branch']),operation('S02',2,'remove-component','must','P-RULES','selected Fire marker anywhere',['SA-ROOM-15-E'],conditions=['discard Fire branch'],decision_ref='D-ROOM-15-FIRE')])

    # 16 Surgery Room
    add('16',['term.larva','term.contamination-card','term.serious-wound-card','icon.actionCard'],['tax.entity.agent.intruder.larva','tax.entity.component.card.contamination','tax.entity.component.card.serious-wound','tax.entity.component.card.action'],[
        decision('D-ROOM-16-BRANCH','P-PLAYER','player-choice',1,1,False,'public-on-declaration',['remove Larva and scan','discard Serious Wound']),decision('D-ROOM-16-WOUND','P-PLAYER','player-choice',1,1,False,'public-on-declaration',['owned Serious Wound'])],
        [{'informationId':'I-ROOM-16','subjectRef':'scanned Contamination hidden text','audience':'scanning-player','revealTrigger':'scan','secrecy':'other players do not gain source-granted access'}],[],[],[
        operation('S01',1,'transition-zone','must','P-RULES','all Action cards in hand to discard',['SA-ROOM-16-E'],conditions=['Larva branch'],transition={'from':'tax.scaffold.zone.hand','to':'tax.scaffold.zone.discard-pile'}),operation('S02',2,'remove-component','must','P-RULES','Larva from Character board',['SA-ROOM-16-E','SA-ROOM-16-N01'],conditions=['Larva branch','Character has Larva']),operation('S03',3,'inspect-private','must','P-PLAYER','all Contaminations in deck/discard',['SA-ROOM-16-E'],conditions=['Larva branch']),operation('S04',4,'transition-zone','must','P-RULES','scanned Infected Contaminations to removed from game',['SA-ROOM-16-E'],conditions=['Larva branch'],transition={'from':'Action deck and discard pile scan set','to':'tax.scaffold.zone.removed-from-game'}),operation('S05',5,'transition-zone','must','P-RULES','remaining scanned Contaminations back into Action deck',['SA-ROOM-16-N02'],conditions=['Larva branch'],transition={'from':'Action deck and discard pile scan set','to':'tax.scaffold.zone.deck'}),operation('S06',6,'shuffle','must','P-RULES','whole Action deck after remaining scanned Contaminations return',['SA-ROOM-16-N02'],conditions=['Larva branch']),operation('S07',7,'remove-component','must','P-RULES','selected Serious Wound',['SA-ROOM-16-E'],conditions=['Wound branch'],decision_ref='D-ROOM-16-WOUND')])

    # 17 Drilling Station
    add('17',['term.corridor','icon.robot'],['tax.entity.spatial.corridor','tax.entity.agent.robot'],[
        decision('D-ROOM-17-ENDPOINT','P-RULES','unresolved',1,1,False,'source-unspecified',['legal edge from Robot Room to Discovered or Undiscovered Room'])],[],[],[],[
        operation('S01',1,'place-component','must','P-RULES','new Corridor leading from Room with Robot',['SA-ROOM-17-E','SA-ROOM-17-N01'],decision_ref='D-ROOM-17-ENDPOINT')],unresolved=['SEM-Q-005'])

    # 18 Hibernatorium
    add('18',['term.hibernate','term.noise-roll'],['tax.process.procedure.hibernate','tax.process.sequence.noise-roll'],[],None,[],[],[
        operation('S01',1,'evaluate-condition','must','P-RULES','Hibernatorium is Active',['SA-ROOM-18-N01']),operation('S02',2,'invoke-process','must','P-CHARACTER','Noise Roll',['SA-ROOM-18-E'],invoke='SEM-NOISE-001'),operation('S03',3,'set-state','if-able','P-CHARACTER','sem.state.participation.hibernated',['SA-ROOM-18-E','SA-ROOM-18-N02'],conditions=['no Intruder in Room after Noise Roll'])])

    # 19 Life Support Control B
    add('19',['term.section-b'],['tax.entity.spatial.section.b'],[
        decision('D-ROOM-19-BRANCH','P-PLAYER','player-choice',1,1,False,'public-on-declaration',['flip Section B Life Support','inspect/reorder Anti-Aircraft tokens']),decision('D-ROOM-19-AA','P-PLAYER','player-choice',1,1,False,'owner-private',['either order of two Anti-Aircraft tokens'])],
        [{'informationId':'I-ROOM-19-AA','subjectRef':'both Anti-Aircraft identities, resulting order, and current top-token status','audience':'owner-private','revealTrigger':'later source-defined Anti-Aircraft reveal','secrecy':'player need not share, may state truth or lie, but cannot show the tokens; top token determines current Anti-Aircraft status'}],[],[],[
        operation('S01',1,'set-state','must','P-RULES','Section B Life Support flips active/inactive',['SA-ROOM-19-E','SA-ROOM-19-N01'],conditions=['Life Support branch']),operation('S02',2,'inspect-private','must','P-PLAYER','both Anti-Aircraft tokens',['SA-ROOM-19-E','SA-ROOM-19-N02','SA-ROOM-19-N03'],conditions=['Anti-Aircraft branch']),operation('S03',3,'set-state','must','P-PLAYER','Anti-Aircraft tokens in chosen private order',['SA-ROOM-19-E','SA-ROOM-19-N02','SA-ROOM-19-N03'],conditions=['Anti-Aircraft branch'],decision_ref='D-ROOM-19-AA')])

    # 20 Server Room
    add('20',['term.discovered','icon.computer','icon.malfunction','term.data-token'],['tax.state.discovery.discovered','tax.entity.component.marker.malfunction','tax.entity.component.token.data'],[
        decision('D-ROOM-20-BRANCH','P-PLAYER','player-choice',1,1,False,'public-on-declaration',['use Discovered Computer Room','gain Data token']),decision('D-ROOM-20-TARGET','P-PLAYER','player-choice',1,1,False,'public-on-declaration',['Discovered Computer Room without Malfunction'])],None,[],[{'targetId':'T-ROOM-20-TARGET','selectorRef':'P-PLAYER','eligibleTaxonIds':['tax.entity.spatial.room'],'cardinality':{'min':1,'max':1},'selectionMode':'player-choice','visibility':'public'}],[
        operation('S01',1,'invoke-process','must','P-CHARACTER','selected Discovered Computer Room effect',['SA-ROOM-20-E','SA-ROOM-20-N01'],conditions=['use Room branch','target is Discovered','target has Computer','target has no Malfunction'],decision_ref='D-ROOM-20-TARGET',target_ref='T-ROOM-20-TARGET'),operation('S02',2,'place-component','must','P-RULES','1 Data token on Character',['SA-ROOM-20-E'],conditions=['Data branch','Character has no Data token'],repeat={'availableSupply':5,'oncePerCharacter':True})])

    # 21 Cooling System
    add('21',['term.autodestruction-procedure'],['tax.process.procedure.autodestruction'],[],None,[],[],[
        operation('S01',1,'invoke-process','must','P-RULES','Autodestruction Procedure',['SA-ROOM-21-E'],invoke='SEM-AUTODESTRUCTION-001')])

    # 22 Life Support Control C
    add('22',['term.section-c','term.hibernatorium'],['tax.entity.spatial.section.c','tax.entity.spatial.room.hibernatorium'],[
        decision('D-ROOM-22-BRANCH','P-PLAYER','player-choice',1,1,False,'public-on-declaration',['flip Section C Life Support','activate Hibernatorium'])],None,[],[],[
        operation('S01',1,'set-state','must','P-RULES','Section C Life Support flips active/inactive',['SA-ROOM-22-E','SA-ROOM-22-N01'],conditions=['Life Support branch']),operation('S02',2,'set-state','must','P-RULES','Hibernatorium becomes Active',['SA-ROOM-22-E','SA-ROOM-22-N02'],conditions=['Hibernatorium branch','Hibernatorium is Inactive'])])

    # 23 Reactor
    add('23',['term.section','icon.autodestruction','term.anti-aircraft-token'],['tax.entity.spatial.section','tax.entity.component.token.autodestruction','tax.entity.component.token.anti-aircraft'],[],None,[],[],[
        operation('S01',1,'transition-zone','must','P-RULES','all Life Support status tokens, Autodestruction token, and both Anti-Aircraft tokens',['SA-ROOM-23-E'],transition={'from':'board/track','to':'tax.scaffold.zone.removed-from-game'}),operation('S02',2,'set-state','must','P-RULES','all Sections treated Inactive',['SA-ROOM-23-N01']),operation('S03',3,'set-state','must','P-RULES','Anti-Aircraft treated Inactive',['SA-ROOM-23-N01']),operation('S04',4,'transition-zone','if-able','P-RULES','Autodestruction token even if on Round track',['SA-ROOM-23-N02'],transition={'from':'board/track','to':'tax.scaffold.zone.removed-from-game'}),operation('S05',5,'set-state','must','P-RULES','Life Support, Anti-Aircraft, and Autodestruction cannot be turned on again',['SA-ROOM-23-N03'])])

    # 24 Escape Shuttle
    add('24',['term.escape','term.noise-roll'],['tax.process.procedure.escape','tax.process.sequence.noise-roll'],[],None,[],[],[
        operation('S01',1,'invoke-process','must','P-CHARACTER','Noise Roll',['SA-ROOM-24-E'],invoke='SEM-NOISE-001'),operation('S02',2,'set-state','if-able','P-CHARACTER','sem.state.participation.escaped',['SA-ROOM-24-E','SA-ROOM-24-N01'],conditions=['no Intruder in Room after Noise Roll','Escape Shuttle still available']),operation('S03',3,'set-state','if-able','P-RULES','Escape Shuttle permanently unavailable',['SA-ROOM-24-N02'],conditions=['Character Escapes using Shuttle'])])

    # 25 Nest
    add('25',['term.egg-token','term.noise-roll','term.heavy-item','term.hand-slot'],['tax.entity.component.token.egg','tax.process.sequence.noise-roll','tax.entity.component.card.item.heavy','tax.entity.component.slot.hand'],[
        decision('D-ROOM-25-EGG','P-PLAYER','player-choice',1,1,False,'public-on-declaration',['take 1 Egg as Heavy Item','destroy 1 Egg']),decision('D-ROOM-25-DISCARD','P-PLAYER','player-choice',0,1,True,'owner-private-until-discard',['held Item to discard before taking Egg'])],None,[],[{'targetId':'T-ROOM-25-HAND','selectorRef':'P-PLAYER','eligibleTaxonIds':['tax.entity.component.slot.hand'],'cardinality':{'min':1,'max':1},'selectionMode':'player-choice','visibility':'public'}],[
        operation('S01',1,'choose','must','P-PLAYER','take or destroy 1 Egg from Nest border space',['SA-ROOM-25-E','SA-ROOM-25-N01','SA-ROOM-25-N02'],decision_ref='D-ROOM-25-EGG'),operation('S02',2,'choose','may','P-PLAYER','discard one held Item before taking Egg',['SA-ROOM-25-N01'],conditions=['take mode','no legal empty Hand slot for the Heavy Egg'],decision_ref='D-ROOM-25-DISCARD'),operation('S03',3,'remove-component','may','P-RULES','selected held Item',['SA-ROOM-25-N01'],conditions=['take mode','held Item selected'],decision_ref='D-ROOM-25-DISCARD',notes='Discarded Item follows normal Item discard/lifecycle rules.'),operation('S04',4,'move-entity','must','selected Egg','empty Hand slot as a Heavy Item',['SA-ROOM-25-N02'],conditions=['take mode'],target_ref='T-ROOM-25-HAND',repeat={'availableEggSupply':5}),operation('S05',5,'remove-component','must','P-RULES','selected Egg',['SA-ROOM-25-E'],conditions=['destroy mode']),operation('S06',6,'invoke-process','must','P-RULES','Nest-destroyed condition update after Egg removal',['SA-ROOM-25-E','SA-ROOM-25-N01'],invoke='SEM-NEST-DESTROYED-001'),operation('S07',7,'invoke-process','must','P-CHARACTER','Noise Roll',['SA-ROOM-25-E'],invoke='SEM-NOISE-001')])

    room07=next(item for item in records if item['ruleId']=='SEM-ROOM-07')
    room07_rulebook=assertion('SA-ROOM-07-RB','SRC-RULEBOOK','printed page 37 / broken Robot effects unavailable',['preconditions','operations'],'All effects mentioning a Robot with a Malfunction are unavailable.','docs/rulebooks/rulebook_text.txt:lines 6015–6022')
    room07['sourceAssertions'].append(room07_rulebook)
    room07['authority']['highest']='official-primary'
    room07['preconditions'].append(condition('C-ROOM-07-ROBOT','predicate',[{'predicate':'Robot used by Security Robot Room is not broken'}],['SA-ROOM-07-RB']))
    for op in room07['operations']:
        op['sourceAssertionIds'].append('SA-ROOM-07-RB'); op['conditionRefs'].append('C-ROOM-07-ROBOT')

    room09=next(item for item in records if item['ruleId']=='SEM-ROOM-09')
    room09_rulebook=assertion('SA-ROOM-09-RB','SRC-RULEBOOK','printed pages 25 and 30 / Surprise Attacks and Corridor capacity',['operations','partialResolution'],'An Intruder moved into a Room with a Character immediately Attacks. Corridor capacity is 6 equivalents and Queen counts as 4.','docs/rules/03-intruders-and-survival.md:INT-002')
    room09['sourceAssertions'].append(room09_rulebook)
    room09['authority']['highest']='official-primary'
    room09['operations'][1]['sourceAssertionIds'].append('SA-ROOM-09-RB')
    room09['operations'][1]['notes']='Destination must be an adjacent Room/Corridor in the chosen direction and must respect Corridor capacity (6 equivalents; Queen counts 4).'
    room09['preconditions'].append(condition('C-ROOM-09-ATTACK','predicate',[{'predicate':'selected Intruder destination is a Room containing at least one Character'}],['SA-ROOM-09-RB'],scope='operation-guard'))
    room09['operations'].append(operation(f"S{len(room09['operations'])+1:02d}",len(room09['operations'])+1,'invoke-process','if-able','moved Intruder','immediate Intruder Attack',['SA-ROOM-09-RB'],invoke='SEM-INT-004'))
    room09['operations'][-1]['conditionRefs']=['C-ROOM-09-ATTACK']

    room12=next(item for item in records if item['ruleId']=='SEM-ROOM-12')
    room12_faq=assertion('SA-ROOM-12-FAQ','SRC-FAQ','Rooms #3 / Technical Corridor Entrance Attack prevention',['operations'],'The virtual Adult Attack caused by Technical Corridor Entrance may be prevented by effects that prevent Intruder Attacks.','docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U19')
    room12['sourceAssertions'].append(room12_faq)
    room12['authority']['highest']='official-errata'
    room12_attack=next(item for item in room12['operations'] if item.get('invokeRuleId')=='SEM-INT-004')
    room12_attack['sourceAssertionIds'].append('SA-ROOM-12-FAQ')
    room12_attack['notes'] += ' Prevention/replacement effects that prevent Intruder Attacks may be used in the normal pre-resolution window.'

    room17=next(item for item in records if item['ruleId']=='SEM-ROOM-17')
    room17_faq=assertion('SA-ROOM-17-FAQ','SRC-FAQ','Rooms #1 / Drilling Station broken Robot',['preconditions','operations'],'The Drilling Station cannot create a Corridor if the Robot is broken.','docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U17')
    room17['sourceAssertions'].append(room17_faq)
    room17['authority']['highest']='official-errata'
    room17['preconditions'].append(condition('C-ROOM-17-ROBOT','predicate',[{'predicate':'Robot used by Drilling Station is not broken'}],['SA-ROOM-17-FAQ']))
    room17['operations'][0]['sourceAssertionIds'].append('SA-ROOM-17-FAQ')
    room17['operations'][0]['conditionRefs'].append('C-ROOM-17-ROBOT')

    room19=next(item for item in records if item['ruleId']=='SEM-ROOM-19')
    room19_rulebook=assertion('SA-ROOM-19-RB','SRC-RULEBOOK','printed page 37 / Anti-Aircraft token secrecy and current status',['informationPolicy','operations'],'The top Anti-Aircraft token indicates current status. The inspecting player may share or lie about the tokens but may not show them.','docs/rules/03-intruders-and-survival.md:INT-009')
    room19['sourceAssertions'].append(room19_rulebook)
    room19['authority']['highest']='official-primary'
    room19['operations'].append(operation(f"S{len(room19['operations'])+1:02d}",len(room19['operations'])+1,'evaluate-condition','must','P-RULES','top Anti-Aircraft token determines current system status; token faces cannot be shown',['SA-ROOM-19-RB']))

    room03=next(item for item in records if item['ruleId']=='SEM-ROOM-03')
    room03_rb=assertion('SA-ROOM-03-RB','SRC-RULEBOOK','printed page 18 / restore fewer Health points',['decisions','operations'],'A player may always restore fewer Health points than the amount described by an effect.','docs/rulebooks/rulebook_text.txt:lines 3821–3823')
    room03['sourceAssertions'].append(room03_rb); room03['authority']['highest']='official-primary'; room03['operations'][0]['sourceAssertionIds'].append('SA-ROOM-03-RB')
    room04=next(item for item in records if item['ruleId']=='SEM-ROOM-04')
    room04_rb=assertion('SA-ROOM-04-RB','SRC-RULEBOOK','printed page 28 / Regular Item storage and Room availability',['preconditions','operations','informationPolicy'],'Regular Items are held in the Backpack, and Room effects cannot be used when the Room has a Malfunction.','docs/rulebooks/rulebook_text.txt:lines 4849–4865')
    room04['sourceAssertions'].append(room04_rb); room04['authority']['highest']='official-primary'
    for op in room04['operations']:
        op['sourceAssertionIds'].append('SA-ROOM-04-RB')
    room05=next(item for item in records if item['ruleId']=='SEM-ROOM-05')
    room05_rb=assertion('SA-ROOM-05-RB','SRC-RULEBOOK','printed pages 16 and 29 / Tactical Gear slots and finite supply',['preconditions','operations','partialResolution'],'Tactical Gear tokens come from finite supplies and must occupy compatible empty slots; selection must be legal before placement.','docs/rules/04-items-and-equipment.md:ITM-005')
    room05['sourceAssertions'].append(room05_rb); room05['authority']['highest']='official-primary'; room05['operations'][-1]['sourceAssertionIds'].append('SA-ROOM-05-RB')
    room06=next(item for item in records if item['ruleId']=='SEM-ROOM-06')
    room06_rb=assertion('SA-ROOM-06-RB','SRC-RULEBOOK','printed pages 22–23 / Door states',['preconditions','operations'],'Destroyed Doors behave as Open and cannot be Closed again; closing requires a Door slot.','docs/rules/02-character-actions.md:Doors')
    room06['sourceAssertions'].append(room06_rb); room06['authority']['highest']='official-primary'; room06['operations'][-1]['sourceAssertionIds'].append('SA-ROOM-06-RB'); room06['preconditions'].append(condition('C-ROOM-06-NOT-DESTROYED','predicate',[{'predicate':'selected Door is not Destroyed'}],['SA-ROOM-06-RB'],scope='operation-guard')); room06['operations'][-1]['conditionRefs'].append('C-ROOM-06-NOT-DESTROYED')
    room08=next(item for item in records if item['ruleId']=='SEM-ROOM-08')
    room08_rb=assertion('SA-ROOM-08-RB','SRC-RULEBOOK','printed page 40 / Hit and die-result semantics',['operations','targets'],'Hits are assigned to eligible Intruders under the official Hit procedure; the Gunnery Room note is a die roll, not a Burst Action.','docs/rulebooks/rulebook_text.txt:lines 5940–5982')
    room08['sourceAssertions'].append(room08_rb); room08['authority']['highest']='official-primary'; room08['operations'][1]['sourceAssertionIds'].append('SA-ROOM-08-RB'); room08['operations'][2]['sourceAssertionIds'].append('SA-ROOM-08-RB')
    room10=next(item for item in records if item['ruleId']=='SEM-ROOM-10')
    room10['operations'][1]['operationType']='invoke-selected-process'; room10['operations'][1]['objectRef']='resolve selected Noise marker through exact Room-context Intruder Help dispatch'; room10['operations'][1]['notes']='Remove the selected marker, draw the token, use its front only, and dispatch by current Queen side plus token front; do not invent a pile-bottom order.'; room10['operations'][1]['dispatchRuleIds']=['SEM-IH-QA-R-01','SEM-IH-QA-R-02','SEM-IH-QD-R-01','SEM-IH-QD-R-02']
    room10_rb=assertion('SA-ROOM-10-RB','SRC-RULEBOOK','printed page 25 / Noise marker resolution',['operations'],'Noise markers resolve through an Intruder token draw and context-specific Help Sheet row; nonexistent markers cannot be resolved.','docs/rules/02-character-actions.md:Noise')
    room10['sourceAssertions'].append(room10_rb); room10['authority']['highest']='official-primary'; room10['operations'][1]['sourceAssertionIds'].append('SA-ROOM-10-RB')
    room13=next(item for item in records if item['ruleId']=='SEM-ROOM-13')
    room13_rb=assertion('SA-ROOM-13-RB','SRC-RULEBOOK','printed page 13 / Oxygen suffocation restriction',['preconditions','costs','operations'],'The Room Action cannot be performed with 1 or fewer Oxygen; all discarded Action cards are public in the discard pile.','docs/rulebooks/rulebook_text.txt:lines 4368–4375')
    room13['sourceAssertions'].append(room13_rb); room13['authority']['highest']='official-primary'; room13['operations'][0]['sourceAssertionIds'].append('SA-ROOM-13-RB'); room13['operations'][1]['sourceAssertionIds'].append('SA-ROOM-13-RB'); room13['operations'][2]['sourceAssertionIds'].append('SA-ROOM-13-RB')
    room14=next(item for item in records if item['ruleId']=='SEM-ROOM-14')
    room14_rb=assertion('SA-ROOM-14-RB','SRC-RULEBOOK','printed pages 16 and 37–38 / Tactical Gear and Lander',['preconditions','operations','partialResolution'],'Connected slot supplies are finite and tokens discarded during the Action return to supply; successful Lander entry becomes the in-Lander state and is checked against Intruder presence after Noise.','docs/rulebooks/rulebook_text.txt:lines 5953–5979')
    room14['sourceAssertions'].append(room14_rb); room14['authority']['highest']='official-primary'; room14['operations'][0]['sourceAssertionIds'].append('SA-ROOM-14-RB'); room14['operations'][-1]['sourceAssertionIds'].append('SA-ROOM-14-RB')
    room16=next(item for item in records if item['ruleId']=='SEM-ROOM-16')
    room16_rb=assertion('SA-ROOM-16-RB','SRC-RULEBOOK','printed page 13 / Action-card discard visibility',['operations','informationPolicy'],'Action cards discarded by the Room effect enter the face-up discard pile; remaining scanned Contaminations return before the whole deck is reshuffled.','docs/rules/02-character-actions.md:ACT-CARD-001')
    room16['sourceAssertions'].append(room16_rb); room16['authority']['highest']='official-primary'; room16['operations'][0]['sourceAssertionIds'].append('SA-ROOM-16-RB'); room16['operations'][4]['sourceAssertionIds'].append('SA-ROOM-16-RB'); room16['operations'][5]['sourceAssertionIds'].append('SA-ROOM-16-RB')
    room11=next(item for item in records if item['ruleId']=='SEM-ROOM-11')
    room11_rb=assertion('SA-ROOM-11-RB','SRC-RULEBOOK','printed pages 16 and 29 / Equipment storage and Tactical Gear slots',['preconditions','operations','informationPolicy'],'Kept Support Equipment is placed according to its Item class; Tactical Gear tokens use compatible empty slots and discarded tokens return to limited supplies.','docs/rules/04-items-and-equipment.md:ITM-005')
    room11['sourceAssertions'].append(room11_rb); room11['authority']['highest']='official-primary'
    for op in room11['operations']:
        op['sourceAssertionIds'].append('SA-ROOM-11-RB')

    shelter_identity=sorted(set(identity_by_title[_norm(entries['02']['printedTitle'])]))
    assert len(shelter_identity)==1
    records.append(record(
        'SEM-ROOM-02-SECURE','Shelter permanent always-secured status','source-backed','constraint','official-errata','verbatim-structure',
        [assertion('SA-ROOM-02-FAQ','SRC-FAQ','Rooms #2 / Shelter always secured',['operations','duration','stacking'],'The Shelter “always secured” is a permanent Room status, not a Secure token; it prevents Attacks from incoming Intruders. Up to 3 additional Secure tokens may exist and are discarded first.','docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U18')],
        ['term.room','icon.secure'],['tax.entity.spatial.room','tax.entity.component.token.secure'],shelter_identity,
        timing('TW-ROOM-02-SECURE','tax.entity.spatial.room','when-triggered','continuous-Shelter-status-and-per-incoming-Intruder'),[participant('P-RULES','rules-system')],'must',[],[],[{'informationId':'I-ROOM-02-SECURE','subjectRef':'permanent secured status and additional Secure token count','audience':'public','revealTrigger':'continuous','secrecy':'none'}],[],[],
        [operation('S01',1,'set-state','must','P-RULES','sem.state.room.always-secured',['SA-ROOM-02-FAQ']),operation('S02',2,'evaluate-condition','must','P-RULES','permanent status prevents Attacks from incoming Intruders',['SA-ROOM-02-FAQ']),operation('S03',3,'evaluate-condition','must','P-RULES','up to 3 additional Secure tokens are separate and discarded first',['SA-ROOM-02-FAQ'])],
        {'policy':'per-effect-check','unit':'incoming Attack or Secure-token-consuming effect','onImpossible':'permanent status is never consumed; separate Secure tokens resolve first'}, {'kind':'permanent-room-status'}, {'policy':'one permanent status plus standard maximum 3 additional Secure tokens'}, [], [], []))

    prohibited_identities=[]
    for number in ('04','12','25'):
        values=sorted(set(identity_by_title[_norm(entries[number]['printedTitle'])])); assert len(values)==1; prohibited_identities.extend(values)
    records.append(record(
        'SEM-ROOM-STATIC-PROHIBITIONS','Room Secure/Malfunction prohibition graphics','source-backed','constraint','official-component-reference','verbatim-structure',
        [assertion('SA-ROOM-PROHIBITIONS','SRC-ROOM-HELP','Rooms 04, 12, and 25 upper-right prohibition graphics',['operations','duration'],'Supply Room, Technical Corridor Entrance, and Nest display no-Secure; Nest also displays no-Malfunction. These are persistent Room properties, not removable markers.','docs/rules/source-extraction/room-help-sheet.json:functionalIconOccurrences')],
        ['term.room','icon.secure','icon.malfunction'],['tax.entity.spatial.room','tax.entity.component.token.secure','tax.entity.component.marker.malfunction'],sorted(prohibited_identities),
        timing('TW-ROOM-PROHIBITIONS','tax.entity.spatial.room','when-triggered','continuous-Room-property-and-per-placement-attempt'),[participant('P-RULES','rules-system')],'must',[],[],[{'informationId':'I-ROOM-PROHIBITIONS','subjectRef':'no-Secure/no-Malfunction Room properties','audience':'public','revealTrigger':'continuous','secrecy':'none'}],[],[],
        [operation('S01',1,'set-state','must','Rooms 04, 12, and 25','sem.state.room.secure-prohibited',['SA-ROOM-PROHIBITIONS']),operation('S02',2,'set-state','must','Room 25','sem.state.room.malfunction-prohibited',['SA-ROOM-PROHIBITIONS'])],
        {'policy':'per-effect-check','unit':'attempt to place matching token/marker','onImpossible':'prohibited placement does not occur; enclosing effect follows its source partial-resolution rule'}, {'kind':'permanent-room-status'}, {'policy':'one persistent prohibition state per printed graphic'}, [], [], []))

    records.append(record(
        'SEM-DATA-TOKEN-001','Data token persistent ownership','source-backed','constraint','official-primary','verbatim-structure',
        [assertion('SA-DATA-TOKEN','SRC-RULEBOOK','printed page 7 / Data token',['operations','duration'],'A Character gains a Data token using the Server Room. Once gained, it cannot be lost or traded.','docs/rulebooks/rulebook_text.txt:lines 803–806')],
        ['term.data-token'],['tax.entity.component.token.data'],[],timing('TW-DATA-TOKEN','tax.entity.component.token.data','when-triggered','continuous-after-gain'),[participant('P-CHARACTER','owner','tax.entity.agent.character'),participant('P-RULES','rules-system')],'must',[],[],[{'informationId':'I-DATA-TOKEN','subjectRef':'Data token ownership','audience':'public','revealTrigger':'gain/continuous','secrecy':'none'}],[],[],
        [operation('S01',1,'set-state','must','P-RULES','Data token remains owned by gaining Character',['SA-DATA-TOKEN']),operation('S02',2,'evaluate-condition','must','P-RULES','Data token cannot be lost or traded',['SA-DATA-TOKEN'])],
        {'policy':'per-effect-check','unit':'attempted loss/trade','onImpossible':'the attempted transfer/loss does not occur'}, {'kind':'persistent-after-gain'}, {'policy':'at most one Data token per Character under Server Room effect'}, [], [], []))

    nest_identity=sorted(set(identity_by_title[_norm(entries['25']['printedTitle'])])); assert len(nest_identity)==1
    records.append(record(
        'SEM-NEST-DESTROYED-001','Nest destroyed condition','source-backed','constraint','official-errata','source-composed',
        [assertion('SA-NEST-DESTROYED','SRC-RULEBOOK','printed page 7 / Nest is Destroyed',['operations','outcomes','duration'],'The Nest is Destroyed when the Facility is Destroyed or no Eggs remain because Characters took/destroyed them.','docs/rulebooks/rulebook_text.txt:lines 821–825'),assertion('SA-NEST-FIRE-FAQ','SRC-FAQ','Rooms #4 / Fire in Nest at game end',['operations'],'A Fire marker in the Nest does not make the Nest Destroyed while Eggs remain.','docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U20')],
        ['term.nest','term.egg-token','icon.fire'],['tax.entity.spatial.room.nest','tax.entity.component.token.egg','tax.entity.component.marker.fire'],nest_identity,timing('TW-NEST-DESTROYED','tax.entity.spatial.room.nest','when-triggered','continuous-condition-and-after-Egg/Facility-change'),[participant('P-RULES','rules-system')],'must',[],[],[{'informationId':'I-NEST-DESTROYED','subjectRef':'Egg count, Facility state, Fire, Nest status','audience':'public','revealTrigger':'continuous','secrecy':'none'}],[],[],
        [operation('S01',1,'set-state','must','Nest','sem.state.room.nest-destroyed',['SA-NEST-DESTROYED'],conditions=['Facility is Destroyed']),operation('S02',2,'set-state','must','Nest','sem.state.room.nest-destroyed',['SA-NEST-DESTROYED'],conditions=['no Eggs remain because Characters took/destroyed them']),operation('S03',3,'evaluate-condition','must','P-RULES','Fire in Nest alone does not destroy Nest while Eggs remain',['SA-NEST-FIRE-FAQ'])],
        {'policy':'per-effect-check','unit':'Nest-destruction check','onImpossible':'Fire alone does not substitute for either source-defined trigger'}, {'kind':'persistent-once-destroyed'}, {'policy':'one Nest destroyed state'}, [{'condition':'Facility destroyed OR no Eggs remain from take/destroy','result':'Nest destroyed'}], [], []))

    # Make every OR-branch decision an explicit ordered operation instead of
    # relying on prose guards alone. This preserves target/card decisions that
    # individual branch operations already reference.
    for item in records:
        branch_decisions=[row['decisionId'] for row in item['decisions'] if row['decisionId'].endswith('-BRANCH')]
        if not branch_decisions:
            continue
        assert len(branch_decisions)==1
        branch_id=branch_decisions[0]
        if any(row.get('decisionRef')==branch_id for row in item['operations']):
            continue
        for index,row in enumerate(item['operations'],2):
            row['sequence']=index
            row['stepId']=f'S{index:02d}'
        item['operations'].insert(0,operation('S01',1,'choose','must','P-PLAYER','one printed OR branch',[item['sourceAssertions'][0]['assertionId']],decision_ref=branch_id))

    room14=next(item for item in records if item['ruleId']=='SEM-ROOM-14')
    discard_ops=[op for op in room14['operations'] if op.get('decisionRef')=='D-ROOM-14-DISCARD']
    room14['operations']=[op for op in room14['operations'] if op.get('decisionRef')!='D-ROOM-14-DISCARD']
    room14['operations'][1:1]=discard_ops
    for index,op in enumerate(room14['operations'],1):
        op['sequence']=index; op['stepId']=f'S{index:02d}'
    room13=next(item for item in records if item['ruleId']=='SEM-ROOM-13')
    room13['informationPolicy'].append({'informationId':'I-ROOM-13-DISCARD','subjectRef':'Action cards discarded by Decontamination Room','audience':'public','revealTrigger':'discard','secrecy':'cards enter the face-up discard pile'})
    room20=next(item for item in records if item['ruleId']=='SEM-ROOM-20')
    room20_data=assertion('SA-ROOM-20-RB','SRC-RULEBOOK','printed page 7 / Data token limit and persistence',['preconditions','operations','duration'],'There are five Data tokens; once gained by a Character, a Data token cannot be lost or traded.','docs/rulebooks/rulebook_text.txt:lines 803–806')
    room20['sourceAssertions'].append(room20_data); room20['authority']['highest']='official-primary'; room20['operations'][1]['sourceAssertionIds'].append('SA-ROOM-20-RB')
    room21=next(item for item in records if item['ruleId']=='SEM-ROOM-21')
    room21['authority']['highest']='official-primary'; room21['sourceAssertions'].append(assertion('SA-ROOM-21-RB','SRC-RULEBOOK','printed page 38 / Autodestruction cross-reference',['operations'],'Cooling System activates the Autodestruction Procedure described in the rulebook.','docs/rulebooks/rulebook_text.txt:lines 6117–6132')); room21['operations'][0]['sourceAssertionIds'].append('SA-ROOM-21-RB')
    room25=next(item for item in records if item['ruleId']=='SEM-ROOM-25')
    room25['operations'][0]['notes']='The Nest supply contains five Eggs; after taking or destroying the final Egg, invoke the persistent Nest-destroyed state.'

    return records
