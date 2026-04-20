from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class AccountType(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"

class Account(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    code: str
    name: str
    account_type: AccountType
    description: Optional[str] = None
    balance: float = 0.0
    is_active: bool = True

    class Config:
        allow_population_by_field_name = True
