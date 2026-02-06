# Lamp RGB Modes - Organized by App Categories

**Hardware:** MELK-OA10 5F (Tyute RGB LED Lamp)
**Source:** Extracted from Lotus Lamp X app (arrays.xml)
**Date:** February 2026

This document shows ALL RGB modes organized by the categories used in the Lotus Lamp X app.

---

## Mode Categories

The app organizes modes into 8 categories, each with specific effects:

| Category | Mode Count | Mode Range | Description |
|----------|------------|------------|-------------|
| **basic** | 47 | 0-2, 77-88, 181-212 | Auto cycle, magic colors, jumps, gradients, strobes |
| **trans** | 20 | 3-22 | Transition effects |
| **tail** | 16 | 23-38 | Tailing effects |
| **water** | 18 | 39-56 | Running water effects |
| **curtain** | 20 | 57-76 | Opening/closing curtain effects |
| **run** | 34 | 89-141 (odd), 167-179 (odd) | Forward running effects |
| **runback** | 34 | 90-142 (even), 168-180 (even) | Backward running effects |
| **flow** | 24 | 143-166 | White-to-color-to-white flow effects |

---

## Complete Mode Listings

### BASIC (47 modes)
```
Modes: 0, 1, 2, 77-88, 181-192, 193-212

Examples (from app strings):
  0 - Auto Play
  1 - Magic Forward
  2 - Magic Back
  77-88 - Various color jumps and gradients
  181-192 - Stroboscopic effects
  193-212 - Advanced color combinations
```

### TRANS (Transition) (20 modes)
```
Modes: 3-22

Transition effects between colors
Light-to-dark and dark-to-light transitions
```

### TAIL (Tailing) (16 modes)
```
Modes: 23-38

Tail/comet effects in various colors
Positive and reverse directions
```

### WATER (Running Water) (18 modes)
```
Modes: 39-56

Flowing water effects
Colorful water patterns
Forward and reverse water flow
```

### CURTAIN (Opening & Closing) (20 modes)
```
Modes: 57-76

Curtain opening/closing effects
Various color combinations
Theater-style curtain animations
```

### RUN (Forward Running) (34 modes)
```
Modes: 89, 91, 93, 95, 97, 99, 101, 103, 105, 107, 109, 111, 113,
       115, 117, 119, 121, 123, 125, 127, 129, 131, 133, 135, 137,
       139, 141, 167, 169, 171, 173, 175, 177, 179

**Verified modes (129-141):**
  129 - 7-color in red running
  131 - 7-color in green running
  133 - 7-color in blue running
  135 - 7-color in yellow running
  137 - 7-color in cyan running
  139 - 7-color in purple running
  141 - 7-color in white running
```

### RUNBACK (Backward Running) (34 modes)
```
Modes: 90, 92, 94, 96, 98, 100, 102, 104, 106, 108, 110, 112, 114,
       116, 118, 120, 122, 124, 126, 128, 130, 132, 134, 136, 138,
       140, 142, 168, 170, 172, 174, 176, 178, 180

**Verified modes (128-142):**
  128 - White-dot in red run back
  130 - 7-color in red run back
  132 - 7-color in green run back
  134 - 7-color in blue run back
  136 - 7-color in yellow run back
  138 - 7-color in cyan run back
  140 - 7-color in purple run back
  142 - 7-color in white run back
```

### FLOW (24 modes)
```
Modes: 143-166

**Verified modes (143-150):**
  143 - W-R-W flow (white-red-white)
  144 - W-R-W flow back
  145 - W-G-W flow (white-green-white)
  146 - W-G-W flow back
  147 - W-B-W flow (white-blue-white)
  148 - W-B-W flow back
  149 - W-Y-W flow (white-yellow-white)
  150 - W-Y-W flow back

Modes 151-166 likely continue with more flow patterns
```

---

## Pattern Observations

### Run vs RunBack Pattern
- **Run** uses **odd** mode numbers (129, 131, 133, ...)
- **RunBack** uses **even** mode numbers (128, 130, 132, ...)
- Each color has both forward and backward variants
- Colors: red, green, blue, yellow, cyan, purple, white

### Flow Pattern
- White-to-color-to-white transitions
- Creates a "breathing" or pulsing effect
- Alternates forward/back for each color
- Modes 143-150: R, G, B, Y colors verified
- Modes 151-166: Likely C, M, other colors

---

## Command Format

All modes use the same command format:

```
7E 07 03 XX FF FF FF 00 EF
```

Where:
- `XX` = Mode number from tables above (in hexadecimal)
- This is the **single-parameter animation format**
- NOT the two-parameter `7E 06 03 XX 03 FF FF 00 EF` format

**Examples:**
```
Mode 138 (0x8A): 7E 07 03 8A FF FF FF 00 EF  # 7-color cyan run back
Mode 143 (0x8F): 7E 07 03 8F FF FF FF 00 EF  # W-R-W flow
Mode 0   (0x00): 7E 07 03 00 FF FF FF 00 EF  # Auto play
```

---

## Python Usage

```python
from lotus_lamp import LotusLamp, get_mode_by_category_index, CATEGORIES

# Create lamp instance
lamp = LotusLamp()
await lamp.connect()

# Get all modes in a category
flow_modes = CATEGORIES['flow']  # [143, 144, 145, ...]

# Set a mode by category and index (as shown in app)
mode = get_mode_by_category_index('flow', 1)  # First flow mode
await lamp.set_animation(mode)

# Or use mode number directly
await lamp.set_animation(138)  # 7-color cyan run back

await lamp.disconnect()
```

---

## Discovery Status

- ✅ **All 213 mode names extracted** from app strings.xml
- ✅ **Modes 128-150:** Manually verified and tested
- ✅ **All mode categories mapped** from app arrays.xml
- 📝 **Remaining modes (0-127, 151-212):** Names extracted, not yet tested

Use the interactive browser to explore all modes:
```bash
python examples/browser.py
```

---

## Notes

1. **Mode numbers and names extracted from app source**
   - Mode numbers from `arrays.xml`
   - Mode names from `strings.xml`
   - All 213 modes with official names included in package
2. **Categories match app UI** - basic, curtain, trans, water, flow, tail, run, runback
3. **Each category item is numbered 1, 2, 3...** in the app UI, but maps to specific mode numbers in the firmware
4. **Command format** uses single-parameter animation format: `7E 07 03 XX FF FF FF 00 EF`
5. **Hardware-specific** - These mappings are for MELK-OA10 5F. Other lamp models may vary.

---

**Last Updated:** February 4, 2026
**Extraction Source:** Lotus Lamp X app (com.szelk.ledlamppro)
**Data Location:** `lotus_lamp/data/` in package
