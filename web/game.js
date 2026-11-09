const canvas = document.querySelector('#canvas');
const frame = document.querySelector('.frame');
const fullscreenButton = document.querySelector('#fullscreen');

function requestMouseCapture() {
  if (document.pointerLockElement === canvas || !canvas.requestPointerLock) return;
  const request = canvas.requestPointerLock();
  if (request && typeof request.catch === 'function') request.catch(() => {});
}

canvas.addEventListener('pointerdown', requestMouseCapture);
fullscreenButton.addEventListener('click', () => {
  requestMouseCapture();
  if (document.fullscreenElement) {
    document.exitFullscreen().catch(() => {});
  } else {
    frame.requestFullscreen().catch(() => {});
  }
});
document.addEventListener('pointerlockchange', () => {
  document.querySelector('#wasm-status').textContent =
    document.pointerLockElement === canvas ? 'MOUSE PRESO' : 'DOOM';
});
document.addEventListener('fullscreenchange', () => {
  fullscreenButton.textContent = document.fullscreenElement ? 'SAIR DA TELA CHEIA' : 'TELA CHEIA';
});

window.Module = {
  canvas,
  noInitialRun: true,
  arguments: ['-warp', '1', '-skill', '3', '-iwad', '/freedoom1.wad', '-nogui', '-nomusic',
    '-config', '/doombrowser.cfg'],
  locateFile: path => `/doom/${path}`,
  print: text => console.log(text),
  printErr(text) {
    console.error(text);
    const message = document.querySelector('#loading span');
    if (message) message.textContent = text;
  },
  onRuntimeInitialized() {
    try {
      callMain(window.Module.arguments);
      document.querySelector('#loading').hidden = true;
      document.querySelector('#wasm-status').textContent = 'DOOM';
    } catch (error) {
      document.querySelector('#loading span').textContent = `Falha ao iniciar: ${error}`;
    }
  },
  onAbort(reason) {
    document.querySelector('#loading').hidden = false;
    document.querySelector('#loading h1').textContent = 'Falha ao iniciar Doom';
    document.querySelector('#loading span').textContent = String(reason);
  },
};
