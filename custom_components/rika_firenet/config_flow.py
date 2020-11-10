import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import (CONF_DEFAULT_TEMPERATURE,CONF_PASSWORD, CONF_USERNAME,DOMAIN, PLATFORMS)
from .core import RikaFirenetConnector


class RikaFirenetFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        # Uncomment the next 2 lines if only a single instance of the integration is allowed:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            valid = await self._test_credentials(
                user_input[CONF_USERNAME], user_input[CONF_PASSWORD], user_input[CONF_DEFAULT_TEMPERATURE]
            )
            if valid:
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME], data=user_input
                )
            else:
                self._errors["base"] = "auth"

            return await self._show_config_form(user_input)

        return await self._show_config_form(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return RikaFirenetOptionsFlowHandler(config_entry)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit data."""
        schema_properties = {
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Required(CONF_DEFAULT_TEMPERATURE, default=21): int
        }

        # schema_properties.update({
        #     vol.Required(x, default=self.options.get(x, True)): bool
        #     for x in sorted(PLATFORMS)
        # })

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(schema_properties),
            errors=self._errors,
        )

    async def _test_credentials(self, username, password, default_temperature):
        """Return true if credentials is valid."""
        try:
            connector = RikaFirenetConnector(
                None, username, password, default_temperature)
            connector.setup()
            return True
        except Exception:  # pylint: disable=broad-except
            pass
        return False


class RikaFirenetOptionsFlowHandler(config_entries.OptionsFlow):

    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        schema_properties = {
            # vol.Required(CONF_USERNAME, default=self.options.get(CONF_USERNAME)): str,
            # vol.Required(CONF_PASSWORD, default=self.options.get(CONF_PASSWORD)): str,
            # vol.Required(CONF_DEFAULT_TEMPERATURE, default=self.options.get(CONF_DEFAULT_TEMPERATURE)): int
        }

        schema_properties.update({
            vol.Required(x, default=self.options.get(x, True)): bool
            for x in sorted(PLATFORMS)
        })

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(schema_properties),
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get(CONF_USERNAME), data=self.options
        )
