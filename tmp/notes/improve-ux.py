from pathlib import Path
import re

p=Path('index.html'); s=p.read_text(encoding='utf8')
s=s.replace('<html lang="en">','<html lang="en" data-theme="dark">',1)
def remove_theme(match):
    code=match.group(0)
    return '' if 'themeToggle' in code or 'localStorage.getItem("ite-theme")' in code else code
s=re.sub(r'<script>[\s\S]*?</script>',remove_theme,s)
s,count=re.subn(r'<button class="theme-toggle".*?</button>','',s,count=1,flags=re.S)
assert count==1
s=s.replace('<body>','<body>\n<a class="skip-link" href="#mainContent">Skip to content</a>',1)
s=s.replace('<main>','<main id="mainContent">',1)
old='<div class="brand-wrap"><div><div class="brand">ITE<span>8</span> Practice Lab</div><div class="sub">YOUR IT ESSENTIALS STUDY COMPANION</div></div></div>'
new='<button class="brand-wrap brand-home" id="brandHome" type="button" aria-label="Practice Lab home"><span><span class="brand">ITE<span>8</span> Practice Lab</span><span class="sub">YOUR IT ESSENTIALS STUDY COMPANION</span></span></button>'
assert old in s;s=s.replace(old,new,1)
old='<span class="header-tag"><span class="dot"></span>Pass target: 70%</span>'
new='<nav class="app-navigation" aria-label="Main navigation"><span class="page-location" id="pageLocation" aria-current="page">Home</span><button class="btn secondary hidden" id="home" type="button">Save &amp; exit</button></nav>'
assert old in s;s=s.replace(old,new,1)
old='<button class="btn secondary" id="home" type="button" aria-label="Save quiz and return home">Home</button>'
assert old in s;s=s.replace(old,'',1)
s=s.replace('Build your confidence one question at a time. Set up a session and make your study time count.','Practise your weak areas, learn from each answer, and test your progress.',1)
s=s.replace('<h2 id="setup-title">Create your study session</h2><p>Choose how you want to practise today.</p>','<h2 id="setup-title" tabindex="-1">Your next study session</h2><p>Set your session length, then choose practice or a test.</p>',1)
old='<section id="setup" class="panel" aria-labelledby="setup-title">'
resume='''<div class="resume-card"><div><strong>Pick up where you left off</strong><p id="resumeSummary">Your saved session is ready.</p></div><button class="btn hidden" id="resume" type="button">Resume session</button></div>'''
assert old in s;s=s.replace(old,old+resume,1)
# Put progress after the primary task instead of making the form harder to find.
progress=re.search(r'<div class="learning-overview".*?</details></div>',s,re.S)
assert progress
overview=progress.group(0)
s=s[:progress.start()]+s[progress.end():]
s=s.replace('<div class="grid">','<p class="step-label">1 <span>Set your session</span></p><div class="grid">',1)
s=s.replace('Session marks</label>','Session length</label>',1)
s=s.replace('Choose a topic</label>','Practice topic</label>',1)
s=s.replace('Focus on a module or cover everything.','This topic applies to practice. Readiness tests cover all modules.',1)
start=s.index('<div class="actions"><button class="btn start-btn" id="start"')
end=s.index('<p id="setupMessage"',start)
s=s[:start]+'''<p class="step-label">2 <span>Choose your next step</span></p>
<div class="study-paths">
  <article class="study-path"><span class="path-eyebrow">Learn &amp; review</span><h3>Targeted practice</h3><p>Work on weak concepts with explanations after each answer.</p><button class="btn" id="start" type="button">Start practice <span aria-hidden="true">→</span></button></article>
  <article class="study-path"><span class="path-eyebrow">Test yourself</span><h3>Readiness test</h3><p>Mix all 14 modules. Answers stay hidden until you submit.</p><button class="btn secondary" id="readinessStart" type="button">Start readiness test <span aria-hidden="true">→</span></button></article>
</div>
'''+s[end:]
needle='<p class="save-note"><span aria-hidden="true">✓</span>Your progress is saved on this device.</p>'
assert needle in s
s=s.replace(needle,needle+'<details class="progress-disclosure"><summary>Your learning progress</summary>'+overview+'</details>',1)
# The question count doubles as an accessible navigation menu, without increasing page height.
needle='<span id="counter" class="pill"></span>'
assert needle in s
s=s.replace(needle,'''<details id="questionMenu" class="question-menu"><summary><span id="counter" class="pill"></span><span class="sr-only"> — open question navigation</span></summary><div class="question-map"><p class="small muted">Choose a question. Filled = answered · ★ = flagged</p><div id="questionGrid" class="question-grid"></div></div></details>''',1)
s=s.replace('<h2 id="question" class="quiz-heading">','<h2 id="question" class="quiz-heading" tabindex="-1">',1)
s=s.replace('<div class="actions"><button class="btn secondary" id="prev"','<div class="actions quiz-actions"><button class="btn secondary" id="prev"',1)
s=s.replace('id="finish" type="button">Finish &amp; score','id="finish" type="button">Submit quiz',1)
s=s.replace('aria-label="Answer explanation"></div>','aria-label="Answer explanation" tabindex="-1"></div>',1)
# Result actions come before the detailed module breakdown.
old='<div id="moduleResults"></div><div class="actions"><button class="btn" id="again" type="button">New quiz</button><button class="btn secondary" id="reviewWrong" type="button">Review incorrect only</button><button class="btn secondary" id="reviewAll" type="button">Review all answers</button></div>'
new='''<div class="actions result-actions"><button class="btn" id="practiceAgain" type="button">Continue practice <span aria-hidden="true">→</span></button><button class="btn secondary" id="again" type="button">Back to home</button></div><div class="review-actions" role="group" aria-label="Review answers"><button class="btn secondary" id="reviewWrong" type="button" aria-pressed="false">Review mistakes</button><button class="btn secondary" id="reviewAll" type="button" aria-pressed="false">Review all answers</button></div><details class="module-breakdown"><summary>Scores by module</summary><div id="moduleResults"></div></details>'''
assert old in s;s=s.replace(old,new,1)
# Navigation behavior is shared by the logo, exit button and result-page Home action.
helper='''  function goHome() {
    if (session) { updateTimer(); save(); }
    show('setup');
    updateLearningOverview();
    if (session) {
      $('resume').textContent = session.finished ? 'View results' : 'Resume session';
      $('resume').classList.remove('hidden');
    }
    window.scrollTo(0, 0);
    $('setup-title').focus({preventScroll: true});
  }

  function goToQuestion(index) {
    if (!canContinue() || index < 0 || index >= session.questions.length) return;
    session.index = index;
    $('questionMenu').open = false;
    save();
    render();
    window.scrollTo(0, 0);
    $('question').focus({preventScroll: true});
  }

  function renderQuestionNavigation() {
    if (!session || !$('questionMenu').open) return;
    const grid = $('questionGrid');
    grid.replaceChildren();
    session.questions.forEach((q, index) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'question-jump';
      const done = answered(session.answers[index]);
      button.classList.toggle('is-answered', done);
      button.classList.toggle('is-current', index === session.index);
      button.textContent = String(index + 1) + (session.flags[index] ? ' ★' : '');
      button.setAttribute('aria-label', 'Question ' + (index + 1) + (done ? ', answered' : ', unanswered') + (session.flags[index] ? ', flagged' : ''));
      if (index === session.index) button.setAttribute('aria-current', 'step');
      button.onclick = () => goToQuestion(index);
      grid.append(button);
    });
  }

'''
needle='  function moveToQuestion(offset) {'
start=s.index(needle);end=s.index('  function render() {',start)
s=s[:start]+helper+'''  function moveToQuestion(offset) {
    goToQuestion(session.index + offset);
  }

'''+s[end:]
needle='    currentView = which;'
assert needle in s
s=s.replace(needle,needle+'''
    $('pageLocation').textContent = which === 'setup' ? 'Home' : which === 'results' ? 'Results' : session?.mode === 'exam' ? 'Readiness test' : 'Practice';
    $('home').classList.toggle('hidden', which === 'setup');
    $('home').textContent = which === 'quiz' ? 'Save & exit' : 'Home';''',1)
# Preserve keyboard position when rebuilding answer choices.
start=s.index('      input.onchange = () => {');end=s.index('      const span =',start)
part=s[start:end]
part=part.replace('        render();','        render();\n        $(\'options\').children[i]?.children[0]?.focus?.({preventScroll: true});',1)
s=s[:start]+part+s[end:]
old="    $('next').textContent = 'Next';\n    updateTimer();"
new="""    $('next').textContent = s.mode === 'exam' || revealed ? 'Next question →' : 'Skip for now';
    $('next').classList.toggle('secondary', s.mode !== 'exam');
    $('finish').textContent = idx === s.questions.length - 1 ? 'Submit & see results' : 'Submit quiz';
    renderQuestionNavigation();
    updateTimer();"""
assert old in s;s=s.replace(old,new,1)
start=s.index("  $('home').onclick = () => {");end=s.index("  $('resume').onclick",start)
s=s[:start]+"  $('home').onclick = goHome;\n  $('brandHome').onclick = goHome;\n  $('questionMenu').ontoggle = renderQuestionNavigation;\n"+s[end:]
start=s.index("  $('again').onclick = () => {");end=s.index("  $('reviewWrong').onclick",start)
s=s[:start]+'''  $('again').onclick = goHome;
  $('practiceAgain').onclick = () => {
    $('count').value = '20';
    $('module').value = 'all';
    makeSession('practice');
  };
'''+s[end:]
s=s.replace("    $('feedback').scrollIntoView({ block: 'start', behavior: 'auto' });","    $('feedback').focus({preventScroll: true});\n    $('feedback').scrollIntoView({ block: 'start', behavior: 'auto' });",1)
needle='  function review(onlyWrong) {'
s=s.replace(needle,needle+'''
    $('reviewWrong').setAttribute('aria-pressed', String(onlyWrong));
    $('reviewAll').setAttribute('aria-pressed', String(!onlyWrong));''',1)
s=s.replace("    parent.replaceChildren(title, summary);","    parent.replaceChildren(summary);",1)
# Keep the saved-session card informative when the learner exits a running timer.
needle="  function updateLearningOverview() {"
s=s.replace(needle,needle+'''
    if (session) $('resumeSummary').textContent = session.finished
      ? 'Your last results are ready to review.'
      : 'Question ' + (session.index + 1) + ' of ' + session.questions.length + ' · ' + timeText(session.deadlineAt - Date.now()) + ' left. The timer is still running.';''',1)
s=s.replace("    $('review').replaceChildren();\n    $('resultMessage')", "    $('review').replaceChildren();\n    $('reviewWrong').setAttribute('aria-pressed', 'false');\n    $('reviewAll').setAttribute('aria-pressed', 'false');\n    $('moduleResults').parentElement.open = false;\n    $('resultMessage')",1)
# Remove obsolete toggle styling. Existing dark colors remain active from first paint.
s=re.sub(r'\.theme-toggle\{[^}]*\}\s*\.theme-toggle:hover\{[^}]*\}','',s,count=1)
css='''
.skip-link{position:fixed;top:8px;left:16px;z-index:100;background:var(--accent);color:#071024;padding:10px 16px;border-radius:8px;transform:translateY(-160%);font-weight:700}.skip-link:focus{transform:translateY(0)}
.brand-home{border:0;background:none;color:var(--ink);padding:0;text-align:left}.brand-home .brand,.brand-home .sub{display:block}.app-navigation{display:flex;align-items:center;gap:14px}.page-location{font-weight:700;color:var(--muted);font-size:12px}.app-navigation .btn{padding:9px 14px;font-size:12px}
.resume-card{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:17px 18px;border:1px solid var(--accent);border-radius:12px;margin-bottom:25px;background:#152a49}.resume-card:has(#resume.hidden){display:none}.resume-card strong{font-size:14px}.resume-card p{font-size:12px;color:var(--muted);margin:4px 0 0}.resume-card .btn{flex:none;font-size:13px}.step-label{display:flex;align-items:center;gap:9px;margin:0 0 15px;color:var(--accent);font-weight:800;font-size:12px}.step-label span{color:var(--ink);font-size:13px}.grid+.step-label{margin-top:27px}.study-paths{display:grid;grid-template-columns:1fr 1fr;gap:14px}.study-path{padding:20px;border:1px solid var(--line);border-radius:13px;background:#0d1729;display:flex;flex-direction:column}.path-eyebrow{font-size:10px;letter-spacing:.1em;text-transform:uppercase;font-weight:800;color:var(--accent)}.study-path h3{font-size:18px;margin:8px 0 6px;letter-spacing:-.025em}.study-path p{color:var(--muted);font-size:13px;line-height:1.6;margin:0 0 18px}.study-path .btn{width:100%;margin-top:auto;padding:11px 12px;font-size:13px}.progress-disclosure{border-top:1px solid var(--line);padding-top:17px;margin-top:22px}.progress-disclosure>summary,.module-breakdown>summary{cursor:pointer;color:var(--ink);font-weight:700;font-size:13px}.progress-disclosure .learning-overview{margin:15px 0 0;border:0;padding:0}.module-breakdown{border-top:1px solid var(--line);padding-top:17px;margin-top:20px}.review-actions{display:flex;gap:9px;flex-wrap:wrap;margin-top:14px}.review-actions .btn{font-size:12px;padding:9px 13px}.review-actions [aria-pressed="true"]{border-color:var(--accent);color:var(--accent)}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}.question-menu{position:relative}.question-menu>summary{cursor:pointer;list-style:none}.question-menu>summary::-webkit-details-marker{display:none}.question-menu .pill:after{content:"▾";margin-left:9px}.question-map{position:absolute;left:0;top:calc(100% + 9px);width:min(360px,80vw);max-height:290px;overflow:auto;padding:15px;background:#111d32;border:1px solid #405577;border-radius:12px;z-index:20;box-shadow:0 15px 40px #0008}.question-map>p{margin:0 0 12px;font-size:11px}.question-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:7px}.question-jump{min-height:36px;border-radius:7px;border:1px solid #3a4c6e;background:#0a1324;color:var(--ink);font-size:12px;font-weight:700}.question-jump.is-answered{background:#253f68}.question-jump.is-current{outline:2px solid var(--accent);outline-offset:1px}.question-jump:hover{border-color:var(--accent)}.quiz-actions{align-items:center}.quiz-actions #finish{margin-left:auto}.quiz-actions .btn{min-height:40px}body.quiz-active .header-inner{min-height:60px;padding-top:8px;padding-bottom:8px}body.quiz-active .sub{display:none}body.quiz-active main{padding-top:12px}body.quiz-active #quiz .quiz-heading{margin-top:13px}.result-actions .btn{min-height:44px}#feedback:focus,#question:focus,#setup-title:focus{outline:none}
@media(max-width:600px){.study-paths{grid-template-columns:1fr}.study-path{padding:17px}.study-path p{margin-bottom:14px}.resume-card{align-items:flex-start;flex-direction:column;padding:15px}.resume-card .btn{width:100%}.app-navigation{gap:10px}.page-location{font-size:11px}.header-inner{gap:10px}.app-navigation .btn{padding:8px 10px;font-size:11px}.quiz-actions #check{order:-1;flex:1 1 100%}.quiz-actions #finish{margin-left:0}.question-grid{grid-template-columns:repeat(5,1fr)}.result-actions .btn{flex:1 1 100%}}
'''
s=s.replace('</style>',css+'\n</style>',1)
p.write_text(s,encoding='utf8')
assert 'id="themeToggle"' not in s and 'localStorage.getItem("ite-theme")' not in s
print('Simplified Home, quiz and results navigation; added question menu; removed theme controls and persisted light mode.')
