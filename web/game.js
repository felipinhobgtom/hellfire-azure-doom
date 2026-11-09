function escapeHtml(value) {
  return value.replace(/[&<>"']/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  })[char]);
}

async function refreshScores() {
  try {
    const response = await fetch('/api/scores');
    const scores = await response.json();
    document.querySelector('#scores').innerHTML = scores.length
      ? scores.map((score, index) => `<div class="row"><span>${String(index + 1).padStart(2, '0')}</span><span>${escapeHtml(score.player)}</span><strong>${score.kills}</strong></div>`).join('')
      : '<div class="empty">Ainda não há recordes. Seja o primeiro.</div>';
    document.querySelector('#status').textContent = '● API ONLINE';
  } catch {
    document.querySelector('#status').textContent = '● API OFFLINE';
  }
}

window.Module = {
  canvas: document.querySelector('#canvas'),
  noInitialRun: true,
  arguments: ['-warp', '1', '-skill', '3', '-iwad', '/freedoom1.wad', '-window', '-nogui', '-nomusic',
    '-config', '/doombrowser.cfg', '-nograbmouse'],
  locateFile: path => `/doom/${path}`,
  print: text => console.log(text),
  printErr(text) {
    console.error(text);
    if (!document.querySelector('#loading').hidden) document.querySelector('#loading p').textContent = text;
  },
  onRuntimeInitialized() {
    try {
      callMain(window.Module.arguments);
      document.querySelector('#loading').hidden = true;
      document.querySelector('#wasm-status').textContent = '● CHOCOLATE DOOM WASM';
    } catch (error) {
      document.querySelector('#loading p').textContent = `Falha ao iniciar o jogo: ${error}`;
    }
  },
  onAbort(reason) {
    document.querySelector('#loading').hidden = false;
    document.querySelector('#loading h2').textContent = 'FALHA AO INICIAR';
    document.querySelector('#loading p').textContent = String(reason);
  },
};
window.addEventListener('error', event => {
  if (!document.querySelector('#loading').hidden) document.querySelector('#loading p').textContent = event.message;
});

refreshScores();
setInterval(refreshScores, 15000);
