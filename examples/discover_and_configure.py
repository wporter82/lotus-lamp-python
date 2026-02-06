#!/usr/bin/env python3
"""
Example: Discover and configure a Lotus Lamp device

NOTE: This example is for demonstration purposes. For actual setup,
use the built-in setup wizard:
    python -m lotus_lamp.setup

This script demonstrates the underlying API used by the setup wizard.
"""

import asyncio
from pathlib import Path
from lotus_lamp import LotusLampScanner, AdvancedDeviceScanner, ConfigManager, DeviceConfig, LotusLamp


async def discover_and_setup():
    """Complete example of discovering and setting up a new lamp"""

    print("=" * 80)
    print("LOTUS LAMP DISCOVERY AND SETUP EXAMPLE")
    print("=" * 80)
    print("\nNOTE: For normal use, run the built-in wizard:")
    print("  python -m lotus_lamp.setup")
    print("\nThis example demonstrates the underlying API.\n")

    # Step 1: Scan for devices
    print("[1/4] Scanning for BLE devices...")
    devices = await LotusLampScanner.scan_lotus_lamps(timeout=10.0)

    if not devices:
        print("No Lotus Lamp devices found!")
        print("\nTrying to scan for ALL BLE devices...")
        devices = await LotusLampScanner.scan_all(timeout=10.0)

    if not devices:
        print("No BLE devices found. Make sure your lamp is powered on and nearby.")
        return

    # Step 2: Show discovered devices
    print("\n[2/4] Found devices:")
    LotusLampScanner.print_device_table(devices)

    # Step 3: Let user select a device
    print("\n[3/4] Select a device to configure")
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

    # Step 4: Discover UUIDs automatically
    print("\n[4/4] Discovering device UUIDs...")
    device_info = await AdvancedDeviceScanner.discover_device_structure(
        selected_device.address
    )

    if not device_info:
        print("Failed to connect to device.")
        return

    # Try to identify UUIDs automatically
    uuids = AdvancedDeviceScanner.identify_lotus_lamp_uuids(device_info)

    if not uuids:
        print("Could not auto-identify UUIDs. Using defaults...")
        uuids = {
            'service_uuid': "0000FFF0-0000-1000-8000-00805F9B34FB",
            'write_char_uuid': "0000FFF3-0000-1000-8000-00805F9B34FB",
            'notify_char_uuid': "0000FFF4-0000-1000-8000-00805F9B34FB",
        }

    print(f"\n✓ UUIDs discovered:")
    print(f"  Service:  {uuids['service_uuid']}")
    print(f"  Write:    {uuids['write_char_uuid']}")
    print(f"  Notify:   {uuids['notify_char_uuid']}")

    # Create configuration
    friendly_name = input(f"\nEnter a friendly name [{selected_device.name}]: ").strip()
    if not friendly_name:
        friendly_name = selected_device.name

    device_config = DeviceConfig(
        name=friendly_name,
        address=selected_device.address,
        service_uuid=uuids['service_uuid'],
        write_char_uuid=uuids['write_char_uuid'],
        notify_char_uuid=uuids['notify_char_uuid']
    )

    # Save configuration
    print("\nSave configuration?")
    print("  1. Save to default location")
    print("  2. Don't save, just test connection")

    choice = input("\nChoice (1-2): ").strip()

    if choice == '1':
        config_path = Path.home() / ".lotus_lamp" / "config.json"
        manager = ConfigManager()
        manager.add_device(device_config)
        manager.save(config_path)
        print(f"\n✓ Configuration saved to {config_path}")
    else:
        print("\nSkipping save, testing connection only...")

    # Test the connection
    print("\n" + "=" * 80)
    print("TESTING CONNECTION")
    print("=" * 80)

    try:
        lamp = LotusLamp(device_config=device_config)

        print("\nConnecting...")
        if await lamp.connect():
            print("✓ Connected!")

            print("\nTesting color control (blue)...")
            await lamp.set_rgb(0, 0, 255)
            await asyncio.sleep(1)

            print("✓ Color test successful!")

            print("\nReturning to white...")
            await lamp.set_rgb(255, 255, 255)

            await lamp.disconnect()
            print("✓ Disconnected")

            print("\n" + "=" * 80)
            print("SUCCESS!")
            print("=" * 80)
            print("\nYour lamp is working correctly!")

            if choice == '1':
                print("\nYou can now use it in your code:")
                print("  from lotus_lamp import LotusLamp")
                print("  lamp = LotusLamp()")
                print("  await lamp.connect()")
        else:
            print("✗ Failed to connect")

    except Exception as e:
        print(f"\n✗ Error: {e}")


async def programmatic_example():
    """Example: Fully programmatic setup without user input"""

    print("Programmatic Setup Example")
    print("=" * 80)

    # For this example, we'll use the first device found
    devices = await LotusLampScanner.scan_all(timeout=5.0)

    if not devices:
        print("No devices found")
        return

    device = devices[0]
    print(f"Using: {device.name} ({device.address})")

    # Discover UUIDs
    device_info = await AdvancedDeviceScanner.discover_device_structure(device.address)
    if not device_info:
        print("Failed to connect")
        return

    uuids = AdvancedDeviceScanner.identify_lotus_lamp_uuids(device_info)
    if not uuids:
        print("Could not identify UUIDs")
        return

    # Create and use config directly
    config = DeviceConfig(
        name="Auto-Discovered Lamp",
        address=device.address,
        service_uuid=uuids['service_uuid'],
        write_char_uuid=uuids['write_char_uuid'],
        notify_char_uuid=uuids['notify_char_uuid']
    )

    # Use the lamp
    lamp = LotusLamp(device_config=config)
    if await lamp.connect():
        print("✓ Connected and ready to use!")
        await lamp.set_rgb(255, 0, 0)  # Red
        await lamp.disconnect()


if __name__ == '__main__':
    import sys

    print("\n" + "=" * 80)
    print("LOTUS LAMP DISCOVERY EXAMPLE")
    print("=" * 80)
    print("\nIMPORTANT: For normal setup, use the built-in wizard:")
    print("  python -m lotus_lamp.setup")
    print("\nThis script is for demonstration/learning purposes.")
    print("=" * 80)

    if len(sys.argv) > 1 and sys.argv[1] == 'programmatic':
        asyncio.run(programmatic_example())
    else:
        try:
            asyncio.run(discover_and_setup())
        except KeyboardInterrupt:
            print("\n\nCancelled by user.")
