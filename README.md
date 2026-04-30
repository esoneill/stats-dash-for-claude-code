# CCode Dashboard Plugin

A Claude Code statusline dashboard that renders an emoji-rich single-line status bar with real-time session metrics and external data.

```
📁 ~/proj │ 🧠 42% │ 💰 $0.23 │ ⏱ 12m │ 🤖 Opus │ ☀️ 72°F │ 📝 +123/-45 │ ⚡ 5h:6%(3h12m) 7d:35%
```

## Prerequisites

- macOS or Linux
- Python 3.6+
- Claude Code CLI

## Install

```bash
bash install.sh
```

This copies the script to `~/.claude/statusline/`, installs the `/statusline` slash command into `~/.claude/commands/`, and adds the `statusLine` key to your Claude Code settings.

## Segments

| Name | Example | Source |
|------|---------|--------|
| `cwd` | `📁 ~/proj` | Session JSON — `workspace.project_dir` (falls back to `cwd`), tilde-shortened |
| `context` | `🧠 42%` | Session JSON — color-coded green/yellow/red |
| `cost` | `💰 $0.23` | Session JSON |
| `time` | `⏱ 12m` | Session JSON — auto-formats s/m/h |
| `model` | `🤖 Opus` | Session JSON — extracts family name |
| `weather` | `☀️ 72°F` | [Open-Meteo API](https://open-meteo.com/) — cached 30 min |
| `diff` | `📝 +123/-45` | Session JSON — green adds, red removes |
| `ratelimit` | `⚡ 5h:6%(3h12m) 7d:35%` | Anthropic OAuth API — cached 5 min, with reset countdown |

Segments that fail to load are silently omitted.

## Toggling segments

Turn individual segments on or off — useful for trimming the bar or skipping the network-backed segments (`weather`, `ratelimit`).

**From inside Claude Code (slash command):**

```
/statusline                       # list current state
/statusline disable weather       # hide a segment
/statusline disable ratelimit
/statusline enable weather        # show it again
/statusline toggle diff           # flip whichever it is
/statusline reset                 # clear all overrides (everything on)
```

**From your shell (CLI):**

```bash
python3 ~/.claude/statusline/statusline.py config list
python3 ~/.claude/statusline/statusline.py config disable weather
python3 ~/.claude/statusline/statusline.py config enable weather
python3 ~/.claude/statusline/statusline.py config toggle ratelimit
python3 ~/.claude/statusline/statusline.py config reset
```

Both write to `~/.claude/statusline/config.json`. The schema is overrides-only — segments not listed in `disabled` stay enabled, so newly added segments default on.

```json
{ "disabled": ["weather", "ratelimit"] }
```

Changes take effect on the next render (next keystroke pause).

## Privacy

- **Rate limits**: The rate limit segment reads your Claude Code OAuth credentials to query the Anthropic usage API. On macOS these are read from the Keychain via the `security` CLI, with a fallback to `~/.claude/.credentials.json` if Keychain access fails. On Linux they are read from `~/.claude/.credentials.json` (where Claude Code stores them as plaintext JSON). No credentials are logged or transmitted elsewhere.
- **Weather**: The weather segment uses IP-based geolocation (via [ip-api.com](http://ip-api.com)) to determine your approximate location for weather data from [Open-Meteo](https://open-meteo.com/). Location coordinates are cached locally in `/tmp/ccode-dashboard/`.

## Customization

Edit `~/.claude/statusline/statusline.py` to customize:

- **Temperature units**: Change `&temperature_unit=fahrenheit` to `celsius` in the Open-Meteo URL
- **Colors**: Modify the `green()`, `yellow()`, `red()` ANSI helpers
- **Thresholds**: Adjust the `>= 80` / `>= 50` breakpoints in `segment_context` and rate limit coloring

## Uninstall

Remove the `statusLine` key from `~/.claude/settings.json`, delete `~/.claude/commands/statusline.md`, then optionally delete `~/.claude/statusline/`.

## License

This project is licensed under the GNU General Public License v3.0 — see the [LICENSE](LICENSE) file for details.
