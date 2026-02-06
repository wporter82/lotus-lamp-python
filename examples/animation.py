#!/usr/bin/env python3

import asyncio
import sys
from lotus_lamp import LotusLamp

# Platform-specific keyboard input handling
if sys.platform == 'win32':
    import msvcrt
    def kbhit():
        return msvcrt.kbhit()
else:
    import select
    def kbhit():
        return select.select([sys.stdin], [], [], 0)[0] != []

async def interruptible_sleep(duration):
    """Sleep for duration seconds, but check for key presses every 0.1 seconds"""
    elapsed = 0
    while elapsed < duration:
        if kbhit():
            return True  # Key was pressed
        await asyncio.sleep(0.1)
        elapsed += 0.1
    return False  # No key pressed

async def main():
    print("=== Police animation ===")

    lamp = LotusLamp()
    await lamp.connect()

    print("Sending power on command...")
    await lamp.power_on()
    
    print("Playing")
    print("\nPress any key to stop...")

    # loop start
    stop = False
    while not stop:
        await lamp.set_rgb(255, 0, 0)  # Set color to red
        if await interruptible_sleep(0.25):
            stop = True
            break
        await lamp.set_rgb(0, 0, 255)  # Set color to blue
        if await interruptible_sleep(0.25):
            stop = True
            break
    # loop end

    print("\nStopping...")

    print("Sending power off command...")
    await lamp.power_off()

    await lamp.disconnect()


if __name__ == '__main__':
    asyncio.run(main())