"""Shared fixtures that mock Android-specific modules for desktop testing."""

import sys
from unittest.mock import MagicMock

import pytest


def _install_android_mocks():
    """Insert mock modules so android_midi can be imported without jnius/Android."""
    mock_jnius = MagicMock()
    mock_jnius.autoclass = MagicMock(side_effect=lambda cls: MagicMock(name=cls))
    mock_jnius.cast = MagicMock(side_effect=lambda cls, obj: obj)

    mocks = {
        "jnius": mock_jnius,
        "plyer": MagicMock(),
        "plyer.platforms": MagicMock(),
        "plyer.platforms.android": MagicMock(),
        "android": MagicMock(),
        "android.media": MagicMock(),
        "android.media.midi": MagicMock(),
    }
    for name, mock in mocks.items():
        sys.modules.setdefault(name, mock)


_install_android_mocks()
