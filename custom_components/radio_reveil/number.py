"""Number entity for Radio Réveil — volume control."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_VOLUME, DEFAULT_VOLUME, VERSION
from .coordinator import RadioReveilCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: RadioReveilCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RadioReveilVolumeEntity(coordinator, entry)])


class RadioReveilVolumeEntity(NumberEntity):
    """Volume level for playback (0.0 → 1.0)."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:volume-high"
    _attr_native_min_value = 0.0
    _attr_native_max_value = 1.0
    _attr_native_step = 0.05
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator: RadioReveilCoordinator, entry: ConfigEntry) -> None:
        self._coordinator = coordinator
        self._entry = entry
        self._value = float(entry.data.get(CONF_VOLUME, DEFAULT_VOLUME))
        self._attr_unique_id = f"{entry.entry_id}_volume"
        self._attr_name = "Volume"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Radio Réveil",
            manufacturer="Communauté HA",
            model="Radio Réveil Hebdomadaire",
            sw_version=VERSION,
        )

    @property
    def native_value(self) -> float:
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        self._value = value
        updated_data = {**self._entry.data, CONF_VOLUME: value}
        self.hass.config_entries.async_update_entry(self._entry, data=updated_data)
        self.async_write_ha_state()
