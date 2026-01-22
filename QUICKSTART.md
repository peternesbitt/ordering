# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- macOS computer
- Amazon account with order history
- Apple Reminders app
- Python 3.8 or higher

## Setup (5 minutes)

### 1. Clone and Setup

```bash
# Navigate to project
cd ordering

# Run setup script
chmod +x setup.sh
./setup.sh
```

### 2. Configure Amazon Credentials

Edit `.env` file:

```bash
nano .env
```

Add your credentials:
```
AMAZON_EMAIL=your_email@example.com
AMAZON_PASSWORD=your_password
```

Save and exit (Ctrl+X, then Y, then Enter)

### 3. Create Test Reminders

Open Apple Reminders app and:
1. Create a new list called "Shopping"
2. Add a few items you've ordered before on Amazon:
   - Bananas
   - Milk
   - Bread
3. Set due date to today

### 4. Test Run (Dry Mode)

```bash
source venv/bin/activate
python main.py --run-now --dry-run --no-headless
```

Watch the browser automation work! It will:
- Read your reminders
- Search Amazon order history
- Show what it would order (but not actually order)

### 5. First Real Run

If the dry run looks good:

```bash
python main.py --run-now
```

This will place actual orders!

## What's Next?

### Schedule Daily Runs

To run automatically every day at 9 AM:

```bash
python main.py --time 09:00
```

Or set up with cron/launchd (see README.md)

### Customize

Edit `.env` to customize:
- Run time
- Reminders list name
- Headless mode
- Dry run default

## Troubleshooting

### Reminders Access Denied

1. Go to **System Preferences** → **Security & Privacy** → **Privacy** → **Reminders**
2. Click the lock to make changes
3. Add Terminal or Python to the list

### Login Issues

If Amazon login fails:
- Check credentials in `.env`
- Try with `--no-headless` to see browser
- Amazon 2FA may require manual login first time

### No Items Found

Make sure:
- Reminders have today's date (or are overdue)
- Items aren't marked as completed
- Using correct list name in config

## Daily Workflow

1. Add items to Apple Reminders (with today's date)
2. Let the automation run (scheduled or manual)
3. Check logs for results
4. Orders placed automatically!

## Tips

- Use product names exactly as they appear in your Amazon order history
- Test new items with `--dry-run` first
- Check `ordering.log` for detailed info
- Start with items you order regularly

## Getting Help

See full documentation in [README.md](README.md)

---

Happy automated shopping! 🛒
