import fs from 'node:fs';
import { execSync } from 'node:child_process';

const endpoint = 'http://127.0.0.1:7699/ingest/ebdb5115-d9dd-44c6-8d91-a7579c00ee54';
const runId = process.env.DEBUG_RUN_ID || 'run1';

async function logDebug(hypothesisId, location, message, data) {
  // #region agent log
  await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Debug-Session-Id': '734dd4' },
    body: JSON.stringify({
      sessionId: '734dd4',
      runId,
      hypothesisId,
      location,
      message,
      data,
      timestamp: Date.now(),
    }),
  }).catch(() => {});
  // #endregion
}

const depYml = fs.readFileSync('.github/dependabot.yml', 'utf8');
const labelsConfigured = (depYml.match(/-\s+"dependencies"|-\s+"github-actions"|-\s+"python"|-\s+"javascript"|-\s+"docker"/g) || []).length;
await logDebug('H1', '.cursor/dependabot-investigate.mjs:26', 'Dependabot labels configured in YAML', { labelsConfigured });

const lockExists = fs.existsSync('webAdmin/package-lock.json');
await logDebug('H2', '.cursor/dependabot-investigate.mjs:29', 'Frontend lockfile presence', { lockExists, path: 'webAdmin/package-lock.json' });

const pkg = JSON.parse(fs.readFileSync('webAdmin/package.json', 'utf8'));
await logDebug('H5', '.cursor/dependabot-investigate.mjs:32', 'Frontend peer compatibility versions', {
  nextVersion: pkg.dependencies?.next ?? null,
  eslintVersion: pkg.devDependencies?.eslint ?? null,
  eslintConfigNextVersion: pkg.devDependencies?.['eslint-config-next'] ?? null,
});

let npmCiError = '';
try {
  execSync('npm ci --prefix webAdmin --dry-run', { stdio: 'pipe' });
} catch (err) {
  npmCiError = String(err.stderr || err.message || '').slice(0, 500);
}
await logDebug('H3', '.cursor/dependabot-investigate.mjs:38', 'Frontend CI install simulation result', {
  npmCiFailed: Boolean(npmCiError),
  npmCiErrorSnippet: npmCiError,
});

let ghLabelError = '';
try {
  execSync('gh label list', { stdio: 'pipe' });
} catch (err) {
  ghLabelError = String(err.stderr || err.message || '').slice(0, 500);
}
await logDebug('H4', '.cursor/dependabot-investigate.mjs:49', 'GitHub label API accessibility for verification', {
  ghLabelError: ghLabelError || null,
});

console.log('Dependabot investigation logs emitted');
