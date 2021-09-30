# Changelog

All notable changes to Speed Focus Mode will be documented here. You can click on each release number to be directed to a detailed log of all code commits for that particular release. The download links will direct you to the GitHub release page, allowing you to manually install a release if you want.

If you enjoy Speed Focus Mode, please consider supporting my work on Patreon, or by buying me a cup of coffee :coffee::

<p align="center">
<a href="https://www.patreon.com/glutanimate" rel="nofollow" title="Support me on Patreon 😄"><img src="https://glutanimate.com/logos/patreon_button.svg"></a>      <a href="https://ko-fi.com/X8X0L4YV" rel="nofollow" title="Buy me a coffee 😊"><img src="https://glutanimate.com/logos/kofi_button.svg"></a>
</p>

:heart: My heartfelt thanks goes out to everyone who has supported this add-on through their tips, contributions, or any other means (you know who you are!). All of this would not have been possible without you. Thank you for being awesome!

## [Unreleased]

The changelog below encompasses all changes since the previous AnkiWeb release.

### Added

- Added a **button** that **stops automated events** from firing ("More Time!"). Can be disabled in the new config file.
- Added a **hotkey** that that does the same (configurable, set to `p` by default,  thanks to AnKing for the inspiration)
- Added a simple **countdown**, indicating the time until the next automated card action
- You can now **bury** cards (thanks to NicolasCuri for the inspiration)
- You can now **mark** cards as **"good"** in addition to "again" (thanks to JulyMorning for the feature request)
- Added ability to launch card actions from the question side, skipping the answer reveal (e.g. to bury cards immediately, thanks to Ba for the suggestion)
- Timers are now suspended automatically when opening dialogs
- Timers are now suspended automatically when typing answer

### Changed

- Please note that Anki versions 2.1.45 and above ship with a new deck options menu that is not ready to be used by add-ons just yet. To access the old deck options and thus Speed Focus Mode's settings, please shift click on the "Options" entry after clicking on the gear icon next to a deck.
- `sound.mp3` files should now be placed in the `user_files` directory to preserve them across add-on updates.
- Some further code refactoring and reorganization to improve maintainability and support with upcoming Anki updates

### Fixed

- Fixed an issue that would cause the add-on to produce an error message when opening the card browser in some scenarios (#38)
- Fixed a compatibility issue with Clickable Tags, AnkiConnect, Review Heatmap, and other add-ons wrapping the dialog manager (#34, #28, #27, #23)
- Dropped support for very old Anki versions. The minimum supported version is now 2.1.22.
- Addressed an issue that would cause the alert not to play in some scenarios
- Added a workaround to make Speed Focus Mode compatible with Advanced Review Bottom Bar

## [0.4.0-beta.1] - 2019-06-28

### [Download](https://github.com/glutanimate/speed-focus-mode/releases/tag/v0.4.0-beta.1)

### Added

- A **button** that **stops automated events** from firing ("More Time!"). Can be disabled in the new config file.
- A **hotkey** that that does the same (configurable, set to `p` by default,  thanks to AnKing for the inspiration)
- A simple **countdown**, indicating the time until the next automated card action
- Ability to **bury** cards (thanks to NicolasCuri for the inspiration)
- Ability to **mark** cards as **"good"** (thanks to JulyMorning for the feature request)
- Ability to launch card actions from the question side, skipping the answer reveal (e.g. to bury cards immediately, thanks to Ba for the suggestion)
- Timers are now suspended automatically when opening dialogs
- Support for Anki 2.1's `user_files` specification
- Support for Anki 2.1's config system. Used for all general settings.

### Changed

- `sound.mp3` files should now be placed in the `user_files` directory to preserve them across add-on updates.
- Some further code refactoring and reorganization to improve maintainability

## [0.4.0-dev.1] - 2019-06-28

### [Download](https://github.com/glutanimate/speed-focus-mode/releases/tag/v0.4.0-dev.1)

## [0.3.0] - 2019-06-02

### [Download](https://github.com/glutanimate/speed-focus-mode/releases/tag/v0.3.0)

### Fixed

- Fix anki.lang warnings

### Changed

- Refactored add-on to improve stability and maintainability

## 0.2.2 - 2019-01-08

### Fixed

- Fixed a new 2.1 bug that would occur on Anki exit (thanks to Elikem & dsd for the report)

## 0.2.1 - 2018-02-17

### Fixed

- Fixed an incompatibility issue with Anki 2.1 (thanks to @khonkhortisan!)

## 0.2.0 - 2018-02-16

### Changed

- renamed add-on to "Speed Focus Mode".

### Added

- Added auto alert option

## 0.1.0 - 2017-12-21

### Added

- Initial release of Speed Focus Mode

[Unreleased]: https://github.com/glutanimate/speed-focus-mode/compare/v0.4.0-beta.1...HEAD
[0.4.0-beta.1]: https://github.com/glutanimate/speed-focus-mode/compare/v0.4.0-dev.1...v0.4.0-beta.1
[0.4.0-dev.1]: https://github.com/glutanimate/speed-focus-mode/compare/v0.3.0...v0.4.0-dev.1
[0.3.0]: https://github.com/glutanimate/speed-focus-mode/releases/tag/v0.3.0

-----

The format of this file is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).