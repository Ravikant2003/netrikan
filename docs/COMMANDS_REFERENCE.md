# Complete Commands Reference - Netrikan Safety App

## 🔗 Device Connection Commands

### USB Connection (Recommended for First Time)

#### Enable USB Debugging on Device
```bash
# On Android Device:
# 1. Settings → About Phone
# 2. Tap "Build Number" 7 times
# 3. Settings → Developer Options
# 4. Enable "USB Debugging"
# 5. Enable "USB File Transfer Mode"
```

#### Check USB Connection
```bash
adb devices
```

**Expected Output**:
```
List of devices attached
8PBEE6IVWSK7GAXC        device
```

#### Install App via USB
```bash
adb install -r mobile_app_new/build/app/outputs/flutter-apk/app-release.apk
```

**Expected Output**:
```
Performing Streamed Install
Success
```

#### Launch App via USB
```bash
adb shell am start -n com.netrikan.netrikan_mobile/com.netrikan.netrikan_mobile.MainActivity
```

---

### Wireless Connection (After USB Setup)

#### Get Device IP Address
```bash
adb shell ip addr show wlan0 | grep "inet " | awk '{print $2}' | cut -d/ -f1
```

**Expected Output**:
```
192.168.1.38
```

#### Enable Wireless Mode (via USB)
```bash
adb tcpip 5555
```

**Expected Output**:
```
restarting in TCP mode port: 5555
```

#### Disconnect USB Cable
```bash
# Physically disconnect USB cable from device
```

#### Connect Wirelessly
```bash
adb connect 192.168.1.38:5555
```

**Expected Output**:
```
connected to 192.168.1.38:5555
```

#### Verify Wireless Connection
```bash
adb devices
```

**Expected Output**:
```
List of devices attached
192.168.1.38:5555      device
```

#### Install App via Wireless
```bash
adb install -r mobile_app_new/build/app/outputs/flutter-apk/app-release.apk
```

#### Launch App via Wireless
```bash
adb shell am start -n com.netrikan.netrikan_mobile/com.netrikan.netrikan_mobile.MainActivity
```

---

### Reconnect Wireless (After Restart)

#### Quick Reconnect
```bash
adb connect 192.168.1.38:5555
```

#### Verify Connection
```bash
adb devices
```

#### Launch App
```bash
adb shell am start -n com.netrikan.netrikan_mobile/com.netrikan.netrikan_mobile.MainActivity
```

---

## 🖥️ Backend Commands

### Start Backend Server
```bash
cd backend
source .venv/bin/activate
python main.py
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
2026-05-03 14:35:56,821 - Netrikan-Core - INFO - Initializing Netrikan 3-Layer Agentic Architecture with LangGraph
INFO:     Application startup complete.
```

### Stop Backend Server
```bash
# Press Ctrl+C in the terminal running the backend
```

### Check Backend Health
```bash
curl http://192.168.1.35:8000/health
```

**Expected Output**:
```json
{
  "status": "ok",
  "architecture": "3-layer-langgraph"
}
```

### Check Queue Status
```bash
curl http://192.168.1.35:8000/queue/status
```

**Expected Output**:
```json
{
  "pending": 0,
  "completed": 10,
  "failed": 0,
  "total": 10
}
```

### Restart Backend
```bash
# Kill existing process
lsof -i :8000
kill -9 <PID>

# Start backend again
cd backend
source .venv/bin/activate
python main.py
```

---

## 📊 Logging & Monitoring Commands

### View All Backend Logs
```bash
tail -f backend/uvicorn.log
```

### View Layer 2 Logs Only
```bash
tail -f backend/uvicorn.log | grep "Layer2Agents"
```

### View Layer 3 Logs Only
```bash
tail -f backend/uvicorn.log | grep "Actions"
```

### View Decision Logs
```bash
tail -f backend/uvicorn.log | grep "Decision:"
```

### View Telegram Logs
```bash
tail -f backend/uvicorn.log | grep "Telegram"
```

### View All Important Logs
```bash
tail -f backend/uvicorn.log | grep -E "(Layer2Agents|Layer3|Decision|TELEGRAM|ADB_CALL|POLICE)"
```

### View Error Logs Only
```bash
tail -f backend/uvicorn.log | grep -E "(ERROR|CRITICAL|WARNING)"
```

### Export Logs to File
```bash
tail -f backend/uvicorn.log > test_logs_$(date +%Y%m%d_%H%M%S).txt
```

### View App Logs
```bash
adb logcat -s "flutter"
```

### View App API Logs
```bash
adb logcat -s "flutter" | grep -E "(API|Decision|Layer|Risk)"
```

### View App FCM Logs
```bash
adb logcat -s "flutter" | grep "FCM"
```

### Clear Device Logs
```bash
adb logcat -c
```

---

## 🧪 Testing Commands

### Test SAFE Scenario
```bash
# On device: Tap "Normal" button
# Monitor backend logs:
tail -f backend/uvicorn.log | grep "Decision:"

# Expected: Decision: NORMAL_MONITORING
# Expected: No popup, no notifications
```

### Test MEDIUM Scenario
```bash
# On device: Tap "Night+Alone" button
# Monitor backend logs:
tail -f backend/uvicorn.log | grep -E "(Decision:|TELEGRAM)"

# Expected: Decision: ROUTE_ADJUSTMENT
# Expected: Orange popup appears
# On device: Tap "SEND ALERT"
# Expected: Telegram notification received
```

### Test HIGH Scenario
```bash
# On device: Tap "SOS" button
# Monitor backend logs:
tail -f backend/uvicorn.log | grep -E "(Decision:|TELEGRAM|ADB_CALL|POLICE)"

# Expected: Decision: EMERGENCY_ESCALATION
# Expected: Red popup appears
# On device: Tap "SEND ALERT"
# Expected: All notifications sent
```

### Send Test API Request
```bash
curl -X POST http://192.168.1.35:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "speed": 12,
    "severity": "low",
    "text_signal": ""
  }'
```

### Send Test MEDIUM Request
```bash
curl -X POST http://192.168.1.35:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "destination": {"lat": 12.9616, "lon": 77.5846},
    "speed": 25,
    "severity": "medium",
    "route_deviation": true,
    "text_signal": "I feel uneasy"
  }'
```

### Send Test HIGH Request
```bash
curl -X POST http://192.168.1.35:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "destination": {"lat": 12.9616, "lon": 77.5846},
    "speed": 5,
    "severity": "high",
    "route_deviation": true,
    "text_signal": "SOS help emergency attack"
  }'
```

---

## 🔧 Troubleshooting Commands

### Check if Port 8000 is in Use
```bash
lsof -i :8000
```

### Kill Process Using Port 8000
```bash
kill -9 <PID>
```

### Restart ADB Server
```bash
adb kill-server
adb start-server
adb devices
```

### Force Stop App
```bash
adb shell am force-stop com.netrikan.netrikan_mobile
```

### Restart App
```bash
adb shell am force-stop com.netrikan.netrikan_mobile
adb shell am start -n com.netrikan.netrikan_mobile/com.netrikan.netrikan_mobile.MainActivity
```

### Check Device Storage
```bash
adb shell df -h
```

### Check Device Memory
```bash
adb shell free -h
```

### Get Device Info
```bash
adb shell getprop ro.build.version.release
adb shell getprop ro.product.model
```

### Check Network Connection
```bash
# On device
adb shell ping -c 4 192.168.1.35

# Or from Mac
ping 192.168.1.38
```

### Verify Backend Connectivity
```bash
curl -v http://192.168.1.35:8000/health
```

---

## 📱 Device Management Commands

### List All Connected Devices
```bash
adb devices -l
```

### Get Device Serial Number
```bash
adb get-serialno
```

### Get Device IP Address
```bash
adb shell ip addr show wlan0 | grep "inet " | awk '{print $2}' | cut -d/ -f1
```

### Reboot Device
```bash
adb reboot
```

### Reboot Device to Bootloader
```bash
adb reboot bootloader
```

### Take Screenshot
```bash
adb shell screencap -p /sdcard/screenshot.png
adb pull /sdcard/screenshot.png
```

### Record Screen
```bash
adb shell screenrecord /sdcard/recording.mp4
# Press Ctrl+C to stop
adb pull /sdcard/recording.mp4
```

### Open Device Settings
```bash
adb shell am start -a android.intent.action.MAIN -n com.android.settings/com.android.settings.Settings
```

---

## 🔐 Configuration Commands

### View Environment Variables
```bash
cat backend/.env
```

### Edit Environment Variables
```bash
nano backend/.env
```

### Check Groq API Key
```bash
grep GROQ_API_KEY backend/.env
```

### Check Telegram Bot Token
```bash
grep TELEGRAM_BOT_TOKEN backend/.env
```

### Check Backend IP Configuration
```bash
grep -E "192.168|localhost|0.0.0.0" backend/.env
```

---

## 📈 Performance Monitoring Commands

### Monitor CPU Usage
```bash
# Backend CPU
ps aux | grep python | grep main.py

# Device CPU
adb shell top -n 1 | head -20
```

### Monitor Memory Usage
```bash
# Backend memory
ps aux | grep python | grep main.py

# Device memory
adb shell free -h
```

### Monitor Network Traffic
```bash
# Device network
adb shell netstat -an | grep ESTABLISHED
```

### Check Response Time
```bash
time curl http://192.168.1.35:8000/health
```

---

## 🚀 Complete Setup Workflow (Copy & Paste)

### Terminal 1: Start Backend
```bash
cd ~/Desktop/Netrikan_02/backend
source .venv/bin/activate
python main.py
```

### Terminal 2: Connect Device (USB)
```bash
# First time setup
adb devices
adb install -r ~/Desktop/Netrikan_02/mobile_app_new/build/app/outputs/flutter-apk/app-release.apk
adb shell am start -n com.netrikan.netrikan_mobile/com.netrikan.netrikan_mobile.MainActivity
```

### Terminal 2: Connect Device (Wireless - After USB Setup)
```bash
# Enable wireless (via USB first)
adb tcpip 5555

# Disconnect USB cable, then:
adb connect 192.168.1.38:5555
adb devices

# Install and launch
adb install -r ~/Desktop/Netrikan_02/mobile_app_new/build/app/outputs/flutter-apk/app-release.apk
adb shell am start -n com.netrikan.netrikan_mobile/com.netrikan.netrikan_mobile.MainActivity
```

### Terminal 3: Monitor Backend Logs
```bash
tail -f ~/Desktop/Netrikan_02/backend/uvicorn.log | grep -E "(Layer2Agents|Layer3|Decision|TELEGRAM)"
```

### Terminal 4: Monitor App Logs
```bash
adb logcat -s "flutter" | grep -E "(API|Decision|Layer)"
```

---

## 📋 Quick Command Cheat Sheet

| Task | Command |
|------|---------|
| Start Backend | `cd backend && source .venv/bin/activate && python main.py` |
| Check Backend | `curl http://192.168.1.35:8000/health` |
| Connect USB | `adb devices` |
| Install App | `adb install -r mobile_app_new/build/app/outputs/flutter-apk/app-release.apk` |
| Launch App | `adb shell am start -n com.netrikan.netrikan_mobile/com.netrikan.netrikan_mobile.MainActivity` |
| Enable Wireless | `adb tcpip 5555` |
| Connect Wireless | `adb connect 192.168.1.38:5555` |
| View Logs | `tail -f backend/uvicorn.log` |
| Filter Logs | `tail -f backend/uvicorn.log \| grep "Decision:"` |
| View App Logs | `adb logcat -s "flutter"` |
| Restart App | `adb shell am force-stop com.netrikan.netrikan_mobile && adb shell am start -n com.netrikan.netrikan_mobile/com.netrikan.netrikan_mobile.MainActivity` |
| Get Device IP | `adb shell ip addr show wlan0 \| grep "inet " \| awk '{print $2}' \| cut -d/ -f1` |
| Restart ADB | `adb kill-server && adb start-server` |

---

## 🎯 Testing Workflow Commands

### Step 1: Setup (First Time)
```bash
# Terminal 1
cd ~/Desktop/Netrikan_02/backend
source .venv/bin/activate
python main.py

# Terminal 2
adb devices
adb install -r ~/Desktop/Netrikan_02/mobile_app_new/build/app/outputs/flutter-apk/app-release.apk
adb shell am start -n com.netrikan.netrikan_mobile/com.netrikan.netrikan_mobile.MainActivity

# Terminal 3
tail -f ~/Desktop/Netrikan_02/backend/uvicorn.log | grep -E "(Layer2Agents|Layer3|Decision)"

# Terminal 4
adb logcat -s "flutter" | grep -E "(API|Decision)"
```

### Step 2: Test SAFE
```bash
# On device: Tap "Normal"
# In Terminal 3: Watch for "Decision: NORMAL_MONITORING"
```

### Step 3: Test MEDIUM
```bash
# On device: Tap "Night+Alone"
# In Terminal 3: Watch for "Decision: ROUTE_ADJUSTMENT"
# On device: Tap "SEND ALERT"
# Check Telegram for notification
```

### Step 4: Test HIGH
```bash
# On device: Tap "SOS"
# In Terminal 3: Watch for "Decision: EMERGENCY_ESCALATION"
# On device: Tap "SEND ALERT"
# Check all notifications
```

---

## 📞 Emergency Commands

### If Backend Crashes
```bash
# Kill and restart
lsof -i :8000
kill -9 <PID>
cd backend && source .venv/bin/activate && python main.py
```

### If Device Disconnects
```bash
# Reconnect
adb kill-server
adb start-server
adb devices
adb connect 192.168.1.38:5555  # If wireless
```

### If App Freezes
```bash
# Force stop and restart
adb shell am force-stop com.netrikan.netrikan_mobile
adb shell am start -n com.netrikan.netrikan_mobile/com.netrikan.netrikan_mobile.MainActivity
```

### If Notifications Don't Work
```bash
# Check logs
tail -f backend/uvicorn.log | grep -i "telegram\|error"
adb logcat -s "flutter" | grep -i "fcm\|notification"
```

---

**Last Updated**: May 3, 2026  
**Status**: ✅ All Commands Tested and Working
