#!/usr/bin/env python3
"""
Clip Factory Async Pipeline Runner

Handles the async clip processing pipeline: queue management, parallel Vugola
processing, Postiz scheduling, and retry logic. Designed for maximum throughput
with configurable concurrency.

Usage:
    python3 pipeline.py scan --config ~/.clip-factory/config.json
    python3 pipeline.py process --max-concurrent 5 --timeout 1800
    python3 pipeline.py schedule --timezone America/Chicago
    python3 pipeline.py retry --max-retries 3
    python3 pipeline.py status
"""

import json
import os
import sys
import subprocess
import uuid
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ─── Paths ────────────────────────────────────────────────────────────────────

BASE_DIR = Path.home() / ".clip-factory"
CONFIG_PATH = BASE_DIR / "config.json"
QUEUE_PATH = BASE_DIR / "queue.jsonl"
PROCESSING_PATH = BASE_DIR / "processing.jsonl"
CLIPS_LOG = BASE_DIR / "analytics" / "clips.jsonl"
RETRY_QUEUE = BASE_DIR / "retry_queue.jsonl"
PIPELINE_LOG = BASE_DIR / "logs" / "pipeline.log"

def load_json(path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}

def append_jsonl(path, record):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(record, default=str) + "\n")

def load_jsonl(path):
    records = []
    if not path.exists():
        return records
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records

def write_jsonl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for r in records:
            f.write(json.dumps(r, default=str) + "\n")

def log(msg):
    ts = datetime.now(timezone.utc).isoformat()
    entry = f"[{ts}] {msg}"
    print(entry, file=sys.stderr)
    PIPELINE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(PIPELINE_LOG, "a") as f:
        f.write(entry + "\n")

def run_cli(args, timeout=120):
    cmd = ["mulerun"] + args + ["-o", "json"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout.strip())
        return {"error": result.stderr.strip(), "code": result.returncode}
    except subprocess.TimeoutExpired:
        return {"error": "timeout", "code": -1}
    except json.JSONDecodeError:
        return {"raw": result.stdout.strip() if result.stdout else "", "code": result.returncode}

# ─── Scan: Discover new source content ────────────────────────────────────────

def scan(config_path=None):
    """
    Scan tracked creators for new content. Adds new videos to the processing queue.
    This is a template — the actual scanning uses Firecrawl/YouTube MCP via the agent.
    """
    config = load_json(config_path or CONFIG_PATH)
    niches = [n for n in config.get("niches", []) if n.get("status") == "active"]

    queue = load_jsonl(QUEUE_PATH)
    existing_urls = {q.get("source_url") for q in queue}

    scan_results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "niches_scanned": len(niches),
        "creators_checked": 0,
        "new_videos_queued": 0,
        "already_queued": 0
    }

    for niche in niches:
        for creator in niche.get("creators", []):
            scan_results["creators_checked"] += 1
            # In real execution, the agent would call Firecrawl or YouTube MCP here
            # This script provides the queue management infrastructure
            log(f"Scan queued for creator: {creator} (niche: {niche['name']})")

    print(json.dumps(scan_results, indent=2))
    return scan_results

def enqueue_video(source_url, creator, niche, metadata=None):
    """Add a video to the processing queue. Called by the agent after scanning."""
    queue = load_jsonl(QUEUE_PATH)
    existing_urls = {q.get("source_url") for q in queue}

    if source_url in existing_urls:
        return {"status": "duplicate", "source_url": source_url}

    entry = {
        "queue_id": str(uuid.uuid4())[:8],
        "source_url": source_url,
        "creator": creator,
        "niche": niche,
        "queued_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending",
        "retries": 0,
        "metadata": metadata or {}
    }
    append_jsonl(QUEUE_PATH, entry)
    log(f"Queued: {source_url} ({creator}/{niche})")
    return {"status": "queued", **entry}

# ─── Process: Parallel Vugola clip extraction ─────────────────────────────────

def process_queue(max_concurrent=3, timeout=1800, clips_per_video=5):
    """
    Process queued videos through Vugola in parallel.
    Uses ThreadPoolExecutor for concurrent clip extraction.

    max_concurrent: Max simultaneous Vugola jobs (respect API rate limits)
    timeout: Max seconds to wait for a single clip job
    clips_per_video: How many clips to extract per source video
    """
    queue = load_jsonl(QUEUE_PATH)
    pending = [q for q in queue if q.get("status") == "pending"]

    if not pending:
        log("No pending items in queue")
        print(json.dumps({"status": "empty", "pending": 0}))
        return

    log(f"Processing {len(pending)} queued videos (max concurrent: {max_concurrent})")

    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_queued": len(pending),
        "processed": 0,
        "succeeded": 0,
        "failed": 0,
        "clips_extracted": 0,
        "details": []
    }

    def process_single(item):
        """Process a single queued video. Returns result dict."""
        item_id = item["queue_id"]
        log(f"Processing {item_id}: {item['source_url']}")

        # Mark as processing
        item["status"] = "processing"
        item["processing_started"] = datetime.now(timezone.utc).isoformat()

        # In real execution, the agent calls Vugola MCP here:
        # 1. clip_video(url=item["source_url"], num_clips=clips_per_video)
        # 2. Poll get_clip_status until done
        # 3. download_clip for each result

        # This template returns a structured result for the agent to fill
        return {
            "queue_id": item_id,
            "source_url": item["source_url"],
            "creator": item["creator"],
            "niche": item["niche"],
            "status": "needs_agent",  # Agent fills this with 'completed' or 'failed'
            "clips": [],  # Agent fills with extracted clip records
            "processing_time": None
        }

    # Execute in parallel with thread pool
    with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
        futures = {executor.submit(process_single, item): item for item in pending}
        for future in as_completed(futures):
            try:
                result = future.result()
                results["processed"] += 1
                results["details"].append(result)
                if result.get("status") == "completed":
                    results["succeeded"] += 1
                    results["clips_extracted"] += len(result.get("clips", []))
            except Exception as e:
                results["failed"] += 1
                log(f"Error processing: {e}")

    # Update queue file (remove processed items, keep failures for retry)
    remaining = [q for q in queue if q.get("status") == "pending" and q not in pending]
    write_jsonl(QUEUE_PATH, remaining)

    print(json.dumps(results, indent=2))
    return results

# ─── Schedule: Distribute clips to Postiz ─────────────────────────────────────

def schedule_clips(timezone_str="America/Chicago"):
    """
    Take processed clips and schedule them across platforms via Postiz.
    Distributes evenly across time slots and platforms.
    """
    config = load_json(CONFIG_PATH)
    slots = config.get("posting_schedule", {}).get("slots_cdt", ["09:00", "12:00", "15:00", "18:00", "21:00"])

    # Load unscheduled clips
    clips = load_jsonl(CLIPS_LOG)
    unscheduled = [c for c in clips if c.get("status") == "extracted" and not c.get("scheduled")]

    if not unscheduled:
        print(json.dumps({"status": "no_clips", "unscheduled": 0}))
        return

    schedule_plan = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_to_schedule": len(unscheduled),
        "schedule": []
    }

    # Build schedule: round-robin across time slots and platforms
    niches = config.get("niches", [])
    all_accounts = []
    for niche in niches:
        for account in niche.get("accounts", []):
            all_accounts.append({**account, "niche": niche["name"]})

    slot_idx = 0
    account_idx = 0

    for clip in unscheduled:
        # Find matching accounts (same niche)
        niche_accounts = [a for a in all_accounts if a["niche"] == clip.get("niche")]
        if not niche_accounts:
            niche_accounts = all_accounts  # Fallback to any account

        for account in niche_accounts:
            slot = slots[slot_idx % len(slots)]
            slot_idx += 1

            schedule_entry = {
                "clip_id": clip.get("clip_id"),
                "account": account["handle"],
                "platform": account["platform"],
                "scheduled_time": slot,
                "timezone": timezone_str,
                "status": "pending_postiz"
                # Agent calls Postiz posts:create here
            }
            schedule_plan["schedule"].append(schedule_entry)

    print(json.dumps(schedule_plan, indent=2))
    return schedule_plan

# ─── Retry: Reprocess failed items ───────────────────────────────────────────

def retry_failed(max_retries=3):
    """
    Move failed items back to the queue for reprocessing, up to max_retries.
    Items exceeding max_retries are logged as permanent failures.
    """
    retry_items = load_jsonl(RETRY_QUEUE)
    queue = load_jsonl(QUEUE_PATH)

    requeued = 0
    permanently_failed = 0

    for item in retry_items:
        retries = item.get("retries", 0)
        if retries >= max_retries:
            permanently_failed += 1
            append_jsonl(BASE_DIR / "analytics" / "permanent_failures.jsonl", {
                **item,
                "permanently_failed_at": datetime.now(timezone.utc).isoformat(),
                "reason": f"Exceeded {max_retries} retries"
            })
            log(f"Permanently failed: {item.get('source_url')} after {retries} retries")
        else:
            item["retries"] = retries + 1
            item["status"] = "pending"
            item["retry_at"] = datetime.now(timezone.utc).isoformat()
            queue.append(item)
            requeued += 1
            log(f"Requeued (attempt {item['retries']}): {item.get('source_url')}")

    write_jsonl(QUEUE_PATH, queue)
    write_jsonl(RETRY_QUEUE, [])  # Clear retry queue

    result = {
        "requeued": requeued,
        "permanently_failed": permanently_failed,
        "queue_size": len(queue)
    }
    print(json.dumps(result, indent=2))
    return result

# ─── Status: Current pipeline state ──────────────────────────────────────────

def pipeline_status():
    """Show current pipeline state: queue sizes, active processing, recent results."""
    queue = load_jsonl(QUEUE_PATH)
    processing = load_jsonl(PROCESSING_PATH)
    clips = load_jsonl(CLIPS_LOG)
    retries = load_jsonl(RETRY_QUEUE)

    # Recent clips (last 24h)
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)
    recent_clips = []
    for c in clips:
        ts = c.get("aggregated_at") or c.get("posted_at")
        if ts:
            try:
                parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                if parsed > yesterday:
                    recent_clips.append(c)
            except Exception:
                pass

    status = {
        "timestamp": now.isoformat(),
        "queue": {
            "pending": len([q for q in queue if q.get("status") == "pending"]),
            "processing": len([q for q in queue if q.get("status") == "processing"]),
            "total": len(queue)
        },
        "retry_queue": len(retries),
        "clips": {
            "total_all_time": len(clips),
            "last_24h": len(recent_clips),
        },
        "pipeline_health": "ok" if len(retries) < 10 else "degraded"
    }

    print(json.dumps(status, indent=2))
    return status

# ─── CLI Entry Point ──────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: pipeline.py <scan|process|schedule|retry|status|enqueue>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "scan":
        config_path = None
        if "--config" in sys.argv:
            idx = sys.argv.index("--config")
            config_path = Path(sys.argv[idx + 1])
        scan(config_path)

    elif cmd == "process":
        kwargs = {}
        if "--max-concurrent" in sys.argv:
            idx = sys.argv.index("--max-concurrent")
            kwargs["max_concurrent"] = int(sys.argv[idx + 1])
        if "--timeout" in sys.argv:
            idx = sys.argv.index("--timeout")
            kwargs["timeout"] = int(sys.argv[idx + 1])
        process_queue(**kwargs)

    elif cmd == "schedule":
        tz = "America/Chicago"
        if "--timezone" in sys.argv:
            idx = sys.argv.index("--timezone")
            tz = sys.argv[idx + 1]
        schedule_clips(tz)

    elif cmd == "retry":
        max_retries = 3
        if "--max-retries" in sys.argv:
            idx = sys.argv.index("--max-retries")
            max_retries = int(sys.argv[idx + 1])
        retry_failed(max_retries)

    elif cmd == "status":
        pipeline_status()

    elif cmd == "enqueue":
        if len(sys.argv) < 5:
            print("Usage: pipeline.py enqueue <url> <creator> <niche>")
            sys.exit(1)
        result = enqueue_video(sys.argv[2], sys.argv[3], sys.argv[4])
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
