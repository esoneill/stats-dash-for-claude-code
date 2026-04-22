#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_DIR="$HOME/.claude/statusline"
DEST_FILE="$DEST_DIR/statusline.py"
SETTINGS="$HOME/.claude/settings.json"

echo "Installing CCode Dashboard Plugin..."

# 1. Copy statusline.py
mkdir -p "$DEST_DIR"
cp "$SCRIPT_DIR/statusline.py" "$DEST_FILE"
chmod +x "$DEST_FILE"
echo "  Copied statusline.py -> $DEST_FILE"

# 2. Clear format-sensitive caches so updated formats take effect immediately
rm -f /tmp/ccode-dashboard/weather /tmp/ccode-dashboard/ratelimit 2>/dev/null || true
echo "  Cleared statusline caches"

# 3. Merge statusLine.command into settings.json
python3 -c "
import json, pathlib, sys

settings_path = pathlib.Path('$SETTINGS')
if settings_path.exists():
    settings = json.loads(settings_path.read_text())
else:
    settings = {}

settings['statusLine'] = {
    'type': 'command',
    'command': 'python3 $DEST_FILE'
}

settings_path.write_text(json.dumps(settings, indent=2) + '\n')
print('  Updated', settings_path)
"

echo ""
echo "Done! Restart Claude Code to see your dashboard statusline."
echo "Format: brain% | cost | time | model | weather | diff | rate-limits"
