"""EDFEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from datetime import datetime, timedelta
from .const import ATTRIBUTION, CONF_PDL, DATA_COST, DATA_ENERGY, DATA_HOURLY, DOMAIN, NAME, VERSION, STATE_CLASS_TOTAL
import logging

_LOGGER: logging.Logger = logging.getLogger(__package__)

class EDFEntity(CoordinatorEntity):
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.config_entry.data[CONF_PDL])},
            "name": NAME + " " + self.config_entry.data[CONF_PDL],
            "model": VERSION,
            "manufacturer": NAME,
        }

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": str(self.coordinator.data.get("id")),
            "integration": DOMAIN,
        }


class EDFDashEntity(EDFEntity):
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_native_value = 0

    @property
    def state_class(self):
        return STATE_CLASS_TOTAL

    @property
    def last_reset(self):
        return datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    def _update_data(self, energy=True):
        _LOGGER.info("update edf entitiy")
        data = self.coordinator.data[DATA_HOURLY]

        key = datetime.now() - timedelta(days=3)
        key = key.replace(second=0, microsecond=0)

        if key.minute >= 45:
            key = key.replace(minute=0) + timedelta(hours=1)
        else:
            key = key.replace(minute=(30 if key.minute > 15 and key.minute < 45 else 0))

        key_str = key.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        if key_str not in data:
            _LOGGER.warn("data not found")
            _LOGGER.error(key_str)
            _LOGGER.info(data)
            return

        d = data[key_str][DATA_ENERGY if energy else DATA_COST]
        _LOGGER.warn("data: " + str(d))

        if key.hour == 0 and key.minute == 0:
            self._attr_native_value = d
        else:
            self._attr_native_value += d
        self.async_write_ha_state()
