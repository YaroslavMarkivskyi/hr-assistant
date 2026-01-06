# Architecture Flow: Request Processing Pipeline

## 📊 Complete Request Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. FastAPI Endpoint (/api/messages)                            │
│    - Receives HTTP POST from Microsoft Teams                    │
│    - Validates Content-Type                                    │
│    - Parses JSON body → Activity object                        │
└──────────────────────┬────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Bot Framework Adapter                                        │
│    - Authenticates request (Azure AD)                           │
│    - Creates TurnContext                                       │
│    - Calls bot.on_turn(turn_context)                           │
└──────────────────────┬────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. HRBot.on_turn() (bot/logic.py)                               │
│    - Wraps TurnContext → ActivityContextWrapper                 │
│    - Routes to router.route_message()                           │
│    - Saves conversation state (finally block)                   │
└──────────────────────┬────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Router (bot/router.py)                                       │
│    - Detects message type:                                      │
│      • ACTION (button click) → handle_action()                  │
│      • TEXT (message) → detect_intent() → handle_intent()      │
│    - Shows typing indicator before AI calls                     │
│    - Handles AI failures gracefully                             │
└──────────────────────┬────────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
┌──────────────────┐        ┌──────────────────┐
│ 5a. Dispatch     │        │ 5b. Dispatch      │
│    Actions        │        │    Intents       │
│ (dispatch_actions)│        │ (dispatch_intents)│
│                   │        │                  │
│ Routes by:        │        │ Routes by:       │
│ - BotModule       │        │ - BotIntent       │
│ - Dictionary      │        │ - Dictionary      │
│   Dispatch        │        │   Dispatch        │
└────────┬──────────┘        └────────┬─────────┘
         │                           │
         └───────────┬───────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. Domain Handlers (handlers/*.py)                              │
│                                                                  │
│    ┌──────────────────────────────────────────────┐            │
│    │ people_ops.py                                 │            │
│    │ - handle_people_ops_intent()                  │            │
│    │ - handle_people_ops_action()                   │            │
│    │ - _handle_onboarding_intent()                  │            │
│    │ - _handle_schedule_meeting_intent()            │            │
│    └──────────────────────────────────────────────┘            │
│                                                                  │
│    ┌──────────────────────────────────────────────┐            │
│    │ time_off.py                                    │            │
│    │ - handle_time_off_intent()                     │            │
│    │ - handle_time_off_action()                     │            │
│    └──────────────────────────────────────────────┘            │
│                                                                  │
│    ┌──────────────────────────────────────────────┐            │
│    │ support.py                                    │            │
│    │ - handle_knowledge_base_intent()              │            │
│    │ - handle_service_desk_intent()                 │            │
│    │ - handle_service_desk_action()                │            │
│    └──────────────────────────────────────────────┘            │
│                                                                  │
│    ┌──────────────────────────────────────────────┐            │
│    │ general.py                                    │            │
│    │ - handle_chat_intent()                        │            │
│    │ - handle_unknown_intent()                      │            │
│    └──────────────────────────────────────────────┘            │
│                                                                  │
│    Responsibilities:                                            │
│    - Extract user context (AAD ID, language)                      │
│    - Prepare intent_data (parse candidate data if needed)        │
│    - Call feature.run_flow()                                     │
└──────────────────────┬────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. Features (features/*.py) ⭐ BUSINESS LOGIC LIVES HERE       │
│                                                                  │
│    ┌──────────────────────────────────────────────┐            │
│    │ onboarding.py                                 │            │
│    │ - run_flow()                                   │            │
│    │   • Parse candidate data (if not provided)     │            │
│    │   • Create Adaptive Card with candidate info   │            │
│    │   • Handle actions: create_user, reject        │            │
│    │ - handle_action()                              │            │
│    │   • Create Azure AD user (GraphService)        │            │
│    │   • Send welcome email (EmailService)          │            │
│    │   • Save to database (DatabaseService)        │            │
│    └──────────────────────────────────────────────┘            │
│                                                                  │
│    ┌──────────────────────────────────────────────┐            │
│    │ calendar.py                                   │            │
│    │ - run_flow()                                   │            │
│    │   • Parse meeting request (AI)                 │            │
│    │   • Resolve participants (GraphService + AI)  │            │
│    │   • Find available time slots                  │            │
│    │   • Create meeting proposal card              │            │
│    │ - handle_action()                             │            │
│    │   • Book meeting (GraphService)               │            │
│    │   • Send confirmation                         │            │
│    └──────────────────────────────────────────────┘            │
│                                                                  │
│    ┌──────────────────────────────────────────────┐            │
│    │ time_off.py                                   │            │
│    │ - run_flow()                                   │            │
│    │   • Parse leave request (AI)                  │            │
│    │   • Check vacation balance (DatabaseService)   │            │
│    │   • Validate dates (no overlaps, past dates)  │            │
│    │   • Create leave request (DatabaseService)    │            │
│    │   • Send approval card to manager             │            │
│    │ - handle_action()                             │            │
│    │   • Approve/reject request                     │            │
│    │   • Update database                            │            │
│    │   • Send notification to employee             │            │
│    └──────────────────────────────────────────────┘            │
│                                                                  │
│    Features use:                                                │
│    - AI Service (parse data, resolve users)                     │
│    - Graph Service (Azure AD, Calendar, Users)                  │
│    - Database Service (employees, leave requests)                │
│    - Email Service (notifications)                              │
│    - Adaptive Cards (UI components)                             │
└──────────────────────┬────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. Services (services/*.py, db/*.py)                            │
│                                                                  │
│    - GraphService: Azure AD, Calendar, Users API               │
│    - DatabaseService: PostgreSQL operations                     │
│    - EmailService: Send emails via SMTP/Graph API              │
│    - AIService: OpenAI/Azure OpenAI for parsing                │
│                                                                  │
│    These are injected via ServiceContainer                      │
└──────────────────────┬────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 9. Response to User                                             │
│    - Adaptive Card (onboarding, calendar, time_off)             │
│    - Text message (errors, confirmations)                      │
│    - Typing indicator (before long operations)                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Key Points

### **Handlers vs Features**

**Handlers** (`handlers/*.py`):
- **Thin routing layer** - decide which feature to call
- Extract context (user ID, language)
- Prepare data (parse if needed)
- **DO NOT contain business logic**

**Features** (`features/*.py`):
- **Business logic lives here** ⭐
- Implement actual functionality (create user, book meeting, approve vacation)
- Use services (Graph, DB, Email, AI)
- Create Adaptive Cards
- Handle user interactions

### **Example Flow: Onboarding**

```
User: "Create account for John Doe, email: john@example.com"
  ↓
Router → detect_intent() → "onboarding"
  ↓
dispatch_intents → handle_people_ops_intent()
  ↓
people_ops.py → _handle_onboarding_intent()
  ↓
  • Extract candidate data (AI parse if needed)
  • Prepare intent_data
  ↓
onboarding_feature.run_flow()
  ↓
  • Create Adaptive Card with candidate info
  • Show buttons: "Create User" / "Reject"
  ↓
User clicks "Create User"
  ↓
onboarding_feature.handle_action()
  ↓
  • Create Azure AD user (GraphService)
  • Send welcome email (EmailService)
  • Save to database (DatabaseService)
  ↓
Response: "✅ User created successfully!"
```

### **Example Flow: Time Off**

```
User: "Request vacation from 2025-01-15 to 2025-01-20"
  ↓
Router → detect_intent() → "request_vacation"
  ↓
dispatch_intents → handle_time_off_intent()
  ↓
time_off.py → handle_time_off_intent()
  ↓
  • Extract user AAD ID
  ↓
time_off_feature.run_flow()
  ↓
  • Parse leave request (AI)
  • Check vacation balance (DatabaseService)
  • Validate dates (no overlaps, not in past)
  • Create leave request (DatabaseService)
  • Send approval card to manager
  ↓
Manager clicks "Approve"
  ↓
time_off_feature.handle_action()
  ↓
  • Update request status (DatabaseService)
  • Send notification to employee
  ↓
Response: "✅ Vacation request approved!"
```

## 📁 File Structure

```
src/
├── api/
│   └── routes.py              # FastAPI endpoints
├── bot/
│   ├── logic.py               # HRBot.on_turn()
│   ├── router.py              # route_message()
│   └── activity_context_wrapper.py
├── handlers/
│   ├── dispatch_intents.py    # Routes intents to domain handlers
│   ├── dispatch_actions.py    # Routes actions to domain handlers
│   ├── people_ops.py          # People Ops domain handler
│   ├── time_off.py            # Time Off domain handler
│   ├── support.py             # Support domain handler
│   ├── general.py             # General handlers (chat, unknown)
│   └── utils.py               # Shared utilities
└── features/                  # ⭐ BUSINESS LOGIC
    ├── onboarding.py          # Onboarding feature
    ├── calendar.py            # Calendar/meeting feature
    └── time_off.py            # Time off feature
```

## 🔄 State Management

- **ConversationState**: Saved in `HRBot.on_turn()` finally block
- Used for: dialog steps, user preferences, temporary data
- Storage: MemoryStorage (in-memory) or CosmosDB (production)

## 🎨 Adaptive Cards

Features create Adaptive Cards for rich UI:
- **Onboarding**: Candidate card with "Create User" / "Reject" buttons
- **Calendar**: Meeting proposal with "Book" / "Reschedule" buttons
- **Time Off**: Approval card with "Approve" / "Reject" buttons

Cards are created using `adaptive_cards.card` module.


