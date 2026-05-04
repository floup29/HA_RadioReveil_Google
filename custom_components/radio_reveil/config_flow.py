"""Config flow for Radio Réveil — supports multiple instances."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_MEDIA_PLAYER,
    CONF_RADIO_URL,
    CONF_VOLUME,
    RADIO_LABELS,
    RADIOS,
    DEFAULT_VOLUME,
)


def _base_schema(defaults: dict) -> vol.Schema:
    return vol.Schema({
        vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, "Réveil")): selector.selector({
            "text": {}
        }),
        vol.Required(CONF_MEDIA_PLAYER, default=defaults.get(CONF_MEDIA_PLAYER, "media_player.salon")): selector.selector({
            "entity": {"domain": "media_player"}
        }),
        vol.Required(CONF_RADIO_URL, default=defaults.get(CONF_RADIO_URL, RADIOS[0]["label"])): selector.selector({
            "select": {
                "options": RADIO_LABELS,
                "custom_value": True,
                "mode": "dropdown",
            }
        }),
        vol.Required(CONF_VOLUME, default=defaults.get(CONF_VOLUME, DEFAULT_VOLUME)): selector.selector({
            "number": {"min": 0.0, "max": 1.0, "step": 0.05, "mode": "slider"}
        }),
    })


def _resolve_url(user_input: dict) -> dict:
    label = user_input.get(CONF_RADIO_URL, "")
    url_map = {r["label"]: r["url"] for r in RADIOS}
    user_input[CONF_RADIO_URL] = url_map.get(label, label)
    return user_input


class RadioReveilConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the initial setup — one flow per alarm instance."""

    VERSION = 1

    # No unique_id lock → multiple instances allowed
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            user_input = _resolve_url(user_input)
            title = user_input.get(CONF_NAME, "Réveil")
            return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_base_schema({}),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return RadioReveilOptionsFlow(config_entry)


class RadioReveilOptionsFlow(config_entries.OptionsFlow):
    """Allow reconfiguring any alarm instance."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        current = {**self.config_entry.data}
        current_url = current.get(CONF_RADIO_URL, RADIOS[0]["url"])
        label_map = {r["url"]: r["label"] for r in RADIOS}
        current[CONF_RADIO_URL] = label_map.get(current_url, current_url)

        if user_input is not None:
            user_input = _resolve_url(user_input)
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                title=user_input.get(CONF_NAME, self.config_entry.title),
                data={**self.config_entry.data, **user_input},
            )
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=_base_schema(current),
        )
