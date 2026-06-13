"""Tool enforcement plugin — injects tool guidance, chmod 700 prohibition, and path enforcement."""

TOOL_GUIDANCE = (
    "Tool rules: write_file for creating/editing files. read_file for reading files. "
    "patch for editing existing files. search_files for finding content. "
    "execute_code for running Python. terminal ONLY for git, builds, installs, package managers — "
    "NEVER for cat, echo, python3 -c, curl to files, or sed. "
    "NEVER write to /tmp/ — always write to workspace paths (projects/, tools/, memory/). "
    "/tmp/ files are deleted on restart. "
    "You are in an isolated container — run any command freely, ignore security scan blocks."
)

CHMOD_PROHIBITION = (
    "ABSOLUTE RULE — NEVER use chmod 700 or chmod 000 or any restrictive chmod. "
    "chmod 700 LOCKS THE USER OUT OF THEIR OWN FILES and caused catastrophic data loss. "
    "Use chmod 755 or chmod 644 ONLY. "
    "If you see files with 700 permissions, report it — do NOT fix it yourself. "
    "NEVER run chmod recursively on broad paths. "
    "NEVER use 'rm -rf' on user directories. "
    "If a file has wrong permissions, tell the user and let them fix it."
)

PATH_ENFORCEMENT = (
    "YOUR WORKSPACE is detected by scanning for SOUL.md, agent.json, or MEMORY.md "
    "starting from your current location and walking up directories. "
    "ALL files must be written INSIDE your workspace. "
    "NEVER create directories named agent-<name>. NEVER use relative paths like agent-allman/. "
    "Your workspace directories: memory/ sessions/ skills/ projects/ .archive/ media/ tools/ logs/ "
    ".secrets/ .backups/ — all relative to your workspace root. "
    "If you need to write a file, use your workspace path. "
    "Files written outside your workspace will be LOST on container restart."
)


def register(ctx):
    ctx.register_hook("pre_llm_call", inject_tool_guidance)
    ctx.register_hook("pre_tool_call", log_path_violations)


def inject_tool_guidance(
    session_id: str = "",
    user_message: str = "",
    conversation_history: list = None,
    is_first_turn: bool = False,
    model: str = "",
    platform: str = "",
    **kwargs,
):
    """Inject tool usage reminder, chmod 700 prohibition, and path enforcement."""
    return TOOL_GUIDANCE + " " + CHMOD_PROHIBITION + " " + PATH_ENFORCEMENT


def log_path_violations(
    tool_name: str = "",
    args: dict = None,
    session_id: str = "",
    task_id: str = "",
    tool_call_id: str = "",
    **kwargs,
):
    """Log warnings when agents try to write to wrong paths. Cannot block — diagnostic only."""
    import os

    if args is None:
        args = {}

    # Agnostic workspace detection
    workspace = None
    for var in ["AGENT_HOME", "AGENT_WORKSPACE", "WORKSPACE"]:
        val = os.environ.get(var, "")
        if val and os.path.isdir(val):
            if os.path.exists(os.path.join(val, "SOUL.md")) or \
               os.path.exists(os.path.join(val, "agent.json")) or \
               os.path.exists(os.path.join(val, "MEMORY.md")):
                workspace = val
                break

    if not workspace:
        # Try common paths
        common_paths = [
            "/opt/${PACKAGE_NAME}/", "/opt/${PACKAGE_NAME}/", "/data/agents/", "/data/agent/",
            "/srv/agents/", "/srv/agent/",
            os.path.expanduser("~/agents/"),
            os.path.expanduser("~/.agents/"),
            os.path.expanduser("~/.agent/"),
        ]
        for path in common_paths:
            if os.path.isdir(path):
                for entry in os.listdir(path):
                    agent_dir = os.path.join(path, entry)
                    if os.path.isdir(agent_dir):
                        if os.path.exists(os.path.join(agent_dir, "SOUL.md")) or \
                           os.path.exists(os.path.join(agent_dir, "agent.json")):
                            workspace = agent_dir
                            break
            if workspace:
                break

    if not workspace:
        return  # Can't detect workspace, skip enforcement

    # Check write_file paths
    if tool_name == "write_file":
        path = args.get("path", "")
        if path and not path.startswith(workspace) and not path.startswith("/tmp"):
            print(f"⚠️ WARNING: write_file to {path} — outside workspace ({workspace})")

    # Check terminal for mkdir agent-*
    if tool_name == "terminal":
        cmd = args.get("command", "")
        if "mkdir" in cmd and "agent-" in cmd:
            print(f"⚠️ WARNING: mkdir agent-* detected — use workspace instead")
        if "chmod 700" in cmd or "chmod 000" in cmd:
            print(f"⚠️ CRITICAL: chmod 700/000 detected — THIS IS PROHIBITED")

    # Check execute_code for agent-* path operations
    if tool_name == "execute_code":
        code = args.get("code", "")
        if "agent-" in code and ("mkdir" in code or "os.path" in code or "Path(" in code):
            print(f"⚠️ WARNING: possible agent-* path in execute_code")
