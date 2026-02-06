# Lotus Lamp Examples

This directory contains example scripts demonstrating various use cases for the Lotus Lamp library.

## Prerequisites

**First-time setup is required!** Before running any examples:

```bash
python -m lotus_lamp.setup
```

This will scan for your lamp and save the configuration.

## Examples

### animation.py
**Basic lamp control with keyboard interrupt**

Demonstrates:
- Connecting to lamp
- Setting RGB colors
- Creating animated patterns
- Handling keyboard interrupts

```bash
python examples/animation.py
```

### browser.py
**Interactive mode browser**

Browse and test all 213 RGB animation modes organized by category.

Demonstrates:
- Using the modes module
- Interactive lamp control
- Mode categories and names

```bash
python examples/browser.py
```

### discover_and_configure.py
**Device discovery and configuration (demonstration)**

NOTE: This is for learning purposes. Use `python -m lotus_lamp.setup` for actual setup.

Demonstrates:
- Using the scanner API
- Using the advanced scanner for UUID discovery
- Creating and saving configurations
- Testing connections

```bash
python examples/discover_and_configure.py
```

### discover_uuids.py
**UUID discovery example**

Shows how to discover UUIDs for unknown lamp models.

Demonstrates:
- Scanning for devices
- Reading GATT structure
- Auto-identifying UUIDs
- Generating configurations

```bash
python examples/discover_uuids.py
```

### multi_device.py
**Control multiple lamps**

Demonstrates controlling multiple lamps simultaneously.

Prerequisites:
- Configure multiple devices first (run setup multiple times)

Demonstrates:
- Loading multiple device configurations
- Synchronized control
- Independent lamp control
- Using asyncio.gather() for parallel operations

```bash
python examples/multi_device.py
```

## Common Patterns

### Basic Usage

```python
from lotus_lamp import LotusLamp
import asyncio

async def main():
    lamp = LotusLamp()  # Loads saved configuration
    await lamp.connect()

    # Your code here
    await lamp.set_rgb(255, 0, 0)  # Red

    await lamp.disconnect()

asyncio.run(main())
```

### Using a Specific Device

```python
lamp = LotusLamp(device_name="Living Room Lamp")
await lamp.connect()
```

### Error Handling

```python
try:
    lamp = LotusLamp()
    await lamp.connect()
    # ... use lamp ...
except ValueError as e:
    print(f"Configuration error: {e}")
    print("Run: python -m lotus_lamp.setup")
finally:
    await lamp.disconnect()
```

### Multiple Devices

```python
lamp1 = LotusLamp(device_name="Living Room")
lamp2 = LotusLamp(device_name="Bedroom")

await asyncio.gather(
    lamp1.connect(),
    lamp2.connect()
)

# Control both simultaneously
await asyncio.gather(
    lamp1.set_rgb(255, 0, 0),
    lamp2.set_rgb(0, 0, 255)
)
```

## Troubleshooting

### "No Lotus Lamp devices configured" Error

Run the setup wizard:
```bash
python -m lotus_lamp.setup
```

### Can't Find Device

1. Make sure lamp is powered on
2. Check Bluetooth is enabled
3. Try the advanced scanner:
   ```bash
   python -m lotus_lamp.advanced_scanner
   ```

### Import Errors

Make sure you're running from the project root or have installed the package:
```bash
pip install -e .
```

## Creating Your Own Examples

Template:

```python
#!/usr/bin/env python3
"""
Your Example Title

Brief description of what this example demonstrates.
"""

import asyncio
from lotus_lamp import LotusLamp


async def main():
    """Your example logic"""
    lamp = LotusLamp()

    try:
        if not await lamp.connect():
            print("Failed to connect")
            return

        # Your code here
        await lamp.set_rgb(255, 0, 0)

    finally:
        await lamp.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
```

## More Information

- **Full Documentation**: See [../README.md](../README.md)
- **Protocol Details**: See [../docs/PROTOCOL.md](../docs/PROTOCOL.md)
