from flask import jsonify

def get_sample_csv_template():
    """
    Get a sample CSV template for bank statement uploads.
    """
    return jsonify({
        "template": "Date,Description,Amount\n2024-01-15,Feed Supplies,-1500.00\n2024-01-16,Feed Sales,+5000.00",
        "columns": ["Date", "Description", "Amount"]
    }), 200
