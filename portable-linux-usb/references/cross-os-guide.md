# Cross-OS Guide
## Table of Contents

- [Windows](#windows)
- [macOS](#macos)
- [Linux](#linux)
- [Network Environments](#network-environments)
- [Multi-Platform USB Configuration](#multi-platform-usb-configuration)
- [Platform-Specific Troubleshooting](#platform-specific-troubleshooting)
- [Remote Access Setup](#remote-access-setup)


Platform-specific instructions for using portable Linux USB on Windows, macOS, and network environments.

## Windows

### Reading ext4 Partitions

Windows cannot read ext4 natively. Solutions:

#### Option 1: Ext2Fsd (Recommended)

1. Download Ext2Fsd from https://www.ext2fsd.com/
2. Install and run Ext2 Volume Manager
3. Mount ext4 partitions as drive letters
4. Full read/write access to ext4

#### Option 2: WSL2 (Windows Subsystem for Linux)

```powershell
# In PowerShell (Admin):
wsl --install

# Restart computer

# Mount USB in WSL2:
wsl --mount \.\PHYSICALDRIVE1 --partition 1 -t ext4

# Access from WSL:
ls /mnt/wsl/PHYSICALDRIVE1p1
```

#### Option 3: DiskInternals Linux Reader

1. Download from https://www.diskinternals.com/linux-reader/
2. Install and run
3. Browse ext4 partitions (read-only)

### Booting from USB

1. Insert USB
2. Restart PC
3. Press boot menu key (F12, F2, DEL, ESC - varies by manufacturer)
4. Select USB device from boot menu
5. Select Ubuntu from Ventoy menu

### UEFI vs BIOS

| Mode | Boot Key | Notes |
|---|---|---|
| UEFI | F12, F2, DEL | Modern systems, secure boot |
| Legacy BIOS | F12, F2, DEL | Older systems, CSM enabled |

### Secure Boot

If secure boot causes issues:
1. Enter BIOS/UEFI setup
2. Disable Secure Boot
3. Save and exit
4. Boot from USB

### Windows Performance Tips

```powershell
# Disable Windows Fast Startup (prevents USB issues):
powercfg /h off

# Disable hibernation:
powercfg -hibernate off

# Optimize USB power settings:
# Device Manager > USB Root Hub > Properties > Power Management
# Uncheck "Allow the computer to turn off this device to save power"
```

## macOS

### Reading ext4 Partitions

#### Option 1: macFUSE + ext4fuse

```bash
# Install Homebrew:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install macFUSE:
brew install --cask macfuse

# Install ext4fuse:
brew install ext4fuse

# Mount ext4 partition:
sudo mkdir /Volumes/ext4
sudo ext4fuse /dev/disk2s1 /Volumes/ext4 -o allow_other

# Unmount:
sudo umount /Volumes/ext4
```

#### Option 2: Paragon ExtFS

1. Download from https://www.paragon-software.com/home/linuxfs-mac/
2. Install and run
3. Mount ext4 partitions with full read/write

#### Option 3: Virtual Machine

```bash
# Use UTM (free) or VMware Fusion:
# 1. Create Linux VM
# 2. Pass through USB device
# 3. Mount ext4 from within VM
```

### Booting from USB on Mac

1. Insert USB
2. Restart Mac
3. Hold Option (⌥) key during boot
4. Select EFI Boot or USB device
5. Select Ubuntu from Ventoy menu

### Mac-Specific Issues

```bash
# Disable System Integrity Protection (if needed):
# 1. Restart Mac
# 2. Hold Command+R to enter Recovery
# 3. Open Terminal
# 4. Run: csrutil disable
# 5. Restart

# Re-enable after USB session:
# 1. Enter Recovery
# 2. Run: csrutil enable
```

### macOS USB Performance

```bash
# Check USB speed:
system_profiler SPUSBDataType

# Monitor USB activity:
sudo fs_usage -f filesys | grep -i usb
```

## Linux

### Native Support

Linux has native ext4 support. No additional software needed.

```bash
# Mount USB:
sudo mount /dev/sdX1 /mnt/usb

# Unmount:
sudo umount /mnt/usb

# Check filesystem:
sudo e2fsck -f /dev/sdX1

# Resize filesystem:
sudo resize2fs /dev/sdX1
```

### Multiple Linux Systems

```bash
# Boot from USB on any Linux system:
# 1. Insert USB
# 2. Restart
# 3. Press boot menu key (varies by distribution)
# 4. Select USB
# 5. Choose Ubuntu from Ventoy

# Or add to GRUB:
sudo nano /etc/grub.d/40_custom

# Add:
menuentry "Ubuntu from USB" {
    insmod part_msdos
    insmod ext2
    set root='(hd0,msdos1)'
    linux /casper/vmlinuz boot=casper persistent
    initrd /casper/initrd
}

sudo update-grub
```

### Network Boot (PXE)

```bash
# Set up PXE boot server:
sudo apt install tftpd-hpa syslinux pxelinux -y

# Configure TFTP:
sudo nano /etc/default/tftpd-hpa
# TFTP_DIRECTORY="/srv/tftp"

# Copy boot files:
sudo mkdir -p /srv/tftp/pxelinux.cfg
sudo cp /usr/lib/PXELINUX/pxelinux.0 /srv/tftp/
sudo cp /usr/lib/syslinux/modules/bios/*.c32 /srv/tftp/
sudo rsync -av /media/ventoy-usb/ /srv/tftp/

# Create default menu:
sudo tee /srv/tftp/pxelinux.cfg/default << 'EOF'
DEFAULTvesamenu.c32
PROMPT0
TIMEOUT300
MENU LABEL Boot from USB

LABEL ubuntu
MENU LABEL Ubuntu from USB
KERNEL /casper/vmlinuz
APPEND initrd=/casper/initrd boot=casper persistent
EOF

# Configure DHCP:
sudo nano /etc/dhcp/dhcpd.conf
# Add:
# next-server <TFTP-IP>;
# filename "pxelinux.0";

# Start services:
sudo systemctl restart tftpd-hpa
sudo systemctl restart dhcpd
```

## Network Environments

### iSCSI (Network Block Device)

```bash
# Server (USB host):
sudo apt install targetcli -y
sudo targetcli

# Create backstores:
/backstores/block create usb_storage /dev/sdX

# Create iSCSI target:
/iscsi create iqn.2024-01.com.usb:target

# Create LUN:
/iscsi/iqn.2024-01.com.usb:target/tpg1/luns create /backstores/block/usb_storage

# Create ACL:
/iscsi/iqn.2024-01.com.usb:target/tpg1/acls create iqn.2024-01.com.usb:client

# Exit and save:
exit

# Client (connect to USB):
sudo apt install open-iscsi -y

# Discover target:
sudo iscsiadm -m discovery -t sendtargets -p <SERVER-IP>

# Login:
sudo iscsiadm -m node --login

# USB appears as /dev/sdX on client
```

### SSH Tunneling

```bash
# Forward USB to remote machine:
# On USB system:
sudo apt install openssh-server -y
sudo systemctl enable ssh

# On client:
ssh -L 2222:localhost:22 user@usb-system.local

# Connect via tunnel:
ssh -p 2222 user@localhost
```

### VNC (Graphical Remote Access)

```bash
# On USB system:
sudo apt install tightvncserver -y
vncserver :1 -geometry 1920x1080 -depth 24

# On client:
vncviewer usb-system.local:5901
```

### RDP (Windows Remote Desktop)

```bash
# On USB system:
sudo apt install xrdp -y
sudo systemctl enable xrdp
sudo systemctl start xrdp

# On Windows:
# Open Remote Desktop Connection
# Enter: usb-system.local
# Login with USB credentials
```

## Multi-Platform USB Configuration

### Partition Scheme for Multi-OS Access

```bash
# Create USB with multiple partitions:
sudo parted /dev/sdX --script mklabel gpt

# Ventoy partition (exfat - readable by all):
sudo parted /dev/sdX --script mkpart primary fat32 1MiB 10GiB

# Persistence partition (ext4 - Linux only):
sudo parted /dev/sdX --script mkpart primary ext4 10GiB 30GiB

# Exchange partition (exfat - readable by all):
sudo parted /dev/sdX --script mkpart primary fat32 30GiB 100%

# Format partitions:
sudo mkfs.vfat -F 32 -n VENTOY /dev/sdX1
sudo mkfs.ext4 -L PERSISTENCE /dev/sdX2
sudo mkfs.vfat -F 32 -n EXCHANGE /dev/sdX3
```

### Auto-Mount on All Platforms

```bash
# Linux (/etc/fstab):
UUID=<uuid> /mnt/usb ext4 defaults,nofail 0 0

# Windows (diskmgmt.msc):
# Right-click partition > Change Drive Letter and Paths > Add

# macOS:
# System Preferences > Users & Groups > Login Items > Add
```

## Platform-Specific Troubleshooting

### Windows Issues

| Issue | Solution |
|---|---|
| USB not in boot menu | Disable Fast Startup in Power Options |
| Secure boot blocks USB | Disable Secure Boot in BIOS |
| Slow USB performance | Disable USB selective suspend in Power Options |
| Can't read ext4 | Install Ext2Fsd or use WSL2 |

### macOS Issues

| Issue | Solution |
|---|---|
| USB not recognized | Hold Option key during boot |
| Can't mount ext4 | Install macFUSE + ext4fuse |
| Slow USB performance | Check USB-C adapter compatibility |
| Kernel panic | Disable SIP temporarily |

### Linux Issues

| Issue | Solution |
|---|---|
| USB not detected | Run `sudo partprobe` |
| Permission denied | Add user to `disk` group |
| Mount fails | Check `dmesg` for errors |
| Slow performance | Use USB 3.0+ port |

## Remote Access Setup

### Quick SSH Setup

```bash
# On USB system (one-time setup):
sudo apt update && sudo apt install openssh-server -y
sudo systemctl enable ssh
sudo systemctl start ssh

# Generate SSH key on client:
ssh-keygen -t ed25519 -C "usb-client"
ssh-copy-id user@usb-system.local

# Connect:
ssh user@usb-system.local
```

### Quick VNC Setup

```bash
# On USB system:
sudo apt install tightvncserver -y
vncserver :1
# Set password when prompted

# On client:
# macOS: Use Screen Sharing app
# Windows: Use TightVNC Viewer
# Linux: vncviewer usb-system.local:5901
```

### Quick RDP Setup

```bash
# On USB system:
sudo apt install xrdp xfce4 -y
sudo systemctl enable xrdp
echo "xfce4-session" > ${HOME}/.xsession
sudo systemctl restart xrdp

# On Windows:
# Open Remote Desktop Connection
# Enter: usb-system.local
# Select Xorg session
```
