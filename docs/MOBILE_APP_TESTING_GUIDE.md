# Mobile App Testing Guide - Three-Condition Notification System

## 📱 App Status
✅ **App Installed**: Netrikan Safety App is installed on device  
✅ **Backend Connected**: App is connected to http://192.168.1.35:8000  
✅ **FCM Token Registered**: Push notifications are enabled  

## 🎯 Testing the Three Conditions

The mobile app has a **Simulation Screen** with scenario buttons to test all three notification levels.

### How to Access Simulation Screen
1. Open the Netrikan Safety App
2. Navigate to the **Simulation** tab (bottom navigation)
3. You'll see scenario buttons organized by severity level

### Test Scenario 1: SAFE (No Actions) ✅
**Scenario**: Normal Walk  
**Expected Behavior**: No notifications, just logging

**Steps**:
1. Tap the **"Normal"** button
2. Watch the map simulation run
3. **Expected Result**: 
   - Decision: `NORMAL_MONITORING`
   - No alerts or notifications
   - Timeline shows: "Decision: NORMAL_MONITORING"

---

### Test Scenario 2: MEDIUM (Human-in-the-Loop) 🟡
**Scenarios**: Night+Alone, Route Deviation  
**Expected Behavior**: Telegram notification + confirmation popup

**Steps for "Night+Alone"**:
1. Tap the **"Night+Alone"** button
2. Watch the map simulation
3. **A popup will appear** asking to confirm sending alerts
4. **Expected Result**:
   - Popup shows: "MEDIUM Risk Detected"
   - Options: "CANCEL" or "SEND ALERT"
   - If you tap "SEND ALERT":
     - Telegram notification sent
     - Timeline shows: "Alerts sent to guardians"
     - Decision: `ROUTE_ADJUSTMENT`
     - Actions: `['TELEGRAM_NOTIFY', 'SAFE_PLACES_SUGGESTION', 'PUSH_NOTIFICATION']`

**Steps for "Route Deviation"**:
1. Tap the **"Deviation"** button
2. Same flow as above
3. **Expected Result**: Same as Night+Alone

---

### Test Scenario 3: HIGH (Automatic Response) 🔴
**Scenarios**: SOS, Multi-Threat  
**Expected Behavior**: Automatic alerts without confirmation

**Steps for "SOS"**:
1. Tap the **"SOS"** button
2. Watch the map simulation
3. **A popup will appear** asking to confirm
4. **Expected Result**:
   - Popup shows: "HIGH Risk Detected"
   - If you tap "SEND ALERT":
     - Telegram notification sent immediately
     - Phone call initiated to PHONE_NUMBER_REMOVED
     - Email sent to guardians
     - SMS sent to guardians
     - Police notification triggered
     - Timeline shows: "Alerts sent to guardians"
     - Decision: `EMERGENCY_ESCALATION`
     - Actions: `['TELEGRAM_NOTIFY', 'ADB_CALL', 'POLICE_NOTIFICATION', 'PUSH_NOTIFICATION', 'SMS_GUARDIANS', 'EMAIL_GUARDIANS']`

**Steps for "Multi-Threat"**:
1. Tap the **"Multi-Threat"** button
2. Same flow as SOS
3. **Expected Result**: Same as SOS

---

## 📊 What to Verify

### For Each Scenario, Check:

1. **Map Animation**
   - ✅ Route displays on map
   - ✅ User position moves along route
   - ✅ Speed slider controls animation speed

2. **Layer 1 (Monitoring)**
   - ✅ Status shows "✅ ML Model Done"
   - ✅ Risk scores displayed
   - ✅ Crime score calculated
   - ✅ Route risk assessed

3. **Layer 2 (LLM Agents)**
   - ✅ Status shows "✅ LLM Agents Done"
   - ✅ Shows which agent is running (Emergency, Route, Personal)
   - ✅ Decision displayed (NORMAL_MONITORING, ROUTE_ADJUSTMENT, EMERGENCY_ESCALATION)
   - ✅ Weighted risk score shown

4. **Layer 3 (Actions)**
   - ✅ For MEDIUM: Telegram notification sent
   - ✅ For HIGH: All notifications sent (Telegram, Phone, Email, SMS, Police)
   - ✅ Status shows "✅ Actions Executed"

5. **Notifications**
   - ✅ Check device notification panel
   - ✅ Telegram bot should send messages
   - ✅ Phone call should be initiated (if ADB configured)

6. **Timeline**
   - ✅ Shows sequence of events
   - ✅ Timestamps for each step
   - ✅ Final decision logged

---

## 🔧 Troubleshooting

### Issue: App Won't Connect to Backend
**Solution**:
1. Check backend is running: `ps aux | grep python`
2. Verify IP: Should be `192.168.1.35:8000`
3. Check network: Device should be on same WiFi as Mac
4. Restart app if needed

### Issue: No Notifications Received
**Solution**:
1. Check Telegram bot token in `.env`
2. Verify TELEGRAM_CHAT_ID is correct
3. Check backend logs: `tail -f backend/uvicorn.log`
4. Verify FCM token registered (check app logs)

### Issue: Popup Doesn't Appear
**Solution**:
1. Make sure you're on MEDIUM or HIGH scenario
2. Check that simulation is running
3. Verify backend is responding (check logs)

### Issue: Wrong Decision Type
**Solution**:
1. Check weighted_risk_score in response
2. Verify scenario is correct
3. Check Layer 2 agent insights
4. Review decision logic thresholds

---

## 📈 Expected Results Summary

| Scenario | Decision | Risk Score | Actions | Notifications |
|----------|----------|-----------|---------|---|
| Normal | NORMAL_MONITORING | 0.28 | None | None |
| Night+Alone | ROUTE_ADJUSTMENT | 0.44 | 3 | Telegram + Push |
| Deviation | ROUTE_ADJUSTMENT | 0.44 | 3 | Telegram + Push |
| SOS | EMERGENCY_ESCALATION | 0.51 | 6 | All (Telegram, Phone, Email, SMS, Police) |
| Multi-Threat | EMERGENCY_ESCALATION | 0.51 | 6 | All (Telegram, Phone, Email, SMS, Police) |

---

## 🎬 Full Test Sequence

**Recommended Order**:
1. **Start with SAFE** (Normal) - Verify no false alerts
2. **Test MEDIUM** (Night+Alone) - Verify HITL popup works
3. **Test HIGH** (SOS) - Verify auto-escalation works
4. **Repeat** with different scenarios to verify consistency

**Expected Time**: ~5-10 minutes per scenario

---

## 📝 Notes

- **HITL (Human-in-the-Loop)**: For MEDIUM and HIGH scenarios, a popup appears asking for confirmation
- **Auto-Escalation**: HIGH scenarios automatically send alerts after confirmation
- **Session ID**: Each simulation has a unique session ID for tracking
- **Timeline**: All events are logged in the timeline for debugging

---

## 🚀 Next Steps After Testing

1. ✅ Verify all three conditions work correctly
2. ✅ Check notification delivery
3. ✅ Confirm decision logic is correct
4. ✅ Review Layer 2 agent insights
5. ✅ Export results for analysis

---

**Status**: Ready for Testing  
**Backend**: Running on http://192.168.1.35:8000  
**LLM Model**: llama-3.1-8b-instant  
**Last Updated**: May 3, 2026
