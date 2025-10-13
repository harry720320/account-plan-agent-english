# Database Schema Documentation

## Overview
This document describes the complete database schema for the Account Plan Agent application.

## Database File
- **File**: `account_plan_agent.db`
- **Type**: SQLite 3
- **Initialization Script**: `init_database.py`

## Tables

### 1. accounts
Customer account information table.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique account ID |
| company_name | VARCHAR(255) | UNIQUE, NOT NULL | Company name |
| industry | VARCHAR(100) | | Industry sector |
| company_size | VARCHAR(50) | | Company size |
| website | VARCHAR(255) | | Company website |
| country | VARCHAR(100) | NOT NULL, DEFAULT 'Unknown' | Country location |
| description | TEXT | | Company description |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Relationships:**
- One-to-many with `account_plans`
- One-to-many with `interactions`
- One-to-many with `external_info`

---

### 2. account_plans
Strategic account plans table.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique plan ID |
| account_id | INTEGER | NOT NULL, FOREIGN KEY | Reference to accounts |
| title | VARCHAR(255) | NOT NULL | Plan title |
| content | TEXT | | Plan content (Markdown format) |
| status | VARCHAR(50) | DEFAULT 'draft' | Plan status (draft/completed/archived) |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |
| change_log | JSON | | Change history log |

**Relationships:**
- Many-to-one with `accounts`
- One-to-many with `interactions`

---

### 3. interactions
Interaction records table (Q&A history).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique interaction ID |
| account_id | INTEGER | NOT NULL, FOREIGN KEY | Reference to accounts |
| plan_id | INTEGER | FOREIGN KEY | Reference to account_plans (nullable) |
| interaction_type | VARCHAR(50) | NOT NULL | Type of interaction |
| question | TEXT | | Question text |
| answer | TEXT | | Answer text |
| structured_data | JSON | | Extracted structured data |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Relationships:**
- Many-to-one with `accounts`
- Many-to-one with `account_plans`

---

### 4. question_templates
Question template library.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique template ID |
| category | VARCHAR(100) | NOT NULL | Question category |
| question_text | TEXT | NOT NULL | Question text |
| description | TEXT | | Question description |
| is_core | BOOLEAN | DEFAULT 1 | Whether it's a core question |
| follow_up_questions | JSON | | Follow-up questions |
| order | INTEGER | DEFAULT 0 | Display order |
| is_active | BOOLEAN | DEFAULT 1 | Whether the template is active |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Default Questions:**
1. Cooperation History
2. Products & Services
3. Challenges & Issues
4. Key Contacts
5. Future Plans
6. Resource Needs

---

### 5. external_info
External information collection table.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique info ID |
| account_id | INTEGER | NOT NULL, FOREIGN KEY | Reference to accounts |
| info_type | VARCHAR(50) | NOT NULL | Information type |
| content | TEXT | | Information content |
| source_url | VARCHAR(500) | | Source URL |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Constraints:**
- UNIQUE(account_id, info_type) - Each account can only have one record per info_type

**Relationships:**
- Many-to-one with `accounts`

---

### 6. countries
Country master data table.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique country ID |
| name | VARCHAR(100) | UNIQUE, NOT NULL | Country name |
| is_active | BOOLEAN | DEFAULT 1 | Whether the country is active |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Default Countries:**
United States, China, Japan, Germany, United Kingdom, France, India, Italy, Brazil, Canada, South Korea, Russia, Australia, Spain, Mexico, Indonesia, Netherlands, Saudi Arabia, Turkey, Switzerland

---

### 7. users
User authentication table.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique user ID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | Username |
| password_hash | VARCHAR(255) | NOT NULL | Password hash (SHA-256) |
| is_admin | BOOLEAN | DEFAULT 0 | Admin privileges |
| is_active | BOOLEAN | DEFAULT 1 | Account status |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Default User:**
- Username: `admin`
- Password: `admin`
- Role: Administrator

---

## Database Initialization

### Running the Initialization Script

```bash
python init_database.py
```

### What the Script Does

1. **Creates all tables** if they don't exist
2. **Adds missing columns** to existing tables (migration support)
3. **Inserts default data**:
   - 6 default question templates
   - 20 default countries
   - 1 default admin user
4. **Validates** table structure

### Migration Support

The script includes ALTER TABLE statements to add missing columns to existing databases:
- `accounts.country` - Added if missing
- `interactions.updated_at` - Added if missing
- `external_info.updated_at` - Added if missing
- `question_templates.order` - Added if missing

### Output Example

```
✅ Database initialization successful!
   📁 Database file: account_plan_agent.db
   📊 Created all necessary tables:
      - accounts
      - account_plans
      - interactions
      - question_templates
      - external_info
      - countries
      - users
   📝 Inserted 6 default question templates
   🌍 Inserted 20 default countries
   👤 Created default admin user (username: admin, password: admin)
   🔍 question_templates table columns: ['id', 'category', 'question_text', 'description', 'is_core', 'follow_up_questions', 'order', 'is_active', 'created_at', 'updated_at']
```

## Entity Relationship Diagram

```
┌─────────────┐
│   accounts  │
└──────┬──────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌─────────────┐   ┌──────────────┐
│account_plans│   │external_info │
└──────┬──────┘   └──────────────┘
       │
       │
       ▼
┌─────────────┐
│interactions │
└─────────────┘

┌──────────────────┐
│question_templates│  (Independent)
└──────────────────┘

┌──────────────┐
│  countries   │  (Independent)
└──────────────┘

┌──────────────┐
│    users     │  (Independent)
└──────────────┘
```

## Notes

1. **Cascade Delete**: When an account is deleted, all related plans, interactions, and external info are automatically deleted.
2. **JSON Fields**: SQLite stores JSON as TEXT. The application handles JSON serialization/deserialization.
3. **Timestamps**: All timestamps use UTC time.
4. **Password Security**: Passwords are hashed using SHA-256. In production, consider using bcrypt or argon2.
5. **Unique Constraints**: 
   - `accounts.company_name` must be unique
   - `external_info(account_id, info_type)` combination must be unique
   - `countries.name` must be unique
   - `users.username` must be unique

## Maintenance

### Backup Database
```bash
cp account_plan_agent.db account_plan_agent.db.backup
```

### Reset Database
```bash
rm account_plan_agent.db
python init_database.py
```

### Check Database Integrity
```bash
sqlite3 account_plan_agent.db "PRAGMA integrity_check;"
```

