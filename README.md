# Telegram Onboarding Bot (Ready to Deploy)

This package contains a ready-to-deploy Telegram bot that collects Pocket Option UIDs and allows manual verification by the admin.

## Files
- `main.py` - bot code
- `requirements.txt` - Python dependencies
- `Procfile` - for Render (start command)
- `bot_data.json` - created automatically when the bot first runs

## How to deploy on Render
1. Create a new GitHub repo and push these files, or upload directly to Render via their web UI.
2. On Render: Create a new **Web Service**.
   - Connect your repository or upload the ZIP contents.
   - Set the **Build Command**: `pip install -r requirements.txt`
   - Set the **Start Command**: `python main.py` (Render will use Procfile if present)
3. Set Environment Variables (recommended - safer than hardcoding):
   - `TELEGRAM_TOKEN` (optional if you left it in the file)
   - `ADMIN_ID` (optional)
   - `BROKER_LINK` (optional)
   - `BONUS_CODE` (optional)
4. Deploy. The bot will run 24/7 and will respond to users.

## Usage
- User: `/start` — shows signup link and instructions.
- User: send `UID 1234567` or just `1234567` — bot stores the UID and notifies admin.
- Admin: `/verify <telegram_id>` — marks user as VIP and sends verification message to that user.
- Admin: `/myid` — returns your Telegram id (useful for confirming admin id).

If you want me to push this to a GitHub repo for you or directly deploy to Render, tell me and I can continue.
