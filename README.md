# Lotus Lamp Python 🏮

A Python library for controlling Lotus Lamp RGB LED strips via Bluetooth Low Energy (BLE).

Supports Lotus Lamp devices using the Lotus Lamp X app protocol. Complete protocol reverse-engineered and documented!

## Features ✨

- 🎨 **RGB Color Control** - 16.7 million colors (full 24-bit RGB)
- 🌈 **213 Built-in Animations** - All modes with official names from the app
- 💡 **Brightness Control** - 0-100% adjustable brightness
- ⚡ **Speed Control** - 0-100% animation speed adjustment
- 🔍 **Mode Search** - Find animations by name or category
- 📁 **8 Categories** - Organized like the official app (basic, flow, run, etc.)
- 🔧 **Auto UUID Discovery** - Automatically finds connection details for any lamp model
- 🚀 **Easy Setup** - Interactive wizard for first-time configuration
- 📖 **Complete Documentation** - Full BLE protocol documented

## Quick Start 🚀

### Installation

```bash
pip install lotus-lamp
```

Or install from source:
```bash
git clone https://github.com/wporter82/lotus-lamp-python.git
cd lotus-lamp-python
pip install -e .
```

### Setup

**Two ways to use Lotus Lamp:**

#### Option A: As a Library (In Your Own Project)

Simply create a config file in your project directory or pass config directly:

```python
from lotus_lamp import LotusLamp, DeviceConfig

# Option 1: Provide config directly (no setup needed)
config = DeviceConfig(
    name="My Lamp",
    address="XX:XX:XX:XX:XX:XX"  # Your lamp's BLE address
)
lamp = LotusLamp(device_config=config)

# Option 2: Create lotus_lamp_config.json in your project
# Then just use: lamp = LotusLamp()
```

Need help finding your lamp's address and UUIDs? Run the setup wizard (see below).

#### Option B: As a Standalone Tool (CLI/Examples)

For using the included CLI tools and examples, run the setup wizard once:

```bash
python -m lotus_lamp.setup
```

This gives you the option to save a global config to `~/.lotus_lamp/config.json` for the CLI tools.

#### Setup Wizard (Optional Helper)

The setup wizard helps you find your lamp and generate a config file:

```bash
python -m lotus_lamp.setup
```

The wizard will:
1. 🔍 Scan for your lamp
2. 🔧 Automatically discover connection details
3. 💾 Offer to save to local project OR global location

You can always create config files manually or programmatically.

### Basic Usage

```python
from lotus_lamp import LotusLamp
import asyncio

async def main():
    # Create lamp controller
    lamp = LotusLamp()

    # Connect to lamp
    await lamp.connect()

    # Set color to red
    await lamp.set_rgb(255, 0, 0)

    # Set animation mode (W-R-W Flow)
    await lamp.set_animation(143)

    # Adjust brightness
    await lamp.set_brightness(75)

    # Adjust animation speed
    await lamp.set_speed(50)

    # Disconnect
    await lamp.disconnect()

asyncio.run(main())
```

### Using Mode Names

```python
from lotus_lamp import LotusLamp, get_mode_by_category_index, search_modes
import asyncio

async def main():
    lamp = LotusLamp()
    await lamp.connect()

    # Get mode by category and index
    flow_mode = get_mode_by_category_index('flow', 1)  # First flow mode
    await lamp.set_animation(flow_mode)

    # Search for modes
    cyan_modes = search_modes("cyan")
    for mode_num, name, category in cyan_modes:
        print(f"Mode {mode_num}: {name} ({category})")
        await lamp.set_animation(mode_num)
        await asyncio.sleep(2)

    await lamp.disconnect()

asyncio.run(main())
```

### Interactive Browser

Explore all 213 modes interactively:

```bash
python examples/browser.py
```

## Mode Categories 📂

All 213 animation modes organized into 8 categories:

| Category | Modes | Description |
|----------|-------|-------------|
| **basic** | 47 | Auto cycle, magic colors, jumps, gradients, strobes |
| **trans** | 20 | Light/dark transitions |
| **tail** | 16 | Comet/tailing effects |
| **water** | 18 | Running water patterns |
| **curtain** | 20 | Opening/closing curtain effects |
| **run** | 34 | Forward running (7-color in various backgrounds) |
| **runback** | 34 | Backward running (7-color in various backgrounds) |
| **flow** | 24 | White-to-color-to-white breathing effects |

### Popular Modes

```python
await lamp.set_animation(0)    # Auto Play
await lamp.set_animation(143)  # W-R-W Flow
await lamp.set_animation(138)  # 7-Color in Cyan Run Back
await lamp.set_animation(157)  # R-W-R Flow
```

## API Reference 📚

### LotusLamp Class

#### Connection
- `await connect()` - Connect to lamp (auto-discovers device)
- `await disconnect()` - Disconnect from lamp

#### Color Control
- `await set_rgb(r, g, b)` - Set RGB color (0-255 per channel)
- `await set_color(name)` - Set by name ('red', 'blue', 'green', etc.)

#### Animation Control
- `await set_animation(mode)` - Set animation mode (0-212)
- `await set_brightness(level)` - Set brightness (0-100)
- `await set_speed(level)` - Set animation speed (0-100)

#### Power Control
- `await power_on()` - Turn lamp on
- `await power_off()` - Turn lamp off

#### Convenience Methods
- `await pulse(r, g, b, times, duration)` - Pulse a color
- `await rainbow_cycle(duration, steps)` - Rainbow color cycle

### Mode Functions

- `get_mode_name(mode_num)` - Get official name for mode
- `get_mode_category(mode_num)` - Get category for mode
- `get_mode_by_category_index(category, index)` - Get mode by category position
- `search_modes(query)` - Search modes by name
- `list_all_categories()` - Print all categories
- `list_category_modes(category)` - Print modes in category

## Requirements 📋

- Python 3.7+
- `bleak>=0.21.0` (Bluetooth Low Energy library)

Works on:
- ✅ Windows 10/11
- ✅ macOS
- ✅ Linux (with BlueZ)

## Hardware Compatibility 🔌

### Tested Devices
- **MELK-OA10 5F** - Fully tested and working

### Likely Compatible
Any RGB LED strip lamp using the **Lotus Lamp X** app (com.szelk.ledlamppro) should work, but mode numbers may vary by model.

**Device Name Format:** `MELK-OA10   5F` (note: spaces in name)

## Examples 💡

See the `examples/` directory for:
- `browser.py` - Interactive mode browser
- More examples coming soon!

## Documentation 📖

**→ [Complete Documentation Guide](https://github.com/wporter82/lotus-lamp-python/blob/main/DOCUMENTATION.md)** - Index of all documentation

### User Documentation
- [Configuration Guide](https://github.com/wporter82/lotus-lamp-python/blob/main/CONFIGURATION.md) - Advanced configuration options
- [Mode Reference](https://github.com/wporter82/lotus-lamp-python/blob/main/docs/MODES.md) - All 213 modes with categories
- [Protocol Documentation](https://github.com/wporter82/lotus-lamp-python/blob/main/docs/PROTOCOL.md) - Complete BLE protocol specification

### Developer Documentation
- [Testing Guide](https://github.com/wporter82/lotus-lamp-python/blob/main/TESTING.md) - Running and writing tests

## Development 🛠️

### Setup Development Environment

```bash
git clone https://github.com/wporter82/lotus-lamp-python.git
cd lotus-lamp-python
pip install -e ".[dev]"
```

### Project Structure

```
lotus-lamp-python/
├── lotus_lamp/          # Main package
│   ├── __init__.py      # Package initialization
│   ├── controller.py    # LotusLamp class
│   ├── modes.py         # Mode lookup functions
│   └── data/            # Mode data (JSON)
├── examples/            # Example scripts
├── docs/                # Documentation
├── README.md
├── LICENSE
├── requirements.txt
├── setup.py
└── pyproject.toml
```

## Contributing 🤝

Contributions welcome! Please feel free to submit a Pull Request.

### Areas for Contribution
- Additional example scripts
- Support for other lamp models
- Enhanced documentation
- Bug fixes and improvements

## License 📄

MIT License - see [LICENSE](https://github.com/wporter82/lotus-lamp-python/blob/main/LICENSE) file for details

## Credits 🙏

- Reverse engineered from the **Lotus Lamp X** Android app (com.szelk.ledlamppro)
- Protocol documentation through APK decompilation and systematic testing

## Disclaimer ⚠️

This is an unofficial library created through reverse engineering. Not affiliated with or endorsed by the lamp manufacturer or app developer.

Use at your own risk. The library sends standard BLE commands but I cannot guarantee compatibility with all hardware variants.

## Troubleshooting 🔧

### Lamp not found
- Ensure lamp is powered on and in range
- Check that Bluetooth is enabled on your computer
- Verify the device name matches exactly (including spaces)

### Connection fails
- Lamp only accepts one BLE connection at a time
- Disconnect official app before using this library
- Try power cycling the lamp

### Commands not working
- Ensure you're connected before sending commands
- Check that you're using the correct mode numbers (0-212)
- Some modes may look similar or vary by hardware revision

## Support 💬

- **Issues:** [GitHub Issues](https://github.com/wporter82/lotus-lamp-python/issues)
- **Discussions:** [GitHub Discussions](https://github.com/wporter82/lotus-lamp-python/discussions)

---

Made with ❤️ by Wayne Porter

**Star ⭐ this repo if you find it useful!**
