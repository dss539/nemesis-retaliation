#!/usr/bin/env python3
from __future__ import annotations
import collections,json,re,unicodedata
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]; DIR=REPO/'docs/rules/vocabulary'
def load(name): return json.loads((DIR/name).read_text())
def nk(s): return re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKC',s).replace('’',"'").replace('“','"').replace('”','"').lower()).strip('-')
def main():
 failures=[]; source=load('source-term-inventory.json'); named=load('named-component-identities.json'); vocab=load('canonical-vocabulary.json'); aliases=load('alias-registry.json'); review=load('vocabulary-review-gates.json'); coverage=load('coverage.json')
 occ=source.get('occurrences') or []; source_ids=[x.get('sourceTermId') for x in occ]; by_id={x['sourceTermId']:x for x in occ}
 if len(source_ids)!=len(set(source_ids)) or source_ids!=[f'ST-{i:05d}' for i in range(1,len(occ)+1)]: failures.append({'check':'source term IDs'})
 for x in occ:
  if nk(x['termText'])!=x['normalizedKey'] or not (REPO/x['sourcePath']).exists(): failures.append({'check':'source term projection','id':x['sourceTermId']})
 expected_source={'occurrences':1853,'uniqueNormalizedKeys':1194}
 if source['counts']['occurrences']!=1853 or source['counts']['uniqueNormalizedKeys']!=1194: failures.append({'check':'source counts','actual':source['counts']})
 # Named identities must contain only the four selected observed roles and exact-key groups.
 selected_roles={'room-title','objective-or-game-term-title','card-or-reference-title','licensed-digital-structured-key'}; groups=named.get('records') or []; named_ids={x['identityObservationId'] for x in groups}; named_source=[]
 for g in groups:
  rows=g.get('sourceOccurrences') or []; named_source+=rows
  if any(r['observedRole'] not in selected_roles or r['sourceTermId'] not in by_id or by_id[r['sourceTermId']]['normalizedKey']!=g['normalizedExactStringKey'] for r in rows): failures.append({'check':'named identity group','id':g['identityObservationId']})
 if named.get('counts')!={'sourceOccurrences':643,'exactStringGroups':501,'multiSourceGroups':85,'groupsWithMultipleObservedSpellings':30}: failures.append({'check':'named identity counts','actual':named.get('counts')})
 # Controlled vocabulary labels/IDs are unique and fully source-cited.
 entries=vocab.get('entries') or []; term_ids={e['termId'] for e in entries}; labels=[e['canonicalLabel'].casefold() for e in entries]
 if len(term_ids)!=len(entries) or len(set(labels))!=len(labels) or 'term.primeblood' in term_ids: failures.append({'check':'canonical ID/label uniqueness'})
 icon_entries=[e for e in entries if e['status']=='accepted-existing-icon-glossary']; proposed=[e for e in entries if e['status']=='proposed-authority-derived']
 if len(entries)!=167 or len(icon_entries)!=50 or len(proposed)!=117: failures.append({'check':'canonical counts'})
 if {e.get('existingIdentifier') for e in icon_entries}!={r.get('existingIdentifier') for r in occ if r['observedRole']=='official-icon-label'}: failures.append({'check':'icon vocabulary closure'})
 for e in entries:
  evidence=e.get('authorityEvidence') or []
  if not evidence or any(x.get('sourceTermId') not in by_id for x in evidence): failures.append({'check':'canonical evidence','termId':e['termId']})
 # Alias targets/scopes/evidence are closed; accepted source-scoped art aliases retain exact tuples.
 alias_rows=aliases.get('aliases') or []; alias_ids={a['aliasId'] for a in alias_rows}
 if aliases.get('counts')!={'aliases':8,'acceptedAliases':7,'proposedReviewAliases':1,'nonAliasBoundaries':5,'reviewGates':2}: failures.append({'check':'alias counts'})
 for a in alias_rows:
  if bool(a.get('targetTermId'))==bool(a.get('targetNamedIdentityId')): failures.append({'check':'alias target cardinality','id':a['aliasId']})
  if a.get('targetTermId') and a['targetTermId'] not in term_ids: failures.append({'check':'alias term target','id':a['aliasId']})
  if a.get('targetNamedIdentityId') and a['targetNamedIdentityId'] not in named_ids: failures.append({'check':'alias identity target','id':a['aliasId']})
  if any(e.get('sourceTermId') not in by_id for e in a.get('sourceEvidence') or []): failures.append({'check':'alias source evidence','id':a['aliasId']})
  for t in a.get('sourceTuples') or []:
   p=t.get('sourcePath')
   if p and not (REPO/p).exists(): failures.append({'check':'alias source tuple','id':a['aliasId'],'path':p})
 if not all(a['targetTermId']=='icon.intruder' for a in alias_rows[:2]): failures.append({'check':'Primeblood official equivalence'})
 if len(aliases.get('nonAliasBoundaries') or [])!=5: failures.append({'check':'non-alias boundaries'})
 personal_alias=next((a for a in alias_rows if a.get('aliasId')=='AL-003'),None)
 if not personal_alias or personal_alias.get('status')!='accepted-source-scoped-alias' or personal_alias.get('reviewGateId') is not None or (personal_alias.get('ownerReview') or {}).get('decision')!='accept source-scoped alias':
  failures.append({'check':'VG-001 accepted source-scoped alias decision'})
 # The remaining open owner gate maps exactly to the remaining proposed alias.
 gates=review.get('gates') or []
 if review.get('counts')!={'reviewGates':2,'resolved':1,'open':1} or {g['reviewGateId'] for g in gates}!={'VG-001','VG-002'}: failures.append({'check':'review gates'})
 gate_by_id={g['reviewGateId']:g for g in gates}
 if gate_by_id['VG-001'].get('status')!='resolved' or gate_by_id['VG-001'].get('decision')!='accept source-scoped alias' or gate_by_id['VG-002'].get('status')!='open': failures.append({'check':'review gate statuses'})
 if {x for g in gates if g.get('status')=='open' for x in g['affectedAliasIds']}!={a['aliasId'] for a in alias_rows if a['status'].startswith('proposed-')}: failures.append({'check':'review/alias linkage'})
 # Coverage is mechanically recomputed.
 cited={x['sourceTermId'] for e in entries for x in e['authorityEvidence']}; alias_cited={x['sourceTermId'] for a in alias_rows for x in a.get('sourceEvidence') or []}; identity_cited={x['sourceTermId'] for g in groups for x in g['sourceOccurrences']}; covered=cited|alias_cited|identity_cited
 expected_cov={'sourceTermOccurrences':1853,'uniqueNormalizedSourceKeys':1194,'namedIdentityOccurrences':643,'namedIdentityExactStringGroups':501,'canonicalVocabularyEntries':167,'acceptedExistingIconTerms':50,'proposedAuthorityDerivedTerms':117,'aliasEntries':8,'acceptedAliases':7,'proposedReviewAliases':1,'directlyReferencedSourceTerms':len(cited|alias_cited),'sourceTermsCoveredByVocabularyAliasOrNamedIdentity':len(covered),'uncitedSourceTermOccurrences':1853-len(covered),'openReviewGates':1}
 if coverage.get('counts')!=expected_cov: failures.append({'check':'coverage counts','expected':expected_cov,'actual':coverage.get('counts')})
 # Taxonomy/ontology/semantic artifacts are forbidden before review closes.
 forbidden=[]
 for pattern in ('*taxonomy*','*ontology*','*semantic*'):
  forbidden += [p.name for p in DIR.glob(pattern)]
 if forbidden: failures.append({'check':'premature later-phase artifacts','files':sorted(set(forbidden))})
 report={'schemaVersion':1,'passed':not failures,'checks':expected_cov,'failureCount':len(failures),'failures':failures}; (DIR/'validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n'); print(json.dumps(report,indent=2,ensure_ascii=False)); return 0 if not failures else 1
if __name__=='__main__': raise SystemExit(main())
