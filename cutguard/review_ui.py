"""Client-side review import/export without server storage."""
SCRIPT = r'''
const initial=JSON.parse(document.getElementById('review-data').textContent);
const fields=[...document.querySelectorAll('.review-row')];
let dirty=false;
function snapshot(){const result=JSON.parse(JSON.stringify(initial));fields.forEach(row=>{result.decisions[row.dataset.index]={status:row.querySelector('select').value,note:row.querySelector('textarea').value};});return result;}
function say(message){document.getElementById('review-message').textContent=message;}
fields.forEach(row=>row.addEventListener('input',()=>{dirty=true;say('미저장 변경이 있습니다. 검토 파일 내보내기를 눌러 보관하세요.');}));
document.getElementById('export-review').addEventListener('click',()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(snapshot(),null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='cutguard-review.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);dirty=false;say('검토 파일 다운로드를 요청했습니다. 파일을 보관하세요.');});
document.getElementById('import-review').addEventListener('change',async event=>{try{const file=event.target.files[0];if(!file)return;if(file.size>2000000)throw Error('검토 파일이 너무 큽니다.');const r=JSON.parse(await file.text());if(r.schema_version!=='1.0'||r.report_id!==initial.report_id||!r.decisions||Array.isArray(r.decisions)||Object.keys(r.decisions).length!==fields.length)throw Error('이 보고서의 검토 파일이 아닙니다.');fields.forEach(row=>{const d=r.decisions[row.dataset.index];if(!d||!['pending','approved','needs_fix'].includes(d.status)||typeof d.note!=='string'||d.note.length>2000)throw Error('잘못된 검토 항목입니다.');});if(dirty&&!confirm('저장하지 않은 변경을 불러온 내용으로 바꿀까요?'))return;fields.forEach(row=>{const d=r.decisions[row.dataset.index];row.querySelector('select').value=d.status;row.querySelector('textarea').value=d.note;});dirty=false;say('검토 내용을 불러왔습니다. 원래 탐지 결과는 유지됩니다.');}catch(error){say(error.message);}finally{event.target.value='';}});
window.addEventListener('beforeunload',event=>{if(dirty){event.preventDefault();event.returnValue='';}});
'''
