#!/usr/bin/env python3
"""
Lotus Lamp Setup Wizard
Interactive first-time setup for configuring your Lotus Lamp device
"""

import asyncio
import json
from pathlib import Path
from typing import Optional, Dict

from .scanner import LotusLampScanner, DeviceInfo
from .advanced_scanner import AdvancedDeviceScanner
from .config import ConfigManager, DeviceConfig


class SetupWizard:
    """Interactive setup wizard for first-time configuration"""

    @staticmethod
    def print_welcome():
        """Print welcome message"""
        print("\n" + "="*80)
        print("LOTUS LAMP SETUP WIZARD")
        print("="*80)
        print("\nWelcome! This wizard will help you configure your Lotus Lamp device.")
        print("\nWe'll:")
        print("  1. Scan for your lamp")
        print("  2. Discover its connection details")
        print("  3. Save the configuration for future use")
        print("\nMake sure your lamp is powered on and nearby.")
        print("="*80)

    @staticmethod
    async def scan_for_devices() -> Optional[DeviceInfo]:
        """
        Scan for devices and let user select one

        Returns:
            Selected device or None if cancelled
        """
        print("\n[Step 1/3] Scanning for BLE devices...")
        print("(This may take 10-15 seconds)\n")

        # Scan for likely Lotus Lamp devices first
        devices = await LotusLampScanner.scan_lotus_lamps(timeout=10.0)

        if not devices:
            print("No Lotus Lamp devices found with common name patterns.")
            print("\nScanning for all BLE devices...")
            devices = await LotusLampScanner.scan_all(timeout=10.0)

        if not devices:
            print("\n✗ No BLE devices found!")
            print("\nTroubleshooting:")
            print("  - Make sure your lamp is powered on")
            print("  - Ensure Bluetooth is enabled on your computer")
            print("  - Move closer to the lamp")
            print("  - Try running the wizard again")
            return None

        # Show devices
        LotusLampScanner.print_device_table(devices)

        # Let user select
        print("\nSelect your Lotus Lamp device:")
        try:
            device_num = input("Enter device number (or 'q' to quit): ").strip()

            if device_num.lower() == 'q':
                return None

            device_num = int(device_num)
            if device_num < 1 or device_num > len(devices):
                print("✗ Invalid device number")
                return None

            selected = devices[device_num - 1]
            print(f"\n✓ Selected: {selected.name} ({selected.address})")
            return selected

        except (ValueError, KeyboardInterrupt):
            print("\n✗ Selection cancelled")
            return None

    @staticmethod
    async def discover_device_uuids(device: DeviceInfo) -> Optional[Dict]:
        """
        Discover device UUIDs

        Args:
            device: Selected device

        Returns:
            UUID suggestions or None if failed
        """
        print("\n[Step 2/3] Discovering device connection details...")
        print("(Connecting to device...)\n")

        # Try to discover device structure
        device_info = await AdvancedDeviceScanner.discover_device_structure(
            device.address,
            timeout=15.0
        )

        if not device_info:
            print("\n✗ Failed to connect to device")
            print("\nYou can:")
            print("  1. Try running the wizard again")
            print("  2. Enter UUIDs manually (advanced)")
            return None

        # Try to identify UUIDs automatically
        suggestions = AdvancedDeviceScanner.identify_lotus_lamp_uuids(device_info)

        if suggestions:
            print("\n✓ Successfully identified device UUIDs!")
            print(f"\nConfidence: {suggestions['confidence'].upper()}")
            print(f"Service UUID:    {suggestions['service_uuid']}")
            print(f"Write Char UUID: {suggestions['write_char_uuid']}")
            print(f"Notify Char UUID: {suggestions['notify_char_uuid']}")

            if suggestions['confidence'] == 'medium':
                print("\nNote: This device uses variant UUIDs (not the standard pattern).")
                print("The UUIDs above should work, but please test after setup.")

            return suggestions

        else:
            print("\n⚠ Could not automatically identify UUIDs")
            print("\nDevice structure:")
            AdvancedDeviceScanner.print_device_structure(device_info)

            print("\nWould you like to:")
            print("  1. Enter UUIDs manually (advanced)")
            print("  2. Quit and seek help")

            choice = input("\nChoice (1-2): ").strip()

            if choice == '1':
                return SetupWizard.enter_uuids_manually()
            else:
                return None

    @staticmethod
    def enter_uuids_manually() -> Optional[Dict]:
        """
        Manually enter UUIDs

        Returns:
            UUID dictionary or None
        """
        print("\nEnter device UUIDs:")
        print("(Press Enter to use common default values)")

        try:
            service = input("\nService UUID [0000FFF0-0000-1000-8000-00805F9B34FB]: ").strip()
            if not service:
                service = "0000FFF0-0000-1000-8000-00805F9B34FB"

            write_char = input("Write Char UUID [0000FFF3-0000-1000-8000-00805F9B34FB]: ").strip()
            if not write_char:
                write_char = "0000FFF3-0000-1000-8000-00805F9B34FB"

            notify_char = input("Notify Char UUID [0000FFF4-0000-1000-8000-00805F9B34FB]: ").strip()
            if not notify_char:
                notify_char = "0000FFF4-0000-1000-8000-00805F9B34FB"

            return {
                'service_uuid': service.upper(),
                'write_char_uuid': write_char.upper(),
                'notify_char_uuid': notify_char.upper(),
                'confidence': 'manual'
            }

        except KeyboardInterrupt:
            return None

    @staticmethod
    def save_configuration(device: DeviceInfo, uuids: Dict) -> bool:
        """
        Save device configuration

        Args:
            device: Selected device
            uuids: UUID suggestions

        Returns:
            True if saved successfully
        """
        print("\n[Step 3/3] Saving configuration...")

        # Ask for a friendly name
        print(f"\nDevice name: {device.name}")
        friendly_name = input("Enter a friendly name (or press Enter to use device name): ").strip()
        if not friendly_name:
            friendly_name = device.name

        # Create configuration
        config = DeviceConfig(
            name=friendly_name,
            address=device.address,
            service_uuid=uuids['service_uuid'],
            write_char_uuid=uuids['write_char_uuid'],
            notify_char_uuid=uuids['notify_char_uuid']
        )

        # Determine save location
        print("\nWhere would you like to save this configuration?")
        print("\n1. Current project directory (recommended for library use)")
        print(f"   → {Path.cwd() / 'lotus_lamp_config.json'}")
        print("\n2. Global user config (recommended for CLI tools)")
        print(f"   → {Path.home() / '.lotus_lamp' / 'config.json'}")
        print("\n3. Custom location")

        choice = input("\nEnter choice (1/2/3) [1]: ").strip() or "1"

        if choice == "1":
            save_path = Path.cwd() / "lotus_lamp_config.json"
        elif choice == "2":
            save_path = Path.home() / ".lotus_lamp" / "config.json"
        elif choice == "3":
            custom_path = input("Enter custom path: ").strip()
            save_path = Path(custom_path) if custom_path else Path.cwd() / "lotus_lamp_config.json"
        else:
            print("Invalid choice, using project directory")
            save_path = Path.cwd() / "lotus_lamp_config.json"

        # Save configuration
        try:
            manager = ConfigManager()
            manager.add_device(config)
            manager.save(save_path)

            print(f"\n✓ Configuration saved to: {save_path}")
            return True

        except Exception as e:
            print(f"\n✗ Failed to save configuration: {e}")
            return False

    @staticmethod
    def print_next_steps(device_name: str):
        """Print next steps after successful setup"""
        print("\n" + "="*80)
        print("SETUP COMPLETE!")
        print("="*80)
        print("\nYour Lotus Lamp is now configured and ready to use!")
        print("\nNext steps:")
        print("\n1. Test your lamp:")
        print("   ```python")
        print("   from lotus_lamp import LotusLamp")
        print("   import asyncio")
        print("")
        print("   async def test():")
        print("       lamp = LotusLamp()")
        print("       await lamp.connect()")
        print("       await lamp.set_rgb(255, 0, 0)  # Red")
        print("       await lamp.disconnect()")
        print("")
        print("   asyncio.run(test())")
        print("   ```")
        print("\n2. Explore the interactive controller:")
        print("   python -m lotus_lamp.controller")
        print("\n3. Check out the examples:")
        print("   - examples/discover_and_configure.py")
        print("   - examples/multi_device.py")
        print("\n4. Read the documentation:")
        print("   - README.md")
        print("   - DEVICE_SETUP.md")
        print("="*80)


async def run_setup():
    """Run the setup wizard"""
    SetupWizard.print_welcome()

    # Step 1: Scan for devices
    device = await SetupWizard.scan_for_devices()
    if not device:
        print("\n✗ Setup cancelled")
        return

    # Step 2: Discover UUIDs
    uuids = await SetupWizard.discover_device_uuids(device)
    if not uuids:
        print("\n✗ Setup cancelled")
        return

    # Step 3: Save configuration
    if SetupWizard.save_configuration(device, uuids):
        SetupWizard.print_next_steps(device.name)
    else:
        print("\n✗ Setup failed")


if __name__ == '__main__':
    try:
        asyncio.run(run_setup())
    except KeyboardInterrupt:
        print("\n\n✗ Setup cancelled by user")
