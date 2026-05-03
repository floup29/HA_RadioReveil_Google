"""Select entity for Radio Réveil — radio station picker."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, RADIOS, RADIO_LABELS, RADIO_URL_MAP, CONF_RADIO_URL, VERSION
from .coordinator import RadioReveilCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: RadioReveilCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RadioReveilSelectEntity(coordinator, entry)])


class RadioReveilSelectEntity(SelectEntity):
    """Select the radio station."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:radio"
    _attr_options = RADIO_LABELS

    def __init__(self, coordinator: RadioReveilCoordinator, entry: ConfigEntry) -> None:
        self._coordinator = coordinator
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_radio"
        self._attr_name = "Station radio"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Radio Réveil",
            manufacturer="Communauté HA",
            model="Radio Réveil Hebdomadaire",
            sw_version=VERSION,
        )
        # Resolve current URL → label for display
        current_url = entry.data.get(CONF_RADIO_URL, RADIOS[0]["url"])
        label_map = {r["url"]: r["label"] for r in RADIOS}
        self._current = label_map.get(current_url, RADIO_LABELS[0])

    @property
    def current_option(self) -> str:
        return self._current

    async def async_select_option(self, option: str) -> None:
        self._current = option
        new_url = RADIO_URL_MAP.get(option, option)
        # Persist to config entry data
        updated_data = {**self._entry.data, CONF_RADIO_URL: new_url}
        self.hass.config_entries.async_update_entry(self._entry, data=updated_data)
        self.async_write_ha_state()
