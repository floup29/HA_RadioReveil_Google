"""Coordinator for Radio Réveil — handles scheduling and playback."""
from __future__ import annotations

import logging
from datetime import datetime, time as dt_time

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    DAYS_HA,
    CONF_MEDIA_PLAYER,
    CONF_RADIO_URL,
    CONF_VOLUME,
)

_LOGGER = logging.getLogger(__name__)


class RadioReveilCoordinator(DataUpdateCoordinator):
    """Manages alarm scheduling and triggers playback."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN)
        self.entry = entry
        self._unsub_listeners: list = []
        self._alarm_times: dict[str, dt_time | None] = {}  # day_key → time
        self._day_enabled: dict[str, bool] = {}            # day_key → bool
        self._global_enabled: bool = True

    # ------------------------------------------------------------------
    # Public API used by entity platforms
    # ------------------------------------------------------------------

    def set_global(self, enabled: bool) -> None:
        self._global_enabled = enabled
        self._reschedule()

    def set_day_enabled(self, day_key: str, enabled: bool) -> None:
        self._day_enabled[day_key] = enabled
        self._reschedule()

    def set_day_time(self, day_key: str, alarm_time: dt_time | None) -> None:
        self._alarm_times[day_key] = alarm_time
        self._reschedule()

    def is_global_enabled(self) -> bool:
        return self._global_enabled

    def is_day_enabled(self, day_key: str) -> bool:
        return self._day_enabled.get(day_key, False)

    def get_day_time(self, day_key: str) -> dt_time | None:
        return self._alarm_times.get(day_key)

    # ------------------------------------------------------------------
    # Scheduling internals
    # ------------------------------------------------------------------

    def _reschedule(self) -> None:
        """Cancel existing listeners and register new time triggers."""
        for unsub in self._unsub_listeners:
            unsub()
        self._unsub_listeners.clear()

        if not self._global_enabled:
            return

        for day_key, alarm_time in self._alarm_times.items():
            if not self._day_enabled.get(day_key):
                continue
            if alarm_time is None:
                continue

            # Capture loop variables
            _day = day_key
            _time = alarm_time

            @callback
            def _fire(now, _d=_day, _t=_time):
                # Verify weekday matches
                ha_day = DAYS_HA[list(self._alarm_times.keys()).index(_d)]
                weekday_map = {"mon": 0, "tue": 1, "wed": 2, "thu": 3,
                               "fri": 4, "sat": 5, "sun": 6}
                if now.weekday() == weekday_map[ha_day]:
                    self.hass.async_create_task(self._play_radio())

            unsub = async_track_time_change(
                self.hass,
                _fire,
                hour=alarm_time.hour,
                minute=alarm_time.minute,
                second=0,
            )
            self._unsub_listeners.append(unsub)

    async def _play_radio(self) -> None:
        """Call HA services to play the radio stream."""
        data = self.entry.data
        entity_id = data.get(CONF_MEDIA_PLAYER, "media_player.salon")
        radio_url = data.get(CONF_RADIO_URL, "")
        volume = float(data.get(CONF_VOLUME, 0.5))

        _LOGGER.info("Radio Réveil → %s @ vol %.2f : %s", entity_id, volume, radio_url)

        await self.hass.services.async_call(
            "media_player", "volume_set",
            {"entity_id": entity_id, "volume_level": volume},
        )
        await self.hass.services.async_call(
            "media_player", "play_media",
            {"entity_id": entity_id,
             "media_content_id": radio_url,
             "media_content_type": "music"},
        )

    async def async_shutdown(self) -> None:
        for unsub in self._unsub_listeners:
            unsub()
        self._unsub_listeners.clear()
