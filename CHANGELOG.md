# Changelog

## [1.10.12] - 2025-09-05

### Added
- Implemented a new in-app update mechanism that launches the installer in a separate terminal. This provides clear, live feedback during updates and prevents conflicts with the running application.

## [1.10.11] - 2025-09-05

### Fixed
- Improved the 'About' dialog's layout and functionality for better readability.
- The version checker is now more robust and can correctly detect a newer system Qt version, even with distribution-specific naming conventions.

## [1.10.10] - 2025-09-05

### Fixed
- Resolved an issue where the application theme was not applying correctly due to a version mismatch between PyQt6 and the system's Qt6 libraries (6.9.1 -> 6.9.2).