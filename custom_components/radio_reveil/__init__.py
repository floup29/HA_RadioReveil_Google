"""Radio Réveil — Home Assistant Integration."""
from __future__ import annotations

import logging
from datetime import time as dt_time

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    PLATFORMS,
    DAYS_FR,
    DEFAULT_TIMES,
    DEFAULT_ENABLED,
)
from .coordinator import RadioReveilCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Radio Réveil from a config entry."""
    coordinator = RadioReveilCoordinator(hass, entry)

    # Initialise default schedule
    for i, day_key in enumerate(DAYS_FR):
        t_str = DEFAULT_TIMES[i]
        h, m = map(int, t_str.split(":"))
        coordinator.set_day_time(day_key, dt_time(h, m))
        coordinator.set_day_enabled(day_key, DEFAULT_ENABLED[i])

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    _LOGGER.info("Radio Réveil chargé — entrée %s", entry.entry_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator: RadioReveilCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
    await coordinator.async_shutdown()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when options are updated."""
    await hass.config_entries.async_reload(entry.entry_id)
