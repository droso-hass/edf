"""Sensor platform for EDF Integration"""
from .const import DATA_COORDINATOR, DOMAIN, CONF_PDL
from .entity import EDFDashEntity

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_MONETARY, DEVICE_CLASS_ENERGY, CURRENCY_EURO
from homeassistant.core import callback

async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
) -> None:
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    async_add_entities(
        [EDFElecSensor(coordinator, entry), EDFElecCostSensor(coordinator, entry)], True
    )


class EDFElecSensor(EDFDashEntity, SensorEntity):
    """EDF Timestamp Sensor class."""
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
    
    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "_elec_energy"

    @property
    def name(self):
        """Return the name of the sensor."""
        return "edf_" + self.config_entry.data[CONF_PDL] + "_elec_energy"
        
    @property
    def device_class(self):
        """Return the class of this sensor."""
        return DEVICE_CLASS_ENERGY

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_data(energy=True)

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return ENERGY_KILO_WATT_HOUR

class EDFElecCostSensor(EDFDashEntity, SensorEntity):
    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "_elec_cost"

    @property
    def name(self):
        """Return the name of the sensor."""
        return "edf_" + self.config_entry.data[CONF_PDL] + "_elec_cost"
        
    @property
    def device_class(self):
        """Return the class of this sensor."""
        return DEVICE_CLASS_MONETARY

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return CURRENCY_EURO

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_data(energy=False)