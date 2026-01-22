# Apple Reminders to Whole Foods Auto-Ordering

Automatically build Whole Foods shopping carts from your Apple Reminders, matching exact products from your order history.

## 🎯 Features

- 📱 **Smart Reminders Integration**: Say "whole milk" in Reminders, get your exact usual brand
- 🛒 **Intelligent Product Matching**: Searches Whole Foods order history for exact matches
- 👀 **Interactive Cart Review**: Approve before anything is added to cart
- ✅ **Auto-Complete Reminders**: Marks ordered items complete automatically
- 📦 **Delivery Verification**: Check what was delivered vs out of stock
- ⏰ **Evening Schedule**: Runs at 7pm by default
- 🥬 **Whole Foods Only**: Focuses on fresh groceries from Whole Foods/Amazon Fresh
- 🧪 **Safe Testing**: Dry-run mode for risk-free testing

## How It Works

### The Complete Workflow

**Evening (7:00 PM)**
1. App reads your Apple Reminders due today
2. Searches your Whole Foods order history for each item
3. Matches generic names to exact products you've ordered before
   - Your reminder: "whole milk"
   - App finds: "365 Organic Whole Milk, 1 Gallon" (your usual brand)
4. Displays cart review showing all matched products
5. Waits for your approval (yes/no)
6. Adds approved items to Amazon cart
7. Marks successfully added items complete in Reminders

**You Complete Checkout**
- Go to Amazon.com
- Review your cart
- Schedule delivery
- Complete checkout

**Next Day (Optional)**
- Run delivery verification
- Check what was delivered vs out of stock
- Out-of-stock items can be re-added to Reminders

### Why This Works

- **Only Whole Foods**: Searches only your Whole Foods/Amazon Fresh orders
- **Order History First**: Uses "most recently ordered" to find your preferred brands
- **Generic → Specific**: Type generic names, get your exact usual products
- **You stay in control**: Review and approve before any purchase

## Requirements

- **macOS** (for Apple Reminders access via EventKit)
- **Python 3.8+**
- **Amazon account** with Whole Foods order history
- **Whole Foods delivery** available in your area

## Installation

### Quick Install

```bash
git clone <your-repo-url>
cd ordering
chmod +x setup.sh
./setup.sh
```

### Manual Install

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Configure
cp .env.example .env
nano .env  # Add your Amazon credentials
```

## Configuration

Edit `.env`:

```bash
# Required
AMAZON_EMAIL=your_email@example.com
AMAZON_PASSWORD=your_password

# Optional
RUN_TIME=19:00                      # 7 PM (when to check reminders)
REMINDERS_LIST_NAME=Shopping        # Specific list, or blank for all
HEADLESS=true                       # false to see browser
DRY_RUN=false                       # true for testing
```

### First-Time Setup

1. **Grant Reminders Access**
   - macOS will prompt on first run
   - Or: System Preferences → Security & Privacy → Privacy → Reminders
   - Add Terminal or Python

2. **Test Amazon Login**
   ```bash
   python main.py --run-now --dry-run --no-headless
   ```

3. **Create Test Reminders**
   - Open Apple Reminders
   - Add items you've ordered from Whole Foods before
   - Set due date to today
   - Use generic names (e.g., "milk", "eggs", "bananas")

## Usage

### Run Immediately

```bash
# Test mode (safe - won't order anything)
python main.py --run-now --dry-run --no-headless

# Real run (adds to cart)
python main.py --run-now

# Non-interactive (auto-approve cart)
python main.py --run-now --no-interactive
```

### Schedule Daily

```bash
# Run daily at 7 PM (default)
python main.py

# Run daily at custom time
python main.py --time 20:00

# Run in background (recommended for production)
nohup python main.py > logs/scheduler.log 2>&1 &
```

### Check Delivery

```bash
# After delivery, check what was delivered vs out of stock
python main.py --verify-delivery
```

### Command Line Options

```
--run-now              Run immediately instead of scheduling
--time HH:MM           Set daily run time (default: 19:00/7pm)
--list NAME            Specific Reminders list name
--no-headless          Show browser window
--dry-run              Test mode without ordering
--no-interactive       Skip cart approval (auto-approve)
--verify-delivery      Check recent order status
--debug                Enable debug logging
```

## Setting Up Reminders

### Best Practices

**Use Generic Names**
- ✅ "whole milk"
- ✅ "bananas"
- ✅ "eggs"
- ✅ "avocados"

NOT:
- ❌ "365 Organic Whole Milk, 1 Gallon" (too specific)
- ❌ "get milk from store" (too vague)

**The app will automatically find your usual brand from order history.**

### Example Workflow

1. Open Apple Reminders
2. Create/use a "Shopping" list
3. Add items:
   - Title: "whole milk"
   - Due: Today
   - Repeat: None
4. Add more items as needed
5. At 7 PM, the app runs automatically

### Reminder Structure

```
Title: whole milk          ← Generic name
Notes: (optional)
Due: Today
List: Shopping
```

The app searches your Whole Foods orders for "milk" and finds your most recent purchase.

## Background Scheduling

### Using macOS LaunchAgent (Recommended)

Create `~/Library/LaunchAgents/com.ordering.daily.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ordering.daily</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/ordering/venv/bin/python</string>
        <string>/path/to/ordering/main.py</string>
        <string>--run-now</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>19</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/path/to/ordering/logs/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/ordering/logs/launchd.error.log</string>
    <key>WorkingDirectory</key>
    <string>/path/to/ordering</string>
</dict>
</plist>
```

Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.ordering.daily.plist
```

### Using Cron

```bash
crontab -e

# Add (runs at 7 PM daily):
0 19 * * * cd /path/to/ordering && /path/to/venv/bin/python main.py --run-now >> logs/cron.log 2>&1
```

## Workflow Examples

### Daily Routine

**Your Day:**
- 10:00 AM - Add "bananas" to Reminders (due today)
- 2:00 PM - Add "whole milk" to Reminders (due today)
- 5:00 PM - Add "eggs" to Reminders (due today)

**7:00 PM - Automation Runs:**
```
==========================================
[1/4] Reading Apple Reminders...
Found 3 items to order:
  - bananas
  - whole milk
  - eggs

[2/4] Searching Whole Foods order history...
Processing: bananas
  ✓ Found: Organic Bananas

Processing: whole milk
  ✓ Found: 365 Organic Whole Milk, 1 Gallon

Processing: eggs
  ✓ Found: Organic Large Brown Eggs, 12 ct

=================================================
CART REVIEW - Please verify before ordering
=================================================

Items to be ordered (3):
----------------------------------------------
1. Organic Bananas
   From reminder: 'bananas'
   Last ordered: Nov 15, 2025

2. 365 Organic Whole Milk, 1 Gallon
   From reminder: 'whole milk'
   Last ordered: Nov 14, 2025

3. Organic Large Brown Eggs, 12 ct
   From reminder: 'eggs'
   Last ordered: Nov 13, 2025

=================================================

Proceed with adding these items to cart? (yes/no): yes

[3/4] Adding items to cart...
Adding: Organic Bananas
  ✓ Success
Adding: 365 Organic Whole Milk, 1 Gallon
  ✓ Success
Adding: Organic Large Brown Eggs, 12 ct
  ✓ Success

[4/4] Marking items complete in Reminders...
✓ Marked complete: bananas
✓ Marked complete: whole milk
✓ Marked complete: eggs

SUMMARY
==========================================
Items processed: 3
Matched from history: 3
Added to cart: 3
Failed to find: 0
==========================================
```

**You:**
- Go to Amazon.com
- Review cart
- Schedule delivery
- Checkout

**Next Day (After Delivery):**
```bash
python main.py --verify-delivery
```

Output:
```
Delivery Summary:
  Delivered: 2 items
  Out of stock: 1 item

Delivered items:
  ✓ Organic Bananas
  ✓ Organic Large Brown Eggs, 12 ct

Out of stock items (not delivered):
  ✗ 365 Organic Whole Milk, 1 Gallon

These items need to be reordered.
Add them back to your Reminders for tomorrow's order.
```

## Troubleshooting

### Reminders Access Denied

**Problem**: "Access to Reminders denied"

**Solution**:
1. System Preferences → Security & Privacy → Privacy → Reminders
2. Click lock and authenticate
3. Add Terminal (or Python) to allowed apps
4. Restart Terminal

### Login Failed

**Problem**: Amazon login fails

**Solutions**:
- Verify credentials in `.env`
- Disable 2FA temporarily (or see 2FA section below)
- Run with `--no-headless` to see what's happening
- Check for CAPTCHA requirement

### Amazon 2FA

If you use two-factor authentication:

**Option 1**: Manual first-time login
```bash
python main.py --run-now --no-headless
```
Log in manually, then let automation continue

**Option 2**: App-specific password (if Amazon supports it)

**Option 3**: Disable 2FA for automation (not recommended for security)

### Products Not Found

**Problem**: "Not found in order history"

**Causes**:
1. Never ordered from Whole Foods before
2. Ordered too long ago
3. Reminder name doesn't match

**Solutions**:
- Order manually once from Whole Foods
- Use more generic names ("milk" instead of "2% milk")
- Try exact product name from order history
- Check order history manually to verify product exists

### Items Not Matching

**Problem**: App finds wrong product

**Solution**:
- Use more specific names
- Check order history for exact wording
- Most recent order is used - order the right one manually first

### Nothing Happens

**Problem**: Scheduled run doesn't work

**Check**:
```bash
# See if scheduler is running
ps aux | grep python | grep ordering

# Check logs
tail -f ordering.log

# Verify schedule
python main.py --debug
```

## Security

### Credentials

- Stored in `.env` file (not in git)
- Never committed to repository
- File permissions should be `600`

```bash
chmod 600 .env
```

### Amazon Account Safety

- Uses official Amazon website (not API)
- No third-party services
- No data sent anywhere except Amazon
- All automation is visible with `--no-headless`

### Recommendations

- Use a strong Amazon password
- Enable Amazon purchase PIN
- Review orders before checkout
- Start with small test orders
- Monitor `ordering.log` regularly

## Logs

### Log Files

- `ordering.log` - Detailed application logs
- `logs/scheduler.log` - Scheduled run output
- `logs/launchd.log` - LaunchAgent output (if using)

### View Logs

```bash
# Real-time monitoring
tail -f ordering.log

# Last 50 lines
tail -50 ordering.log

# Search logs
grep "ERROR" ordering.log
grep "Added to cart" ordering.log
```

## Advanced Usage

### Multiple Reminder Lists

Process multiple lists:

```bash
# Just "Whole Foods" list
python main.py --run-now --list "Whole Foods"

# Just "Groceries" list
python main.py --run-now --list "Groceries"

# All lists (default)
python main.py --run-now
```

### Automated Checkout (Not Recommended)

The app intentionally does NOT complete checkout automatically for safety. You should:
1. Review the cart on Amazon.com
2. Select delivery time
3. Apply any coupons/discounts
4. Complete checkout manually

This ensures you have final control over purchases.

## Project Structure

```
ordering/
├── src/
│   ├── __init__.py
│   ├── reminders_reader.py      # Apple Reminders integration + completion
│   ├── amazon_automation.py     # Whole Foods product matching + cart
│   └── scheduler.py             # Daily scheduling + workflow
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── setup.sh                     # Automated setup script
├── .env.example                 # Configuration template
├── .env                         # Your configuration (not in git)
├── .gitignore                   # Git ignore rules
├── README.md                    # This file
├── QUICKSTART.md                # 5-minute setup guide
├── LICENSE                      # MIT License
└── logs/                        # Log files (created at runtime)
```

## Development

### Run Individual Modules

```bash
# Test Reminders reader
python -m src.reminders_reader

# Test Amazon automation
python -m src.amazon_automation

# Test scheduler
python -m src.scheduler --run-now --dry-run
```

### Debug Mode

```bash
# Verbose logging
python main.py --run-now --debug --no-headless

# See all HTTP requests, selectors, etc.
```

## Limitations

- **macOS only** - Requires Apple Reminders app
- **Whole Foods only** - Only searches Whole Foods/Amazon Fresh orders
- **Previous orders required** - Must have ordered items before
- **No checkout automation** - You complete the purchase
- **Web scraping** - May break if Amazon changes their website
- **Order history depth** - Searches last ~20 orders

## FAQ

**Q: Does this place orders automatically?**
A: No. It adds items to your cart. You review and checkout manually.

**Q: What if I haven't ordered an item before?**
A: It won't be found. Order it manually once, then it will work in the future.

**Q: Can I use this for regular Amazon (not Whole Foods)?**
A: Currently only Whole Foods/Amazon Fresh. Regular Amazon support could be added.

**Q: Will it work with Amazon Subscribe & Save?**
A: No, it adds one-time purchases to cart.

**Q: What if an item is out of stock?**
A: Use `--verify-delivery` after delivery to see what wasn't delivered. Re-add those to Reminders.

**Q: Is this safe?**
A: It only adds to cart (doesn't checkout). Always review before purchasing. Use `--dry-run` for testing.

**Q: Can I run this on Linux/Windows?**
A: Not currently - requires macOS for Apple Reminders. Could be adapted for other reminder systems.

## Roadmap

- [ ] Email/SMS notifications for cart review
- [ ] Support for Google Tasks / Todoist
- [ ] Quantity support from reminder notes
- [ ] Web UI for configuration and monitoring
- [ ] Regular Amazon (non-Whole Foods) support
- [ ] Better product matching with ML
- [ ] Integration with meal planning apps

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

- **Issues**: [GitHub Issues](https://github.com/yourname/ordering/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourname/ordering/discussions)
- **Logs**: Check `ordering.log` for details

## License

MIT License - See [LICENSE](LICENSE) file

## Disclaimer

This tool is for personal use only. It automates interaction with Amazon's website but does not use official APIs. Use at your own risk. Amazon's terms of service should be reviewed before using automation tools. The authors are not responsible for any issues arising from use of this software, including but not limited to accidental purchases, account restrictions, or delivery issues.

Always review your cart before completing checkout.

## Acknowledgments

- Built with [Playwright](https://playwright.dev/) for browser automation
- Uses macOS EventKit for Reminders access
- Inspired by the need to automate weekly grocery shopping

---

Made with ❤️ for automated Whole Foods shopping

**Remember**: You're in control. The app builds the cart, you complete the order.
