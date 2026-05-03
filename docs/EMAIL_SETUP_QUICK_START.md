# Email Notifications - Quick Start Guide

## ✅ What's Fixed
Email notifications are now working in HIGH risk scenarios! When a HIGH severity alert is triggered, guardians will receive:
- 📧 Email notification
- 📱 SMS notification
- ☎️ Phone call
- 💬 Telegram message
- 🚨 Police notification

## 🔧 Setup (5 minutes)

### Step 1: Get Gmail App Password
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification (if not already enabled)
3. Go to "App Passwords"
4. Select "Mail" and "Windows Computer"
5. Copy the 16-character password

### Step 2: Update `.env` File
Edit `backend/.env` and update these lines:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
RECIPIENT_EMAIL=default-recipient@gmail.com
```

**Example:**
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=baburaoganpatraoapte2003@gmail.com
SMTP_PASSWORD=gmeg wbyc gxbj hmhv
RECIPIENT_EMAIL=ravisaraf3000@gmail.com
```

### Step 3: Add Email to Guardians
In your mobile app or API, add email addresses to guardians:

```json
{
  "guardians": [
    {
      "phone": "+918602210205",
      "email": "guardian@example.com",
      "active": true
    }
  ]
}
```

### Step 4: Test It
Run the HIGH scenario from the mobile app:
1. Open Netrikan app
2. Go to Simulation
3. Click "HIGH" scenario button
4. Check your email inbox for the alert

## 📧 Email Content

**Subject:** 🚨 Safety Alert - Immediate Attention Required

**Body:**
```
Hello,

A safety alert has been triggered for your loved one. 
Please check on them immediately.

Location: [coordinates]
Severity: HIGH
Decision: EMERGENCY_ESCALATION

This is an automated alert from Netrikan Safety App.
```

## 🔍 Troubleshooting

### Email not received?
1. Check spam/junk folder
2. Verify email address in guardians data
3. Check backend logs: `tail -f backend/uvicorn.log`
4. Look for: "✉️ Email sent successfully to..."

### SMTP Error?
```
SMTP email send failed: [error message]
```

**Solutions:**
- Verify SMTP credentials are correct
- Check if 2-Step Verification is enabled on Gmail
- Verify App Password (not regular password)
- Check if SMTP_PORT is 587 (not 465)

### No guardians receiving email?
- Ensure `"active": true` in guardian data
- Verify email format is valid
- Check if `RECIPIENT_EMAIL` is set as fallback

## 📋 Verification Checklist

- [ ] Gmail App Password generated
- [ ] `.env` file updated with SMTP credentials
- [ ] Guardians have email addresses in app
- [ ] Backend restarted
- [ ] HIGH scenario tested
- [ ] Email received in inbox

## 🚀 Next Steps

1. **Test all three scenarios:**
   - SAFE: No notifications
   - MEDIUM: Telegram only (requires confirmation)
   - HIGH: All notifications including email

2. **Monitor logs:**
   ```bash
   tail -f backend/uvicorn.log | grep -i email
   ```

3. **Add more guardians:**
   - Each guardian can have phone + email
   - Emails are sent to all active guardians

## 📞 Support

If email notifications still aren't working:
1. Check `backend/uvicorn.log` for errors
2. Verify SMTP configuration in `.env`
3. Test with a simple email first
4. Check Gmail security settings

## 🔐 Security Notes

- ✅ Use App Password, not your regular Gmail password
- ✅ Never commit `.env` file to git
- ✅ Rotate credentials if exposed
- ✅ Use HTTPS for all API calls
- ✅ Keep SMTP_PASSWORD secure

---

**Status:** ✅ Email notifications are now fully functional in HIGH scenarios!
