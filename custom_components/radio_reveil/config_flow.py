"""Config flow for Radio Réveil."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_MEDIA_PLAYER,
    CONF_RADIO_URL,
    CONF_VOLUME,
    RADIO_LABELS,
    RADIOS,
    DEFAULT_VOLUME,
)


class RadioReveilConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the initial setup config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            # Resolve label → URL if user picked from list
            label = user_input.get(CONF_RADIO_URL, RADIOS[0]["label"])
            url_map = {r["label"]: r["url"] for r in RADIOS}
            user_input[CONF_RADIO_URL] = url_map.get(label, label)

            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="Radio Réveil", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_MEDIA_PLAYER, default="media_player.salon"): selector.selector({
                "entity": {"domain": "media_player"}
            }),
            vol.Required(CONF_RADIO_URL, default=RADIOS[0]["label"]): selector.selector({
                "select": {
                    "options": RADIO_LABELS,
                    "custom_value": True,
                    "mode": "dropdown",
                }
            }),
            vol.Required(CONF_VOLUME, default=DEFAULT_VOLUME): selector.selector({
                "number": {"min": 0.0, "max": 1.0, "step": 0.05, "mode": "slider"}
            }),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
            description_placeholders={"doc_url": "https://github.com/votre-repo/radio-reveil"},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return RadioReveilOptionsFlow(config_entry)


class RadioReveilOptionsFlow(config_entries.OptionsFlow):
    """Allow reconfiguring without reinstalling."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        errors = {}
        current = self.config_entry.data

        if user_input is not None:
            label = user_input.get(CONF_RADIO_URL, RADIOS[0]["label"])
            url_map = {r["label"]: r["url"] for r in RADIOS}
            user_input[CONF_RADIO_URL] = url_map.get(label, label)
            return self.async_create_entry(title="Radio Réveil", data=user_input)

        # Find current radio label from URL
        current_url = current.get(CONF_RADIO_URL, RADIOS[0]["url"])
        label_map = {r["url"]: r["label"] for r in RADIOS}
        current_label = label_map.get(current_url, current_url)

        schema = vol.Schema({
            vol.Required(CONF_MEDIA_PLAYER, default=current.get(CONF_MEDIA_PLAYER, "media_player.salon")): selector.selector({
                "entity": {"domain": "media_player"}
            }),
            vol.Required(CONF_RADIO_URL, default=current_label): selector.selector({
                "select": {
                    "options": RADIO_LABELS,
                    "custom_value": True,
                    "mode": "dropdown",
                }
            }),
            vol.Required(CONF_VOLUME, default=current.get(CONF_VOLUME, DEFAULT_VOLUME)): selector.selector({
                "number": {"min": 0.0, "max": 1.0, "step": 0.05, "mode": "slider"}
            }),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
        )
