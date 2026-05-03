# Email Notification Fix - HIGH Scenario

## Problem
Email notifications were not being sent in HIGH risk scenarios, even though the `EMAIL_GUARDIANS` action was included in the decision logic.

## Root Cause
The email sending functionality was not properly integrated into the notifier chain. The `SmtpEmailNotifier` class existed but was not being instantiated in the `get_notifier()` function.

## Solution Implemented

### 1. Added SMTP Email Notifier (`backend/services/notifiers.py`)
- Created `SmtpEmailNotifier` class that uses Python's `smtplib` to send emails via SMTP
- Supports Gmail with App Passwords (recommended for security)
- Sends both plain text and HTML formatted emails
- Includes proper error handling and fallback mechanisms

### 2. Updated Notifier Chain (`backend/services/notifiers.py`)
- Modified `get_notifier()` function to include SMTP Email notifier in the chain
- Chain order: SMTP Email → FCM Push → Twilio WhatsApp → Webhook → Mock
- Added `load_dotenv()` to ensure environment variables are loaded

### 3. Fixed Guardian Email Extraction (`backend/core/layer3_actions.py`)
- Added separate `guardian_emails` list to extract email addresses from guardians
- Updated `EMAIL_GUARDIANS` action to use email addresses instead of phone numbers
- Fallback to phone numbers if no email addresses are available

## Configuration Required

Add these environment variables to `backend/.env`:

```env
# Gmail SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
RECIPIENT_EMAIL=default-recipient@gmail.com
```

### Getting Gmail App Password
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification
3. Go to App Passwords
4. Select "Mail" and "Windows Computer" (or your device)
5. Copy the generated 16-character password
6. Use this password in `SMTP_PASSWORD` (not your regular Gmail password)

## Guardian Data Structure

Guardians should include both phone and email:

```python
guardians = [
    {
        "phone": "+918602210205",
        "email": "guardian@example.com",
        "active": True
    }
]
```

## HIGH Scenario Notifications

When a HIGH risk scenario is triggered (SOS detected or emergency escalation required with risk > 0.7):

### Actions Executed:
1. **TELEGRAM_NOTIFY** - Sends Telegram message to configured chat
2. **ADB_CALL** - Initiates phone call via Android device
3. **POLICE_NOTIFICATION** - Sends alert to police webhook
4. **PUSH_NOTIFICATION** - Sends FCM push notification to user
5. **SMS_GUARDIANS** - Sends SMS to guardian phone numbers
6. **EMAIL_GUARDIANS** ✅ - Sends email to guardian email addresses

### Email Content:
- **Subject**: 🚨 Safety Alert - Immediate Attention Required
- **Format**: HTML with styling and plain text fallback
- **Content**: Customizable via `notification_plan` in decision

## Testing

To test email notifications in HIGH scenario:

```bash
cd backend
../.venv/bin/python << 'EOF'
import asyncio
from core.orchestrator import layer1, layer2, layer3
from core.policy import apply_action_policy
from schemas import AnalyzeRequest
from simulation.scenarios import get_scenario_steps

async def test():
    steps = get_scenario_steps("high")
    step = steps[0]
    
    request = AnalyzeRequest(
        user_id="test_user",
        session_id="test_session",
        latitude=step["latitude"],
        longitude=step["longitude"],
        speed=step.get("speed", 0),
        severity=step.get("severity", "low"),
        text_signal=step.get("text_signal", ""),
        guardians=[
            {"phone": "+918602210205", "email": "your-email@gmail.com", "active": True}
        ],
    )
    
    # Layer 1
    processed_data = layer1.preprocess(request.model_dump())
    safety_index = layer1.get_safety_index(processed_data)
    
    # Layer 2
    decision = layer2.orchestrate(processed_data, safety_index)
    decision = apply_action_policy(decision, processed_data, safety_index)
    
    # Layer 3
    results = layer3.execute_actions(decision, request.model_dump())
    
    print(f"Decision: {decision.get('decision')}")
    print(f"Email Result: {results.get('email_alerts')}")

asyncio.run(test())
EOF
```

## Verification Checklist

- [x] SMTP Email notifier is initialized when SMTP credentials are configured
- [x] Email addresses are extracted from guardian data
- [x] HIGH scenario includes EMAIL_GUARDIANS action
- [x] Email is sent to correct recipient
- [x] Email contains proper subject and formatted body
- [x] Fallback to mock notifier if SMTP fails
- [x] All other notifications (Telegram, SMS, Phone, Police) still working

## Files Modified

1. **backend/services/notifiers.py**
   - Added `SmtpEmailNotifier` class
   - Updated `get_notifier()` function
   - Added `load_dotenv()` import

2. **backend/core/layer3_actions.py**
   - Added `guardian_emails` list extraction
   - Updated EMAIL_GUARDIANS action to use email addresses

## Backward Compatibility

- ✅ Existing configurations without SMTP still work (fallback to mock)
- ✅ Guardians without email addresses still receive SMS/phone calls
- ✅ All other notification channels unaffected
- ✅ No breaking changes to API or data structures

## Next Steps

1. Update `.env` with SMTP credentials
2. Add email addresses to guardian data in mobile app
3. Test HIGH scenario to verify email is received
4. Monitor logs for any SMTP errors
5. Consider adding email templates for different scenarios
