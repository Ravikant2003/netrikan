#!/usr/bin/env python3
"""
ADB Call Script for Netrikan
Triggers voice calls using ADB over WiFi
"""
import os
import sys

def make_call(phone_number):
    """Trigger call using ADB"""
    if not phone_number:
        print("❌ No phone number configured")
        return False
    
    # Sanitize phone number (remove spaces, special chars)
    phone_number = ''.join(c for c in phone_number if c.isdigit() or c == '+')
    
    print(f"📞 Initiating call to {phone_number}...")
    
    try:
        cmd = f"adb shell am start -a android.intent.action.CALL -d tel:{phone_number}"
        result = os.system(cmd)
        
        if result == 0:
            print(f"✅ Call initiated successfully!")
            return True
        else:
            print(f"❌ Failed to initiate call")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def end_call():
    """End current call using ADB"""
    print("📴 Ending call...")
    os.system("adb shell input keyevent KEYCODE_ENDCALL")
    print("✅ Call ended")

def get_adb_status():
    """Check if ADB is connected"""
    result = os.popen("adb devices").read()
    return "device" in result.lower()

if __name__ == "__main__":
    # Get phone number from command line or use default
    phone_number = sys.argv[1] if len(sys.argv) > 1 else "123456"
    
    print("=== Netrikan ADB Call Handler ===")
    print(f"Phone: {phone_number}")
    print(f"ADB Connected: {get_adb_status()}")
    
    make_call(phone_number)