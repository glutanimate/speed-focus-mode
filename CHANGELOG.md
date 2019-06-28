# Changelog

All notable changes to Speed Focus Mode will be documented here. You can click on each release number to be directed to a detailed log of all code commits for that particular release. The download links will direct you to the GitHub release page, allowing you to manually install a release if you want.

If you enjoy Speed Focus Mode, please consider supporting my work on Patreon, or by buying me a cup of coffee :coffee::

<p align="center">
<a href="https://www.patreon.com/glutanimate" rel="nofollow" title="Support me on Patreon 😄"><img src="https://glutanimate.com/logos/patreon_button.svg"></a>      <a href="https://ko-fi.com/X8X0L4YV" rel="nofollow" title="Buy me a coffee 😊"><img src="https://glutanimate.com/logos/kofi_button.svg"></a>
</p>

:heart: My heartfelt thanks goes out to everyone who has supported this add-on through their tips, contributions, or any other means (you know who you are!). All of this would not have been possible without you. Thank you for being awesome!

## [Unreleased]

### Added

- A **button** that **stops automated events** from firing ("More Time!"). Can be disabled in the new config file.
- A **hotkey** that that does the same (configurable, set to `p` by default,  thanks to AnKing for the inspiration)
- A simple **countdown**, indicating the time until the next automated card action
- Ability to **bury** cards (thanks to NicolasCuri for the inspiration)
- Ability to **mark** cards as **"good"** (thanks to JulyMorning for the feature request)
- Ability to launch card actions from the question side, skipping the answer reveal (e.g. to bury cards immediately)
- Timers are now suspended automatically when opening dialogs
- Support for Anki 2.1's `user_files` specification
- Support for Anki 2.1's config system. Used for all general settings.

### Changed

- `sound.mp3` files should now be placed in the `user_files` directory to preserve them across add-on updates.
- Some further code refactoring and reorganization to improve maintainability

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

[Unreleased]: https://github.com/glutanimate/speed-focus-mode/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/glutanimate/speed-focus-mode/releases/tag/v0.3.0

-----

The format of this file is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).