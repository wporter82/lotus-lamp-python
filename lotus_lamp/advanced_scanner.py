#!/usr/bin/env python3
"""
Advanced BLE Device Scanner
Discovers devices and their complete GATT structure (services and characteristics)
"""

import asyncio
from bleak import BleakScanner, BleakClient
from typing import List, Dict, Optional
import json


class ServiceInfo:
    """Information about a BLE service and its characteristics"""

    def __init__(self, uuid: str, description: str = ""):
        self.uuid = uuid
        self.description = description
        self.characteristics: List[Dict[str, str]] = []

    def add_characteristic(self, uuid: str, properties: List[str]):
        """Add a characteristic to this service"""
        self.characteristics.append({
            'uuid': uuid,
            'properties': properties
        })

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'uuid': self.uuid,
            'description': self.description,
            'characteristics': self.characteristics
        }


class AdvancedDeviceScanner:
    """Advanced scanner that reads full GATT structure"""

    # Known service UUIDs and their descriptions
    KNOWN_SERVICES = {
        '0000FFF0-0000-1000-8000-00805F9B34FB': 'Lotus Lamp Service (Common)',
        '00001800-0000-1000-8000-00805F9B34FB': 'Generic Access',
        '00001801-0000-1000-8000-00805F9B34FB': 'Generic Attribute',
        '0000180A-0000-1000-8000-00805F9B34FB': 'Device Information',
        '0000180F-0000-1000-8000-00805F9B34FB': 'Battery Service',
    }

    # Known characteristic UUIDs
    KNOWN_CHARACTERISTICS = {
        '0000FFF3-0000-1000-8000-00805F9B34FB': 'Lotus Lamp Write Char',
        '0000FFF4-0000-1000-8000-00805F9B34FB': 'Lotus Lamp Notify Char',
        '00002A00-0000-1000-8000-00805F9B34FB': 'Device Name',
        '00002A01-0000-1000-8000-00805F9B34FB': 'Appearance',
        '00002A19-0000-1000-8000-00805F9B34FB': 'Battery Level',
    }

    @staticmethod
    async def discover_device_structure(address: str, timeout: float = 10.0) -> Optional[Dict]:
        """
        Connect to a device and read its complete GATT structure

        Args:
            address: BLE device address
            timeout: Connection timeout in seconds

        Returns:
            Dictionary with device structure or None if connection fails
        """
        print(f"\nConnecting to {address}...")

        try:
            async with BleakClient(address, timeout=timeout) as client:
                if not client.is_connected:
                    print("Failed to connect")
                    return None

                print("✓ Connected! Reading services...")

                device_info = {
                    'address': address,
                    'services': []
                }

                # Get all services
                for service in client.services:
                    service_info = ServiceInfo(
                        uuid=service.uuid,
                        description=AdvancedDeviceScanner.KNOWN_SERVICES.get(
                            service.uuid.upper(),
                            "Unknown Service"
                        )
                    )

                    # Get all characteristics for this service
                    for char in service.characteristics:
                        properties = []

                        # Extract characteristic properties
                        if 'read' in char.properties:
                            properties.append('READ')
                        if 'write' in char.properties:
                            properties.append('WRITE')
                        if 'write-without-response' in char.properties:
                            properties.append('WRITE_NO_RESPONSE')
                        if 'notify' in char.properties:
                            properties.append('NOTIFY')
                        if 'indicate' in char.properties:
                            properties.append('INDICATE')

                        service_info.add_characteristic(char.uuid, properties)

                    device_info['services'].append(service_info.to_dict())

                print(f"✓ Found {len(device_info['services'])} services")
                return device_info

        except Exception as e:
            print(f"✗ Error: {e}")
            return None

    @staticmethod
    def print_device_structure(device_info: Dict):
        """Print device structure in a readable format"""
        print("\n" + "="*80)
        print(f"DEVICE STRUCTURE: {device_info['address']}")
        print("="*80)

        for service in device_info['services']:
            service_uuid = service['uuid']
            description = service['description']

            print(f"\n📦 Service: {service_uuid}")
            print(f"   {description}")

            for char in service['characteristics']:
                char_uuid = char['uuid']
                props = ', '.join(char['properties'])
                char_desc = AdvancedDeviceScanner.KNOWN_CHARACTERISTICS.get(
                    char_uuid.upper(),
                    "Unknown Characteristic"
                )

                print(f"   └─ Characteristic: {char_uuid}")
                print(f"      {char_desc}")
                print(f"      Properties: {props}")

        print("="*80)

    @staticmethod
    def identify_lotus_lamp_uuids(device_info: Dict) -> Optional[Dict]:
        """
        Try to identify likely Lotus Lamp control UUIDs from device structure

        Returns:
            Dictionary with suggested UUIDs or None
        """
        suggestions = {
            'service_uuid': None,
            'write_char_uuid': None,
            'notify_char_uuid': None,
            'confidence': 'unknown'
        }

        # Look for known Lotus Lamp service
        for service in device_info['services']:
            service_uuid = service['uuid'].upper()

            # Check if it's the known Lotus Lamp service
            if service_uuid == '0000FFF0-0000-1000-8000-00805F9B34FB':
                suggestions['service_uuid'] = service_uuid
                suggestions['confidence'] = 'high'

                # Look for write and notify characteristics
                for char in service['characteristics']:
                    char_uuid = char['uuid'].upper()
                    props = char['properties']

                    if char_uuid == '0000FFF3-0000-1000-8000-00805F9B34FB':
                        suggestions['write_char_uuid'] = char_uuid
                    elif char_uuid == '0000FFF4-0000-1000-8000-00805F9B34FB':
                        suggestions['notify_char_uuid'] = char_uuid

                break

            # Check for other custom services (0000FFxx pattern)
            elif service_uuid.startswith('0000FF') and service_uuid.endswith('-0000-1000-8000-00805F9B34FB'):
                # This might be a variant
                suggestions['service_uuid'] = service_uuid
                suggestions['confidence'] = 'medium'

                # Look for write-no-response and notify characteristics
                for char in service['characteristics']:
                    props = char['properties']

                    if 'WRITE_NO_RESPONSE' in props and not suggestions['write_char_uuid']:
                        suggestions['write_char_uuid'] = char['uuid'].upper()
                    elif 'NOTIFY' in props and not suggestions['notify_char_uuid']:
                        suggestions['notify_char_uuid'] = char['uuid'].upper()

        # If we found all three UUIDs, return the suggestion
        if all([suggestions['service_uuid'],
                suggestions['write_char_uuid'],
                suggestions['notify_char_uuid']]):
            return suggestions

        return None

    @staticmethod
    def print_uuid_suggestions(suggestions: Dict):
        """Print suggested UUIDs"""
        print("\n" + "="*80)
        print("SUGGESTED CONFIGURATION")
        print("="*80)

        confidence = suggestions.get('confidence', 'unknown')
        print(f"\nConfidence: {confidence.upper()}")

        print(f"\nService UUID:    {suggestions['service_uuid']}")
        print(f"Write Char UUID: {suggestions['write_char_uuid']}")
        print(f"Notify Char UUID: {suggestions['notify_char_uuid']}")

        print("\nConfiguration JSON:")
        config = {
            'name': 'My Lamp',
            'address': None,
            'service_uuid': suggestions['service_uuid'],
            'write_char_uuid': suggestions['write_char_uuid'],
            'notify_char_uuid': suggestions['notify_char_uuid']
        }
        print(json.dumps(config, indent=2))
        print("="*80)


async def interactive_advanced_scan():
    """Interactive advanced scanner"""
    print("\n" + "="*80)
    print("ADVANCED LOTUS LAMP DEVICE SCANNER")
    print("="*80)
    print("\nThis tool will connect to your device and read its complete structure")
    print("to help you identify the correct UUIDs.\n")

    while True:
        print("\nOptions:")
        print("  1. Scan for BLE devices")
        print("  2. Inspect device structure (requires device address)")
        print("  3. Exit")

        choice = input("\nSelect an option (1-3): ").strip()

        if choice == '1':
            # Import from scanner module
            from .scanner import LotusLampScanner

            devices = await LotusLampScanner.scan_all(timeout=10.0)
            LotusLampScanner.print_device_table(devices)

            if devices:
                print("\nUse option 2 to inspect a device's structure.")

        elif choice == '2':
            address = input("\nEnter device address (e.g., XX:XX:XX:XX:XX:XX): ").strip()

            if not address:
                print("No address provided.")
                continue

            # Discover device structure
            device_info = await AdvancedDeviceScanner.discover_device_structure(address)

            if device_info:
                # Print structure
                AdvancedDeviceScanner.print_device_structure(device_info)

                # Try to identify UUIDs
                suggestions = AdvancedDeviceScanner.identify_lotus_lamp_uuids(device_info)

                if suggestions:
                    AdvancedDeviceScanner.print_uuid_suggestions(suggestions)

                    # Offer to save
                    save = input("\nSave this configuration? (y/N): ").strip().lower()
                    if save == 'y':
                        filename = input("Filename [device_config.json]: ").strip()
                        if not filename:
                            filename = "device_config.json"

                        config = {
                            'name': input("Device name: ").strip() or 'My Lamp',
                            'address': address,
                            'service_uuid': suggestions['service_uuid'],
                            'write_char_uuid': suggestions['write_char_uuid'],
                            'notify_char_uuid': suggestions['notify_char_uuid']
                        }

                        with open(filename, 'w') as f:
                            json.dump(config, f, indent=2)
                        print(f"\n✓ Configuration saved to {filename}")
                else:
                    print("\n⚠ Could not automatically identify Lotus Lamp UUIDs.")
                    print("Look for a custom service (0000FFxx pattern) with:")
                    print("  - One WRITE_NO_RESPONSE characteristic (for commands)")
                    print("  - One NOTIFY characteristic (for responses)")

        elif choice == '3':
            print("\nExiting...")
            break
        else:
            print("Invalid option.")


if __name__ == '__main__':
    asyncio.run(interactive_advanced_scan())
