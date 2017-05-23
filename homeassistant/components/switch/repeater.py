"""
Support for switches which need repeated activations.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.repeater/
"""
import asyncio
import logging

import voluptuous as vol

from homeassistant.core import callback
from homeassistant.components.switch import (
    ENTITY_ID_FORMAT, SwitchDevice, PLATFORM_SCHEMA)
from homeassistant.const import (
    ATTR_FRIENDLY_NAME)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.restore_state import async_get_last_state
from homeassistant.helpers.script import Script

_LOGGER = logging.getLogger(__name__)
_VALID_STATES = [STATE_ON, STATE_OFF, 'true', 'false']

CONF_SWITCH = 'switch'
CONF_COUNT = 'count'
CONF_INTERVAL = 'interval'

DEFAULT_COUNT = 1
DEFAULT_INTERVAL = 0

SWITCH_SCHEMA = vol.Schema({
    vol.Required(CONF_SWITCH): cv.entity_id,
    vol.Optional(ATTR_FRIENDLY_NAME): cv.string,
    vol.Optional(CONF_COUNT, default=DEFAULT_COUNT): cv.positive_int,
    vol.Optional(CONF_INTERVAL, default=DEFAULT_INTERVAL): cv.positive_int,
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_SWITCHES): vol.Schema({cv.slug: SWITCH_SCHEMA}),
})


@asyncio.coroutine
# pylint: disable=unused-argument
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """Setup the Repeater switch."""
    switches = []

    for device, device_config in config[CONF_SWITCHES].items():
        switch = device_config[CONF_SWITCH]
        friendly_name = device_config.get(ATTR_FRIENDLY_NAME, device)
        count = device_config[CONF_COUNT]
        interval = device_config[CONF_INTERVAL]

        switches.append(
            SwitchRepeater(
                hass,
                device,
                switch,
                friendly_name,
                count,
                interval)
            )
    if not switches:
        _LOGGER.error("No switches added")
        return False

    async_add_devices(switches, True)
    return True


class SwitchRepeater(SwitchDevice):
    """Representation of a Repeater switch."""

    def __init__(self, hass, device_id, switch_id, friendly_name, count, interval):
        """Initialize the Template switch."""
        self.hass = hass
        self.entity_id = async_generate_entity_id(ENTITY_ID_FORMAT, device_id,
                                                  hass=hass)
        self._switch_id = switch_id
        self._name = friendly_name
        self._count = count
        self._interval = interval

    @asyncio.coroutine
    def async_added_to_hass(self):
        """Register callbacks."""
        state = yield from async_get_last_state(self.hass, self._switch_id)
        if state:
            self._state = state.state == STATE_ON

        @callback
        def repeater_switch_state_listener(entity, old_state, new_state):
            """Called when the target device changes state."""
            self.hass.async_add_job(self.async_update_ha_state(True))

        @callback
        def repeater_switch_startup(event):
            """Update repeater on startup."""
            async_track_state_change(
                self.hass, self._switch_id, repeater_switch_state_listener)

            self.hass.async_add_job(self.async_update_ha_state(True))

        self.hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_START, repeater_switch_startup)

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def available(self):
        """If switch is available."""
        return self._state is not None

    def turn_on(self, **kwargs):
        """Fire the on action."""
        def internal_turn_on():
            pass

    def turn_off(self, **kwargs):
        """Fire the off action."""
        self._off_script.run()

    @asyncio.coroutine
    def async_update(self):
        """Update the state from the template."""
        try:
            state = yield from async_get_last_state(self.hass, self._switch_id)

            if state in _VALID_STATES:
                self._state = state in ('true', STATE_ON)
            else:
                _LOGGER.error(
                    'Received invalid switch is_on state: %s. Expected: %s',
                    state, ', '.join(_VALID_STATES))
                self._state = None

        except TemplateError as ex:
            _LOGGER.error(ex)
            self._state = None
