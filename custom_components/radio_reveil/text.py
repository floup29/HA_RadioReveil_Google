"""Text entity for Radio Réveil — Google Home entity ID."""
from __future__ import annotations

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_MEDIA_PLAYER, VERSION
from .coordinator import RadioReveilCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: RadioReveilCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RadioReveilMediaPlayerText(coordinator, entry)])


class RadioReveilMediaPlayerText(TextEntity):
    """Text entity storing the target media_player entity ID."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:google-home"
    _attr_native_min = 1
    _attr_native_max = 255

    def __init__(self, coordinator: RadioReveilCoordinator, entry: ConfigEntry) -> None:
        self._coordinator = coordinator
        self._entry = entry
        self._value = entry.data.get(CONF_MEDIA_PLAYER, "media_player.salon")
        self._attr_unique_id = f"{entry.entry_id}_media_player"
        self._attr_name = "Google Home / Chromecast"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Radio Réveil",
            manufacturer="Communauté HA",
            model="Radio Réveil Hebdomadaire",
            sw_version=VERSION,
        )

    @property
    def native_value(self) -> str:
        return self._value

    async def async_set_value(self, value: str) -> None:
        self._value = value
        updated_data = {**self._entry.data, CONF_MEDIA_PLAYER: value}
        self.hass.config_entries.async_update_entry(self._entry, data=updated_data)
        self.async_write_ha_state()
