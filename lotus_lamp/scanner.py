#!/usr/bin/env python3
"""
Device Scanner for Lotus Lamp
Discovers BLE devices and helps configure new lamps
"""

import asyncio
from bleak import BleakScanner
from typing import List, Dict, Optional
import json


class DeviceInfo:
    """Information about a discovered BLE device"""

    def __init__(self, name: str, address: str, rssi: int, services: List[str]):
        self.name = name
        self.address = address
        self.rssi = rssi
        self.services = services

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'address': self.address,
            'rssi': self.rssi,
            'services': self.services
        }

    def __repr__(self):
        return f"DeviceInfo(name='{self.name}', address='{self.address}', rssi={self.rssi})"


class LotusLampScanner:
    """Scanner for discovering Lotus Lamp devices and other BLE devices"""

    # Common service UUIDs for Lotus Lamps
    COMMON_SERVICE_UUIDS = [
        "0000FFF0-0000-1000-8000-00805F9B34FB",  # Standard Lotus Lamp service
    ]

    # Common device name patterns
    COMMON_NAME_PATTERNS = [
        "MELK",
        "Lotus",
        "LED",
        "RGB",
        "LAMP",
        "Light",
    ]

    @staticmethod
    async def scan_all(timeout: float = 10.0) -> List[DeviceInfo]:
        """
        Scan for all BLE devices

        Args:
            timeout: How long to scan in seconds

        Returns:
            List of discovered devices
        """
        print(f"Scanning for BLE devices for {timeout} seconds...")

        # Use return_adv=True to get advertisement data including service UUIDs
        devices_dict = await BleakScanner.discover(timeout=timeout, return_adv=True)

        device_list = []
        for address, (device, adv_data) in devices_dict.items():
            # Get service UUIDs from advertisement data
            services = []
            if adv_data and hasattr(adv_data, 'service_uuids') and adv_data.service_uuids:
                services = list(adv_data.service_uuids)

            # Get RSSI from advertisement data
            rssi = adv_data.rssi if adv_data and hasattr(adv_data, 'rssi') else 0

            device_info = DeviceInfo(
                name=device.name or "Unknown",
                address=device.address,
                rssi=rssi,
                services=services
            )
            device_list.append(device_info)

        return device_list

    @staticmethod
    async def scan_lotus_lamps(timeout: float = 10.0) -> List[DeviceInfo]:
        """
        Scan for likely Lotus Lamp devices

        Args:
            timeout: How long to scan in seconds

        Returns:
            List of likely Lotus Lamp devices
        """
        all_devices = await LotusLampScanner.scan_all(timeout)

        # Filter for likely Lotus Lamp devices
        likely_lamps = []
        for device in all_devices:
            # Check if device name contains common patterns
            name_match = any(pattern.lower() in device.name.lower()
                           for pattern in LotusLampScanner.COMMON_NAME_PATTERNS)

            # Check if device has common service UUID
            service_match = any(service in device.services
                              for service in LotusLampScanner.COMMON_SERVICE_UUIDS)

            if name_match or service_match:
                likely_lamps.append(device)

        return likely_lamps

    @staticmethod
    def generate_config(device: DeviceInfo,
                       service_uuid: Optional[str] = None,
                       write_char_uuid: Optional[str] = None,
                       notify_char_uuid: Optional[str] = None) -> dict:
        """
        Generate a device configuration dictionary

        Args:
            device: Device information
            service_uuid: Optional custom service UUID
            write_char_uuid: Optional custom write characteristic UUID
            notify_char_uuid: Optional custom notify characteristic UUID

        Returns:
            Device configuration dictionary
        """
        # Use provided UUIDs or defaults
        if not service_uuid:
            service_uuid = "0000FFF0-0000-1000-8000-00805F9B34FB"
        if not write_char_uuid:
            write_char_uuid = "0000FFF3-0000-1000-8000-00805F9B34FB"
        if not notify_char_uuid:
            notify_char_uuid = "0000FFF4-0000-1000-8000-00805F9B34FB"

        return {
            'name': device.name,
            'address': device.address,
            'service_uuid': service_uuid,
            'write_char_uuid': write_char_uuid,
            'notify_char_uuid': notify_char_uuid
        }

    @staticmethod
    def print_device_table(devices: List[DeviceInfo]):
        """Print a formatted table of devices"""
        if not devices:
            print("No devices found.")
            return

        print(f"\nFound {len(devices)} device(s):")
        print("=" * 80)
        print(f"{'#':<4} {'Name':<25} {'Address':<20} {'RSSI':<6} {'Services'}")
        print("-" * 80)

        for i, device in enumerate(devices, 1):
            services_str = ', '.join(device.services[:2]) if device.services else 'None'
            if len(device.services) > 2:
                services_str += f" (+{len(device.services) - 2} more)"

            print(f"{i:<4} {device.name:<25} {device.address:<20} {device.rssi:<6} {services_str}")

        print("=" * 80)


async def interactive_scan():
    """Interactive device scanner"""
    print("\n" + "="*80)
    print("LOTUS LAMP DEVICE SCANNER")
    print("="*80)
    print("\nThis tool will help you discover and configure Lotus Lamp devices.")
    print("\nNote: For devices with unknown UUIDs, use the advanced scanner:")
    print("  python -m lotus_lamp.advanced_scanner\n")

    while True:
        print("\nOptions:")
        print("  1. Scan for all BLE devices")
        print("  2. Scan for likely Lotus Lamp devices")
        print("  3. Generate device configuration")
        print("  4. Exit")

        choice = input("\nSelect an option (1-4): ").strip()

        if choice == '1':
            devices = await LotusLampScanner.scan_all(timeout=10.0)
            LotusLampScanner.print_device_table(devices)

        elif choice == '2':
            devices = await LotusLampScanner.scan_lotus_lamps(timeout=10.0)
            LotusLampScanner.print_device_table(devices)

        elif choice == '3':
            # First scan for devices
            devices = await LotusLampScanner.scan_all(timeout=10.0)
            if not devices:
                print("No devices found. Please scan first.")
                continue

            LotusLampScanner.print_device_table(devices)

            try:
                device_num = int(input("\nSelect device number to configure: "))
                if device_num < 1 or device_num > len(devices):
                    print("Invalid device number.")
                    continue

                selected_device = devices[device_num - 1]

                print(f"\nSelected: {selected_device.name} ({selected_device.address})")
                print("\nUse default UUIDs? (Y/n): ", end='')
                use_defaults = input().strip().lower() != 'n'

                if use_defaults:
                    config = LotusLampScanner.generate_config(selected_device)
                else:
                    print("\nEnter custom UUIDs (or press Enter to use default):")
                    service = input("Service UUID [0000FFF0-0000-1000-8000-00805F9B34FB]: ").strip()
                    write_char = input("Write Char UUID [0000FFF3-0000-1000-8000-00805F9B34FB]: ").strip()
                    notify_char = input("Notify Char UUID [0000FFF4-0000-1000-8000-00805F9B34FB]: ").strip()

                    config = LotusLampScanner.generate_config(
                        selected_device,
                        service_uuid=service if service else None,
                        write_char_uuid=write_char if write_char else None,
                        notify_char_uuid=notify_char if notify_char else None
                    )

                print("\nGenerated configuration:")
                print(json.dumps(config, indent=2))

                save = input("\nSave to file? (y/N): ").strip().lower()
                if save == 'y':
                    filename = input("Filename [device_config.json]: ").strip()
                    if not filename:
                        filename = "device_config.json"

                    with open(filename, 'w') as f:
                        json.dump(config, f, indent=2)
                    print(f"Configuration saved to {filename}")

            except (ValueError, IndexError) as e:
                print(f"Error: {e}")

        elif choice == '4':
            print("\nExiting...")
            break
        else:
            print("Invalid option.")


if __name__ == '__main__':
    asyncio.run(interactive_scan())
