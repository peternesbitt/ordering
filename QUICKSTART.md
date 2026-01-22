# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- macOS computer
- Amazon account with Whole Foods order history
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
RUN_TIME=19:00
```

Save and exit (Ctrl+X, then Y, then Enter)

### 3. Create Test Reminders

Open Apple Reminders app and:
1. Create a new list called "Shopping" (optional, but recommended)
2. Add a few items you've ordered before from Whole Foods:
   - whole milk
   - bananas
   - eggs
3. Set due date to today

**Important**: Use generic names (like "whole milk") - the app will find the exact product you previously ordered (like "365 Organic Whole Milk, 1 Gallon")

### 4. Test Run (Dry Mode)

```bash
source venv/bin/activate
python main.py --run-now --dry-run --no-headless
```

Watch the automation work! It will:
- Read your reminders
- Search your Whole Foods order history
- Show the exact products it matched
- Display a cart review
- NOT actually add to cart (dry-run mode)

### 5. First Real Run

If the dry run looks good:

```bash
python main.py --run-now --no-headless
```

This will:
1. Find products from your order history
2. Show you a cart review
3. Ask for your approval
4. Add items to your Amazon cart
5. Mark reminders as complete

## How It Works

### Evening Workflow (7pm default)

1. **7:00 PM** - App runs automatically
2. **Read Reminders** - Checks for items due today
3. **Match Products** - Searches your Whole Foods order history
   - Example: "whole milk" → "365 Organic Whole Milk, 1 Gallon"
4. **Cart Review** - Shows you exactly what will be ordered
5. **Your Approval** - You confirm (yes/no)
6. **Add to Cart** - Items are added to your Amazon cart
7. **Complete Reminders** - Successfully ordered items are marked done
8. **You Checkout** - Go to Amazon and complete the checkout

### After Delivery

Check what was delivered vs out of stock:

```bash
python main.py --verify-delivery
```

This helps you know if anything was out of stock and needs to be reordered.

## What's Next?

### Schedule Daily Runs

To run automatically every evening at 7 PM:

```bash
python main.py
```

Or customize the time:

```bash
python main.py --time 20:00  # 8 PM
```

The scheduler will run in the foreground. For background scheduling, use cron or launchd (see README.md).

### Customize

Edit `.env` to customize:
- `RUN_TIME=19:00` - When to check reminders (default 7pm)
- `REMINDERS_LIST_NAME=Shopping` - Which list to scan
- `HEADLESS=true` - Hide browser window
- `DRY_RUN=false` - Test mode toggle

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

### Products Not Found

If items aren't matched:
- Make sure you've ordered them from Whole Foods before
- Try using the exact product name from your order history
- Run `--no-headless` to see the search process

## Daily Workflow

### Your Routine:

1. **Throughout the day**: Add items to Apple Reminders with today's date
2. **7:00 PM**: App automatically runs
3. **Cart review**: Check your terminal/email for the cart review
4. **Approve**: Respond "yes" to approve the cart
5. **Reminders updated**: Items are marked complete automatically
6. **Checkout**: Go to Amazon and complete the order
7. **Next day**: After delivery, optionally run `--verify-delivery` to check for out-of-stock items

### Example Reminder Names:

Use generic names - the app finds the exact product:

| Your Reminder | App Finds |
|--------------|-----------|
| whole milk | 365 Organic Whole Milk, 1 Gallon |
| bananas | Organic Bananas |
| eggs | Organic Large Brown Eggs, 12 ct |
| avocados | Organic Hass Avocados, 4 ct |

## Tips

- **Use generic names** in reminders - let the app find your usual brand
- **Only Whole Foods** - This app only searches Whole Foods/Amazon Fresh orders
- **Test first** - Always use `--dry-run` when testing
- **Check logs** - View `ordering.log` for detailed results
- **Regular items work best** - Items you've ordered multiple times match better

## Command Cheat Sheet

```bash
# Test run (safe)
python main.py --run-now --dry-run --no-headless

# Run once (real)
python main.py --run-now

# Schedule daily at 7pm
python main.py

# Schedule at custom time
python main.py --time 20:00

# Check delivery status
python main.py --verify-delivery

# Non-interactive (auto-approve)
python main.py --run-now --no-interactive
```

## Getting Help

See full documentation in [README.md](README.md)

---

Happy automated Whole Foods shopping! 🥬🛒
