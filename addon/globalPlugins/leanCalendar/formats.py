# A part of leanCalendar
# Copyright (C) 2026 Cary-rowen <manchen_0528@outlook.com>
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

from __future__ import annotations

from typing import TYPE_CHECKING

import addonHandler

addonHandler.initTranslation()

if TYPE_CHECKING:
	from tyme4py.lunar import LunarDay, LunarMonth
	from tyme4py.solar import SolarDay, SolarTerm, SolarTime


def formatLunarDate(lunarDay: LunarDay) -> str:
	lunarMonth: LunarMonth = lunarDay.get_lunar_month()
	return f"{lunarMonth.get_name()} {lunarDay.get_name()}"


def formatLunarDateCompact(lunarDay: LunarDay) -> str:
	lunarMonth: LunarMonth = lunarDay.get_lunar_month()
	return f"{lunarMonth.get_name()}{lunarDay.get_name()}"


def formatLunarMonthSize(lunarMonth: LunarMonth) -> str:
	month: str = lunarMonth.get_name()
	if lunarMonth.get_day_count() == 30:
		# Translators: Reports a 30-day lunar month. {month} is the lunar month name.
		return _("{month} long").format(month=month)
	# Translators: Reports a 29-day lunar month. {month} is the lunar month name.
	return _("{month} short").format(month=month)


def formatSolarTimeOnly(solarTime: SolarTime) -> str:
	return f"{solarTime.get_hour():02d}:{solarTime.get_minute():02d}:{solarTime.get_second():02d}"


def formatYearMonthDayHour(year: str, month: str, day: str, hour: str) -> str:
	# Translators: Compact year, month, day, and hour report.
	return _("{year} year {month} month {day} day {hour} hour").format(
		year=year,
		month=month,
		day=day,
		hour=hour,
	)


def formatClockTime(solarTime: SolarTime) -> str:
	# Translators: Current time. {hour}, {minute}, and {second} are numbers.
	return _("{hour} hour {minute} minute {second} second").format(
		hour=solarTime.get_hour(),
		minute=solarTime.get_minute(),
		second=solarTime.get_second(),
	)


def formatSolarDate(solarDay: SolarDay) -> str:
	# Translators: Gregorian date. {year}, {month}, and {day} are numbers.
	return _("{year}-{month}-{day}").format(
		year=solarDay.get_year(),
		month=solarDay.get_month(),
		day=solarDay.get_day(),
	)


def formatSolarDateHour(solarTime: SolarTime) -> str:
	# Translators: Gregorian date and hour. {year}, {month}, {day}, and {hour} are numbers.
	return _("{year}-{month}-{day} {hour}:00").format(
		year=solarTime.get_year(),
		month=solarTime.get_month(),
		day=solarTime.get_day(),
		hour=solarTime.get_hour(),
	)


def formatSolarDateTime(solarTime: SolarTime) -> str:
	return f"{solarTime.get_year():04d}-{solarTime.get_month():02d}-{solarTime.get_day():02d} {formatSolarTimeOnly(solarTime)}"


def formatSolarTermCompact(solarTerm: SolarTerm) -> str:
	solarTime: SolarTime = solarTerm.get_julian_day().get_solar_time()
	return f"{formatLunarDateCompact(solarTime.get_solar_day().get_lunar_day())}{solarTerm.get_name()}"


def formatSolarMonthDayCount(solarDay: SolarDay) -> str:
	# Translators: Gregorian month day count. {month} and {days} are numbers.
	return _("{month} has {days} days").format(
		month=solarDay.get_month(),
		days=solarDay.get_solar_month().get_day_count(),
	)


def formatWeekday(solarDay: SolarDay) -> str:
	# Translators: Gregorian weekday report. {weekday} is a weekday name or number.
	return _("weekday {weekday}").format(weekday=solarDay.get_week())


def formatYearDay(solarDay: SolarDay) -> str:
	# Translators: Gregorian day-of-year report. {dayNumber} is a number.
	return _("year day {dayNumber}").format(dayNumber=solarDay.get_index_in_year() + 1)


def formatWeekNumber(solarDay: SolarDay) -> str:
	weekNumber: int = solarDay.get_solar_week(1).get_index_in_year() + 1
	# Translators: Gregorian week-of-year report. {weekNumber} is a number.
	return _("week {weekNumber}").format(weekNumber=weekNumber)


def formatQuarter(solarDay: SolarDay) -> str:
	quarter: int = (solarDay.get_month() - 1) // 3 + 1
	# Translators: Gregorian quarter report. {quarter} is a number from 1 to 4.
	return _("quarter {quarter}").format(quarter=quarter)


def formatWesternZodiacSign(solarDay: SolarDay) -> str:
	# Translators: Western zodiac sign report. {sign} is a Western zodiac sign name.
	return _("Western zodiac sign {sign}").format(sign=solarDay.get_constellation())


def formatSecondsUntil(seconds: int) -> str:
	if seconds <= 0:
		# Translators: Remaining time when the target time has already arrived.
		return _("now")
	days: int
	remainingSeconds: int
	days, remainingSeconds = divmod(seconds, 86400)
	hours: int
	hours, remainingSeconds = divmod(remainingSeconds, 3600)
	minutes: int = remainingSeconds // 60
	if days:
		# Translators: Remaining time until the next solar term. {days} and {hours} are numbers.
		return _("{days} days {hours} hours").format(days=days, hours=hours)
	if hours:
		# Translators: Remaining time until the next solar term. {hours} and {minutes} are numbers.
		return _("{hours} hours {minutes} minutes").format(hours=hours, minutes=minutes)
	if not minutes:
		# Translators: Remaining time until the next solar term when less than one minute remains.
		return _("less than 1 minute")
	# Translators: Remaining time until the next solar term. {minutes} is a number.
	return _("{minutes} minutes").format(minutes=minutes)


def formatBriefSecondsUntil(seconds: int) -> str:
	if seconds < 86400:
		return formatSecondsUntil(seconds)
	days: int = seconds // 86400
	# Translators: Remaining whole days until the next solar term. {days} is a number.
	return _("{days} days").format(days=days)


def getLunarFestivalSummary(solarTime: SolarTime) -> str | None:
	lunarFestival = solarTime.get_solar_day().get_lunar_day().get_festival()
	return lunarFestival.get_name() if lunarFestival is not None else None


def getGregorianHolidaySummary(solarTime: SolarTime) -> str | None:
	solarDay: SolarDay = solarTime.get_solar_day()
	names: list[str] = []
	solarFestival = solarDay.get_festival()
	legalHoliday = solarDay.get_legal_holiday()
	if legalHoliday is not None:
		if legalHoliday.is_work():
			# Translators: Reports a legal holiday make-up work day. {holiday} is the holiday name.
			legalHolidayName: str = _("{holiday} work").format(holiday=legalHoliday.get_name())
		else:
			# Translators: Reports a legal holiday day off. {holiday} is the holiday name.
			legalHolidayName = _("{holiday} off").format(holiday=legalHoliday.get_name())
		if legalHolidayName not in names:
			names.append(legalHolidayName)
	if solarFestival is not None and (
		legalHoliday is None or solarFestival.get_name() != legalHoliday.get_name()
	):
		names.append(solarFestival.get_name())
	return " ".join(names) if names else None


def getBriefNextSolarTermSummary(solarTime: SolarTime) -> str | None:
	nextSolarTerm = solarTime.get_term().next(1)
	secondsUntilNextTerm: int = nextSolarTerm.get_julian_day().get_solar_time().subtract(solarTime)
	if secondsUntilNextTerm > 7 * 86400:
		return None
	# Translators: Report item for time remaining until the next solar term.
	return _("until {term} {remaining}").format(
		term=nextSolarTerm.get_name(),
		remaining=formatBriefSecondsUntil(secondsUntilNextTerm),
	)


def getTraditionalPeriodSummaries(solarDay: SolarDay) -> list[str]:
	periods: list[str] = []
	for period in (solarDay.get_dog_day(), solarDay.get_nine_day(), solarDay.get_plum_rain_day()):
		if period is not None:
			periods.append(str(period))
	return periods


def getPhaseDaySummary(solarDay: SolarDay) -> str:
	# Translators: Report item for the current moon phase day.
	return _("moon phase {phaseDay}").format(phaseDay=solarDay.get_phase_day())


def getGregorianDayStatus(solarDay: SolarDay) -> str | None:
	if solarDay.get_legal_holiday() is not None:
		return None
	if solarDay.get_week().get_index() in (0, 6):
		# Translators: Gregorian day status.
		return _("weekend")
	# Translators: Gregorian day status.
	return _("workday")


def joinParts(parts: list[str]) -> str:
	# Translators: Separator between calendar report items.
	return _(", ").join(parts)


def joinLimitedParts(parts: list[str], limit: int = 5) -> str:
	visibleParts: list[str] = parts[:limit]
	text: str = joinParts(visibleParts)
	if len(parts) > limit:
		return f"{text}..."
	return text


def formatSolarTermDay(solarDay: SolarDay) -> str:
	termDay = solarDay.get_term_day()
	# Translators: Current solar term day report. {term} is a solar term name.
	return _("{term} day {dayNumber}").format(
		term=termDay.get_solar_term().get_name(),
		dayNumber=termDay.get_day_index() + 1,
	)
