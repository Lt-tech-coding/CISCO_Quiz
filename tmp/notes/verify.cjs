const fs=require('fs'),vm=require('vm'),assert=require('assert');
const parser=require('C:/Users/south/AppData/Roaming/npm/node_modules/eas-cli/node_modules/@babel/parser');
const html=fs.readFileSync('index.html','utf8');
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(x=>x[1]);
scripts.forEach(s=>parser.parse(s,{sourceType:'script'}));
const context={window:{addEventListener(){}}};
for(const s of scripts.filter(x=>x.includes('window.ITE_QUESTIONS =')||x.includes('window.ITE_STUDY_NOTES ='))) vm.runInNewContext(s,context);
const before=JSON.parse(fs.readFileSync('tmp/notes/questions.json','utf8'));
assert.strictEqual(JSON.stringify(context.window.ITE_QUESTIONS),JSON.stringify(before));
const ids=new Set(before.map(q=>q.id));
for(const [id,key] of Object.entries(context.window.ITE_QUESTION_NOTES)) {
 assert(ids.has(id),'Unknown question ID');
 assert(context.window.ITE_STUDY_NOTES[key]?.text.length>=160,'Missing source text');
}
console.log('All scripts parse. All 1,000 questions and answers unchanged. All note references resolve.');
