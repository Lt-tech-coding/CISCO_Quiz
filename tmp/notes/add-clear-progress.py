from pathlib import Path

p=Path('index.html');s=p.read_text(encoding='utf8')
needle='<details class="progress-disclosure">'
assert needle in s
s=s.replace(needle,'<div class="progress-tools"><button class="btn secondary" id="clearProgress" type="button">Clear progress</button></div>'+needle,1)
needle="    $('setupMessage').textContent = '';"
assert needle in s
s=s.replace(needle,needle+"\n    $('setupMessage').classList.remove('success');",1)
needle="  $('start').onclick = start;"
handler='''  $('clearProgress').onclick = () => {
    if (!confirm('Clear all learning progress, test results and your saved quiz? This cannot be undone.')) return;
    $('setupMessage').classList.remove('success');
    try {
      localStorage.removeItem(store);
      localStorage.removeItem(learningStore);
    } catch (_) {
      $('setupMessage').textContent = 'Unable to clear progress. Please try again.';
      return;
    }
    session = null;
    learning = {concepts: {}, seenFamilies: {}, tests: []};
    $('resume').classList.add('hidden');
    $('resumeSummary').textContent = '';
    $('timer').textContent = '00:00';
    $('timer').classList.remove('time-low');
    $('review').replaceChildren();
    $('feedback').replaceChildren();
    $('feedback').classList.add('hidden');
    show('setup');
    updateLearningOverview();
    $('setupMessage').classList.add('success');
    $('setupMessage').textContent = 'Progress cleared. You can start fresh.';
  };
'''
assert needle in s
s=s.replace(needle,handler+needle,1)
s=s.replace('</style>','.progress-tools{display:flex;justify-content:flex-end;margin-top:15px}.progress-tools .btn{padding:7px 11px;font-size:12px}.setup-message.success{color:var(--good)}\n</style>',1)
p.write_text(s,encoding='utf8')
print('Added confirmed progress reset on Home. Only this quiz\'s session and learning records are removed.')
