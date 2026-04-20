from fastapi import APIRouter, HTTPException, status
from app.models.transaction import (
    Transaction,
    JournalEntry,
    JournalEntryLine,
    TransactionInput,
    TransactionResponse,
    TransactionSource,
    EntryType,
)
from app.routes.settings import business_settings_db, get_industry_coa
from app.services.ai_service import AIService
from app.core.database import get_database
from app.core.mirror_write import MirrorWriter, ReadStrategy
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
import re
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])

# In-memory storage (will be replaced with MongoDB later)
transactions_db: dict = {}
journal_entries_db: dict = {}

# LAZY initialization - don't create at import time
_ai_service: Optional[AIService] = None

def get_ai_service() -> AIService:
    """Get or create AI service (lazy initialization)"""
    global _ai_service
    if _ai_service is None:
        logger.info("Initializing AI Service...")
        _ai_service = AIService()
        logger.info("✅ AI Service initialized")
    return _ai_service


def extract_amount_from_text(text: str) -> Optional[float]:
    """
    Extract amount from text like "Bought feed R3000" or "R 3000.50"
    Returns float amount or None if not found
    """
    match = re.search(r'R\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', text)
    if match:
        # Remove commas and convert to float
        return float(match.group(1).replace(',', ''))
    return None


def convert_ai_response_to_journal_entries(
    ai_response: dict,
    owner_id: str,
    transaction_id: str,
    date: datetime,
    description: str
) -> JournalEntry:
    """
    Convert AI service response to JournalEntry model.
    
    AI response format:
    {
        'entries': [
            {'account': 'Feed Expense', 'code': '5000', 'type': 'debit', 'amount': 3000},
            {'account': 'Bank', 'code': '1010', 'type': 'credit', 'amount': 3000}
        ],
        'confidence': 0.92,
        'reasoning': '...',
        'source': 'ai'
    }
    """
    journal_lines = []
    
    for entry in ai_response.get('entries', []):
        line = JournalEntryLine(
            account_code=entry['code'],
            account_name=entry['account'],
            entry_type=EntryType(entry['type']),
            amount=entry['amount']
        )
        journal_lines.append(line)
    
    # Create JournalEntry
    journal_entry = JournalEntry(
        owner_id=owner_id,
        transaction_id=transaction_id,
        date=date,
        description=description,
        entries=journal_lines
    )
    
    # Calculate totals and validate balance
    journal_entry.calculate_totals()
    
    return journal_entry


@router.post("/")
async def create_transaction(transaction_input: TransactionInput) -> TransactionResponse:
    """
    Create a new transaction with AI-generated double-entry journal.
    
    Input:
    {
        "owner_id": "user@example.com",
        "text": "Bought feed R3000",
        "date": "2024-01-15T10:30:00Z"  (optional, defaults to now)
    }
    
    Flow:
    1. Validate owner has settings
    2. Extract amount from text
    3. Call AI to generate journal
    4. Create Transaction and JournalEntry
    5. Store both
    6. Return response
    """
    owner_id = transaction_input.owner_id
    text = transaction_input.text
    date = transaction_input.date or datetime.utcnow()
    
    # Step 1: Validate owner has settings
    if owner_id not in business_settings_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No settings found for owner {owner_id}. Please create settings first."
        )
    
    business_settings = business_settings_db[owner_id]
    
    # Step 2: Extract amount from text
    amount = extract_amount_from_text(text)
    if amount is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract amount from text. Use format: 'Description R3000'"
        )
    
    # Step 3: Prepare AI call
    industry = business_settings.industry.value
    available_accounts = [
        {
            "code": acc.code,
            "name": acc.name,
            "account_type": acc.account_type
        }
        for acc in business_settings.chart_of_accounts
    ]

    try:
        # Call AI to generate journal (lazy init here)
        ai_response = await get_ai_service().generate_journal(
            description=text,
            amount=amount,
            industry=industry,
            available_accounts=available_accounts,
            date=date.isoformat() if date else None
        )
    except ValueError as e:
        # AI validation failed
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"AI validation failed: {str(e)}"
        )
    except Exception as e:
        # AI service error (timeout, API error, etc.)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {str(e)}"
        )
    
    # Step 4: Create Transaction and JournalEntry objects
    transaction_id = str(ObjectId())
    
    transaction = Transaction(
        id=transaction_id,
        owner_id=owner_id,
        date=date,
        description=text,
        amount=amount,
        source=TransactionSource.AI,
        ai_confidence=ai_response.get('confidence'),
        requires_review=ai_response.get('confidence', 1.0) < 0.85
    )
    
    journal_entry = convert_ai_response_to_journal_entries(
        ai_response,
        owner_id,
        transaction_id,
        date,
        text
    )
    
    # Validate that journal is balanced
    if not journal_entry.is_balanced:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Journal entry is not balanced: debit={journal_entry.total_debit}, credit={journal_entry.total_credit}"
        )

    # Step 5: Mirror write to both in-memory and MongoDB
    try:
        mongo_db = get_database()

        # Convert to dicts for storage
        transaction_dict = transaction.dict()
        journal_dict = journal_entry.dict()

        # Write transaction
        await MirrorWriter.write_transaction(
            transactions_db,
            mongo_db,
            transaction_id,
            transaction_dict
        )

        # Write journal entry
        await MirrorWriter.write_journal_entry(
            journal_entries_db,
            mongo_db,
            transaction_id,
            journal_dict
        )

        logger.info(f"[CREATE] Transaction created: {transaction_id} for {owner_id}")

    except Exception as e:
        logger.error(f"[CREATE] Storage failed: {e}")
        # If mirror write fails completely, still fail the request
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to store transaction: {str(e)}"
        )

    # Step 6: Return response
    return TransactionResponse(
        transaction=transaction,
        journal_entry=journal_entry,
        message=f"Transaction created successfully with balanced journal entry (confidence: {ai_response.get('confidence', 1.0):.2f})"
    )


@router.get("/{transaction_id}")
async def get_transaction(transaction_id: str):
    """
    Retrieve a specific transaction and its journal entry.
    """
    if transaction_id not in transactions_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found"
        )
    
    transaction = transactions_db[transaction_id]
    journal_entry = journal_entries_db.get(transaction_id)
    
    return TransactionResponse(
        transaction=transaction,
        journal_entry=journal_entry,
        message="Transaction retrieved successfully"
    )


@router.get("/user/{owner_id}")
async def get_user_transactions(owner_id: str, limit: int = 50, skip: int = 0):
    """
    Retrieve all transactions for a specific owner.
    
    Query parameters:
    - limit: Maximum number of transactions to return (default: 50)
    - skip: Number of transactions to skip (default: 0)
    """
    user_transactions = [
        tx for tx in transactions_db.values()
        if tx.owner_id == owner_id
    ]
    
    # Sort by date descending
    user_transactions.sort(key=lambda x: x.date, reverse=True)
    
    # Apply pagination
    paginated = user_transactions[skip:skip + limit]
    
    # Build response with journal entries
    result = []
    for transaction in paginated:
        journal_entry = journal_entries_db.get(transaction.id)
        result.append({
            "transaction": transaction,
            "journal_entry": journal_entry
        })
    
    return {
        "owner_id": owner_id,
        "count": len(result),
        "total": len(user_transactions),
        "transactions": result
    }


@router.get("/")
async def list_all_transactions(limit: int = 100, skip: int = 0):
    """
    List all transactions (admin endpoint).
    
    Query parameters:
    - limit: Maximum number to return (default: 100)
    - skip: Number to skip (default: 0)
    """
    all_transactions = list(transactions_db.values())
    all_transactions.sort(key=lambda x: x.date, reverse=True)
    
    paginated = all_transactions[skip:skip + limit]
    
    result = []
    for transaction in paginated:
        journal_entry = journal_entries_db.get(transaction.id)
        result.append({
            "transaction": transaction,
            "journal_entry": journal_entry
        })
    
    return {
        "count": len(result),
        "total": len(all_transactions),
        "transactions": result
    }


@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: str):
    """
    Delete a transaction and its journal entry.
    Uses mirror delete (removes from both in-memory and MongoDB).
    """
    if transaction_id not in transactions_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found"
        )

    try:
        mongo_db = get_database()

        # Mirror delete (in-memory primary, MongoDB secondary)
        await MirrorWriter.delete_mirror(
            transactions_db,
            mongo_db,
            transaction_id
        )

        # Also remove from journal entries
        journal_entries_db.pop(transaction_id, None)

        logger.info(f"[DELETE] Transaction deleted: {transaction_id}")

    except Exception as e:
        logger.warning(f"[DELETE] Mirror delete failed: {e}")
        # Still attempt in-memory delete (primary)
        transactions_db.pop(transaction_id, None)
        journal_entries_db.pop(transaction_id, None)

    return {
        "message": "Transaction deleted successfully",
        "transaction_id": transaction_id
    }
