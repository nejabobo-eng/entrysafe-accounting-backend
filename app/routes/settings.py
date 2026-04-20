from fastapi import APIRouter, HTTPException, status
from app.models.settings import (
    BusinessSettings,
    BusinessSettingsUpdate,
    IndustryType,
    IndustryAccountStructure,
    AccountMapping,
    BackupProvider,
)
from typing import List
from datetime import datetime

router = APIRouter(prefix="/api/settings", tags=["Settings"])

# Industry-specific Chart of Accounts templates
INDUSTRY_COA_TEMPLATES = {
    IndustryType.POULTRY: IndustryAccountStructure(
        industry=IndustryType.POULTRY,
        description="Chart of Accounts for Poultry Farming Business",
        accounts=[
            # Assets
            AccountMapping(code="1000", name="Cash", account_type="asset"),
            AccountMapping(code="1010", name="Bank Account", account_type="asset"),
            AccountMapping(code="1100", name="Accounts Receivable", account_type="asset"),
            AccountMapping(code="1200", name="Inventory - Feed", account_type="asset"),
            AccountMapping(code="1210", name="Inventory - Poultry", account_type="asset"),
            AccountMapping(code="1300", name="Equipment", account_type="asset"),
            AccountMapping(code="1310", name="Accumulated Depreciation", account_type="asset"),
            # Liabilities
            AccountMapping(code="2000", name="Accounts Payable", account_type="liability"),
            AccountMapping(code="2100", name="Loans Payable", account_type="liability"),
            # Equity
            AccountMapping(code="3000", name="Owner's Capital", account_type="equity"),
            AccountMapping(code="3100", name="Retained Earnings", account_type="equity"),
            # Revenue
            AccountMapping(code="4000", name="Egg Sales Revenue", account_type="revenue"),
            AccountMapping(code="4010", name="Poultry Sales Revenue", account_type="revenue"),
            AccountMapping(code="4020", name="Manure Sales Revenue", account_type="revenue"),
            # Expenses
            AccountMapping(code="5000", name="Feed Expense", account_type="expense"),
            AccountMapping(code="5010", name="Veterinary Expense", account_type="expense"),
            AccountMapping(code="5020", name="Labor Expense", account_type="expense"),
            AccountMapping(code="5030", name="Utilities Expense", account_type="expense"),
            AccountMapping(code="5040", name="Depreciation Expense", account_type="expense"),
            AccountMapping(code="5050", name="Marketing Expense", account_type="expense"),
        ]
    ),
    IndustryType.RETAIL: IndustryAccountStructure(
        industry=IndustryType.RETAIL,
        description="Chart of Accounts for Retail Business",
        accounts=[
            # Assets
            AccountMapping(code="1000", name="Cash", account_type="asset"),
            AccountMapping(code="1010", name="Bank Account", account_type="asset"),
            AccountMapping(code="1100", name="Accounts Receivable", account_type="asset"),
            AccountMapping(code="1200", name="Inventory", account_type="asset"),
            AccountMapping(code="1300", name="Equipment", account_type="asset"),
            # Liabilities
            AccountMapping(code="2000", name="Accounts Payable", account_type="liability"),
            AccountMapping(code="2100", name="Short-term Loans", account_type="liability"),
            # Equity
            AccountMapping(code="3000", name="Owner's Capital", account_type="equity"),
            AccountMapping(code="3100", name="Retained Earnings", account_type="equity"),
            # Revenue
            AccountMapping(code="4000", name="Sales Revenue", account_type="revenue"),
            AccountMapping(code="4010", name="Sales Discounts", account_type="revenue"),
            # Expenses
            AccountMapping(code="5000", name="Cost of Goods Sold", account_type="expense"),
            AccountMapping(code="5010", name="Salaries & Wages", account_type="expense"),
            AccountMapping(code="5020", name="Rent Expense", account_type="expense"),
            AccountMapping(code="5030", name="Utilities Expense", account_type="expense"),
            AccountMapping(code="5040", name="Marketing Expense", account_type="expense"),
            AccountMapping(code="5050", name="Depreciation Expense", account_type="expense"),
        ]
    ),
    IndustryType.SERVICES: IndustryAccountStructure(
        industry=IndustryType.SERVICES,
        description="Chart of Accounts for Service Business",
        accounts=[
            # Assets
            AccountMapping(code="1000", name="Cash", account_type="asset"),
            AccountMapping(code="1010", name="Bank Account", account_type="asset"),
            AccountMapping(code="1100", name="Accounts Receivable", account_type="asset"),
            AccountMapping(code="1300", name="Equipment", account_type="asset"),
            # Liabilities
            AccountMapping(code="2000", name="Accounts Payable", account_type="liability"),
            AccountMapping(code="2100", name="Short-term Loans", account_type="liability"),
            # Equity
            AccountMapping(code="3000", name="Owner's Capital", account_type="equity"),
            AccountMapping(code="3100", name="Retained Earnings", account_type="equity"),
            # Revenue
            AccountMapping(code="4000", name="Service Revenue", account_type="revenue"),
            # Expenses
            AccountMapping(code="5000", name="Salaries & Wages", account_type="expense"),
            AccountMapping(code="5010", name="Office Rent", account_type="expense"),
            AccountMapping(code="5020", name="Utilities Expense", account_type="expense"),
            AccountMapping(code="5030", name="Marketing Expense", account_type="expense"),
            AccountMapping(code="5040", name="Professional Fees", account_type="expense"),
            AccountMapping(code="5050", name="Depreciation Expense", account_type="expense"),
        ]
    ),
    IndustryType.AGRICULTURE: IndustryAccountStructure(
        industry=IndustryType.AGRICULTURE,
        description="Chart of Accounts for Agriculture Business",
        accounts=[
            # Assets
            AccountMapping(code="1000", name="Cash", account_type="asset"),
            AccountMapping(code="1010", name="Bank Account", account_type="asset"),
            AccountMapping(code="1100", name="Accounts Receivable", account_type="asset"),
            AccountMapping(code="1200", name="Seeds & Fertilizer Inventory", account_type="asset"),
            AccountMapping(code="1210", name="Crop Inventory", account_type="asset"),
            AccountMapping(code="1300", name="Farm Equipment", account_type="asset"),
            AccountMapping(code="1310", name="Accumulated Depreciation", account_type="asset"),
            # Liabilities
            AccountMapping(code="2000", name="Accounts Payable", account_type="liability"),
            AccountMapping(code="2100", name="Farm Loans", account_type="liability"),
            # Equity
            AccountMapping(code="3000", name="Owner's Capital", account_type="equity"),
            AccountMapping(code="3100", name="Retained Earnings", account_type="equity"),
            # Revenue
            AccountMapping(code="4000", name="Crop Sales Revenue", account_type="revenue"),
            # Expenses
            AccountMapping(code="5000", name="Seeds & Fertilizer Expense", account_type="expense"),
            AccountMapping(code="5010", name="Labor Expense", account_type="expense"),
            AccountMapping(code="5020", name="Water & Irrigation", account_type="expense"),
            AccountMapping(code="5030", name="Equipment Maintenance", account_type="expense"),
            AccountMapping(code="5040", name="Depreciation Expense", account_type="expense"),
        ]
    ),
}


def get_industry_coa(industry: IndustryType) -> List[AccountMapping]:
    """Get Chart of Accounts for a specific industry"""
    if industry in INDUSTRY_COA_TEMPLATES:
        return INDUSTRY_COA_TEMPLATES[industry].accounts
    # Default generic COA for unsupported industries
    return [
        AccountMapping(code="1000", name="Cash", account_type="asset"),
        AccountMapping(code="1100", name="Accounts Receivable", account_type="asset"),
        AccountMapping(code="2000", name="Accounts Payable", account_type="liability"),
        AccountMapping(code="3000", name="Owner's Capital", account_type="equity"),
        AccountMapping(code="4000", name="Revenue", account_type="revenue"),
        AccountMapping(code="5000", name="Expenses", account_type="expense"),
    ]


# In-memory storage for demo (will be replaced with MongoDB later)
business_settings_db: dict = {}


@router.get("/")
async def list_businesses():
    """List all businesses (admin endpoint)"""
    return {
        "count": len(business_settings_db),
        "businesses": list(business_settings_db.values())
    }


@router.get("/{owner_id}")
async def get_business_settings(owner_id: str):
    """Get settings for a specific business owner"""
    if owner_id not in business_settings_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No settings found for owner {owner_id}"
        )
    return business_settings_db[owner_id]


@router.post("/")
async def create_business_settings(settings: BusinessSettings):
    """Create new business settings with auto-generated Chart of Accounts"""
    if settings.owner_id in business_settings_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Settings already exist for owner {settings.owner_id}"
        )
    
    # Auto-populate Chart of Accounts based on industry
    settings.chart_of_accounts = get_industry_coa(settings.industry)
    
    business_settings_db[settings.owner_id] = settings
    
    return {
        "message": f"Business settings created for {settings.business_profile.business_name}",
        "owner_id": settings.owner_id,
        "industry": settings.industry,
        "accounts_count": len(settings.chart_of_accounts),
        "vat_enabled": settings.vat_enabled,
        "vat_rate": settings.vat_rate
    }


@router.put("/{owner_id}")
async def update_business_settings(owner_id: str, updates: BusinessSettingsUpdate):
    """Update business settings"""
    if owner_id not in business_settings_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No settings found for owner {owner_id}"
        )
    
    existing_settings = business_settings_db[owner_id]
    
    # Update fields if provided
    if updates.business_profile:
        existing_settings.business_profile = updates.business_profile
    if updates.industry:
        existing_settings.industry = updates.industry
        # Regenerate COA if industry changed
        existing_settings.chart_of_accounts = get_industry_coa(updates.industry)
    if updates.currency:
        existing_settings.currency = updates.currency
    if updates.vat_enabled is not None:
        existing_settings.vat_enabled = updates.vat_enabled
    if updates.vat_rate is not None:
        existing_settings.vat_rate = updates.vat_rate
    if updates.backup_provider:
        existing_settings.backup_provider = updates.backup_provider
    if updates.backup_enabled is not None:
        existing_settings.backup_enabled = updates.backup_enabled
    
    existing_settings.updated_at = datetime.now()
    business_settings_db[owner_id] = existing_settings
    
    return {
        "message": "Settings updated successfully",
        "owner_id": owner_id,
        "settings": existing_settings
    }


@router.delete("/{owner_id}")
async def delete_business_settings(owner_id: str):
    """Delete business settings"""
    if owner_id not in business_settings_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No settings found for owner {owner_id}"
        )
    
    deleted = business_settings_db.pop(owner_id)
    return {
        "message": f"Settings deleted for {deleted.business_profile.business_name}",
        "owner_id": owner_id
    }


@router.get("/coa/industries")
async def list_available_industries():
    """List all supported industries and their COA templates"""
    return {
        "industries": [
            {
                "value": industry.value,
                "label": industry.name.replace("_", " ").title(),
                "description": INDUSTRY_COA_TEMPLATES.get(
                    industry,
                    IndustryAccountStructure(
                        industry=industry,
                        description=f"{industry.name} (Generic)",
                        accounts=[]
                    )
                ).description,
                "accounts_count": len(get_industry_coa(industry))
            }
            for industry in IndustryType
        ]
    }


@router.get("/coa/{industry}")
async def get_industry_chart_of_accounts(industry: str):
    """Get Chart of Accounts for a specific industry"""
    try:
        industry_type = IndustryType(industry.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid industry: {industry}. Supported industries: {[i.value for i in IndustryType]}"
        )
    
    coa = get_industry_coa(industry_type)
    return {
        "industry": industry_type.value,
        "accounts": coa,
        "count": len(coa)
    }


@router.post("/{owner_id}/backup/test")
async def test_backup_connection(owner_id: str):
    """Test backup provider connection (placeholder for OAuth integration)"""
    if owner_id not in business_settings_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No settings found for owner {owner_id}"
        )
    
    settings = business_settings_db[owner_id]
    
    if settings.backup_provider == BackupProvider.NONE:
        return {
            "status": "warning",
            "message": "No backup provider configured"
        }
    
    # Placeholder for actual OAuth test
    return {
        "status": "success",
        "message": f"Backup provider '{settings.backup_provider.value}' configured",
        "provider": settings.backup_provider.value,
        "note": "OAuth integration pending"
    }
