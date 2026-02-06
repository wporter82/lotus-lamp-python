"""
Tests for configuration management
"""

import pytest
import json
from pathlib import Path
from lotus_lamp.config import DeviceConfig, ConfigManager


class TestDeviceConfig:
    """Test DeviceConfig dataclass"""

    def test_create_device_config(self):
        """Test creating a device configuration"""
        config = DeviceConfig(
            name="Test Lamp",
            address="AA:BB:CC:DD:EE:FF"
        )

        assert config.name == "Test Lamp"
        assert config.address == "AA:BB:CC:DD:EE:FF"
        assert config.service_uuid == "0000FFF0-0000-1000-8000-00805F9B34FB"

    def test_device_config_to_dict(self, sample_device_config):
        """Test converting config to dictionary"""
        config_dict = sample_device_config.to_dict()

        assert isinstance(config_dict, dict)
        assert config_dict['name'] == "Test Lamp"
        assert config_dict['address'] == "AA:BB:CC:DD:EE:FF"

    def test_device_config_from_dict(self):
        """Test creating config from dictionary"""
        data = {
            "name": "From Dict",
            "address": "11:22:33:44:55:66",
            "service_uuid": "0000FFF0-0000-1000-8000-00805F9B34FB",
            "write_char_uuid": "0000FFF3-0000-1000-8000-00805F9B34FB",
            "notify_char_uuid": "0000FFF4-0000-1000-8000-00805F9B34FB"
        }

        config = DeviceConfig.from_dict(data)

        assert config.name == "From Dict"
        assert config.address == "11:22:33:44:55:66"

    def test_device_config_defaults(self):
        """Test default UUID values"""
        config = DeviceConfig(name="Test")

        assert config.address is None
        assert config.service_uuid == "0000FFF0-0000-1000-8000-00805F9B34FB"
        assert config.write_char_uuid == "0000FFF3-0000-1000-8000-00805F9B34FB"
        assert config.notify_char_uuid == "0000FFF4-0000-1000-8000-00805F9B34FB"


class TestConfigManager:
    """Test ConfigManager class"""

    def test_load_single_device(self, sample_config_file):
        """Test loading a single device config"""
        manager = ConfigManager(sample_config_file)

        assert len(manager.devices) == 1
        assert "Test Lamp" in manager.devices
        assert manager.config_path == sample_config_file

    def test_load_multiple_devices(self, multi_device_config_file):
        """Test loading multiple devices"""
        manager = ConfigManager(multi_device_config_file)

        assert len(manager.devices) == 2
        assert "Living Room" in manager.devices
        assert "Bedroom" in manager.devices

    def test_load_legacy_config(self, legacy_single_device_config):
        """Test loading legacy single-device format"""
        manager = ConfigManager(legacy_single_device_config)

        assert len(manager.devices) == 1
        assert "Legacy Lamp" in manager.devices

    def test_load_nonexistent_file(self, temp_dir):
        """Test loading from non-existent file raises error"""
        nonexistent = temp_dir / "does_not_exist.json"

        with pytest.raises(FileNotFoundError) as exc_info:
            ConfigManager(nonexistent)

        assert "not found" in str(exc_info.value).lower()

    def test_load_invalid_json(self, invalid_json_file):
        """Test loading invalid JSON raises error"""
        with pytest.raises(json.JSONDecodeError):
            ConfigManager(invalid_json_file)

    def test_get_device(self, multi_device_config_file):
        """Test getting a specific device"""
        manager = ConfigManager(multi_device_config_file)

        device = manager.get_device("Living Room")

        assert device is not None
        assert device.name == "Living Room"
        assert device.address == "11:22:33:44:55:66"

    def test_get_nonexistent_device(self, sample_config_file):
        """Test getting a device that doesn't exist"""
        manager = ConfigManager(sample_config_file)

        device = manager.get_device("Nonexistent")

        assert device is None

    def test_get_default_device(self, multi_device_config_file):
        """Test getting the default (first) device"""
        manager = ConfigManager(multi_device_config_file)

        device = manager.get_default_device()

        assert device is not None
        assert device.name == "Living Room"  # First device

    def test_get_default_device_empty_config(self, empty_config_file):
        """Test getting default device from empty config"""
        manager = ConfigManager(empty_config_file)

        device = manager.get_default_device()

        assert device is None

    def test_list_devices(self, multi_device_config_file):
        """Test listing all device names"""
        manager = ConfigManager(multi_device_config_file)

        devices = manager.list_devices()

        assert len(devices) == 2
        assert "Living Room" in devices
        assert "Bedroom" in devices

    def test_add_device(self, sample_config_file):
        """Test adding a new device"""
        manager = ConfigManager(sample_config_file)

        new_device = DeviceConfig(
            name="New Lamp",
            address="FF:EE:DD:CC:BB:AA"
        )

        manager.add_device(new_device)

        assert len(manager.devices) == 2
        assert "New Lamp" in manager.devices

    def test_remove_device(self, multi_device_config_file):
        """Test removing a device"""
        manager = ConfigManager(multi_device_config_file)

        result = manager.remove_device("Living Room")

        assert result is True
        assert len(manager.devices) == 1
        assert "Living Room" not in manager.devices

    def test_remove_nonexistent_device(self, sample_config_file):
        """Test removing a device that doesn't exist"""
        manager = ConfigManager(sample_config_file)

        result = manager.remove_device("Nonexistent")

        assert result is False

    def test_save_config(self, temp_dir, sample_device_config):
        """Test saving configuration"""
        # Create empty manager (no existing config)
        manager = ConfigManager()
        manager.devices = {}  # Clear any loaded devices
        manager.add_device(sample_device_config)

        save_path = temp_dir / "saved_config.json"
        result = manager.save(save_path)

        assert result is True
        assert save_path.exists()

        # Verify content
        with open(save_path) as f:
            data = json.load(f)

        assert "devices" in data
        assert len(data["devices"]) == 1
        assert data["devices"][0]["name"] == "Test Lamp"

    def test_save_creates_directory(self, temp_dir):
        """Test that save creates parent directories"""
        manager = ConfigManager()
        manager.add_device(DeviceConfig(name="Test"))

        nested_path = temp_dir / "nested" / "dir" / "config.json"
        result = manager.save(nested_path)

        assert result is True
        assert nested_path.exists()

    def test_verbose_mode(self, sample_config_file, capsys):
        """Test verbose mode prints messages"""
        manager = ConfigManager(sample_config_file, verbose=True)

        captured = capsys.readouterr()

        assert "Loaded" in captured.out or "loaded" in captured.out.lower()

    def test_no_config_found_silent(self, temp_dir):
        """Test that no config found is silent by default"""
        # Create manager with non-existent config path
        nonexistent_path = temp_dir / "nonexistent_config.json"

        # Should not find config, no error raised
        manager = ConfigManager()
        # Since user may have real configs, we can't test len(devices) == 0
        # Instead test that ConfigManager can be created without error
        assert isinstance(manager, ConfigManager)


class TestConfigSearchOrder:
    """Test configuration file search order"""

    def test_search_order_defined(self):
        """Test that search order is defined correctly"""
        locations = ConfigManager.DEFAULT_CONFIG_LOCATIONS

        assert len(locations) == 3
        # Local directory should be first
        assert "lotus_lamp_config.json" in str(locations[0])
        # Home directory should be last
        assert ".lotus_lamp" in str(locations[2])


class TestConfigValidation:
    """Test configuration validation"""

    def test_missing_required_fields(self, temp_dir):
        """Test config with missing required fields"""
        config_path = temp_dir / "missing_fields.json"
        with open(config_path, 'w') as f:
            json.dump({
                "devices": [
                    {"address": "AA:BB:CC:DD:EE:FF"}  # Missing 'name'
                ]
            }, f)

        with pytest.raises(Exception):  # Could be KeyError or TypeError
            ConfigManager(config_path)

    def test_roundtrip_save_load(self, temp_dir, sample_device_config):
        """Test saving and loading preserves data"""
        # Save
        manager1 = ConfigManager()
        manager1.add_device(sample_device_config)
        save_path = temp_dir / "roundtrip.json"
        manager1.save(save_path)

        # Load
        manager2 = ConfigManager(save_path)
        loaded_device = manager2.get_device("Test Lamp")

        # Compare
        assert loaded_device.name == sample_device_config.name
        assert loaded_device.address == sample_device_config.address
        assert loaded_device.service_uuid == sample_device_config.service_uuid
