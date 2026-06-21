# leanCalendar

leanCalendar is an NVDA add-on for quickly reporting Chinese lunar calendar, solar term, and Gregorian date and time information. It also provides a query dialog for other dates.

## Commands

* `NVDA+F11`: report Chinese lunar calendar and solar term information.
* Press `NVDA+F11` twice: report additional lunar and almanac context.
* Press `NVDA+F11` three times: open the leanCalendar query dialog.
* An unassigned command is available in Input Gestures to open the leanCalendar query dialog directly.
* `NVDA+F12`: report the current Gregorian time.
* Press `NVDA+F12` twice: report Gregorian date details.

## What Each Command Reports

### NVDA+F11

Press once to report:

* Chinese lunar date.
* Lunar month size.
* Sexagenary cycle year, month, day, and hour.
* Current solar term day.
* Current hou period.
* Lunar festival, if any.
* Countdown to the next solar term, only when it is within seven days.

Press twice to report:

* Nearby solar terms.
* Countdown to the next solar term.
* Chinese zodiac.
* Full moon time.
* Moon phase day.
* Jianchu duty.
* Sanfu, Shujiu, or Meiyu period, if applicable.

Press three times to open the query dialog. The dialog supports lookup by Gregorian date and time, Chinese lunar date and shichen, or solar term. Results are grouped into Gregorian, Lunar, Solar Terms and Phenology, and Almanac sections.

### NVDA+F12

Press once to report the current time with hour, minute, and second.

Press twice to report:

* Gregorian date and weekday.
* Day of year, week number, quarter, and month length.
* Holiday, legal day off, or make-up work day, when available.
* Workday or weekend when no legal holiday status applies.
* Western zodiac sign.

The lunar date and solar term data are calculated with the bundled [tyme4py](https://github.com/6tail/tyme4py) library.

## License

leanCalendar is distributed under the terms of the GNU General Public License, version 2.
