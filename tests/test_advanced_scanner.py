#!/usr/bin/env python3
"""
Tests for lotus_lamp.advanced_scanner module
"""

import pytest
from lotus_lamp.advanced_scanner import ServiceInfo, AdvancedDeviceScanner


class TestServiceInfo:
    """Test ServiceInfo class"""

    def test_service_info_creation(self):
        """Test creating ServiceInfo object"""
        service = ServiceInfo(
            uuid="0000FFF0-0000-1000-8000-00805F9B34FB",
            description="Test Service"
        )

        assert service.uuid == "0000FFF0-0000-1000-8000-00805F9B34FB"
        assert service.description == "Test Service"
        assert service.characteristics == []

    def test_service_info_no_description(self):
        """Test creating ServiceInfo without description"""
        service = ServiceInfo(uuid="TEST-UUID")

        assert service.uuid == "TEST-UUID"
        assert service.description == ""

    def test_add_characteristic(self):
        """Test adding characteristic to service"""
        service = ServiceInfo(uuid="SERVICE-UUID")
        service.add_characteristic("CHAR-UUID", ["READ", "WRITE"])

        assert len(service.characteristics) == 1
        assert service.characteristics[0]['uuid'] == "CHAR-UUID"
        assert service.characteristics[0]['properties'] == ["READ", "WRITE"]

    def test_add_multiple_characteristics(self):
        """Test adding multiple characteristics"""
        service = ServiceInfo(uuid="SERVICE-UUID")
        service.add_characteristic("CHAR-1", ["READ"])
        service.add_characteristic("CHAR-2", ["WRITE", "NOTIFY"])
        service.add_characteristic("CHAR-3", ["INDICATE"])

        assert len(service.characteristics) == 3
        assert service.characteristics[0]['uuid'] == "CHAR-1"
        assert service.characteristics[1]['uuid'] == "CHAR-2"
        assert service.characteristics[2]['uuid'] == "CHAR-3"

    def test_to_dict(self):
        """Test converting ServiceInfo to dictionary"""
        service = ServiceInfo(uuid="SERVICE-UUID", description="Test")
        service.add_characteristic("CHAR-UUID", ["READ", "WRITE"])

        service_dict = service.to_dict()

        assert service_dict['uuid'] == "SERVICE-UUID"
        assert service_dict['description'] == "Test"
        assert len(service_dict['characteristics']) == 1
        assert service_dict['characteristics'][0]['uuid'] == "CHAR-UUID"


class TestAdvancedDeviceScanner:
    """Test AdvancedDeviceScanner class"""

    def test_known_services_defined(self):
        """Test that known services are defined"""
        assert len(AdvancedDeviceScanner.KNOWN_SERVICES) > 0
        assert "0000FFF0-0000-1000-8000-00805F9B34FB" in AdvancedDeviceScanner.KNOWN_SERVICES

    def test_known_characteristics_defined(self):
        """Test that known characteristics are defined"""
        assert len(AdvancedDeviceScanner.KNOWN_CHARACTERISTICS) > 0
        assert "0000FFF3-0000-1000-8000-00805F9B34FB" in AdvancedDeviceScanner.KNOWN_CHARACTERISTICS
        assert "0000FFF4-0000-1000-8000-00805F9B34FB" in AdvancedDeviceScanner.KNOWN_CHARACTERISTICS

    def test_identify_lotus_lamp_uuids_known_device(self):
        """Test identifying UUIDs from known Lotus Lamp structure"""
        device_info = {
            'address': 'AA:BB:CC:DD:EE:FF',
            'services': [
                {
                    'uuid': '0000FFF0-0000-1000-8000-00805F9B34FB',
                    'description': 'Lotus Lamp Service',
                    'characteristics': [
                        {
                            'uuid': '0000FFF3-0000-1000-8000-00805F9B34FB',
                            'properties': ['WRITE_NO_RESPONSE']
                        },
                        {
                            'uuid': '0000FFF4-0000-1000-8000-00805F9B34FB',
                            'properties': ['NOTIFY']
                        }
                    ]
                }
            ]
        }

        suggestions = AdvancedDeviceScanner.identify_lotus_lamp_uuids(device_info)

        assert suggestions is not None
        assert suggestions['service_uuid'] == '0000FFF0-0000-1000-8000-00805F9B34FB'
        assert suggestions['write_char_uuid'] == '0000FFF3-0000-1000-8000-00805F9B34FB'
        assert suggestions['notify_char_uuid'] == '0000FFF4-0000-1000-8000-00805F9B34FB'
        assert suggestions['confidence'] == 'high'

    def test_identify_lotus_lamp_uuids_custom_service(self):
        """Test identifying UUIDs from custom service with 0000FFxx pattern"""
        device_info = {
            'address': 'AA:BB:CC:DD:EE:FF',
            'services': [
                {
                    'uuid': '0000FFA0-0000-1000-8000-00805F9B34FB',
                    'description': 'Custom Service',
                    'characteristics': [
                        {
                            'uuid': 'CUSTOM-WRITE-UUID',
                            'properties': ['WRITE_NO_RESPONSE']
                        },
                        {
                            'uuid': 'CUSTOM-NOTIFY-UUID',
                            'properties': ['NOTIFY']
                        }
                    ]
                }
            ]
        }

        suggestions = AdvancedDeviceScanner.identify_lotus_lamp_uuids(device_info)

        assert suggestions is not None
        assert suggestions['service_uuid'] == '0000FFA0-0000-1000-8000-00805F9B34FB'
        assert suggestions['write_char_uuid'] == 'CUSTOM-WRITE-UUID'
        assert suggestions['notify_char_uuid'] == 'CUSTOM-NOTIFY-UUID'
        assert suggestions['confidence'] == 'medium'

    def test_identify_lotus_lamp_uuids_no_match(self):
        """Test identifying UUIDs when no match found"""
        device_info = {
            'address': 'AA:BB:CC:DD:EE:FF',
            'services': [
                {
                    'uuid': '00001800-0000-1000-8000-00805F9B34FB',  # Generic Access
                    'description': 'Generic Access',
                    'characteristics': []
                }
            ]
        }

        suggestions = AdvancedDeviceScanner.identify_lotus_lamp_uuids(device_info)

        assert suggestions is None

    def test_identify_lotus_lamp_uuids_incomplete_characteristics(self):
        """Test identifying UUIDs when characteristics are incomplete"""
        device_info = {
            'address': 'AA:BB:CC:DD:EE:FF',
            'services': [
                {
                    'uuid': '0000FFF0-0000-1000-8000-00805F9B34FB',
                    'description': 'Lotus Lamp Service',
                    'characteristics': [
                        {
                            'uuid': '0000FFF3-0000-1000-8000-00805F9B34FB',
                            'properties': ['WRITE_NO_RESPONSE']
                        }
                        # Missing notify characteristic
                    ]
                }
            ]
        }

        suggestions = AdvancedDeviceScanner.identify_lotus_lamp_uuids(device_info)

        # Should return None if not all UUIDs found
        assert suggestions is None

    def test_print_device_structure(self, capsys):
        """Test printing device structure"""
        device_info = {
            'address': 'AA:BB:CC:DD:EE:FF',
            'services': [
                {
                    'uuid': '0000FFF0-0000-1000-8000-00805F9B34FB',
                    'description': 'Lotus Lamp Service',
                    'characteristics': [
                        {
                            'uuid': '0000FFF3-0000-1000-8000-00805F9B34FB',
                            'properties': ['WRITE_NO_RESPONSE']
                        }
                    ]
                }
            ]
        }

        AdvancedDeviceScanner.print_device_structure(device_info)

        captured = capsys.readouterr()
        assert "AA:BB:CC:DD:EE:FF" in captured.out
        assert "0000FFF0-0000-1000-8000-00805F9B34FB" in captured.out
        assert "Lotus Lamp Service" in captured.out
        assert "0000FFF3-0000-1000-8000-00805F9B34FB" in captured.out
        assert "WRITE_NO_RESPONSE" in captured.out

    def test_print_uuid_suggestions(self, capsys):
        """Test printing UUID suggestions"""
        suggestions = {
            'service_uuid': '0000FFF0-0000-1000-8000-00805F9B34FB',
            'write_char_uuid': '0000FFF3-0000-1000-8000-00805F9B34FB',
            'notify_char_uuid': '0000FFF4-0000-1000-8000-00805F9B34FB',
            'confidence': 'high'
        }

        AdvancedDeviceScanner.print_uuid_suggestions(suggestions)

        captured = capsys.readouterr()
        assert "HIGH" in captured.out
        assert "0000FFF0-0000-1000-8000-00805F9B34FB" in captured.out
        assert "0000FFF3-0000-1000-8000-00805F9B34FB" in captured.out
        assert "0000FFF4-0000-1000-8000-00805F9B34FB" in captured.out
        assert "Configuration JSON" in captured.out

    def test_case_insensitive_uuid_matching(self):
        """Test that UUID matching is case-insensitive"""
        device_info = {
            'address': 'AA:BB:CC:DD:EE:FF',
            'services': [
                {
                    'uuid': '0000fff0-0000-1000-8000-00805f9b34fb',  # lowercase
                    'description': 'Lotus Lamp Service',
                    'characteristics': [
                        {
                            'uuid': '0000fff3-0000-1000-8000-00805f9b34fb',  # lowercase
                            'properties': ['WRITE_NO_RESPONSE']
                        },
                        {
                            'uuid': '0000fff4-0000-1000-8000-00805f9b34fb',  # lowercase
                            'properties': ['NOTIFY']
                        }
                    ]
                }
            ]
        }

        suggestions = AdvancedDeviceScanner.identify_lotus_lamp_uuids(device_info)

        assert suggestions is not None
        assert suggestions['confidence'] == 'high'


# Note: Integration tests for discover_device_structure() would require
# either real BLE devices or mocking the BleakClient. These are marked for
# future implementation with proper mocking infrastructure.

@pytest.mark.integration
class TestAdvancedScannerIntegration:
    """Integration tests requiring BLE hardware or mocking"""

    @pytest.mark.skip(reason="Requires BLE hardware or mock infrastructure")
    async def test_discover_device_structure(self):
        """Test discovering device structure"""
        # Would require mocking BleakClient or real hardware
        pass

    @pytest.mark.skip(reason="Requires BLE hardware or mock infrastructure")
    async def test_discover_device_structure_timeout(self):
        """Test timeout handling in device discovery"""
        # Would require mocking BleakClient
        pass
