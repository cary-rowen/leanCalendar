# A part of leanCalendar
# Copyright (C) 2026 Cary-rowen <manchen_0528@outlook.com>
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

import addonHandler
import wx

from gui import guiHelper, nvdaControls
from logHandler import log
import ui

from .data import (
	CalendarQuery,
	ChoiceItem,
	SolarTermChoice,
	buildBasicText,
	buildSummary,
	getLunarDayChoices,
	getLunarHourChoices,
	getLunarMonthChoices,
	getLunarYearChoices,
	getSolarDayChoices,
	getSolarHourChoices,
	getSolarMonthChoices,
	getSolarTermChoices,
	getSolarYearChoices,
)

addonHandler.initTranslation()

QUERY_REFRESH_DELAY_MS = 80
MIN_DIALOG_SIZE = (760, 460)
INITIAL_DIALOG_SIZE = (820, 560)
DISPLAY_MARGIN = (40, 40)
_calendarDialog: LeanCalendarDialog | None = None


def openCalendarDialog(parent: wx.Window) -> None:
	global _calendarDialog
	if _calendarDialog and not _calendarDialog.IsBeingDeleted():
		_calendarDialog.Raise()
		_calendarDialog._focusTabs()
		return
	_calendarDialog = LeanCalendarDialog(parent)
	_calendarDialog.Show()
	_calendarDialog._focusTabs()


class LeanCalendarDialog(nvdaControls.DPIScaledDialog):
	mainSizer: wx.BoxSizer
	settingsSizer: wx.BoxSizer
	notebook: wx.Notebook
	basicPanel: wx.Panel
	summaryCtrl: wx.StaticText
	resultCtrl: wx.TextCtrl
	solarYearCtrl: wx.ComboBox
	solarMonthCtrl: wx.Choice
	solarDayCtrl: wx.Choice
	solarHourCtrl: wx.Choice
	todayButton: wx.Button
	lunarYearCtrl: wx.ComboBox
	lunarMonthCtrl: wx.Choice
	lunarDayCtrl: wx.Choice
	lunarHourCtrl: wx.Choice
	solarTermCtrl: wx.Choice

	def __init__(self, parent: wx.Window):
		# Translators: Title of the leanCalendar dialog.
		title: str = _("leanCalendar")
		self._query = CalendarQuery.fromDatetime(datetime.now())
		self._isRefreshing = False
		self._solarMonthChoices: list[ChoiceItem] = []
		self._solarDayChoices: list[ChoiceItem] = []
		self._lunarMonthChoices: list[ChoiceItem] = []
		self._lunarDayChoices: list[ChoiceItem] = []
		self._lunarHourChoices: list[ChoiceItem] = []
		self._solarTermChoices: list[SolarTermChoice] = []
		self._choiceItemsById: dict[int, list[ChoiceItem]] = {}
		self._solarTermItems: tuple[SolarTermChoice, ...] = ()
		self._pendingQueryFactory: Callable[[], CalendarQuery] | None = None
		self._refreshCall: wx.CallLater | None = None
		super().__init__(
			parent,
			title=title,
			style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX,
		)
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.settingsSizer = wx.BoxSizer(wx.VERTICAL)
		self._makeSettings(self.settingsSizer)
		self.mainSizer.Add(
			self.settingsSizer,
			border=guiHelper.BORDER_FOR_DIALOGS,
			flag=wx.ALL | wx.EXPAND,
			proportion=1,
		)
		self.SetSizer(self.mainSizer)
		self.mainSizer.Fit(self)
		self.SetMinSize(self.scaleSize(MIN_DIALOG_SIZE))
		self._setInitialSize()
		self.Bind(wx.EVT_CLOSE, self._onClose)
		self.Bind(wx.EVT_WINDOW_DESTROY, self._onDestroy)
		self.Bind(wx.EVT_CHAR_HOOK, self._onCharHook)
		self.CentreOnScreen()

	def _makeSettings(self, settingsSizer: wx.BoxSizer) -> None:
		self.notebook = wx.Notebook(self)
		self.basicPanel = wx.Panel(self.notebook)
		self._makeBasicPage(self.basicPanel)
		# Translators: Basic tab in the leanCalendar dialog.
		self.notebook.AddPage(self.basicPanel, _("Basic"))
		settingsSizer.Add(self.notebook, flag=wx.EXPAND, proportion=1)
		wx.CallAfter(self._refreshControls)

	def _focusTabs(self) -> None:
		wx.CallAfter(self.notebook.SetFocus)

	def _setInitialSize(self) -> None:
		width: int
		height: int
		width, height = self.scaleSize(INITIAL_DIALOG_SIZE)
		minSize: wx.Size = self.GetMinSize()
		displayCount: int = wx.Display.GetCount()
		if displayCount:
			displayIndex: int = wx.Display.GetFromWindow(self)
			if displayIndex == wx.NOT_FOUND:
				displayIndex = 0
			workArea: wx.Rect = wx.Display(displayIndex).GetClientArea()
			marginWidth: int
			marginHeight: int
			marginWidth, marginHeight = self.scaleSize(DISPLAY_MARGIN)
			width = min(width, max(minSize.GetWidth(), workArea.GetWidth() - marginWidth))
			height = min(height, max(minSize.GetHeight(), workArea.GetHeight() - marginHeight))
		self.SetSize((width, height))

	def _makeBasicPage(self, panel: wx.Panel) -> None:
		sizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)
		panel.SetSizer(sizer)

		self.summaryCtrl = wx.StaticText(panel, style=wx.ST_NO_AUTORESIZE)
		sizer.Add(self.summaryCtrl, flag=wx.EXPAND)
		sizer.AddSpacer(guiHelper.SPACE_BETWEEN_VERTICAL_DIALOG_ITEMS)

		self._makeQueryControls(panel, sizer)
		sizer.AddSpacer(guiHelper.SPACE_BETWEEN_VERTICAL_DIALOG_ITEMS)

		# Translators: Label for the Basic tab result.
		sizer.Add(wx.StaticText(panel, label=_("&Result:")), flag=wx.EXPAND)
		self.resultCtrl = wx.TextCtrl(
			panel,
			style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2,
		)
		self.resultCtrl.SetMinSize(self.scaleSize((720, 220)))
		sizer.Add(self.resultCtrl, flag=wx.EXPAND, proportion=1)

	def _makeQueryControls(self, parent: wx.Window, parentSizer: wx.BoxSizer) -> None:
		# Translators: Label for the calendar query controls group.
		queryBox: wx.StaticBoxSizer = wx.StaticBoxSizer(wx.VERTICAL, parent, _("Query"))
		queryParent: wx.StaticBox = queryBox.GetStaticBox()
		querySizer: guiHelper.BoxSizerHelper = guiHelper.BoxSizerHelper(queryParent, wx.VERTICAL)

		gregorianRow: guiHelper.BoxSizerHelper = guiHelper.BoxSizerHelper(queryParent, wx.HORIZONTAL)
		self.solarYearCtrl = gregorianRow.addLabeledControl(
			# Translators: Label for Gregorian year query controls.
			_("Gregorian &year:"),
			wx.ComboBox,
			choices=[],
			style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER,
		)
		self.solarMonthCtrl = gregorianRow.addLabeledControl(
			# Translators: Label for Gregorian month query controls.
			_("Gregorian &month:"),
			wx.Choice,
			choices=[],
		)
		self.solarDayCtrl = gregorianRow.addLabeledControl(
			# Translators: Label for Gregorian day query controls.
			_("Gregorian &day:"),
			wx.Choice,
			choices=[],
		)
		self.solarHourCtrl = gregorianRow.addLabeledControl(
			# Translators: Label for Gregorian hour query controls.
			_("Gregorian &hour:"),
			wx.Choice,
			choices=[],
		)
		self.todayButton = wx.Button(
			queryParent,
			# Translators: Button that resets the calendar query to the current date and time.
			label=_("&Today"),
		)
		gregorianRow.addItem(self.todayButton)
		querySizer.addItem(gregorianRow.sizer, flag=wx.EXPAND)

		lunarRow: guiHelper.BoxSizerHelper = guiHelper.BoxSizerHelper(queryParent, wx.HORIZONTAL)
		self.lunarYearCtrl = lunarRow.addLabeledControl(
			# Translators: Label for lunar year query controls.
			_("Lunar y&ear:"),
			wx.ComboBox,
			choices=[],
			style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER,
		)
		self.lunarMonthCtrl = lunarRow.addLabeledControl(
			# Translators: Label for lunar month query controls.
			_("Lunar mo&nth:"),
			wx.Choice,
			choices=[],
		)
		self.lunarDayCtrl = lunarRow.addLabeledControl(
			# Translators: Label for lunar day query controls.
			_("Lunar d&ay:"),
			wx.Choice,
			choices=[],
		)
		self.lunarHourCtrl = lunarRow.addLabeledControl(
			# Translators: Label for lunar hour query controls.
			_("Lunar h&our:"),
			wx.Choice,
			choices=[],
		)
		querySizer.addItem(lunarRow.sizer, flag=wx.EXPAND)

		termRow: guiHelper.BoxSizerHelper = guiHelper.BoxSizerHelper(queryParent, wx.HORIZONTAL)
		self.solarTermCtrl = termRow.addLabeledControl(
			# Translators: Label for solar term query controls.
			_("&Solar term:"),
			wx.Choice,
			choices=[],
		)
		querySizer.addItem(termRow.sizer, flag=wx.EXPAND)

		queryBox.Add(querySizer.sizer, flag=wx.EXPAND)
		parentSizer.Add(queryBox, flag=wx.EXPAND)

		self.solarYearCtrl.Bind(wx.EVT_COMBOBOX, self._onGregorianChanged)
		self.solarYearCtrl.Bind(wx.EVT_TEXT_ENTER, self._onGregorianYearCommitted)
		self.solarYearCtrl.Bind(wx.EVT_KILL_FOCUS, self._onGregorianYearFocusLost)
		self.solarMonthCtrl.Bind(wx.EVT_CHOICE, self._onGregorianChanged)
		self.solarDayCtrl.Bind(wx.EVT_CHOICE, self._onGregorianChanged)
		self.solarHourCtrl.Bind(wx.EVT_CHOICE, self._onGregorianChanged)
		self.todayButton.Bind(wx.EVT_BUTTON, self._onToday)
		self.lunarYearCtrl.Bind(wx.EVT_COMBOBOX, self._onLunarChanged)
		self.lunarYearCtrl.Bind(wx.EVT_TEXT_ENTER, self._onLunarYearCommitted)
		self.lunarYearCtrl.Bind(wx.EVT_KILL_FOCUS, self._onLunarYearFocusLost)
		self.lunarMonthCtrl.Bind(wx.EVT_CHOICE, self._onLunarChanged)
		self.lunarDayCtrl.Bind(wx.EVT_CHOICE, self._onLunarChanged)
		self.lunarHourCtrl.Bind(wx.EVT_CHOICE, self._onLunarChanged)
		self.solarTermCtrl.Bind(wx.EVT_CHOICE, self._onSolarTermChanged)

	def _refreshControls(self) -> None:
		self._isRefreshing = True
		try:
			solarTime = self._query.solarTime
			solarDay = solarTime.get_solar_day()
			lunarDay = solarDay.get_lunar_day()
			lunarMonth = lunarDay.get_lunar_month()
			lunarHour = solarTime.get_lunar_hour()
			summary: str = buildSummary(self._query)
			solarYearChoices: list[ChoiceItem] = getSolarYearChoices()
			lunarYearChoices: list[ChoiceItem] = getLunarYearChoices()
			solarMonthChoices: list[ChoiceItem] = getSolarMonthChoices(solarDay.get_year())
			solarDayChoices: list[ChoiceItem] = getSolarDayChoices(solarDay.get_year(), solarDay.get_month())
			lunarMonthChoices: list[ChoiceItem] = getLunarMonthChoices(lunarMonth.get_year())
			lunarDayChoices: list[ChoiceItem] = getLunarDayChoices(
				lunarMonth.get_year(),
				lunarMonth.get_month_with_leap(),
			)
			lunarHourChoices: list[ChoiceItem] = getLunarHourChoices(
				lunarMonth.get_year(),
				lunarMonth.get_month_with_leap(),
				lunarDay.get_day(),
			)
			lunarHourValue: int = self._getClosestChoiceValue(lunarHourChoices, lunarHour.get_hour(), 0)
			solarTermChoices: list[SolarTermChoice] = getSolarTermChoices(solarDay.get_year())
			basicText: str = buildBasicText(self._query)
			self.Freeze()
			try:
				if self.summaryCtrl.GetLabel() != summary:
					self.summaryCtrl.SetLabel(summary)
				self._setChoiceItems(self.solarYearCtrl, solarYearChoices, solarDay.get_year())
				self._solarMonthChoices = solarMonthChoices
				self._solarDayChoices = solarDayChoices
				self._setChoiceItems(
					self.solarMonthCtrl,
					self._solarMonthChoices,
					solarDay.get_month(),
				)
				self._setChoiceItems(self.solarDayCtrl, self._solarDayChoices, solarDay.get_day())
				self._setChoiceItems(
					self.solarHourCtrl,
					getSolarHourChoices(),
					solarTime.get_hour(),
				)
				self._setChoiceItems(self.lunarYearCtrl, lunarYearChoices, lunarMonth.get_year())
				self._lunarMonthChoices = lunarMonthChoices
				self._lunarDayChoices = lunarDayChoices
				self._lunarHourChoices = lunarHourChoices
				self._setChoiceItems(
					self.lunarMonthCtrl,
					self._lunarMonthChoices,
					lunarMonth.get_month_with_leap(),
				)
				self._setChoiceItems(self.lunarDayCtrl, self._lunarDayChoices, lunarDay.get_day())
				self._setChoiceItems(self.lunarHourCtrl, self._lunarHourChoices, lunarHourValue)

				self._solarTermChoices = solarTermChoices
				self._setSolarTermSelection()
				self._setResultText(basicText)
			finally:
				self.Thaw()
				self.Layout()
		finally:
			self._isRefreshing = False

	def _refreshGregorianQuery(self) -> None:
		year: int = self._getEditableYearValue(
			self.solarYearCtrl,
			getSolarYearChoices(),
			self._query.solarTime.get_year(),
		)
		month: int = self._getSelectedValue(self.solarMonthCtrl, self._solarMonthChoices, 1)
		preferredDay: int = self._getSelectedValue(self.solarDayCtrl, self._solarDayChoices, 1)
		hour: int = self._getSelectedValue(self.solarHourCtrl, getSolarHourChoices(), 0)
		self._scheduleQuery(lambda: self._buildGregorianQuery(year, month, preferredDay, hour))

	def _refreshLunarQuery(self) -> None:
		lunarYear: int = self._query.solarTime.get_solar_day().get_lunar_day().get_lunar_month().get_year()
		year: int = self._getEditableYearValue(self.lunarYearCtrl, getLunarYearChoices(), lunarYear)
		preferredMonth: int = self._getSelectedValue(self.lunarMonthCtrl, self._lunarMonthChoices, 1)
		preferredDay: int = self._getSelectedValue(self.lunarDayCtrl, self._lunarDayChoices, 1)
		preferredHour: int = self._getSelectedValue(self.lunarHourCtrl, self._lunarHourChoices, 0)
		self._scheduleQuery(
			lambda: self._buildLunarQuery(year, preferredMonth, preferredDay, preferredHour),
		)

	def _setChoiceItems(
		self,
		control: wx.Choice | wx.ComboBox,
		items: list[ChoiceItem],
		selectedValue: int,
	) -> None:
		if self._choiceItemsById.get(control.GetId()) is not items:
			control.Clear()
			for item in items:
				control.Append(item.label)
			self._choiceItemsById[control.GetId()] = items
		if items:
			firstValue: int = items[0].value
			lastValue: int = items[-1].value
			if lastValue - firstValue + 1 == len(items):
				control.SetSelection(max(0, min(len(items) - 1, selectedValue - firstValue)))
				return
		for index, item in enumerate(items):
			if item.value == selectedValue:
				control.SetSelection(index)
				return
		if items:
			control.SetSelection(0)
		else:
			control.SetSelection(-1)

	def _setSolarTermSelection(self) -> None:
		solarTermItems: tuple[SolarTermChoice, ...] = tuple(self._solarTermChoices)
		if self._solarTermItems != solarTermItems:
			self.solarTermCtrl.Clear()
			for choice in self._solarTermChoices:
				self.solarTermCtrl.Append(choice.label)
			self._solarTermItems = solarTermItems
		currentTerm = self._query.solarTime.get_term()
		for index, choice in enumerate(self._solarTermChoices):
			if choice.index == currentTerm.get_index() and choice.termYear == currentTerm.get_year():
				self.solarTermCtrl.SetSelection(index)
				return
		self.solarTermCtrl.SetSelection(-1)

	def _setResultText(self, text: str) -> None:
		if self.resultCtrl.GetValue() == text:
			return
		self.resultCtrl.SetValue(text)
		self._scrollResultToTop()
		wx.CallAfter(self._scrollResultToTop)

	def _scrollResultToTop(self) -> None:
		try:
			if not bool(self.resultCtrl):
				return
			self.resultCtrl.SetInsertionPoint(0)
			self.resultCtrl.ShowPosition(0)
		except RuntimeError:
			return

	def _buildGregorianQuery(
		self,
		year: int,
		preferredMonth: int,
		preferredDay: int,
		hour: int,
	) -> CalendarQuery:
		solarMonthChoices: list[ChoiceItem] = getSolarMonthChoices(year)
		month: int = self._getClosestChoiceValue(solarMonthChoices, preferredMonth, 1)
		solarDayChoices: list[ChoiceItem] = getSolarDayChoices(year, month)
		day: int = self._getClosestChoiceValue(solarDayChoices, preferredDay, 1)
		return CalendarQuery.fromSolarValues(year, month, day, hour)

	def _buildLunarQuery(
		self,
		year: int,
		preferredMonth: int,
		preferredDay: int,
		preferredHour: int,
	) -> CalendarQuery:
		lunarMonthChoices: list[ChoiceItem] = getLunarMonthChoices(year)
		month: int = self._getClosestChoiceValue(lunarMonthChoices, preferredMonth, 1)
		if preferredMonth < 0 and month != preferredMonth:
			month = self._getClosestChoiceValue(lunarMonthChoices, abs(preferredMonth), 1)
		lunarDayChoices: list[ChoiceItem] = getLunarDayChoices(year, month)
		day: int = self._getClosestChoiceValue(lunarDayChoices, preferredDay, 1)
		lunarHourChoices: list[ChoiceItem] = getLunarHourChoices(year, month, day)
		hour: int = self._getClosestChoiceValue(lunarHourChoices, preferredHour, 0)
		return CalendarQuery.fromLunarValues(year, month, day, hour)

	def _onGregorianChanged(self, evt: wx.Event) -> None:
		if self._isRefreshing:
			evt.Skip()
			return
		try:
			self._refreshGregorianQuery()
		except Exception:
			self._reportUpdateError()
		evt.Skip()

	def _onLunarChanged(self, evt: wx.Event) -> None:
		if self._isRefreshing:
			evt.Skip()
			return
		try:
			self._refreshLunarQuery()
		except Exception:
			self._reportUpdateError()
		evt.Skip()

	def _onGregorianYearCommitted(self, evt: wx.Event) -> None:
		if self._isRefreshing:
			evt.Skip()
			return
		try:
			self._commitGregorianYear()
		except Exception:
			self._reportUpdateError()
		evt.Skip()

	def _onGregorianYearFocusLost(self, evt: wx.FocusEvent) -> None:
		if not self._isRefreshing:
			try:
				self._commitGregorianYear()
			except Exception:
				self._reportUpdateError()
		evt.Skip()

	def _onLunarYearCommitted(self, evt: wx.Event) -> None:
		if self._isRefreshing:
			evt.Skip()
			return
		try:
			self._commitLunarYear()
		except Exception:
			self._reportUpdateError()
		evt.Skip()

	def _onLunarYearFocusLost(self, evt: wx.FocusEvent) -> None:
		if not self._isRefreshing:
			try:
				self._commitLunarYear()
			except Exception:
				self._reportUpdateError()
		evt.Skip()

	def _onSolarTermChanged(self, evt: wx.Event) -> None:
		if self._isRefreshing:
			evt.Skip()
			return
		try:
			selection: int = self.solarTermCtrl.GetSelection()
			if 0 <= selection < len(self._solarTermChoices):
				self._setQuery(CalendarQuery(self._solarTermChoices[selection].solarTime))
		except Exception:
			self._reportUpdateError()
		evt.Skip()

	def _onToday(self, evt: wx.CommandEvent) -> None:
		self._setQuery(CalendarQuery.fromDatetime(datetime.now()))
		evt.Skip()

	def _setQuery(self, query: CalendarQuery) -> None:
		if self._refreshCall is not None and self._refreshCall.IsRunning():
			self._refreshCall.Stop()
		self._pendingQueryFactory = None
		self._query = query
		self._refreshControls()

	def _scheduleQuery(self, queryFactory: Callable[[], CalendarQuery]) -> None:
		self._pendingQueryFactory = queryFactory
		if self._refreshCall is None:
			self._refreshCall = wx.CallLater(QUERY_REFRESH_DELAY_MS, self._applyScheduledQuery)
		else:
			self._refreshCall.Restart(QUERY_REFRESH_DELAY_MS)

	def _applyScheduledQuery(self) -> None:
		queryFactory: Callable[[], CalendarQuery] | None = self._pendingQueryFactory
		if queryFactory is None:
			return
		try:
			self._setQuery(queryFactory())
		except Exception:
			self._pendingQueryFactory = None
			self._reportUpdateError()

	def _getSelectedValue(self, control: wx.Choice, items: list[ChoiceItem], default: int) -> int:
		selection: int = control.GetSelection()
		if 0 <= selection < len(items):
			return items[selection].value
		return default

	def _getEditableYearValue(
		self,
		control: wx.ComboBox,
		items: list[ChoiceItem],
		default: int,
	) -> int:
		valueText: str = control.GetValue().strip()
		if not valueText:
			return self._getClosestChoiceValue(items, default, default)
		try:
			year: int = int(valueText)
		except ValueError:
			return self._getClosestChoiceValue(items, default, default)
		return self._getClosestChoiceValue(items, year, default)

	def _normalizeYearComboValue(
		self,
		control: wx.ComboBox,
		items: list[ChoiceItem],
		default: int,
	) -> int:
		value: int = self._getEditableYearValue(control, items, default)
		self._setChoiceItems(control, items, value)
		return value

	def _commitGregorianYear(self) -> None:
		currentYear: int = self._query.solarTime.get_year()
		year: int = self._normalizeYearComboValue(
			self.solarYearCtrl,
			getSolarYearChoices(),
			currentYear,
		)
		if year != currentYear:
			self._refreshGregorianQuery()

	def _commitLunarYear(self) -> None:
		lunarYear: int = self._query.solarTime.get_solar_day().get_lunar_day().get_lunar_month().get_year()
		year: int = self._normalizeYearComboValue(self.lunarYearCtrl, getLunarYearChoices(), lunarYear)
		if year != lunarYear:
			self._refreshLunarQuery()

	def _getClosestChoiceValue(self, items: list[ChoiceItem], preferredValue: int, default: int) -> int:
		values: list[int] = [item.value for item in items]
		if preferredValue in values:
			return preferredValue
		previousValues: list[int] = [value for value in values if value <= preferredValue]
		if previousValues:
			return max(previousValues)
		if values:
			return values[0]
		return default

	def _reportUpdateError(self) -> None:
		log.exception("Error updating leanCalendar dialog")
		# Translators: Error message shown when the leanCalendar dialog cannot update its date.
		ui.message(_("Unable to update leanCalendar."))

	def _onCharHook(self, evt: wx.KeyEvent) -> None:
		if evt.GetKeyCode() == wx.WXK_ESCAPE:
			self.Close()
			return
		evt.Skip()

	def _onClose(self, evt: wx.CloseEvent) -> None:
		self.Destroy()

	def _onDestroy(self, evt: wx.WindowDestroyEvent) -> None:
		global _calendarDialog
		if evt.GetEventObject() is self:
			if self._refreshCall is not None and self._refreshCall.IsRunning():
				self._refreshCall.Stop()
			_calendarDialog = None
		evt.Skip()
