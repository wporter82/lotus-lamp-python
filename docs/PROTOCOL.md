# Lotus Lamp RGB LED - Complete BLE Protocol Documentation

**Device:** MELK-OA10 5F (Tyute-branded RGB LED Lamp)
**App:** Lotus Lamp X (com.szelk.ledlamppro)
**Protocol:** Fully reverse-engineered and tested
**Date:** February 2026

---

## Table of Contents
1. [BLE Connection Details](#ble-connection-details)
2. [Command Format](#command-format)
3. [All Commands](#all-commands)
4. [RGB Color Control](#rgb-color-control)
5. [Python Examples](#python-examples)

---

## BLE Connection Details

### Device Information
```
Device Name:    MELK-OA10   5F
                (Note: There are spaces in the name)

Service UUID:   0000FFF0-0000-1000-8000-00805F9B34FB
Write Char:     0000FFF3-0000-1000-8000-00805F9B34FB (WRITE NO RESPONSE)
Notify Char:    0000FFF4-0000-1000-8000-00805F9B34FB (NOTIFY)
```

### Connection Notes
- The lamp accepts **only ONE** BLE connection at a time
- Connecting with a new client disconnects previous connections
- No authentication or pairing required
- Commands use "Write Without Response" (GATT opcode 0x52)

---

## Command Format

**IMPORTANT:** All commands are **9 bytes** (not 8)!

```
┌─────────┬──────────┬──────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐
│  Header │ Protocol │ Command  │ Param 1 │ Param 2 │ Param 3 │ Param 4 │ Fixed   │ Footer  │
│   0x7E  │   Len    │   Type   │         │         │         │         │  0x00   │  0xEF   │
└─────────┴──────────┴──────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘
  Byte 0     Byte 1     Byte 2    Byte 3    Byte 4    Byte 5    Byte 6    Byte 7    Byte 8
```

**Critical Notes:**
- All commands are **9 bytes total** (verified from app source code)
- All commands start with `7E` (header)
- All commands end with `EF` (footer) at position 8
- **Byte 7 is always `00`**
- Byte 1 (Protocol Length) varies by command type:
  - BRIGHTNESS: `07`
  - SPEED: `04` ⚠️
  - MODE: `06` or `07` (depends on parameters)
  - COLOR: `07`
  - ON_OFF: `07`
- Byte 2 is the command type (1-6)
- Bytes 3-6 are parameters (command-specific)
- **Unused parameter bytes MUST be `FF` (not `00`)** ⚠️
- All values are in hexadecimal

---

## All Commands

### 1. RGB Color Control ⭐

**FULLY WORKING - Tested and confirmed!**

```
Command Format: 7E 07 05 03 RR GG BB 10 EF

Where:
  07 = Protocol length
  05 = COLOR command type
  03 = Color mode parameter
  RR = Red value (00-FF / 0-255)
  GG = Green value (00-FF / 0-255)
  BB = Blue value (00-FF / 0-255)
  10 = Mode flag (16 decimal)
```

**Examples:**
```
Red:     7E 07 05 03 FF 00 00 10 EF
Green:   7E 07 05 03 00 FF 00 10 EF
Blue:    7E 07 05 03 00 00 FF 10 EF
White:   7E 07 05 03 FF FF FF 10 EF
Yellow:  7E 07 05 03 FF FF 00 10 EF
Cyan:    7E 07 05 03 00 FF FF 10 EF
Magenta: 7E 07 05 03 FF 00 FF 10 EF
Orange:  7E 07 05 03 FF A5 00 10 EF
Purple:  7E 07 05 03 80 00 80 10 EF
Black:   7E 07 05 03 00 00 00 10 EF (LEDs off)
```

---

### 2. Brightness Control

**WORKING - Tested and confirmed!**

```
Command Format: 7E 07 01 XX FF FF FF 00 EF

Where:
  07 = Protocol length
  01 = BRIGHTNESS command type
  XX = Brightness level (00-64 hex / 0-100 decimal)
  FF FF FF = Unused parameter bytes (MUST be FF!)
  00 = Fixed byte 7
  EF = Footer
```

**Examples:**
```
100% brightness: 7E 07 01 64 FF FF FF 00 EF
75%  brightness: 7E 07 01 4B FF FF FF 00 EF
50%  brightness: 7E 07 01 32 FF FF FF 00 EF
25%  brightness: 7E 07 01 19 FF FF FF 00 EF
0%   brightness: 7E 07 01 00 FF FF FF 00 EF
```

**Notes:**
- Brightness affects current color/animation
- Does NOT change the current mode
- Changes take effect immediately

---

### 3. Speed Control

**WORKING - Tested and confirmed!**

```
Command Format: 7E 04 02 XX FF FF FF 00 EF

Where:
  04 = Protocol length (⚠️ Different from other commands!)
  02 = SPEED command type
  XX = Speed level (00-64 hex / 0-100 decimal)
  FF FF FF = Unused parameter bytes (MUST be FF!)
  00 = Fixed byte 7
  EF = Footer
```

**Examples:**
```
Fastest: 7E 04 02 64 FF FF FF 00 EF  (100%)
Fast:    7E 04 02 50 FF FF FF 00 EF  (80%)
Medium:  7E 04 02 32 FF FF FF 00 EF  (50%)
Slow:    7E 04 02 14 FF FF FF 00 EF  (20%)
Slowest: 7E 04 02 00 FF FF FF 00 EF  (0%)
```

**Notes:**
- ⚠️ **Protocol length is 04, not 07!**
- Speed affects animation playback rate
- Does NOT restart the current animation
- **No effect on solid colors (RGB mode)** - only works with animations!

---

### 4. Animation Modes (RGB Effect Modes)

**FULLY DOCUMENTED - 213 modes organized into 8 categories!**

```
Command Format: 7E 07 03 XX FF FF FF 00 EF

Where:
  07 = Protocol length
  03 = MODE/ANIMATION command type
  XX = Animation mode (00-D4 hex / 0-212 decimal)
  FF FF FF = Unused parameter bytes (MUST be FF!)
  00 = Fixed byte 7
  EF = Footer
```

**Mode Organization:**
All 213 modes are organized into 8 categories as shown in the Lotus Lamp X app:

| Category | Modes | Description |
|----------|-------|-------------|
| **basic** | 47 modes (0-2, 77-88, 181-212) | Auto cycle, magic colors, jumps, gradients, strobes |
| **trans** | 20 modes (3-22) | Light/dark transitions |
| **tail** | 16 modes (23-38) | Comet/tailing effects |
| **water** | 18 modes (39-56) | Running water patterns |
| **curtain** | 20 modes (57-76) | Opening/closing effects |
| **run** | 34 modes (89-141 odd, 167-179 odd) | Forward running (7-color in various backgrounds) |
| **runback** | 34 modes (90-142 even, 168-180 even) | Backward running (7-color in various backgrounds) |
| **flow** | 24 modes (143-166) | White-to-color-to-white breathing effects |

**See:** `LAMP_MODES_BY_CATEGORY.md` for complete mode listings and descriptions

⚠️ **Important:** These mode numbers are specific to MELK-OA10 5F hardware. Other lamp models may use different mappings.

**Examples:**
```
Animation 1:   7E 07 03 01 FF FF FF 00 EF
Animation 10:  7E 07 03 0A FF FF FF 00 EF
Animation 100: 7E 07 03 64 FF FF FF 00 EF
Special fade:  7E 07 03 FF FF FF FF 00 EF
```

**Notes:**
- Over 200 different animation modes available
- Some modes are color-specific (red, green, blue variants)
- Each mode has its own pattern and timing
- Mode is retained even when brightness/speed changes

**Examples:**
```
Mode 0   (0x00): 7E 07 03 00 FF FF FF 00 EF  # Auto play
Mode 138 (0x8A): 7E 07 03 8A FF FF FF 00 EF  # 7-color cyan run back
Mode 143 (0x8F): 7E 07 03 8F FF FF FF 00 EF  # W-R-W flow
```

**Python Usage:**
```python
await lamp.set_animation(0)    # Auto play
await lamp.set_animation(138)  # 7-color cyan run back
await lamp.set_animation(143)  # W-R-W flow

# Or by category
from lamp_mode_categories import get_mode_by_category_index
mode = get_mode_by_category_index('flow', 1)  # First flow mode (143)
await lamp.set_animation(mode)
```

**Tools:**
- `lamp_browser.py` - Interactive mode browser to test all 213 modes
- `lamp_mode_categories.py` - Python module for category-based mode access
- `LAMP_MODES_BY_CATEGORY.md` - Complete reference documentation

---

## RGB Color Control (Detailed)

### Setting Arbitrary RGB Colors

The RGB command format allows setting **any RGB color** from 0-255 per channel:

```python
def set_rgb(r, g, b):
    """Set lamp to specific RGB color"""
    command = bytes([
        0x7E,           # Header
        0x07,           # Protocol length
        0x05,           # COLOR command
        0x03,           # Mode parameter
        r,              # Red (0-255)
        g,              # Green (0-255)
        b,              # Blue (0-255)
        0x10,           # Mode flag
        0xEF            # Footer
    ])
    # Send via BLE to characteristic 0xFFF3
```

### Color Space

- **Range:** 0-255 per channel (standard 24-bit RGB)
- **Total Colors:** 16,777,216 possible colors (256³)
- **Gamma:** Appears to be linear (no gamma correction)

### Performance

- **Update Rate:** ~10 Hz maximum (100ms between commands)
- **Response Time:** < 100ms typical
- **Smooth Transitions:** Not built-in, must be implemented client-side

---

## Python Examples

### Basic Connection and Color Setting

```python
import asyncio
from bleak import BleakClient

DEVICE_NAME = "MELK-OA10   5F"
WRITE_CHAR = "0000FFF3-0000-1000-8000-00805F9B34FB"

async def set_color(r, g, b):
    async with BleakClient(DEVICE_NAME) as client:
        cmd = bytes([0x7E, 0x07, 0x05, 0x03, r, g, b, 0x10, 0xEF])
        await client.write_gatt_char(WRITE_CHAR, cmd, response=False)

# Usage
asyncio.run(set_color(255, 0, 0))  # Red
```

### Full Controller Class

Use the `lotus_lamp` package for a complete implementation:

```python
from lotus_lamp import LotusLamp

lamp = LotusLamp()
await lamp.connect()
await lamp.set_rgb(255, 0, 0)
await lamp.set_animation(143)
await lamp.set_brightness(75)
await lamp.disconnect()
```

Features:
- RGB color control
- Brightness and speed adjustment
- 213 animation modes with official names
- Mode search and lookup
- Interactive browser tool

---

## Command Discovery Process

This protocol was fully reverse-engineered through:

1. **Bluetooth Sniffing:** Attempted but packets were truncated
2. **Systematic Testing:** 200+ command variations tested
3. **APK Decompilation:** Final breakthrough
   - Decompiled Lotus Lamp X app (com.szelk.ledlamppro)
   - Found E1Achieve.java with complete protocol implementation
   - Extracted exact command formats
   - Confirmed with live testing

---

## Important Notes

### Unstable Commands (DO NOT USE)
```
7E 00 05 XX ... - Causes lamp freeze/hang
7E 00 06 XX ... - Causes lamp freeze/hang
```

These command types cause the lamp to become unresponsive and require power cycling.

### Timing Recommendations
- **Minimum delay between commands:** 50ms
- **Recommended delay:** 100-200ms
- **Maximum safe rate:** ~10 commands/second

### Connection Behavior
- Lamp disconnects from app when another device connects
- No graceful disconnect notification
- Reconnection is fast (< 1 second)

---

## Hardware Details

### LED Strip Specifications
- Type: RGB (no separate white channel in this model)
- Control: Single-zone (all LEDs same color)
- Length: Varies by model
- Power: USB-powered (5V)

### Remote Control
- IR remote control also supported
- BLE and IR operate independently
- Commands do NOT conflict

---

---

### 5. Timer/Scheduling

**IMPLEMENTED - Protocol decoded from APK decompilation + behavioral testing.**

The lamp handles scheduling internally (lamp-side). The app sends the current time to
the lamp first, then sends timer configuration. No phone needed after setup.

#### Protocol Format

Timer commands use the **standard E1Achieve format** (same 9-byte structure as all
other commands). They do NOT use a special timer format.

```
┌─────────┬──────────┬──────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐
│  Header │ Protocol │ Command  │ Param 1 │ Param 2 │ Param 3 │ Param 4 │ Fixed   │ Footer  │
│   0x7E  │   Len    │   Type   │         │         │         │         │  0x00   │  0xEF   │
└─────────┴──────────┴──────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘
  Byte 0     Byte 1     Byte 2    Byte 3    Byte 4    Byte 5    Byte 6    Byte 7    Byte 8
```

**Important:** E1Achieve fills 5 parameter slots (positions 3-7).
The 5th param overwrites the normally-fixed 0x00 at position 7.

#### Step 1: Sync Current Time

```
Command Format: 7E 06 83 HH MM SS WW 00 EF

Where:
  06 = Protocol length (DATA_TIME-specific value)
  83 = DATA_TIME command type
  HH = Current hour (00-17 hex / 0-23 decimal)
  MM = Current minute (00-3B hex / 0-59 decimal)
  SS = Current second (00-3B hex / 0-59 decimal)
  WW = Day of week (1-7, where 1=Monday...7=Sunday)
  00 = Fixed byte 7
  EF = Footer
```

**Note:** Weekday values 1-7 correspond directly to bitmask bits 0-6:
- Python's `weekday() + 1` gives Mon=1, Tue=2, ..., Sun=7
- This directly maps to timer bitmask bits: Mon=0x01, Tue=0x02, ..., Sun=0x40

#### Step 2: Set Timer

```
Command Format: 7E 07 82 HH MM 00 TT BB EF

Where:
  07 = Protocol length
  82 = TIMER_SWITCH command type
  HH = Timer hour (00-17 hex / 0-23 decimal)
  MM = Timer minute (00-3B hex / 0-59 decimal)
  00 = Padding byte (always 0x00)
  TT = Timer type (00 = ON, 01 = OFF)
  BB = Week bitmask (bit 7=enabled, bits 0-6=day flags)
  EF = Footer
```

**Week Bitmask:**

The bitmask bits correspond to sync_time weekday values:

| Bit | Value | Day | sync_time WW value |
|-----|-------|-----|-------------------|
| 0 | 0x01 | Monday | 0x01 |
| 1 | 0x02 | Tuesday | 0x02 |
| 2 | 0x04 | Wednesday | 0x03 |
| 3 | 0x08 | Thursday | 0x04 |
| 4 | 0x10 | Friday | 0x05 |
| 5 | 0x20 | Saturday | 0x06 |
| 6 | 0x40 | Sunday | 0x07 |
| 7 | 0x80 | Timer enabled | - |

**Examples:**
```
Sync time (Mon 07:30:00):  7E 06 83 07 1E 00 01 00 EF  (WW=0x01 for Monday)
Sync time (Sat 07:30:00):  7E 06 83 07 1E 00 06 00 EF  (WW=0x06 for Saturday)
Sync time (Sun 07:30:00):  7E 06 83 07 1E 00 07 00 EF  (WW=0x07 for Sunday)
ON timer at 07:30:         7E 07 82 07 1E 00 00 80 EF  (0x80 = enabled, no days)
OFF timer at 23:00:        7E 07 82 17 00 00 01 80 EF
ON timer Mon-Fri 07:30:    7E 07 82 07 1E 00 00 9F EF  (0x80|0x1F = Mon-Fri bits 0-4)
ON timer Sat only:         7E 07 82 07 1E 00 00 A0 EF  (0x80|0x20 = Saturday bit 5)
ON timer Sun only:         7E 07 82 07 1E 00 00 C0 EF  (0x80|0x40 = Sunday bit 6)
Disable ON timer:          7E 07 82 00 00 00 00 00 EF  (bitmask=0x00 = disabled)
Disable OFF timer:         7E 07 82 00 00 00 01 00 EF
```

**Python Usage:**
```python
# Sync time, then set schedule
await lamp.sync_time()
await lamp.set_timer_on(7, 30)
await lamp.set_timer_off(23, 0)

# Disable timers
await lamp.disable_timer_on()
await lamp.disable_timer_off()
```

**Notes:**
- Always call `sync_time()` before setting timers (lamp has no real-time clock)
- The weekday in `sync_time()` must match the bitmask bit values (WW=1 → bit 0, WW=2 → bit 1, etc.)
- Timer survives brief power loss but NOT extended disconnection (30+ seconds)
- ON and OFF timers are independent
- One-shot timers (bitmask=0x80 with no day bits) fire once then must be re-set
- Repeating timers (bitmask with day bits set) fire on specified days of week
- Tested and verified: Mon-Sun all work correctly with proper weekday/bitmask mapping

---

## Future Exploration

### Unknown Parameters
- Byte 3 in RGB command (currently `03`) - purpose unknown
- Byte 7 in RGB command (currently `10`) - purpose unknown
- Protocol length variations - not all documented

### Potential Features
- Individual LED control (if supported)
- Custom animation creation
- Music synchronization parameters

---

## Credits

Protocol reverse-engineered by analyzing:
- Lotus Lamp X Android app (com.szelk.ledlamppro)
- Live BLE packet capture and testing
- Systematic command exploration

---

## License

This documentation is provided for educational and interoperability purposes.

**No warranty provided - use at your own risk.**

---

**Last Updated:** February 4, 2026
**Status:** Complete RGB protocol documented and tested
