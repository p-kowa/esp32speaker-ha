"""Constants for esp32speaker_integration."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "esp32speaker_integration"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"

CONF_UPDATE_INTERVAL_HOURS = "update_interval_hours"

DEFAULT_UPDATE_INTERVAL_HOURS = 1.0
