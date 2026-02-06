#!/usr/bin/env python3
"""
Example: Control multiple Lotus Lamps

This script demonstrates controlling multiple lamps simultaneously
from a single configuration file.
"""

import asyncio
from lotus_lamp import LotusLamp


async def control_multiple_lamps():
    """Example of controlling multiple lamps"""

    print("=" * 80)
    print("MULTI-DEVICE LOTUS LAMP CONTROL")
    print("=" * 80)

    # Load two different lamps from config
    # Make sure your config file has at least 2 devices configured

    print("\nLoading lamp configurations...")

    try:
        # If you have named devices in your config:
        lamp1 = LotusLamp(device_name="Living Room Lamp")
        lamp2 = LotusLamp(device_name="Bedroom Lamp")

        # Or just load the default device:
        # lamp1 = LotusLamp()

    except ValueError as e:
        print(f"Error loading lamp config: {e}")
        print("\nMake sure you have configured devices in your config file.")
        print("Run discover_and_configure.py first to set up your devices.")
        return

    try:
        # Connect to both lamps
        print("\nConnecting to lamps...")
        connected1 = await lamp1.connect()
        connected2 = await lamp2.connect()

        if not (connected1 and connected2):
            print("Failed to connect to one or more lamps")
            return

        print("✓ Both lamps connected!")

        # Synchronized color changes
        print("\n1. Synchronized colors...")
        colors = [
            ("Red", 255, 0, 0),
            ("Green", 0, 255, 0),
            ("Blue", 0, 0, 255),
        ]

        for name, r, g, b in colors:
            print(f"   Setting both to {name}...")
            await asyncio.gather(
                lamp1.set_rgb(r, g, b),
                lamp2.set_rgb(r, g, b)
            )
            await asyncio.sleep(1.5)

        # Different colors on each lamp
        print("\n2. Different colors on each lamp...")
        print("   Lamp 1: Purple, Lamp 2: Orange")
        await asyncio.gather(
            lamp1.set_rgb(128, 0, 128),  # Purple
            lamp2.set_rgb(255, 165, 0)    # Orange
        )
        await asyncio.sleep(2)

        # Alternating pattern
        print("\n3. Alternating pattern...")
        for _ in range(3):
            print("   Lamp 1: On, Lamp 2: Off")
            await asyncio.gather(
                lamp1.set_rgb(255, 255, 255),
                lamp2.set_rgb(0, 0, 0)
            )
            await asyncio.sleep(0.5)

            print("   Lamp 1: Off, Lamp 2: On")
            await asyncio.gather(
                lamp1.set_rgb(0, 0, 0),
                lamp2.set_rgb(255, 255, 255)
            )
            await asyncio.sleep(0.5)

        # Set to animations
        print("\n4. Different animations on each lamp...")
        print("   Lamp 1: Animation 143, Lamp 2: Animation 145")
        await asyncio.gather(
            lamp1.set_animation(143),
            lamp2.set_animation(145)
        )
        await asyncio.sleep(3)

        # Return to white
        print("\n5. Returning both to white...")
        await asyncio.gather(
            lamp1.set_rgb(255, 255, 255),
            lamp2.set_rgb(255, 255, 255)
        )

        print("\n✓ Demo complete!")

    except Exception as e:
        print(f"\nError during control: {e}")

    finally:
        # Disconnect both lamps
        print("\nDisconnecting...")
        await asyncio.gather(
            lamp1.disconnect(),
            lamp2.disconnect()
        )
        print("✓ Disconnected from all lamps")


async def simple_multi_lamp_example():
    """Simpler example with error handling"""

    # List of lamp names from your config
    lamp_names = ["Living Room Lamp", "Bedroom Lamp"]

    # Connect to all lamps
    lamps = []
    for name in lamp_names:
        try:
            lamp = LotusLamp(device_name=name)
            if await lamp.connect():
                lamps.append(lamp)
                print(f"✓ Connected to {name}")
            else:
                print(f"✗ Failed to connect to {name}")
        except Exception as e:
            print(f"✗ Error with {name}: {e}")

    if not lamps:
        print("No lamps connected!")
        return

    try:
        # Set all lamps to red
        print("\nSetting all lamps to red...")
        await asyncio.gather(*[lamp.set_rgb(255, 0, 0) for lamp in lamps])
        await asyncio.sleep(2)

        # Set all lamps to green
        print("Setting all lamps to green...")
        await asyncio.gather(*[lamp.set_rgb(0, 255, 0) for lamp in lamps])
        await asyncio.sleep(2)

    finally:
        # Disconnect all
        print("\nDisconnecting all lamps...")
        await asyncio.gather(*[lamp.disconnect() for lamp in lamps])
        print("✓ Done!")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'simple':
        asyncio.run(simple_multi_lamp_example())
    else:
        asyncio.run(control_multiple_lamps())
