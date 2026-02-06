#!/usr/bin/env python3
"""
Complete Lotus Lamp Controller - CORRECTED COMMAND FORMATS
All commands use 9-byte format with 0xFF for unused parameters
"""

"""
Lotus Lamp BLE Controller

Main controller class for communicating with Lotus Lamp RGB LED strips.
"""

import asyncio
import os
from bleak import BleakClient, BleakScanner
from typing import Optional, Tuple, Union
import colorsys
from pathlib import Path

from .config import DeviceConfig, ConfigManager
from .modes import get_mode_name, list_category_modes, CATEGORIES

class LotusLamp:
    """
    Controller for Lotus Lamp RGB LED strips via BLE

    Supports MELK-OA10 5F and similar models using the Lotus Lamp X app protocol.

    Example:
        >>> lamp = LotusLamp()
        >>> await lamp.connect()
        >>> await lamp.set_rgb(255, 0, 0)  # Red
        >>> await lamp.set_animation(143)   # W-R-W Flow
        >>> await lamp.set_brightness(75)
        >>> await lamp.disconnect()

    You can also specify a custom device configuration:
        >>> config = DeviceConfig(name="My Lamp", address="XX:XX:XX:XX:XX:XX")
        >>> lamp = LotusLamp(device_config=config)

    Or load from a config file:
        >>> lamp = LotusLamp(config_path="my_config.json")
    """

    # Default UUIDs (common for many Lotus Lamps)
    DEFAULT_SERVICE_UUID = "0000FFF0-0000-1000-8000-00805F9B34FB"
    DEFAULT_WRITE_CHAR_UUID = "0000FFF3-0000-1000-8000-00805F9B34FB"
    DEFAULT_NOTIFY_CHAR_UUID = "0000FFF4-0000-1000-8000-00805F9B34FB"

    def __init__(self,
                 device_config: Optional[DeviceConfig] = None,
                 config_path: Optional[Union[str, Path]] = None,
                 device_name: Optional[str] = None,
                 verbose: bool = False):
        """
        Initialize Lotus Lamp controller

        Args:
            device_config: Optional DeviceConfig object with device settings
            config_path: Optional path to config file to load
            device_name: Optional device name to select from config file
            verbose: If True, print configuration loading messages

        Raises:
            ValueError: If no configuration is found and no parameters are provided
            FileNotFoundError: If specified config_path doesn't exist

        Note:
            On first use, you must run the setup wizard to configure your device:
                python -m lotus_lamp.setup
        """
        self.device = None
        self.client: Optional[BleakClient] = None
        self._connected = False

        # Check environment variable for debug mode
        if os.getenv('LOTUS_LAMP_VERBOSE', '').lower() in ('1', 'true', 'yes'):
            verbose = True

        self.verbose = verbose

        # Determine device configuration
        if device_config:
            # Use provided config
            self.config = device_config
            if verbose:
                print(f"Using provided DeviceConfig: {device_config.name}")
        elif config_path:
            # Load from specified config file - will raise FileNotFoundError if not found
            manager = ConfigManager(Path(config_path), verbose=verbose)
            if device_name:
                self.config = manager.get_device(device_name)
                if not self.config:
                    available = manager.list_devices()
                    raise ValueError(
                        f"Device '{device_name}' not found in {config_path}\n"
                        f"Available devices: {', '.join(available) if available else 'none'}"
                    )
            else:
                self.config = manager.get_default_device()
                if not self.config:
                    raise ValueError(f"No devices found in config file: {config_path}")
                if verbose:
                    print(f"Using device: {self.config.name}")
        else:
            # Try to load from default locations
            manager = ConfigManager(verbose=verbose)
            if device_name:
                self.config = manager.get_device(device_name)
                if not self.config:
                    available = manager.list_devices()
                    raise ValueError(
                        f"Device '{device_name}' not found in configuration.\n"
                        f"Available devices: {', '.join(available) if available else 'none'}\n\n"
                        f"Please run the setup wizard to configure your device:\n"
                        f"    python -m lotus_lamp.setup\n"
                    )
                if verbose:
                    print(f"Using device: {self.config.name}")
            else:
                self.config = manager.get_default_device()
                if not self.config:
                    raise ValueError(
                        "No Lotus Lamp devices configured.\n\n"
                        "Option 1: Provide config directly (recommended for library use):\n"
                        "    from lotus_lamp import LotusLamp, DeviceConfig\n"
                        "    config = DeviceConfig(name='My Lamp', address='XX:XX:XX:XX:XX:XX')\n"
                        "    lamp = LotusLamp(device_config=config)\n\n"
                        "Option 2: Create a config file (lotus_lamp_config.json):\n"
                        "    {\n"
                        '      "devices": [{"name": "My Lamp", "address": "XX:XX:XX:XX:XX:XX"}]\n'
                        "    }\n\n"
                        "Option 3: Run setup wizard to find and configure your lamp:\n"
                        "    python -m lotus_lamp.setup\n"
                    )
                if verbose:
                    print(f"Using device: {self.config.name}")

    @property
    def DEVICE_NAME(self):
        """Device name (for backwards compatibility)"""
        return self.config.name

    @property
    def SERVICE_UUID(self):
        """Service UUID (for backwards compatibility)"""
        return self.config.service_uuid

    @property
    def WRITE_CHAR_UUID(self):
        """Write characteristic UUID (for backwards compatibility)"""
        return self.config.write_char_uuid

    @property
    def NOTIFY_CHAR_UUID(self):
        """Notify characteristic UUID (for backwards compatibility)"""
        return self.config.notify_char_uuid

    async def scan(self, timeout: float = 5.0) -> bool:
        """Scan for the Lotus Lamp device"""
        print(f"Scanning for {self.DEVICE_NAME}...")
        devices = await BleakScanner.discover(timeout=timeout)

        # If we have a specific address, look for it
        if self.config.address:
            for device in devices:
                if device.address.upper() == self.config.address.upper():
                    self.device = device
                    print(f"Found: {device.name} ({device.address})")
                    return True
        else:
            # Look for device by name
            for device in devices:
                if self.DEVICE_NAME in str(device.name):
                    self.device = device
                    print(f"Found: {device.name} ({device.address})")
                    # Save the address for future use
                    self.config.address = device.address
                    return True

        print("Device not found!")
        return False

    async def connect(self) -> bool:
        """Connect to the lamp"""
        # If we have a saved address, try connecting directly
        if self.config.address and not self.device:
            print(f"Connecting to {self.config.name}...")
            try:
                self.client = BleakClient(self.config.address)
                await self.client.connect()
                self._connected = True
                print("Connected!")
                return True
            except Exception as e:
                print(f"Failed to connect to saved address: {e}")
                print("Scanning for device...")
                self.config.address = None  # Clear invalid address

        # Fall back to scanning
        if not self.device:
            if not await self.scan():
                return False

        print(f"Connecting to {self.device.name}...")
        self.client = BleakClient(self.device.address)
        await self.client.connect()
        self._connected = True
        print("Connected!")
        return True

    async def disconnect(self):
        """Disconnect from the lamp"""
        if self.client and self._connected:
            await self.client.disconnect()
            self._connected = False
            print("Disconnected")

    async def _send_command(self, command: bytes, delay: float = 0.1):
        """Send a command to the lamp"""
        if not self._connected:
            raise ConnectionError("Not connected to lamp")

        await self.client.write_gatt_char(self.WRITE_CHAR_UUID, command, response=False)
        await asyncio.sleep(delay)

    # ==================== RGB COLOR CONTROL ====================

    async def set_rgb(self, r: int, g: int, b: int):
        """
        Set RGB color

        Args:
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)

        Command: 7E 07 05 03 RR GG BB 10 EF
        Protocol length: 7, Command type: 5 (COLOR)
        Parameters: {3, r, g, b, 16}
        """
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))

        command = bytes([0x7E, 0x07, 0x05, 0x03, r, g, b, 0x10, 0xEF])
        await self._send_command(command)

    async def set_color(self, color: str):
        """Set color by name"""
        colors = {
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'white': (255, 255, 255),
            'yellow': (255, 255, 0),
            'cyan': (0, 255, 255),
            'magenta': (255, 0, 255),
            'orange': (255, 165, 0),
            'purple': (128, 0, 128),
            'pink': (255, 192, 203),
            'off': (0, 0, 0),
        }

        color = color.lower()
        if color in colors:
            r, g, b = colors[color]
            await self.set_rgb(r, g, b)
        else:
            raise ValueError(f"Unknown color: {color}")

    # ==================== BRIGHTNESS CONTROL ====================

    async def set_brightness(self, brightness: int):
        """
        Set brightness level

        Args:
            brightness: Brightness level (0-100)

        Command: 7E 07 01 XX FF FF FF 00 EF
        Protocol length: 7, Command type: 1 (BRIGHTNESS)
        Parameters: {brightness}
        Unused positions: 0xFF
        """
        brightness = max(0, min(100, brightness))
        command = bytes([0x7E, 0x07, 0x01, brightness, 0xFF, 0xFF, 0xFF, 0x00, 0xEF])
        await self._send_command(command)

    # ==================== SPEED CONTROL ====================

    async def set_speed(self, speed: int):
        """
        Set animation speed

        Args:
            speed: Speed level (0-100)

        Command: 7E 04 02 XX FF FF FF 00 EF
        Protocol length: 4, Command type: 2 (SPEED)
        Parameters: {speed}
        Unused positions: 0xFF

        NOTE: Only affects animations, not solid RGB colors!
        """
        speed = max(0, min(100, speed))
        command = bytes([0x7E, 0x04, 0x02, speed, 0xFF, 0xFF, 0xFF, 0x00, 0xEF])
        await self._send_command(command)

    # ==================== ANIMATION MODES ====================

    async def set_animation(self, mode: int):
        """
        Set animation mode

        Args:
            mode: Animation mode (1-233)

        Command: 7E 07 03 XX FF FF FF 00 EF
        Protocol length: 7, Command type: 3 (MODE)
        Parameters: {mode}
        """
        mode = max(1, min(233, mode))
        command = bytes([0x7E, 0x07, 0x03, mode, 0xFF, 0xFF, 0xFF, 0x00, 0xEF])
        await self._send_command(command)

    # ==================== POWER CONTROL ====================

    async def power_on(self):
        """
        Turn lamp ON

        Command: 7E ?? 04 01 00 FF FF 00 EF
        Command type: 4 (ON_OFF)
        Parameters: {1, 0}
        """
        # Try with protocol length 7 (default)
        command = bytes([0x7E, 0x07, 0x04, 0x01, 0x00, 0xFF, 0xFF, 0x00, 0xEF])
        await self._send_command(command, delay=0.5)

    async def power_off(self):
        """
        Turn lamp OFF

        Command: 7E ?? 04 00 00 FF FF 00 EF
        Command type: 4 (ON_OFF)
        Parameters: {0, 0}
        """
        command = bytes([0x7E, 0x07, 0x04, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0xEF])
        await self._send_command(command, delay=0.5)

    # ==================== CONVENIENCE METHODS ====================

    async def pulse(self, r: int, g: int, b: int, times: int = 3, duration: float = 1.0):
        """Pulse a color"""
        for _ in range(times):
            await self.set_rgb(r, g, b)
            await asyncio.sleep(duration / 2)
            await self.set_rgb(0, 0, 0)
            await asyncio.sleep(duration / 2)

    async def rainbow_cycle(self, duration: float = 5.0, steps: int = 30):
        """Cycle through rainbow colors"""
        delay = duration / steps
        for i in range(steps):
            hue = i / steps
            r, g, b = self._hsv_to_rgb(hue, 1.0, 1.0)
            await self.set_rgb(r, g, b)
            await asyncio.sleep(delay)

    @staticmethod
    def _hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Convert HSV to RGB"""
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return int(r * 255), int(g * 255), int(b * 255)


# ==================== DEMO ====================

async def demo():
    """Demonstration of lamp control"""
    lamp = LotusLamp()

    try:
        if not await lamp.connect():
            return

        print("\n" + "="*60)
        print("LOTUS LAMP DEMO - CORRECTED FORMATS")
        print("="*60)

        # Test RGB colors
        print("\n1. Testing RGB colors...")
        colors = [
            ('Red', 255, 0, 0),
            ('Green', 0, 255, 0),
            ('Blue', 0, 0, 255),
            ('White', 255, 255, 255),
        ]

        for name, r, g, b in colors:
            print(f"   {name}...")
            await lamp.set_rgb(r, g, b)
            await asyncio.sleep(1.0)

        # Test brightness with 9-byte format
        print("\n2. Testing brightness (9-byte format)...")
        await lamp.set_rgb(255, 255, 255)
        for brightness in [100, 50, 25, 75, 100]:
            print(f"   Brightness: {brightness}%")
            await lamp.set_brightness(brightness)
            await asyncio.sleep(0.8)

        # Test animation with speed control
        print("\n3. Testing animation with speed control...")
        print("   Setting animation mode 1...")
        await lamp.set_animation(1)
        await asyncio.sleep(2.0)

        print("   Slowing down (speed 20%)...")
        await lamp.set_speed(20)
        await asyncio.sleep(2.0)

        print("   Speeding up (speed 100%)...")
        await lamp.set_speed(100)
        await asyncio.sleep(2.0)

        # Rainbow cycle
        print("\n4. Rainbow cycle...")
        await lamp.rainbow_cycle(duration=3.0)

        print("\n" + "="*60)
        print("Demo complete!")
        print("="*60)

    finally:
        await lamp.disconnect()


async def interactive():
    """Interactive lamp control"""
    lamp = LotusLamp()

    try:
        if not await lamp.connect():
            return

        print("\n" + "="*60)
        print("INTERACTIVE LOTUS LAMP CONTROL")
        print("="*60)
        print("\nCommands:")
        print("  rgb R G B      - Set RGB color (0-255)")
        print("  color NAME     - Set color by name")
        print("  bright N       - Set brightness (0-100)")
        print("  speed N        - Set speed (0-100, animations only)")
        print("  anim N         - Set animation mode by number (0-233)")
        print("  mode N/NAME    - Set mode by number or search by name")
        print("  list           - List animation modes by category")
        print("  on             - Power on")
        print("  off            - Power off")
        print("  rainbow        - Rainbow cycle")
        print("  quit           - Exit")
        print()

        while True:
            try:
                cmd_line = input("lamp> ").strip()
                if not cmd_line:
                    continue

                # Split but preserve case for some commands
                parts = cmd_line.split()
                cmd = parts[0].lower()

                if cmd == 'quit':
                    break
                elif cmd == 'list':
                    print("\nAvailable Animation Modes:")
                    print("="*60)

                    # Show a sample from each category
                    for category_name, category_label in CATEGORIES.items():
                        modes = list_category_modes(category_name)
                        if modes:
                            print(f"\n  {category_label} ({len(modes)} modes):")
                            # Show first 5 modes from each category
                            for mode_num, mode_name in modes[:5]:
                                print(f"    {mode_num}: {mode_name}")
                            if len(modes) > 5:
                                print(f"    ... and {len(modes) - 5} more")

                    print("\nTo see all modes in a category, use:")
                    print("  from lotus_lamp import list_category_modes")
                    print("  modes = list_category_modes('flow')")
                    print("\nFor more info, see the documentation.")
                    print()
                elif cmd == 'rgb' and len(parts) == 4:
                    r, g, b = int(parts[1]), int(parts[2]), int(parts[3])
                    await lamp.set_rgb(r, g, b)
                    print(f"✓ RGB({r}, {g}, {b})")
                elif cmd == 'color' and len(parts) == 2:
                    await lamp.set_color(parts[1].lower())
                    print(f"✓ {parts[1]}")
                elif cmd == 'bright' and len(parts) == 2:
                    await lamp.set_brightness(int(parts[1]))
                    print(f"✓ Brightness {parts[1]}%")
                elif cmd == 'speed' and len(parts) == 2:
                    await lamp.set_speed(int(parts[1]))
                    print(f"✓ Speed {parts[1]}%")
                elif cmd == 'anim' and len(parts) == 2:
                    await lamp.set_animation(int(parts[1]))
                    print(f"✓ Animation {parts[1]}")
                elif cmd == 'mode' and len(parts) >= 2:
                    # Join remaining parts for multi-word mode names
                    mode_input = ' '.join(parts[1:])
                    # Try as number first
                    try:
                        mode_num = int(mode_input)
                        await lamp.set_animation(mode_num)
                        mode_name = get_mode_name(mode_num)
                        if mode_name:
                            print(f"✓ Mode {mode_num}: {mode_name}")
                        else:
                            print(f"✓ Mode {mode_num}")
                    except ValueError:
                        # Search for mode by name
                        from .modes import search_modes
                        results = search_modes(mode_input)
                        if results:
                            # Use first match
                            mode_num, mode_name, category = results[0]
                            await lamp.set_animation(mode_num)
                            print(f"✓ Mode {mode_num}: {mode_name}")
                        else:
                            print(f"✗ No mode found matching '{mode_input}'")
                elif cmd == 'on':
                    await lamp.power_on()
                    print("✓ Power ON")
                elif cmd == 'off':
                    await lamp.power_off()
                    print("✓ Power OFF")
                elif cmd == 'rainbow':
                    print("✓ Rainbow cycle...")
                    await lamp.rainbow_cycle()
                else:
                    print("Invalid command")

            except (ValueError, IndexError) as e:
                print(f"Error: {e}")
            except KeyboardInterrupt:
                break

    finally:
        await lamp.disconnect()


if __name__ == '__main__':
    import sys

    try:
        if len(sys.argv) > 1 and sys.argv[1] == 'demo':
            asyncio.run(demo())
        else:
            asyncio.run(interactive())
    except ValueError as e:
        # Handle unconfigured device error gracefully
        if "No Lotus Lamp devices configured" in str(e):
            print("\n" + "="*80)
            print("SETUP REQUIRED")
            print("="*80)
            print("\nNo Lotus Lamp devices are configured yet.")
            print("\nTo use the interactive controller, you must first configure your device.")
            print("\nPlease run the setup wizard:")
            print("    python -m lotus_lamp.setup")
            print("\nThe wizard will:")
            print("  1. Scan for your lamp")
            print("  2. Discover connection details")
            print("  3. Save the configuration")
            print("\nAfter setup, you can run this controller again.")
            print("="*80)
            sys.exit(1)
        else:
            # Re-raise other ValueErrors
            raise
