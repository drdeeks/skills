#!/usr/bin/env python3
"""
Clip Factory Cron Setup — Deploys all scheduled tasks to MuleRun Computer

Uploads scripts to the compute instance and creates all cron jobs.
Run this once during initial setup, or again to update cron schedules.

Usage:
    python3 setup_crons.py --config ~/.clip-factory/config.json
    python3 setup_crons.py --dry-run    # Show what would be created
    python3 setup_crons.py --status     # Show current cron status
"""

import json
import sys
import subprocess
from pathlib import Path

CRON_DEFINITIONS = [
    {
        "name": "clip-factory-scan",
        "description": "Scan tracked creators for new source content",
        "schedule_type": "cron",
        "schedule_value": "0 */4 * * *",  # Every 4 hours
        "prompt": (
            "Load the clip-factory skill. Read ~/.clip-factory/config.json. "
            "For each active niche, check every tracked creator for new video uploads "
            "since the last scan timestamp in ~/.clip-factory/state.json. "
            "Use Firecrawl to scrape their channel pages, or YouTube MCP if available. "
            "For each new video found, append to ~/.clip-factory/queue.jsonl with fields: "
            "queue_id, source_url, creator, niche, queued_at, status='pending'. "
            "Update the last_scan timestamp in state.json. "
            "Output a scan summary: niches scanned, creators checked, new videos queued."
        )
    },
    {
        "name": "clip-factory-process",
        "description": "Process queued videos through Vugola for clip extraction",
        "schedule_type": "cron",
        "schedule_value": "0 */2 * * *",  # Every 2 hours
        "prompt": (
            "Load the clip-factory skill. Read ~/.clip-factory/queue.jsonl. "
            "For each item with status='pending' (max 5 at a time): "
            "1) Call Vugola clip_video with the source URL, request 5 best clips. "
            "2) Poll get_clip_status every 30s until complete (max 30 min). "
            "3) Download each clip via download_clip. "
            "4) For each clip, create a record in ~/.clip-factory/analytics/clips.jsonl with: "
            "   clip_id, source_video, niche, creator, duration_seconds, status='extracted'. "
            "5) Update queue item status to 'processed' or 'failed'. "
            "If Vugola fails, move item to ~/.clip-factory/retry_queue.jsonl with retries+1. "
            "Output: videos processed, clips extracted, failures."
        )
    },
    {
        "name": "clip-factory-post",
        "description": "Schedule and post ready clips via Postiz",
        "schedule_type": "cron",
        "schedule_value": "*/30 * * * *",  # Every 30 minutes
        "prompt": (
            "Load the clip-factory skill. Read ~/.clip-factory/config.json for posting schedule. "
            "Read ~/.clip-factory/analytics/clips.jsonl for clips with status='extracted'. "
            "For each unposted clip: "
            "1) Determine which accounts and platforms to post to (from config). "
            "2) Pick the next available time slot from the schedule. "
            "3) Call Postiz posts:create with the clip file, caption, platform, and scheduled time. "
            "4) Update the clip record: status='scheduled', posted_at, account, platform. "
            "Space posts at least 2 hours apart per platform to avoid rate limits. "
            "Output: clips scheduled, distribution by platform."
        )
    },
    {
        "name": "clip-factory-metrics",
        "description": "Pull view/engagement metrics from all platforms",
        "schedule_type": "cron",
        "schedule_value": "0 */6 * * *",  # Every 6 hours
        "prompt": (
            "Load the clip-factory skill. Read ~/.clip-factory/analytics/clips.jsonl. "
            "For each clip posted in the last 7 days: "
            "1) Use Postiz analytics:get or scrape the platform to pull current metrics. "
            "2) Update the clip record with: views_1h, views_6h, views_24h, views_48h, views_7d, "
            "   likes, comments, shares, saves, watch_time_avg_pct, follower_delta. "
            "3) Calculate view_velocity (views_6h/views_24h) and engagement_rate. "
            "For each account, update ~/.clip-factory/analytics/accounts.json with aggregated KPIs. "
            "Output: clips updated, avg view velocity, top performing clip."
        )
    },
    {
        "name": "clip-factory-daily-report",
        "description": "Generate daily analytics digest",
        "schedule_type": "cron",
        "schedule_value": "0 23 * * *",  # 11 PM daily
        "prompt": (
            "Load the clip-factory skill. Run the daily report workflow: "
            "1) Read all clip data from the last 24 hours. "
            "2) Generate the DAILY DIGEST statistics block (mandatory format from skill). "
            "3) Save to ~/.clip-factory/reports/daily/{date}.md "
            "4) Append structured JSON to ~/.clip-factory/analytics/run_stats.jsonl "
            "5) If html-report skill is available, generate a visual HTML report. "
            "6) If xlsx skill is available, export data to spreadsheet. "
            "The statistics block MUST include: volume, performance (views, engagement, velocity), "
            "revenue estimates, top 3 clips, signals fired, MCP health status. "
            "Output the full report."
        )
    },
    {
        "name": "clip-factory-weekly-review",
        "description": "Weekly analytics review and decision engine",
        "schedule_type": "cron",
        "schedule_value": "0 22 * * 0",  # Sunday 10 PM
        "prompt": (
            "Load the clip-factory skill. Run the weekly review workflow: "
            "1) Read all clip and account data from the last 7 days. "
            "2) For each account, evaluate SCALE/PIVOT/KILL/MAINTAIN signals using the decision engine. "
            "3) Recalculate niche composite scores. "
            "4) Check A/B test results — adopt winners if confidence >80%. "
            "5) Generate the WEEKLY REVIEW statistics block (mandatory format). "
            "6) Execute any SCALE/PIVOT/KILL actions: "
            "   SCALE: Update config to increase cadence, add account entries. "
            "   PIVOT: Update niche/hook config, reset evaluation window. "
            "   KILL: Set account status to 'killed', archive data. "
            "7) Save report to ~/.clip-factory/reports/weekly/ "
            "8) Recalculate cost tracking and ROI. "
            "Output the full report with all decisions and actions taken."
        )
    },
    {
        "name": "clip-factory-service-mail",
        "description": "Monitor AgentMail inboxes for service notifications",
        "schedule_type": "cron",
        "schedule_value": "0 */12 * * *",  # Every 12 hours
        "prompt": (
            "Load the clip-factory skill. Check all AgentMail inboxes: "
            "1) Read config for agentmail_api_key and inbox IDs. "
            "2) For each inbox, list messages received since last check. "
            "3) Parse for: billing alerts, API key rotation notices, account warnings. "
            "4) If billing failure detected: flag urgently in state.json, output warning. "
            "5) If new Content Rewards campaigns found matching active niches: log opportunity. "
            "6) If API key rotation: attempt auto-update in config.json. "
            "7) Update last_mail_check timestamp in state.json. "
            "Output: messages checked, actions taken, any alerts."
        )
    },
    {
        "name": "clip-factory-health",
        "description": "Pipeline and MCP health check",
        "schedule_type": "cron",
        "schedule_value": "0 * * * *",  # Every hour
        "prompt": (
            "Load the clip-factory skill. Run health checks: "
            "1) Send heartbeat via niche_registry.py heartbeat — updates last_heartbeat in global registry, "
            "   prunes any stale agents (>2h without heartbeat) and releases their niche claims. "
            "2) Verify Vugola API: call get_credits, record response time. "
            "3) Verify Postiz API: call integrations:list, record response time. "
            "4) Check queue sizes: pending, processing, retry. "
            "5) Check for stale items: anything in 'processing' status >2 hours → move to retry. "
            "6) Check disk usage of ~/.clip-factory/ "
            "7) Verify config.json is valid JSON. "
            "8) Append health record to ~/.clip-factory/analytics/mcp_health.jsonl "
            "If any MCP is down 3 consecutive checks, output an alert. "
            "Output: health status JSON."
        )
    },
    {
        "name": "clip-factory-retry",
        "description": "Retry failed pipeline items",
        "schedule_type": "cron",
        "schedule_value": "30 */4 * * *",  # Every 4 hours at :30
        "prompt": (
            "Load the clip-factory skill. Process retry queue: "
            "1) Read ~/.clip-factory/retry_queue.jsonl "
            "2) For each item with retries < 3: move back to queue.jsonl with status='pending'. "
            "3) For each item with retries >= 3: log as permanent failure in analytics. "
            "4) Clear retry_queue.jsonl after processing. "
            "Output: items requeued, permanently failed."
        )
    },
    {
        "name": "clip-factory-niche-discovery",
        "description": "Proactive niche discovery and catalog expansion",
        "schedule_type": "cron",
        "schedule_value": "0 20 * * 0",  # Sunday 8 PM (before weekly review at 10 PM)
        "prompt": (
            "Load the clip-factory skill. Read references/niche-discovery.md for the full workflow. "
            "Run the weekly niche discovery scan: "
            "1) SCRAPE — Use Firecrawl to scrape discovery sources: "
            "   a) TikTok trending topics and rising creators. "
            "   b) YouTube trending Shorts and viral source creators. "
            "   c) Content Rewards platforms (Whop, Clipping.net, Vyro) for new campaigns and CPM changes. "
            "   d) Reddit trending subreddits for new content verticals. "
            "   e) Top clipper pages across platforms for opportunity gaps. "
            "2) EXTRACT — For each potential niche, identify 3-5 creators, estimate content supply, "
            "   check for matching Content Rewards campaigns, estimate competition density. "
            "3) SCORE — Calculate composite niche score using the formula in niche-playbook.md. "
            "4) VALIDATE — Discard niches with composite score <2.5 or content supply <2 videos/week. "
            "   Flag niches with no monetization path as 'experimental'. "
            "   Deduplicate against existing catalog (>60% creator overlap = same niche). "
            "5) REGISTER — Use niche_registry.py discover-add to add validated niches to the shared catalog. "
            "6) RECOMMEND — Sort catalog by composite score, cross-reference with global registry "
            "   for availability, present top 5 available niches as expansion candidates. "
            "Output: niches discovered, niches added to catalog, top 5 recommendations."
        )
    }
]

def run_cli(args, timeout=60):
    cmd = ["mulerun"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {"stdout": result.stdout.strip(), "stderr": result.stderr.strip(), "code": result.returncode}
    except subprocess.TimeoutExpired:
        return {"error": "timeout", "code": -1}

def deploy_scripts():
    """Upload orchestrator and pipeline scripts to the compute instance."""
    scripts_dir = Path(__file__).parent
    scripts = ["orchestrator.py", "pipeline.py", "niche_registry.py"]

    for script in scripts:
        script_path = scripts_dir / script
        if script_path.exists():
            result = run_cli([
                "computer", "fs", "write",
                f"${HOME}/.clip-factory/scripts/{script}",
                "--from-file", str(script_path)
            ])
            if result.get("code") == 0:
                print(f"  Uploaded: {script}")
            else:
                print(f"  Failed to upload {script}: {result.get('stderr', result.get('error'))}")

    # Make executable
    run_cli(["computer", "chat", "--prompt",
             "chmod +x ~/.clip-factory/scripts/*.py"])

def create_crons(dry_run=False):
    """Create all scheduled tasks on the compute instance."""
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Creating {len(CRON_DEFINITIONS)} cron jobs:\n")

    for cron in CRON_DEFINITIONS:
        print(f"  {cron['name']}")
        print(f"    Schedule: {cron['schedule_value']} ({cron['schedule_type']})")
        print(f"    Description: {cron['description']}")

        if not dry_run:
            result = run_cli([
                "computer", "schedule", "create",
                "--name", cron["name"],
                "--prompt", cron["prompt"],
                "--schedule-type", cron["schedule_type"],
                "--schedule-value", cron["schedule_value"],
                "--description", cron["description"]
            ], timeout=30)

            if result.get("code") == 0:
                print(f"    Status: CREATED")
            else:
                print(f"    Status: FAILED — {result.get('stderr', result.get('error', 'unknown'))}")
        else:
            print(f"    Status: [would create]")
        print()

def show_status():
    """List all existing clip-factory cron jobs."""
    result = run_cli(["computer", "schedule", "list", "-o", "json"])
    if result.get("code") != 0:
        print(f"Error listing schedules: {result.get('stderr')}")
        return

    try:
        tasks = json.loads(result.get("stdout", "[]"))
    except json.JSONDecodeError:
        tasks = []

    clip_tasks = [t for t in tasks if str(t.get("name", "")).startswith("clip-factory")]

    if not clip_tasks:
        print("No clip-factory cron jobs found.")
        return

    print(f"\n{len(clip_tasks)} clip-factory cron jobs:\n")
    for task in clip_tasks:
        print(f"  {task.get('name')}")
        print(f"    ID: {task.get('id')}")
        print(f"    Status: {task.get('status', 'unknown')}")
        print(f"    Schedule: {task.get('schedule_value', 'unknown')}")
        print()

def main():
    if "--dry-run" in sys.argv:
        create_crons(dry_run=True)
    elif "--status" in sys.argv:
        show_status()
    elif "--deploy-scripts" in sys.argv:
        deploy_scripts()
    else:
        print("Deploying scripts to compute instance...")
        deploy_scripts()
        print("\nCreating cron jobs...")
        create_crons(dry_run=False)
        print("\nDone. Use --status to verify.")

if __name__ == "__main__":
    main()
