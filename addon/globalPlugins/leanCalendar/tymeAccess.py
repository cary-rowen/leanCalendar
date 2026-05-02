# A part of leanCalendar
# Copyright (C) 2026 Cary-rowen <manchen_0528@outlook.com>
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

from __future__ import annotations

from datetime import datetime
import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from tyme4py.culture import Phase
	from tyme4py.lunar import LunarHour, LunarYear
	from tyme4py.solar import SolarDay, SolarTerm, SolarTime


_ADDON_PATH: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_TYME4PY_PATH: str = os.path.join(_ADDON_PATH, "tyme4py")


def ensureTyme4PyPath() -> None:
	if _TYME4PY_PATH not in sys.path:
		sys.path.insert(0, _TYME4PY_PATH)


def createSolarTime(
	year: int,
	month: int,
	day: int,
	hour: int = 0,
	minute: int = 0,
	second: int = 0,
) -> SolarTime:
	ensureTyme4PyPath()
	from tyme4py.solar import SolarTime

	return SolarTime.from_ymd_hms(year, month, day, hour, minute, second)


def createSolarDay(year: int, month: int, day: int) -> SolarDay:
	ensureTyme4PyPath()
	from tyme4py.solar import SolarDay

	return SolarDay.from_ymd(year, month, day)


def createLunarHour(
	year: int,
	month: int,
	day: int,
	hour: int = 0,
	minute: int = 0,
	second: int = 0,
) -> LunarHour:
	ensureTyme4PyPath()
	from tyme4py.lunar import LunarHour

	return LunarHour.from_ymd_hms(year, month, day, hour, minute, second)


def createLunarYear(year: int) -> LunarYear:
	ensureTyme4PyPath()
	from tyme4py.lunar import LunarYear

	return LunarYear.from_year(year)


def createSolarTerm(year: int, index: int) -> SolarTerm:
	ensureTyme4PyPath()
	from tyme4py.solar import SolarTerm

	return SolarTerm.from_index(year, index)


def createPhase(year: int, month: int, index: int) -> Phase:
	ensureTyme4PyPath()
	from tyme4py.culture import Phase

	return Phase.from_index(year, month, index)


def getSolarTime(now: datetime) -> SolarTime:
	return createSolarTime(
		now.year,
		now.month,
		now.day,
		now.hour,
		now.minute,
		now.second,
	)
