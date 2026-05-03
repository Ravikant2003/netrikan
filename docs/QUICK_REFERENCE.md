# Netrikan Safety App - Quick Reference Guide

## 🎯 Three-Condition Notification System

### Condition 1: SAFE ✅
```
Risk Score: < 0.35
Decision: NORMAL_MONITORING
Actions: None
Example: Normal driving, low speed, no distress
```

### Condition 2: MEDIUM 🟡
```
Risk Score: 0.35 - 0.7
Decision: ROUTE_ADJUSTMENT
Actions: Telegram + Push + Safe Places
Requires: Human confirmation (HITL)
Example: Route deviation, medium severity, uneasy feeling
```

### Condition 3: HIGH 🔴
```
Risk Score: > 0.7 OR SOS detected
Decision: EMERGENCY_ESCALATION
Actions: Telegram + Phone + Email + SMS + Police
Automatic: No confirmation needed
Example: SOS text, high severity, route deviation
```

## 🚀 Quick Start

### Start Backend
```bash
cd backend
source .venv/bin/activate
python main.py
```

### Test Scenarios
```bash
# SAFE
curl -X POST http://192.168.1.35:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","latitude":12.9716,"longitude":77.5946,"speed":12,"severity":"low","text_signal":""}'

# MEDIUM
curl -X POST http://192.168.1.35:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","latitude":12.9716,"longitude":77.5946,"destination":{"lat":12.9616,"lon":77.5846},"speed":25,"severity":"medium","route_deviation":true,"text_signal":"I feel uneasy"}'

# HIGH
curl -X POST http://192.168.1.35:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","latitude":12.9716,"longitude":77.5946,"destination":{"lat":12.9616,"lon":77.5846},"speed":5,"severity":"high","route_deviation":true,"text_signal":"SOS help emergency"}'
```

## 📊 Key Metrics

| Metric | Value |
|--------|-------|
| LLM Model | llama-3.1-8b-instant |
| Speed | 560 tokens/sec |
| Cost | $0.05-0.08 per 1M tokens |
| Response Time | ~1.5-2 seconds |
| Accuracy | 95%+ (based on test scenarios) |

## 🔧 Configuration

### Environment Variables
```bash
GROQ_API_KEY=YOUR_GROQ_API_KEY_HERE
NETRIKAN_LLM_MODEL=llama-3.1-8b-instant
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
TELEGRAM_CHAT_ID=5448497575
ADB_CALL_NUMBER=PHONE_NUMBER_REMOVED
```

### Backend URL
```
http://192.168.1.35:8000
```

### Mobile App IP
```
192.168.1.38
```

## 📱 Mobile App Testing

1. **Build APK**
   ```bash
   cd mobile_app_new
   flutter build apk --release
   ```

2. **Install on Device**
   ```bash
   flutter install
   ```

3. **Test Scenarios**
   - Open app
   - Select scenario (Safe, Medium, High)
   - Verify notifications received

## 🔍 Monitoring

### Check Backend Logs
```bash
tail -f backend/uvicorn.log
```

### Health Check
```bash
curl http://192.168.1.35:8000/health
```

### Queue Status
```bash
curl http://192.168.1.35:8000/queue/status
```

## 🐛 Troubleshooting

### Issue: LLM Errors
**Solution**: Check GROQ_API_KEY in `.env`

### Issue: Notifications Not Sending
**Solution**: Verify Telegram bot token and chat ID

### Issue: Mobile App Can't Connect
**Solution**: Ensure backend IP is 192.168.1.35:8000

### Issue: High Response Times
**Solution**: Check network latency, Groq API status

## 📚 File Structure

```
backend/
├── core/
│   ├── layer1_monitoring.py    # Risk assessment
│   ├── layer2_agents.py        # LLM decision logic
│   ├── layer3_actions.py       # Notification execution
│   └── policy.py               # Action filtering
├── services/
│   ├── notifiers.py            # Telegram, Email, SMS
│   ├── action_processor.py     # Queue management
│   └── incidents.py            # Incident tracking
├── main.py                     # FastAPI server
└── .env                        # Configuration

mobile_app_new/
├── lib/
│   ├── services/api_service.dart
│   ├── screens/setup_screen.dart
│   └── screens/simulation_screen.dart
└── pubspec.yaml
```

## 🎓 Understanding the System

### Layer 1: Monitoring
- Analyzes location, speed, severity
- Calculates risk scores
- Detects anomalies

### Layer 2: Agents
- Emergency Agent: Detects SOS/escalation
- Route Agent: Analyzes route safety
- Personal Agent: Detects behavioral anomalies
- Orchestrator: Combines insights into decision

### Layer 3: Actions
- Executes notifications based on decision
- Manages action queue
- Tracks delivery status

## 📞 Support

For issues or questions:
1. Check logs: `backend/uvicorn.log`
2. Verify configuration: `backend/.env`
3. Test health: `curl http://192.168.1.35:8000/health`
4. Review documentation: `IMPLEMENTATION_SUMMARY.md`

---

**Last Updated**: May 3, 2026  
**Status**: ✅ Production Ready
