#!/usr/bin/env python3
"""
Configuration management for Lotus Lamp devices
Handles loading and saving device configurations
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict


@dataclass
class DeviceConfig:
    """Configuration for a Lotus Lamp device"""
    name: str
    address: Optional[str] = None
    service_uuid: str = "0000FFF0-0000-1000-8000-00805F9B34FB"
    write_char_uuid: str = "0000FFF3-0000-1000-8000-00805F9B34FB"
    notify_char_uuid: str = "0000FFF4-0000-1000-8000-00805F9B34FB"

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'DeviceConfig':
        """Create from dictionary"""
        return cls(**data)


class ConfigManager:
    """Manages device configurations"""

    DEFAULT_CONFIG_LOCATIONS = [
        # Search local directory first (project-specific configs)
        Path.cwd() / "lotus_lamp_config.json",
        Path.cwd() / ".lotus_lamp.json",
        # Then user's home directory (global config)
        Path.home() / ".lotus_lamp" / "config.json",
    ]

    def __init__(self, config_path: Optional[Path] = None, verbose: bool = False):
        """
        Initialize config manager

        Args:
            config_path: Optional path to config file. If None, searches default locations.
            verbose: If True, print config loading messages
        """
        self.config_path = None
        self.devices: Dict[str, DeviceConfig] = {}
        self.verbose = verbose

        if config_path:
            # Explicit path provided
            config_path = Path(config_path)
            if not config_path.exists():
                raise FileNotFoundError(
                    f"Configuration file not found: {config_path}\n"
                    f"Please check the path or run: python -m lotus_lamp.setup"
                )
            self.load(config_path)
        else:
            # Try to load from default locations
            self._load_from_defaults()

    def _load_from_defaults(self):
        """Try to load config from default locations"""
        for path in self.DEFAULT_CONFIG_LOCATIONS:
            if path.exists():
                if self.verbose:
                    print(f"Loading config from: {path}")
                self.load(path)
                return

        # No config found in any location
        if self.verbose:
            print("No configuration file found in default locations:")
            for path in self.DEFAULT_CONFIG_LOCATIONS:
                print(f"  - {path}")

    def load(self, config_path: Path) -> bool:
        """
        Load configuration from file

        Args:
            config_path: Path to configuration file

        Returns:
            True if loaded successfully

        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
            KeyError: If required fields are missing
        """
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)

            # Handle both single device and multi-device configs
            if 'devices' in data:
                # Multi-device config
                for device_data in data['devices']:
                    device = DeviceConfig.from_dict(device_data)
                    self.devices[device.name] = device
            else:
                # Single device config (legacy support)
                device = DeviceConfig.from_dict(data)
                self.devices[device.name] = device

            self.config_path = config_path

            if self.verbose:
                print(f"[OK] Loaded {len(self.devices)} device(s) from: {config_path}")

            return True

        except FileNotFoundError:
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}"
            )
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in configuration file: {config_path}",
                e.doc,
                e.pos
            )
        except KeyError as e:
            raise KeyError(
                f"Missing required field in configuration: {e}"
            )

    def save(self, config_path: Optional[Path] = None) -> bool:
        """
        Save configuration to file

        Args:
            config_path: Optional path to save to. Uses loaded path if None.

        Returns:
            True if saved successfully
        """
        path = config_path or self.config_path
        if not path:
            raise ValueError("No config path specified")

        # Create directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            data = {
                'devices': [device.to_dict() for device in self.devices.values()]
            }

            with open(path, 'w') as f:
                json.dump(data, f, indent=2)

            self.config_path = path
            return True

        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def add_device(self, device: DeviceConfig):
        """Add or update a device configuration"""
        self.devices[device.name] = device

    def remove_device(self, name: str) -> bool:
        """Remove a device configuration"""
        if name in self.devices:
            del self.devices[name]
            return True
        return False

    def get_device(self, name: str) -> Optional[DeviceConfig]:
        """Get a device configuration by name"""
        return self.devices.get(name)

    def list_devices(self) -> List[str]:
        """List all configured device names"""
        return list(self.devices.keys())

    def get_default_device(self) -> Optional[DeviceConfig]:
        """
        Get the default device (first device in config)

        Returns:
            First device config or None if no devices configured
        """
        if self.devices:
            return next(iter(self.devices.values()))
        return None


def create_default_config(config_path: Optional[Path] = None) -> Path:
    """
    Create a default configuration file

    Args:
        config_path: Optional path to create config at. Uses default if None.

    Returns:
        Path to created config file
    """
    if not config_path:
        config_path = ConfigManager.DEFAULT_CONFIG_LOCATIONS[0]

    # Create example config with the original hardcoded device
    default_device = DeviceConfig(
        name="MELK-OA10   5F",
        address=None,  # Will be discovered
        service_uuid="0000FFF0-0000-1000-8000-00805F9B34FB",
        write_char_uuid="0000FFF3-0000-1000-8000-00805F9B34FB",
        notify_char_uuid="0000FFF4-0000-1000-8000-00805F9B34FB"
    )

    manager = ConfigManager()
    manager.add_device(default_device)
    manager.save(config_path)

    return config_path


if __name__ == '__main__':
    # Example usage
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'create':
        path = create_default_config()
        print(f"Created default config at: {path}")
    else:
        print("Usage: python config.py create")
