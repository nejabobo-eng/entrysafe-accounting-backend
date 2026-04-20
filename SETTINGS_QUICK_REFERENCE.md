# Settings Module - Quick Reference

## Overview
The Settings Module is the **command center** for Entry Safe V2. It controls:
- Business profile and contact information
- Industry selection → auto-generates Chart of Accounts
- VAT and tax configuration
- Cloud backup provider setup
- Currency and fiscal year settings

## Quick Start Examples

### 1. Create Business Settings for Poultry Farm

```bash
curl -X POST http://localhost:8000/api/settings/ \
  -H "Content-Type: application/json" \
  -d '{
    "owner_id": "user@example.com",
    "business_profile": {
      "business_name": "Rainbow Poultry Farm",
      "owner_name": "John Mkhize",
      "owner_email": "john@rainbowpoultry.co.za",
      "phone_number": "+27791234567"
    },
    "industry": "poultry",
    "currency": "ZAR",
    "vat_enabled": true,
    "vat_rate": 0.15
  }'
```

### 2. Get Business Settings

```bash
curl http://localhost:8000/api/settings/user@example.com
```

Response includes the **complete Chart of Accounts** with 20 poultry-specific accounts:
- Cash, Bank Account
- Inventory - Feed, Inventory - Poultry
- Egg Sales Revenue, Poultry Sales Revenue
- Feed Expense, Veterinary Expense, Labor Expense
- ... and more

### 3. Switch Industry (Auto-Regenerates COA)

```bash
curl -X PUT http://localhost:8000/api/settings/user@example.com \
  -H "Content-Type: application/json" \
  -d '{"industry": "retail"}'
```

The Chart of Accounts now changes to Retail-specific:
- Sales Revenue, Sales Discounts
- Cost of Goods Sold
- Salaries, Rent, Utilities
- ... and more

### 4. List All Supported Industries

```bash
curl http://localhost:8000/api/settings/coa/industries
```

Returns:
```json
{
  "industries": [
    {
      "value": "poultry",
      "label": "Poultry",
      "description": "Chart of Accounts for Poultry Farming Business",
      "accounts_count": 20
    },
    {
      "value": "retail",
      "label": "Retail",
      "description": "Chart of Accounts for Retail Business",
      "accounts_count": 17
    },
    // ... more industries
  ]
}
```

### 5. Get Chart of Accounts for Specific Industry

```bash
curl http://localhost:8000/api/settings/coa/agriculture
```

Returns the full COA structure for Agriculture with account codes and types.

### 6. Update Business Profile

```bash
curl -X PUT http://localhost:8000/api/settings/user@example.com \
  -H "Content-Type: application/json" \
  -d '{
    "business_profile": {
      "business_name": "Rainbow Poultry Farm Ltd",
      "owner_name": "John Mkhize",
      "owner_email": "john.mkhize@rainbowpoultry.co.za",
      "phone_number": "+27791234567",
      "registration_number": "2024/123456"
    }
  }'
```

### 7. Enable Cloud Backup

```bash
curl -X PUT http://localhost:8000/api/settings/user@example.com \
  -H "Content-Type: application/json" \
  -d '{
    "backup_provider": "google_drive",
    "backup_enabled": true
  }'
```

### 8. Test Backup Connection

```bash
curl -X POST http://localhost:8000/api/settings/user@example.com/backup/test
```

Response:
```json
{
  "status": "success",
  "message": "Backup provider 'google_drive' configured",
  "provider": "google_drive",
  "note": "OAuth integration pending"
}
```

## Supported Industries & Account Counts

| Industry | Accounts | Key Accounts |
|----------|----------|---|
| **Poultry** | 20 | Feed, Egg Sales, Veterinary, Livestock |
| **Retail** | 17 | Sales Revenue, COGS, Salaries, Rent |
| **Services** | 15 | Service Revenue, Professional Fees |
| **Agriculture** | 17 | Crop Sales, Seeds/Fertilizer, Water |
| **Manufacturing** | 6 | Generic fallback |
| **Healthcare** | 6 | Generic fallback |
| **Education** | 6 | Generic fallback |
| **Hospitality** | 6 | Generic fallback |
| **Construction** | 6 | Generic fallback |
| **Other** | 6 | Generic fallback |

## VAT Configuration

```json
{
  "vat_enabled": true,
  "vat_rate": 0.15,  // 15% in South Africa
  "tax_number": "12345678901"
}
```

**Future Impact:**
- VAT calculations on transactions
- VAT reports generation
- Tax compliance reporting

## Backup Providers (Coming Soon)

```json
{
  "backup_provider": "google_drive",  // or onedrive, dropbox, none
  "backup_enabled": true,
  "last_backup": "2024-01-15T10:30:00Z"
}
```

Currently configured but not yet integrated. OAuth flows pending implementation.

## Integration with AI Service

**Current:** AI Service uses fallback rules (keyword matching)

**Future:** AI Service will use Settings context:
```python
# Pass industry to AI for context-aware categorization
result = await ai_service.categorize_transaction(
    description="Bought chicken feed R3000",
    amount=3000,
    industry="poultry"  # From Settings
)
# Expected: {"account": "Inventory - Feed", "code": "1200"}
```

This will dramatically improve AI accuracy—it knows the user is a poultry farm, so "feed" naturally maps to Inventory-Feed account instead of generic guessing.

## Data Model

### BusinessProfile
```python
{
    "business_name": str,
    "owner_name": str,
    "owner_email": str,
    "phone_number": str (optional),
    "website": str (optional),
    "registration_number": str (optional)
}
```

### BusinessSettings
```python
{
    "owner_id": str,              # Unique business identifier
    "business_profile": {         # Profile info above
    "industry": IndustryType,     # poultry, retail, agriculture, etc.
    "currency": str,              # ZAR, USD, EUR, etc.
    "fiscal_year_start": str,     # MM-DD format (default: 01-01)
    "vat_enabled": bool,
    "vat_rate": float,            # e.g., 0.15 for 15%
    "tax_number": str,
    "backup_provider": BackupProvider,
    "backup_enabled": bool,
    "last_backup": datetime,
    "chart_of_accounts": [        # Auto-generated per industry
        {
            "code": str,
            "name": str,
            "account_type": str   # asset, liability, equity, revenue, expense
        }
    ],
    "created_at": datetime,
    "updated_at": datetime
}
```

## Error Handling

### Invalid Industry
```bash
curl http://localhost:8000/api/settings/coa/invalid_industry
```

Returns HTTP 400:
```json
{
  "detail": "Invalid industry: invalid_industry. Supported industries: [poultry, retail, services, ...]"
}
```

### Settings Not Found
```bash
curl http://localhost:8000/api/settings/nonexistent_user
```

Returns HTTP 404:
```json
{
  "detail": "No settings found for owner nonexistent_user"
}
```

### Duplicate Owner
```bash
curl -X POST http://localhost:8000/api/settings/ \
  -d '{"owner_id": "existing_user", ...}'
```

Returns HTTP 409:
```json
{
  "detail": "Settings already exist for owner existing_user"
}
```

## Development Notes

**Current Implementation:**
- ✅ In-memory storage (business_settings_db dict)
- ✅ Industry-based COA templates
- ✅ CRUD operations
- ✅ Dynamic COA regeneration on industry change

**Next Phase:**
- [ ] Replace in-memory with MongoDB persistence
- [ ] Add Firebase authentication
- [ ] Implement Cloud Backup OAuth
- [ ] Connect to AI Service for context injection

## Testing Checklist

- [ ] Create settings for each industry
- [ ] Verify COA count matches expected accounts
- [ ] Test industry switching (COA updates)
- [ ] Update VAT settings
- [ ] Test backup provider configuration
- [ ] Verify API documentation in Swagger UI (/docs)
- [ ] Load test with multiple business profiles
