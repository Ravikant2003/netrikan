# Firebase Setup Guide for Netrikan Push Notifications

## Overview
This guide will help you set up Firebase Cloud Messaging (FCM) to send push notifications from Netrikan to mobile devices.

---

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add project"**
3. Project name: `netrikan` (or your preferred name)
4. Enable Google Analytics (optional - skip for now)
5. Click **"Create Project"** (wait ~1 minute)

---

## Step 2: Get Project ID

1. After creation, you'll be in the Firebase dashboard
2. Click **Project Settings** (gear icon ⚙️)
3. Copy the **Project ID** (e.g., `netrikan-abc123`)
4. Add to `backend/.env`:
   ```
   FCM_PROJECT_ID=netrikan-abc123
   ```

---

## Step 3: Set Up Android App (for mobile app)

1. In Firebase console, click **Add app** → **Android**
2. Package name: `com.netrikan.netrikan_mobile`
3. App nickname: `Netrikan`
4. Click **Register app**
5. Download `google-services.json`
6. Place it in: `mobile_app_new/android/app/google-services.json`

---

## Step 4: Create Service Account (for backend)

1. In Firebase console → **Project Settings**
2. Go to **Service Accounts** tab
3. Click **"Generate new private key"**
4. Save the JSON file as: `backend/firebase-service-account.json`
5. Add to `backend/.env`:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=backend/firebase-service-account.json
   ```

---

## Step 5: Update Mobile App for Push

In `mobile_app_new/android/app/build.gradle.kts`, make sure FCM is enabled:

```kotlin
plugins {
    id("com.google.gms.google-services")  // This enables FCM
}
```

The `google-services.json` you downloaded in Step 3 already contains the FCM configuration.

---

## Step 6: Test Push Notifications

After setup, when Layer 2 detects an emergency:
1. Backend sends push via FCM
2. User's phone receives notification
3. User sees alert on their device

---

## Troubleshooting

### "FCM not working"
- Check that `GOOGLE_APPLICATION_CREDENTIALS` points to valid JSON file
- Verify the service account has "Firebase Admin SDK" role
- Check Firebase console → Cloud Messaging for error logs

### "Device not receiving push"
- Ensure app is registered with FCM (check mobile logs)
- Verify device token is being stored
- Check if notifications are disabled on device

---

## Cost
- Firebase Cloud Messaging: **FREE** (up to 500K notifications/month)

---

## Current Status in Netrikan

The backend has FCM configured but needs:
1. ✅ Project ID (you need to create)
2. ✅ Service account JSON file (you need to download)
3. ✅ `google-services.json` in mobile app (already exists)

Once you complete these steps, push notifications will work!

---

## Quick Checklist

- [ ] Created Firebase project at console.firebase.google.com
- [ ] Copied Project ID to backend/.env
- [ ] Downloaded service account JSON → backend/firebase-service-account.json
- [ ] Updated GOOGLE_APPLICATION_CREDENTIALS in .env
- [ ] Verified google-services.json in mobile app
- [ ] Rebuilt mobile app