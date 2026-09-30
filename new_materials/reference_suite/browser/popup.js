const $ = (id) => document.getElementById(id);
const endpoint = 'http://127.0.0.1:8765';
const operations = {
  openalex: ['lookup', 'search'],
  uspto: ['application', 'documents', 'search', 'petition', 'bulk', 'ptab_trials', 'ptab_documents', 'ptab_decisions', 'ptab_appeals', 'ptab_interferences', 'get'],
  web: ['capture', 'mirror']
};

function updateOperations() {
  const select = $('operation');
  select.replaceChildren(...operations[$('provider').value].map(name => new Option(name, name)));
}

$('provider').addEventListener('change', updateOperations);
updateOperations();

chrome.storage.local.get(['selectedReference'], ({ selectedReference }) => {
  if (selectedReference) $('value').value = selectedReference;
});

function job() {
  return {
    provider: $('provider').value,
    operation: $('operation').value,
    value: $('value').value.trim(),
    max_results: Number($('max-results').value),
    citation_depth: Number($('citation-depth').value),
    max_depth: Number($('max-depth').value),
    download_files: $('download-files').checked,
    render_js: $('render-js').checked,
    render_pdf: $('render-pdf').checked,
    content_selector: $('content-selector').value.trim(),
    allow_hosts: $('hosts').value.split(',').map(s => s.trim()).filter(Boolean)
  };
}

async function request(path) {
  const output = $('output');
  output.textContent = 'Working...';
  try {
    const response = await fetch(endpoint + path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Reference-Suite-Token': $('token').value },
      body: JSON.stringify(job())
    });
    const result = await response.json();
    output.textContent = JSON.stringify(result, null, 2);
    if (response.ok && result.job_id) poll(result.job_id);
  } catch (error) {
    output.textContent = String(error);
  }
}

async function poll(id) {
  for (let i = 0; i < 120; i++) {
    await new Promise(resolve => setTimeout(resolve, 1000));
    try {
      const response = await fetch(endpoint + '/jobs/' + encodeURIComponent(id), {
        headers: { 'X-Reference-Suite-Token': $('token').value }
      });
      const result = await response.json();
      $('output').textContent = JSON.stringify(result, null, 2);
      if (result.status !== 'running') return;
    } catch (error) {
      $('output').textContent = String(error);
      return;
    }
  }
}

$('preview').addEventListener('click', () => request('/plan'));
$('run').addEventListener('click', () => request('/jobs'));
