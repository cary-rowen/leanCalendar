# tyme4py Contract Surface

This document defines the tyme4py behavior that leanCalendar depends on.
Update it when leanCalendar starts using new tyme4py APIs, and keep
`test_tyme4py_contract.py` aligned with this inventory.

## Update Policy

- Submodule updates must be release-tag based, not arbitrary upstream commits.
- Any tyme4py update must pass this contract suite before its PR is ready to merge.
- Upstream tyme4py tests are useful as a compatibility signal, but they do not replace
  these leanCalendar-specific contract tests.
- Contract failures should be treated as blocking until the API change is reviewed and
  leanCalendar is either adapted or the update is rejected.

## Factory APIs

leanCalendar imports tyme4py through `addon/globalPlugins/leanCalendar/tymeAccess.py`.
The following wrappers are the only approved direct construction points:

- `createSolarTime`: wraps `tyme4py.solar.SolarTime.from_ymd_hms`.
- `createSolarDay`: wraps `tyme4py.solar.SolarDay.from_ymd`.
- `createLunarHour`: wraps `tyme4py.lunar.LunarHour.from_ymd_hms`.
- `createLunarYear`: wraps `tyme4py.lunar.LunarYear.from_year`.
- `createSolarTerm`: wraps `tyme4py.solar.SolarTerm.from_index`.
- `createPhase`: wraps `tyme4py.culture.Phase.from_index`.
- `getSolarTime`: adapts a `datetime.datetime` into a tyme4py `SolarTime`.

## Required Object Surface

The test suite verifies that the objects returned by these factories still expose
the methods leanCalendar calls in `data.py`, `formats.py`, `messages.py`, and the
dialog state builder. The contract tests also scan the leanCalendar sources for
new `tyme4py`-style method calls and fail if the inventory is not updated.

### SolarTime

- `get_year`, `get_month`, `get_day`
- `get_hour`, `get_minute`, `get_second`
- `get_solar_day`, `get_lunar_hour`, `get_term`
- `subtract`

### SolarDay

- `get_year`, `get_month`, `get_day`
- `get_solar_month`, `get_solar_week`, `get_index_in_year`
- `get_constellation`, `get_week`
- `get_lunar_day`, `get_festival`, `get_legal_holiday`
- `get_term`, `get_term_day`
- `get_dog_day`, `get_nine_day`, `get_plum_rain_day`
- `get_phase_day`, `get_hide_heaven_stem_day`, `get_phenology_day`
- `get_nine_star`

### LunarYear, LunarMonth, LunarDay, LunarHour

- `LunarYear`: `get_first_month`, `get_months`, `get_leap_month`,
  `get_month_count`, `get_day_count`, `get_sixty_cycle`
- `LunarMonth`: `get_year`, `get_month_with_leap`, `get_name`, `get_day_count`,
  `get_lunar_year`, `get_first_julian_day`, `get_first_day`, `get_days`
- `LunarDay`: `get_day`, `get_name`, `get_lunar_month`, `get_festival`,
  `get_sixty_cycle_day`, `get_duty`, `get_twelve_star`, `get_sixty_cycle`,
  `get_twenty_eight_star`, `get_fetus_day`, `get_minor_ren`, `get_gods`,
  `get_recommends`, `get_avoids`, `get_hours`
- `LunarHour`: `get_hour`, `get_name`, `get_lunar_day`, `get_solar_time`,
  `get_sixty_cycle`, `get_twelve_star`, `get_nine_star`, `get_minor_ren`,
  `get_recommends`, `get_avoids`

### SolarTerm, Phase, and Derived Culture Objects

- `SolarTerm`: `get_name`, `get_index`, `get_year`, `get_julian_day`,
  `get_solar_day`, `is_jie`, `next`
- `Phase`: `get_index`, `get_solar_time`, `get_solar_day`, `next`
- `SolarTermDay`: `get_solar_term`, `get_day_index`
- `PhenologyDay`: `get_phenology`
- `Phenology`: `get_three_phenology`, `next`
- `JulianDay`: `get_solar_time`, `get_solar_day`, `next`
- `SolarMonth`: `get_day_count`
- `SolarWeek`: `get_index_in_year`
- `Week`: `get_index`
- `Festival`: `get_name`
- `LegalHoliday`: `get_name`, `is_work`
- `SixtyCycleDay`: `get_year`, `get_month`, `get_sixty_cycle`
- `SixtyCycle`: `get_heaven_stem`, `get_earth_branch`, `get_sound`,
  `get_peng_zu`
- `HeavenStem`: `next`, `get_element`, `get_wealth_direction`,
  `get_joy_direction`, `get_mascot_direction`
- `EarthBranch`: `get_opposite`, `get_zodiac`, `get_element`, `get_ominous`
- `TwelveStar`: `get_ecliptic`
- `Ecliptic`: `get_luck`
- `TwentyEightStar`: `get_zone`, `get_seven_star`, `get_animal`, `get_luck`
- `God`: `get_luck`
- `Luck`: `get_index`

## Required Semantic Cases

The contract suite covers the following high-risk date and data cases:

- The supported query window, from lunar year 1900 through lunar year 2100,
  including the mapped Gregorian boundaries 1900-01-31 through 2101-01-28.
- Solar-to-lunar and lunar-to-solar round trips for normal dates, range
  boundaries, leap lunar months, and late-range leap-month edge cases.
- Gregorian leap years and century non-leap years.
- Lunar leap months in 1900, 2020, 2023, 2025, and 2033-era data.
- Solar term choice lists for full years and clipped boundary years.
- Solar term navigation across year boundaries.
- Moon phase lookup in normal and leap lunar months.
- Legal holidays, make-up work days, weekends, and normal workdays.
- Traditional periods used in output: dog days, nine-day periods, and plum rain.
- User-facing formatting wrappers and full basic-result construction.

## Test Mapping

- `TymeAccessFactoryContractTest`: direct factory wrappers and object API surface.
- `CalendarQueryRangeContractTest`: query bounds, choices, round trips, and term lists.
- `FormatContractTest`: formatting, holidays, traditional periods, and countdowns.
- `MessagesAndDisplayContractTest`: public message builders and dialog result payloads.
