"""Diagnostics support for the EPA Victoria Air Quality integration."""

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from . import EPAConfigEntry

TO_REDACT = {
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LONGITUDE,
}


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: EPAConfigEntry) -> dict[str, Any]:
    """Return diagnostics for a specific config entry."""
    coordinator = entry.runtime_data.coordinator
    collector = coordinator.collector
    current_api_probe = await collector.async_check_api_reachable()
    last_updated_local = dt_util.as_local(collector.last_updated)

    return async_redact_data(
        {
            "entry": entry.as_dict(),
            "coordinator": {
                "last_update_success": coordinator.last_update_success,
                "last_exception": (str(coordinator.last_exception) if coordinator.last_exception is not None else None),
            },
            "collector": {
                "last_poll_api_reachable": collector.last_poll_api_reachable,
                "last_update_successful": collector.last_update_successful,
                "last_response_status": collector.last_response_status,
                "last_request_error": collector.last_request_error,
                "site_found": collector.site_found,
                "sites_found": collector.sites_found,
                "site_id": collector.site_id,
                "site_name": collector.site_name,
                "last_updated": last_updated_local.isoformat(),
                "until": collector.until,
                "current_api_reachable": current_api_probe["reachable"],
                "current_api_response_status": current_api_probe["response_status"],
                "current_api_error": current_api_probe["error"],
                "available_sensor_keys": sorted(collector.get_available_sensor_keys()),
                "observation_data": collector.observation_data,
                "sensor_attributes": collector.sensor_attributes,
            },
        },
        TO_REDACT,
    )
