# DEPRECATED: This repository is no longer maintained, latest tests shows that this API is working but could get your account banned

# EDF integration for Home Assistant

## About

A simple EDF integration to retrieve the energy usage and costs from your EDF account.

The sensors are compatible with the energy dashboard (note that there is an offset of 3 days as EDF is pretty slow to make the data available).

A status binary sensor is also provided to monitor the grid outages.

Currently only compatible with electricity data (Linky) without HP/HC distinction.

Based on the python library [edf-api](https://github.com/droso-hass/edf-api).


## Installation with HACS

Open HACS and add this custom repository `https://github.com/droso-hass/edf` with the category `Integration`.

Then click on the integration, and click `Download this repository with HACS`.

You can then go in `Settings > Devices & Services` and add the integration.



## Content-card-linky

This integration provides a sensor `edf_xxxxxx_linky_card` compatible with  [content-card-linky](https://github.com/saniho/content-card-linky).

The recommanded configuration is the following:

```yaml
type: custom:content-card-linky
entity: sensor.edf_xxxxxxx_linky_card
nbJoursAffichage: '7'
titleName: Linky
showError: false
showYesterdayRatio: true
showMonthRatio: true
showDayHCHP: false
showDayPriceHCHP: false
showInTableUnit: true
showHistory: true
showIcon: true
showTitle: true
showPeakOffPeak: false
showDayPrice: true
showPrice: true
showCurrentMonthRatio: true
showWeekRatio: true
showTitreLigne: false
```
