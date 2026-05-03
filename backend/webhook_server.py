#!/usr/bin/env python3
"""
Webhook server for Netrikan notifications.
Receives webhooks from backend and sends email + Telegram notifications.
"""
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import json
import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Email Configuration
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "")
EMAIL_CONFIGURED = SMTP_USER and SMTP_PASSWORD and RECIPIENT_EMAIL

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
TELEGRAM_CONFIGURED = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)

# ADB Call Configuration
ADB_CALL_NUMBER = os.environ.get("ADB_CALL_NUMBER", "123456")
ADB_SMS_NUMBER = os.environ.get("ADB_SMS_NUMBER", "123456")
ADB_ENABLED = os.environ.get("ADB_ENABLED", "true").lower() == "true"

# CallMeBot for Telegram Calls (backup)
CALLMEBOT_USERNAME = os.environ.get("CALLMEBOT_USERNAME", "")
CALLMEBOT_AUDIO_URL = os.environ.get("CALLMEBOT_AUDIO_URL", "").replace("dl=0", "dl=1")
CALLMEBOT_CONFIGURED = bool(CALLMEBOT_USERNAME and CALLMEBOT_AUDIO_URL)

# Firebase Configuration
FCM_PROJECT_ID = os.environ.get("FCM_PROJECT_ID", "")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
FCM_CONFIGURED = bool(FCM_PROJECT_ID and GOOGLE_APPLICATION_CREDENTIALS)


@app.route('/webhook/netrikan', methods=['POST'])
def handle_webhook():
    """Receive and process Netrikan notifications."""
    data = request.json
    notification_type = data.get('type', 'unknown')
    
    print(f"\n{'='*60}")
    print(f"📨 NETRIKAN WEBHOOK RECEIVED!")
    print(f"{'='*60}")
    print(f"Type: {notification_type}")
    print(f"Full Data: {json.dumps(data, indent=2)}")
    
    # Send Email
    if EMAIL_CONFIGURED:
        result = send_email_for_type(data)
        if result:
            print(f"✅ Email sent successfully!")
        else:
            print(f"❌ Email failed to send")
    else:
        print(f"⚠️ Email not configured")
    
    # Send Telegram for text messages
    if TELEGRAM_CONFIGURED:
        result = send_telegram_for_type(data)
        if notification_type == 'call':
            pass  # Call handled separately via ADB
        elif result:
            print(f"✅ Telegram message sent!")
        else:
            print(f"❌ Telegram message failed")
    
    # For calls, use ADB (instead of Telegram/CallMeBot)
    if notification_type == 'call':
        if ADB_ENABLED:
            result = make_adb_call(ADB_CALL_NUMBER)
            if result:
                print(f"📞 ADB call initiated to {ADB_CALL_NUMBER}")
            else:
                print(f"❌ ADB call failed")
        else:
            print(f"⚠️ ADB calls disabled")
    
    # SMS feature removed - using Telegram instead
    # if notification_type == 'sms' and ADB_ENABLED:
    #     sms_message = data.get('message', 'Emergency alert from Netrikan!')
    #     result = make_adb_sms(ADB_SMS_NUMBER, sms_message)
    #     if result:
    #         print(f"📱 ADB SMS sent to {ADB_SMS_NUMBER}")
    #     else:
    #         print(f"❌ ADB SMS failed")
    
    # Firebase Push Notifications
    if notification_type == 'push' and FCM_CONFIGURED:
        title = data.get('title', 'Netrikan Alert')
        body = data.get('body', 'Emergency alert!')
        user_id = data.get('user_id')
        result = send_firebase_push(title, body, user_id)
        if result:
            print(f"📲 Firebase push notification processed!")
        else:
            print(f"❌ Firebase push failed")
    
    print(f"{'='*60}\n")
    
    return jsonify({"status": "received"})


@app.route('/webhook/test', methods=['GET'])
def test_endpoint():
    """Test endpoint."""
    return jsonify({
        "status": "ok", 
        "message": "Webhook server is running!",
        "email_configured": EMAIL_CONFIGURED,
        "telegram_configured": TELEGRAM_CONFIGURED,
        "adb_enabled": ADB_ENABLED,
        "adb_call_number": ADB_CALL_NUMBER,
        "fcm_configured": FCM_CONFIGURED,
        "fcm_project_id": FCM_PROJECT_ID
    })


@app.route('/api/push/register', methods=['POST'])
def register_push_token():
    """Register device push token for Firebase notifications."""
    from services.push_tokens import register_token
    
    data = request.json
    user_id = data.get('user_id', '').strip()
    token = data.get('token', '').strip()
    platform = data.get('platform', 'mobile')
    
    if not user_id or not token:
        return jsonify({"status": "error", "detail": "user_id and token are required"}), 400
    
    count = register_token(user_id, token)
    print(f"📲 Registered push token for user_id={user_id}, platform={platform}, total_tokens={count}")
    
    return jsonify({"status": "ok", "user_id": user_id, "tokens": count})


@app.route('/api/push/test', methods=['POST'])
def test_push():
    """Send a test push notification to registered devices."""
    from services.push_tokens import get_tokens
    from services.notifiers import FCMNotifier
    
    data = request.json
    user_id = data.get('user_id', '').strip()
    title = data.get('title', 'Netrikan Test')
    body = data.get('body', 'Test push notification')
    
    if not user_id:
        return jsonify({"status": "error", "detail": "user_id is required"}), 400
    
    tokens = get_tokens(user_id)
    if not tokens:
        return jsonify({"status": "error", "detail": "No push tokens registered for this user"}), 404
    
    try:
        notifier = FCMNotifier()
        result = notifier.send(user_id, title, body)
        return jsonify({"status": "ok", "sent": len(tokens), "result": str(result)})
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Safety analysis endpoint - triggers notifications based on severity."""
    data = request.json
    user_id = data.get('user_id', 'default')
    severity = data.get('severity', 'low')
    latitude = data.get('latitude', 0)
    longitude = data.get('longitude', 0)
    text_signal = data.get('text_signal', '')
    
    # Determine notification types based on severity (no push, no SMS)
    notifications = []
    if severity == 'high':
        notifications = ['telegram', 'email', 'call']
    elif severity == 'medium':
        notifications = ['telegram', 'email']
    else:
        notifications = []
    
    results = {}
    
    # Send Telegram
    if 'telegram' in notifications:
        try:
            msg = f"🚨 SAFETY ALERT\n\nUser: {user_id}\nSeverity: {severity.upper()}\nLocation: {latitude}, {longitude}\nSignal: {text_signal}"
            send_telegram_message(TELEGRAM_CHAT_ID, msg)
            results['telegram'] = 'sent'
        except Exception as e:
            results['telegram'] = str(e)
    
    # Send Email
    if 'email' in notifications:
        try:
            email_data = {
                "type": "push", # Reusing format_push_email
                "user_id": user_id,
                "title": f"Safety Alert - {severity.upper()}",
                "body": f"User {user_id} is in a {severity} risk situation at {latitude}, {longitude}. Signal: {text_signal}"
            }
            send_email_for_type(email_data)
            results['email'] = 'sent'
        except Exception as e:
            results['email'] = str(e)
    
    # Make ADB Call
    if 'call' in notifications:
        try:
            phone = os.environ.get("ADB_CALL_NUMBER", "PHONE_NUMBER_REMOVED")
            make_adb_call(phone)
            results['call'] = 'initiated'
        except Exception as e:
            results['call'] = str(e)
    
    return jsonify({
        "status": "ok",
        "layer1_monitoring": {
            "risk_score": 0.3,
            "crime_score": 0.2,
            "route_risk": 0.1,
            "combined_risk_score": 0.3,
            "safety_level": "SAFE" if severity != "high" else "DANGER",
            "emergency_anomaly": {
                "level": "HIGH" if severity == "high" else "NONE",
                "anomaly_score": 0.8 if severity == "high" else 0.1
            },
            "thresholds": {"safe": 0.4, "warning": 0.7},
            "safe_zone_status": {"in_safe_zone": False, "nearest_distance_m": None}
        },
        "layer2_agents": {
            "decision": "HIGH_ALERT" if severity == "high" else "NORMAL_MONITORING",
            "weighted_risk_score": 0.7 if severity == "high" else 0.2,
            "required_actions": ["alert_guardian", "log_incident"] if severity == "high" else [],
            "agent_insights": {
                "emergency": {
                    "sos_detected": severity == "high",
                    "escalation_required": severity == "high",
                    "logic": "Triggered by severity level"
                }
            }
        },
        "notifications": results
    })


def send_telegram_for_type(data):
    """Send Telegram message based on notification type."""
    notification_type = data.get('type', 'unknown')
    
    # Skip calls - they're handled via ADB instead
    if notification_type == 'call':
        return True  # Call is handled separately
    
    # For other notifications, send Telegram message
    message = format_telegram_message(notification_type, data)
    return send_telegram_message(TELEGRAM_CHAT_ID, message)


def send_telegram_call(username, audio_url):
    """Make Telegram call with pre-recorded voice using CallMeBot API."""
    try:
        from urllib.parse import quote
        encoded_url = quote(audio_url, safe='')
        url = f"http://api.callmebot.com/start.php?user={username}&file={encoded_url}"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            print(f"CallMeBot response: {response.text}")
            return True
        else:
            print(f"CallMeBot error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"CallMeBot exception: {e}")
        return False


def send_telegram_message(chat_id, message):
    """Send message to Telegram bot."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return True
        else:
            print(f"Telegram API error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Telegram error: {e}")
        return False


def make_adb_call(phone_number):
    """Make phone call using ADB over WiFi."""
    try:
        import subprocess
        
        if not phone_number:
            print("❌ No phone number configured")
            return False
        
        # Sanitize phone number
        phone = ''.join(c for c in str(phone_number) if c.isdigit() or c == '+')
        
        print(f"📞 Initiating ADB call to {phone}...")
        
        # Execute ADB command to start call
        result = subprocess.run(
            ["adb", "shell", "am", "start", "-a", "android.intent.action.CALL", "-d", f"tel:{phone}"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ ADB call initiated!")
            return True
        else:
            print(f"❌ ADB call failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ ADB not found - make sure Android SDK platform-tools are installed")
        return False
    except Exception as e:
        print(f"❌ ADB error: {e}")
        return False


def make_adb_sms(phone_number, message):
    """Send SMS using ADB - opens Messages app with pre-filled message."""
    try:
        import subprocess
        
        if not phone_number:
            print("❌ No phone number configured")
            return False
        
        # Sanitize phone number (just digits, no +)
        phone = ''.join(c for c in str(phone_number) if c.isdigit())
        
        print(f"📱 Opening Messages app for {phone}...")
        print(f"   Message: {message[:50]}...")
        
        # Open Google Messages with pre-filled message
        result = subprocess.run(
            ["adb", "shell", "am", "start",
             "-n", "com.google.android.apps.messaging/com.google.android.apps.messaging.ui.conversation.LaunchConversationActivity",
             "-d", f"sms:{phone}",
             "--es", "body", message],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✅ SMS app opened!")
            print(f"   To: {phone}")
            print(f"   Message ready - tap Send to send")
            return True
        else:
            print(f"❌ ADB SMS failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ ADB not found - make sure Android SDK platform-tools are installed")
        return False
    except Exception as e:
        print(f"❌ ADB SMS error: {e}")
        return False


def send_firebase_push(title, body, user_id=None):
    """Send push notification via Firebase Cloud Messaging."""
    try:
        import firebase_admin
        from firebase_admin import messaging
        
        # Initialize Firebase if not already done
        if not firebase_admin._apps:
            cred_path = os.path.join(os.path.dirname(__file__), GOOGLE_APPLICATION_CREDENTIALS)
            if os.path.exists(cred_path):
                cred = firebase_admin.credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                print(f"❌ Firebase credentials file not found: {cred_path}")
                return False
        
        # Get device tokens from storage
        from services.push_tokens import get_tokens
        tokens = get_tokens(user_id) if user_id else []
        
        if not tokens:
            print(f"📲 Firebase push prepared but no device tokens stored")
            print(f"   Title: {title}")
            print(f"   Body: {body}")
            print(f"   User ID: {user_id or 'not provided'}")
            print(f"   Note: Mobile app needs to register first")
            return True
        
        # Send to all stored tokens for this user
        success_count = 0
        for token in tokens:
            try:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    token=token,
                )
                response = messaging.send(message)
                success_count += 1
                print(f"   ✅ Push sent to {token[:20]}...")
            except Exception as token_err:
                print(f"   ❌ Failed to send to {token[:20]}...: {token_err}")
        
        if success_count > 0:
            print(f"📲 Firebase push sent to {success_count} device(s)!")
            return True
        else:
            print(f"❌ Firebase push failed - no tokens worked")
            return False
        
    except Exception as e:
        print(f"❌ Firebase push error: {e}")
        return False


def format_telegram_message(notification_type, data):
    """Format Telegram message based on type."""
    if notification_type == 'push':
        title = data.get('title', 'Alert')
        body = data.get('body', '')
        return f"📱 *Netrikan Alert*\n\n*{title}*\n{body}"
    
    elif notification_type == 'sms':
        message = data.get('message', 'Emergency alert sent to guardian')
        location = data.get('last_location', {})
        lat = location.get('lat')
        lon = location.get('lon')
        maps = f"📍 https://maps.google.com/?q={lat},{lon}" if lat and lon else ""
        return f"💬 *Netrikan SMS Alert*\n\n{message}\n{maps}"
    
    elif notification_type == 'call':
        message = data.get('message', 'URGENT - Call the user immediately!')
        return f"📞 *Netrikan CALL - URGENT*\n\n⚠️ {message}\n\nPlease call immediately!"
    
    elif notification_type == 'police_alert':
        decision = data.get('decision', 'EMERGENCY')
        risk = data.get('risk_score', 'N/A')
        location = data.get('last_location', {})
        lat = location.get('lat')
        lon = location.get('lon')
        maps = f"📍 https://maps.google.com/?q={lat},{lon}" if lat and lon else ""
        return f"🚨 *NETRIKAN EMERGENCY*\n\n⚠️ *{decision}*\nRisk: {risk}\n{maps}"
    
    else:
        return f"🔔 *Netrikan Notification*\n\n{json.dumps(data, indent=2)}"


def send_email_for_type(data):
    """Send email notification."""
    notification_type = data.get('type', 'unknown')
    
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = RECIPIENT_EMAIL
        
        if notification_type == 'push':
            subject = "📱 Netrikan Push Notification"
            body = format_push_email(data)
        elif notification_type == 'sms':
            subject = "💬 Netrikan SMS Alert"
            body = format_sms_email(data)
        elif notification_type == 'call':
            subject = "📞 Netrikan CALL Alert - URGENT"
            body = format_call_email(data)
        elif notification_type == 'police_alert':
            subject = "🚨 Netrikan EMERGENCY ALERT"
            body = format_emergency_email(data)
        else:
            subject = f"🔔 Netrikan: {notification_type}"
            body = json.dumps(data, indent=2)
        
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Email error: {e}")
        return False


def format_push_email(data):
    body = f"""🚨 NETRIKAN PUSH NOTIFICATION

Type: Push Notification
User: {data.get('user_id', 'Unknown')}
Title: {data.get('title', 'No title')}
Message: {data.get('body', 'No message')}

---
Sent via Netrikan Safety App
"""
    return body


def format_sms_email(data):
    location = data.get('last_location', {})
    lat = location.get('lat', 'N/A')
    lon = location.get('lon', 'N/A')
    maps_link = f"https://maps.google.com/?q={lat},{lon}"
    
    body = f"""💬 NETRIKAN SMS TO GUARDIAN

To: {data.get('to', 'Unknown')}
Message: {data.get('message', 'No message')}

Location: {maps_link}

---
Sent via Netrikan Safety App
"""
    return body


def format_call_email(data):
    body = f"""📞 NETRIKAN VOICE CALL REQUEST

To: {data.get('to', 'Unknown')}
Message: {data.get('message', 'No message')}

⚠️ URGENT: This is an emergency call request!
Please call the user immediately.

---
Sent via Netrikan Safety App
"""
    return body


def format_emergency_email(data):
    location = data.get('last_location', {})
    lat = location.get('lat', 'N/A')
    lon = location.get('lon', 'N/A')
    maps_link = f"https://maps.google.com/?q={lat},{lon}"
    
    decision = data.get('decision', 'UNKNOWN')
    risk = data.get('risk_score', 'N/A')
    
    body = f"""🚨 🚨 🚨 NETRIKAN EMERGENCY ALERT 🚨 🚨 🚨

Decision: {decision}
Risk Score: {risk}

Last Known Location: {maps_link}

⚠️ IMMEDIATE ACTION REQUIRED!

---
Sent via Netrikan Safety App
Emergency Contact: {data.get('guardians_notified', 0)} guardian(s) notified
"""
    return body


if __name__ == '__main__':
    print("🚀 Starting Netrikan Webhook Server")
    print(f"   Email configured: {EMAIL_CONFIGURED}")
    print(f"   Telegram configured: {TELEGRAM_CONFIGURED}")
    print(f"   ADB enabled: {ADB_ENABLED}")
    print(f"   ADB Call Number: {ADB_CALL_NUMBER}")
    print(f"   Firebase Push: {FCM_CONFIGURED}")
    if FCM_CONFIGURED:
        print(f"   FCM Project ID: {FCM_PROJECT_ID}")
    port = int(os.environ.get("WEBHOOK_PORT", "5001"))
    print(f"   🌐 URL: http://0.0.0.0:{port}/webhook/netrikan")
    print(f"   📱 Phone URL: http://192.168.1.35:{port}/webhook/netrikan")
    app.run(host='0.0.0.0', port=port, debug=False)