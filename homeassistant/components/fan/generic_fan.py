"""
Generic fan platform, a-la generic thermostat.

For more details about this platform, please refer to the documentation
https://home-assistant.io/components/fan.generic_fan/
"""
import asyncio
import logging
import voluptuous as vol

from homeassistant.components import switch
from homeassistant.components.fan import (SPEED_LOW, SPEED_MEDIUM, SPEED_HIGH,
                                          FanEntity, SUPPORT_SET_SPEED,
                                          SUPPORT_OSCILLATE, SUPPORT_DIRECTION,
                                          PLATFORM_SCHEMA)
from homeassistant.const import STATE_OFF, CONF_DEVICES, CONF_NAME
import homeassistant.helpers.config_validation as cv

CONF_POWER_SWITCH = "power"
CONF_SET_SPEED = "set_speed"
CONF_CHANGE_SPEED = "change_speed"
CONF_OSCILLATION_SWITCH = "oscillation"
CONF_SET_DIRECTION = "set_direction"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_POWER_SWITCH): cv.entity_id,
    vol.Optional(CONF_OSCILLATION_SWITCH, default=None): cv.entity_id,
})

# pylint: disable=unused-argument
@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """Set up the generic fan platform."""
    async_add_devices([GenericFan(
        config.get(CONF_NAME),
        config.get(CONF_POWER_SWITCH),
        config.get(CONF_OSCILLATION_SWITCH)
        )
    ])


class GenericFan(FanEntity):
    """A generic fan component."""

    def __init__(self, name: str, power_switch: str,
                 oscillation_switch: str) -> None:
        """Initialize the generic fan."""
        self._name = name
        self._power_switch = power_switch
        self._oscillation_switch = oscillation_switch

    @property
    def should_poll(self):
        """No polling needed for a generic fan."""
        return False

    @property
    def assumed_state(self):
        """Return true, since state is not maintained by a sensor."""
        return False

    @property
    def is_on(self):
        """Return true if device is on."""
        return switch.is_on(self.hass, self._power_switch)

    @property
    def name(self) -> str:
        """Get entity name."""
        return self._name

    @property
    def speed_list(self) -> list:
        """Get the list of available speeds."""
        return [1, 2, 3]

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        if self._oscillation_switch:
            return SUPPORT_OSCILLATE

    @property
    def speed(self):
        """Return the current speed."""
        if not self.is_on:
            return 0
        else:
            raise NotImplementedError()

    @property
    def oscillating(self):
        """Return the oscillation state."""
        if not self._oscillation_switch:
            return False
        else:
            raise NotImplementedError()

    @asyncio.coroutine
    def async_turn_on(self, speed: str=None) -> None:
        """Turn on the entity.

        This method is a coroutine.
        """
        switch.async_turn_on(self.hass, self._power_switch)

        if speed:
            yield from self.async_set_speed(speed)

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
        raise NotImplementedError()

    @asyncio.coroutine
    def async_oscillate(self, oscillating: bool) -> None:
        """Set oscillation.

        This method is a coroutine.
        """
        if not self._oscillation_switch:
            raise NotImplementedError()

        raise NotImplementedError()
