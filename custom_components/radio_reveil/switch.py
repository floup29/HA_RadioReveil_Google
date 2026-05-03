"""Switch entities for Radio Réveil."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, DAYS_FR, DAYS_FR_FULL, VERSION
from .coordinator import RadioReveilCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: RadioReveilCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [RadioReveilGlobalSwitch(coordinator, entry)]
    for i, day_key in enumerate(DAYS_FR):
        entities.append(RadioReveilDaySwitch(coordinator, entry, day_key, DAYS_FR_FULL[i]))
    async_add_entities(entities)


def _device_info(entry: ConfigEntry) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name="Radio Réveil",
        manufacturer="Communauté HA",
        model="Radio Réveil Hebdomadaire",
        sw_version=VERSION,
    )


class RadioReveilGlobalSwitch(SwitchEntity):
    """Master on/off switch."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:alarm"

    def __init__(self, coordinator: RadioReveilCoordinator, entry: ConfigEntry) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_global"
        self._attr_name = "Réveil actif"
        self._attr_device_info = _device_info(entry)

    @property
    def is_on(self) -> bool:
        return self._coordinator.is_global_enabled()

    async def async_turn_on(self, **kwargs) -> None:
        self._coordinator.set_global(True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._coordinator.set_global(False)
        self.async_write_ha_state()


class RadioReveilDaySwitch(SwitchEntity):
    """Per-day enable/disable switch."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:calendar-today"

    def __init__(
        self,
        coordinator: RadioReveilCoordinator,
        entry: ConfigEntry,
        day_key: str,
        day_label: str,
    ) -> None:
        self._coordinator = coordinator
        self._day_key = day_key
        self._attr_unique_id = f"{entry.entry_id}_{day_key}"
        self._attr_name = day_label
        self._attr_device_info = _device_info(entry)

    @property
    def is_on(self) -> bool:
        return self._coordinator.is_day_enabled(self._day_key)

    async def async_turn_on(self, **kwargs) -> None:
        self._coordinator.set_day_enabled(self._day_key, True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._coordinator.set_day_enabled(self._day_key, False)
        self.async_write_ha_state()
