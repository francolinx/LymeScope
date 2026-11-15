// Presentation only: consume saved evidence. No inference or scientific recomputation.
const storyKeys=['coverage','disagreement','dimer','experiment'];
let storyIndex=0,storyMotion=false;
function storyCard(parent,title){const box=node('article','',parent,'guided-card');node('h3',title,box);return box;}
function countChips(parent,row){const chips=node('div','',parent,'residue-counts');for(const [aa,n] of Object.entries(row.original_residue_counts))node('span',`${aa}: ${n}`,chips);}
function storyColumnAction(parent,column){const link=node('a',`Inspect column ${column} ↓`,parent);link.href='#column-detail';link.addEventListener('click',()=>showColumn(column));}
function renderGuidedStory(index){
 storyIndex=((Number(index)||0)+storyKeys.length)%storyKeys.length;storyMotion=false;
 const key=storyKeys[storyIndex],box=$('story-content');box.replaceChildren();
 for(const name of storyKeys)$('story-'+name).setAttribute('aria-pressed',String(name===key));
 $('story-step').textContent=`Story ${storyIndex+1} of 4`;
 $('story-image').hidden=key!=='dimer';$('story-media-actions').hidden=key!=='dimer';
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
  $('story-title').textContent='Independent experiments are the next test.';
  $('story-status').textContent='PRIMARY SOURCES VERIFIED · LOCAL CONTACT MAPPING PENDING';$('story-status').className='guided-status pending';
  $('story-intro').textContent=D.experimental_evidence.question;
  for(const source of D.experimental_evidence.sources){const paper=node('article','',box,'guided-paper');node('span',source.pdb_id?`${source.pdb_id} · ${source.method} · ${source.resolution_angstrom.toFixed(2)} Å`:'Literature-defined region · no atomic-contact overlay',paper,'guided-status');node('h3',source.label,paper);node('p',source.evidence,paper);const link=node('a',source.citation,paper);link.href=source.primary_reference;if(source.pdb_url){const pdb=node('a','Official PDB record',paper);pdb.href=source.pdb_url;}node('p',source.limitation,paper,'guided-caption');}
  $('story-caption').textContent='These are independent published studies, not new LymeScope measurements. Published numbering, construct position and frozen alignment index require an explicit verified map.';
  $('story-caution').textContent='No antibody-contact labels are displayed until the Spark validates chains, residue identities, insertion codes, missingness and alignment correspondence. Homodimer proximity is never substituted for antibody binding.';
 }
}
for(let i=0;i<storyKeys.length;i++)$('story-'+storyKeys[i]).addEventListener('click',()=>renderGuidedStory(i));
$('story-back').addEventListener('click',()=>renderGuidedStory(storyIndex-1));
$('story-next').addEventListener('click',()=>renderGuidedStory(storyIndex+1));
$('story-motion').addEventListener('click',()=>{storyMotion=!storyMotion;$('story-image').src='assets/ospc-dimer.'+(storyMotion?'gif':'png');$('story-motion').textContent=storyMotion?'Stop rotation':'Rotate the deposited dimer';$('story-motion').setAttribute('aria-pressed',String(storyMotion));});
renderGuidedStory(0);
