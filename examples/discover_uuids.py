#!/usr/bin/env python3
"""
Example: Discover UUIDs for an unknown Lotus Lamp variant

This script demonstrates how to use the advanced scanner to discover
the service and characteristic UUIDs for any BLE LED lamp.
"""

import asyncio
from lotus_lamp import AdvancedDeviceScanner, LotusLampScanner


async def discover_and_identify_uuids():
    """Complete example of discovering UUIDs for an unknown device"""

    print("=" * 80)
    print("UUID DISCOVERY FOR LOTUS LAMP VARIANTS")
    print("=" * 80)
    print("\nThis example shows how to find the UUIDs for any BLE LED lamp,")
    print("even if it's a different model or variant.\n")

    # Step 1: Scan for devices
    print("[Step 1] Scanning for BLE devices...")
    devices = await LotusLampScanner.scan_all(timeout=10.0)

    if not devices:
        print("No devices found!")
        return

    # Show discovered devices
    LotusLampScanner.print_device_table(devices)

    # Step 2: Select a device
    print("\n[Step 2] Select a device to inspect")
    try:
        device_num = int(input("Enter device number: "))
        if device_num < 1 or device_num > len(devices):
            print("Invalid device number.")
            return

        selected_device = devices[device_num - 1]
        print(f"\nSelected: {selected_device.name} ({selected_device.address})")

    except (ValueError, KeyboardInterrupt):
        print("\nCancelled.")
        return

    # Step 3: Inspect device structure
    print("\n[Step 3] Reading device structure...")
    print("(This will connect to the device and read all services/characteristics)\n")

    device_info = await AdvancedDeviceScanner.discover_device_structure(
        selected_device.address
    )

    if not device_info:
        print("Failed to read device structure.")
        return

    # Step 4: Print complete structure
    print("\n[Step 4] Device Structure")
    AdvancedDeviceScanner.print_device_structure(device_info)

    # Step 5: Try to identify UUIDs
    print("\n[Step 5] Identifying Lotus Lamp UUIDs...")
    suggestions = AdvancedDeviceScanner.identify_lotus_lamp_uuids(device_info)

    if suggestions:
        print("\n✓ Successfully identified likely UUIDs!")
        AdvancedDeviceScanner.print_uuid_suggestions(suggestions)

        # Explain what was found
        print("\nℹ️  Explanation:")
        if suggestions['confidence'] == 'high':
            print("   This device uses the standard Lotus Lamp UUIDs.")
            print("   No configuration needed - the default settings will work!")
        elif suggestions['confidence'] == 'medium':
            print("   This device uses a variant of the Lotus Lamp protocol.")
            print("   The UUIDs above should work, but testing is recommended.")

        print("\nℹ️  How to use these UUIDs:")
        print("   1. Save the configuration to a file (option shown above)")
        print("   2. Use it in your code:")
        print(f"      lamp = LotusLamp(config_path='device_config.json')")
        print("   3. Test the connection:")
        print("      await lamp.connect()")

    else:
        print("\n⚠️  Could not automatically identify Lotus Lamp UUIDs.")
        print("\nManual inspection required:")
        print("  1. Look at the device structure printed above")
        print("  2. Find a custom service (UUID starting with 0000FF)")
        print("  3. Within that service, find:")
        print("     - A characteristic with WRITE_NO_RESPONSE property (for commands)")
        print("     - A characteristic with NOTIFY property (for responses)")
        print("\nExample:")
        print("  Service: 0000FFF0-... (custom service)")
        print("    ├─ Char: 0000FFF3-... [WRITE_NO_RESPONSE] ← Use this for write_char_uuid")
        print("    └─ Char: 0000FFF4-... [NOTIFY]           ← Use this for notify_char_uuid")


async def programmatic_example():
    """Example: Programmatic UUID discovery without user interaction"""

    print("Programmatic UUID Discovery Example")
    print("=" * 80)

    # Assume we know the device address
    device_address = "XX:XX:XX:XX:XX:XX"  # Replace with actual address

    # Discover structure
    print(f"Inspecting device at {device_address}...")
    device_info = await AdvancedDeviceScanner.discover_device_structure(device_address)

    if device_info:
        # Try to identify UUIDs
        suggestions = AdvancedDeviceScanner.identify_lotus_lamp_uuids(device_info)

        if suggestions:
            print("\nFound UUIDs:")
            print(f"  Service: {suggestions['service_uuid']}")
            print(f"  Write:   {suggestions['write_char_uuid']}")
            print(f"  Notify:  {suggestions['notify_char_uuid']}")

            # Use the UUIDs to create a config
            from lotus_lamp import DeviceConfig, LotusLamp

            config = DeviceConfig(
                name="Auto-Discovered Lamp",
                address=device_address,
                service_uuid=suggestions['service_uuid'],
                write_char_uuid=suggestions['write_char_uuid'],
                notify_char_uuid=suggestions['notify_char_uuid']
            )

            # Create lamp instance with discovered config
            lamp = LotusLamp(device_config=config)
            print("\n✓ Lamp configured with discovered UUIDs!")

            # Test connection
            if await lamp.connect():
                print("✓ Connection successful!")
                await lamp.set_rgb(255, 0, 0)  # Test with red
                await lamp.disconnect()
            else:
                print("✗ Connection failed - UUIDs may be incorrect")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'programmatic':
        asyncio.run(programmatic_example())
    else:
        asyncio.run(discover_and_identify_uuids())
