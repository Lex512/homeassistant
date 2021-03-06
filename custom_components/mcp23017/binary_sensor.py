"""
Support for binary sensor using MCP23017.
For more details about this platform, please refer to the README.md file.
"""
import logging

import voluptuous as vol

from homeassistant.components.binary_sensor import (
    BinarySensorDevice, PLATFORM_SCHEMA)
from homeassistant.const import DEVICE_DEFAULT_NAME
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_INVERT_LOGIC = 'invert_logic'
CONF_PINS = 'pins'
CONF_PULL_MODE = 'pull_mode'
CONF_I2C_ADDRESS = 'i2c_address'

DEFAULT_INVERT_LOGIC = False
DEFAULT_PULL_MODE = 'UP'
DEFAULT_I2C_ADDRESS= 0x20

_SENSORS_SCHEMA = vol.Schema({
    cv.positive_int: cv.string,
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_PINS): _SENSORS_SCHEMA,
    vol.Optional(CONF_INVERT_LOGIC, default=DEFAULT_INVERT_LOGIC): cv.boolean,
    vol.Optional(CONF_PULL_MODE, default=DEFAULT_PULL_MODE): cv.string,
    vol.Optional(CONF_I2C_ADDRESS, default=DEFAULT_I2C_ADDRESS): vol.Coerce(int),
})


async def async_setup_platform(hass, config, async_add_devices, 
                               discovery_info=None):
    """Set up the MCP23017 binary sensors."""
    import board
    import busio
    import adafruit_mcp230xx
    
    pull_mode = config.get(CONF_PULL_MODE)
    invert_logic = config.get(CONF_INVERT_LOGIC)
    i2c_address = config.get(CONF_I2C_ADDRESS)
        
    i2c = busio.I2C(board.SCL, board.SDA)
    mcp = adafruit_mcp230xx.MCP23017(i2c, address=i2c_address)
    
    binary_sensors = []
    pins = config.get(CONF_PINS)
    
    for pin_num, pin_name in pins.items():
        pin = mcp.get_pin(pin_num)
        binary_sensors.append(mcp23017BinarySensor(
            pin_name, pin, pull_mode, invert_logic))
            
    async_add_devices(binary_sensors, True)

class mcp23017BinarySensor(BinarySensorDevice):
    """Represent a binary sensor that uses MCP23017."""

    def __init__(self, name, pin, pull_mode, invert_logic):
        """Initialize the MCP23017 binary sensor."""
        import digitalio
        self._name = name or DEVICE_DEFAULT_NAME
        self._pin = pin
        self._pull_mode = pull_mode
        self._invert_logic = invert_logic
        self._state = None
        self._pin.direction = digitalio.Direction.INPUT
        self._pin.pull = digitalio.Pull.UP

    @property
    def should_poll(self):
        """No polling needed."""
        return True

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def is_on(self):
        """Return the state of the entity."""
        return self._state != self._invert_logic    
       
    async def async_update(self):
        """Update the GPIO state."""
        self._state = self._pin.value
