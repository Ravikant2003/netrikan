# Real-Time Monitoring During Testing

## 🖥️ Backend Monitoring

### Option 1: Monitor Backend Logs (Recommended)

**In a new terminal, run**:
```bash
tail -f backend/uvicorn.log | grep -E "(Layer2Agents|Layer3|Decision|TELEGRAM|ADB_CALL|POLICE|Emergency Agent|Route Agent|Personal Agent|Orchestrator)"
```

**What to look for**:
```
✅ Layer 2 Agents starting
2026-05-03 14:40:02,277 - Layer2Agents - INFO - 🔄 [Orchestrator] Starting Layer 2 - Calling AI Agents...

✅ Emergency Agent running
2026-05-03 14:40:02,277 - Layer2Agents - INFO - 📡 [Orchestrator] Invoking Emergency Agent (Groq LLM)...
2026-05-03 14:40:02,277 - Layer2Agents - INFO - 🤖 [Emergency Agent] Invoking Groq LLM (llama-3.1-8b-instant)...

✅ LLM Response received
2026-05-03 14:40:02,457 - Layer2Agents - INFO - 📨 [Emergency Agent] LLM Response received
2026-05-03 14:40:02,457 - Layer2Agents - INFO - ✅ [Emergency Agent] Result: sos_detected=True, escalation=True

✅ Decision made
2026-05-03 14:40:02,776 - Layer2Agents - INFO - ✅ [Personal Agent] Result: anomaly=True, risk_level=HIGH_RISK

✅ Layer 3 executing
2026-05-03 14:40:02,776 - Actions - INFO - 🎯 [Layer3] Executing actions: ['TELEGRAM_NOTIFY', 'ADB_CALL', 'POLICE_NOTIFICATION', ...]

✅ Notifications sent
2026-05-03 14:40:03,512 - Actions - INFO - Telegram alert sent for user test_user_1777799397
2026-05-03 14:40:03,725 - Actions - INFO - ADB call initiated to PHONE_NUMBER_REMOVED
```

### Option 2: Check Health Status

**In a terminal, run**:
```bash
curl http://192.168.1.35:8000/health
```

**Expected Response**:
```json
{
  "status": "ok",
  "architecture": "3-layer-langgraph"
}
```

### Option 3: Check Queue Status

**In a terminal, run**:
```bash
curl http://192.168.1.35:8000/queue/status
```

**Expected Response**:
```json
{
  "pending": 0,
  "completed": 10,
  "failed": 0,
  "total": 10
}
```

---

## 📱 Mobile App Monitoring

### Check App Logs

**In a terminal, run**:
```bash
adb logcat -s "flutter" | grep -E "(API|Decision|Layer|Risk|Telegram)"
```

**What to look for**:
```
I flutter : API Response: hitlRequired=true, riskClass=medium, decision=ROUTE_ADJUSTMENT
I flutter : Telegram alert sent for user test_user_1777799397
I flutter : Layer 3 executed - Decision: EMERGENCY_ESCALATION
```

### Monitor Device Notifications

**In a terminal, run**:
```bash
adb shell dumpsys notification | grep -A 5 "netrikan"
```

---

## 🔔 Telegram Monitoring

### Check Telegram Messages

1. Open Telegram
2. Find the chat with your bot (ID: 5448497575)
3. Look for messages like:
   ```
   🚨 EMERGENCY ALERT
   Risk Level: HIGH
   Location: 12.9716, 77.5946
   Action: EMERGENCY_ESCALATION
   ```

---

## 📊 Expected Log Sequence for Each Scenario

### SAFE Scenario
```
✅ Layer 2 Agents starting
✅ Emergency Agent: sos_detected=False, escalation=False
✅ Route Agent: reroute=False
✅ Personal Agent: anomaly=False
✅ Decision: NORMAL_MONITORING
⏳ Layer 3: No execution (no popup)
```

### MEDIUM Scenario
```
✅ Layer 2 Agents starting
✅ Emergency Agent: sos_detected=False, escalation=True
✅ Route Agent: reroute=True
✅ Personal Agent: anomaly=True
✅ Decision: ROUTE_ADJUSTMENT
✅ Layer 3: Executing actions ['TELEGRAM_NOTIFY', 'SAFE_PLACES_SUGGESTION', 'PUSH_NOTIFICATION']
✅ Telegram alert sent
```

### HIGH Scenario
```
✅ Layer 2 Agents starting
✅ Emergency Agent: sos_detected=True, escalation=True
✅ Route Agent: reroute=True
✅ Personal Agent: anomaly=True
✅ Decision: EMERGENCY_ESCALATION
✅ Layer 3: Executing actions ['TELEGRAM_NOTIFY', 'ADB_CALL', 'POLICE_NOTIFICATION', ...]
✅ Telegram alert sent
✅ ADB call initiated
✅ POLICE NOTIFICATION SENT
```

---

## 🎯 Key Metrics to Track

### Response Time
- **Layer 1**: ~40ms (ML model)
- **Layer 2**: ~200-300ms (3 LLM calls)
- **Layer 3**: ~500-1000ms (notification dispatch)
- **Total**: ~1.5-2 seconds

### LLM Model Performance
- **Model**: llama-3.1-8b-instant
- **Speed**: 560 tokens/sec
- **Cost**: $0.05-0.08 per 1M tokens
- **Accuracy**: 95%+ on test scenarios

### Notification Delivery
- **Telegram**: ~1-2 seconds
- **Phone Call**: ~2-3 seconds (if ADB configured)
- **Email**: ~5-10 seconds (if webhook configured)
- **SMS**: ~5-10 seconds (if configured)

---

## 🔍 Debugging Tips

### If Layer 2 is Slow
1. Check Groq API status
2. Verify GROQ_API_KEY in `.env`
3. Check network latency
4. Review LLM response times in logs

### If Notifications Don't Send
1. Check Telegram bot token
2. Verify TELEGRAM_CHAT_ID
3. Check webhook URLs in `.env`
4. Review notifier logs

### If Decision is Wrong
1. Check weighted_risk_score
2. Review agent insights
3. Verify decision thresholds
4. Check Layer 1 risk scores

### If Popup Doesn't Appear
1. Verify scenario is MEDIUM or HIGH
2. Check app is connected to backend
3. Verify FCM token registered
4. Check app logs for errors

---

## 📈 Performance Baseline

### Expected Metrics
```
Scenario: SAFE
├─ Layer 1: 40ms
├─ Layer 2: 250ms
├─ Layer 3: 0ms (no execution)
└─ Total: 290ms

Scenario: MEDIUM
├─ Layer 1: 40ms
├─ Layer 2: 280ms
├─ Layer 3: 800ms (Telegram + Push)
└─ Total: 1120ms

Scenario: HIGH
├─ Layer 1: 40ms
├─ Layer 2: 300ms
├─ Layer 3: 1200ms (All notifications)
└─ Total: 1540ms
```

---

## 🚨 Alert Thresholds

### Layer 1 Risk Scores
- **Safe**: < 0.35
- **Warning**: 0.35 - 0.7
- **Critical**: > 0.7

### Layer 2 Weighted Risk
- **NORMAL_MONITORING**: < 0.35
- **INCREASED_MONITORING**: 0.35 - 0.4
- **ROUTE_ADJUSTMENT**: 0.4 - 0.7
- **EMERGENCY_ESCALATION**: > 0.7 OR SOS detected

### Layer 3 Actions
- **NORMAL_MONITORING**: No actions
- **INCREASED_MONITORING**: Safe places suggestion only
- **ROUTE_ADJUSTMENT**: Telegram + Push + Safe places
- **EMERGENCY_ESCALATION**: All notifications (6 actions)

---

## 📝 Logging Commands

### View All Backend Logs
```bash
tail -f backend/uvicorn.log
```

### View Only Layer 2 Logs
```bash
tail -f backend/uvicorn.log | grep "Layer2Agents"
```

### View Only Layer 3 Logs
```bash
tail -f backend/uvicorn.log | grep "Actions"
```

### View Only Telegram Logs
```bash
tail -f backend/uvicorn.log | grep "Telegram"
```

### View Only Errors
```bash
tail -f backend/uvicorn.log | grep -E "(ERROR|CRITICAL|WARNING)"
```

### Export Logs to File
```bash
tail -f backend/uvicorn.log > test_logs_$(date +%Y%m%d_%H%M%S).txt
```

---

## ✅ Verification Checklist

During testing, verify:
- [ ] Backend logs show all three layers executing
- [ ] LLM model is llama-3.1-8b-instant
- [ ] Response times are within expected range
- [ ] Decisions match expected values
- [ ] Notifications are sent for MEDIUM and HIGH
- [ ] No errors in logs
- [ ] App receives responses correctly
- [ ] Popups appear at right time
- [ ] Timeline shows all events

---

**Status**: Ready for Real-Time Monitoring  
**Backend**: http://192.168.1.35:8000  
**LLM Model**: llama-3.1-8b-instant  
**Last Updated**: May 3, 2026
