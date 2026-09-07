#!/bin/sh
set -eu
NARRATION_HOME="${NARRATION_HOME:-/Volumes/SP Extreme SSD/GyanSutraAudio}"
if [ ! -d "$NARRATION_HOME" ]; then
  echo "Connect the audio SSD, or set NARRATION_HOME to its GyanSutraAudio folder." >&2
  exit 1
fi
export HF_HOME="$NARRATION_HOME/huggingface"
export HF_HUB_DISABLE_TELEMETRY=1
export HF_HUB_DISABLE_XET=1
export HF_HUB_DOWNLOAD_TIMEOUT=60
export TOKENIZERS_PARALLELISM=false
export NARRATION_HOME
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ "${1:-}" = '--download' ]; then
  shift
  exec "$NARRATION_HOME/.venv/bin/python" "$SCRIPT_DIR/download_model.py" "$@"
fi
exec "$NARRATION_HOME/.venv/bin/python" "$SCRIPT_DIR/generate_mac.py" "$@"
