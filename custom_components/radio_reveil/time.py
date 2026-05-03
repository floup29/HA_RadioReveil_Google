"""Time entities for Radio Réveil — one per day."""
from __future__ import annotations

from datetime import time as dt_time

from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, DAYS_FR, DAYS_FR_FULL, DEFAULT_TIMES, VERSION
from .coordinator import RadioReveilCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: RadioReveilCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for i, day_key in enumerate(DAYS_FR):
        h, m = map(int, DEFAULT_TIMES[i].split(":"))
        entities.append(
            RadioReveilTimeEntity(coordinator, entry, day_key, DAYS_FR_FULL[i], dt_time(h, m))
        )
    async_add_entities(entities)


class RadioReveilTimeEntity(TimeEntity):
    """Alarm time for a single weekday."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:clock-outline"

    def __init__(
        self,
        coordinator: RadioReveilCoordinator,
        entry: ConfigEntry,
        day_key: str,
        day_label: str,
        default_time: dt_time,
    ) -> None:
        self._coordinator = coordinator
        self._day_key = day_key
        self._value = default_time
        self._attr_unique_id = f"{entry.entry_id}_time_{day_key}"
        self._attr_name = f"Heure {day_label}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Radio Réveil",
            manufacturer="Communauté HA",
            model="Radio Réveil Hebdomadaire",
            sw_version=VERSION,
        )

    @property
    def native_value(self) -> dt_time:
        return self._coordinator.get_day_time(self._day_key) or self._value

    async def async_set_value(self, value: dt_time) -> None:
        self._value = value
        self._coordinator.set_day_time(self._day_key, value)
        self.async_write_ha_state()
