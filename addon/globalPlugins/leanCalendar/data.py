# A part of leanCalendar
# Copyright (C) 2026 Cary-rowen <manchen_0528@outlook.com>
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from functools import cache
from typing import TYPE_CHECKING

import addonHandler

from . import formats
from .tymeAccess import (
	createPhase,
	createLunarHour,
	createLunarYear,
	createSolarDay,
	createSolarTerm,
	createSolarTime,
	getSolarTime,
)

addonHandler.initTranslation()

if TYPE_CHECKING:
	from tyme4py.lunar import LunarDay, LunarHour, LunarMonth
	from tyme4py.solar import SolarDay, SolarTime


@dataclass(frozen=True)
class CalendarQuery:
	solarTime: SolarTime

	@classmethod
	def fromDatetime(cls, now: datetime) -> CalendarQuery:
		return cls(clampSolarTimeToQueryRange(getSolarTime(now)))

	@classmethod
	def fromSolarValues(
		cls,
		year: int,
		month: int,
		day: int,
		hour: int,
		minute: int = 0,
		second: int = 0,
	) -> CalendarQuery:
		solarTime: SolarTime = createSolarTime(year, month, day, hour, minute, second)
		_validateSolarTimeInQueryRange(solarTime)
		return cls(solarTime)

	@classmethod
	def fromLunarValues(
		cls,
		year: int,
		month: int,
		day: int,
		hour: int,
		minute: int = 0,
		second: int = 0,
	) -> CalendarQuery:
		solarTime: SolarTime = createLunarHour(year, month, day, hour, minute, second).get_solar_time()
		_validateSolarTimeInQueryRange(solarTime)
		return cls(solarTime)


@dataclass(frozen=True)
class ChoiceItem:
	value: int
	label: str


@dataclass(frozen=True)
class SolarTermChoice:
	index: int
	termYear: int
	label: str
	solarTime: SolarTime


@dataclass(frozen=True)
class DisplaySection:
	label: str
	lines: list[str]


MIN_QUERY_LUNAR_YEAR = 1900
MAX_QUERY_LUNAR_YEAR = 2100


@cache
def getMinQuerySolarDay() -> SolarDay:
	return createLunarYear(MIN_QUERY_LUNAR_YEAR).get_first_month().get_first_day().get_solar_day()


@cache
def getMaxQuerySolarDay() -> SolarDay:
	lastLunarMonth: LunarMonth = createLunarYear(MAX_QUERY_LUNAR_YEAR).get_months()[-1]
	return lastLunarMonth.get_days()[-1].get_solar_day()


def _solarDayKey(solarDay: SolarDay) -> tuple[int, int, int]:
	return solarDay.get_year(), solarDay.get_month(), solarDay.get_day()


def isSolarDayInQueryRange(solarDay: SolarDay) -> bool:
	return (
		_solarDayKey(getMinQuerySolarDay()) <= _solarDayKey(solarDay) <= _solarDayKey(getMaxQuerySolarDay())
	)


def isSolarTimeInQueryRange(solarTime: SolarTime) -> bool:
	return isSolarDayInQueryRange(solarTime.get_solar_day())


def clampSolarTimeToQueryRange(solarTime: SolarTime) -> SolarTime:
	solarDay: SolarDay = solarTime.get_solar_day()
	if _solarDayKey(solarDay) < _solarDayKey(getMinQuerySolarDay()):
		minSolarDay: SolarDay = getMinQuerySolarDay()
		return createSolarTime(minSolarDay.get_year(), minSolarDay.get_month(), minSolarDay.get_day())
	if _solarDayKey(solarDay) > _solarDayKey(getMaxQuerySolarDay()):
		maxSolarDay: SolarDay = getMaxQuerySolarDay()
		return createSolarTime(
			maxSolarDay.get_year(),
			maxSolarDay.get_month(),
			maxSolarDay.get_day(),
			23,
			59,
			59,
		)
	return solarTime


def _validateSolarTimeInQueryRange(solarTime: SolarTime) -> None:
	if not isSolarTimeInQueryRange(solarTime):
		raise ValueError("query date is outside the supported leanCalendar range")


@cache
def getSolarYearChoices() -> list[ChoiceItem]:
	minSolarDay: SolarDay = getMinQuerySolarDay()
	maxSolarDay: SolarDay = getMaxQuerySolarDay()
	return [ChoiceItem(year, str(year)) for year in range(minSolarDay.get_year(), maxSolarDay.get_year() + 1)]


@cache
def getLunarYearChoices() -> list[ChoiceItem]:
	return [ChoiceItem(year, str(year)) for year in range(MIN_QUERY_LUNAR_YEAR, MAX_QUERY_LUNAR_YEAR + 1)]


@cache
def getSolarMonthChoices(year: int) -> list[ChoiceItem]:
	return [ChoiceItem(month, str(month)) for month in range(1, 13) if getSolarDayChoices(year, month)]


@cache
def getSolarDayChoices(year: int, month: int) -> list[ChoiceItem]:
	dayCount: int = createSolarDay(year, month, 1).get_solar_month().get_day_count()
	dayNumbers: list[int] = list(range(1, dayCount + 1))
	dayNumbers = [day for day in dayNumbers if isSolarDayInQueryRange(createSolarDay(year, month, day))]
	return [ChoiceItem(day, str(day)) for day in dayNumbers]


@cache
def getSolarHourChoices() -> list[ChoiceItem]:
	return [ChoiceItem(hour, f"{hour:02d}") for hour in range(24)]


@cache
def getLunarMonthChoices(year: int) -> list[ChoiceItem]:
	return [
		ChoiceItem(lunarMonth.get_month_with_leap(), lunarMonth.get_name())
		for lunarMonth in createLunarYear(year).get_months()
	]


@cache
def getLunarDayChoices(year: int, month: int) -> list[ChoiceItem]:
	lunarYear = createLunarYear(year)
	for candidate in lunarYear.get_months():
		if candidate.get_month_with_leap() == month:
			return [ChoiceItem(day.get_day(), day.get_name()) for day in candidate.get_days()]
	return []


@cache
def getLunarHourChoices(year: int, month: int, day: int) -> list[ChoiceItem]:
	lunarDay: LunarDay = createLunarHour(year, month, day, 0).get_lunar_day()
	return [ChoiceItem(lunarHour.get_hour(), lunarHour.get_name()) for lunarHour in lunarDay.get_hours()]


@cache
def getSolarTermChoices(year: int) -> list[SolarTermChoice]:
	choices: list[SolarTermChoice] = []
	for index in range(1, 25):
		solarTerm = createSolarTerm(year, index)
		solarTime: SolarTime = solarTerm.get_julian_day().get_solar_time()
		if not isSolarTimeInQueryRange(solarTime):
			continue
		choices.append(
			SolarTermChoice(
				index=solarTerm.get_index(),
				termYear=solarTerm.get_year(),
				# Translators: Solar term choice in the query controls. {term} is the solar term name,
				# and {dateTime} is its Gregorian date and time.
				label=_("{term} {dateTime}").format(
					term=solarTerm.get_name(),
					dateTime=formats.formatSolarDateTime(solarTime),
				),
				solarTime=solarTime,
			),
		)
	return choices


def buildSummary(query: CalendarQuery) -> str:
	solarTime: SolarTime = query.solarTime
	solarDay: SolarDay = solarTime.get_solar_day()
	lunarDay: LunarDay = solarDay.get_lunar_day()
	# Translators: Summary at the top of the leanCalendar dialog.
	return _("{dateTime} | Lunar {lunarDate} | {solarTermDay}").format(
		dateTime=formats.formatSolarDateHour(solarTime),
		lunarDate=formats.formatLunarDate(lunarDay),
		solarTermDay=formats.formatSolarTermDay(solarDay),
	)


def _formatFourPillars(lunarDay: LunarDay, lunarHour: LunarHour) -> str:
	sixtyCycleDay = lunarDay.get_sixty_cycle_day()
	return formats.formatYearMonthDayHour(
		str(sixtyCycleDay.get_year()),
		str(sixtyCycleDay.get_month()),
		str(sixtyCycleDay.get_sixty_cycle()),
		str(lunarHour.get_sixty_cycle()),
	)


def _formatFullMoonTime(lunarMonth: LunarMonth) -> str:
	fullMoon = createPhase(lunarMonth.get_year(), lunarMonth.get_month_with_leap(), 4)
	# Translators: Report item for the full moon time. {time} is the time of day.
	return _("full moon at {time}").format(time=formats.formatSolarTimeOnly(fullMoon.get_solar_time()))


def _formatYi(lunarDay: LunarDay) -> str | None:
	recommends: list[str] = [str(recommend) for recommend in lunarDay.get_recommends()]
	if not recommends:
		return None
	# Translators: Huangli Yi item, listing suitable activities for the day.
	return _("Yi {items}").format(items=formats.joinLimitedParts(recommends, limit=30))


def _formatJi(lunarDay: LunarDay) -> str | None:
	avoids: list[str] = [str(avoid) for avoid in lunarDay.get_avoids()]
	if not avoids:
		return None
	# Translators: Huangli Ji item, listing activities to avoid for the day.
	return _("Ji {items}").format(items=formats.joinLimitedParts(avoids, limit=30))


def _formatCardinalDirection(directionName: str) -> str:
	if directionName in {"东", "南", "西", "北"}:
		# Translators: Cardinal direction. {direction} is one of east, south, west, or north.
		return _("due {direction}").format(direction=directionName)
	return directionName


def _formatChongSha(lunarDay: LunarDay) -> str:
	sixtyCycle = lunarDay.get_sixty_cycle()
	earthBranch = sixtyCycle.get_earth_branch()
	oppositeBranch = earthBranch.get_opposite()
	oppositeStem = sixtyCycle.get_heaven_stem().next(4)
	oppositeCycle = f"{oppositeStem}{oppositeBranch}"
	# Translators: Huangli Chong Sha item.
	# {dayZodiac} and {targetZodiac} are Chinese zodiac names, {targetCycle} is a sexagenary cycle,
	# and {direction} is a Sha direction.
	return _("{dayZodiac} day chong {targetZodiac} ({targetCycle}), sha {direction}").format(
		dayZodiac=earthBranch.get_zodiac(),
		targetZodiac=oppositeBranch.get_zodiac(),
		targetCycle=oppositeCycle,
		direction=earthBranch.get_ominous(),
	)


def _formatFiveElements(lunarDay: LunarDay) -> str:
	sixtyCycle = lunarDay.get_sixty_cycle()
	# Translators: Almanac five elements item.
	# {stemElement}, {branchElement}, and {sound} are Chinese five-element or Na Yin names.
	return _("five elements {stemElement}{branchElement} {sound}").format(
		stemElement=sixtyCycle.get_heaven_stem().get_element(),
		branchElement=sixtyCycle.get_earth_branch().get_element(),
		sound=sixtyCycle.get_sound(),
	)


def _formatTwentyEightStar(lunarDay: LunarDay) -> str:
	star = lunarDay.get_twenty_eight_star()
	# Translators: TwentyEightStar detail item, matching tyme4py's TwentyEightStar type.
	# {zone}, {star}, {sevenStar}, {animal}, and {luck} are Chinese astrology names.
	return _("{zone} {star}{sevenStar}{animal} {luck}").format(
		zone=star.get_zone(),
		star=star,
		sevenStar=star.get_seven_star(),
		animal=star.get_animal(),
		luck=star.get_luck(),
	)


def _formatDeityDirections(lunarDay: LunarDay) -> str:
	heavenStem = lunarDay.get_sixty_cycle().get_heaven_stem()
	# Translators: Huangli deity direction item. Cai Shen, Xi Shen, and Fu Shen are deity names.
	return _("Cai Shen {caiShen}, Xi Shen {xiShen}, Fu Shen {fuShen}").format(
		caiShen=_formatCardinalDirection(str(heavenStem.get_wealth_direction())),
		xiShen=_formatCardinalDirection(str(heavenStem.get_joy_direction())),
		fuShen=_formatCardinalDirection(str(heavenStem.get_mascot_direction())),
	)


def _formatTwelveStar(lunarDay: LunarDay) -> str:
	twelveStar = lunarDay.get_twelve_star()
	ecliptic = twelveStar.get_ecliptic()
	# Translators: Huangdao/Heidao TwelveStar item, matching tyme4py's TwelveStar type.
	return _("TwelveStar {twelveStar}-{ecliptic}-{luck}").format(
		twelveStar=twelveStar,
		ecliptic=ecliptic,
		luck=ecliptic.get_luck(),
	)


def _formatGodList(lunarDay: LunarDay, *, isLucky: bool) -> str | None:
	luckIndex: int = 0 if isLucky else 1
	gods: list[str] = [str(god) for god in lunarDay.get_gods() if god.get_luck().get_index() == luckIndex]
	if not gods:
		return None
	if isLucky:
		# Translators: Huangli Ji Shen item.
		return _("Ji Shen {gods}").format(gods=formats.joinLimitedParts(gods, limit=12))
	# Translators: Huangli Xiong Shen item.
	return _("Xiong Shen {gods}").format(gods=formats.joinLimitedParts(gods, limit=12))


def _formatLunarHourLuck(lunarDay: LunarDay) -> str:
	hourItems: list[str] = [
		f"{lunarHour.get_sixty_cycle()}{lunarHour.get_twelve_star().get_ecliptic().get_luck()}"
		for lunarHour in lunarDay.get_hours()[:12]
	]
	# Translators: LunarHour luck item, matching tyme4py's LunarHour type.
	return _("LunarHour luck {items}").format(items=formats.joinParts(hourItems))


def _buildGregorianLines(solarTime: SolarTime) -> list[str]:
	solarDay: SolarDay = solarTime.get_solar_day()
	dayStatus: str | None = formats.getGregorianHolidaySummary(solarTime) or formats.getGregorianDayStatus(
		solarDay,
	)
	summaryParts: list[str] = [
		formats.formatSolarDateHour(solarTime),
		formats.formatWeekday(solarDay),
	]
	if dayStatus:
		summaryParts.append(dayStatus)
	summaryParts.append(formats.formatWesternZodiacSign(solarDay))
	return [
		formats.joinParts(summaryParts),
		formats.joinParts(
			[
				formats.formatYearDay(solarDay),
				formats.formatWeekNumber(solarDay),
				formats.formatQuarter(solarDay),
				formats.formatSolarMonthDayCount(solarDay),
			],
		),
	]


def _buildLunarLines(solarTime: SolarTime) -> list[str]:
	solarDay: SolarDay = solarTime.get_solar_day()
	lunarDay: LunarDay = solarDay.get_lunar_day()
	lunarMonth: LunarMonth = lunarDay.get_lunar_month()
	lunarHour: LunarHour = solarTime.get_lunar_hour()
	zodiacText: str = str(lunarMonth.get_lunar_year().get_sixty_cycle().get_earth_branch().get_zodiac())
	dateParts: list[str] = [
		formats.formatLunarDate(lunarDay),
		formats.formatLunarMonthSize(lunarMonth),
		lunarHour.get_name(),
		# Translators: Report item for the Chinese zodiac. {zodiac} is a zodiac animal name.
		_("Chinese zodiac {zodiac}").format(zodiac=zodiacText),
	]
	lunarFestivalSummary: str | None = formats.getLunarFestivalSummary(solarTime)
	if lunarFestivalSummary:
		dateParts.append(lunarFestivalSummary)
	return [
		formats.joinParts(dateParts),
		_formatFourPillars(lunarDay, lunarHour),
	]


def _buildSolarTermLines(solarTime: SolarTime) -> list[str]:
	solarDay: SolarDay = solarTime.get_solar_day()
	currentTerm = solarTime.get_term()
	previousJie = currentTerm if currentTerm.is_jie() else currentTerm.next(-1)
	nextJie = previousJie.next(2)
	nextJieTime: SolarTime = nextJie.get_julian_day().get_solar_time()
	phenologyDay = solarDay.get_phenology_day()
	threePhenology = phenologyDay.get_phenology().get_three_phenology()
	termParts: list[str] = [
		formats.formatSolarTermCompact(previousJie),
		formats.formatSolarTermCompact(nextJie),
		# Translators: Report item for time remaining until the next solar term.
		_("until {term} {remaining}").format(
			term=nextJie.get_name(),
			remaining=formats.formatSecondsUntil(nextJieTime.subtract(solarTime)),
		),
	]
	phenologyParts: list[str] = [
		formats.formatSolarTermDay(solarDay),
		f"{threePhenology} {phenologyDay}",
	]
	phenologyParts.extend(formats.getTraditionalPeriodSummaries(solarDay))
	return [formats.joinParts(phenologyParts), formats.joinParts(termParts)]


def _buildAlmanacLines(solarTime: SolarTime) -> list[str]:
	solarDay: SolarDay = solarTime.get_solar_day()
	lunarDay: LunarDay = solarDay.get_lunar_day()
	lunarMonth: LunarMonth = lunarDay.get_lunar_month()
	coreParts: list[str] = [
		_formatFullMoonTime(lunarMonth),
		formats.getPhaseDaySummary(solarDay),
		# Translators: Jianchu duty item, matching tyme4py's Duty type.
		_("Jianchu duty {duty}").format(duty=lunarDay.get_duty()),
		_formatTwelveStar(lunarDay),
	]
	starCoreParts: list[str] = [
		_formatChongSha(lunarDay),
		_formatFiveElements(lunarDay),
		# Translators: TwentyEightStar item, matching tyme4py's TwentyEightStar type.
		_("TwentyEightStar {twentyEightStar}").format(
			twentyEightStar=_formatTwentyEightStar(lunarDay),
		),
	]
	starExtraParts: list[str] = [
		# Translators: NineStar item, matching tyme4py's NineStar type.
		_("NineStar {star}").format(star=solarDay.get_nine_star()),
		# Translators: Report item for Xiao Liu Ren.
		_("Xiao Liu Ren {minorRen}").format(minorRen=lunarDay.get_minor_ren()),
	]
	deityParts: list[str] = [
		# Translators: FetusDay item, matching tyme4py's FetusDay type.
		_("FetusDay {fetusDay}").format(fetusDay=lunarDay.get_fetus_day()),
		_formatDeityDirections(lunarDay),
	]
	# Translators: PengZu Baiji item, matching tyme4py's PengZu type.
	pengZuLine: str = _("PengZu Baiji {pengZu}").format(
		pengZu=lunarDay.get_sixty_cycle().get_peng_zu(),
	)
	godLines: list[str] = [
		line
		for line in (
			_formatGodList(lunarDay, isLucky=True),
			_formatGodList(lunarDay, isLucky=False),
		)
		if line
	]
	activityParts: list[str] = [part for part in (_formatYi(lunarDay), _formatJi(lunarDay)) if part]
	lines: list[str] = [
		formats.joinParts(coreParts),
		formats.joinParts(starCoreParts),
		formats.joinParts(starExtraParts),
		"",
		formats.joinParts(deityParts),
		pengZuLine,
	]
	if godLines:
		lines.append("")
		lines.extend(godLines)
	if activityParts:
		lines.append("")
		lines.extend(activityParts)
	lines.append("")
	lines.append(_formatLunarHourLuck(lunarDay))
	return lines


def buildBasicSections(query: CalendarQuery) -> list[DisplaySection]:
	solarTime: SolarTime = query.solarTime
	return [
		# Translators: Section title in the leanCalendar dialog result.
		DisplaySection(_("Gregorian"), _buildGregorianLines(solarTime)),
		# Translators: Section title in the leanCalendar dialog result.
		DisplaySection(_("Lunar"), _buildLunarLines(solarTime)),
		# Translators: Section title in the leanCalendar dialog result.
		DisplaySection(_("Solar Terms and Phenology"), _buildSolarTermLines(solarTime)),
		# Translators: Section title in the leanCalendar dialog result.
		DisplaySection(_("Almanac"), _buildAlmanacLines(solarTime)),
	]


def buildBasicText(query: CalendarQuery) -> str:
	blocks: list[str] = []
	for section in buildBasicSections(query):
		if not section.lines:
			continue
		blockLines: list[str] = [section.label]
		blockLines.extend(section.lines)
		blocks.append("\n".join(blockLines))
	return "\n\n".join(blocks)
