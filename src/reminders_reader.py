"""
Apple Reminders Reader
Reads reminders from macOS Reminders app using EventKit framework.
"""

import sys
from typing import List, Dict, Optional
from datetime import datetime, timedelta

# Check if running on macOS
if sys.platform != 'darwin':
    raise ImportError("This module requires macOS")

try:
    from EventKit import EKEventStore, EKEntityTypeReminder
    from Foundation import NSDate, NSPredicate
except ImportError as e:
    raise ImportError(
        "EventKit framework not available. Install with: pip install pyobjc-framework-EventKit"
    ) from e


class RemindersReader:
    """Reads reminders from Apple Reminders app."""

    def __init__(self):
        """Initialize the EventKit store."""
        self.store = EKEventStore.alloc().init()
        self._request_access()

    def _request_access(self):
        """Request access to reminders."""
        # Request access (will prompt user if not already granted)
        success = self.store.requestAccessToEntityType_completion_(
            EKEntityTypeReminder,
            None
        )
        if not success:
            print("Warning: Access to Reminders may need to be granted in System Preferences")

    def get_todays_reminders(self, list_name: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Get all incomplete reminders due today or overdue.

        Args:
            list_name: Optional name of specific reminders list to filter by

        Returns:
            List of dictionaries with reminder details
        """
        # Get all calendars (lists) for reminders
        calendars = self.store.calendarsForEntityType_(EKEntityTypeReminder)

        # Filter by list name if provided
        if list_name:
            calendars = [cal for cal in calendars if cal.title() == list_name]
            if not calendars:
                print(f"Warning: Reminders list '{list_name}' not found")
                return []

        # Create predicate for incomplete reminders
        predicate = self.store.predicateForIncompleteRemindersWithDueDateStarting_ending_calendars_(
            None,  # No start date limit (get overdue items too)
            NSDate.dateWithTimeIntervalSinceNow_(86400),  # End at tomorrow
            calendars
        )

        # Fetch reminders
        reminders_list = []

        def completion_handler(reminders):
            if reminders:
                for reminder in reminders:
                    reminders_list.append({
                        'title': reminder.title() or '',
                        'notes': reminder.notes() or '',
                        'list': reminder.calendar().title() if reminder.calendar() else '',
                        'due_date': str(reminder.dueDateComponents()) if reminder.dueDateComponents() else None,
                        'completed': reminder.isCompleted()
                    })

        # Fetch (synchronous for simplicity)
        self.store.fetchRemindersMatchingPredicate_completion_(
            predicate,
            completion_handler
        )

        # Wait a bit for async fetch (in production, use proper async handling)
        import time
        time.sleep(0.5)

        return reminders_list

    def get_shopping_items(self, list_name: Optional[str] = None) -> List[str]:
        """
        Get shopping items from reminders.

        Args:
            list_name: Optional name of specific reminders list (e.g., "Shopping")

        Returns:
            List of item names to order
        """
        reminders = self.get_todays_reminders(list_name)
        items = []

        for reminder in reminders:
            if not reminder['completed']:
                # Use title as the item name
                item_name = reminder['title'].strip()
                if item_name:
                    items.append(item_name)

                # Also check notes for additional items (one per line)
                if reminder['notes']:
                    for line in reminder['notes'].split('\n'):
                        line = line.strip()
                        if line and line not in items:
                            items.append(line)

        return items


def main():
    """Test the reminders reader."""
    reader = RemindersReader()

    print("Fetching today's reminders...")
    reminders = reader.get_todays_reminders()

    print(f"\nFound {len(reminders)} reminders:")
    for reminder in reminders:
        print(f"  - {reminder['title']} (List: {reminder['list']})")
        if reminder['notes']:
            print(f"    Notes: {reminder['notes']}")

    print("\nShopping items:")
    items = reader.get_shopping_items()
    for item in items:
        print(f"  - {item}")


if __name__ == '__main__':
    main()
