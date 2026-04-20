from flask import jsonify
from app.services.ai_service import AIService

def categorize_transaction(data):
    """
    Use OpenAI to automatically categorize a transaction.
    Returns the best Chart of Account match.
    """
    description = data.get("description", "")
    amount = data.get("amount")

    ai_service = AIService()
    result = ai_service.categorize_transaction_sync(
        description=description,
        amount=amount
    )
    return jsonify(result), 200

def get_chart_of_accounts():
    """
    Get the predefined Chart of Accounts for categorization.
    """
    return jsonify({
        "accounts": [
            {"code": "1000", "name": "Cash", "type": "Asset"},
            {"code": "1100", "name": "Accounts Receivable", "type": "Asset"},
            {"code": "1200", "name": "Inventory", "type": "Asset"},
            {"code": "2000", "name": "Accounts Payable", "type": "Liability"},
            {"code": "3000", "name": "Revenue", "type": "Income"},
            {"code": "4000", "name": "Cost of Goods Sold", "type": "Expense"},
            {"code": "5000", "name": "Operating Expenses", "type": "Expense"},
        ]
    }), 200
