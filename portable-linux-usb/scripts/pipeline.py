#!/usr/bin/env python3
"""
Pipeline Script for Portable Linux USB

Orchestrates the complete workflow for creating, managing, and deploying
portable Linux USB environments with agent isolation.

Usage:
    python3 pipeline.py create --device /dev/sdX --iso ubuntu-24.04.4-desktop-amd64.iso
    python3 pipeline.py deploy --usb /dev/sdX --agents alpha,beta
    python3 pipeline.py backup --usb /dev/sdX --full
    python3 pipeline.py restore --usb /dev/sdX --from-backup ${HOME}/backups/usb.img.gz
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class USBPipeline:
    """Main pipeline class for USB operations."""
    
    def __init__(self):
        self.steps = []
        self.errors = []
        self.warnings = []
    
    def log(self, message, level="INFO"):
        """Log a message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def run_step(self, name, command, check=True):
        """Execute a pipeline step."""
        self.log(f"Starting: {name}")
        try:
            result = subprocess.run(
                command, shell=True, check=check,
                capture_output=True, text=True
            )
            if result.returncode == 0:
                self.log(f"Completed: {name}")
                return result
            else:
                self.log(f"Warning: {name} returned non-zero exit code", "WARN")
                if result.stderr:
                    self.log(f"Stderr: {result.stderr[:200]}")
                return result
        except subprocess.CalledProcessError as e:
            self.log(f"Failed: {name}", "ERROR")
            self.errors.append(f"{name}: {str(e)}")
            return None
    
    def create_usb(self, args):
        """Create a new portable Linux USB."""
        self.log("=" * 60)
        self.log("Starting USB Creation Pipeline")
        self.log("=" * 60)
        
        device = args.device
        iso_path = args.iso
        persistence_size = args.persistence
        
        # Step 1: Check prerequisites
        self.log("\nStep 1: Checking prerequisites...")
        self.run_step("Check tools", "which dd mkfs.vfat mkfs.ext4 parted")
        
        # Step 2: Download Ventoy if needed
        self.log("\nStep 2: Setting up Ventoy...")
        self.run_step(
            "Download Ventoy",
            "wget -P /tmp https://github.com/ventoy/Ventoy/releases/download/v1.1.12/ventoy-1.1.12-linux.tar.gz"
        )
        self.run_step("Extract Ventoy", "tar -xf /tmp/ventoy-1.1.12-linux.tar.gz -C /tmp")
        
        # Step 3: Install Ventoy
        self.log("\nStep 3: Installing Ventoy to USB...")
        self.run_step(
            "Install Ventoy",
            f"cd /tmp/ventoy-1.1.12 && sudo ./Ventoy2Disk.sh -iI {device}",
            check=False
        )
        
        # Step 4: Mount USB
        self.log("\nStep 4: Mounting USB...")
        self.run_step("Create mount point", "sudo mkdir -p /media/ventoy-usb")
        self.run_step("Mount USB", f"sudo mount {device}1 /media/ventoy-usb")
        
        # Step 5: Copy ISO
        self.log("\nStep 5: Copying ISO file...")
        iso_name = os.path.basename(iso_path)
        self.run_step("Copy ISO", f"sudo cp {iso_path} /media/ventoy-usb/")
        
        # Step 6: Create persistence
        self.log("\nStep 6: Creating persistence file...")
        persist_size_mb = int(persistence_size.replace("G", "")) * 1024
        self.run_step(
            "Create persistence",
            f"sudo dd if=/dev/zero of=/media/ventoy-usb/persistence/ubuntu-persistence.dat "
            f"bs=1M count={persist_size_mb} status=progress"
        )
        self.run_step(
            "Format persistence",
            "sudo mkfs.ext4 -F -L casper-rw /media/ventoy-usb/persistence/ubuntu-persistence.dat"
        )
        
        # Step 7: Create Ventoy config
        self.log("\nStep 7: Creating Ventoy configuration...")
        config = {
            "persistence": [
                {
                    "image": f"/{iso_name}",
                    "backend": "/persistence/ubuntu-persistence.dat"
                }
            ]
        }
        
        config_json = json.dumps(config, indent=4)
        self.run_step(
            "Write config",
            f"sudo tee /media/ventoy-usb/ventoy/ventoy.json > /dev/null << 'EOF'\n{config_json}\nEOF"
        )
        
        # Step 8: Verify
        self.log("\nStep 8: Verifying setup...")
        self.run_step("List USB contents", "ls -la /media/ventoy-usb/")
        
        # Step 9: Unmount
        self.log("\nStep 9: Cleanup...")
        self.run_step("Unmount USB", "sudo umount /media/ventoy-usb")
        
        self.log("\n" + "=" * 60)
        if self.errors:
            self.log(f"Pipeline completed with {len(self.errors)} errors", "WARN")
            for error in self.errors:
                self.log(f"  - {error}", "ERROR")
        else:
            self.log("Pipeline completed successfully!")
        self.log("=" * 60)
        
        return len(self.errors) == 0
    
    def deploy_agents(self, args):
        """Deploy agent workspaces to existing USB."""
        self.log("=" * 60)
        self.log("Starting Agent Deployment Pipeline")
        self.log("=" * 60)
        
        device = args.usb
        agents = [a.strip() for a in args.agents.split(",")]
        agent_size = args.agent_size
        
        # Step 1: Mount USB
        self.log("\nStep 1: Mounting USB...")
        self.run_step("Mount USB", f"sudo mount {device}1 /media/ventoy-usb")
        
        # Step 2: Create agents directory
        self.log("\nStep 2: Creating agents directory...")
        self.run_step("Create agents dir", "sudo mkdir -p /media/ventoy-usb/agents")
        
        # Step 3: Create agent workspaces
        self.log("\nStep 3: Creating agent workspaces...")
        agent_configs = {}
        
        for agent in agents:
            self.log(f"\nCreating workspace for agent: {agent}")
            
            agent_file = f"/media/ventoy-usb/agents/{agent}-home.dat"
            size_mb = int(agent_size.replace("G", "")) * 1024
            
            self.run_step(
                f"Create {agent} storage",
                f"sudo dd if=/dev/zero of={agent_file} bs=1M count={size_mb} status=progress"
            )
            
            self.run_step(
                f"Format {agent}",
                f"sudo mkfs.ext4 -F -L {agent}-home {agent_file}"
            )
            
            # Initialize agent home
            self.run_step(f"Initialize {agent}", f"sudo mkdir -p /tmp/agent-init-{agent}")
            self.run_step(
                f"Mount {agent}",
                f"sudo mount -o loop {agent_file} /tmp/agent-init-{agent}"
            )
            
            # Create directory structure
            dirs = ["bin", "lib", "share", "workspace", "config", "cache", "logs"]
            for d in dirs:
                self.run_step(
                    f"Create {agent}/{d}",
                    f"sudo mkdir -p /tmp/agent-init-{agent}/{d}"
                )
            
            # Create agent info
            agent_info = {
                "name": agent,
                "created": datetime.now().isoformat(),
                "version": "1.0",
                "isolation_level": "L2",
                "storage_size": agent_size
            }
            
            info_json = json.dumps(agent_info, indent=2)
            self.run_step(
                f"Write {agent} info",
                f"sudo tee /tmp/agent-init-{agent}/agent-info.json > /dev/null << 'EOF'\n{info_json}\nEOF"
            )
            
            self.run_step(f"Set {agent} permissions", "sudo chown -R 1000:1000 /tmp/agent-init-{agent}")
            self.run_step(f"Unmount {agent}", f"sudo umount /tmp/agent-init-{agent}")
            
            agent_configs[agent] = {
                "backend": f"/agents/{agent}-home.dat",
                "description": f"Isolated workspace for agent {agent}",
                "storage_size": agent_size
            }
        
        # Step 4: Update Ventoy config
        self.log("\nStep 4: Updating Ventoy configuration...")
        
        config_file = "/media/ventoy-usb/ventoy/ventoy.json"
        if os.path.exists(config_file):
            # Read existing config
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            config = {"persistence": []}
        
        config["agent_isolation"] = agent_configs
        
        config_json = json.dumps(config, indent=4)
        self.run_step(
            "Update config",
            f"sudo tee {config_file} > /dev/null << 'EOF'\n{config_json}\nEOF"
        )
        
        # Step 5: Verify
        self.log("\nStep 5: Verifying deployment...")
        self.run_step("List agents", "ls -la /media/ventoy-usb/agents/")
        
        # Step 6: Unmount
        self.log("\nStep 6: Cleanup...")
        self.run_step("Unmount USB", "sudo umount /media/ventoy-usb")
        
        self.log("\n" + "=" * 60)
        if self.errors:
            self.log(f"Deployment completed with {len(self.errors)} errors", "WARN")
        else:
            self.log(f"Successfully deployed {len(agents)} agent workspaces!")
        self.log("=" * 60)
        
        return len(self.errors) == 0
    
    def backup_usb(self, args):
        """Backup USB contents."""
        self.log("=" * 60)
        self.log("Starting USB Backup Pipeline")
        self.log("=" * 60)
        
        device = args.usb
        backup_dir = args.output or os.path.expanduser("${HOME}/usb-backups")
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        os.makedirs(backup_dir, exist_ok=True)
        
        if args.full:
            # Full image backup
            backup_file = os.path.join(backup_dir, f"usb-full-{timestamp}.img.gz")
            self.log(f"Creating full image backup: {backup_file}")
            
            self.run_step(
                "Create full backup",
                f"sudo dd if={device} bs=4M status=progress | gzip > {backup_file}"
            )
            
            # Create checksum
            self.run_step(
                "Create checksum",
                f"sha256sum {backup_file} > {backup_file}.sha256"
            )
        else:
            # Selective backup
            self.log("Mounting USB for selective backup...")
            self.run_step("Mount USB", f"sudo mount {device}1 /media/ventoy-usb")
            
            # Backup persistence
            if args.persistence:
                persist_backup = os.path.join(backup_dir, f"persistence-{timestamp}.dat")
                self.run_step(
                    "Backup persistence",
                    f"sudo dd if={device}5 of={persist_backup} bs=4M status=progress"
                )
            
            # Backup agents
            if args.agents:
                for agent in args.agents.split(","):
                    agent_backup = os.path.join(backup_dir, f"agent-{agent}-{timestamp}.dat")
                    agent_file = f"/media/ventoy-usb/agents/{agent}-home.dat"
                    
                    if os.path.exists(agent_file):
                        self.run_step(
                            f"Backup agent {agent}",
                            f"sudo dd if={agent_file} of={agent_backup} bs=4M status=progress"
                        )
            
            # Backup config
            if args.config:
                config_backup = os.path.join(backup_dir, f"ventoy-config-{timestamp}")
                self.run_step(
                    "Backup Ventoy config",
                    f"sudo cp -r /media/ventoy-usb/ventoy {config_backup}"
                )
            
            self.run_step("Unmount USB", "sudo umount /media/ventoy-usb")
        
        self.log("\n" + "=" * 60)
        if self.errors:
            self.log(f"Backup completed with {len(self.errors)} errors", "WARN")
        else:
            self.log("Backup completed successfully!")
        self.log("=" * 60)
        
        return len(self.errors) == 0


def main():
    parser = argparse.ArgumentParser(
        description="Portable Linux USB Pipeline Manager"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Pipeline command")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create new USB")
    create_parser.add_argument("--device", "-d", required=True, help="USB device")
    create_parser.add_argument("--iso", "-i", required=True, help="ISO file path")
    create_parser.add_argument("--persistence", "-p", default="20G", help="Persistence size")
    
    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy agents to USB")
    deploy_parser.add_argument("--usb", "-u", required=True, help="USB device")
    deploy_parser.add_argument("--agents", "-a", required=True, help="Comma-separated agent names")
    deploy_parser.add_argument("--agent-size", "-s", default="5G", help="Size per agent")
    
    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Backup USB")
    backup_parser.add_argument("--usb", "-u", required=True, help="USB device")
    backup_parser.add_argument("--full", "-f", action="store_true", help="Full image backup")
    backup_parser.add_argument("--persistence", "-p", action="store_true", help="Backup persistence")
    backup_parser.add_argument("--agents", "-a", help="Comma-separated agent names to backup")
    backup_parser.add_argument("--config", "-c", action="store_true", help="Backup Ventoy config")
    backup_parser.add_argument("--output", "-o", help="Output directory")
    
    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore USB from backup")
    restore_parser.add_argument("--usb", "-u", required=True, help="USB device")
    restore_parser.add_argument("--from-backup", "-f", required=True, help="Backup file")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    pipeline = USBPipeline()
    
    if args.command == "create":
        success = pipeline.create_usb(args)
    elif args.command == "deploy":
        success = pipeline.deploy_agents(args)
    elif args.command == "backup":
        success = pipeline.backup_usb(args)
    elif args.command == "restore":
        # TODO: Implement restore
        print("Restore not yet implemented")
        success = False
    else:
        parser.print_help()
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
