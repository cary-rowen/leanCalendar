# A part of leanCalendar
# Copyright (C) 2026 Cary-rowen <manchen_0528@outlook.com>
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

from __future__ import annotations

import builtins
from collections.abc import Iterable
from datetime import datetime
import importlib
from pathlib import Path
import re
import sys
import types
import unittest


ROOT_DIR = Path(__file__).resolve().parents[1]
ADDON_DIR = ROOT_DIR / "addon"
TYME4PY_DIR = ADDON_DIR / "tyme4py"
LEAN_CALENDAR_DIR = ADDON_DIR / "globalPlugins" / "leanCalendar"
LEAN_CALENDAR_TEST_PACKAGE = "_leanCalendarContract"
CONTRACT_METHOD_NAMES = frozenset(
	{
		"from_index",
		"from_year",
		"from_ymd",
		"from_ymd_hms",
		"get_animal",
		"get_avoids",
		"get_constellation",
		"get_day",
		"get_day_count",
		"get_day_index",
		"get_days",
		"get_dog_day",
		"get_duty",
		"get_earth_branch",
		"get_ecliptic",
		"get_element",
		"get_festival",
		"get_fetus_day",
		"get_first_day",
		"get_first_julian_day",
		"get_first_month",
		"get_gods",
		"get_heaven_stem",
		"get_hide_heaven_stem_day",
		"get_hour",
		"get_hours",
		"get_index",
		"get_index_in_year",
		"get_joy_direction",
		"get_julian_day",
		"get_leap_month",
		"get_legal_holiday",
		"get_luck",
		"get_lunar_day",
		"get_lunar_hour",
		"get_lunar_month",
		"get_lunar_year",
		"get_mascot_direction",
		"get_minor_ren",
		"get_minute",
		"get_month",
		"get_month_count",
		"get_month_with_leap",
		"get_months",
		"get_name",
		"get_nine_day",
		"get_nine_star",
		"get_ominous",
		"get_opposite",
		"get_peng_zu",
		"get_phase_day",
		"get_phenology",
		"get_phenology_day",
		"get_plum_rain_day",
		"get_recommends",
		"get_second",
		"get_seven_star",
		"get_sixty_cycle",
		"get_sixty_cycle_day",
		"get_solar_day",
		"get_solar_month",
		"get_solar_term",
		"get_solar_time",
		"get_solar_week",
		"get_sound",
		"get_term",
		"get_term_day",
		"get_three_phenology",
		"get_twelve_star",
		"get_twenty_eight_star",
		"get_wealth_direction",
		"get_week",
		"get_year",
		"get_zodiac",
		"get_zone",
		"is_jie",
		"is_work",
		"next",
		"subtract",
	},
)
TYME_STYLE_METHOD_PATTERN = re.compile(r"\.([A-Za-z_][A-Za-z0-9_]*)\(")


def _translationIdentity(message: str) -> str:
	return message


def _installAddonHandlerStub() -> None:
	addonHandler = types.ModuleType("addonHandler")

	def initTranslation() -> None:
		builtins._ = _translationIdentity

	addonHandler.initTranslation = initTranslation
	sys.modules["addonHandler"] = addonHandler
	initTranslation()


def _installLeanCalendarTestPackage() -> None:
	package = types.ModuleType(LEAN_CALENDAR_TEST_PACKAGE)
	package.__path__ = [str(LEAN_CALENDAR_DIR)]
	package.__file__ = str(LEAN_CALENDAR_DIR / "__init__.py")
	sys.modules[LEAN_CALENDAR_TEST_PACKAGE] = package


def _importLeanCalendarModule(moduleName: str):
	return importlib.import_module(f"{LEAN_CALENDAR_TEST_PACKAGE}.{moduleName}")


def _solarDateTuple(solarDay) -> tuple[int, int, int]:
	return solarDay.get_year(), solarDay.get_month(), solarDay.get_day()


def _solarTimeTuple(solarTime) -> tuple[int, int, int, int, int, int]:
	return (
		solarTime.get_year(),
		solarTime.get_month(),
		solarTime.get_day(),
		solarTime.get_hour(),
		solarTime.get_minute(),
		solarTime.get_second(),
	)


def _values(items) -> list[int]:
	return [item.value for item in items]


def _collectTymeStyleMethodNames() -> set[str]:
	methodNames: set[str] = set()
	for path in LEAN_CALENDAR_DIR.glob("*.py"):
		text = path.read_text(encoding="utf-8")
		for match in TYME_STYLE_METHOD_PATTERN.finditer(text):
			methodName = match.group(1)
			if (
				methodName.startswith("get_")
				or methodName.startswith("is_")
				or methodName in {"next", "subtract", "from_index", "from_year", "from_ymd", "from_ymd_hms"}
			):
				methodNames.add(methodName)
	return methodNames


sys.path.insert(0, str(TYME4PY_DIR))
_installAddonHandlerStub()
_installLeanCalendarTestPackage()

from tyme4py.culture import Phase  # noqa: E402
from tyme4py.lunar import LunarHour, LunarYear  # noqa: E402
from tyme4py.solar import SolarDay, SolarTerm, SolarTime  # noqa: E402

tymeAccess = _importLeanCalendarModule("tymeAccess")
formats = _importLeanCalendarModule("formats")
data = _importLeanCalendarModule("data")
messages = _importLeanCalendarModule("messages")


class ContractInventoryTest(unittest.TestCase):
	def test_all_tyme_style_calls_are_registered_in_contract_inventory(self) -> None:
		usedMethodNames = _collectTymeStyleMethodNames()
		self.assertEqual(usedMethodNames - CONTRACT_METHOD_NAMES, set())


class ContractTestCase(unittest.TestCase):
	def assertCallableAttributes(self, obj: object, attributes: Iterable[str]) -> None:
		for attribute in attributes:
			with self.subTest(obj=type(obj).__name__, attribute=attribute):
				self.assertTrue(callable(getattr(obj, attribute, None)))

	def assertSolarDate(self, solarDay, expected: tuple[int, int, int]) -> None:
		self.assertEqual(_solarDateTuple(solarDay), expected)

	def assertSolarTime(self, solarTime, expected: tuple[int, int, int, int, int, int]) -> None:
		self.assertEqual(_solarTimeTuple(solarTime), expected)


class TymeAccessFactoryContractTest(ContractTestCase):
	def test_ensure_tyme4py_path_is_idempotent(self) -> None:
		tyme4pyPath = tymeAccess._TYME4PY_PATH
		originalSysPath = list(sys.path)
		try:
			sys.path[:] = [path for path in sys.path if path != tyme4pyPath]
			tymeAccess.ensureTyme4PyPath()
			tymeAccess.ensureTyme4PyPath()
			self.assertEqual(sys.path[0], tyme4pyPath)
			self.assertEqual(sys.path.count(tyme4pyPath), 1)
		finally:
			sys.path[:] = originalSysPath

	def test_factory_wrappers_preserve_constructor_inputs(self) -> None:
		solarTime = tymeAccess.createSolarTime(2026, 5, 3, 20, 15, 30)
		self.assertIsInstance(solarTime, SolarTime)
		self.assertSolarTime(solarTime, (2026, 5, 3, 20, 15, 30))

		solarDay = tymeAccess.createSolarDay(2026, 5, 3)
		self.assertIsInstance(solarDay, SolarDay)
		self.assertSolarDate(solarDay, (2026, 5, 3))

		lunarHour = tymeAccess.createLunarHour(2023, -2, 1, 23, 59, 58)
		self.assertIsInstance(lunarHour, LunarHour)
		self.assertSolarTime(lunarHour.get_solar_time(), (2023, 3, 22, 23, 59, 58))

		lunarYear = tymeAccess.createLunarYear(2023)
		self.assertIsInstance(lunarYear, LunarYear)
		self.assertEqual(lunarYear.get_leap_month(), 2)
		self.assertEqual(lunarYear.get_month_count(), 13)

		solarTerm = tymeAccess.createSolarTerm(2026, 1)
		self.assertIsInstance(solarTerm, SolarTerm)
		self.assertEqual(solarTerm.get_index(), 1)
		self.assertSolarDate(solarTerm.get_solar_day(), (2026, 1, 5))

		phase = tymeAccess.createPhase(2023, -2, 4)
		self.assertIsInstance(phase, Phase)
		self.assertEqual(phase.get_index(), 4)
		self.assertSolarDate(phase.get_solar_day(), (2023, 4, 6))

	def test_datetime_adapter_preserves_all_time_fields(self) -> None:
		now = datetime(2026, 5, 3, 20, 15, 30)
		self.assertSolarTime(tymeAccess.getSolarTime(now), (2026, 5, 3, 20, 15, 30))

	def test_required_methods_exist_on_calendar_object_graph(self) -> None:
		solarTime = tymeAccess.createSolarTime(2026, 5, 3, 20, 15, 30)
		solarDay = solarTime.get_solar_day()
		solarMonth = solarDay.get_solar_month()
		solarWeek = solarDay.get_solar_week(1)
		week = solarDay.get_week()
		lunarDay = solarDay.get_lunar_day()
		lunarMonth = lunarDay.get_lunar_month()
		lunarYear = lunarMonth.get_lunar_year()
		lunarHour = solarTime.get_lunar_hour()
		solarTerm = solarTime.get_term()
		phase = tymeAccess.createPhase(lunarMonth.get_year(), lunarMonth.get_month_with_leap(), 4)

		self.assertCallableAttributes(
			solarTime,
			(
				"get_year",
				"get_month",
				"get_day",
				"get_hour",
				"get_minute",
				"get_second",
				"get_solar_day",
				"get_lunar_hour",
				"get_term",
				"subtract",
			),
		)
		self.assertCallableAttributes(
			solarDay,
			(
				"get_year",
				"get_month",
				"get_day",
				"get_solar_month",
				"get_solar_week",
				"get_index_in_year",
				"get_constellation",
				"get_week",
				"get_lunar_day",
				"get_festival",
				"get_legal_holiday",
				"get_term",
				"get_term_day",
				"get_dog_day",
				"get_nine_day",
				"get_plum_rain_day",
				"get_phase_day",
				"get_hide_heaven_stem_day",
				"get_phenology_day",
				"get_nine_star",
			),
		)
		self.assertCallableAttributes(solarMonth, ("get_day_count",))
		self.assertCallableAttributes(solarWeek, ("get_index_in_year",))
		self.assertCallableAttributes(week, ("get_index",))
		self.assertCallableAttributes(
			lunarYear,
			(
				"get_first_month",
				"get_months",
				"get_leap_month",
				"get_month_count",
				"get_day_count",
				"get_sixty_cycle",
			),
		)
		self.assertCallableAttributes(
			lunarMonth,
			(
				"get_year",
				"get_month_with_leap",
				"get_name",
				"get_day_count",
				"get_lunar_year",
				"get_first_julian_day",
				"get_first_day",
				"get_days",
			),
		)
		self.assertCallableAttributes(
			lunarDay,
			(
				"get_day",
				"get_name",
				"get_lunar_month",
				"get_festival",
				"get_sixty_cycle_day",
				"get_duty",
				"get_twelve_star",
				"get_sixty_cycle",
				"get_twenty_eight_star",
				"get_fetus_day",
				"get_minor_ren",
				"get_gods",
				"get_recommends",
				"get_avoids",
				"get_hours",
			),
		)
		self.assertCallableAttributes(
			lunarHour,
			(
				"get_hour",
				"get_name",
				"get_lunar_day",
				"get_solar_time",
				"get_sixty_cycle",
				"get_twelve_star",
				"get_nine_star",
				"get_minor_ren",
				"get_recommends",
				"get_avoids",
			),
		)
		self.assertCallableAttributes(
			solarTerm,
			("get_name", "get_index", "get_year", "get_julian_day", "get_solar_day", "is_jie", "next"),
		)
		self.assertCallableAttributes(phase, ("get_index", "get_solar_time", "get_solar_day", "next"))

	def test_required_methods_exist_on_derived_culture_objects(self) -> None:
		solarTime = tymeAccess.createSolarTime(2026, 5, 3, 20, 15, 30)
		solarDay = solarTime.get_solar_day()
		lunarDay = solarDay.get_lunar_day()
		lunarHour = solarTime.get_lunar_hour()
		sixtyCycleDay = lunarDay.get_sixty_cycle_day()
		sixtyCycle = lunarDay.get_sixty_cycle()
		heavenStem = sixtyCycle.get_heaven_stem()
		earthBranch = sixtyCycle.get_earth_branch()
		twelveStar = lunarDay.get_twelve_star()
		ecliptic = twelveStar.get_ecliptic()
		twentyEightStar = lunarDay.get_twenty_eight_star()
		termDay = solarDay.get_term_day()
		phenologyDay = solarDay.get_phenology_day()
		phenology = phenologyDay.get_phenology()
		solarTermJulianDay = termDay.get_solar_term().get_julian_day()
		lunarMonthJulianDay = lunarDay.get_lunar_month().get_first_julian_day()
		gods = lunarDay.get_gods()
		legalHoliday = tymeAccess.createSolarDay(2022, 10, 8).get_legal_holiday()
		solarFestival = tymeAccess.createSolarDay(2011, 5, 1).get_festival()
		lunarFestival = tymeAccess.createSolarDay(2024, 2, 10).get_lunar_day().get_festival()

		self.assertCallableAttributes(sixtyCycleDay, ("get_year", "get_month", "get_sixty_cycle"))
		self.assertCallableAttributes(
			sixtyCycle,
			("get_heaven_stem", "get_earth_branch", "get_sound", "get_peng_zu"),
		)
		self.assertCallableAttributes(
			heavenStem,
			("next", "get_element", "get_wealth_direction", "get_joy_direction", "get_mascot_direction"),
		)
		self.assertCallableAttributes(
			earthBranch,
			("get_opposite", "get_zodiac", "get_element", "get_ominous"),
		)
		self.assertCallableAttributes(twelveStar, ("get_ecliptic",))
		self.assertCallableAttributes(ecliptic, ("get_luck",))
		self.assertCallableAttributes(
			twentyEightStar,
			("get_zone", "get_seven_star", "get_animal", "get_luck"),
		)
		self.assertCallableAttributes(termDay, ("get_solar_term", "get_day_index"))
		self.assertCallableAttributes(phenologyDay, ("get_phenology",))
		self.assertCallableAttributes(phenology, ("get_three_phenology", "next"))
		self.assertGreater(len(str(phenology.get_three_phenology())), 0)
		self.assertCallableAttributes(solarTermJulianDay, ("get_solar_time", "get_solar_day", "next"))
		self.assertCallableAttributes(lunarMonthJulianDay, ("get_solar_day", "next"))
		self.assertGreater(len(gods), 0)
		self.assertCallableAttributes(gods[0], ("get_luck",))
		self.assertCallableAttributes(gods[0].get_luck(), ("get_index",))
		self.assertIsNotNone(legalHoliday)
		self.assertCallableAttributes(legalHoliday, ("get_name", "is_work"))
		self.assertTrue(legalHoliday.is_work())
		self.assertIsNotNone(solarFestival)
		self.assertCallableAttributes(solarFestival, ("get_name",))
		self.assertIsNotNone(lunarFestival)
		self.assertCallableAttributes(lunarFestival, ("get_name",))
		self.assertEqual(lunarHour.get_lunar_day().get_day(), lunarDay.get_day())


class CalendarQueryRangeContractTest(ContractTestCase):
	def test_query_range_boundaries_are_inclusive(self) -> None:
		self.assertSolarDate(data.getMinQuerySolarDay(), (1900, 1, 31))
		self.assertSolarDate(data.getMaxQuerySolarDay(), (2101, 1, 28))

		minQuery = data.CalendarQuery.fromSolarValues(1900, 1, 31, 0, 0, 0)
		maxQuery = data.CalendarQuery.fromSolarValues(2101, 1, 28, 23, 59, 59)
		clampedMin = data.CalendarQuery.fromDatetime(datetime(1899, 12, 31, 12, 30, 45))
		clampedMax = data.CalendarQuery.fromDatetime(datetime(2101, 2, 1, 12, 30, 45))
		self.assertSolarTime(minQuery.solarTime, (1900, 1, 31, 0, 0, 0))
		self.assertSolarTime(maxQuery.solarTime, (2101, 1, 28, 23, 59, 59))
		self.assertSolarTime(clampedMin.solarTime, (1900, 1, 31, 0, 0, 0))
		self.assertSolarTime(clampedMax.solarTime, (2101, 1, 28, 23, 59, 59))

		with self.assertRaisesRegex(ValueError, "outside the supported leanCalendar range"):
			data.CalendarQuery.fromSolarValues(1900, 1, 30, 23, 59, 59)
		with self.assertRaisesRegex(ValueError, "outside the supported leanCalendar range"):
			data.CalendarQuery.fromSolarValues(2101, 1, 29, 0, 0, 0)

	def test_query_range_clamping_uses_boundary_day_extremes(self) -> None:
		beforeRange = tymeAccess.createSolarTime(1899, 12, 31, 12, 30, 45)
		afterRange = tymeAccess.createSolarTime(2101, 2, 1, 12, 30, 45)
		self.assertSolarTime(data.clampSolarTimeToQueryRange(beforeRange), (1900, 1, 31, 0, 0, 0))
		self.assertSolarTime(data.clampSolarTimeToQueryRange(afterRange), (2101, 1, 28, 23, 59, 59))

	def test_lunar_boundaries_map_to_query_solar_boundaries(self) -> None:
		minQuery = data.CalendarQuery.fromLunarValues(1900, 1, 1, 0, 0, 0)
		maxQuery = data.CalendarQuery.fromLunarValues(2100, 12, 29, 23, 0, 0)
		self.assertSolarTime(minQuery.solarTime, (1900, 1, 31, 0, 0, 0))
		self.assertSolarTime(maxQuery.solarTime, (2101, 1, 28, 23, 0, 0))

	def test_solar_and_lunar_round_trips_cover_edge_cases(self) -> None:
		samples = (
			(1900, 1, 31, 0, 0, 0),
			(2020, 5, 23, 23, 59, 58),
			(2023, 3, 22, 23, 59, 58),
			(2033, 12, 22, 0, 0, 0),
			(2026, 5, 3, 20, 15, 30),
			(2101, 1, 28, 23, 59, 59),
		)
		for sample in samples:
			with self.subTest(sample=sample):
				solarQuery = data.CalendarQuery.fromSolarValues(*sample)
				solarTime = solarQuery.solarTime
				lunarDay = solarTime.get_solar_day().get_lunar_day()
				lunarMonth = lunarDay.get_lunar_month()
				roundTrip = data.CalendarQuery.fromLunarValues(
					lunarMonth.get_year(),
					lunarMonth.get_month_with_leap(),
					lunarDay.get_day(),
					solarTime.get_hour(),
					solarTime.get_minute(),
					solarTime.get_second(),
				)
				self.assertSolarTime(roundTrip.solarTime, sample)

	def test_choice_lists_cover_boundary_clipping_and_leap_months(self) -> None:
		solarYears = data.getSolarYearChoices()
		self.assertEqual((solarYears[0].value, solarYears[-1].value, len(solarYears)), (1900, 2101, 202))
		self.assertEqual(_values(data.getSolarHourChoices()), list(range(24)))
		self.assertEqual([item.label for item in data.getSolarHourChoices()[:3]], ["00", "01", "02"])

		self.assertEqual(_values(data.getSolarDayChoices(1900, 1)), [31])
		self.assertEqual(_values(data.getSolarMonthChoices(2101)), [1])
		self.assertEqual(_values(data.getSolarDayChoices(2101, 1)), list(range(1, 29)))
		self.assertEqual(len(data.getSolarDayChoices(2024, 2)), 29)
		self.assertEqual(len(data.getSolarDayChoices(2100, 2)), 28)

		lunarYears = data.getLunarYearChoices()
		self.assertEqual((lunarYears[0].value, lunarYears[-1].value, len(lunarYears)), (1900, 2100, 201))
		for year, leapMonth, leapDayCount in (
			(1900, -8, 29),
			(2020, -4, 29),
			(2023, -2, 29),
			(2033, -11, 29),
		):
			with self.subTest(year=year, leapMonth=leapMonth):
				monthValues = _values(data.getLunarMonthChoices(year))
				self.assertIn(leapMonth, monthValues)
				self.assertEqual(len(monthValues), 13)
				self.assertEqual(len(data.getLunarDayChoices(year, leapMonth)), leapDayCount)

		self.assertEqual(data.getLunarDayChoices(2023, -3), [])
		self.assertEqual(
			_values(data.getLunarHourChoices(2023, -2, 1)),
			[0, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23],
		)

	def test_solar_term_choices_cover_full_and_clipped_years(self) -> None:
		fullYearChoices = data.getSolarTermChoices(2026)
		self.assertEqual(len(fullYearChoices), 24)
		self.assertEqual(fullYearChoices[0].index, 1)
		self.assertSolarDate(fullYearChoices[0].solarTime.get_solar_day(), (2026, 1, 5))
		self.assertEqual(fullYearChoices[-1].index, 0)
		self.assertEqual(fullYearChoices[-1].termYear, 2027)
		self.assertSolarDate(fullYearChoices[-1].solarTime.get_solar_day(), (2026, 12, 22))

		minBoundaryChoices = data.getSolarTermChoices(1900)
		self.assertEqual(len(minBoundaryChoices), 22)
		self.assertEqual(minBoundaryChoices[0].index, 3)
		self.assertEqual(minBoundaryChoices[-1].index, 0)

		maxBoundaryChoices = data.getSolarTermChoices(2101)
		self.assertEqual(len(maxBoundaryChoices), 2)
		self.assertEqual([choice.index for choice in maxBoundaryChoices], [1, 2])
		self.assertSolarDate(maxBoundaryChoices[-1].solarTime.get_solar_day(), (2101, 1, 20))

	def test_phase_lookup_supports_normal_and_leap_lunar_months(self) -> None:
		for lunarYear, lunarMonth in ((2026, 1), (2023, -2), (2033, -11)):
			with self.subTest(lunarYear=lunarYear, lunarMonth=lunarMonth):
				for phaseIndex in (0, 2, 4, 6):
					phase = tymeAccess.createPhase(lunarYear, lunarMonth, phaseIndex)
					self.assertEqual(phase.get_index(), phaseIndex)
					self.assertIsInstance(phase.get_solar_time(), SolarTime)
					self.assertIsInstance(phase.get_solar_day(), SolarDay)


class FormatContractTest(ContractTestCase):
	def test_basic_formatters_preserve_numeric_fields(self) -> None:
		solarTime = tymeAccess.createSolarTime(2026, 5, 3, 20, 15, 30)
		solarDay = solarTime.get_solar_day()
		lunarDay = solarDay.get_lunar_day()
		lunarMonth = lunarDay.get_lunar_month()

		self.assertEqual(formats.formatSolarTimeOnly(solarTime), "20:15:30")
		self.assertEqual(formats.formatClockTime(solarTime), "20 hour 15 minute 30 second")
		self.assertEqual(formats.formatSolarDate(solarDay), "2026-5-3")
		self.assertEqual(formats.formatSolarDateHour(solarTime), "2026-5-3 20:00")
		self.assertEqual(formats.formatSolarDateTime(solarTime), "2026-05-03 20:15:30")
		self.assertEqual(formats.formatSolarMonthDayTime(solarTime), "5-3 20:15:30")
		self.assertEqual(
			formats.formatYearMonthDayHour("2026", "5", "3", "20"),
			"2026 year 5 month 3 day 20 hour",
		)
		self.assertEqual(formats.formatSolarMonthDayCount(solarDay), "5 has 31 days")
		self.assertEqual(formats.formatYearDay(solarDay), "year day 123")
		self.assertTrue(formats.formatWeekNumber(solarDay).startswith("week "))
		self.assertEqual(formats.formatQuarter(solarDay), "quarter 2")
		self.assertTrue(formats.formatWeekday(solarDay).startswith("weekday "))
		self.assertTrue(formats.formatWesternZodiacSign(solarDay).startswith("Western zodiac sign "))
		self.assertTrue(formats.formatLunarDate(lunarDay).startswith(lunarMonth.get_name()))
		self.assertTrue(formats.formatLunarDateCompact(lunarDay).startswith(lunarMonth.get_name()))

	def test_lunar_month_size_distinguishes_long_and_short_months(self) -> None:
		monthsByValue = {
			lunarMonth.get_month_with_leap(): lunarMonth
			for lunarMonth in tymeAccess.createLunarYear(2023).get_months()
		}
		self.assertTrue(formats.formatLunarMonthSize(monthsByValue[2]).endswith(" long"))
		self.assertTrue(formats.formatLunarMonthSize(monthsByValue[-2]).endswith(" short"))

	def test_duration_formatters_cover_zero_minute_hour_and_day_boundaries(self) -> None:
		self.assertEqual(formats.formatSecondsUntil(0), "now")
		self.assertEqual(formats.formatSecondsUntil(-1), "now")
		self.assertEqual(formats.formatSecondsUntil(59), "less than 1 minute")
		self.assertEqual(formats.formatSecondsUntil(60), "1 minutes")
		self.assertEqual(formats.formatSecondsUntil(3599), "59 minutes")
		self.assertEqual(formats.formatSecondsUntil(3600), "1 hours 0 minutes")
		self.assertEqual(formats.formatSecondsUntil(90061), "1 days 1 hours")
		self.assertEqual(formats.formatBriefSecondsUntil(86399), "23 hours 59 minutes")
		self.assertEqual(formats.formatBriefSecondsUntil(86400), "1 days")
		self.assertEqual(formats.formatBriefSecondsUntil(172799), "1 days")

	def test_holiday_weekday_and_traditional_period_contracts(self) -> None:
		holidayOff = formats.getGregorianHolidaySummary(tymeAccess.createSolarTime(2011, 5, 1))
		holidayWork = formats.getGregorianHolidaySummary(tymeAccess.createSolarTime(2022, 10, 8))
		self.assertIsNotNone(holidayOff)
		self.assertIsNotNone(holidayWork)
		self.assertTrue(holidayOff.endswith(" off"))
		self.assertTrue(holidayWork.endswith(" work"))

		self.assertIsNone(formats.getGregorianDayStatus(tymeAccess.createSolarDay(2011, 5, 1)))
		self.assertEqual(formats.getGregorianDayStatus(tymeAccess.createSolarDay(2026, 5, 10)), "weekend")
		self.assertEqual(formats.getGregorianDayStatus(tymeAccess.createSolarDay(2026, 5, 6)), "workday")

		self.assertIsNotNone(formats.getLunarFestivalSummary(tymeAccess.createSolarTime(2024, 2, 10)))
		self.assertEqual(formats.getTraditionalPeriodSummaries(tymeAccess.createSolarDay(2024, 5, 1)), [])
		for sample in ((2011, 7, 14), (2020, 12, 21), (2024, 6, 11)):
			with self.subTest(sample=sample):
				self.assertGreater(
					len(formats.getTraditionalPeriodSummaries(tymeAccess.createSolarDay(*sample))),
					0,
				)

	def test_solar_term_and_phase_formatting_contracts(self) -> None:
		solarDay = tymeAccess.createSolarDay(2023, 12, 22)
		self.assertTrue(formats.formatSolarTermDay(solarDay).endswith(" day 1"))
		self.assertTrue(formats.getPhaseDaySummary(solarDay).startswith("moon phase "))

		solarTerm = tymeAccess.createSolarTerm(2026, 1)
		compact = formats.formatSolarTermCompact(solarTerm)
		self.assertIn(solarTerm.get_name(), compact)
		self.assertGreater(len(compact), len(solarTerm.get_name()))

	def test_next_solar_term_summary_respects_seven_day_window(self) -> None:
		nearTerm = formats.getBriefNextSolarTermSummary(tymeAccess.createSolarTime(2026, 5, 3, 0, 0, 0))
		farFromTerm = formats.getBriefNextSolarTermSummary(tymeAccess.createSolarTime(2026, 5, 10, 0, 0, 0))
		self.assertIsNotNone(nearTerm)
		self.assertTrue(nearTerm.startswith("until "))
		self.assertIsNone(farFromTerm)

	def test_join_helpers_are_stable_for_empty_limited_and_over_limit_lists(self) -> None:
		self.assertEqual(formats.joinParts(["a", "b", "c"]), "a, b, c")
		self.assertEqual(formats.joinLimitedParts(["a", "b", "c"], limit=2), "a, b...")
		self.assertEqual(formats.joinLimitedParts(["a", "b"], limit=2), "a, b")


class MessagesAndDisplayContractTest(ContractTestCase):
	def test_public_messages_for_fixed_datetime_cover_all_report_modes(self) -> None:
		now = datetime(2026, 5, 10, 20, 15, 30)

		self.assertEqual(messages.getBriefGregorianMessage(now), "20 hour 15 minute 30 second")
		detailedGregorian = messages.getDetailedGregorianMessage(now)
		for fragment in (
			"2026-5-10",
			"weekday ",
			"year day 130",
			"quarter 2",
			"5 has 31 days",
			"weekend",
			"Western zodiac sign ",
		):
			with self.subTest(fragment=fragment):
				self.assertIn(fragment, detailedGregorian)

		briefLeanCalendar = messages.getBriefLeanCalendarMessage(now)
		self.assertIn(" year, ", briefLeanCalendar)
		self.assertIn(" month, ", briefLeanCalendar)
		self.assertIn(" day ", briefLeanCalendar)

		detailedLeanCalendar = messages.getDetailedLeanCalendarMessage(now)
		for fragment in ("until ", "Chinese zodiac ", "full moon at ", "moon phase ", "Jianchu duty "):
			with self.subTest(fragment=fragment):
				self.assertIn(fragment, detailedLeanCalendar)

	def test_detailed_lunar_message_uses_immediate_next_solar_term(self) -> None:
		now = datetime(2026, 6, 14, 0, 0, 0)
		solarTime = tymeAccess.createSolarTime(now.year, now.month, now.day, now.hour, now.minute, now.second)
		currentTerm = solarTime.get_term()
		nextTerm = currentTerm.next(1)
		nextJie = currentTerm.next(2)

		detailedLeanCalendar = messages.getDetailedLeanCalendarMessage(now)

		self.assertTrue(currentTerm.is_jie())
		self.assertIn(formats.formatSolarTermCompact(nextTerm), detailedLeanCalendar)
		self.assertIn(f"until {nextTerm.get_name()} ", detailedLeanCalendar)
		self.assertNotIn(f"until {nextJie.get_name()} ", detailedLeanCalendar)

	def test_detailed_lunar_message_does_not_skip_current_qi_term(self) -> None:
		now = datetime(2026, 6, 27, 0, 0, 0)
		solarTime = tymeAccess.createSolarTime(now.year, now.month, now.day, now.hour, now.minute, now.second)
		currentTerm = solarTime.get_term()
		previousJie = currentTerm.next(-1)
		nextTerm = currentTerm.next(1)

		detailedLeanCalendar = messages.getDetailedLeanCalendarMessage(now)

		self.assertFalse(currentTerm.is_jie())
		self.assertLess(
			detailedLeanCalendar.index(formats.formatSolarTermCompact(previousJie)),
			detailedLeanCalendar.index(formats.formatSolarTermCompact(currentTerm)),
		)
		self.assertLess(
			detailedLeanCalendar.index(formats.formatSolarTermCompact(currentTerm)),
			detailedLeanCalendar.index(formats.formatSolarTermCompact(nextTerm)),
		)
		self.assertIn(f"until {nextTerm.get_name()} ", detailedLeanCalendar)

	def test_basic_display_uses_immediate_next_solar_term(self) -> None:
		query = data.CalendarQuery.fromSolarValues(2026, 6, 14, 0, 0, 0)
		currentTerm = query.solarTime.get_term()
		nextTerm = currentTerm.next(1)
		nextJie = currentTerm.next(2)

		sections = data.buildBasicSections(query)
		solarTermSection = next(
			section for section in sections if section.label == "Solar Terms and Phenology"
		)
		countdownLine = solarTermSection.lines[1]

		self.assertTrue(currentTerm.is_jie())
		self.assertIn(formats.formatSolarTermCompact(nextTerm), countdownLine)
		self.assertIn(f"until {nextTerm.get_name()} ", countdownLine)
		self.assertNotIn(f"until {nextJie.get_name()} ", countdownLine)

	def test_basic_display_sections_cover_all_result_groups(self) -> None:
		query = data.CalendarQuery.fromSolarValues(2026, 5, 3, 20, 15, 30)
		sections = data.buildBasicSections(query)
		self.assertEqual(
			[section.label for section in sections],
			["Gregorian", "Lunar", "Solar Terms and Phenology", "Almanac"],
		)
		for section in sections:
			with self.subTest(section=section.label):
				self.assertGreater(len(section.lines), 0)

		summary = data.buildSummary(query)
		self.assertIn("2026-5-3 20:00", summary)
		self.assertIn(" | Lunar ", summary)

		basicText = data.buildBasicText(query)
		for fragment in (
			"Gregorian\n",
			"Lunar\n",
			"Solar Terms and Phenology\n",
			"Almanac\n",
			"Moon phases ",
			"LunarHour luck ",
			"FetusDay ",
			"PengZu Baiji ",
			"TwentyEightStar ",
			"Jianchu duty ",
			"until ",
		):
			with self.subTest(fragment=fragment):
				self.assertIn(fragment, basicText)

	def test_edge_case_dates_build_public_payloads_without_runtime_errors(self) -> None:
		samples = (
			(1900, 1, 31, 0),
			(2011, 5, 1, 12),
			(2011, 7, 14, 12),
			(2020, 12, 21, 12),
			(2023, 3, 22, 23),
			(2024, 2, 10, 8),
			(2024, 6, 11, 12),
			(2033, 12, 22, 0),
			(2101, 1, 28, 23),
		)
		for year, month, day, hour in samples:
			with self.subTest(year=year, month=month, day=day, hour=hour):
				query = data.CalendarQuery.fromSolarValues(year, month, day, hour)
				self.assertGreater(len(data.buildSummary(query)), 0)
				self.assertEqual(len(data.buildBasicSections(query)), 4)
				self.assertGreater(len(data.buildBasicText(query)), 0)


if __name__ == "__main__":
	unittest.main()
