// Tests the exported review script in a simulated DOM; not a browser visual test.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
(async()=>{
const initial={schema_version:'1.0',report_id:'abc',decisions:{'0':{status:'pending',note:''}}};
const handlers={},sel={value:'pending'},note={value:''};
const row={dataset:{index:'0'},querySelector:s=>s==='select'?sel:note,addEventListener:(e,f)=>handlers.input=f};
const elements={'review-data':{textContent:JSON.stringify(initial)},'review-message':{textContent:''},'export-review':{addEventListener:(e,f)=>handlers.export=f},'import-review':{addEventListener:(e,f)=>handlers.import=f}};
let saved;
const ctx={document:{getElementById:id=>elements[id],querySelectorAll:()=>[row],createElement:()=>({click(){}})},JSON,Blob,URL:{createObjectURL:b=>(saved=b,'blob:test'),revokeObjectURL(){}},setTimeout:f=>f(),confirm:()=>true,window:{addEventListener(){}}};
vm.runInNewContext(fs.readFileSync(process.argv[2],'utf8'),ctx);
sel.value='approved';note.value='의도된 연출';handlers.input();handlers.export();
let out=JSON.parse(await saved.text());assert.equal(out.decisions['0'].status,'approved');
sel.value='pending';note.value='';await handlers.import({target:{files:[{size:100,text:async()=>JSON.stringify(out)}],value:'test'}});assert.equal(sel.value,'approved');assert.equal(note.value,'의도된 연출');
out.report_id='wrong';out.decisions['0'].status='needs_fix';await handlers.import({target:{files:[{size:100,text:async()=>JSON.stringify(out)}],value:'test'}});assert.equal(sel.value,'approved');assert.match(elements['review-message'].textContent,/보고서/);
console.log('Review UI logic: export, import, wrong-report rejection passed (simulated DOM).');
})().catch(e=>{console.error(e);process.exit(1)});
