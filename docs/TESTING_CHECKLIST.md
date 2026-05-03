# Three-Condition Notification System - Testing Checklist

## ✅ Pre-Test Verification

- [x] Backend running on http://192.168.1.35:8000
- [x] LLM Model: llama-3.1-8b-instant
- [x] Mobile app installed on device
- [x] App connected to backend
- [x] FCM token registered
- [x] Telegram bot configured
- [x] ADB call service configured

---

## 🧪 Test Case 1: SAFE Scenario (Normal Walk)

**Objective**: Verify no false alerts for normal conditions

### Pre-Test
- [ ] Open Netrikan app
- [ ] Navigate to Simulation screen
- [ ] Verify map is visible

### Execution
- [ ] Tap "Normal" button
- [ ] Watch map animation (should take ~10-15 seconds)
- [ ] Observe Layer 1, Layer 2, Layer 3 status updates

### Verification
- [ ] **Layer 1**: Status shows "✅ ML Model Done"
  - [ ] Risk score: ~0.28
  - [ ] Crime score: ~0.46
  - [ ] Route risk: ~0.2
  - [ ] Safety level: WARNING

- [ ] **Layer 2**: Status shows "✅ LLM Agents Done"
  - [ ] Decision: `NORMAL_MONITORING`
  - [ ] Weighted risk score: ~0.28
  - [ ] Required actions: `[]` (empty)

- [ ] **Layer 3**: Status shows "⏳ Pending" (no execution)
  - [ ] No popup appears
  - [ ] No notifications sent

- [ ] **Timeline**: Shows "Decision: NORMAL_MONITORING"

- [ ] **Backend Logs**: 
  - [ ] Shows "Decision: NORMAL_MONITORING"
  - [ ] No Layer 3 execution

### Result
- [ ] ✅ PASS - No false alerts
- [ ] ❌ FAIL - Unexpected behavior

**Notes**: _______________________________________________

---

## 🧪 Test Case 2: MEDIUM Scenario (Night+Alone)

**Objective**: Verify HITL popup and Telegram notification

### Pre-Test
- [ ] Reset simulation (tap refresh button)
- [ ] Verify map is ready

### Execution
- [ ] Tap "Night+Alone" button
- [ ] Watch map animation
- [ ] **A popup should appear** asking to confirm alert

### Verification - Before Popup
- [ ] **Layer 1**: Status shows "✅ ML Model Done"
  - [ ] Risk score: ~0.34
  - [ ] Emergency level: ELEVATED

- [ ] **Layer 2**: Status shows "✅ LLM Agents Done"
  - [ ] Decision: `ROUTE_ADJUSTMENT`
  - [ ] Weighted risk score: ~0.44
  - [ ] Required actions: `['TELEGRAM_NOTIFY', 'SAFE_PLACES_SUGGESTION', 'PUSH_NOTIFICATION']`

### Verification - Popup
- [ ] Popup title: "MEDIUM Risk Detected"
- [ ] Popup color: Orange
- [ ] Shows LLM model info: "llama-3.1-8b-instant"
- [ ] Shows decision: "ROUTE_ADJUSTMENT"
- [ ] Two buttons: "CANCEL" and "SEND ALERT"

### Execution - Confirm Alert
- [ ] Tap "SEND ALERT" button

### Verification - After Confirmation
- [ ] **Layer 3**: Status shows "✅ Actions Executed"
  - [ ] Telegram notification sent
  - [ ] Push notification sent
  - [ ] Safe places suggestion provided

- [ ] **Timeline**: Shows "Alerts sent to guardians"

- [ ] **Notifications**:
  - [ ] Check device notification panel
  - [ ] Telegram message received (if bot configured)

- [ ] **Backend Logs**:
  - [ ] Shows "Decision: ROUTE_ADJUSTMENT"
  - [ ] Shows "Layer 3 executed"
  - [ ] Shows "Telegram alert sent"

### Result
- [ ] ✅ PASS - HITL popup works, notifications sent
- [ ] ❌ FAIL - Unexpected behavior

**Notes**: _______________________________________________

---

## 🧪 Test Case 3: MEDIUM Scenario (Route Deviation)

**Objective**: Verify HITL works for different medium scenario

### Pre-Test
- [ ] Reset simulation
- [ ] Verify map is ready

### Execution
- [ ] Tap "Deviation" button
- [ ] Watch map animation
- [ ] **A popup should appear**

### Verification
- [ ] **Layer 2**: Decision: `ROUTE_ADJUSTMENT`
- [ ] **Popup**: "MEDIUM Risk Detected"
- [ ] **After confirmation**: Telegram notification sent
- [ ] **Timeline**: "Alerts sent to guardians"

### Result
- [ ] ✅ PASS - Same as Night+Alone
- [ ] ❌ FAIL - Different behavior

**Notes**: _______________________________________________

---

## 🧪 Test Case 4: HIGH Scenario (SOS)

**Objective**: Verify automatic escalation with all notifications

### Pre-Test
- [ ] Reset simulation
- [ ] Verify map is ready

### Execution
- [ ] Tap "SOS" button
- [ ] Watch map animation
- [ ] **A popup should appear** asking to confirm

### Verification - Before Popup
- [ ] **Layer 1**: Status shows "✅ ML Model Done"
  - [ ] Risk score: ~0.19
  - [ ] Emergency level: CRITICAL
  - [ ] Safety level: CRITICAL

- [ ] **Layer 2**: Status shows "✅ LLM Agents Done"
  - [ ] Decision: `EMERGENCY_ESCALATION`
  - [ ] Weighted risk score: ~0.51
  - [ ] Required actions: `['TELEGRAM_NOTIFY', 'ADB_CALL', 'POLICE_NOTIFICATION', 'PUSH_NOTIFICATION', 'SMS_GUARDIANS', 'EMAIL_GUARDIANS']`

### Verification - Popup
- [ ] Popup title: "HIGH Risk Detected"
- [ ] Popup color: Red
- [ ] Shows LLM model info
- [ ] Shows decision: "EMERGENCY_ESCALATION"

### Execution - Confirm Alert
- [ ] Tap "SEND ALERT" button

### Verification - After Confirmation
- [ ] **Layer 3**: Status shows "✅ Actions Executed"
  - [ ] Telegram notification sent
  - [ ] Phone call initiated to PHONE_NUMBER_REMOVED
  - [ ] Email sent to guardians
  - [ ] SMS sent to guardians
  - [ ] Police notification triggered
  - [ ] Push notification sent

- [ ] **Timeline**: Shows "Alerts sent to guardians"

- [ ] **Notifications**:
  - [ ] Check device notification panel
  - [ ] Telegram message received
  - [ ] Phone call initiated (if ADB configured)
  - [ ] Email received (if webhook configured)

- [ ] **Backend Logs**:
  - [ ] Shows "Decision: EMERGENCY_ESCALATION"
  - [ ] Shows "Layer 3 executed"
  - [ ] Shows "Telegram alert sent"
  - [ ] Shows "ADB call initiated"
  - [ ] Shows "POLICE NOTIFICATION SENT"

### Result
- [ ] ✅ PASS - All notifications sent
- [ ] ❌ FAIL - Some notifications missing

**Notes**: _______________________________________________

---

## 🧪 Test Case 5: HIGH Scenario (Multi-Threat)

**Objective**: Verify HIGH scenario works for different threat type

### Pre-Test
- [ ] Reset simulation
- [ ] Verify map is ready

### Execution
- [ ] Tap "Multi-Threat" button
- [ ] Watch map animation
- [ ] **A popup should appear**

### Verification
- [ ] **Layer 2**: Decision: `EMERGENCY_ESCALATION`
- [ ] **Popup**: "HIGH Risk Detected"
- [ ] **After confirmation**: All notifications sent
- [ ] **Timeline**: "Alerts sent to guardians"

### Result
- [ ] ✅ PASS - Same as SOS
- [ ] ❌ FAIL - Different behavior

**Notes**: _______________________________________________

---

## 📊 Summary Results

| Test Case | Decision | Popup | Notifications | Status |
|-----------|----------|-------|---|---|
| Normal | NORMAL_MONITORING | No | None | ⏳ |
| Night+Alone | ROUTE_ADJUSTMENT | Yes | Telegram + Push | ⏳ |
| Deviation | ROUTE_ADJUSTMENT | Yes | Telegram + Push | ⏳ |
| SOS | EMERGENCY_ESCALATION | Yes | All 6 | ⏳ |
| Multi-Threat | EMERGENCY_ESCALATION | Yes | All 6 | ⏳ |

---

## 🔍 Detailed Verification Points

### Layer 1 Monitoring
- [ ] Risk scores calculated correctly
- [ ] Crime score reflects location
- [ ] Route risk assessed
- [ ] Emergency anomaly detected for high-risk scenarios
- [ ] Safety level updated appropriately

### Layer 2 Agents
- [ ] Emergency Agent: Detects SOS keywords
- [ ] Route Agent: Detects route deviations
- [ ] Personal Agent: Detects behavioral anomalies
- [ ] Orchestrator: Combines insights correctly
- [ ] Decision logic: Correct thresholds applied

### Layer 3 Actions
- [ ] Telegram notifications sent
- [ ] Phone calls initiated (if configured)
- [ ] Email notifications sent (if configured)
- [ ] SMS sent (if configured)
- [ ] Police notification triggered (if configured)
- [ ] Push notifications sent

### UI/UX
- [ ] Map animation smooth
- [ ] Status indicators update correctly
- [ ] Popup appears at right time
- [ ] Timeline shows all events
- [ ] Results panel displays correctly

---

## 🐛 Issues Found

### Issue 1
**Description**: _______________________________________________
**Severity**: [ ] Critical [ ] High [ ] Medium [ ] Low
**Steps to Reproduce**: _______________________________________________
**Expected**: _______________________________________________
**Actual**: _______________________________________________
**Solution**: _______________________________________________

### Issue 2
**Description**: _______________________________________________
**Severity**: [ ] Critical [ ] High [ ] Medium [ ] Low
**Steps to Reproduce**: _______________________________________________
**Expected**: _______________________________________________
**Actual**: _______________________________________________
**Solution**: _______________________________________________

---

## ✅ Final Sign-Off

- [ ] All test cases passed
- [ ] No critical issues found
- [ ] System ready for production
- [ ] Documentation complete

**Tested By**: _______________________________________________
**Date**: _______________________________________________
**Time**: _______________________________________________

---

**Status**: Ready for Testing  
**Backend**: http://192.168.1.35:8000  
**LLM Model**: llama-3.1-8b-instant
