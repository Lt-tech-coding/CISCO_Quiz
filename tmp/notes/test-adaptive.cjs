const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const html = fs.readFileSync('index.html', 'utf8');
const scripts = [...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(match => match[1]);
const data = {window: {addEventListener(){}}};
for (const script of scripts.filter(source => /window\.ITE_(QUESTIONS =|QUESTIONS\.push|LESSONS =|STUDY_NOTES =)/.test(source))) {
  vm.runInNewContext(script, data);
}

class Element {
  constructor(tag='div') {
    this.tag=tag; this.children=[]; this.className=''; this.textContent=''; this.style={}; this.value='';this.parentElement={open:false};this.attributes={};
    this.classList={
      add:(...values)=>{this.className=[...new Set([...this.className.split(' ').filter(Boolean),...values])].join(' ');},
      remove:(...values)=>{this.className=this.className.split(' ').filter(value=>!values.includes(value)).join(' ');},
      contains:value=>this.className.split(' ').includes(value),
      toggle:(value,enabled)=>{enabled=enabled===undefined?!this.classList.contains(value):enabled;enabled?this.classList.add(value):this.classList.remove(value);return enabled;}
    };
  }
  append(...nodes){this.children.push(...nodes);}
  replaceChildren(...nodes){this.children=nodes;}
  setAttribute(key,value){this.attributes[key]=value;}
  focus(){this.focused=true;}
  scrollIntoView(){this.scrolled=true;}
}

function createApp({questions=data.window.ITE_QUESTIONS, memory=new Map(), now=Date.UTC(2026,10,16,8), count='20', module='all'}={}) {
  const elements={};
  for (const match of html.matchAll(/<[^>]+\bid="([^"]+)"[^>]*>/g)) {
    elements[match[1]]=new Element();
    elements[match[1]].className=match[0].match(/\bclass="([^"]*)"/)?.[1]||'';
  }
  elements.count.value=count; elements.module.value=module;
  const clock={now};
  class FakeDate extends Date { static now(){return clock.now;} }
  const intervals=[];
  const confirmation={allow:true};
  let randomCalls=0;
  const testMath=Object.create(Math);
  testMath.random=()=>{randomCalls++;return Math.random();};
  const context={
    Date:FakeDate, Math:testMath,
    window:{...data.window, ITE_QUESTIONS:questions, scrollTo(){}, addEventListener(){}},
    document:{body:new Element(), addEventListener(){}, getElementById:id=>elements[id],createElement:tag=>new Element(tag),createTextNode:text=>({textContent:text})},
    localStorage:{getItem:key=>memory.get(key)||null,setItem:(key,value)=>memory.set(key,value),removeItem:key=>memory.delete(key)},
    setInterval:callback=>intervals.push(callback), alert:message=>{throw Error(message);}, confirm:()=>confirmation.allow
  };
  vm.runInNewContext(scripts.find(source=>source.includes('function render()')),context);
  const app={elements, clock, memory, intervals, confirmation,
    session:()=>JSON.parse(memory.get('ite8_session_v1')),
    profile:()=>JSON.parse(memory.get('ite8_learning_v1')||'{}'),
    advance:milliseconds=>{clock.now+=milliseconds;intervals.forEach(callback=>callback());},
    randomCalls:()=>randomCalls,
    select(index){const input=elements.options.children[index].children[0];input.checked=true;input.onchange();},
    correct(){const session=app.session(),q=session.questions[session.index];for(const index of q.answers||[q.answer]) app.select(index);},
    wrong(){const session=app.session(),q=session.questions[session.index];const correct=q.answers||[q.answer];app.select(q.options.findIndex((_,index)=>!correct.includes(index)));}
  };
  return app;
}

// Time budgets use the actual number of one-mark questions.
for(const [count,minutes] of [['20',24],['50',60],['100',120]]) {
  const app=createApp({count});app.elements.start.onclick();
  assert.strictEqual(app.session().durationMs,minutes*60*1000);
  assert.strictEqual(app.session().questions.length,Number(count));
  assert(app.randomCalls()>0);
}

// Timer survives navigation, a reload and an expired page. Late actions cannot extend it.
let app=createApp();app.elements.start.onclick();app.correct();app.elements.check.onclick();
const deadline=app.session().deadlineAt;
assert(!app.elements.feedback.classList.contains('hidden'));
assert(app.elements.feedback.scrolled);
app.advance(5*60*1000);app.elements.home.onclick();
assert(!app.elements.setup.classList.contains('hidden'));
const reloaded=createApp({memory:app.memory,now:app.clock.now});
reloaded.elements.resume.onclick();
assert.strictEqual(reloaded.session().deadlineAt,deadline);
assert.strictEqual(reloaded.elements.timer.textContent,'19:00');
reloaded.advance(20*60*1000);
assert(reloaded.session().finished&&reloaded.session().timeExpired);
assert(!reloaded.elements.results.classList.contains('hidden'));
assert(reloaded.elements.resultMessage.textContent.includes('automatically'));

// Incorrect practice answers schedule one later follow-up without adding marks/time.
app=createApp({count:'5',questions:data.window.ITE_QUESTIONS.filter(q=>q.module===1&&q.options.includes('Power supply unit'))});app.elements.start.onclick();
const before=app.session();app.wrong();app.elements.check.onclick();
const after=app.session();
assert.strictEqual(after.questions.length,before.questions.length);
assert.strictEqual(after.deadlineAt,before.deadlineAt);
assert(Object.values(after.followUps).some(Boolean));
assert(Object.keys(after.followUpSlots).every(position=>Number(position)>=3));
const firstHistory=Object.values(app.profile().concepts).reduce((n,record)=>n+record.history.length,0);
app.elements.check.onclick();app.elements.home.onclick();app.elements.resume.onclick();
assert.strictEqual(Object.values(app.profile().concepts).reduce((n,record)=>n+record.history.length,0),firstHistory);

// A readiness test hides feedback, covers all modules, and uses unique unseen families.
app=createApp({count:'50'});app.elements.readinessStart.onclick();
let test=app.session();assert.strictEqual(test.mode,'exam');
assert.strictEqual(new Set(test.questions.map(q=>q.module)).size,14);
assert(app.elements.check.classList.contains('hidden'));
const attempts=test.questions.length;
for(let i=0;i<attempts;i++){app.correct();if(i<attempts-1)app.elements.next.onclick();}
assert(app.elements.feedback.classList.contains('hidden'));
app.elements.finish.onclick();
assert.strictEqual(app.profile().tests.length,1);assert.strictEqual(app.profile().tests[0].score,100);
const firstIds=new Set(test.questions.map(q=>q.id));
app.clock.now+=1000;app.elements.readinessStart.onclick();
test=app.session();assert(!test.questions.some(q=>firstIds.has(q.id)));
for(let i=0;i<test.questions.length;i++){app.correct();if(i<test.questions.length-1)app.elements.next.onclick();}
app.elements.finish.onclick();assert(app.elements.readinessProgress.textContent.includes('Goal reached'));

// A small exhausted pool is not silently relabeled as a fresh readiness test.
const tiny=createApp({questions:data.window.ITE_QUESTIONS.slice(0,5)});
tiny.elements.readinessStart.onclick();assert(tiny.elements.setupMessage.textContent.includes('new questions'));
assert(!tiny.memory.has('ite8_session_v1'));

// A family cannot earn repeated concept credit from reworded copies in one session.
app=createApp({count:'all',questions:data.window.ITE_QUESTIONS.filter(q=>q.module===1&&q.options.includes('Power supply unit')).slice(0,4)});
app.elements.start.onclick();
test=app.session();
for(let i=0;i<test.questions.length;i++){app.correct();app.elements.check.onclick();if(i<test.questions.length-1)app.elements.next.onclick();}
assert.strictEqual(Object.values(app.profile().concepts).reduce((n,record)=>n+record.history.length,0),1);

// Clear navigation: numbered questions, flag status, Home, logo and result actions.
app=createApp();
assert(app.elements.home.classList.contains('hidden'));
app.elements.brandHome.onclick();assert.strictEqual(app.elements.pageLocation.textContent,'Home');
app.elements.start.onclick();assert.strictEqual(app.elements.pageLocation.textContent,'Practice');
assert.strictEqual(app.elements.next.textContent,'Skip for now');
app.elements.questionMenu.open=true;app.elements.questionMenu.ontoggle();
assert.strictEqual(app.elements.questionGrid.children.length,20);
app.elements.flag.onclick();
assert(app.elements.questionGrid.children[0].attributes['aria-label'].includes('flagged'));
app.elements.questionGrid.children[5].onclick();
assert.strictEqual(app.session().index,5);assert.strictEqual(app.elements.questionMenu.open,false);
assert(app.elements.question.focused);
app.correct();app.elements.check.onclick();
assert.strictEqual(app.elements.next.textContent,'Next question →');
assert(!app.elements.next.classList.contains('secondary'));
const homeDeadline=app.session().deadlineAt;
app.elements.brandHome.onclick();assert.strictEqual(app.elements.pageLocation.textContent,'Home');
assert(app.elements.resumeSummary.textContent.includes('timer is still running'));
app.elements.resume.onclick();assert.strictEqual(app.session().deadlineAt,homeDeadline);
app.elements.finish.onclick();assert.strictEqual(app.elements.pageLocation.textContent,'Results');
app.elements.reviewWrong.onclick();assert.strictEqual(app.elements.reviewWrong.attributes['aria-pressed'],'true');
app.elements.again.onclick();assert.strictEqual(app.elements.pageLocation.textContent,'Home');
app.elements.resume.onclick();assert.strictEqual(app.elements.pageLocation.textContent,'Results');
app.elements.practiceAgain.onclick();assert.strictEqual(app.elements.pageLocation.textContent,'Practice');
assert.strictEqual(app.session().questions.length,20);
assert(!html.includes('id="themeToggle"'));assert(!html.includes('localStorage.getItem("ite-theme")'));
assert(html.includes('<html lang="en" data-theme="dark">'));
// Reset requires confirmation, clears the quiz's data and stops its saved timer.
app.elements.home.onclick();
app.memory.set('unrelated-app','keep');
const savedBeforeClear=app.memory.get('ite8_session_v1');
app.confirmation.allow=false;app.elements.clearProgress.onclick();
assert.strictEqual(app.memory.get('ite8_session_v1'),savedBeforeClear);
app.confirmation.allow=true;app.elements.clearProgress.onclick();
assert(!app.memory.has('ite8_session_v1'));assert(!app.memory.has('ite8_learning_v1'));
assert.strictEqual(app.memory.get('unrelated-app'),'keep');
assert(app.elements.resume.classList.contains('hidden'));
assert(app.elements.conceptProgress.textContent.startsWith('0 of '));
assert.strictEqual(app.elements.timer.textContent,'00:00');
app.advance(180*60*1000);assert(!app.memory.has('ite8_session_v1'));
console.log('Passed: timer persistence and expiry; adaptive lessons and follow-ups; fresh readiness tests; scoring; numbered navigation and flags; Home/logo/resume/results flows; continue practice; and dark-only UI.');
