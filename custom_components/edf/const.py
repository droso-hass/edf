"""Constants for EDF """
# Base component constants
NAME = "EDF"
DOMAIN = "edf"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "1.0"
ATTRIBUTION = "Data provided by EDF"

ISSUE_URL = "https://github.com/droso-hass/edf/issues"

# Platforms
BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
PLATFORMS = [BINARY_SENSOR, SENSOR]

DATA_COORDINATOR = "data_coordinator"
GRID_COORDINATOR = "grid_coordinator"


# Configuration and options
CONF_JS_ERROR = "launch_error_str"
CONF_CODE_VERIFIER = "code_verifier"
CONF_STATE = "state"
CONF_NONCE = "nonce"
CONF_ACCESS_TOKEN = "access_token"
CONF_REFRESH_TOKEN = "refresh_token"
CONF_INSEE_CODE = "insee_code"
CONF_BUSINESS_PARTNER = "business_partner_number"
CONF_PDL = "pdl_id"
CONF_TOKEN_EXPIRATION = "expiration_date"

DATA_COST = "cost"
DATA_ENERGY = "energy"
DATA_DAILY = "daily"
DATA_HOURLY = "hourly"

ATTR_OUTAGE_TITLE = "title"
ATTR_OUTAGE_DESC = "description"
ATTR_OUTAGE_GRID = "grid_status"
ATTR_OUTAGE_HOMES = "affected_homes"
ATTR_OUTAGE_START = "start_date"
ATTR_OUTAGE_END = "end_date"
ATTR_OUTAGE_STATUS = "status"

STATE_CLASS_TOTAL = "total"

# Defaults
DEFAULT_NAME = DOMAIN

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
