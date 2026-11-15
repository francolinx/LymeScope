// Presentation only: consume saved evidence. No inference or scientific recomputation.
const storyKeys=['coverage','disagreement','dimer','experiment'];
let storyIndex=0,storyMotion=false;
function storyCard(parent,title){const box=node('article','',parent,'guided-card');node('h3',title,box);return box;}
function countChips(parent,row){const chips=node('div','',parent,'residue-counts');for(const [aa,n] of Object.entries(row.original_residue_counts))node('span',`${aa}: ${n}`,chips);}
function storyColumnAction(parent,column){const link=node('a',`Inspect column ${column} ↓`,parent);link.href='#column-detail';link.addEventListener('click',()=>showColumn(column));}
function renderAntibodySite(parent,column){
 parent.replaceChildren();
 const site=D.frontier_science.complexes['9BIF'].sites[column-1];
 const state=x=>x===null?'unknown / unavailable':x?'yes, observed contact':'no observed contact';
 node('h4',`B11 / 9BIF assembly 1 · alignment column ${column}`,parent);
 node('p',`Q07337 native position: ${site.Q07337_position===null?'unmapped':site.Q07337_position} · complex label chains: ${site.complex_label_chains===null?'unmapped':site.complex_label_chains} · author chains: ${site.complex_auth_chains===null?'unmapped':site.complex_auth_chains}`,parent);
 node('p',`Observed Fab contact union (≤4.5 Å): ${state(site.observed_contact_union_4_5_A)}. Complete-copy contact label: ${state(site.strict_contact_union_4_5_A)}.`,parent);
 node('strong',site.strict_eligible?'Included in the 152-site diagnostic.':`Excluded from the diagnostic: ${site.exclusion_reasons}.`,parent);
 node('p',`Separate reference geometry — 1GGQ homodimer contact: ${state(site.reference_dimer_contact)}; calculated dimer SASA: ${site.reference_dimer_sasa_A2===null?'unknown':site.reference_dimer_sasa_A2.toFixed(2)+' Å²'}.`,parent,'guided-caption');
 storyColumnAction(parent,column);
}
function renderGuidedStory(index){
 storyIndex=((Number(index)||0)+storyKeys.length)%storyKeys.length;storyMotion=false;
 const key=storyKeys[storyIndex],box=$('story-content');box.replaceChildren();
 for(const name of storyKeys)$('story-'+name).setAttribute('aria-pressed',String(name===key));
 $('story-step').textContent=`Story ${storyIndex+1} of 4`;
 $('story-image').hidden=key!=='dimer';$('story-media-actions').hidden=key!=='dimer';$('frontier-media').hidden=key!=='experiment';
 $('story-image').src='assets/ospc-dimer.png';$('story-motion').textContent='Rotate the deposited dimer';$('story-motion').setAttribute('aria-pressed','false');
 $('story-status').textContent='VERIFIED SAVED EVIDENCE';$('story-status').className='guided-status';
 if(key==='coverage'){
  $('story-title').textContent='100% agreement can mean one observation.';
  $('story-intro').textContent='Column 1 and column 154 have the same observed modal fraction. Their evidence differs by a factor of thirty.';
  const grid=node('div','',box,'guided-metrics');
  for(const column of [1,154]){const x=S.columns[column-1],card=storyCard(grid,`Alignment column ${column}`);node('div',fraction(x.modal_fraction)+' agreement',card,'guided-big');node('strong',`${x.observed_residue_count}/30 sequences contribute`,card);const dots=node('div','',card,'observation-dots');dots.setAttribute('aria-label',`${x.observed_residue_count} observed residues, ${30-x.observed_residue_count} gaps`);for(let k=0;k<30;k++)node('span','',dots,'observation-dot'+(k<x.observed_residue_count?' observed'+(column===154?' single':''):''));countChips(card,x);node('p',`${30-x.observed_residue_count} gaps · ${fraction(x.coverage)} coverage`,card,'guided-caption');storyColumnAction(card,column);}
  $('story-caption').textContent='Filled cells are observations. Pale cells are missing observations, not disagreements. Denominator: all 30 frozen sequences.';
  $('story-caution').textContent='The percentage is correctly calculated from one observation; that is insufficient support for broad conservation in this panel. Columns 154 and 173 are reference gaps and receive no 3D coordinate.';
 }else if(key==='disagreement'){
  $('story-title').textContent='Agreement is not model predictability.';
  $('story-intro').textContent='Mask one original residue in its full natural sequence. ESM-2 scores that original residue from its surrounding context. NLL is not conservation, immunogenicity or an antibody-contact score.';
  const grid=node('div','',box,'guided-metrics');
  for(const column of [177,129]){const x=S.columns[column-1],card=storyCard(grid,`Alignment column ${column}`);node('div',fraction(x.modal_fraction)+' agreement',card,'guided-big');node('strong',`${x.mean_masked_nll_nats.toFixed(5)} nats · mean masked NLL`,card);countChips(card,x);node('p',`${x.observed_residue_count}/30 contributors · lower NLL = more predictable to this checkpoint`,card,'guided-caption');storyColumnAction(card,column);}
  $('story-caption').textContent='Both examples belong to F: the 202 fully covered columns. Full-panel agreement versus predictability Spearman rho = 0.134696; tied ranks are averaged.';
  $('story-caution').textContent='These selected examples illustrate two measurements. The 239 overlapping panel perturbations are sensitivity checks, not independent replicates, a confidence interval or evidence of a biological mechanism.';
 }else if(key==='dimer'){
  $('story-title').textContent='Two experimentally observed OspC partners.';
  $('story-intro').textContent='The 1GGQ biological assembly contains real chains A and B. The model did not generate these coordinates. Motion below rotates the camera; it is not folding or molecular dynamics.';
  const grid=node('div','',box,'guided-metrics');
  const left=storyCard(grid,'Heavy-atom contacts · ≤4.5 Å');node('div','118 residue pairs',left,'guided-big');node('p','51 contacting residues on each partner. OspC–OspC interface, not an antibody interface.',left);
  const right=storyCard(grid,'Calculated SASA loss · separate measure');node('div','4,081.16 Å²',right,'guided-big');node('p','Total loss on dimerization; mean partner interface area is half: 2,040.58 Å². 1.40 Å probe; 1,920 points/atom.',right);
  $('story-image').alt='Rigid rotation of observed 1GGQ chains A and B. Amber shows the separate legacy 8 angstrom C-alpha proximity proxy, not antibody contacts.';
  $('story-caption').textContent='Teal: chain A. Blue: chain B. Amber in this preserved animation: nearest other-chain Cα ≤8 Å (49 residues/chain), a different definition from the 4.5 Å heavy-atom contacts above.';
  $('story-caution').textContent='Static, incomplete crystal constructs do not measure physiological or antibody accessibility. Missing structure stays unknown; zero calculated SASA is a distinct observed-computation state.';
 }else{
  const F=D.frontier_science,m=F.primary_metrics;
  $('story-title').textContent='A real footprint. A hypothesis not supported.';
  $('story-status').textContent='EXACT EXPERIMENTAL MAPPING · NEGATIVE PRIMARY RESULT';
  $('story-intro').textContent='Does agreement–predictability discordance add information beyond agreement, amino-acid identity and unbound-reference geometry? In the predeclared B11 diagnostic, adding signed discordance worsened error.';
  const grid=node('div','',box,'guided-metrics');
  const left=storyCard(grid,'B11 · 9BIF · primary comparison');node('div','31 / 152',left,'guided-big');node('p','Eligible contact sites / eligible alignment sites. There are 32 observed union-contact sites in the whole mapped construct; one is outside this strict comparison set.',left);
  const right=storyCard(grid,'Blocked Brier error · lower is better');node('div',`${m.B2.brier.toFixed(6)} → ${m.B3.brier.toFixed(6)}`,right,'guided-result');node('strong',`+${F.primary_summary.primary_delta_oof_brier_B3_minus_B2.toFixed(6)} worse with signed discordance`,right);node('p',`AUROC: ${m.B2.auroc.toFixed(6)} → ${m.B3.auroc.toFixed(6)}. Eight held-region blocks with five-column guards; no independent-site significance claim.`,right);
  const footprint=storyCard(box,'Inspect the saved B11 antibody footprint');
  node('p','Each button is a strict eligible antibody-contact alignment column. Inspect any other column below, including missing or excluded sites. These labels do not recolor the separate 1GGQ homodimer.',footprint);
  const chips=node('div','',footprint,'residue-counts'),detail=node('div','',footprint);
  const label=node('label','Alignment column (1–218): ',footprint),input=node('input','',label);input.type='number';input.min='1';input.max='218';input.value='154';input.setAttribute('aria-label','B11 footprint alignment column');
  const select=c=>{input.value=String(c);renderAntibodySite(detail,c);};
  input.addEventListener('change',event=>select(Math.min(218,Math.max(1,Math.round(Number(event.target.value)||1)))));
  for(const site of F.complexes['9BIF'].sites.filter(s=>s.strict_eligible&&s.strict_contact_union_4_5_A===true)){const button=node('button',String(site.alignment_column),chips);button.setAttribute('aria-label',`Inspect B11 contact at alignment column ${site.alignment_column}`);button.addEventListener('click',()=>select(site.alignment_column));}
  select(154);
  node('p','B5 / 7UIJ supports structural context: 25 eligible contacts in its own 152-site set (27 observed construct contacts). The eligible sets are not assumed identical. 8C1 is a 21-position literature HDX region, Q07337 130–150; atomic-contact values remain null.',box,'guided-caption');
  for(const source of D.experimental_evidence.sources){const paper=node('article','',box,'guided-paper');node('span',source.pdb_id?`${source.pdb_id} · ${source.method} · ${source.resolution_angstrom.toFixed(2)} Å`:'Literature-defined region · no atomic-contact overlay',paper,'guided-status');node('h3',source.label,paper);node('p',source.evidence,paper);const link=node('a',source.citation,paper);link.href=source.primary_reference;if(source.pdb_url){const pdb=node('a','Official PDB record',paper);pdb.href=source.pdb_url;}node('p',source.limitation,paper,'guided-caption');}
  $('story-caption').textContent='Original Spark figure: deposited experimental coordinates, not AI-generated folds. Gray: Fab; teal: OspC; magenta: observed atom-contact sites. The small mean-NLL-added comparator improvement is exploratory and does not rescue the negative primary discordance result.';
  $('story-caution').textContent='One selected antigen/reference, correlated residues and incomplete antibody coordinates limit the diagnostic. A false contact label means no observed distance contact, not biological non-binding. No incremental predictive value, new epitope target, protection or clinical utility is established. Zero new model calls; the original 6,305 scores were reused.';
 }
}
for(let i=0;i<storyKeys.length;i++)$('story-'+storyKeys[i]).addEventListener('click',()=>renderGuidedStory(i));
$('story-back').addEventListener('click',()=>renderGuidedStory(storyIndex-1));
$('story-next').addEventListener('click',()=>renderGuidedStory(storyIndex+1));
$('story-motion').addEventListener('click',()=>{storyMotion=!storyMotion;$('story-image').src='assets/ospc-dimer.'+(storyMotion?'gif':'png');$('story-motion').textContent=storyMotion?'Stop rotation':'Rotate the deposited dimer';$('story-motion').setAttribute('aria-pressed',String(storyMotion));});
renderGuidedStory(0);
