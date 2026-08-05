---
title: Mounted Partitions Block Ventoy Install
category: usb-hardware
date: 2026-06-10
failure: >
  Ventoy2Disk.sh refused to install onto a real USB device because an NTFS
  partition on that device was auto-mounted (via fuseblk), and Ventoy
  refuses to touch a device with any mounted partition.
root_cause: >
  OS auto-mount behavior for NTFS partitions was not accounted for before
  invoking a disk-imaging tool that hard-requires a fully unmounted device.
resolution: >
  Added an explicit unmount loop over every partition on the target device
  before running Ventoy, tolerating already-unmounted partitions.
prevention: >
  Always unmount ALL partitions on a target device before disk operations;
  check with `lsblk -o NAME,MOUNTPOINT`, and fall back to `fuser -km` if a
  partition reports busy.
verified: true
---

# Lesson: Mounted Partitions Block Ventoy Install

## Context
Installing Ventoy on a real USB device (`/dev/sdd`) that had an NTFS partition mounted at `/mnt/usb-test` via `fuseblk`.

## What Happened
Ventoy2Disk.sh refused to install:
```
/dev/sdd is already mounted, please umount it first!
```
The script checks `mount` output and refuses to install if ANY partition of the target device is mounted. NTFS partitions are commonly auto-mounted by the OS via `fuseblk`.

## Resolution
Added explicit unmount loop before running Ventoy:
```bash
for part in "${DEVICE}"*; do
    if [[ -b "$part" ]]; then
        umount "$part" 2>/dev/null || true
    fi
done
```

## Prevention
- Always unmount ALL partitions on the target device before disk operations
- Check with `mount | grep "/dev/sdX"` or `lsblk -o NAME,MOUNTPOINT /dev/sdX`
- Use `umount` not `mount -u`
- If unmount fails with "target is busy", use `fuser -km /dev/sdXN`
- For NTFS: `sudo umount /dev/sdXN` (fuseblk)

## Date: 2026-06-10
## Verified: yes
