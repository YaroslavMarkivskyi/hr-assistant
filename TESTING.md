# Testing Guide - Local Development without Real Azure ID

## Overview

You can test the bot locally **without a real Azure AD Object ID**. The system supports test IDs for local development.

## Setup for Local Testing

### 1. Set TEST_USER_ID in `.env`

Add to your `.env.local.user` or `.env.local`:

```bash
# Use any GUID format for testing (doesn't need to be a real Azure ID)
TEST_USER_ID=123e4567-e89b-12d3-a456-426614174000
```

**Important**: This can be **any GUID** - it doesn't need to be a real Azure AD Object ID. The bot will use this for all operations when running locally.

### 2. How It Works

#### Scenario A: With Graph API Available
```
1. Bot receives message
2. ctx.activity.from_property.aad_object_id = None (not available locally)
3. Bot uses TEST_USER_ID from config
4. Bot tries Graph API: get_user_by_id(TEST_USER_ID)
   - If Graph API works → gets real user data
   - If Graph API fails → creates employee with test data
5. Employee created in DB with aad_id = TEST_USER_ID
```

#### Scenario B: Without Graph API (Fully Local)
```
1. Bot receives message
2. Uses TEST_USER_ID from config
3. Graph API call fails (no connection/auth)
4. Bot creates employee with:
   - aad_id = TEST_USER_ID
   - full_name = "Test User"
   - email = "{TEST_USER_ID}@test.local"
   - vacation_balance = 20
   - sick_balance = 10
```

## Testing Different Users

### Option 1: Single Test User (Simplest)
```bash
TEST_USER_ID=123e4567-e89b-12d3-a456-426614174000
```
- All messages will be treated as from this user
- Good for testing basic functionality

### Option 2: Multiple Test Users (Advanced)
You can manually create multiple employees in the database with different test IDs:

```python
# In a test script or Python console
from src.db.database import DatabaseService
from src.models.employee import Employee

db = DatabaseService("time_off.db")

# Create test employee 1
emp1 = Employee(
    aad_id="test-user-1",
    full_name="Test User 1",
    email="test1@test.local",
    vacation_balance=20,
    sick_balance=10
)
db.create_employee(emp1)

# Create test employee 2
emp2 = Employee(
    aad_id="test-user-2",
    full_name="Test User 2",
    email="test2@test.local",
    vacation_balance=15,
    sick_balance=5
)
db.create_employee(emp2)
```

Then change `TEST_USER_ID` to switch between users.

## Database Location

The database file is created at:
- Default: `time_off.db` (in project root)
- Or set via: `DB_PATH=path/to/database.db` in `.env`

## Example Test Flow

1. **Set TEST_USER_ID**:
   ```bash
   echo "TEST_USER_ID=test-123-456" >> .env.local.user
   ```

2. **Start the bot**

3. **Test Time Off**:
   - Send: "Хочу у відпустку з 20.05 по 25.05"
   - Bot will:
     - Use `test-123-456` as user ID
     - Create employee in DB if not exists
     - Create leave request
     - Send approval card (to same user for testing)

4. **Check Balance**:
   - Send: "Скільки в мене відпустки?"
   - Bot will show balance for `test-123-456`

## Important Notes

- ✅ **TEST_USER_ID can be any string** - doesn't need to be a real GUID
- ✅ **Graph API calls will fail gracefully** - bot creates test data instead
- ✅ **Database is local** - safe to test without affecting production
- ✅ **All operations work** - Time Off, Balance Check, etc.

## Troubleshooting

### Issue: "Employee not found"
- Check that `TEST_USER_ID` is set in `.env`
- Check that database file exists and is writable

### Issue: "Graph API error" (expected in local testing)
- This is normal when testing without Azure connection
- Bot will create employee with test data automatically

### Issue: Want to test with real Azure ID
- Set `TEST_USER_ID` to your real Azure AD Object ID
- Ensure Graph API credentials are configured
- Bot will fetch real user data from Azure


