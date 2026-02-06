#!/usr/bin/env python3
"""
Tests for lotus_lamp.scanner module
"""

import pytest
from lotus_lamp.scanner import DeviceInfo, LotusLampScanner


class TestDeviceInfo:
    """Test DeviceInfo class"""

    def test_device_info_creation(self):
        """Test creating DeviceInfo object"""
        device = DeviceInfo(
            name="Test Lamp",
            address="AA:BB:CC:DD:EE:FF",
            rssi=-50,
            services=["0000FFF0-0000-1000-8000-00805F9B34FB"]
        )

        assert device.name == "Test Lamp"
        assert device.address == "AA:BB:CC:DD:EE:FF"
        assert device.rssi == -50
        assert len(device.services) == 1

    def test_device_info_to_dict(self):
        """Test converting DeviceInfo to dictionary"""
        device = DeviceInfo(
            name="Test Lamp",
            address="AA:BB:CC:DD:EE:FF",
            rssi=-50,
            services=["0000FFF0-0000-1000-8000-00805F9B34FB"]
        )

        device_dict = device.to_dict()

        assert device_dict['name'] == "Test Lamp"
        assert device_dict['address'] == "AA:BB:CC:DD:EE:FF"
        assert device_dict['rssi'] == -50
        assert device_dict['services'] == ["0000FFF0-0000-1000-8000-00805F9B34FB"]

    def test_device_info_repr(self):
        """Test DeviceInfo string representation"""
        device = DeviceInfo(
            name="Test Lamp",
            address="AA:BB:CC:DD:EE:FF",
            rssi=-50,
            services=[]
        )

        repr_str = repr(device)
        assert "Test Lamp" in repr_str
        assert "AA:BB:CC:DD:EE:FF" in repr_str
        assert "-50" in repr_str

    def test_device_info_empty_services(self):
        """Test DeviceInfo with empty services list"""
        device = DeviceInfo(
            name="Unknown Device",
            address="11:22:33:44:55:66",
            rssi=-80,
            services=[]
        )

        assert device.services == []
        assert len(device.services) == 0


class TestLotusLampScanner:
    """Test LotusLampScanner class"""

    def test_common_service_uuids_defined(self):
        """Test that common service UUIDs are defined"""
        assert len(LotusLampScanner.COMMON_SERVICE_UUIDS) > 0
        assert "0000FFF0-0000-1000-8000-00805F9B34FB" in LotusLampScanner.COMMON_SERVICE_UUIDS

    def test_common_name_patterns_defined(self):
        """Test that common name patterns are defined"""
        assert len(LotusLampScanner.COMMON_NAME_PATTERNS) > 0
        assert any("MELK" in pattern for pattern in LotusLampScanner.COMMON_NAME_PATTERNS)

    def test_generate_config_with_defaults(self):
        """Test generating config with default UUIDs"""
        device = DeviceInfo(
            name="Test Lamp",
            address="AA:BB:CC:DD:EE:FF",
            rssi=-50,
            services=[]
        )

        config = LotusLampScanner.generate_config(device)

        assert config['name'] == "Test Lamp"
        assert config['address'] == "AA:BB:CC:DD:EE:FF"
        assert config['service_uuid'] == "0000FFF0-0000-1000-8000-00805F9B34FB"
        assert config['write_char_uuid'] == "0000FFF3-0000-1000-8000-00805F9B34FB"
        assert config['notify_char_uuid'] == "0000FFF4-0000-1000-8000-00805F9B34FB"

    def test_generate_config_with_custom_uuids(self):
        """Test generating config with custom UUIDs"""
        device = DeviceInfo(
            name="Custom Lamp",
            address="11:22:33:44:55:66",
            rssi=-60,
            services=[]
        )

        config = LotusLampScanner.generate_config(
            device,
            service_uuid="CUSTOM-SERVICE-UUID",
            write_char_uuid="CUSTOM-WRITE-UUID",
            notify_char_uuid="CUSTOM-NOTIFY-UUID"
        )

        assert config['service_uuid'] == "CUSTOM-SERVICE-UUID"
        assert config['write_char_uuid'] == "CUSTOM-WRITE-UUID"
        assert config['notify_char_uuid'] == "CUSTOM-NOTIFY-UUID"

    def test_generate_config_partial_custom_uuids(self):
        """Test generating config with some custom UUIDs"""
        device = DeviceInfo(
            name="Partial Custom Lamp",
            address="AA:BB:CC:DD:EE:FF",
            rssi=-50,
            services=[]
        )

        config = LotusLampScanner.generate_config(
            device,
            service_uuid="CUSTOM-SERVICE-UUID"
            # write_char and notify_char should use defaults
        )

        assert config['service_uuid'] == "CUSTOM-SERVICE-UUID"
        assert config['write_char_uuid'] == "0000FFF3-0000-1000-8000-00805F9B34FB"
        assert config['notify_char_uuid'] == "0000FFF4-0000-1000-8000-00805F9B34FB"

    def test_print_device_table_empty(self, capsys):
        """Test printing device table with no devices"""
        LotusLampScanner.print_device_table([])

        captured = capsys.readouterr()
        assert "No devices found" in captured.out

    def test_print_device_table_with_devices(self, capsys):
        """Test printing device table with devices"""
        devices = [
            DeviceInfo("Lamp 1", "AA:BB:CC:DD:EE:FF", -50, ["UUID1"]),
            DeviceInfo("Lamp 2", "11:22:33:44:55:66", -60, ["UUID2", "UUID3"])
        ]

        LotusLampScanner.print_device_table(devices)

        captured = capsys.readouterr()
        assert "Found 2 device(s)" in captured.out
        assert "Lamp 1" in captured.out
        assert "Lamp 2" in captured.out
        assert "AA:BB:CC:DD:EE:FF" in captured.out
        assert "11:22:33:44:55:66" in captured.out

    def test_print_device_table_many_services(self, capsys):
        """Test printing device with many services shows truncation"""
        devices = [
            DeviceInfo("Lamp", "AA:BB:CC:DD:EE:FF", -50,
                      ["UUID1", "UUID2", "UUID3", "UUID4", "UUID5"])
        ]

        LotusLampScanner.print_device_table(devices)

        captured = capsys.readouterr()
        assert "+3 more" in captured.out  # Should show first 2 + "3 more"


# Note: Integration tests for scan_all() and scan_lotus_lamps() would require
# either real BLE devices or mocking the BleakScanner. These are marked for
# future implementation with proper mocking infrastructure.

@pytest.mark.integration
class TestScannerIntegration:
    """Integration tests requiring BLE hardware or mocking"""

    @pytest.mark.skip(reason="Requires BLE hardware or mock infrastructure")
    async def test_scan_all(self):
        """Test scanning for all devices"""
        # Would require mocking BleakScanner or real hardware
        pass

    @pytest.mark.skip(reason="Requires BLE hardware or mock infrastructure")
    async def test_scan_lotus_lamps(self):
        """Test scanning for Lotus Lamp devices"""
        # Would require mocking BleakScanner or real hardware
        pass
