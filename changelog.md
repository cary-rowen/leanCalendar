# leanCalendar Changelog

## 0.2.6

* Fixed detailed lunar reports so the current solar term is included when it is a qi term, preventing nearby solar terms from being skipped.
* Show minutes in multi-day solar term countdowns for more precise remaining time.
* Improved report readability by grouping F11 and detailed F12 output across semantic lines while preserving punctuation before line breaks.

## 0.2.3

* Dependent Updates.

## 0.2.2

* Fixed next solar term countdowns in the detailed lunar report and query results so intermediate solar terms are no longer skipped.
* Streamlined the brief lunar report by removing repeated lunar hour wording when the four pillars already include the hour pillar.

## 0.2.1

* Use the generic zh locale so Chinese localization can apply across Chinese regional variants.

## 0.2.0

* Richer calendar query results.
* Added an unassigned command to open the query dialog directly.
* Fixed focus order in the query dialog.

## 0.1.2

* Update translation.

## 0.1.1

* Sync upstream AddonTemplate and release build checks.

## 0.1.0

* Initial release.
* Added `NVDA+F11` to report Chinese lunar date and solar term information. Press twice for additional lunar context, or three times to open the calendar query dialog.
* Added `NVDA+F12` to report the current time. Press twice for Gregorian date details.
