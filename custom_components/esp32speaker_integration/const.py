"""Constants for esp32speaker_integration."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "esp32speaker_integration"
CONF_DEVICE_ID = "device_id"
CONF_POWER_ENTITY = "power_entity"
CONF_TOPIC_PREFIX = "topic_prefix"
CONF_ENTITIES = "entities"

ENTITY_SUFFIXES = {
	"power": "power",
	"volume": "volume",
	"station": "station",
	"title": "title",
	"radio": "station_select",
	"sd": "sd_select",
	"announcing": "announcing",
}
