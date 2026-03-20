#!/usr/bin/env python3
"""Claude Code statusline dashboard — emoji-rich single-line status bar."""

import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# ── Constants ───────────────────────────────────────────────────────────────

CACHE_DIR = Path("/tmp/ccode-dashboard")
WEATHER_TTL = 1800    # 30 minutes
LOCATION_TTL = 1800   # 30 minutes
RATELIMIT_TTL = 300  # 5 minutes
SEP = " \u2502 "     # │

# Mimics the Claude Code client UA — the Anthropic usage API may require this.
# Update to match your installed Claude Code version if needed.
CLAUDE_CODE_UA = "claude-code/2.0.31"

# ── ANSI color helpers ──────────────────────────────────────────────────────

def green(s):  return f"\033[32m{s}\033[0m"
def yellow(s): return f"\033[33m{s}\033[0m"
def red(s):    return f"\033[31m{s}\033[0m"
def dim(s):    return f"\033[2m{s}\033[0m"

# ── Cache helpers ───────────────────────────────────────────────────────────

def read_cache(path, ttl):
    try:
        p = CACHE_DIR / path
        if p.exists() and (time.time() - p.stat().st_mtime) < ttl:
            return p.read_text().strip()
    except Exception:
        pass
    return None

def write_cache(path, content):
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        (CACHE_DIR / path).write_text(content)
    except Exception:
        pass

# ── Segment functions ───────────────────────────────────────────────────────

def segment_context(data):
    pct = data["context_window"]["used_percentage"]
    label = f"\U0001f9e0 {pct:.0f}%"
    if pct >= 80:
        return red(label)
    elif pct >= 50:
        return yellow(label)
    return green(label)

def segment_cost(data):
    cost = data["cost"]["total_cost_usd"]
    return f"\U0001f4b0 ${cost:.2f}"

def segment_time(data):
    ms = data["cost"]["total_duration_ms"]
    total_sec = int(ms / 1000)
    if total_sec < 60:
        human = f"{total_sec}s"
    elif total_sec < 3600:
        human = f"{total_sec // 60}m"
    else:
        h = total_sec // 3600
        m = (total_sec % 3600) // 60
        human = f"{h}h{m}m" if m else f"{h}h"
    return f"\u23f1 {human}"

def segment_model(data):
    display = data["model"]["display_name"]
    # Extract the family name (first word, e.g. "Opus" from "Opus 4.6 (1M context)")
    family = display.split()[0] if display else "?"
    return f"\U0001f916 {family}"

WMO_WEATHER_CODES = {
    0: ("☀️", "Clear"),
    1: ("⛅", "Mostly clear"),
    2: ("⛅", "Partly cloudy"),
    3: ("☁️", "Overcast"),
    45: ("🌫️", "Fog"),
    48: ("🌫️", "Rime fog"),
    51: ("🌧️", "Light drizzle"),
    53: ("🌧️", "Drizzle"),
    55: ("🌧️", "Heavy drizzle"),
    56: ("🌧️", "Freezing drizzle"),
    57: ("🌧️", "Heavy freezing drizzle"),
    61: ("🌧️", "Light rain"),
    63: ("🌧️", "Rain"),
    65: ("🌧️", "Heavy rain"),
    66: ("🌧️", "Freezing rain"),
    67: ("🌧️", "Heavy freezing rain"),
    71: ("❄️", "Light snow"),
    73: ("❄️", "Snow"),
    75: ("❄️", "Heavy snow"),
    77: ("❄️", "Snow grains"),
    80: ("🌧️", "Light showers"),
    81: ("🌧️", "Showers"),
    82: ("🌧️", "Heavy showers"),
    85: ("❄️", "Light snow showers"),
    86: ("❄️", "Heavy snow showers"),
    95: ("⚡", "Thunderstorm"),
    96: ("⚡", "Thunderstorm w/ hail"),
    99: ("⚡", "Heavy thunderstorm w/ hail"),
}

def _get_location():
    cached = read_cache("location", LOCATION_TTL)
    if cached:
        parts = cached.split(",")
        return float(parts[0]), float(parts[1])
    req = urllib.request.Request(
        "http://ip-api.com/json/?fields=lat,lon",
        headers={"User-Agent": "ccode-dashboard/0.1"},
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode())
    lat, lon = data["lat"], data["lon"]
    write_cache("location", f"{lat},{lon}")
    return lat, lon

def segment_weather():
    cached = read_cache("weather", WEATHER_TTL)
    if cached:
        return cached

    try:
        lat, lon = _get_location()
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,weather_code"
            f"&temperature_unit=fahrenheit"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "ccode-dashboard/0.1"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
        current = data["current"]
        temp = current["temperature_2m"]
        code = current["weather_code"]
        icon, condition = WMO_WEATHER_CODES.get(code, ("🌡️", "Unknown"))
        segment = f"{icon} {temp:.0f}°F"
        write_cache("weather", segment)
        return segment
    except Exception:
        return "🌡️ --"

def segment_diff(data):
    added = data["cost"]["total_lines_added"]
    removed = data["cost"]["total_lines_removed"]
    return f"\U0001f4dd {green(f'+{added}')}/{red(f'-{removed}')}"

def _format_countdown(resets_at_str):
    """Parse an ISO 8601 timestamp and return a compact countdown like '2h13m'."""
    if not resets_at_str:
        return None
    try:
        resets_at = datetime.fromisoformat(resets_at_str.replace("Z", "+00:00"))
        delta = resets_at - datetime.now(timezone.utc)
        total_seconds = int(delta.total_seconds())
        if total_seconds <= 0:
            return None
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        if days > 0:
            return f"{days}d{hours}h" if hours else f"{days}d"
        if hours > 0:
            return f"{hours}h{minutes}m" if minutes else f"{hours}h"
        return f"{minutes}m"
    except Exception:
        return None

def segment_ratelimit():
    cached = read_cache("ratelimit", RATELIMIT_TTL)
    if cached:
        return cached

    try:
        # Get OAuth token from macOS Keychain
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "Claude Code-credentials", "-w"],
            capture_output=True, text=True, timeout=3,
        )
        if result.returncode != 0:
            return None

        creds = json.loads(result.stdout.strip())
        token = creds.get("claudeAiOauth", {}).get("accessToken")
        if not token:
            return None

        req = urllib.request.Request(
            "https://api.anthropic.com/api/oauth/usage",
            headers={
                "Authorization": f"Bearer {token}",
                "anthropic-beta": "oauth-2025-04-20",
                "User-Agent": CLAUDE_CODE_UA,
            },
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            usage = json.loads(resp.read().decode())

        five_h = usage.get("five_hour", {}).get("utilization", 0)
        seven_d = usage.get("seven_day", {}).get("utilization", 0)
        five_h_resets = usage.get("five_hour", {}).get("resets_at")
        seven_d_resets = usage.get("seven_day", {}).get("resets_at")

        def color_pct(v):
            s = f"{v:.0f}%" if isinstance(v, float) else f"{v}%"
            if v >= 80:
                return red(s)
            elif v >= 50:
                return yellow(s)
            return green(s)

        def fmt_window(label, pct, resets_at_str):
            base = f"{label}:{color_pct(pct)}"
            countdown = _format_countdown(resets_at_str)
            if countdown and pct > 0:
                return f"{base}({countdown})"
            return base

        segment = f"\u26a1 {fmt_window('5h', five_h, five_h_resets)} {fmt_window('7d', seven_d, seven_d_resets)}"
        # Cache a plain version (ANSI codes included)
        write_cache("ratelimit", segment)
        return segment
    except Exception:
        return None

# ── Main ────────────────────────────────────────────────────────────────────

def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    segments = []

    # JSON-backed segments (require data)
    for fn in [segment_context, segment_cost, segment_time, segment_model]:
        try:
            result = fn(data)
            if result is not None:
                segments.append(result)
        except Exception:
            pass

    # External segments (no data dependency)
    try:
        w = segment_weather()
        if w:
            segments.append(w)
    except Exception:
        pass

    # Diff segment (requires data)
    try:
        d = segment_diff(data)
        if d:
            segments.append(d)
    except Exception:
        pass

    # Rate limit segment (external)
    try:
        r = segment_ratelimit()
        if r:
            segments.append(r)
    except Exception:
        pass

    if segments:
        print(SEP.join(segments))
    else:
        print(dim("\U0001f9e0 --") + SEP + dim("\u23f1 --"))


if __name__ == "__main__":
    main()
