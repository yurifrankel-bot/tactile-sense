# Changelog

All notable changes to TactileSense will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Windows executable build
- Physical TactileGlove hardware integration
- Additional test scenarios based on peer feedback
- Performance optimizations

---

## [3.2.0-baseline] - 2026-02-04

### Added
- **Digital Master Record (DMR) System**
  - Complete session metadata capture (patient ID, PT ID, location, treatment type)
  - Unique session ID generation (DMR-YYYYMMDD-HHMMSS format)
  - FDA 21 CFR Part 11 compliant structure
  - Session state management (new/paused/saved)
  - Pause/resume capability during recording
  
- **Frame Capture Control**
  - PT-adjustable frame period (20ms to 5000ms)
  - Pulse averaging: Multiple sensor samples averaged per frame
  - Visual slider with live feedback (ms/sec, Hz, averaging status)
  - Frame metadata: period, pulses averaged, timestamp
  
- **Integer Data Format**
  - All sensor data stored as integers (kPa)
  - DMR files contain integer arrays
  - CSV exports contain integer values
  - Clinically appropriate precision (no false accuracy)
  
- **Display Data Distinction**
  - Fingers show frames when recording (smooth, averaged)
  - Fingers show pulses when not recording (real-time feedback)
  - "You see what you record" principle
  - Display updates at frame period rate during recording
  
- **Frame Viewer**
  - Frame-by-frame navigation (first/last/prev/next buttons)
  - Slider for direct frame access
  - Playback mode with speed control (0.5x/1x/2x)
  - Per-frame statistics and zone classification
  - Heatmap visualization for each frame
  - Hand orientation display per frame
  - Pattern identification per frame
  
- **Data Export**
  - CSV export with full sensor data
  - DMR Report with human-readable summary
  - Auto-export option: automatic CSV on save
  - Organized directories: PT_CSV, PTA_CSV, Robot_CSV
  
- **User Interface Improvements**
  - Auto-export checkbox in main UI (always visible)
  - PT ID in all displays (recording label, status bar)
  - Frame period slider in DMR Controls
  - Enhanced DMR info bar showing session details
  
- **Demo Simulator**
  - 9 therapy patterns: Ball Grip, Precision Pinch, Power Grip, 
    PT Shoulder/Elbow/Wrist, Three-Finger, Lateral Pinch, Idle
  - Real-time pattern switching
  - Simulated hand orientation changes
  
- **Comprehensive Documentation**
  - Quick Start Guide (5-minute first session)
  - PT User Guide (complete manual)
  - Test Scenarios (15 structured tests)
  - Baseline Specification (technical details)
  - Windows Deployment Guide
  - Frame Period Control Guide
  - Frames vs Pulses Explanation
  - Troubleshooting guides

### Changed
- Frame capture now independent from sensor update loop
  - Sensor samples at 50ms (fixed)
  - Frames captured at PT-adjustable period
- All displays (heatmap, hand, stats) now use display_data
  - Shows frames during recording
  - Shows pulses when not recording
- DMR form moved checkbox to main UI for better visibility
- Enhanced error messages for three recording states
- Improved file naming conventions with semantic patterns

### Fixed
- disconnect() leaving recording active
- DMR dialog freeze bug (self.root vs self parameter)
- Misleading "Frame: 0" label (now "Sensor: X")
- connect_demo() prompting when already in demo mode
- Frame Viewer empty display (added debug output)
- Export errors with no frames (state-specific messages)

### Technical
- Python 3.12 compatible
- NumPy array operations with integer dtype
- Frame capture scheduling with root.after()
- Pulse buffer for averaging implementation
- Session state tracking
- ISO 8601 timestamp format

### Documentation
- 7 comprehensive documentation files
- BUILD_INSTRUCTIONS.txt for Windows deployment
- GITHUB_SETUP_GUIDE.txt for repository setup
- REVIEWERS_GUIDE.md for peer reviewers
- Complete test scenarios with checkboxes

---

## [3.1] - Not Released

### Notes
- Development version, not publicly released
- Initial DMR structure exploration
- Frame recording experiments

---

## [3.0] - 2025-12-XX

### Added
- Interactive pressure zone configuration
- Visual hand representation with real-time color coding
- Enhanced heatmap visualization
- 3D hand orientation display
- Demo simulator with multiple patterns
- Basic session recording
- CSV export capability

### Initial Features
- 65-sensor tactile glove support
- Real-time pressure visualization
- Basic data logging
- Manual pressure zone adjustment

---

## Version Format

Versions follow Semantic Versioning: MAJOR.MINOR.PATCH

- **MAJOR** version: Incompatible API changes or complete redesigns
- **MINOR** version: Backwards-compatible functionality additions
- **PATCH** version: Backwards-compatible bug fixes

### Version Tags
- `-baseline`: Initial release for testing/review
- `-rc1, -rc2`: Release candidates
- `-alpha, -beta`: Pre-release versions

---

## Categories

### Added
New features

### Changed
Changes in existing functionality

### Deprecated
Soon-to-be removed features

### Removed
Removed features

### Fixed
Bug fixes

### Security
Security vulnerability fixes

---

## Upcoming Versions

### [3.2.1] - Planned
Bug fixes based on peer review feedback

### [3.3.0] - Q2 2026
PTA execution mode implementation
- Protocol execution interface
- Protocol comparison features
- PTA training tools
- Performance metrics

### [4.0.0] - Future
Robot integration
- Robot control interface
- Autonomous execution
- Multi-robot coordination
- Advanced analytics

---

## Links

- [Repository](https://github.com/YOUR-USERNAME/tactile-sense)
- [Releases](https://github.com/YOUR-USERNAME/tactile-sense/releases)
- [Issues](https://github.com/YOUR-USERNAME/tactile-sense/issues)
- [Documentation](docs/)

---

[Unreleased]: https://github.com/YOUR-USERNAME/tactile-sense/compare/v3.2.0-baseline...HEAD
[3.2.0-baseline]: https://github.com/YOUR-USERNAME/tactile-sense/releases/tag/v3.2.0-baseline
[3.0]: https://github.com/YOUR-USERNAME/tactile-sense/releases/tag/v3.0
