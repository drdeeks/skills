---
description: Comprehensive USB drive management. Handles detection, mounting, partitioning,
  formatting, Ventoy multi-boot setup with persistence, mkusb live/persistent USB
  creation, hidden device recovery, unrecognized drive troubleshooting, boot configuration,
  GUI/terminal access, Docker container/volume management, and disk image management.
  Use when managing any USB storage device.
license: MIT
metadata:
  category: system
  tags:
  - usb
  - storage
  - ventoy
  - mkusb
  - partitioning
  - live-usb
  - hidden-devices
  - boot
  - gui
  - terminal
  - docker
  - containers
  - volumes
  - disk-images
  - persistence
name: unified-usb-skill
version: 0.0.3
---


# USB Manager

Comprehensive USB drive management tool. Handles detection, mounting, partitioning, formatting, Ventoy multi-boot setup with persistence, mkusb live/persistent USB creation, hidden device recovery, unrecognized drive troubleshooting, boot configuration, GUI/terminal access, Docker container/volume management, and disk image management.
# Portable Linux USB

Complete lifecycle management for portable Linux USB environments — from raw USB drive to enterprise multi-agent isolated deployments.

## When to Use

- Detecting and listing all USB storage devices (visible and hidden)
- Mounting/unmounting USB partitions with automatic filesystem detection
- Creating partition tables (MBR/GPT) and formatting drives
- Setting up Ventoy for multi-ISO bootable USB drives
- Managing Ventoy persistence images (create, mount, copy, resize)
- Creating live or persistent USB drives with mkusb
- Recovering hidden, unrecognized, or failed USB devices
- Scanning USB contents for security threats or file analysis
- Cloning USB drives for backup or deployment
- Configuring BIOS/UEFI for USB boot
- Accessing USB drives via GUI file managers or terminal commands
- Managing Docker containers and volumes on USB drives
- Running portable Docker environments from USB
- Creating, mounting, converting, and managing disk images
- Installing and running services entirely from USB (no host modifications)
- Managing systemd services stored on USB for portability


## Provider Compatibility

| Provider | Compatibility | Notes |
|----------|---------------|-------|
| Claude (Anthropic) | Full | MCP servers, tool use |
| OpenAI / ChatGPT | Full | Function calling, Actions |
| Mistral / Le Chat | Full | Tool calling, script execution |
| Gemini (Google) | Full | Extensions, Vertex AI |
| Any LLM + tools | Full | Scripts are plain Bash, provider-independent |

### Agent Framework Support

| Framework | Compatibility | Integration |
|---|---|---|
| OpenAI (ChatGPT) | Full | Run agents in Docker containers on USB |
| Claude (Anthropic) | Full | Agent isolation via partition separation |
| Mistral / Le Chat | Full | Containerized agent workspaces |
| Gemini (Google) | Full | Multi-agent deployment on USB |
| Hermes (Nous) | Full | Local LLM agents on persistent USB |
| GitHub Copilot | Full | Development environment on USB |
| Any LLM + tools | Full | Scripts are provider-independent |

### Platform Support

| Platform | Boot | Persistence | VM Access | Notes |
|---|---|---|---|---|
| Linux Host | Yes | Yes | Yes (QEMU/KVM) | Full support, native tools |
| Windows Host | Yes | Yes | Yes (QEMU) | Use Ext2Fsd for ext4 access |
| macOS Host | Yes | Yes | Yes (UTM/VMware) | Use macFUSE for ext4 access |
| Any PC (UEFI) | Yes | Yes | N/A | Boot from USB directly |
| Any PC (BIOS) | Yes | Yes | N/A | Legacy boot support |

## Quick Start

```bash
# Interactive mode (recommended)
sudo bash scripts/usb-manager.sh

# List all USB devices
lsblk -o NAME,SIZE,TYPE,TRAN,MODEL | grep -i usb

# List all block devices including hidden
lsblk -ndo NAME,SIZE,TYPE,TRAN | grep -E 'disk|usb'
```

### Basic Persistent USB

# 1. Download Ventoy
wget https://github.com/ventoy/Ventoy/releases/download/v1.1.12/ventoy-1.1.12-linux.tar.gz
tar -xf ventoy-1.1.12-linux.tar.gz -C /tmp

# 2. Install to USB (WARNING: wipes drive)
cd /tmp/ventoy-1.1.12 && sudo ./Ventoy2Disk.sh -i /dev/sdX

# 3. Copy ISO and configure persistence
sudo mount /dev/sdX1 /media/ventoy-usb
sudo cp ~/Downloads/ubuntu-24.04.4-desktop-amd64.iso /media/ventoy-usb/
sudo mkdir -p /media/ventoy-usb/persistence
sudo dd if=/dev/zero of=/media/ventoy-usb/persistence/ubuntu-persistence.dat bs=1M count=20000
sudo mkfs.ext4 -F -L casper-rw /media/ventoy-usb/persistence/ubuntu-persistence.dat

# 4. Configure Ventoy
sudo tee /media/ventoy-usb/ventoy/ventoy.json > /dev/null << 'EOF'
{
    "persistence": [{
        "image": "/ubuntu-24.04.4-desktop-amd64.iso",
        "backend": "/persistence/ubuntu-persistence.dat"
    }]
}
EOF
sudo umount /media/ventoy-usb

### Automated Setup

python3 scripts/setup.py --device /dev/sdX --iso ~/Downloads/ubuntu-24.04.4-desktop-amd64.iso --persistence 20G

### Enhanced Setup with Self-Healing, Testing, and AI Agent Support

# Run the enhanced setup script with dry-run to see what would be done
sudo bash scripts/setup-essentials-enhanced.sh --dry-run

# Run with self-healing enabled (restarts services if needed)
sudo bash scripts/setup-essentials-enhanced.sh --self-heal

# Run with verbose output for detailed debugging
sudo bash scripts/setup-essentials-enhanced.sh --verbose

# Run cleanup and debloating process
sudo bash scripts/setup-essentials-enhanced.sh --cleanup

# Interactive mode with all prompts
sudo bash scripts/setup-essentials-enhanced.sh

## Core Capabilities

| Capability | Description |
|------------|-------------|
| **Detect** | Find all USB devices including hidden and unrecognized drives |
| **Mount** | Smart mounting with automatic filesystem detection and dependency installation |
| **Partition** | Create MBR/GPT partition tables and partitions |
| **Format** | Format to FAT32, exFAT, NTFS, ext4, or other supported filesystems |
| **Ventoy** | Set up multi-ISO bootable USB with Ventoy |
| **Ventoy Persistence** | Manage persistence images (mount, copy, resize, inspect) |
| **mkusb** | Create live or persistent USB drives from ISO images |
| **Clone** | Disk-level cloning with verification |
| **Scan** | File type analysis, security scanning, and disk usage |
| **Recover** | Recover hidden, write-protected, or unrecognized devices |
| **Boot** | Configure BIOS/UEFI for USB boot, boot menu access, troubleshooting |
| **GUI/Terminal** | Access USB via file managers (Nautilus, Dolphin, Explorer) or CLI |
| **Docker** | Manage containers and volumes on USB, portable Docker environments |
| **Disk Images** | Create, mount, convert, inspect, and manage disk images (img, qcow2, vdi, vmdk) |
| **Services** | Install and run systemd services entirely from USB (no host modifications) |


## Use Case Guide

### I need to mount a USB drive

```bash
# Detect and mount interactively
sudo bash scripts/usb-manager.sh
# Select device -> option 4 (Mount partition)
```

The script auto-detects filesystem type and installs missing drivers (ntfs-3g, exfat-fuse) if needed.

### I need to create a bootable USB

Choose based on your needs:

| Need | Tool | Method |
|------|------|--------|
| Multiple ISOs on one USB | Ventoy | Copy ISOs to Ventoy partition |
| Single live Linux ISO | mkusb | Write ISO with persistent storage |
| Windows installer USB | Ventoy or mkusb | Copy ISO or write directly |
| Persistent live USB | mkusb | Create with overlay partition |
| Clone existing bootable USB | usb-manager | Disk-level clone with dd |

### I need to set up Ventoy (multi-ISO boot)

See [references/ventoy-setup.md](references/ventoy-setup.md)

```bash
# Quick Ventoy setup
sudo bash scripts/usb-manager.sh --ventoy-setup
```

Ventoy lets you copy multiple ISO files to a USB drive and boot any of them directly. No need to reformat for each ISO.

### I need to manage Ventoy persistence

See [references/ventoy-setup.md](references/ventoy-setup.md)

```bash
# Manage persistence interactively
sudo bash scripts/usb-manager.sh --ventoy-persist
```

Ventoy persistence allows saving data between boot sessions. The persistence is stored as a .dat image file in the persistence directory.

### I need to create a live/persistent USB with mkusb

See [references/mkusb-guide.md](references/mkusb-guide.md)

```bash
# Create live USB
sudo bash scripts/usb-manager.sh --mkusb-live

# Create persistent USB
sudo bash scripts/usb-manager.sh --mkusb-persistent
```

mkusb creates Linux live USBs with optional persistent storage for saving files and settings between sessions.

### I have a hidden or unrecognized USB

See [references/hidden-usb.md](references/hidden-usb.md)

```bash
# Scan for hidden devices
sudo bash scripts/usb-manager.sh --scan-hidden

# Attempt device recovery
sudo bash scripts/usb-manager.sh --recover-device
```

Hidden USBs can be caused by: corrupted partition tables, write protection, kernel driver issues, or hardware faults.

### I need to format a USB for specific use

| Target Use | Filesystem | Max File Size | Compatibility |
|------------|-----------|---------------|---------------|
| Cross-platform (Win/Mac/Linux) | exFAT | No limit | Most modern OS |
| Windows primary | NTFS | No limit | Windows (Linux/Mac read-only) |
| Maximum compatibility | FAT32 | 4 GB | Universal (all OS) |
| Linux only | ext4 | No limit | Linux native |
| Large file transfer | exFAT or NTFS | No limit | Modern OS |

### I need to boot from USB

See [references/boot-guide.md](references/boot-guide.md)

```bash
# Check if USB is bootable
sudo fdisk -l /dev/sdX | grep "Boot"

# List boot menu keys by manufacturer
# Dell: F12, HP: F9, Lenovo: F12, Acer: F12, ASUS: F8
```

Boot from USB requires:
- BIOS/UEFI with USB boot enabled
- Correct partition table (MBR for BIOS, GPT for UEFI)
- Bootable USB with proper bootloader

### I need to access USB via GUI or terminal

See [references/gui-terminal.md](references/gui-terminal.md)

| OS | GUI Tool | Terminal Command |
|----|----------|------------------|
| Linux | Nautilus, Dolphin, Thunar | `mount /dev/sdX1 /mnt/usb` |
| Windows | File Explorer, Disk Management | `diskpart` or `assign letter=Z` |
| macOS | Finder, Disk Utility | `diskutil mount /dev/disk2s1` |

### I need to manage Docker containers/volumes on USB

See [references/docker-usb.md](references/docker-usb.md)

```bash
# Run container with USB volume
docker run -d --name myapp -v /mnt/usb/data:/data nginx:latest

# Create volume on USB
docker volume create --driver local --opt type=none --opt device=/mnt/usb/volumes/mydata --opt o=bind usb-volume

# Backup Docker data to USB
docker run --rm -v myvolume:/source:ro -v /mnt/usb/backups:/backup alpine tar czf /backup/vol-backup.tar.gz -C /source .
```

Use cases:
- Portable Docker environments
- Persistent development workspaces
- Data processing pipelines
- Backup containers

### I need to install and run services from USB

USB-localized services run entirely from the USB drive with no host modifications. This ensures portability and isolation.

```bash
# Create service file on USB
mkdir -p /mnt/usb/systemd
cat > /mnt/usb/systemd/my-service.service << EOF
[Unit]
Description=My USB Service
After=network.target

[Service]
Type=simple
Environment="APP_HOME=/mnt/usb/app"
ExecStart=/mnt/usb/bin/my-service
Restart=on-failure
WorkingDirectory=/mnt/usb

[Install]
WantedBy=default.target
EOF

# To run the service (host must have systemd)
systemctl --user daemon-reload
systemctl --user start my-service
```

### Enhanced USB Setup with Self-Healing and AI Agent Support

For a comprehensive USB compute environment with self-healing capabilities, testing sweeps, cleanup processes, and AI agent support:

```bash
# Run the enhanced setup script with dry-run to see what would be done
sudo bash scripts/setup-essentials-enhanced.sh --dry-run

# Run with self-healing enabled (restarts services if needed)
sudo bash scripts/setup-essentials-enhanced.sh --self-heal

# Run with verbose output for detailed debugging
sudo bash scripts/setup-essentials-enhanced.sh --verbose

# Run cleanup and debloating process
sudo bash scripts/setup-essentials-enhanced.sh --cleanup

# Interactive mode with all prompts
sudo bash scripts/setup-essentials-enhanced.sh

# The script installs and configures:
# - Build essentials, development tools, Python, Node.js
# - LLM engines (llama.cpp, Ollama)
# - Agent harnesses (AutoGen, CrewAI, LangChain)
# - AI agent systems (OpenClaw, Hermes-agent, Opencode, Mistral Vibe, GitHub Copilot, Gemini, Claude Code, Cursor CLI)
# - Models directory for GGUF files
# - Self-healing services for auto-boot VM management
# - Comprehensive testing sweeps (pre/post installation)
# - Cleanup and debloating processes
# - Timestamped JSON configuration tracking
```

Key principles:
- **USB-first**: All files, configs, and dependencies stay on USB
- **No symlinks**: Everything is finite, atomic, and whole
- **No host modifications**: Service files never copied to host
- **Portable**: Works on any host with systemd
- **Isolated**: USB environment is self-contained

### I need to manage disk images

```bash
# Manage disk images interactively
sudo bash scripts/usb-manager.sh --image-manage /mnt/usb

# Create new disk image
sudo bash scripts/usb-manager.sh --image-create /mnt/usb

# Mount a disk image
sudo bash scripts/usb-manager.sh --image-mount /path/to/image.qcow2

# Convert image format
sudo bash scripts/usb-manager.sh --image-convert /path/to/image.img

# Inspect image
sudo bash scripts/usb-manager.sh --image-inspect /path/to/image.img
```

Supported formats: raw (img), QCOW2, VDI (VirtualBox), VMDK (VMware), ISO


## Automount System

Automatic USB device detection and mounting via udev rules. Devices mount to `/mnt/usb/<label-or-device>/` with predictable paths.

### Setup

```bash
# Install automount (requires root)
sudo bash assets/usb-automount/setup-usb-automount.sh

# USB devices will now auto-mount to /mnt/usb/<device-name>/
```

### Commands

| Command | Description |
|---|---|
| `usb-mount.sh add <device>` | Mount a device (e.g., sdb1) |
| `usb-mount.sh remove <device>` | Unmount a device |
| `usb-mount.sh list` | List mounted USB devices |
| `usb-mount.sh mount-all` | Mount all connected USB devices |
| `usb-mount.sh unmount-all` | Unmount all USB devices |
| `usb-mount.sh status` | Show mount status and log file |

### Supported Filesystems

| Filesystem | Mount Options |
|---|---|
| ext4, ext3, ext2 | defaults |
| exfat | utf8, uid=$UID, gid=$GID, shortname=mixed, nodev, nosuid |
| ntfs | exfat options + permissions (ntfs-3g if available) |
| vfat | exfat options + dmask/fmask |
| btrfs, xfs | defaults |
| iso9660, udf | exfat options |

### Safety Features

- **No formatting** — automount never modifies device data
- **Read-only corruption check** — detects issues without writing
- **Lock file protection** — prevents concurrent mount operations
- **Log file** — `/var/log/usb-mount.log` records all operations
- **User-writable fallback** — works without root for listing/status

### Uninstall

```bash
sudo bash assets/usb-automount/teardown-usb-automount.sh
```

## USB State Management

Persistent device tracking across reboots via JSON state file. Tracks device UUIDs, labels, filesystems, mount history, and custom tags.

### State File Location

- **User**: `~/.usb-state.json`
- **System**: `/var/lib/usb-state.json` (if writable)

### State Schema

```json
{
  "version": "1.0",
  "last_updated": "ISO8601",
  "devices": {
    "<uuid>": {
      "device": "/dev/sdb1",
      "uuid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "label": "MY_DRIVE",
      "filesystem": "exfat",
      "size_bytes": 32212254720,
      "model": "SanDisk Ultra",
      "vendor": "SanDisk",
      "first_seen": "ISO8601",
      "last_seen": "ISO8601",
      "last_mount_point": "/mnt/usb/my-drive",
      "mount_count": 42,
      "health_status": "healthy|warning|critical|unknown",
      "tags": ["portable", "backup"]
    }
  },
  "mount_history": [
    {
      "timestamp": "ISO8601",
      "event": "mount|unmount|error|health_check|scan",
      "device_uuid": "xxx",
      "details": {}
    }
  ]
}
```

### Commands

```bash
# List all tracked devices
python3 scripts/usb_state_manager.py --list

# List with JSON output
python3 scripts/usb_state_manager.py --list --json

# Scan for USB devices and update state
python3 scripts/usb_state_manager.py --scan

# Show device history
python3 scripts/usb_state_manager.py --history <uuid>

# Add tags to device
python3 scripts/usb_state_manager.py --tag <uuid> --add "backup" "portable"

# Remove tags
python3 scripts/usb_state_manager.py --tag <uuid> --remove "backup"

# Remove device from tracking
python3 scripts/usb_state_manager.py --remove <uuid>

# Export state to file
python3 scripts/usb_state_manager.py --export state-backup.json

# Import state from file
python3 scripts/usb_state_manager.py --import state-backup.json

# Dry-run mode (no changes written)
python3 scripts/usb_state_manager.py --scan --dry-run
```

### Use Cases

| Use Case | Command |
|---|---|
| Find a specific drive | `--list` then grep for label/model |
| Track drive usage | `--history <uuid>` shows mount count and timestamps |
| Mark drives by purpose | `--tag <uuid> --add "backup"` |
| Backup state before reinstall | `--export state-backup.json` |
| Restore state on new system | `--import state-backup.json` |
| Detect newly inserted drives | `--scan` updates last_seen timestamps |

## Script Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/usb-manager.sh` | Main interactive USB management tool | `sudo bash scripts/usb-manager.sh` |
| `scripts/usb_state_manager.py` | Persistent USB device state tracking | `python3 scripts/usb_state_manager.py --scan` |


## Key References

- **Ventoy Setup**: [references/ventoy-setup.md](references/ventoy-setup.md)
- **mkusb Guide**: [references/mkusb-guide.md](references/mkusb-guide.md)
- **Hidden USB Recovery**: [references/hidden-usb.md](references/hidden-usb.md)
- **Filesystem Reference**: [references/filesystem-guide.md](references/filesystem-guide.md)
- **Boot Guide**: [references/boot-guide.md](references/boot-guide.md)
- **GUI/Terminal Access**: [references/gui-terminal.md](references/gui-terminal.md)
- **Docker on USB**: [references/docker-usb.md](references/docker-usb.md)

- **USB Creation**: [references/usb-creation-guide.md](references/usb-creation-guide.md)
- **Alias System**: [references/alias-system.md](references/alias-system.md)
- **Agent Isolation**: [references/agent-isolation.md](references/agent-isolation.md)
- **Container Integration**: [references/container-integration.md](references/container-integration.md)
- **Cross-OS Guide**: [references/cross-os-guide.md](references/cross-os-guide.md)
- **Backup & Restore**: [references/backup-restore.md](references/backup-restore.md)
- **Error Handling**: [references/error-handling.md](references/error-handling.md)
- **Free-First Strategy**: [references/free-first-strategy.md](references/free-first-strategy.md)

## Architecture

```
scripts/
  usb-manager.sh          # Main entry point (interactive menu + all operations)
  usb_state_manager.py    # Persistent USB device state tracking
assets/
  usb-automount/
    usb-mount.sh          # Core mount/unmount logic
    udev-usb-automount.rules  # Kernel-level device detection
    usb-automount.service # Systemd service for boot-time mount
    setup-usb-automount.sh    # Installation script
    teardown-usb-automount.sh # Clean uninstall
references/
  ventoy-setup.md          # Ventoy multi-ISO boot setup guide
  mkusb-guide.md           # mkusb live/persistent USB creation guide
  hidden-usb.md            # Hidden and unrecognized USB recovery
  filesystem-guide.md      # Filesystem selection and management reference
  boot-guide.md            # BIOS/UEFI USB boot configuration guide
  gui-terminal.md          # GUI and terminal access methods
  docker-usb.md            # Docker container/volume management on USB
```

### Default Layout

/dev/sdX
├── sdX1  exfat   Ventoy        (ISO + config)
│   ├── ubuntu-24.04.4-desktop-amd64.iso
│   ├── ventoy/ventoy.json
│   └── persistence/ubuntu-persistence.dat
└── sdX2  vfat    VTOYEFI       (EFI boot)

### Multi-Agent Layout

├── sdX1  exfat   Ventoy
│   ├── persistence/ubuntu-persistence.dat
│   ├── global-deps.dat          (read-only shared libs)
│   └── agents/
│       ├── alpha-home.dat       (isolated per-agent)
│       ├── beta-home.dat
│       └── gamma-home.dat
└── sdX2  vfat    VTOYEFI

## Sources

- **Docker**: https://docs.docker.com/ - Container and volume management
- **Ventoy**: https://www.ventoy.net/en/doc_start.html - Multi-ISO boot setup
- **mkusb**: https://help.ubuntu.com/community/mkusb - Live/persistent USB creation
- **systemd**: https://systemd.io/ - Service management on USB

- Ventoy: https://www.ventoy.net
- QEMU: https://www.qemu.org
- Docker: https://www.docker.com
- LXC/LXD: https://linuxcontainers.org
- Ubuntu ISO: https://ubuntu.com/download
- ext4fuse (macOS): https://github.com/gerard/ext4fuse
- macFUSE: https://osxfuse.github.io
- Ext2Fsd (Windows): https://www.ext2fsd.com

## Safety Features

- Pre-operation safety scans check for mounted partitions, write protection, and device usage
- Multiple confirmation prompts for destructive operations (format, partition table, clone)
- All operations logged to `/tmp/usb-manager.log`
- Automatic dependency detection and installation prompts
- Write-protected device detection before write operations



## Workflow

### Step 1: Installation

```bash
# Install dependencies if needed
```

### Step 2: Configuration

```bash
# Configure the skill
```

### Step 3: Usage

```bash
# Use the skill
python3 scripts/main.py
```

### Step 4: Validation

```bash
# Validate the skill
python3 scripts/validate.py
```



## Free-First Strategy

| Tier | Cost | Stack |
|------|------|-------|
| **Tier 0** | $0/mo | Python 3.8+ (all scripts use stdlib only) |
| **Tier 1** | $0-5/mo | + CI/CD for automated validation |
| **Tier 2** | $5-20/mo | + Hosted skill registry for team distribution |

The entire core toolchain is permanently $0.


|---|---|---|
| **Tier 0** | $0/mo | Ventoy + ext4 + QEMU + Docker + rsync |
| **Tier 1** | $0-5/mo | + rclone cloud sync + GitHub Actions |
| **Tier 2** | $5-20/mo | + Backblaze B2 + Cloudflare + monitoring |

Core toolchain is permanently $0. See [references/free-first-strategy.md](references/free-first-strategy.md).

## Enforced Output Statistics

Every script produces structured output on completion:

```json
{
  "operation": "script_name",
  "timestamp": "ISO8601",
  "status": "success | failed",
  "skill_name": "the-skill-name",
  "details": {},
  "cost": {"tier": 0, "amount_usd": 0.0, "service": "local"}
}
```


Every operation produces structured output:

    "operation": "usb_create | agent_create | backup | restore",
    "device": "/dev/sdX",
    "details": {
        "persistence_size": "20G",
        "agents_created": ["alpha", "beta"],
        "backup_size": "4.2G"
    },
    "cost": {
        "tier": 0,
        "amount_usd": 0.0,
        "service": "local"

### Operation Metrics

| Operation | Time | Disk I/O | Network |
|---|---|---|---|
| USB Creation | 5-10 min | High | None |
| Agent Setup | 2-5 min | Medium | None |
| Full Backup | 10-30 min | High | None |
| Cloud Backup | 15-60 min | Medium | High |
| Restore | 10-30 min | High | None |


## Enhancement Hooks

| Skill | Enhancement | When to Add |
|-------|-------------|-------------|
| `skill-creator` | Basic skill creation | When creating simple skills |
| `skill-creator-pro` | Enterprise upgrade | When upgrading to enterprise |
| `html-report` | Visual validation dashboard | When auditing many skills |
| `xlsx` | Export validation results | When tracking skill quality metrics |


## Error Handling

| Error | Response |
|-------|----------|
| Device not detected | Check USB connection, run `dmesg | tail -20`, try different port |
| Mount fails | Check filesystem type, install missing drivers, review logs |
| Format fails | Verify device is not write-protected, check available space |
| Ventoy install fails | Ensure Ventoy is downloaded, check device is not mounted |
| mkusb fails | Verify ISO integrity, check device size meets requirements |
| Persistence not found | Check for .dat files in persistence directory |
| Docker not installed | Install Docker or use portable binaries on USB |
| Image mount fails | Check image format, install qemu-utils for QCOW2 |

## Connection & Access Modes

| Mode | Command | Use Case |
|---|---|---|
| **Direct Boot** | Boot from USB | Portable computing |
| **QEMU VM** | `qemu-system-x86_64 -m 4G -drive file=/dev/sdX,format=raw -boot c` | Host-side VM |
| **QEMU+KVM** | `qemu-system-x86_64 -enable-kvm -m 4G -drive file=/dev/sdX,format=raw,if=virtio -boot c` | Fast VM (requires VT-x) |
| **SSH** | `ssh user@usb-ip` | Headless/remote |
| **VNC** | `qemu-system-x86_64 -display vnc=:1` | Graphical remote |
| **Chroot** | `sudo chroot /mnt/usb /bin/bash` | Recovery/repair |
| **Docker** | `docker run -it -v /media/usb:/workspace ubuntu:24.04` | App isolation |
| **LXC** | `lxc launch ubuntu:24.04 agent-workspace` | System containers |

See [references/usb-creation-guide.md](references/usb-creation-guide.md) for detailed setup.


## Alias System

Install aliases for streamlined USB management:

```bash
cat scripts/usb-aliases.sh >> ~/.bashrc && source ~/.bashrc
```

| Alias | Command |
|---|---|
| `usb-list` | `lsblk -f /dev/sd*` |
| `usb-mount` | `sudo mount /dev/sdX1 /media/ventoy-usb` |
| `usb-unmount` | `sudo umount /dev/sdX*` |
| `usb-vm-boot` | `sudo qemu-system-x86_64 -m 4G -drive file=/dev/sdX,format=raw -boot c -display gtk` |
| `usb-backup` | `sudo dd if=/dev/sdX of=~/usb-backup.img bs=4M status=progress` |
| `usb-agent-create` | `python3 scripts/agent-manager.py create` |

See [references/alias-system.md](references/alias-system.md).


## Agent Isolation

### Create Isolated Agent Workspaces

```bash
# Create agents with isolated storage
python3 scripts/agent-manager.py create --name alpha --size 5G
python3 scripts/agent-manager.py create --name beta --size 5G

# Enter agent workspace
python3 scripts/agent-manager.py enter --name alpha

# Backup/restore agents
python3 scripts/agent-manager.py backup --name alpha --dest ~/backups/
python3 scripts/agent-manager.py restore --name alpha --src ~/backups/alpha.tar.gz

# Clone agents
python3 scripts/agent-manager.py clone --source alpha --dest gamma
```

### Global Read-Only Dependencies

```bash
# Create shared read-only partition
sudo dd if=/dev/zero of=global-deps.dat bs=1M count=10000
sudo mkfs.ext4 -F -L global-deps global-deps.dat
sudo tune2fs -O ro global-deps.dat

# Mount as read-only in agent sessions
sudo mount -o ro,loop global-deps.dat /mnt/global
```

See [references/agent-isolation.md](references/agent-isolation.md).


## Container Integration

### Docker

```bash
# Install on persistent USB
sudo apt install docker.io -y
sudo usermod -aG docker $USER

# Run isolated containers
docker run -it --rm -v /media/usb/workspace:/workspace ubuntu:24.04 bash

# With GUI forwarding
docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix ubuntu:24.04 bash
```

### LXC/LXD

```bash
sudo snap install lxd && sudo lxd init
lxc launch ubuntu:24.04 agent-alpha
lxc exec agent-alpha bash
```

See [references/container-integration.md](references/container-integration.md).


## Cross-OS Support

| OS | ext4 Access | Boot | Notes |
|---|---|---|---|
| **Linux** | Native | F12/F2/DEL | Full support |
| **Windows** | Ext2Fsd/WSL2 | F12/F2/DEL | Disable Fast Startup |
| **macOS** | macFUSE+ext4fuse | Hold Option | May need SIP disabled |

See [references/cross-os-guide.md](references/cross-os-guide.md).


## Backup & Restore

```bash
# Full backup
sudo dd if=/dev/sdX of=~/usb-backup-$(date +%Y%m%d).img.gz bs=4M status=progress | gzip

# Selective backup
python3 scripts/pipeline.py backup --usb /dev/sdX --persistence --agents

# Restore
gunzip -c ~/usb-backup.img.gz | sudo dd of=/dev/sdX bs=4M status=progress
```

See [references/backup-restore.md](references/backup-restore.md).


## Troubleshooting

| Issue | Solution |
|---|---|
| USB not detected | `sudo partprobe` or unplug/replug |
| Ventoy tools fail | `sudo cp /tmp/ventoy-1.1.12/tool/x86_64/* /usr/sbin/` |
| Black screen QEMU | Use `-vga std` instead of `-vga virtio` |
| No persistence | Verify `casper-rw` label and `persistent` boot option |
| Windows can't read | Create ExFAT exchange partition |
| KVM unavailable | Use QEMU without `-enable-kvm` |

See [references/error-handling.md](references/error-handling.md).


## Scripts

| Script | Purpose |
|---|---|
| `scripts/setup.py` | Automated USB creation with persistence |
| `scripts/agent-manager.py` | Agent workspace management |
| `scripts/pipeline.py` | Orchestrated workflow automation |


## Workflow: Create Portable USB

### Step 1: Preparation

- Identify USB device: `lsblk -f`
- Download Ubuntu ISO
- Verify ISO integrity: `sha256sum -c SHA256SUMS`

### Step 2: Install Ventoy

```bash
wget https://github.com/ventoy/Ventoy/releases/download/v1.1.12/ventoy-1.1.12-linux.tar.gz
tar -xf ventoy-1.1.12-linux.tar.gz -C /tmp
cd /tmp/ventoy-1.1.12 && sudo ./Ventoy2Disk.sh -i /dev/sdX
```

### Step 3: Configure Persistence

```bash
sudo mount /dev/sdX1 /media/ventoy-usb
sudo cp ~/Downloads/ubuntu-24.04.4-desktop-amd64.iso /media/ventoy-usb/
sudo dd if=/dev/zero of=/media/ventoy-usb/persistence/ubuntu-persistence.dat bs=1M count=20000
sudo mkfs.ext4 -F -L casper-rw /media/ventoy-usb/persistence/ubuntu-persistence.dat
```

### Step 4: Create Configuration

```bash
sudo tee /media/ventoy-usb/ventoy/ventoy.json > /dev/null << 'EOF'
{
    "persistence": [{
        "image": "/ubuntu-24.04.4-desktop-amd64.iso",
        "backend": "/persistence/ubuntu-persistence.dat"
    }]
}
EOF
sudo umount /media/ventoy-usb
```

### Step 5: Verify and Test

- Boot from USB on target machine
- Verify persistence works
- Test reboot and data retention


## Workflow: Deploy Agent Isolation

### Step 1: Create Agent Workspaces

```bash
python3 scripts/agent-manager.py create --name alpha --size 5G
python3 scripts/agent-manager.py create --name beta --size 5G
```

### Step 2: Configure Isolation

- Each agent gets isolated ext4 partition
- Shared read-only dependencies via global-deps.dat
- Agent-specific home directories

### Step 3: Verify Isolation

```bash
python3 scripts/agent-manager.py health --name alpha
python3 scripts/agent-manager.py list
```
