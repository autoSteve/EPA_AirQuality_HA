"""Tests for the EPA Victoria Air Quality diagnostics."""

from datetime import UTC, datetime as dt
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.components.diagnostics import REDACTED
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant

from tests.components.diagnostics import get_diagnostics_for_config_entry
from tests.typing import ClientSessionGenerator

from . import TEST_SITE_ID_1, TEST_SITE_NAME_1, create_mock_config_entry


async def test_entry_diagnostics(
    hass: HomeAssistant,
    hass_client: ClientSessionGenerator,
) -> None:
    """Test config entry diagnostics."""
    entry = create_mock_config_entry()
    entry.add_to_hass(hass)

    mock_collector = MagicMock()
    mock_collector.async_update = AsyncMock(return_value=None)
    mock_collector.async_setup = AsyncMock(return_value=None)
    mock_collector.async_check_api_reachable = AsyncMock(
        return_value={
            "reachable": True,
            "response_status": 200,
            "error": None,
        }
    )
    mock_collector.get_sensor.return_value = None
    mock_collector.get_available_sensor_keys.return_value = {"aqi", "pm25"}
    mock_collector.last_poll_api_reachable = True
    mock_collector.last_update_successful = True
    mock_collector.last_response_status = 200
    mock_collector.last_request_error = None
    mock_collector.site_found = True
    mock_collector.sites_found = True
    mock_collector.site_id = TEST_SITE_ID_1
    mock_collector.site_name = TEST_SITE_NAME_1
    mock_collector.last_updated = dt(2026, 8, 23, 10, 30, 0, tzinfo=UTC)
    mock_collector.until = "2026-08-23T11:00:00"
    mock_collector.observation_data = {"aqi": 42.0, "pm25": 8.4}
    mock_collector.sensor_attributes = {
        "pm25": {
            "confidence": 0.95,
            "data_source": "1HR_AV",
        }
    }

    with patch(
        "homeassistant.components.epa_victoria_air_quality.Collector",
        return_value=mock_collector,
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    with patch(
        "homeassistant.components.epa_victoria_air_quality.diagnostics.dt_util.as_local",
        return_value=dt(2026, 8, 23, 20, 30, 0, tzinfo=UTC),
    ):
        result = await get_diagnostics_for_config_entry(hass, hass_client, entry)

    assert result["entry"]["options"][CONF_API_KEY] == REDACTED
    assert result["collector"] == {
        "last_poll_api_reachable": True,
        "last_update_successful": True,
        "last_response_status": 200,
        "last_request_error": None,
        "site_found": True,
        "sites_found": True,
        "site_id": TEST_SITE_ID_1,
        "site_name": TEST_SITE_NAME_1,
        "last_updated": "2026-08-23T20:30:00+00:00",
        "until": "2026-08-23T11:00:00",
        "current_api_reachable": True,
        "current_api_response_status": 200,
        "current_api_error": None,
        "available_sensor_keys": ["aqi", "pm25"],
        "observation_data": {"aqi": 42.0, "pm25": 8.4},
        "sensor_attributes": {
            "pm25": {
                "confidence": 0.95,
                "data_source": "1HR_AV",
            }
        },
    }
    assert result["coordinator"] == {
        "last_update_success": True,
        "last_exception": None,
    }
