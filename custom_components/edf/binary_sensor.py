"""Binary sensor platform for EDF Integration"""
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass

from .const import CONF_INSEE_CODE, DOMAIN, ATTR_OUTAGE_DESC, ATTR_OUTAGE_END, ATTR_OUTAGE_GRID, ATTR_OUTAGE_HOMES, ATTR_OUTAGE_START, ATTR_OUTAGE_STATUS, ATTR_OUTAGE_TITLE, GRID_COORDINATOR
from .entity import EDFEntity

async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
) -> None:
    """Setup binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id][GRID_COORDINATOR]
    async_add_entities(
        [EDFBinarySensor(coordinator, entry)], True
    )


class EDFBinarySensor(EDFEntity, BinarySensorEntity):
    """EDF binary_sensor class."""
    def __init__(
        self,
        coordinator,
        config_entry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, config_entry)
        self._attrs = {}

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "_status"

    @property
    def name(self):
        """Return the name of the binary_sensor."""
        return "edf_" + self.config_entry.data[CONF_INSEE_CODE] + "_status"

    @property
    def device_class(self):
        """Return the class of this binary_sensor."""
        return BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return self.coordinator.data.outage

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        data = self.coordinator.data

        if data.outage:
            self._attrs.update(
                {
                    ATTR_OUTAGE_TITLE: data.title,
                    ATTR_OUTAGE_DESC: data.description,
                    ATTR_OUTAGE_GRID: data.grid_status,
                    ATTR_OUTAGE_HOMES: data.number_affected_homes,
                    ATTR_OUTAGE_START: data.outage_start_date,
                    ATTR_OUTAGE_END: data.outage_end_date,
                    ATTR_OUTAGE_STATUS: data.status
                }
            )
        else:
            self._attrs.update(
                {
                    ATTR_OUTAGE_TITLE: "",
                    ATTR_OUTAGE_DESC: "",
                    ATTR_OUTAGE_GRID: 0,
                    ATTR_OUTAGE_HOMES: 0,
                    ATTR_OUTAGE_START: "",
                    ATTR_OUTAGE_END: "",
                    ATTR_OUTAGE_STATUS: ""
                }
            )

        return self._attrs
