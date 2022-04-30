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

DAY_OFFSET = 3
ENABLE_LINKYCARD = True

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
DATA_MONTHLY = "monthly"

ATTR_OUTAGE_TITLE = "title"
ATTR_OUTAGE_DESC = "description"
ATTR_OUTAGE_GRID = "grid_status"
ATTR_OUTAGE_HOMES = "affected_homes"
ATTR_OUTAGE_START = "start_date"
ATTR_OUTAGE_END = "end_date"
ATTR_OUTAGE_STATUS = "status"
ATTR_UPDATE_DATE = "update_date"

# linky card attributes
ATTR_LINKYCARD_YESTERDAY_HP = "yesterday_HP"
ATTR_LINKYCARD_YESTERDAY_HC = "yesterday_HC"
ATTR_LINKYCARD_YESTERDAY_HPHC = "yesterday_HCHP"
ATTR_LINKYCARD_YESTERDAY = "yesterday"
ATTR_LINKYCARD_YESTERDAY_EVOLUTION = "yesterday_evolution"
ATTR_LINKYCARD_YESTERDAY_LAST_YEAR = "yesterdayLastYear"
ATTR_LINKYCARD_CURRENT_WEEK = "current_week"
ATTR_LINKYCARD_CURRENT_WEEK_LAST_YEAR = "current_week_last_year"
ATTR_LINKYCARD_CURRENT_WEEK_EVOLUTION = "current_week_evolution"
ATTR_LINKYCARD_UNIT = "unit_of_measurement"
ATTR_LINKYCARD_TYPE_COMPTEUR = "typeCompteur"
ATTR_LINKYCARD_PERCENT_HP = "peak_offpeak_percent"
ATTR_LINKYCARD_ERROR = "errorLastCall"
ATTR_LINKYCARD_DAILY_COST = "daily_cost"
ATTR_LINKYCARD_MONTHLY_EVOLUTION = "monthly_evolution"
ATTR_LINKYCARD_LAST_MONTH = "last_month"
ATTR_LINKYCARD_LAST_MONTH_LAST_YEAR = "last_month_last_year"
ATTR_LINKYCARD_CURRENT_MONTH = "current_month"
ATTR_LINKYCARD_CURRENT_MONTH_EVOLUTION = "current_month_evolution"
ATTR_LINKYCARD_CURRENT_MONTH_LAST_YEAR = "current_month_last_year"
ATTR_LINKYCARD_DAILY = "daily"
ATTR_LINKYCARD_DAILY_WEEK = "dailyweek"
ATTR_LINKYCARD_DAILY_WEEK_HC = "dailyweek_HC"
ATTR_LINKYCARD_DAILY_WEEK_HP = "dailyweek_HP"
ATTR_LINKYCARD_DAILY_WEEK_COST = "dailyweek_cost"
ATTR_LINKYCARD_DAILY_WEEK_COST_HC = "dailyweek_costHC"
ATTR_LINKYCARD_DAILY_WEEK_COST_HP = "dailyweek_costHP"


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
