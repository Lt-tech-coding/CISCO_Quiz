from pathlib import Path
p=Path('index.html');s=p.read_text(encoding='utf8')
helper='''  // Original SVG teaching diagrams stay available offline inside this HTML file.
  function appendLessonImage(parent, q) {
    const text = (q.question + ' ' + correctIndices(q).map(i => q.options[i]).join(' ')).toLowerCase();
    const diagram = (title, labels, caption, icons) => ({ title, labels, caption, icons });
    const overview = {
      1: diagram('Inside a computer', ['Processor', 'Working memory', 'Storage'], 'The CPU processes instructions, RAM holds active work, and storage retains files.', ['chip', 'ram', 'drive']),
      2: diagram('A connected system', ['Motherboard', 'Data connection', 'Storage drive'], 'Assembly brings compatible components, data cables, and power connections together.', ['board', 'cable', 'drive']),
      3: diagram('Starting a computer', ['Firmware', 'Hardware checks', 'Operating system'], 'Firmware initializes the system before control passes to the operating system.', ['chip', 'tools', 'screen']),
      4: diagram('Troubleshoot systematically', ['Gather symptoms', 'Test a cause', 'Verify the fix'], 'Use evidence to diagnose the problem, then check that the repair works.', ['document', 'tools', 'check']),
      5: diagram('Between networks', ['Local computer', 'Router', 'Other network'], 'A router forwards traffic between IP networks.', ['screen', 'router', 'cloud']),
      6: diagram('Check network connectivity', ['Client settings', 'Local connection', 'Destination'], 'Check the assigned address and local connection before investigating remote services.', ['screen', 'router', 'cloud']),
      7: diagram('A mobile workspace', ['Laptop', 'Wireless link', 'Peripherals'], 'Mobile computers combine portable hardware with wired or wireless connections.', ['screen', 'router', 'tools']),
      8: diagram('From file to paper', ['Print job', 'Print queue', 'Printer'], 'The queue manages jobs before the printer produces physical output.', ['document', 'server', 'printer']),
      9: diagram('Virtual machines share a host', ['Physical host', 'Hypervisor', 'Guest systems'], 'The hypervisor allocates the host’s resources to isolated virtual machines.', ['server', 'chip', 'screen']),
      10: diagram('Prepare before installing', ['Back up files', 'Installation media', 'Windows setup'], 'Protect existing data and verify hardware and media compatibility before installation.', ['drive', 'document', 'screen']),
      11: diagram('Choose the right Windows tool', ['Processes', 'Device drivers', 'System events'], 'Task Manager, Device Manager, and Event Viewer answer different diagnostic questions.', ['chip', 'board', 'document']),
      12: diagram('Protect a mobile device', ['Screen lock', 'Encryption', 'Trusted updates'], 'Use several layers of protection for access, stored data, and software.', ['lock', 'drive', 'check']),
      13: diagram('Layers of account protection', ['Strong password', 'Second factor', 'Limited access'], 'Authentication protects sign-in; least privilege limits what an account can do.', ['lock', 'check', 'tools']),
      14: diagram('A clear support record', ['Record symptoms', 'Record actions', 'Verify outcome'], 'A useful ticket explains the issue, the work performed, and the result.', ['document', 'tools', 'check'])
    };
    let visual = overview[q.module] || overview[4];
    if (/sata.*(data|connect)|data.*sata/.test(text)) {
      visual = diagram('SATA data: drive to motherboard', ['SATA drive', 'SATA data cable', 'Motherboard port'], 'The data cable links the drive to a SATA port. The drive has a separate power connection.', ['drive', 'cable', 'board']);
    } else if (/power supply|ac wall|converts ac/.test(text) && !/multimeter|measure|voltage\?/.test(text)) {
      visual = diagram('Power conversion', ['AC wall supply', 'Power supply unit', 'DC to components'], 'The PSU converts wall AC into the regulated DC power used inside the computer.', ['plug', 'server', 'board']);
    } else if (/thermal|heat sink|overheat|cooling airflow/.test(text)) {
      visual = diagram('Move heat away from the CPU', ['CPU generates heat', 'Paste + heat sink', 'Fan and airflow'], 'Thermal paste fills tiny gaps; the heat sink transfers heat, and airflow carries it away.', ['chip', 'cooler', 'fan']);
    } else if (/ram|working memory|sodimm|so-dimm/.test(text)) {
      visual = diagram('RAM is working memory', ['Open application', 'Active data in RAM', 'CPU uses the data'], 'RAM stores active work temporarily. Unlike storage, it loses its contents when power is removed.', ['screen', 'ram', 'chip']);
    } else if (/dhcp|169\\.254/.test(text)) {
      visual = diagram('DHCP supplies an IP configuration', ['Client requests', 'DHCP server', 'Address leased'], 'If a Windows client cannot obtain a lease, it may assign itself a 169.254.x.x link-local address.', ['screen', 'server', 'document']);
    } else if (/dns|domain names/.test(text)) {
      visual = diagram('DNS: names to addresses', ['Domain name', 'DNS lookup', 'IP address'], 'DNS resolves a name to an address. It does not supply the client’s network configuration.', ['document', 'server', 'screen']);
    } else if (/gateway|router|different ip networks|between ip networks/.test(text)) {
      visual = overview[5];
    } else if (/raid|mirroring/.test(text)) {
      visual = /raid 0|without redundancy/.test(text)
        ? diagram('RAID 0: striped data', ['Data blocks', 'Split across disks', 'No redundancy'], 'Striping distributes data for performance; one failed disk can make the array’s data unavailable.', ['document', 'drive', 'drive'])
        : diagram('RAID 1: mirrored data', ['Original data', 'Disk A: copy', 'Disk B: copy'], 'Mirroring keeps duplicate data on drives. It does not replace an independent backup.', ['document', 'drive', 'drive']);
    } else if (/phishing/.test(text)) {
      visual = diagram('Recognize the phishing trap', ['Deceptive message', 'Fake request', 'Stolen information'], 'Pause and verify the sender through a trusted channel before sharing information or opening links.', ['document', 'lock', 'document']);
    } else if (/fuser|toner|laser/.test(text)) {
      visual = diagram('Laser printing: fixing the image', ['Toner on paper', 'Fuser: heat + pressure', 'Bonded print'], 'The fuser bonds toner to the paper. Let hot printer parts cool before servicing.', ['document', 'cooler', 'printer']);
    } else if (/snapshot/.test(text)) {
      visual = diagram('A rollback point for a VM', ['Capture snapshot', 'Test a change', 'Revert if needed'], 'A snapshot records a point-in-time state for rollback. Keep independent backups as well.', ['drive', 'tools', 'check']);
    }
    const icons = {
      screen: '<rect x="-25" y="-19" width="50" height="33" rx="4"/><path d="M0 14v9m-14 0h28"/>',
      chip: '<rect x="-19" y="-19" width="38" height="38" rx="5"/><rect x="-10" y="-10" width="20" height="20"/><path d="M-28-12h9m-9 12h9m-9 12h9m38-24h9m-9 12h9m-9 12h9M-12-28v9M0-28v9m12-9v9m-24 38v9M0 19v9m12-9v9"/>',
      ram: '<rect x="-32" y="-13" width="64" height="26" rx="3"/><path d="M-26 13v7m8-7v7m8-7v7m8-7v7m8-7v7m8-7v7m8-7v7"/><path d="M-23-6h10V6h-10zm18 0H5V6H-5zm18 0h10V6H13z"/>',
      drive: '<rect x="-25" y="-22" width="50" height="44" rx="5"/><circle r="13"/><circle r="3"/><path d="m3 3 16 13m-36 0h4"/>',
      board: '<rect x="-27" y="-24" width="54" height="48" rx="4"/><rect x="-16" y="-12" width="20" height="20"/><path d="M13-15v28m7-28v28M-19 16h21m11 2h11"/>',
      cable: '<path d="M-24-9h9v18h-9zm48 0h-9v18h9zM-15 0h30M-30-5h6m0 10h-6m54-10h6m-6 10h6"/>',
      router: '<rect x="-27" y="0" width="54" height="20" rx="4"/><path d="M-18 0v-20m36 20v-20m-32 31h2m7 0h2m7 0h2M-9-13q9-10 18 0m-13 4q4-4 8 0"/>',
      server: '<rect x="-24" y="-25" width="48" height="50" rx="4"/><path d="M-24-8h48m-48 17h48m-39-25h4m-4 17h4m-4 17h4m10-34h14m-14 17h14m-14 17h14"/>',
      cloud: '<path d="M-20 17h40a13 13 0 0 0 2-26 22 22 0 0 0-42-2 14 14 0 0 0 0 28Z"/>',
      document: '<path d="M-20-26H9l13 13v39h-42Zm29 0v13h13M-11-3h22m-22 10h22m-22 10H4"/>',
      lock: '<rect x="-20" y="-4" width="40" height="29" rx="5"/><path d="M-12-4v-11a12 12 0 0 1 24 0v11M0 6v9"/>',
      check: '<circle r="26"/><path d="m-13 0 9 10 19-21"/>',
      tools: '<path d="m-22 22 27-27a16 16 0 0 0 18-19L12-13l-9-9 11-11A16 16 0 0 0-5-5l-27 27Z"/>',
      cooler: '<rect x="-27" y="-18" width="54" height="36" rx="3"/><path d="M-19-18v36m9-36v36m10-36v36m10-36v36m9-36v36"/>',
      fan: '<circle r="26"/><circle r="5"/><path d="M0-5q-22-30-22-1 2 12 17 8M5 0q30-22 1-22-12 2-8 17M0 5q22 30 22 1-2-12-17-8M-5 0q-30 22-1 22 12-2 8-17"/>',
      printer: '<path d="M-18-9v-16h36v16m-36 27h-9V-9h54v27h-9M-18 7h36v21h-36zM-10 15h20m-20 6h16"/>',
      plug: '<path d="M-12-27v17m24-17v17M-20-10h40v6a20 20 0 0 1-40 0ZM0 16v15"/>'
    };
    const escape = value => value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
    const figure = document.createElement('figure');
    figure.className = 'lesson-image';
    let svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 220" role="img" aria-label="' + escape(visual.title + '. ' + visual.caption) + '"><text x="28" y="31" class="diagram-small">VISUAL EXPLANATION</text><text x="28" y="57" class="diagram-label">' + escape(visual.title) + '</text>';
    visual.labels.forEach((label, i) => {
      const x = 110 + i * 250;
      svg += '<rect class="diagram-node" x="' + (x - 83) + '" y="77" width="166" height="125" rx="13"/><g transform="translate(' + x + ' 124)" stroke="#a9c9ff" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' + (icons[visual.icons[i]] || icons.document) + '</g><text x="' + x + '" y="181" text-anchor="middle" class="diagram-small">' + escape(label) + '</text>';
      if (i < 2) svg += '<path class="diagram-wire" d="M' + (x + 94) + ' 138h45m-8-8 8 8-8 8"/>';
    });
    figure.innerHTML = svg + '</svg>';
    const caption = document.createElement('figcaption');
    caption.textContent = visual.caption;
    figure.append(caption);
    parent.append(figure);
  }
'''
assert '  function appendStudyNotes(parent, q)' in s
s=s.replace('  function appendStudyNotes(parent, q)',helper+'\n  function appendStudyNotes(parent, q)',1)
p.write_text(s,encoding='utf8')
