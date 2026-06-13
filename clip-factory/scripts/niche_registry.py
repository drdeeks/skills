#!/usr/bin/env python3
"""
Clip Factory Global Niche Registry — Multi-Agent Coordination via MuleRun Drive

Manages the shared global registry that prevents niche collisions across
up to 25+ independent clip-factory agents. Max 2 agents per niche.

Uses MuleRun Drive as the shared coordination layer:
  /clip-factory/global-registry.json  — niche claims + heartbeats
  /clip-factory/niche-catalog.json    — discovered niches
  /clip-factory/coordination-log.jsonl — audit trail

Usage:
    python3 niche_registry.py register
    python3 niche_registry.py claim <niche>
    python3 niche_registry.py release <niche>
    python3 niche_registry.py heartbeat
    python3 niche_registry.py available
    python3 niche_registry.py status
    python3 niche_registry.py discover-add <niche_json>
    python3 niche_registry.py catalog
    python3 niche_registry.py prune
"""

import json
import os
import sys
import subprocess
import uuid
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────────────

DRIVE_REGISTRY = "/clip-factory/global-registry.json"
DRIVE_CATALOG = "/clip-factory/niche-catalog.json"
DRIVE_LOG = "/clip-factory/coordination-log.jsonl"

MAX_AGENTS_PER_NICHE = 2
HEARTBEAT_TIMEOUT_HOURS = 2

LOCAL_INSTANCE_FILE = Path.home() / ".clip-factory" / "instance_id"

def get_instance_id():
    """Get or create a persistent instance ID for this agent."""
    if LOCAL_INSTANCE_FILE.exists():
        return LOCAL_INSTANCE_FILE.read_text().strip()
    instance_id = f"agent-{uuid.uuid4().hex[:6]}"
    LOCAL_INSTANCE_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_INSTANCE_FILE.write_text(instance_id)
    return instance_id

def now_iso():
    return datetime.now(timezone.utc).isoformat()

# ─── Drive I/O ────────────────────────────────────────────────────────────────

def drive_download(remote_path, local_path):
    """Download a file from MuleRun Drive."""
    result = subprocess.run(
        ["mulerun", "drive", "download", remote_path, "--dest", local_path],
        capture_output=True, text=True, timeout=30
    )
    return result.returncode == 0

def drive_upload(local_path, remote_path):
    """Upload a file to MuleRun Drive."""
    result = subprocess.run(
        ["mulerun", "drive", "upload", local_path, remote_path],
        capture_output=True, text=True, timeout=30
    )
    return result.returncode == 0

def drive_ensure_dir(path):
    """Create a directory on Drive if it doesn't exist."""
    subprocess.run(
        ["mulerun", "drive", "mkdir", path],
        capture_output=True, text=True, timeout=15
    )

def load_registry():
    """Download and parse the global registry from Drive."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        tmp = f.name

    if drive_download(DRIVE_REGISTRY, tmp):
        try:
            with open(tmp) as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        finally:
            os.unlink(tmp)

    # Registry doesn't exist yet — create empty
    return {
        "version": 1,
        "last_updated": now_iso(),
        "max_agents_per_niche": MAX_AGENTS_PER_NICHE,
        "agents": {},
        "niche_claims": {}
    }

def save_registry(registry):
    """Upload the registry back to Drive."""
    registry["last_updated"] = now_iso()
    drive_ensure_dir("/clip-factory")

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump(registry, f, indent=2, default=str)
        tmp = f.name

    success = drive_upload(tmp, DRIVE_REGISTRY)
    os.unlink(tmp)
    return success

def append_log(entry):
    """Append an entry to the coordination log on Drive."""
    entry["timestamp"] = now_iso()

    # Download existing log, append, re-upload
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
        tmp = f.name

    existing = ""
    if drive_download(DRIVE_LOG, tmp):
        try:
            with open(tmp) as f:
                existing = f.read()
        except FileNotFoundError:
            pass

    with open(tmp, "w") as f:
        if existing:
            f.write(existing)
            if not existing.endswith("\n"):
                f.write("\n")
        f.write(json.dumps(entry, default=str) + "\n")

    drive_upload(tmp, DRIVE_LOG)
    os.unlink(tmp)

def load_catalog():
    """Download and parse the niche catalog from Drive."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        tmp = f.name

    if drive_download(DRIVE_CATALOG, tmp):
        try:
            with open(tmp) as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        finally:
            os.unlink(tmp)

    return {"version": 1, "last_updated": now_iso(), "niches": []}

def save_catalog(catalog):
    """Upload the catalog back to Drive."""
    catalog["last_updated"] = now_iso()

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump(catalog, f, indent=2, default=str)
        tmp = f.name

    success = drive_upload(tmp, DRIVE_CATALOG)
    os.unlink(tmp)
    return success

# ─── Stale Agent Pruning ─────────────────────────────────────────────────────

def prune_stale_agents(registry):
    """Remove agents whose heartbeat is older than HEARTBEAT_TIMEOUT_HOURS."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=HEARTBEAT_TIMEOUT_HOURS)
    pruned = []

    for agent_id, info in list(registry["agents"].items()):
        hb = info.get("last_heartbeat")
        if not hb:
            continue
        try:
            hb_time = datetime.fromisoformat(hb.replace("Z", "+00:00"))
            if hb_time < cutoff:
                # Remove from all niche claims
                released_niches = []
                for niche, claim in registry["niche_claims"].items():
                    if agent_id in claim.get("claimed_by", []):
                        claim["claimed_by"].remove(agent_id)
                        claim["available_slots"] = claim["max_slots"] - len(claim["claimed_by"])
                        released_niches.append(niche)

                info["status"] = "expired"
                pruned.append({"agent": agent_id, "released_niches": released_niches})
        except (ValueError, TypeError):
            continue

    return pruned

# ─── Commands ─────────────────────────────────────────────────────────────────

def register():
    """Register this agent instance in the global registry."""
    instance_id = get_instance_id()
    registry = load_registry()

    if instance_id in registry["agents"] and registry["agents"][instance_id].get("status") == "active":
        print(json.dumps({"status": "already_registered", "instance_id": instance_id}))
        return

    registry["agents"][instance_id] = {
        "instance_id": instance_id,
        "registered_at": now_iso(),
        "last_heartbeat": now_iso(),
        "niches": [],
        "accounts_count": 0,
        "status": "active"
    }

    # Prune stale while we're here
    pruned = prune_stale_agents(registry)

    save_registry(registry)
    append_log({"agent": instance_id, "event": "register"})

    result = {"status": "registered", "instance_id": instance_id}
    if pruned:
        result["pruned_stale"] = pruned
    print(json.dumps(result, indent=2))

def claim(niche):
    """Attempt to claim a niche slot. Fails if niche is full (>= max_agents_per_niche)."""
    instance_id = get_instance_id()
    registry = load_registry()

    # Prune stale first
    prune_stale_agents(registry)

    # Ensure niche exists in claims
    if niche not in registry["niche_claims"]:
        registry["niche_claims"][niche] = {
            "claimed_by": [],
            "max_slots": registry.get("max_agents_per_niche", MAX_AGENTS_PER_NICHE),
            "available_slots": registry.get("max_agents_per_niche", MAX_AGENTS_PER_NICHE)
        }

    claim_info = registry["niche_claims"][niche]
    current_claimants = [c for c in claim_info["claimed_by"] if registry["agents"].get(c, {}).get("status") == "active"]
    claim_info["claimed_by"] = current_claimants  # Clean up stale refs

    max_slots = claim_info.get("max_slots", MAX_AGENTS_PER_NICHE)

    # Check if already claimed by this agent
    if instance_id in current_claimants:
        print(json.dumps({"status": "already_claimed", "niche": niche, "instance_id": instance_id}))
        return

    # Check capacity
    if len(current_claimants) >= max_slots:
        # Niche is full
        available = get_available_list(registry)
        append_log({"agent": instance_id, "event": "claim_denied", "niche": niche,
                     "reason": f"{len(current_claimants)}/{max_slots} slots full"})

        result = {
            "status": "denied",
            "niche": niche,
            "reason": f"Niche full: {len(current_claimants)}/{max_slots} agents active",
            "current_agents": current_claimants,
            "available_niches": available[:10]
        }
        save_registry(registry)
        print(json.dumps(result, indent=2))
        return

    # Claim the slot
    claim_info["claimed_by"].append(instance_id)
    claim_info["available_slots"] = max_slots - len(claim_info["claimed_by"])

    # Update agent record
    if instance_id in registry["agents"]:
        if niche not in registry["agents"][instance_id].get("niches", []):
            registry["agents"][instance_id].setdefault("niches", []).append(niche)
        registry["agents"][instance_id]["last_heartbeat"] = now_iso()

    save_registry(registry)

    # Collision check — re-download and verify
    verify_registry = load_registry()
    verify_claimants = verify_registry.get("niche_claims", {}).get(niche, {}).get("claimed_by", [])
    if len(verify_claimants) > max_slots:
        # Race condition — newest agent yields
        timestamps = {}
        for aid in verify_claimants:
            agent_info = verify_registry["agents"].get(aid, {})
            timestamps[aid] = agent_info.get("registered_at", "9999")
        sorted_agents = sorted(timestamps.items(), key=lambda x: x[1])
        newest = sorted_agents[-1][0]

        if newest == instance_id:
            # We're the newest — yield
            verify_registry["niche_claims"][niche]["claimed_by"].remove(instance_id)
            verify_registry["niche_claims"][niche]["available_slots"] += 1
            if instance_id in verify_registry["agents"]:
                niches = verify_registry["agents"][instance_id].get("niches", [])
                if niche in niches:
                    niches.remove(niche)
            save_registry(verify_registry)
            append_log({"agent": instance_id, "event": "claim_yielded", "niche": niche,
                         "reason": "race condition — newest agent yields"})
            print(json.dumps({"status": "yielded", "niche": niche, "reason": "race condition resolved"}))
            return

    append_log({"agent": instance_id, "event": "claim_niche", "niche": niche,
                 "slot": f"{len(claim_info['claimed_by'])}/{max_slots}"})

    print(json.dumps({
        "status": "claimed",
        "niche": niche,
        "slot": f"{len(claim_info['claimed_by'])}/{max_slots}",
        "instance_id": instance_id
    }, indent=2))

def release(niche):
    """Release a niche claim."""
    instance_id = get_instance_id()
    registry = load_registry()

    if niche in registry["niche_claims"]:
        claim_info = registry["niche_claims"][niche]
        if instance_id in claim_info.get("claimed_by", []):
            claim_info["claimed_by"].remove(instance_id)
            claim_info["available_slots"] = claim_info["max_slots"] - len(claim_info["claimed_by"])

    if instance_id in registry["agents"]:
        niches = registry["agents"][instance_id].get("niches", [])
        if niche in niches:
            niches.remove(niche)

    save_registry(registry)
    append_log({"agent": instance_id, "event": "release_niche", "niche": niche})

    print(json.dumps({"status": "released", "niche": niche, "instance_id": instance_id}))

def heartbeat():
    """Send a heartbeat and prune stale agents."""
    instance_id = get_instance_id()
    registry = load_registry()

    if instance_id in registry["agents"]:
        registry["agents"][instance_id]["last_heartbeat"] = now_iso()
        registry["agents"][instance_id]["status"] = "active"

    pruned = prune_stale_agents(registry)
    save_registry(registry)

    if pruned:
        for p in pruned:
            append_log({"agent": instance_id, "event": "pruned_stale",
                         "stale_agent": p["agent"], "released_niches": p["released_niches"]})

    result = {"status": "heartbeat_sent", "instance_id": instance_id, "pruned": pruned}
    print(json.dumps(result, indent=2))

def get_available_list(registry):
    """Return list of niches with available slots, sorted by availability."""
    available = []
    for niche, info in registry.get("niche_claims", {}).items():
        active_claimants = [c for c in info.get("claimed_by", [])
                           if registry["agents"].get(c, {}).get("status") == "active"]
        max_s = info.get("max_slots", MAX_AGENTS_PER_NICHE)
        slots = max_s - len(active_claimants)
        if slots > 0:
            available.append({
                "niche": niche,
                "available_slots": slots,
                "current_agents": len(active_claimants),
                "max_slots": max_s
            })
    return sorted(available, key=lambda n: n["available_slots"], reverse=True)

def show_available():
    """Show all niches with available slots."""
    registry = load_registry()
    prune_stale_agents(registry)
    available = get_available_list(registry)

    # Also check catalog for unclaimed niches
    catalog = load_catalog()
    registered_niches = set(registry.get("niche_claims", {}).keys())
    for cat_niche in catalog.get("niches", []):
        name = cat_niche.get("name", "")
        if name and name not in registered_niches:
            available.append({
                "niche": name,
                "available_slots": MAX_AGENTS_PER_NICHE,
                "current_agents": 0,
                "max_slots": MAX_AGENTS_PER_NICHE,
                "source": "catalog",
                "composite_score": cat_niche.get("scoring", {}).get("composite_score", 0)
            })

    print(json.dumps({"available_niches": available, "total": len(available)}, indent=2))

def show_status():
    """Show full registry status."""
    registry = load_registry()
    prune_stale_agents(registry)

    active_agents = [a for a in registry["agents"].values() if a.get("status") == "active"]
    total_claims = sum(len(c.get("claimed_by", [])) for c in registry.get("niche_claims", {}).values())

    status = {
        "active_agents": len(active_agents),
        "total_agents_ever": len(registry["agents"]),
        "niches_tracked": len(registry.get("niche_claims", {})),
        "total_claims": total_claims,
        "agents": {aid: {
            "niches": info.get("niches", []),
            "status": info.get("status"),
            "last_heartbeat": info.get("last_heartbeat")
        } for aid, info in registry["agents"].items() if info.get("status") == "active"},
        "niche_claims": {niche: {
            "agents": info.get("claimed_by", []),
            "slots": f"{len(info.get('claimed_by', []))}/{info.get('max_slots', MAX_AGENTS_PER_NICHE)}"
        } for niche, info in registry.get("niche_claims", {}).items()}
    }
    print(json.dumps(status, indent=2))

def show_catalog():
    """Show the shared niche catalog."""
    catalog = load_catalog()
    niches = catalog.get("niches", [])
    sorted_niches = sorted(niches, key=lambda n: n.get("scoring", {}).get("composite_score", 0), reverse=True)

    summary = [{
        "name": n.get("name"),
        "category": n.get("category"),
        "composite_score": n.get("scoring", {}).get("composite_score", 0),
        "creators_count": len(n.get("creators", [])),
        "status": n.get("status"),
        "discovered_at": n.get("discovered_at")
    } for n in sorted_niches]

    print(json.dumps({"total_niches": len(summary), "niches": summary}, indent=2))

def discover_add(niche_json_str):
    """Add a newly discovered niche to the shared catalog."""
    instance_id = get_instance_id()

    try:
        niche_data = json.loads(niche_json_str)
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON"}))
        return

    catalog = load_catalog()

    # Deduplicate by name
    existing_names = {n.get("name", "").lower() for n in catalog.get("niches", [])}
    if niche_data.get("name", "").lower() in existing_names:
        print(json.dumps({"status": "duplicate", "niche": niche_data.get("name")}))
        return

    # Enrich with metadata
    niche_data.setdefault("id", str(uuid.uuid4())[:8])
    niche_data.setdefault("discovered_at", now_iso())
    niche_data.setdefault("discovered_by", instance_id)
    niche_data.setdefault("status", "new")
    niche_data.setdefault("last_validated", now_iso())

    catalog["niches"].append(niche_data)
    save_catalog(catalog)

    append_log({"agent": instance_id, "event": "niche_discovered", "niche": niche_data.get("name"),
                 "source": niche_data.get("discovery_source", "manual")})

    print(json.dumps({"status": "added", "niche": niche_data.get("name"), "catalog_size": len(catalog["niches"])}))

def do_prune():
    """Force prune stale agents and recalculate slots."""
    registry = load_registry()
    pruned = prune_stale_agents(registry)
    save_registry(registry)

    if pruned:
        instance_id = get_instance_id()
        for p in pruned:
            append_log({"agent": instance_id, "event": "pruned_stale",
                         "stale_agent": p["agent"], "released_niches": p["released_niches"]})

    print(json.dumps({"pruned": pruned, "pruned_count": len(pruned)}, indent=2))

# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: niche_registry.py <register|claim|release|heartbeat|available|status|catalog|discover-add|prune>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "register":
        register()
    elif cmd == "claim" and len(sys.argv) >= 3:
        claim(sys.argv[2])
    elif cmd == "release" and len(sys.argv) >= 3:
        release(sys.argv[2])
    elif cmd == "heartbeat":
        heartbeat()
    elif cmd == "available":
        show_available()
    elif cmd == "status":
        show_status()
    elif cmd == "catalog":
        show_catalog()
    elif cmd == "discover-add" and len(sys.argv) >= 3:
        discover_add(sys.argv[2])
    elif cmd == "prune":
        do_prune()
    else:
        print(f"Unknown command or missing args: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
