# USB Creation Guide
## Table of Contents

- [Ventoy Installation](#ventoy-installation)
- [Persistence Management](#persistence-management)
- [ISO Management](#iso-management)


Complete reference for creating portable Linux USB drives from scratch.

## Ventoy Installation

### Prerequisites Check

```bash
# Verify USB is detected:
lsblk -f

# Check available space:
df -h

# Verify Ventoy dependencies:
which parted mkfs.vfat mkfs.ext4 dd hexdump
```

### Installation Options

**Interactive (recommended):**
```bash
cd /tmp/ventoy-1.1.12
sudo ./Ventoy2Disk.sh -i /dev/sdX
```

**Automatic (no prompts):**
```bash
sudo ./Ventoy2Disk.sh -iI /dev/sdX
```

**Force install (overwrite existing Ventoy):**
```bash
sudo ./Ventoy2Disk.sh -iI /dev/sdX
```

### Ventoy Configuration

#### Basic Persistence

```json
{
    "persistence": [
        {
            "image": "/ubuntu-24.04.4-desktop-amd64.iso",
            "backend": "/persistence/ubuntu-persistence.dat"
        }
    ]
}
```

#### Multiple ISOs with Persistence

```json
{
    "persistence": [
        {
            "image": "/ubuntu-24.04.4-desktop-amd64.iso",
            "backend": "/persistence/ubuntu-persistence.dat"
        },
        {
            "image": "/ubuntu-22.04.4-desktop-amd64.iso",
            "backend": "/persistence/ubuntu22-persistence.dat"
        }
    ]
}
```

#### Agent Isolation Config

```json
{
    "persistence": [
        {
            "image": "/ubuntu-24.04.4-desktop-amd64.iso",
            "backend": "/persistence/ubuntu-persistence.dat"
        }
    ],
    "agent_isolation": {
        "alpha": {"backend": "/agents/alpha-home.dat"},
        "beta": {"backend": "/agents/beta-home.dat"}
    }
}
```

## Persistence Management

### Creating Persistence Files

```bash
# Create 20GB persistence file:
sudo dd if=/dev/zero of=persistence/ubuntu-persistence.dat \
    bs=1M count=20000 status=progress
sudo mkfs.ext4 -F -L casper-rw persistence/ubuntu-persistence.dat
```

### Expanding Persistence

```bash
# Resize the file:
sudo dd if=/dev/zero of=new-persistence.dat bs=1M count=40000 status=progress
sudo mkfs.ext4 -F -L casper-rw new-persistence.dat

# Copy existing data:
sudo mkdir -p /tmp/old /tmp/new
sudo mount -o loop ubuntu-persistence.dat /tmp/old
sudo mount -o loop new-persistence.dat /tmp/new
sudo rsync -av ${TMPDIR:-/tmp}/ ${TMPDIR:-/tmp}/
sudo umount /tmp/old /tmp/new

# Replace:
mv new-persistence.dat persistence/ubuntu-persistence.dat
```

### Persistence Backup

```bash
# Backup persistence data:
sudo dd if=/dev/sdX5 of=${HOME}/persistence-backup.dat bs=4M status=progress

# Restore persistence:
sudo dd if=${HOME}/persistence-backup.dat of=/dev/sdX5 bs=4M status=progress
```

## ISO Management

### Adding ISOs

```bash
# Copy to USB:
sudo cp ${HOME}/Downloads/*.iso /media/ventoy-usb/

# Verify:
ls -lh /media/ventoy-usb/*.iso
```

### Supported ISO Types

| Type | Boot | Persistence | Notes |
|---|---|---|---|
| Ubuntu Desktop | Yes | Yes | Full support |
| Ubuntu Server | Yes | Limited | No GUI |
| Kubuntu/Xubuntu | Yes | Yes | Alternative desktops |
| Debian | Yes | Yes | Different persistence syntax |
| Fedora | Yes | Limited | Different overlay system |
| Arch Linux | Yes | Manual | Manual persistence setup |
| Windows | Yes | No | Not applicable |

### ISO Verification

```bash
# Verify ISO integrity:
sha256sum -c SHA256SUMS

# Check ISO type:
file ubuntu-24.04.4-desktop-amd64.iso
```
