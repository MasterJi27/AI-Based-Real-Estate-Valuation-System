# 🔐 Google API Key Setup Instructions

## Quick Setup

### Step 1: Get Your API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the generated API key

### Step 2: Add API Key to Your Application

**Option A: Using .env file (Recommended)**

1. Open the `.env` file:
   ```bash
   nano "/workspaces/AI-Based-Real-Estate-Valuation-System/Milestone 2/.env"
   ```

2. Uncomment and update the line:
   ```bash
   GOOGLE_API_KEY=paste_your_actual_api_key_here
   ```

3. Save the file:
   - Press `Ctrl + O` to save
   - Press `Enter` to confirm
   - Press `Ctrl + X` to exit

**Option B: Using environment variable**

```bash
export GOOGLE_API_KEY="your_actual_api_key_here"
```

### Step 3: Restart the Application

```bash
cd "/workspaces/AI-Based-Real-Estate-Valuation-System/Milestone 2"
pkill -f streamlit
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

---

## Security Best Practices

### ✅ DO:
- Keep your API key in the `.env` file (already in `.gitignore`)
- Rotate your API key if it's exposed
- Use environment variables for production
- Set API quota limits in Google Cloud Console

### ❌ DON'T:
- Commit API keys to git
- Share API keys in chat/email
- Hardcode API keys in source files
- Use the same key for dev and production

---

## Application Behavior

### With API Key:
- ✅ Full Gemini AI features enabled
- ✅ Property market analysis
- ✅ Investment recommendations
- ✅ Market trends analysis
- ✅ Real estate Q&A
- ✅ Property reports

### Without API Key:
- ⚠️ Gemini AI features use fallback content
- ✅ ML predictions still work
- ✅ EMI calculator still works
- ✅ Financial calculations still work
- ⚠️ Professional fallback content displayed for AI features

---

## Troubleshooting

### "Google API key not provided" Error

**Cause:** API key not found in environment

**Solution:**
1. Check `.env` file exists and has the key
2. Verify the key is uncommented
3. Restart the application
4. Check for typos in variable name

### "Invalid API key" Error

**Cause:** API key is incorrect or revoked

**Solution:**
1. Go to Google AI Studio
2. Generate a new API key
3. Update the `.env` file
4. Restart the application

### AI Features Show Fallback Content

**Cause:** API key missing or invalid

**Solution:**
1. Check logs: `tail -50 "Milestone 2/logs/production.log"`
2. Look for "Gemini AI service initialized successfully"
3. If not present, check API key setup

---

## Quick Commands

**Check if API key is set:**
```bash
cd "/workspaces/AI-Based-Real-Estate-Valuation-System/Milestone 2"
grep -q "^GOOGLE_API_KEY=" .env && echo "✅ API key is set" || echo "❌ API key not set"
```

**Test API key:**
```bash
cd "/workspaces/AI-Based-Real-Estate-Valuation-System/Milestone 2"
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✅ API key loaded' if os.getenv('GOOGLE_API_KEY') else '❌ No API key')"
```

**View application logs:**
```bash
tail -f "/workspaces/AI-Based-Real-Estate-Valuation-System/Milestone 2/logs/production.log"
```

---

## For Production Deployment

### Using Streamlit Cloud Secrets:

1. Go to your Streamlit Cloud dashboard
2. Select your app
3. Go to **Settings** → **Secrets**
4. Add:
   ```toml
   GOOGLE_API_KEY = "your_api_key_here"
   ```

### Using Docker/Container:

```dockerfile
# Pass as environment variable
ENV GOOGLE_API_KEY="your_api_key_here"
```

Or use Docker secrets/configs for better security.

---

## Need Help?

- **Google AI Studio:** https://makersuite.google.com/app/apikey
- **API Documentation:** https://ai.google.dev/docs
- **Gemini API Reference:** https://ai.google.dev/api/python/google/generativeai

---

**Remember:** Your `.env` file is already protected by `.gitignore` and won't be committed to GitHub! 🔒
