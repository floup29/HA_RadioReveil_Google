"""Select entity for Radio Réveil — radio station, per instance."""
from __future__ import annotations
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, RADIOS, RADIO_LABELS, RADIO_URL_MAP, CONF_RADIO_URL, CONF_NAME, VERSION
from .coordinator import RadioReveilCoordinator


async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator: RadioReveilCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RadioReveilSelectEntity(coordinator, entry)])


def _device(entry):
    name = entry.data.get(CONF_NAME, entry.title)
    return DeviceInfo(identifiers={(DOMAIN, entry.entry_id)}, name=f"Radio Réveil — {name}",
                      manufacturer="Communauté HA", model="Radio Réveil Hebdomadaire", sw_version=VERSION)


class RadioReveilSelectEntity(SelectEntity):
    _attr_has_entity_name = True
    _attr_icon = "mdi:radio"
    _attr_options = RADIO_LABELS

    def __init__(self, coordinator, entry: ConfigEntry):
        self._coordinator = coordinator
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_radio"
        self._attr_name = "Station radio"
        self._attr_device_info = _device(entry)
        current_url = entry.data.get(CONF_RADIO_URL, RADIOS[0]["url"])
        label_map = {r["url"]: r["label"] for r in RADIOS}
        self._current = label_map.get(current_url, RADIO_LABELS[0])

    @property
    def current_option(self): return self._current

    async def async_select_option(self, option: str):
        self._current = option
        new_url = RADIO_URL_MAP.get(option, option)
        updated = {**self._entry.data, CONF_RADIO_URL: new_url}
        self.hass.config_entries.async_update_entry(self._entry, data=updated)
        self.async_write_ha_state()
