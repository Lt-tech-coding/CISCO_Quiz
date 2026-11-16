const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('index.html','utf8');
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(x=>x[1]);
const data={window:{addEventListener(){}}};
vm.runInNewContext(scripts.find(s=>s.includes('window.ITE_QUESTIONS =')),data);
vm.runInNewContext(scripts.find(s=>s.includes('window.ITE_LESSONS =')),data);
vm.runInNewContext(scripts.find(s=>s.includes('window.ITE_QUESTIONS.push(')),data);
class Element {
 constructor(tag='div'){this.tag=tag;this.children=[];this.className='';this.textContent='';this.style={};this.value='';this.classList={add:(...v)=>{this.className=[...new Set([...this.className.split(' ').filter(Boolean),...v])].join(' ')},remove:(...v)=>{this.className=this.className.split(' ').filter(x=>!v.includes(x)).join(' ')},contains:v=>this.className.split(' ').includes(v),toggle:(v,b)=>{b=b===undefined?!this.classList.contains(v):b;b?this.classList.add(v):this.classList.remove(v);return b}};}
 append(...nodes){this.children.push(...nodes)}
 replaceChildren(...nodes){this.children=nodes}
 setAttribute(){}
 scrollIntoView(){}
}
function check(q, selected, mode='practice', config={}) {
 const els={};for(const x of html.matchAll(/\bid="([^"]+)"/g))els[x[1]]=new Element();
 els.module.value=config.module||'all';els.count.value=config.count||'20';
 const memory=new Map();let randomCalls=0;
 const testMath=Object.create(Math);testMath.random=()=>{randomCalls++;return config.random===undefined?.999999:config.random};
 const ctx={Math:testMath,window:{ITE_QUESTIONS:config.questions||[q],ITE_SOURCE_IMAGES:data.window.ITE_SOURCE_IMAGES,ITE_LESSONS:data.window.ITE_LESSONS,ITE_QUESTION_LESSONS:data.window.ITE_QUESTION_LESSONS,ITE_STUDY_NOTES:{},ITE_QUESTION_NOTES:{},scrollTo(){}},document:{body:new Element(),getElementById:id=>els[id],createElement:tag=>new Element(tag),createTextNode:text=>({textContent:text})},localStorage:{getItem:key=>memory.get(key)||null,setItem:(key,value)=>memory.set(key,value),removeItem:key=>memory.delete(key)},alert:()=>{throw Error('unexpected alert')},confirm:()=>true};
 vm.runInNewContext(scripts.find(s=>s.includes('function render()')),ctx);
 els.start.onclick();
 for(const index of selected){const input=els.options.children[index].children[0];input.checked=true;input.onchange();}
 if(mode==='practice') els.check.onclick();
 assert(randomCalls>0,'Start did not shuffle options');
 return els;
}
const single=data.window.ITE_QUESTIONS[0];
let els=check(single,[0]);
assert(els.answerResult.textContent.includes('Incorrect'));
assert(els.answerResult.textContent.includes('B. Power supply unit'));
assert(els.options.children[0].classList.contains('wrong'));
assert(els.options.children[1].classList.contains('correct'));
assert(els.options.children[0].children.at(-1).textContent.includes('Incorrect'));
assert(els.options.children[1].children.at(-1).textContent.includes('Correct answer'));
assert(els.feedback.children.some(x=>x.children.some(y=>y.classList?.contains('lesson-image'))));
const detail=els.feedback.children.find(x=>x.className==='detail');
const lesson=detail.children.find(x=>x.className==='teaching-explanation');
assert.strictEqual(lesson.tag,'section');
assert(lesson.children.some(x=>x.children.some(y=>y.textContent==='1. In simple terms')));
assert(lesson.children.some(x=>x.children.some(y=>y.textContent==='2. Why this answer is right')));
assert(lesson.children.some(x=>x.children.some(y=>y.textContent==='3. A practical example')));
assert(lesson.children.some(x=>x.children.some(y=>y.textContent==='Remember for the exam')));
assert(detail.children.some(x=>x.className==='btn explanation-next'));
els=check(single,[1]);assert(els.answerResult.textContent.startsWith('✓ Correct!'));
const multi=data.window.ITE_QUESTIONS.find(q=>Array.isArray(q.answers));
els=check(multi,[multi.answers[0]]);assert(els.answerResult.textContent.includes('Incorrect'));
for(const i of multi.answers) assert(els.options.children[i].classList.contains('correct'));
els=check(multi,multi.answers);assert(els.answerResult.textContent.startsWith('✓ Correct!'));
els=check(single,[0],'select');assert(els.answerResult.classList.contains('hidden'));assert(!els.options.children.some(x=>x.classList.contains('correct')||x.classList.contains('wrong')));
els=check(single,[0],'practice',{random:0});assert(els.answerResult.textContent.startsWith('✓ Correct!'),'Shuffling lost the correct answer mapping');
els.home.onclick();assert(!els.setup.classList.contains('hidden'));assert(els.quiz.classList.contains('hidden'));assert(!els.resume.classList.contains('hidden'));
els.resume.onclick();assert(!els.quiz.classList.contains('hidden'));assert(els.setup.classList.contains('hidden'));assert(els.answerResult.textContent.startsWith('✓ Correct!'),'Home/resume lost the answer');
// Exercise the visual explanation for every built-in question.
for(const q of data.window.ITE_QUESTIONS) {
 assert(q.lesson||data.window.ITE_LESSONS[data.window.ITE_QUESTION_LESSONS[q.id]],'Question missing its lesson');
 const rendered=check(q,q.answers||[q.answer]);
 assert(!rendered.feedback.classList.contains('hidden'),'Checked explanation hidden');
}
const full=check(single,[],'select',{count:'all',questions:data.window.ITE_QUESTIONS});
assert.strictEqual(full.counter.textContent,'Question 1 of 1140');
for(const id of ['bankSource','shuffle','mode'])assert(!html.includes(`id="${id}"`),'Removed control still present');
for(let module=1;module<=14;module++) {
 const state=check(single,[],'select',{count:'all',module:String(module),questions:data.window.ITE_QUESTIONS});
 const total=data.window.ITE_QUESTIONS.filter(q=>q.module===module).length;
 assert.strictEqual(state.counter.textContent,`Question 1 of ${total}`);
}
console.log('Passed: full 1,140-question bank, mandatory shuffling, answer remapping, all explanations, multiple-answer scoring, and Home/resume with saved answers.');
