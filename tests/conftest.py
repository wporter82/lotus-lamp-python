"""
Pytest configuration and fixtures
"""

import pytest
import json
import tempfile
from pathlib import Path
from lotus_lamp.config import DeviceConfig, ConfigManager


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_device_config():
    """Sample device configuration"""
    return DeviceConfig(
        name="Test Lamp",
        address="AA:BB:CC:DD:EE:FF",
        service_uuid="0000FFF0-0000-1000-8000-00805F9B34FB",
        write_char_uuid="0000FFF3-0000-1000-8000-00805F9B34FB",
        notify_char_uuid="0000FFF4-0000-1000-8000-00805F9B34FB"
    )


@pytest.fixture
def sample_config_file(temp_dir, sample_device_config):
    """Create a sample config file"""
    config_path = temp_dir / "test_config.json"
    config_data = {
        "devices": [sample_device_config.to_dict()]
    }

    with open(config_path, 'w') as f:
        json.dump(config_data, f)

    return config_path


@pytest.fixture
def multi_device_config_file(temp_dir):
    """Create a config file with multiple devices"""
    config_path = temp_dir / "multi_config.json"
    config_data = {
        "devices": [
            {
                "name": "Living Room",
                "address": "11:22:33:44:55:66",
                "service_uuid": "0000FFF0-0000-1000-8000-00805F9B34FB",
                "write_char_uuid": "0000FFF3-0000-1000-8000-00805F9B34FB",
                "notify_char_uuid": "0000FFF4-0000-1000-8000-00805F9B34FB"
            },
            {
                "name": "Bedroom",
                "address": "AA:BB:CC:DD:EE:FF",
                "service_uuid": "0000FFF0-0000-1000-8000-00805F9B34FB",
                "write_char_uuid": "0000FFF3-0000-1000-8000-00805F9B34FB",
                "notify_char_uuid": "0000FFF4-0000-1000-8000-00805F9B34FB"
            }
        ]
    }

    with open(config_path, 'w') as f:
        json.dump(config_data, f)

    return config_path


@pytest.fixture
def invalid_json_file(temp_dir):
    """Create an invalid JSON file"""
    config_path = temp_dir / "invalid.json"
    with open(config_path, 'w') as f:
        f.write("{ invalid json")
    return config_path


@pytest.fixture
def empty_config_file(temp_dir):
    """Create an empty config file"""
    config_path = temp_dir / "empty.json"
    with open(config_path, 'w') as f:
        json.dump({"devices": []}, f)
    return config_path


@pytest.fixture
def legacy_single_device_config(temp_dir):
    """Create a legacy single-device config file"""
    config_path = temp_dir / "legacy.json"
    config_data = {
        "name": "Legacy Lamp",
        "address": "00:11:22:33:44:55",
        "service_uuid": "0000FFF0-0000-1000-8000-00805F9B34FB",
        "write_char_uuid": "0000FFF3-0000-1000-8000-00805F9B34FB",
        "notify_char_uuid": "0000FFF4-0000-1000-8000-00805F9B34FB"
    }

    with open(config_path, 'w') as f:
        json.dump(config_data, f)

    return config_path
