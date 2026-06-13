---
name: portable-linux-usb
description: 'Create, manage, and extend portable Linux USB environments with Ventoy,
  persistence, agent isolation, container integration, and multi-OS support. Covers
  USB creation, alias systems, partition-based agent isolation, Docker/LXC integration,
  QEMU/KVM virtualization, SSH/headless/GUI access, cross-platform mounting, backup/restore,
  and multi-agent deployments. Use when: creating portable Linux USB, setting up Ventoy
  persistent drive, building agent isolation environments, creating bootable USB with
  persistence, managing portable Linux systems, configuring USB-based agent workspaces.'
license: MIT
version: 0.0.2
---
# Portable Linux USB

Complete lifecycle management for portable Linux USB environments — from raw USB drive to enterprise multi-agent isolated deployments.

## Provider Compatibility

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

## Free-First Strategy

| Tier | Cost | Stack |
|---|---|---|
| **Tier 0** | $0/mo | Ventoy + ext4 + QEMU + Docker + rsync |
| **Tier 1** | $0-5/mo | + rclone cloud sync + GitHub Actions |
| **Tier 2** | $5-20/mo | + Backblaze B2 + Cloudflare + monitoring |

Core toolchain is permanently $0. See [references/free-first-strategy.md](references/free-first-strategy.md).

## Quick Start

### Basic Persistent USB

```bash
# 1. Download Ventoy
wget https://github.com/ventoy/Ventoy/releases/download/v1.1.12/ventoy-1.1.12-linux.tar.gz
tar -xf ventoy-1.1.12-linux.tar.gz -C /tmp

# 2. Install to USB (WARNING: wipes drive)
cd /tmp/ventoy-1.1.12 && sudo ./Ventoy2Disk.sh -i /dev/sdX

# 3. Copy ISO and configure persistence
sudo mount /dev/sdX1 /media/ventoy-usb
sudo cp ${HOME}/Downloads/ubuntu-24.04.4-desktop-amd64.iso /media/ventoy-usb/
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
```

### Automated Setup

```bash
python3 scripts/setup.py --device /dev/sdX --iso ${HOME}/Downloads/ubuntu-24.04.4-desktop-amd64.iso --persistence 20G
```

## Architecture

### Default Layout

```
/dev/sdX
├── sdX1  exfat   Ventoy        (ISO + config)
│   ├── ubuntu-24.04.4-desktop-amd64.iso
│   ├── ventoy/ventoy.json
│   └── persistence/ubuntu-persistence.dat
└── sdX2  vfat    VTOYEFI       (EFI boot)
```

### Multi-Agent Layout

```
/dev/sdX
├── sdX1  exfat   Ventoy
│   ├── ubuntu-24.04.4-desktop-amd64.iso
│   ├── ventoy/ventoy.json
│   ├── persistence/ubuntu-persistence.dat
│   ├── global-deps.dat          (read-only shared libs)
│   └── agents/
│       ├── alpha-home.dat       (isolated per-agent)
│       ├── beta-home.dat
│       └── gamma-home.dat
└── sdX2  vfat    VTOYEFI
```

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
cat scripts/usb-aliases.sh >> ${HOME}/.bashrc && source ${HOME}/.bashrc
```

| Alias | Command |
|---|---|
| `usb-list` | `lsblk -f /dev/sd*` |
| `usb-mount` | `sudo mount /dev/sdX1 /media/ventoy-usb` |
| `usb-unmount` | `sudo umount /dev/sdX*` |
| `usb-vm-boot` | `sudo qemu-system-x86_64 -m 4G -drive file=/dev/sdX,format=raw -boot c -display gtk` |
| `usb-backup` | `sudo dd if=/dev/sdX of=${HOME}/usb-backup.img bs=4M status=progress` |
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
python3 scripts/agent-manager.py backup --name alpha --dest ${HOME}/backups/
python3 scripts/agent-manager.py restore --name alpha --src ${HOME}/backups/alpha.tar.gz

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
sudo dd if=/dev/sdX of=${HOME}/usb-backup-$(date +%Y%m%d).img.gz bs=4M status=progress | gzip

# Selective backup
python3 scripts/pipeline.py backup --usb /dev/sdX --persistence --agents

# Restore
gunzip -c ${HOME}/usb-backup.img.gz | sudo dd of=/dev/sdX bs=4M status=progress
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
sudo cp ${HOME}/Downloads/ubuntu-24.04.4-desktop-amd64.iso /media/ventoy-usb/
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

## Enforced Output Statistics

Every operation produces structured output:

```json
{
    "operation": "usb_create | agent_create | backup | restore",
    "timestamp": "ISO8601",
    "status": "success | failed",
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
    }
}
```

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

## Sources

| Service | Purpose | Free Tier | Cost (Paid) |
|---------|---------|-----------|-------------|
| Ventoy | Multi-ISO USB bootloader | Full | — |
| Docker | Container runtime | Full (Docker Desktop: individual free) | $5-24/mo (team) |
| QEMU/KVM | Virtualization | Full | — |
| GitHub Releases | Ventoy binary downloads | Full | — |

## Key References

- **USB Creation**: [references/usb-creation-guide.md](references/usb-creation-guide.md)
- **Alias System**: [references/alias-system.md](references/alias-system.md)
- **Agent Isolation**: [references/agent-isolation.md](references/agent-isolation.md)
- **Container Integration**: [references/container-integration.md](references/container-integration.md)
- **Cross-OS Guide**: [references/cross-os-guide.md](references/cross-os-guide.md)
- **Backup & Restore**: [references/backup-restore.md](references/backup-restore.md)
- **Error Handling**: [references/error-handling.md](references/error-handling.md)
- **Free-First Strategy**: [references/free-first-strategy.md](references/free-first-strategy.md)
