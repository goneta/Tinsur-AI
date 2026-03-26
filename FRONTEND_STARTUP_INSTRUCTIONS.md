# Frontend Startup Instructions

**Status:** Frontend dev server is starting  
**Expected URL:** http://localhost:3000  
**Timeline:** 1-2 minutes for first-time compilation  

---

## 📝 What Should Happen

A new **PowerShell/Command Prompt window** should have opened showing:

```
Starting Tinsur-AI Frontend...

The application will be available at:
  http://localhost:3000

Compiling... (this may take 30-60 seconds on first run)
```

Then you'll see output like:

```
> tinsur-ai-frontend@0.1.0 dev
> next dev

ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

**Once you see "ready - started server", the app is running!**

---

## 🌐 THEN OPEN IN BROWSER

Once you see the "ready" message:

1. **Open Firefox or Chrome**
2. **Go to:** http://localhost:3000
3. **You should see:** Tinsur-AI web interface
4. **Login with:**
   - Email: `admin@example.com`
   - Password: `admin123`

---

## ⏱️ Waiting Times

### First Run
- **Expected time:** 60-120 seconds
- **What's happening:** Next.js is compiling the app
- **How to tell it's done:** You see "ready - started server" message

### Subsequent Runs
- **Expected time:** < 1 second per page load
- **Why:** Hot Module Replacement (HMR) caches are active

---

## ❌ If Nothing Happens

### Check 1: Is the new window open?
- Look for a new **PowerShell** or **Command Prompt** window
- It might be behind your Firefox window
- Use **Alt+Tab** to switch between windows

### Check 2: What does it say?
- Is there a "ready - started server" message?
- Are there any error messages?
- If errors, take a screenshot and share

### Check 3: Try the API Instead
- While waiting, test the backend API
- Open: http://127.0.0.1:8000/docs
- Login and test quote calculations
- The frontend will be ready shortly

---

## 🔄 If It Still Doesn't Work

### Manual Startup

1. **Open PowerShell**
2. **Navigate to frontend:**
   ```powershell
   cd "C:\THUNDERFAM APPS\tinsur-ai"
   ```

3. **Start the dev server:**
   ```powershell
   npm run dev --workspace=tinsur-ai-frontend
   ```

4. **Wait for "ready - started server" message**

5. **Open browser:** http://localhost:3000

---

## 🔗 All URLs

| What | URL |
|------|-----|
| **Frontend App** | http://localhost:3000 |
| **Backend API** | http://127.0.0.1:8000 |
| **Swagger Docs** | http://127.0.0.1:8000/docs |

---

## 👤 Login Credentials

```
Email: admin@example.com
Password: admin123
```

---

## 💡 Tips

- **Browser won't load?** Try **Ctrl+Shift+Delete** to clear cache
- **Still blank?** Try a different browser (Chrome, Edge, Safari)
- **Port 3000 taken?** Kill other Node processes
- **Need help?** Check the **new window for error messages**

---

## ✅ Success Indicators

You'll know it's working when:
- ✅ New PowerShell window shows "ready - started server"
- ✅ http://localhost:3000 loads in the browser
- ✅ You see the Tinsur-AI login page
- ✅ You can login with admin@example.com / admin123

---

**The frontend is compiling now. This usually takes 1-2 minutes.**

**Once it's ready, you'll have the full Tinsur-AI web application!** 🎉

