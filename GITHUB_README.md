# TactileSense v3.2 DMR Edition

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-3.2.0--baseline-green.svg)](https://github.com/YOUR-USERNAME/tactile-sense/releases)
[![Status](https://img.shields.io/badge/status-peer--review-yellow.svg)]()

**Clinical data capture system for PT Robotic's therapeutic platform**

TactileSense creates FDA-compliant Digital Master Records (DMR) of physical therapy treatments using tactile glove sensors, enabling Physical Therapists to develop, document, and replicate treatment protocols.

![TactileSense Interface](docs/images/main-interface.png)
*Main interface showing real-time pressure visualization and DMR controls*

---

## 🎯 Overview

TactileSense v3.2 DMR Edition is designed for **Physical Therapists (PT)** to create master treatment protocols that can later be executed by Physical Therapy Assistants (PTA) or autonomous robotic systems.

### Key Features

- **Digital Master Record System** - FDA 21 CFR Part 11 compliant session recording
- **Adjustable Frame Capture** - PT-controlled frame periods (20ms to 5000ms) with pulse averaging
- **Integer Data Format** - Clinically appropriate precision (whole kPa values)
- **Frame Viewer** - Frame-by-frame clinical review with navigation and playback
- **Real-time Feedback** - Pressure zones, heatmaps, and 3D hand orientation
- **Multi-format Export** - DMR (JSON), CSV, and human-readable reports
- **Auto-export** - Automatic CSV backup on session save

---

## 📊 Current Status

**Version:** 3.2.0-baseline  
**Release Date:** February 4, 2026  
**Status:** Ready for peer review and PT testing

### Implemented Features

✅ Complete PT protocol development workflow  
✅ Frame capture with pulse averaging  
✅ Integer data format (DMR + CSV)  
✅ Frame Viewer for clinical review  
✅ Pressure zone configuration  
✅ Demo Simulator with 9 therapy patterns  
✅ Comprehensive documentation

### In Development

🔄 Windows executable build  
🔄 Physical TactileGlove hardware integration  
⏳ PTA execution mode (v3.3)  
⏳ Robot autonomous execution (future)

---

## 🚀 Quick Start

### For Peer Reviewers

1. **Download** the [latest release](https://github.com/YOUR-USERNAME/tactile-sense/releases)
2. **Extract** TactileSense_v3.2_Package.zip
3. **Read** [Quick Start Guide](docs/QUICK_START.md)
4. **Follow** [Test Scenarios](tests/TEST_SCENARIOS.md)
5. **Submit** feedback via [GitHub Issues](https://github.com/YOUR-USERNAME/tactile-sense/issues)

### For Developers

```bash
# Clone repository
git clone https://github.com/YOUR-USERNAME/tactile-sense.git
cd tactile-sense

# Install dependencies
pip install -r src/requirements.txt

# Run application
python src/tactile_sense_main.py
```

See [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) for building Windows executables.

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Quick Start Guide](docs/QUICK_START.md) | 5-minute guide to your first DMR session |
| [User Guide](docs/USER_GUIDE.md) | Complete PT user manual |
| [Test Scenarios](tests/TEST_SCENARIOS.md) | Structured testing checklist for reviewers |
| [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) | Building Windows executables with PyInstaller |
| [Baseline Specification](docs/BASELINE_SPECIFICATION.md) | Complete feature list and technical specs |
| [Reviewers Guide](REVIEWERS_GUIDE.md) | How to review and provide feedback |

---

## 📁 Repository Structure

```
tactile-sense/
├── src/                    # Source code
│   ├── tactile_sense_main.py
│   └── requirements.txt
├── docs/                   # Documentation
│   ├── QUICK_START.md
│   ├── USER_GUIDE.md
│   └── images/
├── tests/                  # Test scenarios
│   └── TEST_SCENARIOS.md
├── examples/               # Example DMR files
├── .github/                # GitHub templates
│   └── ISSUE_TEMPLATE/
└── README.md               # This file
```

---

## 🤝 Contributing

We welcome feedback from:
- Physical Therapists (clinical workflow validation)
- Software Engineers (code review, improvements)
- Medical Device Consultants (regulatory compliance)
- UI/UX Designers (interface improvements)

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

To submit feedback:
1. Check existing [Issues](https://github.com/YOUR-USERNAME/tactile-sense/issues)
2. Create new issue using appropriate template:
   - [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md)
   - [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md)
   - [Feedback](.github/ISSUE_TEMPLATE/feedback.md)

---

## 📝 License

Copyright © 2026 PT Robotic LLC

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

---

## 👥 Team

**PT Robotic LLC**

- **Yuri** - CEO, Lead Developer
- **Dr. J.C. Metivier** - Chief Clinical Officer

---

## 📧 Contact

- **Email:** [your.email@company.com]
- **GitHub Issues:** [Report bugs or request features](https://github.com/YOUR-USERNAME/tactile-sense/issues)

---

## 🗺️ Roadmap

### v3.2.x (Current - PT Testing Phase)
- ✅ Complete PT protocol development features
- 🔄 Windows executable build
- 🔄 Peer review feedback integration

### v3.3 (Q2 2026 - PTA Implementation)
- PTA execution mode
- Protocol comparison features
- PTA training interface

### v4.0 (Future - Robot Integration)
- Robot control interface
- Autonomous execution
- Advanced analytics

---

## ⚕️ Regulatory Status

**IMPORTANT:** This is a research prototype for peer review and testing.  
Not yet cleared for clinical use.  
FDA 510(k) submission planned for Q3 2026.

---

<div align="center">

**[Download Latest Release](https://github.com/YOUR-USERNAME/tactile-sense/releases)** | **[Read Documentation](docs/)** | **[Report Issue](https://github.com/YOUR-USERNAME/tactile-sense/issues/new)**

Made with ❤️ for the physical therapy community

</div>
