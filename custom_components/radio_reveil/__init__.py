"""Radio Réveil — supports multiple alarm instances."""
from __future__ import annotations

import logging
import os
from datetime import time as dt_time
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS, DAYS_FR, DEFAULT_TIMES, DEFAULT_ENABLED

_LOGGER = logging.getLogger(__name__)

ICON_URL = "/local/radio_reveil/icon.png"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register static path for the integration icon."""
    icon_path = Path(__file__).parent / "icon.png"
    if icon_path.exists():
        await hass.http.async_register_static_paths([
            StaticPathConfig(
                url_path="/local/radio_reveil",
                path=str(icon_path.parent),
                cache_headers=True,
            )
        ])
        _LOGGER.debug("Radio Réveil icon served at %s", ICON_URL)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    from .coordinator import RadioReveilCoordinator

    coordinator = RadioReveilCoordinator(hass, entry)

    for i, day_key in enumerate(DAYS_FR):
        h, m = map(int, DEFAULT_TIMES[i].split(":"))
        coordinator.set_day_time(day_key, dt_time(h, m))
        coordinator.set_day_enabled(day_key, DEFAULT_ENABLED[i])

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    _LOGGER.info("Radio Réveil '%s' chargé (%s)", entry.title, entry.entry_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    from .coordinator import RadioReveilCoordinator
    coordinator: RadioReveilCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
    await coordinator.async_shutdown()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
