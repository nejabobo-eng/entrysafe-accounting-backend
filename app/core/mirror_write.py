"""
Mirror Write Strategy: Write to both in-memory and MongoDB simultaneously.

This ensures:
1. Zero risk migration (in-memory is fallback)
2. Data consistency (same write to both)
3. Easy rollback (just disable MongoDB writes)
4. Progressive read switch (gradual migration)

Flow:
  User Input
    ↓
  Write to In-Memory (ALWAYS)
    ↓
  Write to MongoDB (new, with fallback)
    ↓
  Return success if in-memory succeeds
  (MongoDB failure = log warning, still succeed)
"""

from typing import Dict, Any, Optional
from datetime import datetime
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class MirrorWriter:
    """
    Handles dual writes to both in-memory and MongoDB.
    In-memory is the source of truth for now.
    MongoDB is a backup/persistent copy.
    """
    
    @staticmethod
    async def write_transaction(
        in_memory_db: dict,
        mongo_db: Any,
        transaction_id: str,
        transaction_data: Dict[str, Any]
    ) -> bool:
        """
        Write transaction to both in-memory and MongoDB.
        
        Args:
            in_memory_db: Reference to transactions_db dict
            mongo_db: Motor async database instance
            transaction_id: ID of transaction
            transaction_data: Transaction document to write
        
        Returns:
            True if in-memory write succeeded (MongoDB failure is non-blocking)
        """
        try:
            # STEP 1: Always write to in-memory (never fails)
            in_memory_db[transaction_id] = transaction_data
            logger.debug(f"[MIRROR] In-memory write OK: {transaction_id}")
            
            # STEP 2: Attempt to write to MongoDB (non-blocking)
            try:
                await mongo_db.transactions.insert_one({
                    "_id": ObjectId(transaction_id),
                    **transaction_data,
                    "created_at": datetime.utcnow()
                })
                logger.debug(f"[MIRROR] MongoDB write OK: {transaction_id}")
            except Exception as mongo_error:
                # MongoDB failed, but in-memory succeeded
                # Log the error but don't fail the request
                logger.warning(f"[MIRROR] MongoDB write failed (non-blocking): {mongo_error}")
                # System continues - in-memory is the active store
            
            return True
            
        except Exception as e:
            logger.error(f"[MIRROR] In-memory write failed: {e}")
            raise  # This should never happen with dict

    @staticmethod
    async def write_journal_entry(
        in_memory_db: dict,
        mongo_db: Any,
        transaction_id: str,
        journal_data: Dict[str, Any]
    ) -> bool:
        """
        Write journal entry to both in-memory and MongoDB.
        Same strategy as transactions.
        """
        try:
            # In-memory write (primary)
            in_memory_db[transaction_id] = journal_data
            logger.debug(f"[MIRROR] Journal in-memory OK: {transaction_id}")
            
            # MongoDB write (backup, non-blocking)
            try:
                await mongo_db.journal_entries.insert_one({
                    "_id": ObjectId(),
                    "transaction_id": transaction_id,
                    **journal_data,
                    "created_at": datetime.utcnow()
                })
                logger.debug(f"[MIRROR] Journal MongoDB OK: {transaction_id}")
            except Exception as mongo_error:
                logger.warning(f"[MIRROR] Journal MongoDB write failed (non-blocking): {mongo_error}")
            
            return True
            
        except Exception as e:
            logger.error(f"[MIRROR] Journal in-memory write failed: {e}")
            raise

    @staticmethod
    async def delete_mirror(
        in_memory_db: dict,
        mongo_db: Any,
        transaction_id: str
    ) -> bool:
        """
        Delete from both in-memory and MongoDB.
        In-memory delete is primary (must succeed).
        MongoDB delete is secondary.
        """
        try:
            # In-memory delete (primary)
            if transaction_id in in_memory_db:
                del in_memory_db[transaction_id]
                logger.debug(f"[MIRROR] In-memory delete OK: {transaction_id}")
            
            # MongoDB delete (secondary)
            try:
                await mongo_db.transactions.delete_one({"_id": ObjectId(transaction_id)})
                logger.debug(f"[MIRROR] MongoDB delete OK: {transaction_id}")
            except Exception as mongo_error:
                logger.warning(f"[MIRROR] MongoDB delete failed (non-blocking): {mongo_error}")
            
            return True
            
        except Exception as e:
            logger.error(f"[MIRROR] Delete failed: {e}")
            raise


class ReadStrategy:
    """
    Handles reading from the correct source during migration.
    
    PHASE 1 (Current): Read from in-memory (MongoDB is write-only)
    PHASE 2 (Next): Read from MongoDB (in-memory still gets writes)
    PHASE 3 (Final): Remove in-memory entirely
    """
    
    # Current phase (change this to switch read source)
    CURRENT_PHASE = "phase_1"  # Options: "phase_1", "phase_2", "phase_3"
    
    @staticmethod
    async def read_transaction(
        in_memory_db: dict,
        mongo_db: Any,
        transaction_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Read transaction based on current phase.
        """
        if ReadStrategy.CURRENT_PHASE == "phase_1":
            # Read from in-memory only
            return in_memory_db.get(transaction_id)
        
        elif ReadStrategy.CURRENT_PHASE == "phase_2":
            # Try MongoDB first, fall back to in-memory
            try:
                doc = await mongo_db.transactions.find_one(
                    {"_id": ObjectId(transaction_id)}
                )
                if doc:
                    # Remove MongoDB's _id, keep our id
                    return {k: v for k, v in doc.items() if k != "_id"}
                # Not found in MongoDB, try in-memory
                return in_memory_db.get(transaction_id)
            except Exception as e:
                logger.warning(f"[READ] MongoDB read failed, using in-memory: {e}")
                return in_memory_db.get(transaction_id)
        
        elif ReadStrategy.CURRENT_PHASE == "phase_3":
            # Read only from MongoDB
            try:
                doc = await mongo_db.transactions.find_one(
                    {"_id": ObjectId(transaction_id)}
                )
                if doc:
                    return {k: v for k, v in doc.items() if k != "_id"}
            except Exception as e:
                logger.error(f"[READ] MongoDB read failed: {e}")
            return None
    
    @staticmethod
    async def list_user_transactions(
        in_memory_db: dict,
        mongo_db: Any,
        owner_id: str,
        limit: int = 10,
        skip: int = 0
    ) -> tuple[list, int]:
        """
        List user transactions from appropriate source.
        Returns (transactions, total_count)
        """
        if ReadStrategy.CURRENT_PHASE == "phase_1":
            # Read from in-memory
            results = [
                tx for tx in in_memory_db.values()
                if tx.get("owner_id") == owner_id
            ]
            filtered = results[skip:skip + limit]
            return (filtered, len(results))
        
        elif ReadStrategy.CURRENT_PHASE in ["phase_2", "phase_3"]:
            # Read from MongoDB
            try:
                cursor = mongo_db.transactions.find(
                    {"owner_id": owner_id}
                ).skip(skip).limit(limit)
                
                results = []
                async for doc in cursor:
                    results.append({k: v for k, v in doc.items() if k != "_id"})
                
                total = await mongo_db.transactions.count_documents(
                    {"owner_id": owner_id}
                )
                return (results, total)
            except Exception as e:
                logger.warning(f"[READ] MongoDB list failed: {e}")
                # Fallback to in-memory
                results = [
                    tx for tx in in_memory_db.values()
                    if tx.get("owner_id") == owner_id
                ]
                filtered = results[skip:skip + limit]
                return (filtered, len(results))
