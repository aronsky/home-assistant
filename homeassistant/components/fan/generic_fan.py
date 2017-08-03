"""
Generic fan platform, a-la generic thermostat.

For more details about this platform, please refer to the documentation
https://home-assistant.io/components/fan.generic_fan/
"""
import asyncio
import logging
import voluptuous as vol

from homeassistant.core import callback
from homeassistant.components import switch
from homeassistant.components.fan import (SPEED_LOW, SPEED_MEDIUM, SPEED_HIGH,
                                          FanEntity, SUPPORT_SET_SPEED,
                                          SUPPORT_OSCILLATE, SUPPORT_DIRECTION,
                                          PLATFORM_SCHEMA)
from homeassistant.const import (STATE_UNKNOWN, STATE_OFF, STATE_ON,
                                 CONF_DEVICES, CONF_NAME,
                                 EVENT_HOMEASSISTANT_START)
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.restore_state import async_get_last_state
from homeassistant.helpers.script import Script

import homeassistant.helpers.config_validation as cv

CONF_POWER_SWITCH = "power"
CONF_SET_SPEED = "set_speed"
CONF_CHANGE_SPEED = "change_speed"
CONF_OSCILLATION_SWITCH = "oscillation"
CONF_SET_DIRECTION = "set_direction"
CONF_MEMORY = "memory"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_POWER_SWITCH): cv.entity_id,
    vol.Optional(CONF_OSCILLATION_SWITCH, default=None): cv.entity_id,
    vol.Optional(CONF_SET_SPEED, default=None): cv.SCRIPT_SCHEMA,
    vol.Optional(CONF_SET_DIRECTION, default=None): cv.SCRIPT_SCHEMA,
    vol.Optional(CONF_MEMORY, default=False): cv.boolean,
})

# pylint: disable=unused-argument
@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """Set up the generic fan platform."""
    async_add_devices([GenericFan(
        hass,
        config.get(CONF_NAME),
        config.get(CONF_POWER_SWITCH),
        config.get(CONF_OSCILLATION_SWITCH),
        config.get(CONF_SET_SPEED),
        config.get(CONF_SET_DIRECTION),
        config.get(CONF_MEMORY)
        )
    ], True)


class GenericFan(FanEntity):
    """A generic fan component."""

    def __init__(self, hass, name: str, power_switch: str,
                 oscillation_switch: str, set_speed_script: str,
                 set_direction_script: str, memory: bool) -> None:
        """Initialize the generic fan."""
        self._name = name
        
        self._power_switch = power_switch
        self._oscillation_switch = oscillation_switch
        self._set_speed_script = Script(hass, set_speed_script) \
            if set_speed_script else None
        self._set_direction_script = Script(hass, set_direction_script) \
            if set_direction_script else None
        self._memory = memory

        self._supported_features = 0
        if self._oscillation_switch:
            self._supported_features |= SUPPORT_OSCILLATE
        if self._set_speed_script:
            self._supported_features |= SUPPORT_SET_SPEED
        if self._set_direction_script:
            self._supported_features |= SUPPORT_DIRECTION

        self._state = STATE_UNKNOWN
        self._speed = STATE_OFF
        self._oscillating = False

    @property
    def should_poll(self):
        """No polling needed for a generic fan."""
        return False

    @property
    def assumed_state(self):
        """Return true, since state is not maintained by a sensor."""
        return True

    @property
    def is_on(self):
        """Return true if the fan is on."""
        return self._state == STATE_ON

    @property
    def name(self) -> str:
        """Get entity name."""
        return self._name

    @property
    def speed_list(self) -> list:
        """Return the list of available speeds."""
        if not self._set_speed_script:
            return None

        return [STATE_OFF, SPEED_LOW, SPEED_MEDIUM, SPEED_HIGH]

    @property
    def supported_features(self) -> int:
        """Return the supported features bitmask."""
        return self._supported_features

    @property
    def speed(self) -> str:
        """Return the current speed of the fan."""
        if not self._set_speed_script:
            return None
        return self._speed

    @property
    def oscillating(self) -> bool:
        """Return the oscillation state of the fan."""
        if not self.is_on or not self._oscillation_switch:
            return None

        return self._oscillating
    
    @property
    def current_direction(self) -> str:
        """Return the current direction of the fan."""
        if not self._set_direction_script:
            return None

        raise NotImplementedError()

    @asyncio.coroutine
    def async_added_to_hass(self):
        """Register callbacks."""
        state = yield from async_get_last_state(self.hass, self.entity_id)
        if state:
            self._state = state.state == STATE_ON

        @callback
        def switch_state_listener(entity, old_state, new_state):
            """Handle switches state changes."""
            self.hass.async_add_job(self.async_update_ha_state(True))

        @callback
        def generic_fan_startup(event):
            """Update fan on startup."""
            async_track_state_change(
                self.hass, self._power_switch, switch_state_listener)

            if self._oscillation_switch:
                async_track_state_change(
                    self.hass, self._oscillation_switch, switch_state_listener)

            self.hass.async_add_job(self.async_update_ha_state(True))

        self.hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_START, generic_fan_startup)

    @asyncio.coroutine
    def async_turn_on(self, speed: str=None) -> None:
        """Turn on the entity.

        This method is a coroutine.
        """
        switch.turn_on(self.hass, self._power_switch)

        if speed:
            yield from self.async_set_speed(speed)

        if not self._memory and self.oscillating:
            yield from self.oscillate(self._oscillating)

    @asyncio.coroutine
    def async_turn_off(self) -> None:
        """Turn off the entity.

        This method is a coroutine.
        """
        switch.async_turn_off(self.hass, self._power_switch)

    @asyncio.coroutine
    def async_set_speed(self, speed: str) -> None:
        """Set the speed of the fan.

        This method is a coroutine.
        """
        if not self._set_speed_script:
            raise NotImplementedError()

        raise NotImplementedError()

    @asyncio.coroutine
    def async_oscillate(self, oscillating: bool) -> None:
        """Set oscillation.

        This method is a coroutine.
        """
        if not self._oscillation_switch:
            raise NotImplementedError()

        if oscillating:
            switch.async_turn_on(self.hass, self._oscillation_switch)
        else:
            switch.async_turn_off(self.hass, self._oscillation_switch)

    @asyncio.coroutine
    def async_update(self) -> None:
        """Update the state."""
        if switch.is_on(self.hass, self._power_switch):
            self._state = STATE_ON
        else:
            self._state = STATE_OFF

        if self._oscillation_switch:
            if switch.is_on(self.hass, self._oscillation_switch):
                self._oscillating = True
            else:
                self._oscillating = False
