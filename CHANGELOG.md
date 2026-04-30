# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.1] - 2026-04-30

### Changed

- `📁` cwd segment now caps display at the last 3 path components, prefixing with `…` when truncated (e.g. `~/code/work/2026/q2/big-project` → `~/…/2026/q2/big-project`). Anchors (`~`, `/`) are preserved. Paths already ≤ 3 components are unchanged.

## [1.0.0] - 2026-04-30

### Added

- Working-directory segment (`📁`) showing the project folder Claude was opened in, tilde-shortened (e.g. `📁 ~/Documents/Rando Projects/CCode Dashboard Plugin`). Reads `workspace.project_dir` from the statusline JSON, falling back to `cwd` for older Claude Code clients. Rendered as the leftmost segment.
- Per-segment on/off toggle. Each segment now has a stable name (`cwd`, `context`, `cost`, `time`, `model`, `weather`, `diff`, `ratelimit`) and can be individually disabled.
  - `/statusline` slash command (installed to `~/.claude/commands/`) with `list`, `enable <name>`, `disable <name>`, `toggle <name>`, and `reset` subcommands.
  - Equivalent CLI: `python3 ~/.claude/statusline/statusline.py config <subcommand>`.
  - State persisted at `~/.claude/statusline/config.json` using an overrides-only schema (`{"disabled": [...]}`), so future segments default to enabled.

### Changed

- Refactored render loop in `main()` to iterate a single `SEGMENT_REGISTRY`, replacing four separate try/except blocks with one. Render order is now defined by registry list order.

### Fixed

- Installer no longer aborts under `set -e` when `commands/` exists but contains no `.md` files; the slash-command copy step is now guarded by a glob match check.
- Installer's final format hint now mentions the new `cwd` segment.

## [0.1.2] - 2026-04-22

### Fixed

- Installer now writes the required `type: "command"` field in `settings.json`, fixing "Invalid settings: statusLine" schema errors on fresh installs (previously severe enough to block Claude Code from loading)
- Rate limit segment now works on Linux by reading `~/.claude/.credentials.json` when the macOS `security` CLI is unavailable; added macOS fallback to the same path when Keychain access fails

### Changed

- Bumped plugin User-Agent to `ccode-dashboard/0.1.2` (used for weather and geolocation requests)

## [0.1.1] - 2026-03-20

### Changed

- Switched weather provider from wttr.in to Open-Meteo API (free, no API key, more reliable)
- Added IP-based geolocation via ip-api.com with 30-minute cache
- Weather segment now shows WMO weather code description and temperature in °F
- Increased weather fetch timeout from 2s to 5s
- Weather failures now show `🌡️ --` fallback instead of silently disappearing
- Shortened weather segment to emoji + temperature only (removed redundant condition text)
- Rate limit segment now shows reset countdowns in parentheses, e.g. `5h:42%(2h13m)`

### Added

- `_format_countdown()` helper for compact ISO 8601 → countdown formatting
- "Skills used in session" tracking via hooks (future feature)

### Fixed

- Installer now clears format-sensitive caches (weather, ratelimit) on update to prevent stale data

## [0.1.0] - 2026-03-18

### Added

- Context window usage segment with ANSI color thresholds (green <50%, yellow <80%, red >=80%)
- Session cost tracking segment
- Session duration segment with human-readable formatting
- Model name segment extracted from display name
- Weather segment via wttr.in with 30-minute cache
- Lines changed segment with green/red diff coloring
- Rate limit utilization segment (5h and 7d) via Anthropic OAuth API
- `install.sh` auto-installer for Claude Code statusline integration
