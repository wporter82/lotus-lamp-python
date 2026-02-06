#!/usr/bin/env python3
"""
Lotus Lamp CLI entry point
Handles running the setup wizard or controller based on configuration state
"""

import sys
from pathlib import Path
from .config import ConfigManager


def main():
    """Main entry point for lotus_lamp module"""

    # Check if configuration exists
    manager = ConfigManager()
    has_config = manager.get_default_device() is not None

    if not has_config:
        # No configuration found - guide user to setup
        print("\n" + "="*80)
        print("WELCOME TO LOTUS LAMP")
        print("="*80)
        print("\nIt looks like this is your first time using Lotus Lamp!")
        print("\nBefore you can control your lamp, you need to run the setup wizard.")
        print("\nThe setup wizard will:")
        print("  1. Scan for your Lotus Lamp device")
        print("  2. Automatically discover connection details")
        print("  3. Save the configuration for future use")
        print("\nWould you like to run the setup wizard now? (Y/n): ", end='')

        try:
            response = input().strip().lower()

            if response in ('', 'y', 'yes'):
                # Run setup
                print("\nStarting setup wizard...")
                from .setup import run_setup
                import asyncio
                asyncio.run(run_setup())
            else:
                print("\nYou can run the setup wizard later with:")
                print("    python -m lotus_lamp.setup")
                print("\n" + "="*80)

        except KeyboardInterrupt:
            print("\n\nSetup cancelled.")
            print("\nYou can run the setup wizard later with:")
            print("    python -m lotus_lamp.setup")
            sys.exit(1)
    else:
        # Configuration exists - run interactive controller
        print("\n" + "="*80)
        print("LOTUS LAMP INTERACTIVE CONTROLLER")
        print("="*80)
        print("\nCommands:")
        print("  controller  - Interactive lamp controller")
        print("  demo        - Run demo sequence")
        print("  setup       - Run setup wizard (add/reconfigure devices)")
        print("  scan        - Scan for devices")
        print("  help        - Show this help")
        print("="*80)

        # Parse command
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()

            if command == 'controller':
                from .controller import interactive
                import asyncio
                try:
                    asyncio.run(interactive())
                except ValueError as e:
                    if "No Lotus Lamp devices configured" in str(e):
                        print(f"\n{e}")
                    else:
                        raise

            elif command == 'demo':
                from .controller import demo
                import asyncio
                try:
                    asyncio.run(demo())
                except ValueError as e:
                    if "No Lotus Lamp devices configured" in str(e):
                        print(f"\n{e}")
                    else:
                        raise

            elif command == 'setup':
                from .setup import run_setup
                import asyncio
                asyncio.run(run_setup())

            elif command == 'scan':
                from .scanner import interactive_scan
                import asyncio
                asyncio.run(interactive_scan())

            elif command in ('help', '-h', '--help'):
                print("\nFor more information, see:")
                print("  - QUICK_START.md")
                print("  - README.md")
                print("  - https://github.com/your-repo/lotus-lamp-python")

            else:
                print(f"\nUnknown command: {command}")
                print("\nRun 'python -m lotus_lamp' to see available commands.")
        else:
            # No command given - show usage
            print("\nUsage:")
            print("  python -m lotus_lamp <command>")
            print("\nRun 'python -m lotus_lamp help' for more information.")


if __name__ == '__main__':
    main()
