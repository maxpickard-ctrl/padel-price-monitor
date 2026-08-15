# Padel Outlet Price Monitor - Quick Start (10 Minutes)

## TL;DR Setup

### 1. Install Requirements (2 min)
```bash
# Clone/download files to a folder
mkdir padel-monitor && cd padel-monitor

# Install Python packages
pip3 install requests beautifulsoup4 selenium flask flask-cors

# Download ChromeDriver: https://chromedriver.chromium.org/
# Place it in the same folder
```

### 2. Configure Email (3 min)
```bash
# Get Gmail App Password:
# 1. Go to https://myaccount.google.com/apppasswords
# 2. Create one (copy the 16-char password)
# 3. Save it safely
```

### 3. Test It (5 min)
```bash
python3 price_monitor.py your_email@gmail.com "xxxx xxxx xxxx xxxx"
```

Watch it:
- Scrape padeloutlet.ae ✓
- Check competitors ✓
- Send email to gm@padelart.ae ✓

---

## What Happens Next

### Option A: Run Daily Automatically (Recommended)

**On Mac/Linux:**
```bash
# Edit crontab
crontab -e

# Add this line (run 6 AM daily):
0 6 * * * cd /path/to/padel-monitor && python3 price_monitor.py your_email@gmail.com "xxxx xxxx xxxx xxxx"
```

**On Windows:**
Use Task Scheduler (see SETUP.md for details)

### Option B: View Dashboard

```bash
# Terminal 1 - Start API server
python3 api_server.py
# Runs on http://localhost:5000

# Terminal 2 - View API data
curl http://localhost:5000/api/price-data
```

---

## Expected Email Output

Daily at 6 AM, you'll get an email like:

```
Subject: Padel Outlet Price Alert - 2024-01-15

Undercuts Found: 3

| Product              | Your Price | Competitor    | Their Price | Difference |
|----------------------|------------|----------------|-------------|-----------|
| Royal Padel Seventh  | 399 AED    | padel4less.ae  | 349 AED     | -50 AED   |
| Bullpadel Vertex    | 449 AED    | padelsouq.com  | 419 AED     | -30 AED   |
| Dunlop Blaze        | 259 AED    | racketshop.ae  | 239 AED     | -20 AED   |
```

---

## Customization Quick Fixes

### Website changed layout?
Edit `price_monitor.py` lines 125-135, update CSS class names after inspecting website.

### Add/remove competitor?
Edit top of `price_monitor.py`:
```python
COMPETITORS = {
    "padelsouq": "https://www.padelsouq.com",
    # add or remove here
}
```

### Change alert time?
Edit cron: change `0 6` to your preferred time (hour minute format)

---

## Database

Automatically creates `padel_prices.db` with:
- ✓ All products from padeloutlet.ae
- ✓ Competitor prices (last 30 days)
- ✓ All price alerts (searchable by date/competitor)

Query it:
```bash
sqlite3 padel_prices.db "SELECT * FROM price_alerts ORDER BY alert_date DESC LIMIT 5;"
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Email not sent | Check Gmail app password is correct, enable 2FA |
| No products found | Update CSS selectors in price_monitor.py (inspect website) |
| Timeout errors | Increase timeout in `requests.get()` calls (change 10 to 20) |
| ChromeDriver not found | Download from https://chromedriver.chromium.org/ and add to PATH |

---

## Next: Production Deployment

Once working locally:

1. **Pick a server** - Heroku, AWS, DigitalOcean (~$5-10/month)
2. **Set environment variables** - Email credentials
3. **Enable persistent scheduling** - systemd or cloud scheduler
4. **Optional: Dashboard** - Host React frontend on same server

See `SETUP.md` for full production guide.

---

**That's it!** You now have automated price monitoring. 🎉
