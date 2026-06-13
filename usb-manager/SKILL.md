---
name: usb-manager
description: "Comprehensive USB drive management. Handles detection, mounting, partitioning, formatting, Ventoy multi-boot setup with persistence, mkusb live/persistent USB creation, hidden device recovery, unrecognized drive troubleshooting, boot configuration, GUI/terminal access, Docker container/volume management, and disk image management. Use when managing any USB storage device."
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
version: 0.0.2
---

# USB Manager

Comprehensive USB drive management tool. Handles detection, mounting, partitioning, formatting, Ventoy multi-boot setup with persistence, mkusb live/persistent USB creation, hidden device recovery, unrecognized drive troubleshooting, boot configuration, GUI/terminal access, Docker container/volume management, and disk image management.

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

## Provider Compatibility

| Provider | Compatibility | Notes |
|----------|---------------|-------|
| Claude (Anthropic) | Full | MCP servers, tool use |
| OpenAI / ChatGPT | Full | Function calling, Actions |
| Mistral / Le Chat | Full | Tool calling, script execution |
| Gemini (Google) | Full | Extensions, Vertex AI |
| Any LLM + tools | Full | Scripts are plain Bash, provider-independent |

## Quick Start

```bash
# Interactive mode (recommended)
sudo bash scripts/usb-manager.sh

# List all USB devices
lsblk -o NAME,SIZE,TYPE,TRAN,MODEL | grep -i usb

# List all block devices including hidden
lsblk -ndo NAME,SIZE,TYPE,TRAN | grep -E 'disk|usb'
```

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

## Script Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/usb-manager.sh` | Main interactive USB management tool | `sudo bash scripts/usb-manager.sh` |

## Key References

- **Ventoy Setup**: [references/ventoy-setup.md](references/ventoy-setup.md)
- **mkusb Guide**: [references/mkusb-guide.md](references/mkusb-guide.md)
- **Hidden USB Recovery**: [references/hidden-usb.md](references/hidden-usb.md)
- **Filesystem Reference**: [references/filesystem-guide.md](references/filesystem-guide.md)
- **Boot Guide**: [references/boot-guide.md](references/boot-guide.md)
- **GUI/Terminal Access**: [references/gui-terminal.md](references/gui-terminal.md)
- **Docker on USB**: [references/docker-usb.md](references/docker-usb.md)

## Architecture

```
scripts/
  usb-manager.sh          # Main entry point (interactive menu + all operations)
references/
  ventoy-setup.md          # Ventoy multi-ISO boot setup guide
  mkusb-guide.md           # mkusb live/persistent USB creation guide
  hidden-usb.md            # Hidden and unrecognized USB recovery
  filesystem-guide.md      # Filesystem selection and management reference
  boot-guide.md            # BIOS/UEFI USB boot configuration guide
  gui-terminal.md          # GUI and terminal access methods
  docker-usb.md            # Docker container/volume management on USB
```

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
| mkusb | Live/persistent USB creator | Full | — |
| Docker | Container runtime | Full (Docker Desktop: individual free) | $5-24/mo (team) |
| qemu-utils | Disk image conversion | Full | — |

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