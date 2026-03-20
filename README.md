# CCode Dashboard Plugin

A Claude Code statusline dashboard that renders an emoji-rich single-line status bar with real-time session metrics and external data.

```
🧠 42% │ 💰 $0.23 │ ⏱ 12m │ 🤖 Opus │ ☀️ 72°F │ 📝 +123/-45 │ ⚡ 5h:6%(3h12m) 7d:35%
```

## Prerequisites

- macOS
- Python 3.6+
- Claude Code CLI

## Install

```bash
bash install.sh
```

This copies the script to `~/.claude/statusline/` and adds the `statusLine` key to your Claude Code settings.

## Segments

| Segment | Example | Source |
|---------|---------|--------|
| Context window | `🧠 42%` | Session JSON — color-coded green/yellow/red |
| Cost | `💰 $0.23` | Session JSON |
| Duration | `⏱ 12m` | Session JSON — auto-formats s/m/h |
| Model | `🤖 Opus` | Session JSON — extracts family name |
| Weather | `☀️ 72°F` | [Open-Meteo API](https://open-meteo.com/) — cached 30 min |
| Lines changed | `📝 +123/-45` | Session JSON — green adds, red removes |
| Rate limits | `⚡ 5h:6%(3h12m) 7d:35%` | Anthropic OAuth API — cached 5 min, with reset countdown |

Segments that fail to load are silently omitted.

## Privacy

- **Rate limits**: The rate limit segment reads your Claude Code OAuth credentials from the macOS Keychain to query the Anthropic usage API. No credentials are logged or transmitted elsewhere.
- **Weather**: The weather segment uses IP-based geolocation (via [ip-api.com](http://ip-api.com)) to determine your approximate location for weather data from [Open-Meteo](https://open-meteo.com/). Location coordinates are cached locally in `/tmp/ccode-dashboard/`.

## Customization

Edit `~/.claude/statusline/statusline.py` to customize:

- **Temperature units**: Change `&temperature_unit=fahrenheit` to `celsius` in the Open-Meteo URL
- **Colors**: Modify the `green()`, `yellow()`, `red()` ANSI helpers
- **Thresholds**: Adjust the `>= 80` / `>= 50` breakpoints in `segment_context` and rate limit coloring

## Uninstall

Remove the `statusLine` key from `~/.claude/settings.json`, then optionally delete `~/.claude/statusline/`.

## License

This project is licensed under the GNU General Public License v3.0 — see the [LICENSE](LICENSE) file for details.
