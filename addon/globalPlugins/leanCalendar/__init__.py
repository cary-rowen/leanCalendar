# A part of leanCalendar
# Copyright (C) 2026 Cary-rowen <manchen_0528@outlook.com>
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

from __future__ import annotations

import addonHandler
import gui
import globalPluginHandler
from inputCore import InputGesture
from logHandler import log
from scriptHandler import getLastScriptRepeatCount, script
import ui
import wx

from .dialog import openCalendarDialog
from .messages import (
	getBriefGregorianMessage,
	getBriefLeanCalendarMessage,
	getDetailedGregorianMessage,
	getDetailedLeanCalendarMessage,
)

addonHandler.initTranslation()


def _openCalendarDialog() -> None:
	def showDialog() -> None:
		gui.mainFrame.prePopup()
		try:
			openCalendarDialog(gui.mainFrame)
		except Exception:
			log.exception("Error opening leanCalendar dialog")
			# Translators: Error message shown when the leanCalendar dialog cannot be opened.
			ui.message(_("Unable to open leanCalendar."))
		finally:
			gui.mainFrame.postPopup()

	wx.CallAfter(showDialog)


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	# Translators: The name of the category for this add-on's scripts in the Input Gestures dialog.
	scriptCategory = _("leanCalendar")

	@script(
		# Translators: Describes a command in Input Help mode and the Input Gestures dialog.
		description=_(
			"Report Chinese lunar calendar information. Press once for concise lunar date and solar term "
			"details, press twice for additional lunar context, or press three times to open the "
			"leanCalendar query dialog"
		),
		gesture="kb:NVDA+f11",
		speakOnDemand=True,
	)
	def script_reportCurrentLunarDateAndSolarTerm(self, gesture: InputGesture) -> None:
		try:
			repeatCount: int = getLastScriptRepeatCount()
			if repeatCount == 0:
				ui.message(getBriefLeanCalendarMessage())
			elif repeatCount == 1:
				ui.message(getDetailedLeanCalendarMessage())
			else:
				_openCalendarDialog()
		except Exception:
			log.exception("Error reporting lunar date and solar term")
			# Translators: Error message shown when lunar date or solar term calculation fails.
			ui.message(_("Unable to calculate the lunar date and solar term."))

	@script(
		# Translators: Describes a command in Input Help mode and the Input Gestures dialog.
		description=_(
			"Report Gregorian date and time information. Press once for the current time, or press twice "
			"for Gregorian date details"
		),
		gesture="kb:NVDA+f12",
		speakOnDemand=True,
	)
	def script_reportCurrentGregorianTimeAndDate(self, gesture: InputGesture) -> None:
		try:
			if getLastScriptRepeatCount() == 0:
				ui.message(getBriefGregorianMessage())
			else:
				ui.message(getDetailedGregorianMessage())
		except Exception:
			log.exception("Error reporting Gregorian time and calendar details")
			# Translators: Error message shown when Gregorian time or calendar calculation fails.
			ui.message(_("Unable to calculate the Gregorian time and calendar details."))
