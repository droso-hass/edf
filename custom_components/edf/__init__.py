"""
Custom integration for EDF for Home Assistant.
"""
import asyncio
import aiohttp
import logging
from datetime import timedelta, datetime
import calendar
from dateutil.relativedelta import relativedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from edf_api import EDFApi
from .const import (
    BINARY_SENSOR,
    CONF_INSEE_CODE,
    CONF_ACCESS_TOKEN,
    CONF_REFRESH_TOKEN,
    CONF_PDL,
    CONF_BUSINESS_PARTNER,
    CONF_TOKEN_EXPIRATION,
    DATA_COORDINATOR,
    DATA_COST,
    DATA_DAILY,
    DATA_ENERGY,
    DATA_HOURLY,
    DOMAIN,
    GRID_COORDINATOR,
    PLATFORMS,
    SENSOR,
    STARTUP_MESSAGE,
    ENABLE_LINKYCARD,
    DATA_MONTHLY,
    DAY_OFFSET
)

DATA_SCAN_INTERVAL = timedelta(minutes=30)
GRID_SCAN_INTERVAL = timedelta(minutes=10)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    access_token = entry.data.get(CONF_ACCESS_TOKEN)
    refresh_token = entry.data.get(CONF_REFRESH_TOKEN)
    token_expiration = entry.data.get(CONF_TOKEN_EXPIRATION)
    pdl = entry.data.get(CONF_PDL)
    bp = entry.data.get(CONF_BUSINESS_PARTNER)
    insee = entry.data.get(CONF_INSEE_CODE)

    #session = async_get_clientsession(hass)
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=1, force_close=True))
    client = EDFApi(session, access_token, refresh_token, token_expiration, bp, pdl, insee)

    grid_coordinator = EDFGridDataUpdateCoordinator(
        hass, client=client, pdl_id=pdl, insee_code=insee
    )
    data_coordinator = EDFDataUpdateCoordinator(
        hass, client=client, bp_id=bp, pdl_id=pdl
    )
    await grid_coordinator.async_refresh()
    await data_coordinator.async_refresh()

    if not data_coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = {
        GRID_COORDINATOR: grid_coordinator,
        DATA_COORDINATOR: data_coordinator,
    }

    if entry.options.get(BINARY_SENSOR, True):
        grid_coordinator.platforms.append(BINARY_SENSOR)
        hass.async_add_job(
            hass.config_entries.async_forward_entry_setup(entry, BINARY_SENSOR)
        )
    if entry.options.get(SENSOR, True):
        data_coordinator.platforms.append(SENSOR)
        hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, SENSOR))

    entry.add_update_listener(async_reload_entry)
    return True


class EDFDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: EDFApi,
        bp_id: str,
        pdl_id: str,
    ) -> None:
        """Initialize."""
        self.api = client
        self.bp_id = bp_id
        self.pdl_id = pdl_id
        self.platforms = []
        self._data = {}
        self._next_update = None

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=DATA_SCAN_INTERVAL)

    async def async_update(self):
        await self._async_update_data()

    async def _get_data(self, year, month):
        start = datetime(year, month, 1)
        data = await self.api.get_elec_daily_data(
            start.strftime("%Y-%m-%d"),
            (start.replace(day=calendar.monthrange(start.year, start.month)[1])).strftime("%Y-%m-%d"),
        )
        if "errorCode" in data:
            raise UpdateFailed(data.get("errorDescription"))
        # process data
        for i in data["dailyLoadCurves"]:
            self._data[DATA_DAILY][i["day"]] = {
                DATA_COST: i["totalCost"],
                DATA_ENERGY: i["totalEnergy"],
            }
            for j in i["consumptions"]:
                self._data[DATA_HOURLY][j["timestamp"]] = {
                    DATA_COST: j["cost"],
                    DATA_ENERGY: j["energy"],
                }

    async def _async_update_data(self):
        """Update data via library."""
        try:
            if self._next_update is None or datetime.now() >= self._next_update:
                # fetch data
                self._data = {DATA_HOURLY: {}, DATA_DAILY: {}, DATA_MONTHLY: {}}

                start = datetime.now() - timedelta(days=DAY_OFFSET)
                if ENABLE_LINKYCARD:
                    start = datetime.now() - timedelta(days=DAY_OFFSET+14)
                end = datetime.now() - timedelta(days=1)

                await self._get_data(start.year,start.month)
                if end.month != start.month:
                    await self._get_data(end.year,end.month)

                if ENABLE_LINKYCARD:
                    # get this month, last month, this month last year, last month last year data
                    monthly = await self.api.get_elec_monthly_data((start - relativedelta(years=1) - relativedelta(months=1)).strftime("%Y-%m"), (end+relativedelta(months=1)).strftime("%Y-%m"))
                    for i in monthly["monthlyConsumptions"]:
                        self._data[DATA_MONTHLY][i["endTs"][0:7]] = {
                            DATA_COST: i["consumption"]["cost"],
                            DATA_ENERGY: i["consumption"]["energy"],
                        }

                # set next update to the next day at 11 AM
                self._next_update = (datetime.now() + timedelta(days=1)).replace(
                    hour=11
                )
                _LOGGER.info(
                    "next update: " + self._next_update.strftime("%Y-%m-%dT%H:%M:%SZ")
                )

            return self._data
        except UpdateFailed:
            raise
        except Exception as exception:
            _LOGGER.warn(exception)
            raise UpdateFailed() from exception


class EDFGridDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self, hass: HomeAssistant, client: EDFApi, pdl_id: str, insee_code: str
    ) -> None:
        """Initialize."""
        self.api = client
        self.pdl_id = pdl_id
        self.insee_code = insee_code
        self.platforms = []
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=GRID_SCAN_INTERVAL)

    async def async_update(self):
        await self._async_update_data()

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.api.get_grid_info()
        except Exception as exception:
            raise UpdateFailed() from exception


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    platforms = (
        hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR].platforms
        + hass.data[DOMAIN][entry.entry_id][GRID_COORDINATOR].platforms
    )
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
