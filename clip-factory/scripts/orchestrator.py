#!/usr/bin/env python3
"""
Clip Factory Orchestrator — Async Multi-Agent Pipeline Controller

Manages parallel niche subagents, monitors their progress, aggregates results,
and enforces statistics output. Designed to be called by the orchestrator agent
or cron jobs on a MuleRun compute instance.

Usage:
    python3 orchestrator.py dispatch --config ~/.clip-factory/config.json
    python3 orchestrator.py poll --run-id <run_id>
    python3 orchestrator.py report --run-id <run_id>
    python3 orchestrator.py decide --config ~/.clip-factory/config.json
    python3 orchestrator.py health
"""

import json
import os
import sys
import subprocess
import uuid
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────

BASE_DIR = Path.home() / ".clip-factory"
CONFIG_PATH = BASE_DIR / "config.json"
STATE_PATH = BASE_DIR / "state.json"
ANALYTICS_DIR = BASE_DIR / "analytics"
CLIPS_LOG = ANALYTICS_DIR / "clips.jsonl"
RUN_STATS_LOG = ANALYTICS_DIR / "run_stats.jsonl"
MCP_HEALTH_LOG = ANALYTICS_DIR / "mcp_health.jsonl"
QUEUE_PATH = BASE_DIR / "queue.jsonl"
REPORTS_DIR = BASE_DIR / "reports"

def ensure_dirs():
    for d in [ANALYTICS_DIR, REPORTS_DIR / "daily", REPORTS_DIR / "weekly", REPORTS_DIR / "monthly", BASE_DIR / "logs"]:
        d.mkdir(parents=True, exist_ok=True)

def load_json(path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)

def append_jsonl(path, record):
    with open(path, "a") as f:
        f.write(json.dumps(record, default=str) + "\n")

def load_jsonl(path, max_lines=None):
    records = []
    if not path.exists():
        return records
    with open(path) as f:
        for i, line in enumerate(f):
            if max_lines and i >= max_lines:
                break
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records

def run_cli(args, timeout=120):
    """Run a mulerun CLI command and return parsed output."""
    cmd = ["mulerun"] + args + ["-o", "json"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout.strip())
        return {"error": result.stderr.strip(), "code": result.returncode}
    except subprocess.TimeoutExpired:
        return {"error": "timeout", "code": -1}
    except json.JSONDecodeError:
        return {"raw": result.stdout.strip(), "code": result.returncode}

# ─── Dispatch: Spawn parallel niche subagents ─────────────────────────────────

def build_niche_prompt(niche, config):
    """Build the prompt for a niche-scoped subagent."""
    creators = ", ".join(niche.get("creators", []))
    accounts = "; ".join(
        f'{a["handle"]}@{a["platform"]}' for a in niche.get("accounts", [])
    )
    clips_per_day = niche.get("clips_per_day", 5)
    schedule = ", ".join(config.get("posting_schedule", {}).get("slots_cdt", []))
    tz = config.get("timezone", "America/Chicago")

    return f"""You are a niche clipping agent for: {niche['name']}

SCOPE:
- Creators: {creators}
- Accounts: {accounts}
- Cadence: {clips_per_day} clips/day
- Schedule: {schedule} ({tz})

EXECUTE THIS PIPELINE:
1. SCAN: Check each creator for new uploads since last scan. Use Firecrawl or YouTube MCP to discover latest videos.
2. CLIP: For each new video, call Vugola clip_video. Request {clips_per_day} best moments. Poll get_clip_status until complete. Download clips.
3. CAPTION: Ensure all clips have captions (Vugola handles this). Verify caption quality.
4. SCHEDULE: For each clip, call Postiz posts:create. Distribute across accounts and platforms. Space posts across time slots.
5. LOG: For each clip, output a JSON record with fields: clip_id, source_video, niche, creator, account, platform, posted_at, duration_seconds, hook_style, status.

OUTPUT FORMAT (mandatory):
Return a JSON object:
{{
  "niche": "{niche['name']}",
  "source_videos_scanned": <int>,
  "new_videos_found": <int>,
  "clips_extracted": <int>,
  "clips_captioned": <int>,
  "clips_scheduled": <int>,
  "clips_posted": <int>,
  "clips_failed": <int>,
  "failures": [{{ "clip_id": "...", "reason": "..." }}],
  "distribution": {{ "tiktok": <int>, "youtube": <int>, "instagram": <int>, "x": <int> }},
  "clip_records": [<clip JSON records>],
  "errors": [<any errors encountered>]
}}

Do NOT output anything except this JSON object. No commentary, no markdown."""

def dispatch(config_path=None):
    """Spawn one subagent per active niche, return run manifest."""
    ensure_dirs()
    config = load_json(config_path or CONFIG_PATH)
    niches = [n for n in config.get("niches", []) if n.get("status") == "active"]

    if not niches:
        print(json.dumps({"error": "No active niches found"}))
        return

    run_id = str(uuid.uuid4())[:8]
    run_manifest = {
        "run_id": run_id,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "niches": [],
        "status": "dispatching"
    }

    for niche in niches:
        prompt = build_niche_prompt(niche, config)
        result = run_cli([
            "session", "run",
            "--name", f"clip-{niche['name']}-{run_id}",
            "--prompt", prompt,
            "--wait=false"
        ], timeout=30)

        session_id = result.get("id") or result.get("session_id") or result.get("raw", "")
        run_manifest["niches"].append({
            "niche": niche["name"],
            "session_id": str(session_id),
            "status": "running" if not result.get("error") else "failed",
            "error": result.get("error")
        })

    run_manifest["status"] = "running"
    # Save run manifest
    state = load_json(STATE_PATH)
    state.setdefault("runs", {})[run_id] = run_manifest
    save_json(STATE_PATH, state)

    print(json.dumps(run_manifest, indent=2))
    return run_manifest

# ─── Poll: Check all subagents for completion ─────────────────────────────────

def poll(run_id):
    """Poll all subagents in a run, collect results when done."""
    state = load_json(STATE_PATH)
    run = state.get("runs", {}).get(run_id)
    if not run:
        print(json.dumps({"error": f"Run {run_id} not found"}))
        return

    all_done = True
    for niche_entry in run["niches"]:
        if niche_entry["status"] in ("completed", "failed"):
            continue

        sid = niche_entry["session_id"]
        result = run_cli(["session", "get", sid], timeout=15)
        status = result.get("status", "unknown")

        if status in ("completed", "finished", "done"):
            niche_entry["status"] = "completed"
            niche_entry["result"] = result.get("output") or result.get("response") or result
            niche_entry["completed_at"] = datetime.now(timezone.utc).isoformat()
        elif status in ("failed", "error", "cancelled"):
            niche_entry["status"] = "failed"
            niche_entry["error"] = result.get("error") or str(result)
        else:
            all_done = False
            niche_entry["status"] = "running"

    if all_done:
        run["status"] = "completed"
        run["completed_at"] = datetime.now(timezone.utc).isoformat()

        # Aggregate clip records
        _aggregate_results(run)

    save_json(STATE_PATH, state)
    print(json.dumps(run, indent=2))
    return run

def _aggregate_results(run):
    """Parse subagent outputs and append clip records to analytics."""
    totals = {
        "source_videos_scanned": 0, "new_videos_found": 0,
        "clips_extracted": 0, "clips_captioned": 0,
        "clips_scheduled": 0, "clips_posted": 0, "clips_failed": 0,
        "distribution": {}, "errors": []
    }

    for niche_entry in run["niches"]:
        result = niche_entry.get("result")
        if not result:
            continue

        # Try to parse if it's a string
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                continue

        for key in ["source_videos_scanned", "new_videos_found", "clips_extracted",
                     "clips_captioned", "clips_scheduled", "clips_posted", "clips_failed"]:
            totals[key] += result.get(key, 0)

        for platform, count in result.get("distribution", {}).items():
            totals["distribution"][platform] = totals["distribution"].get(platform, 0) + count

        totals["errors"].extend(result.get("errors", []))

        # Append individual clip records
        for clip in result.get("clip_records", []):
            clip["run_id"] = run["run_id"]
            clip["aggregated_at"] = datetime.now(timezone.utc).isoformat()
            append_jsonl(CLIPS_LOG, clip)

    run["totals"] = totals

# ─── Report: Generate statistics block ────────────────────────────────────────

def generate_run_report(run_id):
    """Generate the mandatory per-run statistics block."""
    state = load_json(STATE_PATH)
    run = state.get("runs", {}).get(run_id)
    if not run:
        return {"error": f"Run {run_id} not found"}

    totals = run.get("totals", {})
    dist = totals.get("distribution", {})
    started = run.get("started_at", "")
    completed = run.get("completed_at", "")

    # Calculate duration
    duration_str = "[pending]"
    if started and completed:
        try:
            s = datetime.fromisoformat(started)
            e = datetime.fromisoformat(completed)
            delta = e - s
            mins = int(delta.total_seconds() // 60)
            secs = int(delta.total_seconds() % 60)
            duration_str = f"{mins}m {secs}s"
        except Exception:
            pass

    errors = totals.get("errors", [])
    error_summary = "; ".join(str(e) for e in errors[:5]) if errors else "None"

    report = f"""═══════════════════════════════════════════
 CLIP FACTORY RUN REPORT
═══════════════════════════════════════════
 Run ID:          {run_id}
 Timestamp:       {started}
 Duration:        {duration_str}
 Status:          {run.get('status', '[pending]')}
 Niches:          {len(run.get('niches', []))}
───────────────────────────────────────────
 PIPELINE
   Source videos scanned:    {totals.get('source_videos_scanned', '[pending]')}
   New videos found:         {totals.get('new_videos_found', '[pending]')}
   Clips extracted:          {totals.get('clips_extracted', '[pending]')}
   Clips captioned:          {totals.get('clips_captioned', '[pending]')}
   Clips scheduled:          {totals.get('clips_scheduled', '[pending]')}
   Clips posted:             {totals.get('clips_posted', '[pending]')}
   Clips failed:             {totals.get('clips_failed', '[pending]')}
───────────────────────────────────────────
 DISTRIBUTION
   TikTok:     {dist.get('tiktok', 0)} posts  │  YouTube: {dist.get('youtube', 0)} posts
   Instagram:  {dist.get('instagram', 0)} posts  │  X:       {dist.get('x', 0)} posts
   LinkedIn:   {dist.get('linkedin', 0)} posts  │  Threads: {dist.get('threads', 0)} posts
───────────────────────────────────────────
 ERRORS
   {error_summary}
═══════════════════════════════════════════"""

    # Save to run_stats.jsonl
    stat_record = {
        "run_id": run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "duration": duration_str,
        "status": run.get("status"),
        **totals
    }
    append_jsonl(RUN_STATS_LOG, stat_record)

    print(report)
    return report

# ─── Decide: Run the decision engine ──────────────────────────────────────────

def decide(config_path=None):
    """
    Evaluate SCALE / PIVOT / KILL / MAINTAIN signals for each account.
    Reads the last 7-30 days of clip data and produces decisions.
    """
    config = load_json(config_path or CONFIG_PATH)
    clips = load_jsonl(CLIPS_LOG)

    if not clips:
        print(json.dumps({"message": "No clip data yet — need at least 7 days of data"}))
        return

    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)
    fourteen_days_ago = now - timedelta(days=14)
    thirty_days_ago = now - timedelta(days=30)

    # Group clips by account
    accounts = {}
    for clip in clips:
        key = f"{clip.get('account', 'unknown')}@{clip.get('platform', 'unknown')}"
        accounts.setdefault(key, []).append(clip)

    decisions = []
    for account_key, account_clips in accounts.items():
        # Filter to time windows
        recent_7d = [c for c in account_clips if _parse_ts(c.get("posted_at")) and _parse_ts(c.get("posted_at")) > seven_days_ago]
        recent_14d = [c for c in account_clips if _parse_ts(c.get("posted_at")) and _parse_ts(c.get("posted_at")) > fourteen_days_ago]
        recent_30d = [c for c in account_clips if _parse_ts(c.get("posted_at")) and _parse_ts(c.get("posted_at")) > thirty_days_ago]

        # Calculate KPIs
        avg_views_7d = _avg([c.get("metrics", {}).get("views_24h", 0) for c in recent_7d]) if recent_7d else 0
        avg_views_30d = _avg([c.get("metrics", {}).get("views_24h", 0) for c in recent_30d]) if recent_30d else 0
        hit_rate_14d = _hit_rate(recent_14d, threshold=10000)
        revenue_7d = sum(c.get("revenue", {}).get("total", 0) for c in recent_7d)
        revenue_per_day = revenue_7d / 7 if recent_7d else 0
        clips_count_30d = len(recent_30d)

        # Determine signal
        signal = "MAINTAIN"
        reason = "No triggers fired"

        # SCALE check
        if avg_views_7d > 5000 and hit_rate_14d > 0.20 and revenue_per_day > 30:
            signal = "SCALE"
            reason = f"Avg views {avg_views_7d:.0f} >5K, hit rate {hit_rate_14d:.0%} >20%, rev ${revenue_per_day:.0f}/day >$30"
        # KILL check (most restrictive first)
        elif clips_count_30d > 0 and avg_views_30d < 500 and revenue_7d < 20:
            # Check pivot history
            state = load_json(STATE_PATH)
            pivot_count = state.get("pivot_history", {}).get(account_key, 0)
            if pivot_count >= 2:
                signal = "KILL"
                reason = f"Avg views {avg_views_30d:.0f} <500 after 30d, rev ${revenue_7d:.0f} <$20, {pivot_count} failed pivots"
            else:
                signal = "PIVOT"
                reason = f"Avg views {avg_views_7d:.0f} <1K for 7d"
        # PIVOT check
        elif avg_views_7d < 1000 and len(recent_7d) > 7:
            signal = "PIVOT"
            reason = f"Avg views {avg_views_7d:.0f} <1K for 7+ days"
        elif hit_rate_14d < 0.05 and len(recent_14d) > 14:
            signal = "PIVOT"
            reason = f"Hit rate {hit_rate_14d:.0%} <5% over 14 days"

        decisions.append({
            "account": account_key,
            "signal": signal,
            "reason": reason,
            "kpis": {
                "avg_views_7d": round(avg_views_7d),
                "avg_views_30d": round(avg_views_30d),
                "hit_rate_14d": round(hit_rate_14d, 3),
                "revenue_per_day": round(revenue_per_day, 2),
                "clips_30d": clips_count_30d
            }
        })

    output = {"timestamp": now.isoformat(), "decisions": decisions}
    print(json.dumps(output, indent=2))

    # Save decisions
    append_jsonl(ANALYTICS_DIR / "decisions.jsonl", output)
    return output

def _parse_ts(ts_str):
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except Exception:
        return None

def _avg(values):
    return sum(values) / len(values) if values else 0

def _hit_rate(clips, threshold=10000):
    if not clips:
        return 0
    hits = sum(1 for c in clips if c.get("metrics", {}).get("views_24h", 0) >= threshold)
    return hits / len(clips)

# ─── Health: Check MCP and pipeline health ────────────────────────────────────

def health_check():
    """Check MCP server connectivity and pipeline state."""
    ensure_dirs()
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mcps": {},
        "pipeline": {},
        "state": {}
    }

    # Check compute instance
    compute_result = run_cli(["computer", "list"], timeout=15)
    results["pipeline"]["compute"] = "ok" if not compute_result.get("error") else compute_result.get("error")

    # Check state files
    results["state"]["config_exists"] = CONFIG_PATH.exists()
    results["state"]["state_exists"] = STATE_PATH.exists()
    results["state"]["clips_count"] = len(load_jsonl(CLIPS_LOG))
    results["state"]["queue_size"] = len(load_jsonl(QUEUE_PATH))

    # Check active runs
    state = load_json(STATE_PATH)
    active_runs = [r for r in state.get("runs", {}).values() if r.get("status") == "running"]
    results["state"]["active_runs"] = len(active_runs)

    append_jsonl(MCP_HEALTH_LOG, results)
    print(json.dumps(results, indent=2))
    return results

# ─── Daily Report ─────────────────────────────────────────────────────────────

def daily_report():
    """Generate the mandatory daily digest."""
    ensure_dirs()
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)
    date_str = now.strftime("%Y-%m-%d")

    clips = load_jsonl(CLIPS_LOG)
    recent = [c for c in clips if _parse_ts(c.get("aggregated_at")) and _parse_ts(c.get("aggregated_at")) > yesterday]

    # Aggregate
    total_posted = len(recent)
    views = [c.get("metrics", {}).get("views_24h", 0) for c in recent]
    total_views = sum(views)
    avg_views = _avg(views) if views else 0

    # Best/worst
    sorted_clips = sorted(recent, key=lambda c: c.get("metrics", {}).get("views_24h", 0), reverse=True)
    best = sorted_clips[0] if sorted_clips else {}
    worst = sorted_clips[-1] if sorted_clips else {}

    # Revenue
    total_rev = sum(c.get("revenue", {}).get("total", 0) for c in recent)

    # Platforms
    platforms = {}
    for c in recent:
        p = c.get("platform", "unknown")
        platforms[p] = platforms.get(p, 0) + 1

    # Niches
    niches = set(c.get("niche", "unknown") for c in recent)

    report = f"""═══════════════════════════════════════════
 DAILY DIGEST — {date_str}
═══════════════════════════════════════════
 VOLUME
   Total clips posted:      {total_posted}
   Across platforms:         {len(platforms)}
   Across niches:            {len(niches)}
───────────────────────────────────────────
 PERFORMANCE (24h window)
   Total views accrued:      {total_views:,}
   Avg views/clip:           {avg_views:,.0f}
   Best clip:                {best.get('clip_id', '[none]')} — {best.get('metrics', {}).get('views_24h', 0):,} views
   Worst clip:               {worst.get('clip_id', '[none]')} — {worst.get('metrics', {}).get('views_24h', 0):,} views
───────────────────────────────────────────
 REVENUE (estimated)
   Total:                    ${total_rev:,.2f}
───────────────────────────────────────────
 DISTRIBUTION
   {chr(10).join(f'   {p}: {c} posts' for p, c in sorted(platforms.items()))}
═══════════════════════════════════════════"""

    # Save
    report_path = REPORTS_DIR / "daily" / f"{date_str}.md"
    with open(report_path, "w") as f:
        f.write(report)

    append_jsonl(RUN_STATS_LOG, {
        "type": "daily",
        "date": date_str,
        "clips_posted": total_posted,
        "total_views": total_views,
        "avg_views": round(avg_views),
        "total_revenue": round(total_rev, 2)
    })

    print(report)
    return report

# ─── CLI Entry Point ──────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: orchestrator.py <dispatch|poll|report|decide|health|daily>")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "dispatch":
        config_path = None
        if "--config" in sys.argv:
            idx = sys.argv.index("--config")
            config_path = Path(sys.argv[idx + 1])
        dispatch(config_path)
    elif cmd == "poll":
        if "--run-id" not in sys.argv:
            print("Usage: orchestrator.py poll --run-id <id>")
            sys.exit(1)
        idx = sys.argv.index("--run-id")
        poll(sys.argv[idx + 1])
    elif cmd == "report":
        if "--run-id" not in sys.argv:
            print("Usage: orchestrator.py report --run-id <id>")
            sys.exit(1)
        idx = sys.argv.index("--run-id")
        generate_run_report(sys.argv[idx + 1])
    elif cmd == "decide":
        config_path = None
        if "--config" in sys.argv:
            idx = sys.argv.index("--config")
            config_path = Path(sys.argv[idx + 1])
        decide(config_path)
    elif cmd == "health":
        health_check()
    elif cmd == "daily":
        daily_report()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
