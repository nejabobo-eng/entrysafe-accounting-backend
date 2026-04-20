from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum


class IndustryType(str, Enum):
    """Supported business industries with predefined COA structures"""
    POULTRY = "poultry"
    RETAIL = "retail"
    SERVICES = "services"
    AGRICULTURE = "agriculture"
    MANUFACTURING = "manufacturing"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    HOSPITALITY = "hospitality"
    CONSTRUCTION = "construction"
    OTHER = "other"


class BackupProvider(str, Enum):
    """Cloud backup providers"""
    GOOGLE_DRIVE = "google_drive"
    ONEDRIVE = "onedrive"
    DROPBOX = "dropbox"
    NONE = "none"


class AccountMapping(BaseModel):
    """Account mapping for a specific industry"""
    code: str
    name: str
    account_type: str


class IndustryAccountStructure(BaseModel):
    """Industry-specific Chart of Accounts structure"""
    industry: IndustryType
    accounts: List[AccountMapping]
    description: str


class BusinessProfile(BaseModel):
    """Basic business profile information"""
    business_name: str
    owner_name: str
    owner_email: str
    phone_number: Optional[str] = None
    website: Optional[str] = None
    registration_number: Optional[str] = None


class BusinessSettings(BaseModel):
    """Main settings model for a business"""
    id: Optional[str] = Field(None, alias="_id")
    owner_id: str  # Will be linked to Firebase user ID
    business_profile: BusinessProfile
    industry: IndustryType
    currency: str = "ZAR"  # Default to South African Rand
    fiscal_year_start: str = "01-01"  # MM-DD format
    
    # Tax configuration
    vat_enabled: bool = True
    vat_rate: float = 0.15  # 15% VAT
    tax_number: Optional[str] = None
    
    # Backup configuration
    backup_provider: BackupProvider = BackupProvider.NONE
    backup_enabled: bool = False
    last_backup: Optional[datetime] = None
    
    # Chart of Accounts (auto-populated based on industry)
    chart_of_accounts: List[AccountMapping] = []
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True


class BusinessSettingsUpdate(BaseModel):
    """Update request model for business settings"""
    business_profile: Optional[BusinessProfile] = None
    industry: Optional[IndustryType] = None
    currency: Optional[str] = None
    vat_enabled: Optional[bool] = None
    vat_rate: Optional[float] = None
    backup_provider: Optional[BackupProvider] = None
    backup_enabled: Optional[bool] = None
