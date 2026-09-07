#!/bin/sh
set -eu
NARRATION_HOME="${NARRATION_HOME:-/Volumes/SP Extreme SSD/GyanSutraAudio}"
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ ! -d "$(dirname -- "$NARRATION_HOME")" ]; then
  echo 'Connect the SSD or set NARRATION_HOME to a location on your disk.' >&2
  exit 1
fi
if [ "$(uname -m)" != arm64 ]; then
  echo 'This setup requires an Apple Silicon Mac and an ARM Python interpreter.' >&2
  exit 1
fi
python3 -m venv "$NARRATION_HOME/.venv"
"$NARRATION_HOME/.venv/bin/python" -m pip install --cache-dir "$NARRATION_HOME/pip-cache" -r "$SCRIPT_DIR/requirements-mac.lock"
echo "Voice software installed at $NARRATION_HOME. Run run-mac.sh to generate audio."
