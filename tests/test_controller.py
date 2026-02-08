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



class TestTimerCommands:
    """Test timer command packet construction"""

    def _make_lamp(self, sample_device_config):
        """Create a lamp with mocked BLE connection"""
        lamp = LotusLamp(device_config=sample_device_config)
        lamp._connected = True
        lamp.client = AsyncMock()
        lamp.client.write_gatt_char = AsyncMock()
        return lamp

    def _run(self, coro):
        """Run a coroutine synchronously"""
        import asyncio
        return asyncio.run(coro)

    def test_sync_time_sends_9_bytes(self, sample_device_config):
        """sync_time sends correct 9-byte packet using E1Achieve format"""
        lamp = self._make_lamp(sample_device_config)
        self._run(lamp.sync_time())

        packet = lamp.client.write_gatt_char.call_args[0][1]
        # E1Achieve format: [0x7E] [LEN] [CMD] [params...] [0x00] [0xEF]
        # DATA_TIME: length=0x06, params: hour, minute, second, weekday = 4 bytes
        # Total: 9 bytes
        assert len(packet) == 9
        assert packet[0] == 0x7E
        assert packet[1] == 0x06  # DATA_TIME protocol length
        assert packet[2] == 0x83  # DATA_TIME command
        # Validate hour, minute, second are reasonable values
        assert 0 <= packet[3] <= 23  # hour
        assert 0 <= packet[4] <= 59  # minute
        assert 0 <= packet[5] <= 59  # second
        # Weekday: Java Calendar convention (Mon=1, ..., Sat=6, Sun=7)
        assert 0 <= packet[6] <= 7   # weekday
        assert packet[7] == 0x00
        assert packet[8] == 0xEF

    def test_set_timer_on_correct_packet(self, sample_device_config):
        """set_timer_on sends correct 9-byte packet using E1Achieve format"""
        lamp = self._make_lamp(sample_device_config)
        self._run(lamp.set_timer_on(7, 30))

        packet = lamp.client.write_gatt_char.call_args[0][1]
        # E1Achieve format with 5 params: bitmask overwrites position 7
        # Total: 9 bytes
        assert len(packet) == 9
        assert packet[0] == 0x7E
        assert packet[1] == 0x07  # TIMER_SWITCH protocol length
        assert packet[2] == 0x82  # TIMER_SWITCH command
        assert packet[3] == 7     # hour
        assert packet[4] == 30    # minute
        assert packet[5] == 0x00  # padding
        assert packet[6] == 0x00  # type = ON
        assert packet[7] == 0x80  # bitmask (enabled, no repeat)
        assert packet[8] == 0xEF

    def test_set_timer_off_correct_packet(self, sample_device_config):
        """set_timer_off sends correct 9-byte packet with type=0x01"""
        lamp = self._make_lamp(sample_device_config)
        self._run(lamp.set_timer_off(23, 0))

        packet = lamp.client.write_gatt_char.call_args[0][1]
        assert len(packet) == 9
        assert packet[1] == 0x07   # protocol length
        assert packet[2] == 0x82   # TIMER_SWITCH command
        assert packet[3] == 23     # hour
        assert packet[4] == 0      # minute
        assert packet[6] == 0x01   # type = OFF
        assert packet[7] == 0x80   # bitmask

    def test_set_timer_on_simple(self, sample_device_config):
        """set_timer_on with just hour/minute"""
        lamp = self._make_lamp(sample_device_config)
        self._run(lamp.set_timer_on(8, 0))

        packet = lamp.client.write_gatt_char.call_args[0][1]
        assert packet[3] == 8      # hour
        assert packet[4] == 0      # minute
        assert packet[6] == 0x00   # type = ON

    def test_disable_timer_on(self, sample_device_config):
        """disable_timer_on sends ON type with zeroed time"""
        lamp = self._make_lamp(sample_device_config)
        self._run(lamp.disable_timer_on())

        packet = lamp.client.write_gatt_char.call_args[0][1]
        assert packet[2] == 0x82   # TIMER_SWITCH command
        assert packet[6] == 0x00   # type = ON

    def test_disable_timer_off(self, sample_device_config):
        """disable_timer_off sends OFF type with zeroed time"""
        lamp = self._make_lamp(sample_device_config)
        self._run(lamp.disable_timer_off())

        packet = lamp.client.write_gatt_char.call_args[0][1]
        assert packet[2] == 0x82   # TIMER_SWITCH command
        assert packet[6] == 0x01   # type = OFF

    def test_timer_hour_clamped(self, sample_device_config):
        """Hours are clamped to 0-23"""
        lamp = self._make_lamp(sample_device_config)
        self._run(lamp.set_timer_on(25, 0))
        # hour at position 3 in E1Achieve format (after header, length, cmd)
        assert lamp.client.write_gatt_char.call_args[0][1][3] == 23

    def test_timer_minute_clamped(self, sample_device_config):
        """Minutes are clamped to 0-59"""
        lamp = self._make_lamp(sample_device_config)
        self._run(lamp.set_timer_on(12, 99))
        # minute at position 4 in E1Achieve format
        assert lamp.client.write_gatt_char.call_args[0][1][4] == 59

    def test_sync_time_weekday_conversion(self, sample_device_config):
        """Test weekday conversion from Python to Java Calendar convention"""
        from datetime import datetime
        from unittest.mock import patch

        lamp = self._make_lamp(sample_device_config)

        # Test each day of the week
        test_cases = [
            # (Python weekday, Expected lamp weekday, Day name)
            (0, 1, "Monday"),     # Mon: Python=0 -> Lamp=1
            (1, 2, "Tuesday"),    # Tue: Python=1 -> Lamp=2
            (2, 3, "Wednesday"),  # Wed: Python=2 -> Lamp=3
            (3, 4, "Thursday"),   # Thu: Python=3 -> Lamp=4
            (4, 5, "Friday"),     # Fri: Python=4 -> Lamp=5
            (5, 6, "Saturday"),   # Sat: Python=5 -> Lamp=6
            (6, 7, "Sunday"),     # Sun: Python=6 -> Lamp=7
        ]

        for py_weekday, expected_lamp_weekday, day_name in test_cases:
            # Mock datetime to return specific weekday
            mock_now = datetime(2026, 2, 2 + py_weekday, 12, 0, 0)  # Start from a Monday
            with patch('lotus_lamp.controller.datetime') as mock_datetime:
                mock_datetime.now.return_value = mock_now

                self._run(lamp.sync_time())

                packet = lamp.client.write_gatt_char.call_args[0][1]
                actual_weekday = packet[6]

                assert actual_weekday == expected_lamp_weekday, \
                    f"{day_name}: Expected lamp weekday {expected_lamp_weekday}, got {actual_weekday}"
