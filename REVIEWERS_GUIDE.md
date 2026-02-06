# Peer Reviewers Guide
**TactileSense v3.2 DMR Edition**

Thank you for volunteering as a peer reviewer! This guide will help you download, test, and provide feedback on TactileSense.

---

## 📋 Table of Contents

1. [Your Role as Reviewer](#your-role-as-reviewer)
2. [What to Review](#what-to-review)
3. [Getting Started](#getting-started)
4. [Testing Process](#testing-process)
5. [Providing Feedback](#providing-feedback)
6. [Timeline](#timeline)

---

## 👤 Your Role as Reviewer

As a peer reviewer, you'll help validate:
- **Clinical Workflow** - Does it fit PT practice needs?
- **Usability** - Is the interface intuitive?
- **Functionality** - Do all features work correctly?
- **Documentation** - Is it clear and complete?
- **Data Quality** - Are exports accurate and useful?

Your expertise is invaluable in refining this system before clinical deployment.

---

## 🎯 What to Review

### For Physical Therapists
Focus on:
- Clinical workflow integration
- Treatment documentation adequacy
- Pressure zone appropriateness
- Frame capture rate usefulness
- Data export utility for practice

### For Software Engineers
Focus on:
- Code quality and organization
- Error handling
- Performance
- Security considerations
- Technical documentation

### For Medical Device Consultants
Focus on:
- FDA 21 CFR Part 11 compliance
- Data integrity and traceability
- Audit trail completeness
- Risk mitigation
- Documentation adequacy

### For UI/UX Experts
Focus on:
- Interface intuitiveness
- Visual hierarchy
- Color scheme and contrast
- Workflow efficiency
- Accessibility

---

## 🚀 Getting Started

### STEP 1: Download from GitHub

1. Go to: https://github.com/YOUR-USERNAME/tactile-sense
2. Click "Releases" (right sidebar)
3. Download latest: `TactileSense_v3.2_Package.zip`
4. Extract to your preferred location

### STEP 2: Choose How to Run

#### Option A: Windows Executable (When Available)
```
1. Extract TactileSense_v3.2_Windows.zip
2. Double-click TactileSense_v3.2.exe
3. Click "Run anyway" if Windows shows warning
```

#### Option B: Run from Python Source
```
1. Install Python 3.12 from python.org
2. Open Command Prompt
3. Navigate to extracted folder
4. Run: pip install -r src/requirements.txt
5. Run: python src/tactile_sense_main.py
```

### STEP 3: First Launch

1. Application window opens
2. Familiarize yourself with interface
3. Read docs/QUICK_START.md
4. Try connecting Demo Simulator

---

## 🧪 Testing Process

### Phase 1: Quick Validation (15 minutes)

**Goal:** Verify basic functionality

1. **Launch Application**
   - Does it start without errors?
   - Are all interface elements visible?

2. **Connect Demo Simulator**
   - Sensor → Demo Simulator
   - Does visualization appear?
   - Do statistics update?

3. **Create Test DMR**
   - Click Record
   - Fill form with test data
   - Record for 10 seconds
   - Stop & Save
   - Does file save successfully?

4. **Review Frames**
   - DMR → Review Frames
   - Can you navigate frames?
   - Is data visible in heatmap?

5. **Export Data**
   - File → Export Data
   - Does CSV export work?
   - Can you open CSV in Excel?

**If all pass → Continue to Phase 2**  
**If any fail → Report issue and wait for fix**

### Phase 2: Comprehensive Testing (2-3 hours)

**Goal:** Complete all test scenarios

Follow: [tests/TEST_SCENARIOS.md](tests/TEST_SCENARIOS.md)

This includes:
- Installation & startup
- Demo Simulator connection
- DMR recording (simple, adjusted, paused)
- Frame Viewer navigation
- Data export (CSV, Report)
- Auto-export functionality
- DMR loading
- Pressure zone configuration
- All demo patterns
- Long session stress test
- Error handling
- File organization
- Overall usability evaluation

**Complete all 15 scenarios and fill in the feedback forms.**

### Phase 3: Real-World Usage (Optional, 1-2 weeks)

**Goal:** Test in realistic conditions

If you're a PT:
1. Try creating protocols for actual treatment types
2. Use different frame periods for different therapies
3. Review saved sessions like you would in practice
4. Export and analyze data as you would clinically
5. Note any workflow issues or missing features

**Keep notes on:**
- What works well
- What's frustrating
- What's missing
- What would you change

---

## 💬 Providing Feedback

### Where to Submit Feedback

**GitHub Issues:** https://github.com/YOUR-USERNAME/tactile-sense/issues

Choose the appropriate template:
- 🐛 **Bug Report** - Something doesn't work correctly
- ✨ **Feature Request** - Suggest a new feature
- 💭 **Feedback** - General comments and suggestions

### Bug Reports

When reporting a bug:

**Title:** Brief description  
Example: "Frame Viewer shows empty heatmap"

**Description:**
```
**What I was doing:**
1. Recorded 20-second DMR session
2. Clicked "Review Frames"
3. Frame Viewer opened

**What I expected:**
Heatmap showing pressure distribution

**What happened:**
Heatmap was blank/empty

**System Info:**
- TactileSense version: v3.2.0-baseline
- Windows: 10
- Python: 3.12.1

**Screenshots:**
[Attach if helpful]
```

### Feature Requests

When suggesting features:

**Title:** Clear feature name  
Example: "Add keyboard shortcuts for frame navigation"

**Description:**
```
**Feature:**
Keyboard shortcuts in Frame Viewer

**Use Case:**
As a PT reviewing frames, I want to use arrow keys to navigate
so I can review treatments more quickly.

**Proposed Implementation:**
- Left arrow: Previous frame
- Right arrow: Next frame
- Home: First frame
- End: Last frame
- Space: Play/Pause

**Priority:** Medium
```

### General Feedback

For overall impressions:

**Title:** "Feedback from [Your Role]"  
Example: "Feedback from Physical Therapist"

**Description:**
```
**Background:**
[Your experience/expertise]

**Overall Impression:**
[1-5 rating, overall thoughts]

**What Works Well:**
- Clear visual feedback
- Easy to understand controls
- Comprehensive data export

**What Needs Improvement:**
- Frame period slider is hard to adjust precisely
- Documentation could use more screenshots
- Would like undo button

**Suggested Priorities:**
1. Fix critical bug X
2. Improve usability of Y
3. Add feature Z

**Additional Comments:**
[Any other thoughts]
```

### Response Time

We aim to:
- Acknowledge issues within 24 hours
- Triage priority within 48 hours
- Fix critical bugs within 1 week
- Implement high-priority features in next release

---

## 📅 Timeline

### Week 1: Initial Testing
- Download and install
- Complete Phase 1 (Quick Validation)
- Report any blocking issues
- Begin Phase 2 if no blockers

### Week 2: Comprehensive Testing
- Complete Phase 2 (All Test Scenarios)
- Submit detailed feedback
- Begin Phase 3 if applicable

### Week 3: Real-World Usage (Optional)
- Use in realistic conditions
- Note workflow integration issues
- Document feature requests

### Week 4: Final Feedback
- Submit final comprehensive review
- Participate in feedback discussion
- Validate any fixes made

---

## ❓ FAQ

### Q: I found a bug. Should I keep testing?

**A:** Report it immediately via GitHub Issues. If it's blocking (prevents basic use), wait for a fix. If it's minor, continue testing and note it.

### Q: Can I suggest features not related to current version?

**A:** Absolutely! We want to hear your ideas for future versions. Use the Feature Request template.

### Q: I'm not technical. Can I still help?

**A:** Yes! Clinical and usability feedback is extremely valuable. Focus on workflow and interface testing.

### Q: How long should testing take?

**A:** Phase 1: 15 minutes, Phase 2: 2-3 hours spread over a week. Phase 3 is optional and ongoing.

### Q: Will my feedback be implemented?

**A:** We review all feedback carefully. Critical issues are fixed immediately. Features are prioritized based on impact and feasibility.

### Q: Can I share TactileSense with others?

**A:** If repository is public, yes! Share the GitHub link. If private, check with maintainers first.

### Q: Who can I contact for help?

**A:** 
- **Questions:** Open GitHub Discussion
- **Issues:** Use GitHub Issues
- **Private concerns:** Email [maintainer]

---

## 🏆 Thank You!

Your time and expertise are greatly appreciated. Peer review is essential for creating robust, clinically useful software.

**Your feedback will directly impact:**
- System usability
- Clinical adoption
- Patient outcomes
- Future development direction

Thank you for contributing to better physical therapy outcomes!

---

## 📞 Contact

- **GitHub:** https://github.com/YOUR-USERNAME/tactile-sense
- **Email:** [contact email]
- **Issues:** https://github.com/YOUR-USERNAME/tactile-sense/issues

---

**Ready to start?**  
[Download Latest Release](https://github.com/YOUR-USERNAME/tactile-sense/releases) | [View Test Scenarios](tests/TEST_SCENARIOS.md) | [Submit Feedback](https://github.com/YOUR-USERNAME/tactile-sense/issues/new)
