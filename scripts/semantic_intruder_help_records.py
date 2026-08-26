from __future__ import annotations
import json


def build_intruder_help_records(repo, record, assertion, timing, participant, condition, operation):
    source=json.loads((repo/'docs/rules/source-extraction/intruder-help-sheet.json').read_text())
    occurrences={}
    metadata={}
    for side in source['sides']:
        for column in side['columns']:
            for row in column['rows']:
                occurrences[row['occurrenceId']]=row['printedInstruction']
                metadata[row['occurrenceId']]={'side':side['sideId'],'context':column['columnId']}
        row=side['bottomRow']
        occurrences[row['occurrenceId']]=row['printedInstruction']
        metadata[row['occurrenceId']]={'side':side['sideId'],'context':'bag-development'}

    expected={'QA-C-01','QA-C-02','QA-C-03','QA-R-01','QA-R-02','QA-B-01','QA-B-02','QA-B-03','QA-BOTTOM-01','QD-C-01','QD-C-02','QD-C-03','QD-R-01','QD-R-02','QD-B-01','QD-B-02','QD-B-03','QD-BOTTOM-01'}
    assert set(occurrences)==expected
    trigger_by_suffix={
        'C-01':'Queen-icon token back', 'C-02':'numbered Intruder token back (white Adult count and red Drone count)', 'C-03':'Larva-icon token back',
        'R-01':'Queen token front', 'R-02':'Drone, Adult, or Larva token front',
        'B-01':'Queen token front', 'B-02':'Drone or Adult token front', 'B-03':'Larva token front',
        'BOTTOM-01':'Blank token front',
    }
    records=[]

    for occurrence_id in sorted(expected):
        meta=metadata[occurrence_id]
        context=meta['context']
        side=meta['side']
        help_source_id='SRC-INTRUDER-HELP-QA' if side=='queen-alive' else 'SRC-INTRUDER-HELP-QD'
        source_assertion=assertion(f'SA-{occurrence_id}',help_source_id,f'{side} side / {context} / {occurrence_id}',['preconditions','operations'],occurrences[occurrence_id],f'docs/rules/source-extraction/intruder-help-sheet.json:{occurrence_id}')
        source_assertion['textKind']='verbatim'
        lifecycle_assertion=assertion(f'SA-{occurrence_id}-LIFE','SRC-RULEBOOK','printed pages 15, 25, and 30 / token lifecycle, Corridor capacity, Surprise Attacks',['preconditions','operations','partialResolution'],'After resolution, non-Blank tokens return to the matching pile and Blank returns to the bag unless printed text removes it. A Corridor holds 6 Intruder equivalents (Queen counts 4). An Intruder placed or moved into a Room with a Character immediately Attacks.','docs/rules/03-intruders-and-survival.md:INT-001')
        assertions=[source_assertion,lifecycle_assertion]
        if context=='corridor':
            anchor='tax.entity.spatial.corridor'; context_taxa=['tax.entity.spatial.corridor']; timing_relation='when-triggered'
        elif context=='room':
            anchor='tax.entity.spatial.room'; context_taxa=['tax.entity.spatial.room']; timing_relation='when-triggered'
        else:
            anchor='tax.process.temporal.phase.event'; context_taxa=['tax.scaffold.zone.intruder-bag']; timing_relation='during'
        participants=[participant('P-RULES','rules-system')]
        trigger_key=occurrence_id.split('-',1)[1]
        preconditions=[condition('C-SIDE','predicate',[{'predicate':f'Intruder Help side is {side}'}],[f'SA-{occurrence_id}']),condition('C-CONTEXT','predicate',[{'predicate':f'caller context is {context}'}],[f'SA-{occurrence_id}'])]
        token_condition=condition('C-TOKEN','predicate',[{'predicate':f'drawn token discriminator is {trigger_by_suffix[trigger_key]}'}],[f'SA-{occurrence_id}'])
        token_condition['tokenDiscriminator']={'context':context,'side':side,'sourceOccurrenceId':occurrence_id,'label':trigger_by_suffix[trigger_key]}
        preconditions.append(token_condition)
        ops=[]
        term_refs=[]; taxon_refs=context_taxa[:]; targets=[]
        if occurrence_id in {'QA-C-01'}:
            term_refs=['term.queen']; taxon_refs+=['tax.entity.agent.intruder.queen']
            ops=[operation('S01',1,'invoke-process','if-able','Queen','Activate Queen',[f'SA-{occurrence_id}'],conditions=['Queen activation is possible']),operation('S02',2,'place-component','must','P-RULES','Queen in caller Corridor',[f'SA-{occurrence_id}'],conditions=['Queen activation is not possible'])]
        elif occurrence_id=='QA-R-01':
            term_refs=['term.queen']; taxon_refs+=['tax.entity.agent.intruder.queen']
            ops=[operation('S01',1,'invoke-process','if-able','Queen','Activate Queen',[f'SA-{occurrence_id}'],conditions=['Queen activation is possible']),operation('S02',2,'place-component','must','P-RULES','Queen in caller Room',[f'SA-{occurrence_id}'],conditions=['Queen activation is not possible'])]
        elif occurrence_id in {'QA-B-01'}:
            term_refs=['term.queen','term.larva']; taxon_refs+=['tax.entity.agent.intruder.queen','tax.entity.agent.intruder.larva']
            ops=[operation('S01',1,'invoke-process','if-able','Queen','Activate Queen',[f'SA-{occurrence_id}'],conditions=['Queen is on map']),operation('S02',2,'place-component','if-able','P-RULES','2 Larva tokens into Intruder bag',[f'SA-{occurrence_id}'],conditions=['Queen is not on map'])]
        elif occurrence_id in {'QA-C-02','QD-C-02'}:
            term_refs=['term.adult','term.drone']; taxon_refs+=['tax.entity.agent.intruder.adult','tax.entity.agent.intruder.drone']
            face_resolution={'2':{'adultCount':2,'droneCount':0},'3':{'adultCount':3,'droneCount':0},'4':{'adultCount':4,'droneCount':0},'1+1':{'adultCount':1,'droneCount':1},'2+1':{'adultCount':2,'droneCount':1},'3+1':{'adultCount':3,'droneCount':1}}
            ops=[operation('S01',1,'place-component','if-able','P-RULES','Adults/Drones in caller Corridor from token-back counts',[f'SA-{occurrence_id}'],repeat={'tokenFaceResolutions':face_resolution,'adultCount':'white number on token back','droneCount':'red addend on token back','corridorCapacityEquivalentLimit':6,'sourceVisualBasis':'numbered token backs show white Adult count and red Drone addend'})]
        elif occurrence_id in {'QA-R-02','QD-R-02'}:
            term_refs=['term.adult','term.drone','term.larva']; taxon_refs+=['tax.entity.agent.intruder.adult','tax.entity.agent.intruder.drone','tax.entity.agent.intruder.larva']
            ops=[operation('S01',1,'place-component','if-able','P-RULES','1 Intruder matching token-front type in caller Room',[f'SA-{occurrence_id}'])]
        elif occurrence_id in {'QA-C-03','QD-C-03'}:
            term_refs=['term.larva']; taxon_refs+=['tax.entity.agent.intruder.larva']
            ops=[operation('S01',1,'place-component','if-able','P-RULES','1 Larva in caller Corridor',[f'SA-{occurrence_id}'])]
        elif occurrence_id=='QA-B-02':
            term_refs=['term.queen']; taxon_refs+=['tax.entity.agent.intruder.queen']
            ops=[operation('S01',1,'place-component','if-able','P-RULES','2 Queen tokens into Intruder bag',[f'SA-{occurrence_id}'])]
        elif occurrence_id in {'QA-B-03','QD-B-01','QD-B-03'}:
            term_refs=['term.drone']; taxon_refs+=['tax.entity.agent.intruder.drone']
            ops=[operation('S01',1,'draw-random','if-able','P-RULES','2 random Drone tokens from matching pile into Intruder bag',[f'SA-{occurrence_id}'])]
        elif occurrence_id=='QD-B-02':
            term_refs=['term.larva']; taxon_refs+=['tax.entity.agent.intruder.larva']
            ops=[operation('S01',1,'place-component','if-able','P-RULES','2 Larva tokens into Intruder bag',[f'SA-{occurrence_id}'])]
        elif occurrence_id in {'QD-C-01','QD-R-01'}:
            term_refs=['term.drone']; taxon_refs+=['tax.entity.agent.intruder.drone']
            destination='caller Corridor' if context=='corridor' else 'caller Room'
            ops=[operation('S01',1,'place-component','if-able','P-RULES',f'1 Drone in {destination}',[f'SA-{occurrence_id}']),operation('S02',2,'transition-zone','must','P-RULES','drawn Queen token',[f'SA-{occurrence_id}'],transition={'from':'drawn-token','to':'tax.scaffold.zone.removed-from-game'})]
        elif occurrence_id in {'QA-BOTTOM-01','QD-BOTTOM-01'}:
            term_refs=['term.adult']; taxon_refs+=['tax.entity.agent.intruder.adult']
            ops=[operation('S01',1,'draw-random','if-able','P-RULES','2 random Adult tokens from matching pile into Intruder bag',[f'SA-{occurrence_id}']),operation('S02',2,'transition-zone','must','P-RULES','drawn Blank token',[f'SA-{occurrence_id}'],transition={'from':'drawn-token','to':'tax.scaffold.zone.intruder-bag'})]
        else:
            raise AssertionError(occurrence_id)

        explicit_lifecycle=occurrence_id in {'QD-C-01','QD-R-01','QD-B-01','QA-BOTTOM-01','QD-BOTTOM-01'}
        if context=='room' and occurrence_id in {'QA-R-01','QA-R-02','QD-R-01','QD-R-02'}:
            targets=[{'targetId':f'T-{occurrence_id}-ATTACK','selectorRef':'rules-system','eligibleTaxonIds':['tax.entity.agent.character'],'cardinality':{'min':0,'max':1},'selectionMode':'deterministic-turn-order','visibility':'public'}]
            attack_op=operation('S99',99,'invoke-process','if-able','newly placed Intruder','immediate Intruder Attack',[f'SA-{occurrence_id}-LIFE'],conditions=['caller Room contains at least one Character'],invoke='SEM-INT-004')
            attack_op['targetRef']=f'T-{occurrence_id}-ATTACK'
            if occurrence_id=='QD-R-01':
                ops.insert(1,attack_op)
            else:
                ops.append(attack_op)
            for index,op in enumerate(ops,1):
                op['sequence']=index; op['stepId']=f'S{index:02d}'
        if occurrence_id=='QD-B-01':
            ops.append(operation(f'S{len(ops)+1:02d}',len(ops)+1,'transition-zone','must','P-RULES','drawn Queen token',[f'SA-{occurrence_id}'],transition={'from':'drawn-token','to':'tax.scaffold.zone.removed-from-game'}))
        elif not explicit_lifecycle:
            transition={'from':'drawn-token','to':'tax.scaffold.zone.token-pile'}
            if context=='bag-development': transition['positionRef']='sem.position.deck-bottom'
            ops.append(operation(f'S{len(ops)+1:02d}',len(ops)+1,'transition-zone','must','P-RULES','resolved non-Blank Intruder token',[f'SA-{occurrence_id}-LIFE'],transition=transition))

        if context=='corridor':
            for op in ops:
                if op['operationType']=='place-component':
                    op['notes']='Place only models that fit the 6-equivalent Corridor capacity; Queen counts as 4. Apply finite-model supply limits and continue.'

        records.append(record(
            f'SEM-IH-{occurrence_id}',f'Intruder Help {occurrence_id}','source-backed','dispatcher','official-primary','verbatim-structure',
            assertions,term_refs,sorted(set(taxon_refs)),[],timing(f'TW-IH-{occurrence_id}',anchor,timing_relation,f'per-{occurrence_id}-dispatch'),participants,'must',preconditions,[],[{'informationId':f'I-{occurrence_id}','subjectRef':'drawn token, caller context, placements, and lifecycle','audience':'public','revealTrigger':'draw/resolution','secrecy':'none'}],[],targets,ops,
            {'policy':'source-limited-components','unit':'requested model/token','onImpossible':'use the general finite-component rule; resolve remaining printed sentences'}, {'kind':'instantaneous-dispatch-row'}, {'policy':'one row per caller context and current Queen side'}, [], [], []))

    return records
