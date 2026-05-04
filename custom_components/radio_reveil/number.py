"""Number entity for Radio Réveil — volume, per instance."""
from __future__ import annotations
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, CONF_VOLUME, CONF_NAME, DEFAULT_VOLUME, VERSION
from .coordinator import RadioReveilCoordinator


async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator: RadioReveilCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RadioReveilVolumeEntity(coordinator, entry)])


def _device(entry):
    name = entry.data.get(CONF_NAME, entry.title)
    return DeviceInfo(identifiers={(DOMAIN, entry.entry_id)}, name=f"Radio Réveil — {name}",
                      manufacturer="Communauté HA", model="Radio Réveil Hebdomadaire", sw_version=VERSION)


class RadioReveilVolumeEntity(NumberEntity):
    _attr_has_entity_name = True
    _attr_icon = "mdi:volume-high"
    _attr_native_min_value = 0.0
    _attr_native_max_value = 1.0
    _attr_native_step = 0.05
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator, entry: ConfigEntry):
        self._coordinator = coordinator
        self._entry = entry
        self._value = float(entry.data.get(CONF_VOLUME, DEFAULT_VOLUME))
        self._attr_unique_id = f"{entry.entry_id}_volume"
        self._attr_name = "Volume"
        self._attr_device_info = _device(entry)

    @property
    def native_value(self): return self._value

    async def async_set_native_value(self, value: float):
        self._value = value
        self.hass.config_entries.async_update_entry(self._entry, data={**self._entry.data, CONF_VOLUME: value})
        self.async_write_ha_state()
