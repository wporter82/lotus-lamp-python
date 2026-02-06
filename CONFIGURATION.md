# Configuration Guide

Advanced configuration guide for Lotus Lamp devices.

## Two Usage Patterns

Lotus Lamp supports two main usage patterns:

1. **Library Use** - Integrating into your own Python projects
   - Create config in your project directory (`lotus_lamp_config.json`)
   - Or pass config directly in code (`DeviceConfig(...)`)
   - No "setup" required - configure as part of your app

2. **Standalone Use** - Using CLI tools and examples
   - Run setup wizard once (`python -m lotus_lamp.setup`)
   - Choose to save to global config (`~/.lotus_lamp/config.json`)
   - Tools automatically find your lamp

This guide covers both patterns.

## Configuration Loading

### Search Order

The library searches for configuration files in this order:

1. **Local directory** (project-specific):
   - `./lotus_lamp_config.json`
   - `./.lotus_lamp.json`

2. **User home directory** (global):
   - `~/.lotus_lamp/config.json`

This allows you to have project-specific configurations that override your global settings.

### Loading Feedback

By default, configuration loading is silent. To see where configs are loaded from:

**Option 1: Verbose parameter**
```python
lamp = LotusLamp(verbose=True)
```

**Option 2: Environment variable**
```bash
export LOTUS_LAMP_VERBOSE=1  # Linux/Mac
set LOTUS_LAMP_VERBOSE=1     # Windows
```

Then in your code:
```python
lamp = LotusLamp()  # Will automatically be verbose
```

### Example Output (Verbose Mode)

```
Loading config from: ./lotus_lamp_config.json
✓ Loaded 2 device(s) from: ./lotus_lamp_config.json
Using device: My Lamp
```

## Configuration File Format

### Multiple Devices

```json
{
  "devices": [
    {
      "name": "Living Room Lamp",
      "address": "XX:XX:XX:XX:XX:XX",
      "service_uuid": "0000FFF0-0000-1000-8000-00805F9B34FB",
      "write_char_uuid": "0000FFF3-0000-1000-8000-00805F9B34FB",
      "notify_char_uuid": "0000FFF4-0000-1000-8000-00805F9B34FB"
    },
    {
      "name": "Bedroom Lamp",
      "address": "YY:YY:YY:YY:YY:YY",
      "service_uuid": "0000FFF0-0000-1000-8000-00805F9B34FB",
      "write_char_uuid": "0000FFF3-0000-1000-8000-00805F9B34FB",
      "notify_char_uuid": "0000FFF4-0000-1000-8000-00805F9B34FB"
    }
  ]
}
```

### Single Device (Legacy)

```json
{
  "name": "My Lamp",
  "address": "XX:XX:XX:XX:XX:XX",
  "service_uuid": "0000FFF0-0000-1000-8000-00805F9B34FB",
  "write_char_uuid": "0000FFF3-0000-1000-8000-00805F9B34FB",
  "notify_char_uuid": "0000FFF4-0000-1000-8000-00805F9B34FB"
}
```

## Configuration Methods

### 1. Automatic (Default Locations)

```python
lamp = LotusLamp()  # Searches default locations
```

### 2. Specific Config File

```python
lamp = LotusLamp(config_path="my_config.json")
```

**Error if file not found:**
```
FileNotFoundError: Configuration file not found: my_config.json
Please check the path or run: python -m lotus_lamp.setup
```

### 3. Specific Device by Name

```python
lamp = LotusLamp(device_name="Living Room Lamp")
```

**Error if device not found:**
```
ValueError: Device 'Living Room Lamp' not found in configuration.
Available devices: Bedroom Lamp, Office Lamp

Please run the setup wizard to configure your device:
    python -m lotus_lamp.setup
```

### 4. Explicit Config Object

```python
from lotus_lamp import DeviceConfig

config = DeviceConfig(
    name="My Lamp",
    address="XX:XX:XX:XX:XX:XX",
    service_uuid="0000FFF0-0000-1000-8000-00805F9B34FB",
    write_char_uuid="0000FFF3-0000-1000-8000-00805F9B34FB",
    notify_char_uuid="0000FFF4-0000-1000-8000-00805F9B34FB"
)

lamp = LotusLamp(device_config=config)
```

## Project-Specific Configurations

Create a `lotus_lamp_config.json` in your project directory:

```
my_project/
  ├── lotus_lamp_config.json  # Project-specific config
  ├── main.py
  └── ...
```

This will be loaded instead of your global config when running from that directory.

**Benefits:**
- Different lamps for different projects
- Version control your config
- Easy sharing with team members
- Override global settings

## Managing Multiple Devices

### Setup Multiple Devices

```bash
# Configure first device
python -m lotus_lamp.setup

# Configure second device (adds to existing config)
python -m lotus_lamp.setup

# Configure third device
python -m lotus_lamp.setup
```

### Use Different Devices

```python
# Default (first device in config)
lamp = LotusLamp()

# Specific device
lamp1 = LotusLamp(device_name="Living Room Lamp")
lamp2 = LotusLamp(device_name="Bedroom Lamp")
```

### List Available Devices

```python
from lotus_lamp import ConfigManager

# Use default config file
manager = ConfigManager()

# Specify config file
manager = ConfigManager(config_path="my_config.json")

devices = manager.list_devices()
print(f"Available devices: {devices}")
```

## Troubleshooting

### "Configuration file not found"

**Cause:** Specified path doesn't exist

**Solution:**
```python
# Check the path
from pathlib import Path
print(Path("my_config.json").absolute())

# Or use default locations
lamp = LotusLamp()  # Don't specify path
```

### "No devices found in config file"

**Cause:** Config file is empty or malformed

**Solution:**
1. Check JSON syntax
2. Ensure `devices` array exists
3. Verify required fields (name, service_uuid, etc.)

### Config Loaded from Wrong Location

**Problem:** Not sure which config is being used

**Solution:**
```python
# Enable verbose mode to see
lamp = LotusLamp(verbose=True)
```

Output will show:
```
Loading config from: /home/user/.lotus_lamp/config.json
✓ Loaded 2 device(s) from: /home/user/.lotus_lamp/config.json
Using device: My Lamp
```

### Want to Override Global Config

**Solution:** Create local config file:
```bash
# In your project directory
cp ~/.lotus_lamp/config.json ./lotus_lamp_config.json

# Edit local version
nano lotus_lamp_config.json
```

Now the local version will be used when running from this directory.

## Advanced Configuration

### Programmatic Config Management

```python
from lotus_lamp import ConfigManager, DeviceConfig
from pathlib import Path

# Create manager
manager = ConfigManager()

# Add device
manager.add_device(DeviceConfig(
    name="New Lamp",
    address="AA:BB:CC:DD:EE:FF"
))

# Remove device
manager.remove_device("Old Lamp")

# List devices
print(manager.list_devices())

# Get specific device
config = manager.get_device("New Lamp")

# Save to file
manager.save(Path("my_lamps.json"))
```

### Custom Default Locations

```python
from lotus_lamp.config import ConfigManager
from pathlib import Path

# Override default locations
ConfigManager.DEFAULT_CONFIG_LOCATIONS = [
    Path("/my/custom/path/config.json"),
    Path.cwd() / "config.json",
]

# Now searches custom locations
from lotus_lamp import LotusLamp
lamp = LotusLamp()
```

## Environment Variables

### LOTUS_LAMP_VERBOSE

Enable verbose logging globally:

```bash
# Linux/Mac
export LOTUS_LAMP_VERBOSE=1

# Windows CMD
set LOTUS_LAMP_VERBOSE=1

# Windows PowerShell
$env:LOTUS_LAMP_VERBOSE=1
```

Then all LotusLamp instances will print loading information.

### Future Variables

Planned environment variables:
- `LOTUS_LAMP_CONFIG` - Override config file path
- `LOTUS_LAMP_DEVICE` - Default device name
- `LOTUS_LAMP_DEBUG` - Enable debug logging

## Configuration Security

### Don't Commit Addresses

If version controlling your config, consider:

```json
{
  "devices": [
    {
      "name": "My Lamp",
      "address": null,  // Will be discovered on connection
      "service_uuid": "0000FFF0-0000-1000-8000-00805F9B34FB",
      "write_char_uuid": "0000FFF3-0000-1000-8000-00805F9B34FB",
      "notify_char_uuid": "0000FFF4-0000-1000-8000-00805F9B34FB"
    }
  ]
}
```

The address will be discovered and saved automatically on first connection.

### Git Ignore

Add to `.gitignore`:
```
# Lotus Lamp configs with addresses
.lotus_lamp.json
lotus_lamp_config.json
```

Commit a template instead:
```
lotus_lamp_config.example.json
```

## See Also

- [Main README](README.md) - Quick start and basic usage
- [Testing Guide](TESTING.md) - Testing and development
- [Protocol Documentation](docs/PROTOCOL.md) - BLE protocol details
- [Mode Reference](docs/MODES.md) - All 213 modes documented
