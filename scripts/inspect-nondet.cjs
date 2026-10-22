// Read-only receipt diagnostics. No signing or network calls.
const fs=require('node:fs'),path=require('node:path'),{pathToFileURL}=require('node:url');
const {createRequire}=require('node:module');
async function main(){
 const cli=process.env.GENLAYER_CLI_PATH;if(!cli)throw Error('Set GENLAYER_CLI_PATH');
 const {abi}=await import(pathToFileURL(createRequire(cli).resolve('genlayer-js')).href);
 const receipt=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
 function plain(x){
  if(typeof x==='bigint'){const n=Number(x);if(!Number.isSafeInteger(n))throw Error('Unsafe integer');return n;}
  if(x instanceof Map)return Object.fromEntries([...x].map(([k,v])=>[k,plain(v)]));
  if(Array.isArray(x))return x.map(plain);return x;
 }
 const leaders=receipt.consensus_data.leader_receipt.map((entry,index)=>({index,execution:entry.execution_result,outputs:Object.entries(entry.eq_outputs||{}).map(([call,encoded])=>{
  const raw=Buffer.from(encoded,'base64');return {call,tag:raw[0],model:raw[0]===0?plain(abi.calldata.decode(raw.subarray(1))).model:null};
 })}));
 const validators=receipt.consensus_data.validators.map(v=>({vote:v.vote,nondet_disagree:v.nondet_disagree,stdout:v.genvm_result?.stdout,stderr:v.genvm_result?.stderr}));
 console.log(JSON.stringify({hash:receipt.hash||receipt.tx_id,result:receipt.result_name||receipt.result,leaders,validators},null,2));
}
main().catch(e=>{console.error(e.stack);process.exitCode=1;});
