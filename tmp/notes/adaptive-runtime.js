  const learningStore = 'ite8_learning_v1';
  const minute = 60 * 1000;
  const day = 24 * 60 * minute;
  let currentView = 'setup';
  let learning = safeParse(safeGet(learningStore), null) || {};
  learning.concepts ||= {};
  learning.seenFamilies ||= {};
  learning.tests ||= [];

  // Variants share a lesson key. Related new scenarios join that same concept.
  const relatedConcepts = {
    'CPU cache': 'cpu-cache', 'Firmware storage': 'uefi',
    'CPU alignment': 'cpu-installation', 'Cooler preparation': 'cooling',
    'CPU compatibility': 'cpu-compatibility', 'DDR compatibility': 'sodimm',
    'Memory channels': 'raminstall', 'PSU capacity': 'psu',
    'Mechanical storage': 'ssd', 'Rear I/O shield': 'motherboard-mounting',
    'Front-panel wiring': 'front-panel', 'Expansion-card power': 'eps',
    'Loose hardware': 'standoffs', 'Correct mounting': 'standoffs',
    'Modular PSU cables': 'psu', 'CPU-fan header': 'cooling',
    'Final assembly check': 'airflow', 'Boot order': 'uefi',
    'Firmware update preparation': 'uefi', 'Hardware virtualization': 'hypervisor',
    'Firmware password scope': 'encryption', 'Firmware recovery': 'uefi',
    'Controlled troubleshooting': 'troubleshoot', 'Known-good testing': 'testcause',
    'Intermittent problems': 'troubleshoot', 'Protecting data': 'backup',
    'Dust removal': 'airflow', 'Fan cleaning': 'airflow',
    'No-power diagnosis': 'psu', 'After-service fault': 'cooling',
    'Memory testing': 'ram', 'Subnet capacity': 'subnet',
    'Local versus remote': 'subnet', 'Prefix conversion': 'subnet',
    'Broadcast address': 'subnet', 'DNS testing': 'dns',
    'DHCP ports': 'dhcp', 'DHCP renewal': 'dhcp',
    'DNS transport': 'dns', 'Isolating name-resolution faults': 'dns',
    'Airplane mode': 'wifi', 'Brightness control': 'backlight',
    'Battery disposal': 'battery', 'Storage upgrade preparation': 'backup',
    'Laptop antenna leads': 'wifi', 'Power adapter compatibility': 'battery',
    'Laser development stage': 'laser', 'Printer driver mismatch': 'printer-driver',
    'Stuck queue': 'spooler', 'Print server': 'spooler',
    'Paper handling': 'printercare', 'Standalone test page': 'printerlink',
    'VM resource planning': 'virtualbenefits', 'Type 2 hypervisor': 'hypervisor',
    'Installation verification': 'verify', 'Post-install updates': 'installprep',
    'Selecting the target disk': 'approval', 'Trusted driver source': 'devicemanager',
    'Upgrade installation': 'cleaninstall', 'Large disks': 'gpt',
    'Driver rollback': 'devicemanager', 'File permissions': 'leastprivilege',
    'Revoking access': 'permissions', 'Application sources': 'permissions',
    'Factory reset preparation': 'backup', 'Ransomware response': 'ransomware',
    'Unattended workstation': 'mobilecare', 'Physical security': 'mobilecare',
    'Backup diversity': 'backup', 'Open questions': 'listening',
    'Remote support consent': 'approval', 'Credential handling': 'accountcare',
    'Rollback planning': 'backup', 'Data sanitization': 'approval',
    'Empathy in support': 'listening', 'Useful escalation': 'escalate'
  };

  function conceptKey(q) {
    return window.ITE_QUESTION_LESSONS[q.id] || relatedConcepts[q.lesson?.title] ||
      'topic-' + String(q.lesson?.title || q.id).toLowerCase().replace(/[^a-z0-9]+/g, '-');
  }

  function familyKey(q) {
    if (q.id.startsWith('ite8-expanded-')) return q.id;
    return q.module + ':' + correctIndices(q).map(i => q.options[i].trim().toLowerCase()).sort().join('|');
  }

  function conceptLabel(q) {
    return window.ITE_LESSONS[conceptKey(q)]?.title || q.lesson?.title || 'Module ' + q.module;
  }

  function saveLearning() {
    try { localStorage.setItem(learningStore, JSON.stringify(learning)); } catch (_) {}
  }

  function answered(value) {
    return value !== undefined && (!Array.isArray(value) || value.length > 0);
  }

  function conceptState(key) {
    const record = learning.concepts[key];
    if (!record?.history?.length) return 'new';
    const recent = record.history.slice(-5);
    const accuracy = recent.filter(item => item.correct).length / recent.length;
    if (!recent.at(-1).correct || accuracy < 0.7) return 'weak';
    if (record.dueAt <= Date.now()) return 'due';
    return 'learning';
  }

  function secureConcept(record) {
    const history = record.history || [];
    const recent = history.slice(-3);
    return recent.length === 3 && recent.every(item => item.correct) &&
      new Set(recent.map(item => item.session)).size >= 2 &&
      new Set(recent.map(item => item.family)).size >= 2;
  }

  function shuffledQuestion(q) {
    const choices = shuffle(q.options.map((label, index) => ({label, index})));
    const result = {...q, options: choices.map(item => item.label)};
    if (Array.isArray(q.answers)) {
      result.answers = choices.flatMap((item, index) => q.answers.includes(item.index) ? [index] : []);
    } else result.answer = choices.findIndex(item => item.index === q.answer);
    return result;
  }

  function choosePractice(pool, count) {
    const groups = new Map();
    shuffle([...pool]).forEach(q => {
      const key = conceptKey(q);
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(q);
    });
    // Exhaust a concept's unseen families before recycling wording variants.
    groups.forEach(questions => questions.sort((a, b) =>
      Number(!!learning.seenFamilies[familyKey(a)]) - Number(!!learning.seenFamilies[familyKey(b)])));
    const selected = [];
    const conceptUses = {};
    const usedFamilies = new Set();
    const coverageIncomplete = [...groups.keys()].some(key => conceptState(key) === 'new');
    const fractions = coverageIncomplete ? [['weak', .3], ['due', .2], ['new', .5]] : [['weak', .5], ['due', .3], ['new', .2]];
    const quotas = fractions.map(([state, fraction]) => [state, Math.floor(count * fraction)]);

    function take(state) {
      const keys = [...groups.keys()].filter(key => groups.get(key).length && (!state || conceptState(key) === state));
      shuffle(keys);
      keys.sort((a, b) => (conceptUses[a] || 0) - (conceptUses[b] || 0));
      if (!keys.length) return false;
      const key = keys[0];
      const list = groups.get(key);
      const novel = list.findIndex(q => !usedFamilies.has(familyKey(q)));
      const [q] = list.splice(novel < 0 ? 0 : novel, 1);
      usedFamilies.add(familyKey(q));
      conceptUses[key] = (conceptUses[key] || 0) + 1;
      selected.push(q);
      return true;
    }

    quotas.forEach(([state, quota]) => {
      for (let i = 0; i < quota; i++) if (!take(state)) break;
    });
    while (selected.length < count && take(null)) {}
    return shuffle(selected).map(shuffledQuestion);
  }

  function chooseReadiness(pool, count) {
    const families = new Map();
    shuffle([...pool]).forEach(q => {
      const family = familyKey(q);
      if (!learning.seenFamilies[family] && !families.has(family)) families.set(family, q);
    });
    if (families.size < count) {
      $('setupMessage').textContent = 'You have ' + families.size + ' unseen question families left. Choose a shorter readiness test, or continue targeted practice.';
      return null;
    }
    const byModule = new Map();
    families.forEach(q => {
      if (!byModule.has(q.module)) byModule.set(q.module, []);
      byModule.get(q.module).push(q);
    });
    // A mixed test needs at least one unseen family in every module.
    if (byModule.size < 14) {
      $('setupMessage').textContent = 'A fresh mixed test needs unseen questions in all 14 modules. Continue targeted practice; repeated questions will not be counted as a fresh readiness test.';
      return null;
    }
    const selected = [];
    while (selected.length < count) {
      let added = false;
      shuffle([...byModule.keys()]).forEach(module => {
        if (selected.length < count && byModule.get(module).length) {
          selected.push(byModule.get(module).pop());
          added = true;
        }
      });
      if (!added) break;
    }
    return shuffle(selected).map(shuffledQuestion);
  }

  function makeSession(kind) {
    $('setupMessage').textContent = '';
    const readiness = kind === 'exam';
    const pool = bank.filter(q => readiness || $('module').value === 'all' || q.module === Number($('module').value));
    if (!pool.length) {
      $('setupMessage').textContent = 'Choose another topic to start practising.';
      return;
    }
    const countValue = $('count').value;
    if (readiness && countValue === 'all') {
      $('setupMessage').textContent = 'Choose 20, 50 or 100 marks for a readiness test.';
      return;
    }
    const requested = countValue === 'all' ? pool.length : Number(countValue);
    const count = Math.min(requested, pool.length);
    const questions = readiness ? chooseReadiness(pool, count) : choosePractice(pool, count);
    if (!questions?.length) return;
    const durationMs = questions.length * 72 * 1000;
    session = {
      id: 'session-' + Date.now() + '-' + Math.random().toString(36).slice(2),
      questions, answers: {}, checked: {}, flags: {}, index: 0,
      mode: readiness ? 'exam' : 'practice', finished: false,
      startedAt: Date.now(), deadlineAt: Date.now() + durationMs,
      durationMs, recorded: {}, followUps: {}, freshTest: readiness
    };
    save();
    render();
  }

  function ensureSessionMetadata() {
    session.id ||= 'saved-' + Date.now() + '-' + Math.random().toString(36).slice(2);
    session.recorded ||= {};
    session.followUps ||= {};
    if (!session.deadlineAt && !session.finished) {
      session.durationMs = session.questions.length * 72 * 1000;
      session.startedAt = Date.now();
      session.deadlineAt = Date.now() + session.durationMs;
    }
  }

  function markSeen(q) {
    const key = familyKey(q);
    if (!learning.seenFamilies[key]) {
      learning.seenFamilies[key] = Date.now();
      saveLearning();
    }
  }

  function recordAttempt(index) {
    if (session.recorded[index]) return;
    const q = session.questions[index];
    const key = conceptKey(q);
    const family = familyKey(q);
    const record = learning.concepts[key] ||= {label: conceptLabel(q), history: [], dueAt: 0};
    // A second wording of a family in one session cannot inflate concept mastery.
    if (!record.history.some(item => item.session === session.id && item.family === family)) {
      const correct = isCorrect(q, session.answers[index]);
      record.history.push({correct, family, session: session.id, at: Date.now()});
      record.history = record.history.slice(-30);
      record.dueAt = Date.now() + (correct ? (secureConcept(record) ? 2 * day : day) : 5 * minute);
    }
    session.recorded[index] = true;
    saveLearning();
  }

  function scheduleFollowUp(index) {
    const q = session.questions[index];
    const key = conceptKey(q);
    if (isCorrect(q, session.answers[index]) || session.followUps[key]) return;
    const slot = session.questions.findIndex((item, position) => position >= index + 3 &&
      !answered(session.answers[position]) && !session.checked[position] && !session.followUpSlots?.[position]);
    if (slot < 0) return;
    const queued = new Set(session.questions.map(item => item.id));
    const candidates = shuffle(bank.filter(item => conceptKey(item) === key && !queued.has(item.id)));
    candidates.sort((a, b) => Number(familyKey(a) === familyKey(q)) - Number(familyKey(b) === familyKey(q)));
    if (!candidates.length) return;
    session.questions[slot] = shuffledQuestion(candidates[0]);
    session.followUps[key] = true;
    session.followUpSlots ||= {};
    session.followUpSlots[slot] = true;
  }

  function timeText(milliseconds) {
    const seconds = Math.max(0, Math.ceil(milliseconds / 1000));
    return String(Math.floor(seconds / 60)).padStart(2, '0') + ':' + String(seconds % 60).padStart(2, '0');
  }

  function updateTimer() {
    if (!session || session.finished) return;
    ensureSessionMetadata();
    const remaining = session.deadlineAt - Date.now();
    $('timer').textContent = timeText(remaining);
    $('timer').classList.toggle('time-low', remaining <= 5 * minute);
    if (remaining <= 0) finalizeSession(true);
  }

  function canContinue() {
    if (!session || session.finished) return false;
    ensureSessionMetadata();
    if (Date.now() >= session.deadlineAt) {
      finalizeSession(true);
      return false;
    }
    return true;
  }

  function finalizeSession(expired) {
    if (!session || session.finished) return;
    const wasInQuiz = currentView === 'quiz';
    session.timeExpired = expired;
    session.finished = true;
    session.questions.forEach((q, index) => {
      if (session.mode === 'exam' || session.checked[index] || answered(session.answers[index])) recordAttempt(index);
    });
    if (session.mode === 'exam' && session.freshTest && !learning.tests.some(test => test.session === session.id)) {
      const score = Math.round(session.questions.filter((q, index) => isCorrect(q, session.answers[index])).length / session.questions.length * 100);
      learning.tests.push({session: session.id, score, marks: session.questions.length, at: Date.now()});
      learning.tests = learning.tests.slice(-10);
      saveLearning();
    }
    save();
    updateLearningOverview();
    if (wasInQuiz) { results(); window.scrollTo(0, 0); }
    else {
      $('resume').textContent = 'View saved results';
      $('resume').classList.remove('hidden');
    }
  }

  function updateLearningOverview() {
    const concepts = new Set(bank.map(conceptKey));
    let seen = 0, weak = 0, due = 0;
    concepts.forEach(key => {
      const state = conceptState(key);
      if (state !== 'new') seen++;
      if (state === 'weak') weak++;
      if (state === 'due') due++;
    });
    $('conceptProgress').textContent = seen + ' of ' + concepts.size + ' concepts practised';
    $('reviewProgress').textContent = weak + ' need work · ' + due + ' due for review';
    const tests = learning.tests.slice(-2);
    $('readinessProgress').textContent = tests.length === 2 && tests.every(test => test.score >= 85)
      ? 'Readiness target met: two fresh tests at 85%+. Keep reviewing weak modules.'
      : 'Readiness goal: 85%+ in two fresh mixed tests. This is a practice target.';
    $('timeEstimate').textContent = $('count').value === 'all'
      ? '1 mark per question · 72 seconds per mark. The full bank is a long session.'
      : $('count').value + ' marks · ' + (Number($('count').value) * 1.2) + ' minutes · 1 mark per question';
  }

  function appendModuleResults(parent) {
    const title = document.createElement('h3');
    title.textContent = 'Where to focus next';
    const summary = document.createElement('div');
    summary.className = 'module-results';
    names.forEach((name, module) => {
      let total = 0, correct = 0;
      session.questions.forEach((q, index) => {
        if (Number(q.module) !== module + 1) return;
        total++;
        if (isCorrect(q, session.answers[index])) correct++;
      });
      if (!total) return;
      const row = document.createElement('p');
      row.textContent = 'Module ' + (module + 1) + ': ' + name + ' — ' + correct + '/' + total;
      row.className = correct / total < .7 ? 'bad' : 'muted';
      summary.append(row);
    });
    parent.replaceChildren(title, summary);
    const guidance = document.createElement('p');
    guidance.className = 'small muted';
    guidance.textContent = 'These module scores show this session only. Targeted practice will revisit weak concepts.';
    parent.append(guidance);
  }
