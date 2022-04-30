"""Adds config flow for EDF Integration"""
from typing import Any, Dict, Optional
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_URL
from aiohttp import ClientSession
import re

from edf_api import EDFAuth
from .const import (
    CONF_JS_ERROR,
    CONF_CODE_VERIFIER,
    CONF_NONCE,
    CONF_STATE,
    CONF_ACCESS_TOKEN,
    CONF_REFRESH_TOKEN,
    CONF_TOKEN_EXPIRATION,
    CONF_INSEE_CODE,
    CONF_BUSINESS_PARTNER,
    CONF_PDL,
    DOMAIN,
    DEFAULT_NAME,
)


class EDFFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for EDF."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._auth = EDFAuth(ClientSession())
        self.data = {}

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        errors = {}

        if user_input is not None:
            error_str = user_input[CONF_JS_ERROR]
            code = re.findall("code=(.{8}-.{4}-.{4}-.{4}-.{12})", error_str)
            resp_state = re.findall("&state=(.*)&client_id", error_str)
            if len(code) != 1 or len(resp_state) != 1:
                errors["base"] = "unable to extract code and/or state"
            else:
                if resp_state[0] != self.data[CONF_STATE]:
                    errors["base"] = "invalid state"
                else:
                    (
                        access_token,
                        refresh_token,
                        expiration,
                    ) = await self._auth.get_token(
                        code=code[0],
                        code_verifier=self.data[CONF_CODE_VERIFIER],
                        nonce=self.data[CONF_NONCE],
                    )
                    if access_token is not None:
                        accord_co, bp_num, address = await self._auth.get_person_data(
                            access_token
                        )
                        valid, pdl = await self._auth.get_pdl(
                            access_token, accord_co, bp_num
                        )
                        insee = await self._auth.get_insee(address)
                        if not valid:
                            errors["base"] = "your linky is not compatible"
                        else:
                            await self.async_set_unique_id(pdl)
                            self._abort_if_unique_id_configured()
                            return self.async_create_entry(
                                title=DEFAULT_NAME,
                                data={
                                    CONF_ACCESS_TOKEN: access_token,
                                    CONF_REFRESH_TOKEN: refresh_token,
                                    CONF_TOKEN_EXPIRATION: expiration,
                                    CONF_PDL: pdl,
                                    CONF_BUSINESS_PARTNER: bp_num,
                                    CONF_INSEE_CODE: insee,
                                },
                            )
                    else:
                        errors["base"] = "unable to request the access token"

        link, code_verifier, state, nonce = self._auth.get_login_url()
        self.data[CONF_CODE_VERIFIER] = code_verifier
        self.data[CONF_STATE] = state
        self.data[CONF_NONCE] = nonce

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_JS_ERROR): str}),
            description_placeholders={CONF_URL: link},
            errors=errors,
        )
