"""Text entity for Radio Réveil — media player entity ID, per instance."""
from __future__ import annotations
from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, CONF_MEDIA_PLAYER, CONF_NAME, VERSION
from .coordinator import RadioReveilCoordinator


async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator: RadioReveilCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RadioReveilMediaPlayerText(coordinator, entry)])


def _device(entry):
    name = entry.data.get(CONF_NAME, entry.title)
    return DeviceInfo(identifiers={(DOMAIN, entry.entry_id)}, name=f"Radio Réveil — {name}",
                      manufacturer="Communauté HA", model="Radio Réveil Hebdomadaire", sw_version=VERSION)


class RadioReveilMediaPlayerText(TextEntity):
    _attr_has_entity_name = True
    _attr_icon = "mdi:google-home"
    _attr_native_min = 1
    _attr_native_max = 255

    def __init__(self, coordinator, entry: ConfigEntry):
        self._coordinator = coordinator
        self._entry = entry
        self._value = entry.data.get(CONF_MEDIA_PLAYER, "media_player.salon")
        self._attr_unique_id = f"{entry.entry_id}_media_player"
        self._attr_name = "Google Home / Chromecast"
        self._attr_device_info = _device(entry)

    @property
    def native_value(self): return self._value

    async def async_set_value(self, value: str):
        self._value = value
        self.hass.config_entries.async_update_entry(self._entry, data={**self._entry.data, CONF_MEDIA_PLAYER: value})
        self.async_write_ha_state()
