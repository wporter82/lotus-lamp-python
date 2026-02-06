"""
Mode lookup and category management for Lotus Lamp

Provides access to all 213 RGB animation modes with official names
extracted from the Lotus Lamp X app.
"""

import json
import os
from typing import List, Tuple, Optional

# Get path to data directory
_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# Load mode categories
with open(os.path.join(_DATA_DIR, 'mode_categories.json'), 'r', encoding='utf-8') as f:
    CATEGORIES = json.load(f)

# Load mode names
with open(os.path.join(_DATA_DIR, 'mode_names.json'), 'r', encoding='utf-8') as f:
    _MODE_NAMES = {int(k): v for k, v in json.load(f).items()}


def get_mode_name(mode_num: int) -> str:
    """
    Get official app name for a mode

    Args:
        mode_num: Mode number (0-212)

    Returns:
        Official mode name from Lotus Lamp X app

    Example:
        >>> get_mode_name(143)
        'W-R-W Flow'
    """
    return _MODE_NAMES.get(mode_num, f"Unknown Mode {mode_num}")


def get_mode_category(mode_num: int) -> str:
    """
    Get category for a mode

    Args:
        mode_num: Mode number (0-212)

    Returns:
        Category name (basic, trans, tail, water, curtain, run, runback, flow)

    Example:
        >>> get_mode_category(143)
        'flow'
    """
    for category, modes in CATEGORIES.items():
        if mode_num in modes:
            return category
    return "unknown"


def get_mode_by_category_index(category: str, index: int) -> int:
    """
    Get mode number by category and index (1-based, as shown in app)

    Args:
        category: Category name (basic, curtain, trans, water, flow, tail, run, runback)
        index: 1-based index as shown in app UI (1 = first item, 2 = second item, etc.)

    Returns:
        Actual mode number to send to lamp

    Raises:
        ValueError: If category is invalid or index is out of range

    Example:
        >>> get_mode_by_category_index('flow', 1)
        143  # First flow mode: "W-R-W Flow"
    """
    if category not in CATEGORIES:
        raise ValueError(
            f"Unknown category: {category}. "
            f"Valid categories: {', '.join(CATEGORIES.keys())}"
        )

    modes = CATEGORIES[category]
    if index < 1 or index > len(modes):
        raise ValueError(
            f"Index {index} out of range for category {category} (1-{len(modes)})"
        )

    return modes[index - 1]  # Convert 1-based to 0-based


def search_modes(query: str) -> List[Tuple[int, str, str]]:
    """
    Search for modes by name

    Args:
        query: Search term (case-insensitive)

    Returns:
        List of (mode_number, name, category) tuples

    Example:
        >>> search_modes("cyan")
        [(137, '7-Color in Cyan Running', 'run'),
         (138, '7-Color in Cyan Run Back', 'runback'), ...]
    """
    query = query.lower()
    results = []

    for mode_num, name in _MODE_NAMES.items():
        if query in name.lower():
            category = get_mode_category(mode_num)
            results.append((mode_num, name, category))

    return sorted(results, key=lambda x: x[0])


def list_all_categories() -> None:
    """Print all categories and their mode counts"""
    print("\nLamp Mode Categories:")
    print("="*70)
    for category, modes in CATEGORIES.items():
        mode_range = f"{min(modes)}-{max(modes)}"
        print(f"{category:12} ({len(modes):2} modes): {mode_range}")
    print(f"\nTotal: {sum(len(m) for m in CATEGORIES.values())} modes "
          f"across {len(CATEGORIES)} categories")


def list_category_modes(category: str, show_all: bool = True) -> None:
    """
    Print all modes in a specific category

    Args:
        category: Category name
        show_all: If True, show all modes; if False, show only first 10

    Example:
        >>> list_category_modes('flow')

        FLOW Category (24 modes):
        ======================================================================
          1. Mode 143 (0x8F): W-R-W Flow
          2. Mode 144 (0x90): W-R-W Flow Back
          ...
    """
    if category not in CATEGORIES:
        print(f"Unknown category: {category}")
        print(f"Valid categories: {', '.join(CATEGORIES.keys())}")
        return

    modes = CATEGORIES[category]
    print(f"\n{category.upper()} Category ({len(modes)} modes):")
    print("="*70)

    display_modes = modes if show_all else modes[:10]
    for i, mode_num in enumerate(display_modes, 1):
        name = get_mode_name(mode_num)
        print(f"  {i:2}. Mode {mode_num:3} (0x{mode_num:02X}): {name}")

    if not show_all and len(modes) > 10:
        print(f"  ... and {len(modes) - 10} more")


def get_all_mode_names() -> dict:
    """
    Get dictionary of all mode numbers and names

    Returns:
        Dictionary mapping mode numbers to names
    """
    return _MODE_NAMES.copy()


if __name__ == '__main__':
    # Command-line interface
    import sys

    if len(sys.argv) < 2:
        print("Lamp Mode Lookup Tool")
        print("="*70)
        print("\nUsage:")
        print("  python -m lotus_lamp.modes <mode_number>    - Get name for mode")
        print("  python -m lotus_lamp.modes search <query>   - Search mode names")
        print("  python -m lotus_lamp.modes list <category>  - List category modes")
        print("  python -m lotus_lamp.modes categories       - List all categories")
        sys.exit(0)

    if sys.argv[1] == 'search' and len(sys.argv) > 2:
        query = ' '.join(sys.argv[2:])
        results = search_modes(query)
        print(f"\nSearch results for '{query}': {len(results)} matches")
        print("="*70)
        for mode_num, name, category in results:
            print(f"Mode {mode_num:3} ({category:8}): {name}")

    elif sys.argv[1] == 'list' and len(sys.argv) > 2:
        list_category_modes(sys.argv[2].lower())

    elif sys.argv[1] == 'categories':
        list_all_categories()

    else:
        try:
            mode_num = int(sys.argv[1])
            name = get_mode_name(mode_num)
            category = get_mode_category(mode_num)
            print(f"\nMode {mode_num} (0x{mode_num:02X})")
            print(f"Name:     {name}")
            print(f"Category: {category}")
        except ValueError:
            print(f"Invalid mode number: {sys.argv[1]}")
