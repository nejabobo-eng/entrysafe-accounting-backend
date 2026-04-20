# Entry Safe Backend - FastAPI

## Overview
The FastAPI backend powers the Entry Safe AI accounting platform. It handles:
- AI-driven transaction categorization using OpenAI GPT-4o
- CSV/Excel file parsing and bulk uploads
- Duplicate transaction detection
- MongoDB data persistence
- Financial reporting and reconciliation

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration and environment variables
│   ├── routes/                 # API endpoints
│   │   ├── settings.py          # Business settings & configuration
│   │   ├── transactions.py      # Transaction CRUD operations
│   │   ├── ai_categorization.py # AI categorization endpoints
│   │   └── file_upload.py       # File upload and parsing
│   ├── services/               # Business logic
│   │   ├── ai_service.py        # OpenAI integration with reliability patterns
│   │   └── file_parser.py       # CSV/Excel parsing
│   └── models/                 # Data models
│       ├── settings.py          # Business settings, industry, COA mapping
│       ├── transaction.py       # Transaction and JournalEntry models
│       └── account.py           # Chart of Accounts models
├── requirements.txt
├── Dockerfile
├── .env.example
├── .env                        # Local development (git ignored)
└── README_BACKEND.md
```

## Getting Started

### Prerequisites
- Python 3.10+
- MongoDB Atlas (or local MongoDB)
- OpenAI API key
- Firebase service account (for authentication)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd EntrySafe/backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys and MongoDB URI
   ```

5. **Run the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at: `http://localhost:8000`

### API Documentation
Once the server is running, access the interactive API docs:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## API Endpoints

### Settings (Business Configuration)
- `GET /api/settings/` - List all businesses (admin)
- `GET /api/settings/{owner_id}` - Get business settings by owner ID
- `POST /api/settings/` - Create new business settings
- `PUT /api/settings/{owner_id}` - Update business settings
- `DELETE /api/settings/{owner_id}` - Delete business settings
- `GET /api/settings/coa/industries` - List all supported industries
- `GET /api/settings/coa/{industry}` - Get Chart of Accounts for specific industry
- `POST /api/settings/{owner_id}/backup/test` - Test backup provider connection

### Transactions
- `GET /api/transactions/` - List all transactions
- `GET /api/transactions/{id}` - Get transaction by ID
- `POST /api/transactions/` - Create new transaction
- `PUT /api/transactions/{id}` - Update transaction
- `DELETE /api/transactions/{id}` - Delete transaction
- `POST /api/transactions/check-duplicates` - Check for duplicates

### AI Categorization
- `POST /api/ai/categorize` - Categorize a single transaction
- `POST /api/ai/batch-categorize` - Categorize multiple transactions
- `GET /api/ai/chart-of-accounts` - Get Chart of Accounts

### File Upload
- `POST /api/upload/csv` - Upload CSV bank statement
- `POST /api/upload/excel` - Upload Excel bank statement
- `GET /api/upload/sample` - Get sample CSV template

### Health Check
- `GET /health` - API health status

## Configuration

All configuration is managed through environment variables in `.env`:

```env
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# MongoDB
MONGO_URI=mongodb+srv://user:pass@cluster...
MONGO_DB_NAME=entry_safe

# JWT
JWT_SECRET_KEY=your-secret-key

# Firebase
FIREBASE_CREDENTIALS=path/to/firebase.json
```

## Key Features

### 1. AI Transaction Categorization
The `AIService` uses OpenAI GPT-4o to automatically categorize transactions:
```python
ai_service = AIService()
result = await ai_service.categorize_transaction(
    description="Payment for chicken feed",
    amount=1500.00
)
```

**Returns:**
```json
{
  "description": "Payment for chicken feed",
  "suggested_account": "Inventory",
  "account_code": "1200",
  "confidence": 0.95,
  "reasoning": "Feed purchases are typically categorized as inventory assets."
}
```

### 2. File Parsing
Upload CSV or Excel files for bulk transaction processing:
- Parses bank statements
- Extracts Date, Description, Amount
- Returns structured transaction data for AI categorization

### 3. Duplicate Detection
Identifies potential duplicate transactions to maintain data integrity.

### 4. Chart of Accounts
Predefined accounting categories:
- **Assets:** Cash (1000), A/R (1100), Inventory (1200), Equipment (1300)
- **Liabilities:** A/P (2000)
- **Income:** Revenue (3000)
- **Expenses:** COGS (4000), Operating (5000), Utilities (5100), Salaries (5200)

## Database Schema (MongoDB)

### Transactions Collection
```json
{
  "_id": "ObjectId",
  "date": "2024-01-15",
  "description": "Feed Supplies",
  "amount": 1500.00,
  "transaction_type": "debit",
  "account_code": "1200",
  "account_name": "Inventory",
  "category": "Feed Supplies",
  "is_duplicate": false,
  "ai_confidence": 0.95,
  "notes": "",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Accounts Collection
```json
{
  "_id": "ObjectId",
  "code": "1200",
  "name": "Inventory",
  "account_type": "asset",
  "description": "Feed and supplies inventory",
  "balance": 5000.00,
  "is_active": true
}
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
```bash
black app/
flake8 app/
```

### Adding New Endpoints

1. Create a new route file in `app/routes/`
2. Define the router and endpoints
3. Include the router in `app/main.py`

Example:
```python
# app/routes/reports.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/profit-loss")
async def get_profit_loss_statement():
    return {"statement": "..."}
```

Then in `app/main.py`:
```python
from app.routes import reports
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
```

## Deployment

### Docker (Recommended)
Create a `Dockerfile`:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t entry-safe-backend .
docker run -p 8000:8000 --env-file .env entry-safe-backend
```

### Heroku / Cloud Deployment
Set environment variables on your cloud platform and deploy.

## Troubleshooting

### OpenAI API Errors
- Verify `OPENAI_API_KEY` is set correctly
- Check API quota and billing

### MongoDB Connection Issues
- Ensure `MONGO_URI` is correct
- Add your IP to MongoDB Atlas whitelist

### CORS Issues
Update allowed origins in `app/main.py`:
```python
allow_origins=["http://localhost:3000", "https://yourdomain.com"]
```

## Settings Module (Business Configuration)

The Settings Module is the **foundation of V2**, controlling industry selection, Chart of Accounts mapping, VAT configuration, and backup provider setup.

### Key Features

#### 1. Industry-Based COA Generation
When users select their industry, the system automatically generates an industry-specific Chart of Accounts:

```bash
# Get list of supported industries
curl http://localhost:8000/api/settings/coa/industries

# Get COA for specific industry (e.g., Poultry)
curl http://localhost:8000/api/settings/coa/poultry
```

**Supported Industries:**
- **Poultry**: Inventory-Feed, Egg Sales, Veterinary Expense, Labor
- **Retail**: Sales Revenue, Cost of Goods Sold, Salaries, Rent
- **Services**: Service Revenue, Professional Fees, Office Rent
- **Agriculture**: Crop Sales, Seeds/Fertilizer, Water/Irrigation
- **Manufacturing, Healthcare, Education, Hospitality, Construction** (with generic COA fallback)
- **Other** (generic COA)

#### 2. Creating Business Settings

```bash
curl -X POST http://localhost:8000/api/settings/ \
  -H "Content-Type: application/json" \
  -d '{
    "owner_id": "user123",
    "business_profile": {
      "business_name": "Rainbow Poultry Farm",
      "owner_name": "John Mkhize",
      "owner_email": "john@rainbowpoultry.co.za",
      "phone_number": "+27791234567",
      "website": "www.rainbowpoultry.co.za"
    },
    "industry": "poultry",
    "currency": "ZAR",
    "vat_enabled": true,
    "vat_rate": 0.15
  }'
```

**Response:**
```json
{
  "message": "Business settings created for Rainbow Poultry Farm",
  "owner_id": "user123",
  "industry": "poultry",
  "accounts_count": 20,
  "vat_enabled": true,
  "vat_rate": 0.15
}
```

#### 3. Retrieving Settings with Auto-Generated COA

```bash
curl http://localhost:8000/api/settings/user123
```

**Returns:**
```json
{
  "owner_id": "user123",
  "business_profile": {
    "business_name": "Rainbow Poultry Farm",
    "owner_name": "John Mkhize",
    "owner_email": "john@rainbowpoultry.co.za"
  },
  "industry": "poultry",
  "currency": "ZAR",
  "fiscal_year_start": "01-01",
  "vat_enabled": true,
  "vat_rate": 0.15,
  "backup_provider": "none",
  "backup_enabled": false,
  "chart_of_accounts": [
    {"code": "1000", "name": "Cash", "account_type": "asset"},
    {"code": "1200", "name": "Inventory - Feed", "account_type": "asset"},
    {"code": "4000", "name": "Egg Sales Revenue", "account_type": "revenue"},
    {"code": "5000", "name": "Feed Expense", "account_type": "expense"},
    // ... 16 more accounts specific to Poultry
  ]
}
```

#### 4. Updating Settings (Industry Change)

```bash
curl -X PUT http://localhost:8000/api/settings/user123 \
  -H "Content-Type: application/json" \
  -d '{"industry": "retail"}'
```

When industry changes, **Chart of Accounts automatically regenerates** with retail-specific accounts.

#### 5. Tax Configuration

VAT control is centralized in settings:

```json
{
  "vat_enabled": true,
  "vat_rate": 0.15,           // 15% VAT (South Africa)
  "tax_number": "12345678901" // Business tax registration
}
```

This will later control:
- VAT line item calculations on transactions
- Tax report generation
- Compliance reporting

#### 6. Backup Provider Configuration

```json
{
  "backup_provider": "google_drive",  // or onedrive, dropbox
  "backup_enabled": true,
  "last_backup": "2024-01-15T10:30:00Z"
}
```

**Test Connection:**
```bash
curl -X POST http://localhost:8000/api/settings/user123/backup/test
```

### Database Schema (MongoDB)

#### BusinessSettings Collection
```json
{
  "_id": "ObjectId",
  "owner_id": "user123",
  "business_profile": {
    "business_name": "Rainbow Poultry Farm",
    "owner_name": "John Mkhize",
    "owner_email": "john@rainbowpoultry.co.za",
    "phone_number": "+27791234567",
    "website": "www.rainbowpoultry.co.za"
  },
  "industry": "poultry",
  "currency": "ZAR",
  "fiscal_year_start": "01-01",
  "vat_enabled": true,
  "vat_rate": 0.15,
  "tax_number": null,
  "backup_provider": "google_drive",
  "backup_enabled": true,
  "last_backup": "2024-01-15T10:30:00Z",
  "chart_of_accounts": [
    {"code": "1000", "name": "Cash", "account_type": "asset"},
    // ... auto-generated based on industry
  ],
  "created_at": "2024-01-10T08:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Integration with AI Service

The AI Service will eventually use Settings context for smarter categorization:

```python
# Future implementation
result = await ai_service.categorize_transaction(
    description="Bought chicken feed R3000",
    amount=3000,
    industry="poultry"  # From Settings
)
# Returns: {"account": "Inventory - Feed", "code": "1200", "confidence": 0.98}
```

Currently, the AI Service operates with fallback rules; Settings integration will improve accuracy.

## Next Steps

1. ✅ **Settings Module** - Business configuration, industry selection, COA mapping (COMPLETED)
2. **MongoDB Integration** - Replace in-memory settings storage with persistent MongoDB
3. **Settings → AI Context** - Pass industry context to AI Service for smarter categorization
4. **JWT Authentication** - Protect Settings endpoints with Firebase auth
5. **Duplicate Detection** - String similarity algorithm for transaction matching
6. **Batch Reporting** - P&L, Trial Balance, Balance Sheet, VAT reports
7. **Cloud Backup OAuth** - Google Drive, OneDrive, Dropbox integration
8. **Multi-user Roles** - Owner, Clerk, Viewer access levels

---

For frontend integration, see the main [README.md](../README.md)
