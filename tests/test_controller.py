"""
Tests for LotusLamp controller

Note: These tests do NOT require a physical lamp.
They test configuration, initialization, and error handling.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from lotus_lamp import LotusLamp, DeviceConfig


class TestLotusLampInit:
    """Test LotusLamp initialization"""

    def test_init_with_device_config(self, sample_device_config):
        """Test initialization with explicit DeviceConfig"""
        lamp = LotusLamp(device_config=sample_device_config)

        assert lamp.config == sample_device_config
        assert lamp.config.name == "Test Lamp"

    def test_init_with_config_path(self, sample_config_file):
        """Test initialization with config file path"""
        lamp = LotusLamp(config_path=sample_config_file)

        assert lamp.config is not None
        assert lamp.config.name == "Test Lamp"

    def test_init_with_invalid_path(self, temp_dir):
        """Test initialization with non-existent config path"""
        with pytest.raises(FileNotFoundError):
            LotusLamp(config_path=temp_dir / "nonexistent.json")

    def test_init_with_device_name(self, multi_device_config_file):
        """Test initialization with specific device name"""
        lamp = LotusLamp(
            config_path=multi_device_config_file,
            device_name="Bedroom"
        )

        assert lamp.config.name == "Bedroom"
        assert lamp.config.address == "AA:BB:CC:DD:EE:FF"

    def test_init_with_invalid_device_name(self, sample_config_file):
        """Test initialization with non-existent device name"""
        with pytest.raises(ValueError) as exc_info:
            LotusLamp(
                config_path=sample_config_file,
                device_name="Nonexistent"
            )

        assert "not found" in str(exc_info.value).lower()
        assert "available devices" in str(exc_info.value).lower()

    def test_init_no_config_available(self):
        """Test initialization with no configuration"""
        # Mock ConfigManager to return no devices
        with patch('lotus_lamp.controller.ConfigManager') as mock_manager:
            mock_instance = Mock()
            mock_instance.get_default_device.return_value = None
            mock_instance.list_devices.return_value = []
            mock_manager.return_value = mock_instance

            with pytest.raises(ValueError) as exc_info:
                LotusLamp()

            error_msg = str(exc_info.value).lower()
            assert ("not configured" in error_msg or "no lotus lamp" in error_msg)
            assert "setup" in error_msg

    def test_init_verbose_mode(self, sample_config_file, capsys):
        """Test verbose mode shows loading info"""
        lamp = LotusLamp(config_path=sample_config_file, verbose=True)

        captured = capsys.readouterr()
        assert "Test Lamp" in captured.out or "loaded" in captured.out.lower()

    def test_init_verbose_from_env(self, sample_config_file, monkeypatch, capsys):
        """Test verbose mode from environment variable"""
        monkeypatch.setenv("LOTUS_LAMP_VERBOSE", "1")

        lamp = LotusLamp(config_path=sample_config_file)

        captured = capsys.readouterr()
        # Should be verbose due to environment variable
        assert len(captured.out) > 0


class TestLotusLampProperties:
    """Test LotusLamp property accessors"""

    def test_device_name_property(self, sample_device_config):
        """Test DEVICE_NAME property for backwards compatibility"""
        lamp = LotusLamp(device_config=sample_device_config)

        assert lamp.DEVICE_NAME == "Test Lamp"

    def test_service_uuid_property(self, sample_device_config):
        """Test SERVICE_UUID property"""
        lamp = LotusLamp(device_config=sample_device_config)

        assert lamp.SERVICE_UUID == "0000FFF0-0000-1000-8000-00805F9B34FB"

    def test_write_char_uuid_property(self, sample_device_config):
        """Test WRITE_CHAR_UUID property"""
        lamp = LotusLamp(device_config=sample_device_config)

        assert lamp.WRITE_CHAR_UUID == "0000FFF3-0000-1000-8000-00805F9B34FB"

    def test_notify_char_uuid_property(self, sample_device_config):
        """Test NOTIFY_CHAR_UUID property"""
        lamp = LotusLamp(device_config=sample_device_config)

        assert lamp.NOTIFY_CHAR_UUID == "0000FFF4-0000-1000-8000-00805F9B34FB"


class TestLotusLampDefaults:
    """Test default UUID values"""

    def test_default_uuids(self):
        """Test that default UUIDs are defined"""
        assert hasattr(LotusLamp, 'DEFAULT_SERVICE_UUID')
        assert hasattr(LotusLamp, 'DEFAULT_WRITE_CHAR_UUID')
        assert hasattr(LotusLamp, 'DEFAULT_NOTIFY_CHAR_UUID')

    def test_device_config_uses_defaults(self):
        """Test that DeviceConfig uses default UUIDs"""
        config = DeviceConfig(name="Test")

        assert config.service_uuid == LotusLamp.DEFAULT_SERVICE_UUID
        assert config.write_char_uuid == LotusLamp.DEFAULT_WRITE_CHAR_UUID
        assert config.notify_char_uuid == LotusLamp.DEFAULT_NOTIFY_CHAR_UUID


class TestLotusLampState:
    """Test LotusLamp state management"""

    def test_initial_state(self, sample_device_config):
        """Test initial state of lamp"""
        lamp = LotusLamp(device_config=sample_device_config)

        assert lamp.device is None
        assert lamp.client is None
        assert lamp._connected is False

    def test_config_stored(self, sample_device_config):
        """Test that config is stored correctly"""
        lamp = LotusLamp(device_config=sample_device_config)

        assert lamp.config is not None
        assert lamp.config.name == sample_device_config.name
        assert lamp.config.address == sample_device_config.address


class TestLotusLampErrorMessages:
    """Test error message quality"""

    def test_no_config_error_helpful(self):
        """Test that no config error is helpful"""
        with patch('lotus_lamp.controller.ConfigManager') as mock_manager:
            mock_instance = Mock()
            mock_instance.get_default_device.return_value = None
            mock_instance.list_devices.return_value = []
            mock_manager.return_value = mock_instance

            with pytest.raises(ValueError) as exc_info:
                LotusLamp()

            error_msg = str(exc_info.value)
            # Should mention setup wizard
            assert "setup" in error_msg.lower()
            # Should provide command
            assert "python -m lotus_lamp.setup" in error_msg

    def test_device_not_found_error_shows_available(self, multi_device_config_file):
        """Test that device not found error shows available devices"""
        with pytest.raises(ValueError) as exc_info:
            LotusLamp(
                config_path=multi_device_config_file,
                device_name="Nonexistent"
            )

        error_msg = str(exc_info.value)
        # Should show available devices
        assert "Living Room" in error_msg or "Bedroom" in error_msg

    def test_file_not_found_error_helpful(self, temp_dir):
        """Test that file not found error is helpful"""
        with pytest.raises(FileNotFoundError) as exc_info:
            LotusLamp(config_path=temp_dir / "missing.json")

        error_msg = str(exc_info.value)
        assert "not found" in error_msg.lower()
