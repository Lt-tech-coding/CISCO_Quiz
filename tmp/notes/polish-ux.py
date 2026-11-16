from pathlib import Path
p=Path('index.html');s=p.read_text(encoding='utf8')
s=s.replace('<main id="mainContent">','<main id="mainContent" tabindex="-1">',1)
s=s.replace('<strong>Pick up where you left off</strong>','<strong id="resumeTitle">Your session is in progress</strong>',1)
s=s.replace("'Resume saved quiz'", "'Resume session'")
s=s.replace("'View saved results'", "'View results'")
needle="    document.body.classList.toggle('quiz-active', which === 'quiz');"
assert needle in s
s=s.replace(needle,needle+"\n    document.body.classList.toggle('results-active', which === 'results');",1)
needle="    const remaining = session.deadlineAt - Date.now();"
s=s.replace(needle,needle+"\n    if (currentView === 'setup') $('resumeSummary').textContent = 'Question ' + (session.index + 1) + ' of ' + session.questions.length + ' · ' + timeText(remaining) + ' left. The timer is still running.';",1)
needle="  function updateLearningOverview() {"
s=s.replace(needle,needle+"\n    $('resumeTitle').textContent = session?.finished ? 'Your latest results' : 'Your session is in progress';",1)
s=s.replace('</style>','body.results-active .hero,body.results-active .sidebar{display:none}body.results-active .layout{display:block}body.results-active main{max-width:950px;padding-top:24px}\n</style>',1)
p.write_text(s,encoding='utf8')
