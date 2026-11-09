window.Module = {
  canvas: document.querySelector('#canvas'),
  noInitialRun: true,
  arguments: ['-warp', '1', '-skill', '3', '-iwad', '/freedoom1.wad', '-window', '-nogui', '-nomusic',
    '-config', '/doombrowser.cfg', '-nograbmouse'],
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
