# A part of leanCalendar
# Copyright (C) 2026 Cary-rowen <manchen_0528@outlook.com>
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

from __future__ import annotations

from datetime import datetime

import addonHandler

from . import formats
from .tymeAccess import createPhase, getSolarTime

addonHandler.initTranslation()


def getBriefLeanCalendarMessage(now: datetime | None = None) -> str:
	if now is None:
		now = datetime.now()
	solarTime = getSolarTime(now)
	solarDay = solarTime.get_solar_day()
	lunarDay = solarDay.get_lunar_day()
	lunarMonth = lunarDay.get_lunar_month()
	lunarHour = solarTime.get_lunar_hour()
	sixtyCycleDay = lunarDay.get_sixty_cycle_day()
	phenologyDay = solarDay.get_phenology_day()
	threePhenology = phenologyDay.get_phenology().get_three_phenology()
	# Translators: Four pillars report. {year}, {month}, {day}, and {hour} are sexagenary cycle names.
	sixtyCycleText: str = _("{year} year, {month} month, {day} day, {hour} hour").format(
		year=sixtyCycleDay.get_year(),
		month=sixtyCycleDay.get_month(),
		day=sixtyCycleDay.get_sixty_cycle(),
		hour=lunarHour.get_sixty_cycle(),
	)
	parts: list[str] = [
		formats.formatLunarDate(lunarDay),
		formats.formatLunarMonthSize(lunarMonth),
		lunarHour.get_name(),
		sixtyCycleText,
		formats.formatSolarTermDay(solarDay),
		f"{threePhenology} {phenologyDay}",
	]
	lunarFestivalSummary: str | None = formats.getLunarFestivalSummary(solarTime)
	if lunarFestivalSummary:
		parts.append(lunarFestivalSummary)
	nextSolarTermSummary: str | None = formats.getBriefNextSolarTermSummary(solarTime)
	if nextSolarTermSummary:
		parts.append(nextSolarTermSummary)
	return formats.joinParts(parts)


def getDetailedLeanCalendarMessage(now: datetime | None = None) -> str:
	if now is None:
		now = datetime.now()
	solarTime = getSolarTime(now)
	solarDay = solarTime.get_solar_day()
	lunarDay = solarDay.get_lunar_day()
	lunarMonth = lunarDay.get_lunar_month()
	currentTerm = solarTime.get_term()
	previousJie = currentTerm if currentTerm.is_jie() else currentTerm.next(-1)
	nextJie = previousJie.next(2)
	nextJieTime = nextJie.get_julian_day().get_solar_time()
	fullMoon = createPhase(lunarMonth.get_year(), lunarMonth.get_month_with_leap(), 4)
	zodiacText: str = str(lunarMonth.get_lunar_year().get_sixty_cycle().get_earth_branch().get_zodiac())
	parts: list[str] = [
		formats.formatSolarTermCompact(previousJie),
		formats.formatSolarTermCompact(nextJie),
		# Translators: Report item for time remaining until the next solar term.
		_("until {term} {remaining}").format(
			term=nextJie.get_name(),
			remaining=formats.formatSecondsUntil(nextJieTime.subtract(solarTime)),
		),
		# Translators: Report item for the Chinese zodiac. {zodiac} is a zodiac animal name.
		_("Chinese zodiac {zodiac}").format(zodiac=zodiacText),
		# Translators: Report item for the full moon time. {time} is the time of day.
		_("full moon at {time}").format(time=formats.formatSolarTimeOnly(fullMoon.get_solar_time())),
		formats.getPhaseDaySummary(solarDay),
		# Translators: Jianchu duty item, matching tyme4py's Duty type.
		_("Jianchu duty {duty}").format(duty=lunarDay.get_duty()),
	]
	parts.extend(formats.getTraditionalPeriodSummaries(solarDay))
	return formats.joinParts(parts)


def getBriefGregorianMessage(now: datetime | None = None) -> str:
	if now is None:
		now = datetime.now()
	return formats.formatClockTime(getSolarTime(now))


def getDetailedGregorianMessage(now: datetime | None = None) -> str:
	if now is None:
		now = datetime.now()
	solarTime = getSolarTime(now)
	solarDay = solarTime.get_solar_day()
	parts: list[str] = [
		formats.formatSolarDate(solarDay),
		formats.formatWeekday(solarDay),
		formats.formatYearDay(solarDay),
		formats.formatWeekNumber(solarDay),
		formats.formatQuarter(solarDay),
		formats.formatSolarMonthDayCount(solarDay),
	]
	gregorianHolidaySummary: str | None = formats.getGregorianHolidaySummary(solarTime)
	if gregorianHolidaySummary:
		parts.append(gregorianHolidaySummary)
	gregorianDayStatus: str | None = formats.getGregorianDayStatus(solarDay)
	if gregorianDayStatus:
		parts.append(gregorianDayStatus)
	parts.append(formats.formatWesternZodiacSign(solarDay))
	return formats.joinParts(parts)
