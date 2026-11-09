#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE="$ROOT/vendor/chocolate-doom"
BUILD="$ROOT/build/wasm"
WAD="$ROOT/web/assets/freedoom1.wad"
CONFIG="$ROOT/web/assets/doombrowser.cfg"
if [[ ! -f "$SOURCE/CMakeLists.txt" ]]; then
  echo 'Submódulo ausente; clone com: git clone --recurse-submodules ...' >&2
  exit 1
fi
if ! command -v emcmake >/dev/null || ! command -v cmake >/dev/null; then
  echo 'Toolchain ausente. Use nix develop (ou instale Emscripten, CMake e GNU Make).' >&2
  exit 1
fi
mkdir -p "$ROOT/web/doom"
emcmake cmake -S "$SOURCE" -B "$BUILD" \
  -DCMAKE_BUILD_TYPE=Release \
  -DENABLE_SDL2_MIXER=OFF \
  -DENABLE_SDL2_NET=OFF \
-DCMAKE_EXE_LINKER_FLAGS="--preload-file $WAD@/freedoom1.wad --preload-file $CONFIG@/doombrowser.cfg"
cmake --build "$BUILD" --target chocolate-doom --parallel "${BUILD_JOBS:-2}"
for ext in js wasm data; do
  file="$BUILD/src/chocolate-doom.$ext"
  [[ -f "$file" ]] || { echo "Saída ausente: $file" >&2; exit 1; }
  cp "$file" "$ROOT/web/doom/"
done
printf 'Artefatos WebAssembly publicados em web/doom/\n'
