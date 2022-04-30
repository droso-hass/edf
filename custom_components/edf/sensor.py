"""Sensor platform for EDF Integration"""
from .const import *
from .entity import EDFEntity
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    ENERGY_KILO_WATT_HOUR,
    DEVICE_CLASS_MONETARY,
    DEVICE_CLASS_ENERGY,
    CURRENCY_EURO,
)
from homeassistant.core import callback

import logging

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
) -> None:
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    e = [
        EDFDashSensor(coordinator, entry, True, True),
        EDFDashSensor(coordinator, entry, True, False),
        EDFDashSensor(coordinator, entry, False, True),
        EDFDashSensor(coordinator, entry, False, False),
    ]
    if ENABLE_LINKYCARD:
        e.append(EDFLinkyCardSensor(coordinator, entry))
    async_add_entities(e, True)


class EDFDashSensor(EDFEntity, SensorEntity):
    """EDF Timestamp Sensor class."""

    def __init__(self, coordinator, config_entry, energy=True, month=False):
        super().__init__(coordinator, config_entry)

        self._energy = energy
        self._month = month
        self._attr_extra_state_attributes = {ATTR_UPDATE_DATE: None}

        suffix = (
            "_elec_" + ("energy" if energy else "cost") + ("_month" if month else "")
        )
        self._attr_unique_id = self.config_entry.entry_id + suffix
        self._attr_name = "edf_" + self.config_entry.data[CONF_PDL] + suffix
        self._attr_state_class = STATE_CLASS_TOTAL

        if energy:
            self._attr_device_class = DEVICE_CLASS_ENERGY
            self._attr_unit_of_measurement = ENERGY_KILO_WATT_HOUR
        else:
            self._attr_device_class = DEVICE_CLASS_MONETARY
            self._attr_unit_of_measurement = CURRENCY_EURO

        if self._attr_native_value is None:
            self._attr_native_value = 0

    @property
    def last_reset(self):
        if self._month:
            return datetime.now().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
        else:
            return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    @callback
    def _handle_coordinator_update(self) -> None:
        data = self.coordinator.data[DATA_HOURLY]

        key = datetime.now() - timedelta(days=DAY_OFFSET)
        key = key.replace(second=0, microsecond=0)
        if key.minute >= 45:
            key = key.replace(minute=0) + timedelta(hours=1)
        else:
            key = key.replace(minute=(30 if key.minute > 15 and key.minute < 45 else 0))
        key_str = key.strftime("%Y-%m-%dT%H:%M:%SZ")

        if key_str not in data:
            _LOGGER.warn("data not found for key:" + key_str)
            _LOGGER.debug(data)
            return

        d = data[key_str][DATA_ENERGY if self._energy else DATA_COST]

        if (
            (not self._month or (self._month and key.day == 1))
            and key.hour == 0
            and key.minute == 0
        ):
            self._attr_native_value = d
        else:
            self._attr_native_value += d

        self._attr_extra_state_attributes[ATTR_UPDATE_DATE] = key

        self.async_write_ha_state()


class EDFLinkyCardSensor(EDFEntity, SensorEntity):
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)

        self._attr_unique_id = self.config_entry.entry_id + "_linky_card"
        self._attr_name = "edf_" + self.config_entry.data[CONF_PDL] + "_linky_card"
        self._attr_device_class = DEVICE_CLASS_ENERGY
        self._attr_icon = "mdi:home-lightning-bolt"

        if self._attr_native_value is None:
            self._attr_native_value = 0

        self._attr_extra_state_attributes = {
            ATTR_LINKYCARD_DAILY_COST: 0,
            ATTR_LINKYCARD_YESTERDAY_HP: 0,
            ATTR_LINKYCARD_YESTERDAY_HC: 0,
            ATTR_LINKYCARD_YESTERDAY_HPHC: 0,
            ATTR_LINKYCARD_YESTERDAY: 0,
            ATTR_LINKYCARD_YESTERDAY_EVOLUTION: 0,
            ATTR_LINKYCARD_YESTERDAY_LAST_YEAR: 0,
            ATTR_LINKYCARD_CURRENT_WEEK: 0,
            ATTR_LINKYCARD_CURRENT_WEEK_LAST_YEAR: 0,
            ATTR_LINKYCARD_CURRENT_WEEK_EVOLUTION: 0,
            ATTR_LINKYCARD_UNIT: ENERGY_KILO_WATT_HOUR,
            ATTR_LINKYCARD_TYPE_COMPTEUR: "consommation",
            ATTR_LINKYCARD_PERCENT_HP: 100,
            ATTR_LINKYCARD_ERROR: False,
            ATTR_LINKYCARD_MONTHLY_EVOLUTION: 0,
            ATTR_LINKYCARD_LAST_MONTH: 0,
            ATTR_LINKYCARD_LAST_MONTH_LAST_YEAR: 0,
            ATTR_LINKYCARD_CURRENT_MONTH: 0,
            ATTR_LINKYCARD_CURRENT_MONTH_EVOLUTION: 0,
            ATTR_LINKYCARD_CURRENT_MONTH_LAST_YEAR: 0,
            ATTR_LINKYCARD_DAILY: [],
            ATTR_LINKYCARD_DAILY_WEEK: "",
            ATTR_LINKYCARD_DAILY_WEEK_HC: "0,0,0,0,0,0,0",
            ATTR_LINKYCARD_DAILY_WEEK_HP: "0,0,0,0,0,0,0",
            ATTR_LINKYCARD_DAILY_WEEK_COST: "0,0,0,0,0,0,0",
            ATTR_LINKYCARD_DAILY_WEEK_COST_HC: "0,0,0,0,0,0,0",
            ATTR_LINKYCARD_DAILY_WEEK_COST_HP: "0,0,0,0,0,0,0",
        }

    def round_to_month(self, date, ref_date):
        if date.month == ref_date.month:
            return date
        elif date.month < ref_date.month:
            return date.replace(month=ref_date.month, day=1)
        elif date.month > ref_date.month:
            return date.replace(
                month=ref_date.month,
                day=calendar.monthrange(ref_date.year, ref_date.month)[1],
            )

    def evolution(self, y, x):
        if x == 0:
            return 0
        return round((y - x) / x * 100)

    @callback
    def _handle_coordinator_update(self) -> None:
        daily = self.coordinator.data[DATA_DAILY]
        monthly = self.coordinator.data[DATA_MONTHLY]

        ref_date = datetime.now() - timedelta(days=DAY_OFFSET)

        # update latest day (now-3) energy and cost
        key = ref_date.strftime("%Y-%m-%d")
        if key in daily:
            self._attr_native_value = daily[key][DATA_ENERGY]
            self._attr_extra_state_attributes[ATTR_LINKYCARD_DAILY_COST] = daily[key][
                DATA_COST
            ]
            self._attr_extra_state_attributes[ATTR_LINKYCARD_YESTERDAY] = daily[key][
                DATA_ENERGY
            ]

        # update last week history
        self._attr_extra_state_attributes[ATTR_LINKYCARD_DAILY] = []
        self._attr_extra_state_attributes[ATTR_LINKYCARD_DAILY_WEEK] = ""
        self._attr_extra_state_attributes[ATTR_LINKYCARD_DAILY_WEEK_COST] = ""
        current_week_sum = 0
        prev = None
        for i in range(DAY_OFFSET, DAY_OFFSET + 7):
            key = self.round_to_month(
                datetime.now() - timedelta(days=i), ref_date
            ).strftime("%Y-%m-%d")
            if key != prev:
                prev = key

                d = daily.get(key)
                if d is None:
                    break
                self._attr_extra_state_attributes[ATTR_LINKYCARD_DAILY].append(
                    d[DATA_ENERGY]
                )
                self._attr_extra_state_attributes[ATTR_LINKYCARD_DAILY_WEEK] += (
                    key + ","
                )
                self._attr_extra_state_attributes[ATTR_LINKYCARD_DAILY_WEEK_COST] += (
                    str(d[DATA_COST]) + ","
                )

                if i == DAY_OFFSET + 1:  # yesterday
                    self._attr_extra_state_attributes[
                        ATTR_LINKYCARD_YESTERDAY_LAST_YEAR
                    ] = d[DATA_ENERGY]
                    self._attr_extra_state_attributes[
                        ATTR_LINKYCARD_YESTERDAY_EVOLUTION
                    ] = self.evolution(
                        self._attr_extra_state_attributes[ATTR_LINKYCARD_YESTERDAY],
                        self._attr_extra_state_attributes[
                            ATTR_LINKYCARD_YESTERDAY_LAST_YEAR
                        ],
                    )
                current_week_sum += d[DATA_ENERGY]

        # update last week results
        prev = None
        last_week_sum = 0
        for i in range(DAY_OFFSET + 7, DAY_OFFSET + 14):
            key = self.round_to_month(
                datetime.now() - timedelta(days=i), ref_date
            ).strftime("%Y-%m-%d")
            if key != prev:
                prev = key
                if key in daily:
                    last_week_sum += daily[key][DATA_ENERGY]
        self._attr_extra_state_attributes[
            ATTR_LINKYCARD_CURRENT_WEEK
        ] = current_week_sum
        self._attr_extra_state_attributes[
            ATTR_LINKYCARD_CURRENT_WEEK_LAST_YEAR
        ] = last_week_sum
        self._attr_extra_state_attributes[
            ATTR_LINKYCARD_CURRENT_WEEK_EVOLUTION
        ] = self.evolution(current_week_sum, last_week_sum)

        # update monthly results
        last_month = (ref_date - relativedelta(months=1)).strftime("%Y-%m")
        if last_month in monthly:
            self._attr_extra_state_attributes[ATTR_LINKYCARD_LAST_MONTH] = monthly[
                last_month
            ][DATA_ENERGY]
        last_month_last_year = (
            ref_date - relativedelta(years=1) - relativedelta(months=1)
        ).strftime("%Y-%m")
        if last_month_last_year in monthly:
            self._attr_extra_state_attributes[
                ATTR_LINKYCARD_LAST_MONTH_LAST_YEAR
            ] = monthly[last_month_last_year][DATA_ENERGY]
        self._attr_extra_state_attributes[
            ATTR_LINKYCARD_MONTHLY_EVOLUTION
        ] = self.evolution(
            self._attr_extra_state_attributes[ATTR_LINKYCARD_LAST_MONTH],
            self._attr_extra_state_attributes[ATTR_LINKYCARD_LAST_MONTH_LAST_YEAR],
        )

        current_month = ref_date.strftime("%Y-%m")
        if current_month in monthly:
            self._attr_extra_state_attributes[ATTR_LINKYCARD_CURRENT_MONTH] = monthly[
                current_month
            ][DATA_ENERGY]
        current_month_last_year = (ref_date - relativedelta(years=1)).strftime("%Y-%m")
        if current_month_last_year in monthly:
            self._attr_extra_state_attributes[
                ATTR_LINKYCARD_CURRENT_MONTH_LAST_YEAR
            ] = monthly[current_month_last_year][DATA_ENERGY]
        self._attr_extra_state_attributes[
            ATTR_LINKYCARD_CURRENT_MONTH_EVOLUTION
        ] = self.evolution(
            self._attr_extra_state_attributes[ATTR_LINKYCARD_CURRENT_MONTH],
            self._attr_extra_state_attributes[ATTR_LINKYCARD_CURRENT_MONTH_LAST_YEAR],
        )

        self.async_write_ha_state()