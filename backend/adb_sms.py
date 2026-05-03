#!/usr/bin/env python3
"""
ADB SMS Script for Netrikan
Sends SMS by opening Messages app with pre-filled message
"""
import subprocess
import sys

def send_sms(phone_number, message):
    """Send SMS using ADB - opens Messages app with pre-filled message"""
    try:
        # Sanitize phone number
        phone = ''.join(c for c in str(phone_number) if c.isdigit())
        
        print(f"📱 Opening Messages app...")
        print(f"   To: {phone}")
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
            print(f"   User needs to tap Send to send the message")
            return True
        else:
            print(f"❌ Failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    phone = sys.argv[1] if len(sys.argv) > 1 else "8602210205"
    message = sys.argv[2] if len(sys.argv) > 2 else "Netrikan Emergency Alert"
    
    print("=== ADB SMS Handler ===")
    send_sms(phone, message)