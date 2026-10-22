const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),repo='moorisi/twin-tail';
const cases={stepdown:{decisions:['SUPPORTED','SUPPORTED']},multiplicity:{decisions:['NOT_ESTABLISHED','NOT_ESTABLISHED']},ambiguity:{decisions:['REVIEW','REVIEW']}};
const canonical=x=>Array.isArray(x)?x.map(canonical):x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,canonical(x[k])])):x;
const equal=(a,b)=>JSON.stringify(canonical(a))===JSON.stringify(canonical(b)),clone=x=>JSON.parse(JSON.stringify(x));
function assert(ok,message){if(!ok)throw Error(message);}
function descriptor(id,revision){return [0,1].map(i=>({url:`https://raw.githubusercontent.com/${repo}/${revision}/fixtures/${id}-${i}.json`,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,'fixtures',`${id}-${i}.json`))).digest('hex')}));}
function args(id,revision){const d=descriptor(id,revision);return [repo,id+'-family',['archive-export','report-import'],[0,1].map(()=>Array.from({length:8},(_,i)=>'pair-'+(i+1))),d.map(x=>x.url),d.map(x=>x.sha256)];}
function configuration(a){return {repository:a[0],family:a[1],endpoints:a[2],pairs:a[3],urls:a[4],hashes:a[5]};}
function initial(id,revision){return {configuration:configuration(args(id,revision)),assessments:[null,null],bounds:[null,null],result:null};}
function statuses(id,index){
 if(index===1)return id==='multiplicity'?[...Array(3).fill(['PASS','FAIL']),...Array(5).fill(['FAIL','FAIL'])]:[...Array(5).fill(['FAIL','PASS']),...Array(3).fill(['PASS','PASS'])];
 if(id==='stepdown')return [...Array(7).fill(['FAIL','PASS']),['PASS','PASS']];
 if(id==='multiplicity')return [...Array(5).fill(['FAIL','PASS']),...Array(3).fill(['PASS','PASS'])];
 return [...Array(6).fill(['FAIL','PASS']),...Array(2).fill(['UNKNOWN','UNKNOWN'])];
}
function oracle(labels){
 // Independent exhaustive oracle: enumerate every binary completion and every
 // null coin assignment; no contract DP or binomial-coefficient implementation.
 let found=new Map();
 function visit(i,w,l,completion){
  if(i<labels.length){const arms=labels[i].map(x=>x==='UNKNOWN'?[0,1]:[Number(x==='PASS')]);for(const c of arms[0])for(const t of arms[1])visit(i+1,w+Number(t>c),l+Number(c>t),[...completion,[c,t]]);return;}
  const key=w+','+l,prior=found.get(key);if(prior&&JSON.stringify(prior.completion)<=JSON.stringify(completion))return;
  let favorable=0;for(let bits=0;bits<2**(w+l);bits++){let count=0;for(let j=0;j<w+l;j++)count+=Number(Boolean(bits&(1<<j)));if(count>=w)favorable++;}
  found.set(key,{w,l,completion,ticks:favorable*2**(8-w-l)});
 }
 visit(0,0,0,[]);
 const values=[...found.values()],lex=(a,b)=>JSON.stringify(a.completion).localeCompare(JSON.stringify(b.completion));
 const low=[...values].sort((a,b)=>a.ticks-b.ticks||lex(a,b))[0],high=[...values].sort((a,b)=>b.ticks-a.ticks||lex(a,b))[0];
 return {lower_ticks:low.ticks,upper_ticks:high.ticks,lower_witness:low.completion,upper_witness:high.completion,lower_counts:[low.w,low.l],upper_counts:[high.w,high.l],reachable_counts:found.size};
}
function familyOracle(bounds){
 function adjusted(ticks){
  // Rejection at every attainable rational threshold yields an independent
  // adjusted value for each hypothesis, rather than copying cumulative-max code.
  const order=ticks.map((_,i)=>i).sort((a,b)=>ticks[a]-ticks[b]||a-b),answer=Array(ticks.length).fill(256);
  for(let level=0;level<=256;level++)for(let k=0;k<order.length;k++){const i=order[k];if(ticks[i]*(ticks.length-k)>level)break;if(answer[i]===256)answer[i]=level;}
  return answer;
 }
 const lo=adjusted(bounds.map(x=>x.lower_ticks)),hi=adjusted(bounds.map(x=>x.upper_ticks));
 const decisions=lo.map((x,i)=>hi[i]*20<=256?'SUPPORTED':x*20>256?'NOT_ESTABLISHED':'REVIEW');
 return {status:decisions.includes('REVIEW')?'REVIEW':'COMPLETE',denominator:256,alpha:[1,20],lower_adjusted_ticks:lo,upper_adjusted_ticks:hi,decisions};
}
function check(s,id,revision){
 assert(Object.keys(s).sort().join(',')==='assessments,bounds,configuration,result'&&equal(s.configuration,configuration(args(id,revision)))&&s.assessments.length===2&&s.bounds.length===2,'Exact source-bound whole state');
 for(let i=0;i<2;i++){
  const a=s.assessments[i];if(a===null){assert(s.bounds[i]===null,'No inference without assessment');continue;}
  const source=JSON.parse(fs.readFileSync(path.join(root,'fixtures',`${id}-${i}.json`))),labels=statuses(id,i);
  assert(Object.keys(a).sort().join(',')==='observations,source'&&equal(a.source,source)&&Object.keys(a.observations).join(',')==='rows'&&a.observations.rows.length===8,'Complete full-source assessment');
  for(let j=0;j<8;j++){
   const row=a.observations.rows[j],text=source.pairs[j];assert(Object.keys(row).sort().join(',')==='control,control_quote,pair,treatment,treatment_quote'&&row.pair===text.pair&&equal([row.control,row.treatment],labels[j]),'Every exact PASS/FAIL/UNKNOWN decision');
   for(const arm of ['control','treatment'])assert(typeof row[arm+'_quote']==='string'&&row[arm+'_quote'].length>=12&&row[arm+'_quote'].length<=300&&text[arm].includes(row[arm+'_quote']),'Verbatim source-linked decision quote');
  }
  assert(equal(s.bounds[i],oracle(labels)),'Exhaustive null-distribution and completion oracle');
 }
 if(s.result!==null)assert(s.bounds.every(x=>x!==null)&&equal(s.result,familyOracle(s.bounds))&&equal(s.result.decisions,cases[id].decisions),'Exact multiplicity-aware final family');
}
function plan(id){return [
 {label:id+'-reject-empty-family',caller:1,method:'finalize',args:[],error:'[EXPECTED] Every endpoint required'},
 {label:id+'-adjudicate-second',caller:2,method:'adjudicate',args:[1]},
 {label:id+'-reject-partial-family',caller:3,method:'finalize',args:[],error:'[EXPECTED] Every endpoint required'},
 {label:id+'-adjudicate-first',caller:1,method:'adjudicate',args:[0]},
 {label:id+'-finalize',caller:3,method:'finalize',args:[]},
 {label:id+'-reject-repeat-endpoint',caller:0,method:'adjudicate',args:[0],error:'[EXPECTED] Endpoint already adjudicated'},
 {label:id+'-reject-repeat-finalize',caller:0,method:'finalize',args:[],error:'[EXPECTED] Family already finalized'}
 ];}
function replay(before,item,after,id,revision){
 check(before,id,revision);check(after,id,revision);
 if(item.error){assert(equal(before,after),'Expected rejection changed state');return;}
 const e=clone(before);
 if(item.method==='adjudicate'){const i=item.args[0];assert(e.assessments[i]===null,'One assessment per fixed endpoint');e.assessments[i]=clone(after.assessments[i]);e.bounds[i]=oracle(statuses(id,i));}
 else if(item.method==='finalize'){assert(e.result===null&&e.bounds.every(x=>x!==null),'Complete family before finalization');e.result=familyOracle(e.bounds);}
 else throw Error('Unknown planned method');
 assert(equal(e,after),'Independent full-state replay: '+item.label);
}
module.exports={cases,args,descriptor,initial,plan,replay,oracle,check,statuses,familyOracle};
