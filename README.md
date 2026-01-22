# Apple Reminders to Amazon/Whole Foods Auto-Ordering

Automatically place Amazon and Whole Foods orders based on your Apple Reminders, using your previous order history.

## Features

- 📱 Reads shopping items from Apple Reminders (macOS only)
- 🛒 Automatically reorders items from your Amazon order history
- 🥬 Supports Whole Foods orders through Amazon Fresh
- ⏰ Runs on a daily schedule
- 🔄 Intelligent matching using "Buy it again" feature
- 🧪 Dry-run mode for testing
- 📝 Detailed logging

## How It Works

1. **Reads Reminders**: Scans your Apple Reminders for items due today (or overdue)
2. **Searches Order History**: Looks for matching items in your Amazon order history
3. **Places Orders**: Uses "Buy it again" to reorder items automatically
4. **Fallback to Search**: If not in order history, searches Whole Foods/Amazon Fresh

## Requirements

- macOS (for Apple Reminders access)
- Python 3.8+
- Amazon account with order history
- Whole Foods delivery available in your area (optional)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd ordering
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

5. **Configure environment**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Amazon credentials:
   ```
   AMAZON_EMAIL=your_email@example.com
   AMAZON_PASSWORD=your_password
   RUN_TIME=09:00
   REMINDERS_LIST_NAME=Shopping
   ```

6. **Grant Reminders access**:
   - First run will prompt for Reminders access
   - Go to System Preferences → Security & Privacy → Privacy → Reminders
   - Allow Terminal or your Python executable

## Usage

### Run Once (Test Mode)

Test the automation with dry-run mode (won't place actual orders):

```bash
python main.py --run-now --dry-run --no-headless
```

### Run Once (Live)

Run immediately and place actual orders:

```bash
python main.py --run-now
```

### Schedule Daily Runs

Start the scheduler to run automatically every day:

```bash
python main.py
```

This will run daily at the time specified in your `.env` file (default: 09:00).

### Command Line Options

```
Options:
  --run-now         Run immediately instead of scheduling
  --time HH:MM      Set daily run time (default: 09:00)
  --list NAME       Specify Reminders list name (default: all lists)
  --no-headless     Show browser window during automation
  --dry-run         Test mode - don't place actual orders
  --debug           Enable debug logging
```

### Examples

```bash
# Test with visible browser
python main.py --run-now --dry-run --no-headless

# Run now with specific reminders list
python main.py --run-now --list "Whole Foods"

# Schedule daily at 8:00 AM
python main.py --time 08:00

# Debug mode
python main.py --run-now --debug
```

## Setting Up Reminders

1. Open Apple Reminders app on your Mac
2. Create a list (e.g., "Shopping" or "Whole Foods")
3. Add items as reminders with today's date or overdue
4. Item names should match products you've ordered before

**Example Reminders**:
- Bananas
- Organic Whole Milk
- Large Eggs
- Avocados
- Bread

**Tips**:
- Use product names as they appear on Amazon
- The app will search your order history first
- Previous orders have the best matching
- You can use reminder notes for multiple items

## Automation with Cron (macOS)

To run automatically every day, add to your crontab:

```bash
# Edit crontab
crontab -e

# Add this line (runs at 9 AM daily)
0 9 * * * cd /path/to/ordering && /path/to/venv/bin/python main.py --run-now >> logs/cron.log 2>&1
```

Or use macOS Launch Agent for better reliability:

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
        <string>/path/to/venv/bin/python</string>
        <string>/path/to/ordering/main.py</string>
        <string>--run-now</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/path/to/ordering/logs/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/ordering/logs/launchd.error.log</string>
</dict>
</plist>
```

Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.ordering.daily.plist
```

## Configuration

Edit `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `AMAZON_EMAIL` | Your Amazon account email | Required |
| `AMAZON_PASSWORD` | Your Amazon account password | Required |
| `RUN_TIME` | Daily run time (HH:MM) | 09:00 |
| `REMINDERS_LIST_NAME` | Specific reminders list to scan | All lists |
| `HEADLESS` | Run browser invisibly | true |
| `DRY_RUN` | Test mode without ordering | false |

## Security Notes

- **Credentials**: Stored in `.env` file (not committed to git)
- **2FA**: If you use Amazon 2FA, you may need to:
  - Temporarily disable it, or
  - Manually log in first time with `--no-headless`
- **Permissions**: Requires Reminders access (macOS will prompt)

## Troubleshooting

### "Access to Reminders denied"
- Go to System Preferences → Security & Privacy → Privacy → Reminders
- Add Terminal or Python to allowed apps

### "Login failed"
- Check credentials in `.env` file
- Try running with `--no-headless` to see what's happening
- Amazon 2FA may need manual intervention first time

### "Items not found in order history"
- Make sure you've ordered these items before
- Try using exact product names from your order history
- Use `--no-headless --dry-run` to see search process

### Browser issues
- Run: `playwright install chromium`
- Update Playwright: `pip install --upgrade playwright`

## Logs

- Console output shows real-time progress
- `ordering.log` - Detailed logs of all runs
- Use `--debug` flag for verbose logging

## Project Structure

```
ordering/
├── src/
│   ├── __init__.py
│   ├── reminders_reader.py    # Apple Reminders integration
│   ├── amazon_automation.py   # Amazon/Whole Foods automation
│   └── scheduler.py           # Daily scheduling logic
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Example configuration
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## Development

Run individual modules for testing:

```bash
# Test Reminders reader
python -m src.reminders_reader

# Test Amazon automation
python -m src.amazon_automation

# Test scheduler
python -m src.scheduler --run-now --dry-run
```

## Limitations

- macOS only (for Apple Reminders)
- Requires previous Amazon order history for best results
- Amazon may change their website, breaking automation
- Whole Foods delivery must be available in your area
- No official Amazon API (uses browser automation)

## Future Enhancements

- [ ] Support for other reminder apps (Google Tasks, Todoist)
- [ ] Better product matching with fuzzy search
- [ ] Support for other grocery services
- [ ] Quantity support from reminders
- [ ] Email/SMS notifications for order confirmations
- [ ] Web UI for configuration

## License

MIT License - See LICENSE file

## Disclaimer

This tool is for personal use only. Use at your own risk. Amazon's terms of service should be reviewed before using automation tools. The authors are not responsible for any issues arising from use of this software.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues or questions:
- Check the Troubleshooting section
- Review logs in `ordering.log`
- Open an issue on GitHub

---

Made with ❤️ for automated grocery shopping
