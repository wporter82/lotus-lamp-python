#!/usr/bin/env python3
"""
Interactive Lamp Mode Browser

Browse and test all 213 RGB modes organized by category.
Requires the lotus_lamp package to be installed and configured.

Usage:
    python browser.py

Note: Run 'python -m lotus_lamp.setup' first if you haven't configured your lamp yet.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path if running from examples/
sys.path.insert(0, str(Path(__file__).parent.parent))

from lotus_lamp import LotusLamp
from lotus_lamp.modes import CATEGORIES, get_mode_category, get_mode_name


class LampBrowser:
    def __init__(self):
        self.lamp = None
        self.current_category = None
        self.current_index = 0

    async def connect(self):
        """Connect to the lamp"""
        print("Connecting to lamp...")

        try:
            self.lamp = LotusLamp()
        except ValueError as e:
            print(f"\n{e}")
            return False

        if not await self.lamp.connect():
            print("Failed to connect to lamp!")
            return False

        print("Connected!\n")
        return True

    async def disconnect(self):
        """Disconnect from lamp"""
        if self.lamp:
            await self.lamp.disconnect()

    async def set_mode(self, mode_num: int):
        """Set lamp to specific mode"""
        await self.lamp.set_animation(mode_num)
        await asyncio.sleep(0.2)

    def show_categories(self):
        """Display all categories"""
        print("\n" + "="*70)
        print("LAMP MODE CATEGORIES")
        print("="*70)
        for i, (category, modes) in enumerate(CATEGORIES.items(), 1):
            # CATEGORIES dict maps category name -> list of mode numbers
            print(f"{i}. {category:12} - {len(modes):3} modes")
        print("="*70)

    def show_category_modes(self, category: str):
        """Display all modes in a category"""
        from lotus_lamp.modes import get_mode_name

        # Get mode numbers from CATEGORIES dict
        if category not in CATEGORIES:
            print(f"Unknown category: {category}")
            return

        mode_numbers = CATEGORIES[category]

        print(f"\n{'='*70}")
        print(f"{category.upper()} CATEGORY ({len(mode_numbers)} modes)")
        print("="*70)

        for i, mode_num in enumerate(mode_numbers, 1):
            mode_name = get_mode_name(mode_num)
            print(f"{i:2}. Mode {mode_num:3} (0x{mode_num:02X}): {mode_name}")

        print("="*70)

    async def browse_category(self, category: str):
        """Interactive mode browser for a category"""
        from lotus_lamp.modes import get_mode_name

        # Get mode numbers from CATEGORIES dict
        if category not in CATEGORIES:
            print(f"Unknown category: {category}")
            return

        mode_numbers = CATEGORIES[category]

        self.current_category = category
        self.current_index = 0

        print(f"\n{'='*70}")
        print(f"BROWSING: {category.upper()} CATEGORY")
        print("="*70)
        print("Commands: n=next, p=prev, j=jump, q=quit, l=list")
        print("="*70)

        while True:
            mode_num = mode_numbers[self.current_index]
            mode_name = get_mode_name(mode_num)

            print(f"\n[{self.current_index + 1}/{len(mode_numbers)}] Mode {mode_num} (0x{mode_num:02X})")
            print(f"Name: {mode_name}")

            # Set the mode
            await self.set_mode(mode_num)

            cmd = input("\nCommand (n/p/j/q/l): ").strip().lower()

            if cmd == 'q':
                break
            elif cmd == 'n':
                self.current_index = (self.current_index + 1) % len(mode_numbers)
            elif cmd == 'p':
                self.current_index = (self.current_index - 1) % len(mode_numbers)
            elif cmd == 'j':
                try:
                    jump = int(input(f"Jump to index (1-{len(mode_numbers)}): "))
                    if 1 <= jump <= len(mode_numbers):
                        self.current_index = jump - 1
                    else:
                        print(f"Invalid index. Must be 1-{len(mode_numbers)}")
                except ValueError:
                    print("Invalid number")
            elif cmd == 'l':
                self.show_category_modes(category)

    async def quick_test(self):
        """Quick test of first 2 modes from each category"""
        print("\n" + "="*70)
        print("QUICK TEST: Sample Modes from Each Category")
        print("="*70)

        from lotus_lamp.modes import get_mode_name

        for category, mode_numbers in CATEGORIES.items():
            print(f"\n{category.upper()} category:")

            # Test first 2 modes from each category
            for mode_num in mode_numbers[:2]:
                mode_name = get_mode_name(mode_num)
                print(f"  Mode {mode_num}: {mode_name}")
                await self.set_mode(mode_num)
                await asyncio.sleep(2.0)

        print("\nQuick test complete!")

    async def interactive(self):
        """Main interactive menu"""
        if not await self.connect():
            return

        try:
            while True:
                print("\n" + "="*70)
                print("LAMP MODE BROWSER")
                print("="*70)
                print("1. Show all categories")
                print("2. Browse category modes")
                print("3. Quick test sample modes")
                print("4. Jump to specific mode")
                print("5. Quit")
                print("="*70)

                choice = input("\nChoice: ").strip()

                if choice == '1':
                    self.show_categories()

                elif choice == '2':
                    self.show_categories()
                    cat_choice = input("\nEnter category name: ").strip().lower()
                    if cat_choice in CATEGORIES:
                        await self.browse_category(cat_choice)
                    else:
                        print("Invalid category")

                elif choice == '3':
                    await self.quick_test()

                elif choice == '4':
                    try:
                        mode_num = int(input("Enter mode number (0-212): "))
                        if 0 <= mode_num <= 212:
                            name = get_mode_name(mode_num)
                            category = get_mode_category(mode_num)
                            print(f"\nMode {mode_num} ({category}): {name}")
                            await self.set_mode(mode_num)
                            input("Press Enter to continue...")
                        else:
                            print("Mode must be 0-212")
                    except ValueError:
                        print("Invalid number")

                elif choice == '5':
                    break

        finally:
            await self.disconnect()


async def async_main():
    """Run the browser (async)"""
    browser = LampBrowser()
    await browser.interactive()


def main():
    """Console script entry point"""
    print("="*70)
    print("LOTUS LAMP MODE BROWSER")
    print("="*70)
    print("\nBrowse all 213 RGB modes organized by category")
    print("Test modes and document what they do")
    print("\nNote: Make sure you've configured your lamp first:")
    print("  python -m lotus_lamp.setup")
    print("\nPress Enter to start...")
    input()

    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\n\nBrowser stopped.")


if __name__ == '__main__':
    main()
