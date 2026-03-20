# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
