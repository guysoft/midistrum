"""Tests for MIDI device name fallback logic (fixes crash with None device names)."""

import sys
import os
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from android_midi import get_midi_device_display_name


def _make_device_info(name=None, product=None, manufacturer=None):
    """Create a mock MidiDeviceInfo with configurable property values."""
    props = MagicMock()

    def get_string(key):
        prop_map = {
            "PROPERTY_NAME": name,
            "PROPERTY_PRODUCT": product,
            "PROPERTY_MANUFACTURER": manufacturer,
        }
        for mock_attr, value in prop_map.items():
            if key is getattr(dev_info, mock_attr, None):
                return value
            if hasattr(key, '_mock_name') and mock_attr in str(key._mock_name):
                return value
        return name

    props.getString = MagicMock(side_effect=get_string)
    dev_info = MagicMock()
    dev_info.getProperties.return_value = props
    return dev_info


class TestGetMidiDeviceDisplayName:
    """Tests for get_midi_device_display_name fallback chain."""

    def test_valid_name_passes_through(self):
        dev = _make_device_info(name="Roland MIDI Keyboard")
        result = get_midi_device_display_name(dev, 0)
        assert result == "Roland MIDI Keyboard"

    def test_none_name_falls_back_to_generic(self):
        dev = _make_device_info(name=None)
        result = get_midi_device_display_name(dev, 0)
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

    def test_none_name_generic_includes_index(self):
        dev = _make_device_info(name=None)
        result = get_midi_device_display_name(dev, 4)
        assert "5" in result

    def test_empty_string_name_falls_back(self):
        dev = _make_device_info(name="")
        result = get_midi_device_display_name(dev, 0)
        assert result is not None
        assert len(result) > 0


class TestGetMidiDeviceDisplayNameFallbackChain:
    """Test the PROPERTY_NAME -> PROPERTY_PRODUCT -> PROPERTY_MANUFACTURER chain."""

    def test_fallback_to_product(self):
        props = MagicMock()
        values = [None, "USB MIDI Interface", None]
        props.getString = MagicMock(side_effect=values)
        dev = MagicMock()
        dev.getProperties.return_value = props

        result = get_midi_device_display_name(dev, 0)
        assert result == "USB MIDI Interface"

    def test_fallback_to_manufacturer(self):
        props = MagicMock()
        values = [None, None, "Yamaha"]
        props.getString = MagicMock(side_effect=values)
        dev = MagicMock()
        dev.getProperties.return_value = props

        result = get_midi_device_display_name(dev, 0)
        assert result == "Yamaha"

    def test_fallback_to_generic_when_all_none(self):
        props = MagicMock()
        values = [None, None, None]
        props.getString = MagicMock(side_effect=values)
        dev = MagicMock()
        dev.getProperties.return_value = props

        result = get_midi_device_display_name(dev, 2)
        assert result == "MIDI Device 3"

    def test_name_preferred_over_product(self):
        props = MagicMock()
        values = ["My Synth"]
        props.getString = MagicMock(side_effect=values)
        dev = MagicMock()
        dev.getProperties.return_value = props

        result = get_midi_device_display_name(dev, 0)
        assert result == "My Synth"
