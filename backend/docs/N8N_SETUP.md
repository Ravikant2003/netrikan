# Netrikan + n8n Setup Guide

## Overview
Use n8n to receive webhooks from Netrikan and send notifications via Gmail (free SMS alternative).

---

## Step 1: Set Up n8n

### Option A: Self-Hosted (Free)
```bash
# Install n8n
npm install -g n8n

# Start n8n
n8n start
# Access at http://localhost:5678
```

### Option B: Cloud (Free Tier)
1. Go to https://n8n.io/
2. Sign up for free account
3. Create new workflow

---

## Step 2: Create Webhook Workflow

### Quick Import Method
1. Open n8n
2. Click "Import from File"
3. Select `backend/docs/n8n_workflow.json`
4. The workflow will import automatically

### Manual Setup (if import fails)

1. **Add Webhook Node**
   - Add "Webhook" node
   - HTTP Method: POST
   - Path: `netrikan`
   - Copy the Webhook URL (e.g., `https://your-n8n.io/webhook/netrikan`)

2. **Add Switch/IF Node**
   - Add "Switch" node
   - Rules:
     - If `type` = "sms" → SMS output
     - If `type` = "call" → Call output  
     - If `type` = "push" → Push output
     - If `type` = "police_alert" → Police output

3. **Add Gmail Nodes** (for each output)
   - Add "Gmail" → "Send Email" node
   - Connect to respective switch outputs
   - Configure your Gmail account (OAuth required)
   - Set recipient to guardian's email

---

## Step 3: Configure Netrikan

1. Edit `backend/.env`:
```bash
# Your n8n webhook URL (from Step 2)
NETRIKAN_PUSH_WEBHOOK_URL=https://your-n8n.io/webhook/netrikan
NETRIKAN_SMS_WEBHOOK_URL=https://your-n8n.io/webhook/netrikan
NETRIKAN_CALL_WEBHOOK_URL=https://your-n8n.io/webhook/netrikan
NETRIKAN_POLICE_WEBHOOK_URL=https://your-n8n.io/webhook/netrikan
```

2. Restart backend:
```bash
cd backend
source .venv/bin/activate
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Step 4: Test Webhooks

### Check Webhook Status
```bash
curl http://localhost:8000/api/webhooks/status
```

Expected response:
```json
{
  "status": "ok",
  "configured": true,
  "endpoints": {
    "push": true,
    "sms": true,
    "call": true,
    "police": true
  }
}
```

### Test Webhook
```bash
curl -X POST http://localhost:8000/api/webhooks/test
```

---

## Step 5: Add Real SMS (Optional)

### Option A: Email to SMS (Free)
Most carriers support email to SMS:
- AT&T: `number@txt.att.net`
- Verizon: `number@vtext.com`
- T-Mobile: `number@tmomail.net`

Configure n8n Gmail node to send to these addresses!

### Option B: Twilio via n8n (Paid but reliable)
1. Get Twilio credentials
2. Add "Twilio" node in n8n
3. Connect to SMS output

---

## How It Works

```
Netrikan Backend → Webhook → n8n → Gmail → Guardian Email/SMS
```

| Notification Type | Netrikan Sends | n8n Receives | n8n Sends |
|-------------------|-----------------|---------------|-----------|
| Push | `{type: "push", ...}` | Webhook | Email to user |
| SMS | `{type: "sms", to: "+91...", message: "..."}` | Webhook | Email to guardian |
| Call | `{type: "call", to: "+91...", message: "..."}` | Webhook | Email with call request |
| Police | `{type: "police_alert", ...}` | Webhook | Emergency email |

---

## Troubleshooting

### Webhook not reaching n8n?
1. Check n8n webhook is active (play button clicked)
2. Verify URL in `.env` is correct
3. Check n8n execution history

### Gmail not sending?
1. Re-authenticate Gmail in n8n
2. Check "Less secure app access" is enabled OR use OAuth

### Test locally first?
Use ngrok to expose local n8n:
```bash
ngrok http 5678
```

---

## Quick Checklist

- [ ] n8n running and accessible
- [ ] Webhook workflow created
- [ ] Webhook URL copied
- [ ] Added to backend/.env
- [ ] Backend restarted
- [ ] Tested with `/api/webhooks/test`

---

## Cost

| Component | Cost |
|-----------|------|
| n8n (self-hosted) | Free |
| n8n (cloud free tier) | Free |
| Gmail (personal) | Free |
| Email to SMS | Free (via carrier) |

**Total: $0** 🎉