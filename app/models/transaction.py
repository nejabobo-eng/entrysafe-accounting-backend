from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum


class EntryType(str, Enum):
    """Debit or Credit entry type"""
    DEBIT = "debit"
    CREDIT = "credit"


class TransactionSource(str, Enum):
    """How the transaction was created"""
    AI = "ai"
    MANUAL = "manual"
    IMPORT = "import"


class JournalEntryLine(BaseModel):
    """Single line in a journal entry (debit or credit)"""
    account_code: str
    account_name: str
    entry_type: EntryType
    amount: float
    
    class Config:
        use_enum_values = True


class Transaction(BaseModel):
    """User-facing transaction record"""
    id: Optional[str] = Field(None, alias="_id")
    owner_id: str
    date: datetime
    description: str
    amount: float  # Total transaction amount
    source: TransactionSource = TransactionSource.AI
    ai_confidence: Optional[float] = None
    requires_review: bool = False
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True


class JournalEntry(BaseModel):
    """Double-entry journal with balanced debits and credits"""
    id: Optional[str] = Field(None, alias="_id")
    owner_id: str
    transaction_id: str
    date: datetime
    description: str
    entries: List[JournalEntryLine]  # Must have at least 2 lines
    total_debit: float = 0.0
    total_credit: float = 0.0
    is_balanced: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
    
    @validator('entries')
    def validate_entries(cls, v):
        """Ensure at least 2 entries (debit and credit)"""
        if len(v) < 2:
            raise ValueError('Journal entry must have at least 2 lines (debit and credit)')
        return v
    
    def calculate_totals(self):
        """Calculate total debits and credits"""
        self.total_debit = sum(
            entry.amount for entry in self.entries 
            if entry.entry_type == EntryType.DEBIT
        )
        self.total_credit = sum(
            entry.amount for entry in self.entries 
            if entry.entry_type == EntryType.CREDIT
        )
        self.is_balanced = abs(self.total_debit - self.total_credit) < 0.01
        return self.is_balanced


class TransactionInput(BaseModel):
    """User input for creating a transaction"""
    owner_id: str
    text: str
    date: Optional[datetime] = Field(default_factory=datetime.utcnow)


class TransactionResponse(BaseModel):
    """Response after creating a transaction"""
    transaction: Transaction
    journal_entry: JournalEntry
    message: str
