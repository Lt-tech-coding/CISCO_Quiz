from pathlib import Path
import re

path=Path('index.html')
s=path.read_text(encoding='utf8')
helper=Path('tmp/notes/adaptive-runtime.js').read_text(encoding='utf8')
needle='  function valid(q) {'
assert needle in s
s=s.replace(needle,helper+'\n'+needle,1)
s=s.replace('  function show(which) {','  function show(which) {\n    currentView = which;',1)
start=s.index('  function start() {')
end=s.index('  // Downloaded source diagrams',start)
s=s[:start]+"  function start() {\n    makeSession('practice');\n  }\n"+s[end:]
s=s.replace('  function render() {\n    show(\'quiz\');',"  function render() {\n    if (!canContinue()) return;\n    show('quiz');",1)
s=s.replace("      idx = s.index;\n    $('counter')", "      idx = s.index;\n    markSeen(q);\n    $('quizHelp').textContent = s.mode === 'exam' ? 'Readiness test: answers appear after submission. The timer keeps running on Home.' : 'Check each answer to learn. The timer keeps running on Home.';\n    $('sessionKind').textContent = s.mode === 'exam' ? 'Readiness test' : 'Targeted practice';\n    $('counter')",1)
s=s.replace('      input.onchange = () => {','      input.onchange = () => {\n        if (!canContinue()) return;',1)
s=s.replace("    $('next').textContent = 'Next';\n  }", "    $('next').textContent = 'Next';\n    updateTimer();\n  }",1)
s=s.replace('  function moveToQuestion(offset) {','  function moveToQuestion(offset) {\n    if (!canContinue()) return;',1)
start=s.index('  function finish() {')
end=s.index('  function results() {',start)
s=s[:start]+'''  function finish() {
    if (!canContinue()) return;
    const unanswered = session.questions.filter((q, index) => !answered(session.answers[index])).length;
    if (!confirm(`Submit quiz? ${unanswered} unanswered question(s) will count as incorrect.`)) return;
    finalizeSession(false);
  }
'''+s[end:]
needle="    $('review').replaceChildren();\n  }\n  function review(onlyWrong)"
assert needle in s
s=s.replace(needle,"""    $('review').replaceChildren();
    $('resultMessage').textContent = (s.timeExpired ? 'Time is up. Your answers were submitted automatically. ' : '') +
      (s.mode === 'exam' ? 'Readiness test: ' : 'Targeted practice: ') + right + ' of ' + total + ' marks. Unanswered questions count as incorrect.';
    appendModuleResults($('moduleResults'));
    updateLearningOverview();
  }
  function review(onlyWrong)""",1)
start=s.index("  $('start').onclick = start;")
end=s.index("  $('prev').onclick",start)
s=s[:start]+'''  $('start').onclick = start;
  $('readinessStart').onclick = () => makeSession('exam');
  $('home').onclick = () => {
    updateTimer();
    save();
    show('setup');
    updateLearningOverview();
    $('resume').textContent = session.finished ? 'View saved results' : 'Resume saved quiz';
    $('resume').classList.remove('hidden');
    window.scrollTo(0, 0);
  };
  $('resume').onclick = () => {
    session = safeParse(safeGet(store), null);
    if (!session || !Array.isArray(session.questions)) return;
    ensureSessionMetadata();
    if (!session.finished && Date.now() >= session.deadlineAt) finalizeSession(true);
    session.finished ? results() : render();
    window.scrollTo(0, 0);
  };
'''+s[end:]
s=s.replace("  $('check').onclick = () => {", "  $('check').onclick = () => {\n    if (!canContinue()) return;",1)
s=s.replace('    session.checked[session.index] = true;\n    save();', '    session.checked[session.index] = true;\n    recordAttempt(session.index);\n    scheduleFollowUp(session.index);\n    save();',1)
s=s.replace("  $('flag').onclick = () => {", "  $('flag').onclick = () => {\n    if (!canContinue()) return;",1)
needle="  const saved = safeParse(safeGet(store), null);\n  if (saved && Array.isArray(saved.questions)) $('resume').classList.remove('hidden');"
assert needle in s
s=s.replace(needle,"""  const saved = safeParse(safeGet(store), null);
  if (saved && Array.isArray(saved.questions)) {
    session = saved;
    if (!session.finished) { ensureSessionMetadata(); save(); updateTimer(); }
    $('resume').textContent = session.finished ? 'View saved results' : 'Resume saved quiz';
    $('resume').classList.remove('hidden');
  }
  $('count').onchange = updateLearningOverview;
  $('module').onchange = updateLearningOverview;
  updateLearningOverview();
  setInterval(updateTimer, 1000);
  window.addEventListener('focus', updateTimer);
  document.addEventListener('visibilitychange', updateTimer);""",1)
# Learner-facing controls; no technical algorithm settings are exposed.
needle='<div class="grid">'
assert needle in s
s=s.replace(needle,'''<div class="learning-overview" aria-label="Your learning progress"><div><strong id="conceptProgress"></strong><span id="reviewProgress"></span></div><p id="readinessProgress"></p></div>
<div class="grid">''',1)
s=s.replace('<label class="field-label" for="count">Number of questions</label>','<label class="field-label" for="count">Session marks</label>',1)
for n in [20,50,100]: s=s.replace(f'<option value="{n}">{n} questions</option>',f'<option value="{n}">{n} marks</option>',1)
s=s.replace('<span class="field-help">Pick a pace that works for you.</span>', '<span class="field-help" id="timeEstimate"></span>',1)
s=s.replace('Start practising <span aria-hidden="true">→</span>', 'Targeted practice <span aria-hidden="true">→</span>',1)
needle='<button class="btn secondary hidden" id="resume"'
assert needle in s
s=s.replace(needle,'<button class="btn secondary" id="readinessStart" type="button">Readiness test</button>'+needle,1)
s=s.replace('<p class="save-note">','<p class="small muted">Readiness tests mix all 14 modules and reveal answers after submission.</p><p id="setupMessage" class="setup-message" role="status"></p><p class="save-note">',1)
needle='<section id="quiz" class="panel hidden" aria-label="Quiz">'
assert needle in s
s=s.replace(needle,needle+'<div class="session-clock"><span id="sessionKind">Targeted practice</span><span class="clock-label">Time left <strong id="timer" role="timer" aria-live="off">00:00</strong></span></div>',1)
s=s.replace('<p class="small muted">Check each answer to learn as you go. Unanswered questions count as incorrect when you finish.</p>','<p class="small muted" id="quizHelp">Check each answer to learn. The timer keeps running on Home.</p>',1)
s=s.replace('<div id="stats" class="stats"></div>','<div id="stats" class="stats"></div><p id="resultMessage" class="small muted"></p><div id="moduleResults"></div>',1)
css='''
.learning-overview{padding:17px 19px;border:1px solid var(--line);border-radius:12px;margin-bottom:23px;background:var(--panel)}.learning-overview strong{display:block;font-size:15px}.learning-overview span,.learning-overview p{font-size:12px;color:var(--muted)}.learning-overview p{margin:10px 0 0;padding-top:10px;border-top:1px solid var(--line)}.setup-message{color:var(--bad);font-size:13px}.setup-message:empty{display:none}.session-clock{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:13px;font-size:12px;color:var(--muted)}.clock-label{display:flex;align-items:center;gap:10px}#timer{font-variant-numeric:tabular-nums;color:var(--ink);font-size:20px;letter-spacing:.03em}#timer.time-low{color:var(--bad)}#moduleResults{margin-top:24px}#moduleResults h3{font-size:17px}.module-results{display:grid;grid-template-columns:1fr 1fr;gap:8px 16px}.module-results p{margin:0;font-size:12px;line-height:1.5}
@media(max-width:560px){.module-results{grid-template-columns:1fr}.session-clock{margin-bottom:9px}#timer{font-size:18px}.learning-overview{padding:13px 15px}}
'''
s=s.replace('</style>',css+'\n</style>',1)
path.write_text(s,encoding='utf8')
print('Installed adaptive practice, concept tracking, follow-up lessons, readiness tests, and persistent per-mark timers.')
