# Contributing to TactileSense

Thank you for your interest in contributing to TactileSense! This document provides guidelines for different types of contributors.

## 📋 Table of Contents

- [Types of Contributors](#types-of-contributors)
- [How to Submit Feedback](#how-to-submit-feedback)
- [Code Contributions](#code-contributions)
- [Documentation](#documentation)
- [Testing](#testing)
- [Code of Conduct](#code-of-conduct)

---

## 👥 Types of Contributors

### Physical Therapists
**What we need:**
- Clinical workflow validation
- Feature requests based on practice needs
- Usability feedback
- Testing scenarios
- Treatment pattern suggestions

**How to contribute:**
1. Download and test the application
2. Complete [Test Scenarios](tests/TEST_SCENARIOS.md)
3. Submit feedback via GitHub Issues
4. Suggest improvements based on clinical experience

### Software Engineers
**What we need:**
- Code reviews
- Bug fixes
- Performance improvements
- New feature implementation
- Testing automation

**How to contribute:**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
5. See [Code Contributions](#code-contributions) for details

### Medical Device Consultants
**What we need:**
- Regulatory compliance review (FDA 21 CFR Part 11)
- Security assessment
- Data integrity validation
- Documentation review
- Risk analysis

**How to contribute:**
1. Review documentation and code
2. Create issues for compliance concerns
3. Suggest regulatory improvements
4. Provide industry best practices

### UI/UX Designers
**What we need:**
- Interface usability assessment
- Workflow optimization
- Visual design improvements
- Accessibility evaluation
- Color scheme and contrast review

**How to contribute:**
1. Test the interface
2. Create mockups for improvements
3. Submit design suggestions via Issues
4. Provide accessibility recommendations

---

## 🐛 How to Submit Feedback

### Reporting Bugs

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md)

**Before submitting:**
1. Check [existing issues](https://github.com/YOUR-USERNAME/tactile-sense/issues)
2. Verify you're using the latest release
3. Try to reproduce the issue

**Include in your report:**
- TactileSense version
- Operating system (Windows 10/11)
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if applicable)
- Error messages (if any)

### Requesting Features

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md)

**Before submitting:**
1. Check if feature already requested
2. Consider if feature aligns with project goals

**Include in your request:**
- Clear description of feature
- Use case / clinical need
- Proposed implementation (if applicable)
- Impact on clinical workflow

### General Feedback

Use the [Feedback template](.github/ISSUE_TEMPLATE/feedback.md)

**What to include:**
- Your role (PT, developer, consultant, etc.)
- Overall impressions
- What works well
- What needs improvement
- Suggestions for future

---

## 💻 Code Contributions

### Getting Started

1. **Fork the repository**
   ```bash
   # Click "Fork" button on GitHub
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR-USERNAME/tactile-sense.git
   cd tactile-sense
   ```

3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/ORIGINAL-OWNER/tactile-sense.git
   ```

4. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bugfix-name
   ```

### Development Setup

```bash
# Install dependencies
pip install -r src/requirements.txt

# Install development dependencies (optional)
pip install pytest black flake8

# Run application
python src/tactile_sense_main.py
```

### Coding Standards

**Python Style:**
- Follow PEP 8
- Use descriptive variable names
- Add docstrings to functions
- Maximum line length: 100 characters
- Use type hints where appropriate

**Example:**
```python
def calculate_average_pressure(sensor_data: np.ndarray) -> float:
    """
    Calculate average pressure from active sensors.
    
    Args:
        sensor_data: Array of 65 sensor values in kPa
        
    Returns:
        float: Average pressure of active sensors (> 1 kPa)
    """
    active = sensor_data > 1.0
    if np.any(active):
        return np.mean(sensor_data[active])
    return 0.0
```

**File Organization:**
- Keep related functions together
- Use clear section comments
- Separate UI code from logic
- Document complex algorithms

### Testing Your Changes

Before submitting:
1. Test all affected features
2. Verify no new errors
3. Check console output
4. Test on Windows if possible

**Manual Testing:**
```bash
# Run application
python src/tactile_sense_main.py

# Test:
# 1. Connect Demo Simulator
# 2. Record session
# 3. Save DMR
# 4. Review frames
# 5. Export data
```

### Submitting Pull Request

1. **Commit your changes**
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```

2. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**
   - Go to original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill in PR template
   - Submit

**Pull Request Guidelines:**
- Clear title describing the change
- Reference related issues (#123)
- Explain what changed and why
- List any breaking changes
- Add screenshots for UI changes

**Example PR Title:**
```
Fix: Frame Viewer empty display on immediate open (#45)
```

**Example PR Description:**
```
Fixes #45

### Changes
- Added frame count check before opening Frame Viewer
- Display warning if no frames available
- Added 10-second minimum recommendation

### Testing
- Tested with immediate open (shows warning)
- Tested after 10+ seconds (works correctly)
- Verified on Windows 10

### Screenshots
[Before] [After images]
```

---

## 📚 Documentation

### Documentation Standards

**Markdown Files:**
- Use clear headings (# ## ###)
- Include table of contents for long docs
- Add code examples where helpful
- Use screenshots for UI instructions
- Keep line length reasonable

**Code Comments:**
```python
# Good: Explains WHY
# Average pulses to reduce noise before frame capture
averaged_data = np.mean(pulse_buffer, axis=0).astype(int)

# Bad: Explains WHAT (obvious from code)
# Calculate mean and convert to integer
averaged_data = np.mean(pulse_buffer, axis=0).astype(int)
```

### Documentation Types

**User Documentation:**
- Quick Start guides
- Step-by-step tutorials
- Troubleshooting tips
- FAQ sections

**Technical Documentation:**
- Architecture diagrams
- API documentation
- Data format specifications
- Build instructions

**Clinical Documentation:**
- Workflow descriptions
- Clinical use cases
- Regulatory compliance
- Safety considerations

---

## 🧪 Testing

### Manual Testing

Follow [Test Scenarios](tests/TEST_SCENARIOS.md) and check off completed items.

### Automated Testing (Future)

We plan to add:
- Unit tests for core functions
- Integration tests for workflows
- UI automation tests
- Performance benchmarks

If you'd like to help set up automated testing, please open an issue!

---

## 🤝 Code of Conduct

### Our Standards

**Be Respectful:**
- Use welcoming and inclusive language
- Respect differing viewpoints
- Accept constructive criticism gracefully
- Focus on what's best for the project and community

**Be Professional:**
- Stay on topic in discussions
- Provide constructive feedback
- Back up claims with evidence
- Be patient with newcomers

**Be Collaborative:**
- Share knowledge openly
- Credit others' contributions
- Work together on solutions
- Help maintain a positive environment

### Unacceptable Behavior

- Harassment or discriminatory comments
- Personal attacks or trolling
- Publishing others' private information
- Spam or off-topic content
- Any illegal or unethical conduct

### Enforcement

Violations may result in:
1. Warning
2. Temporary ban
3. Permanent ban

Report concerns to: [maintainer email]

---

## 📞 Getting Help

### Questions?

- **General Questions:** Open a [Discussion](https://github.com/YOUR-USERNAME/tactile-sense/discussions)
- **Bug Reports:** Use [Issues](https://github.com/YOUR-USERNAME/tactile-sense/issues)
- **Security Issues:** Email privately to [security email]

### Resources

- [GitHub Docs](https://docs.github.com)
- [Python Style Guide](https://pep8.org)
- [Markdown Guide](https://www.markdownguide.org)

---

## 🎯 Priorities

### High Priority

1. Bug fixes (especially blocking issues)
2. Clinical workflow improvements
3. Windows executable build testing
4. Documentation clarity

### Medium Priority

1. Performance optimization
2. UI/UX improvements
3. Additional test scenarios
4. Code refactoring

### Low Priority

1. New feature additions
2. Advanced analytics
3. Experimental features

---

## 🏆 Recognition

Contributors will be:
- Listed in CHANGELOG.md
- Credited in releases
- Mentioned in documentation
- Appreciated in README.md

Thank you for contributing to TactileSense! Your efforts help improve physical therapy outcomes.

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

See [LICENSE](LICENSE) for details.
