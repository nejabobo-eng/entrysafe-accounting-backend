import csv
import io
from fastapi import UploadFile
from typing import List

class FileParserService:
    
    async def parse_csv(self, file: UploadFile):
        """
        Parse a CSV file (bank statement) and extract transactions.
        Expected columns: Date, Description, Amount
        """
        try:
            contents = await file.read()
            text = contents.decode('utf-8')
            
            # Parse CSV
            reader = csv.DictReader(io.StringIO(text))
            transactions = []
            
            for row in reader:
                transaction = {
                    "date": row.get("Date", ""),
                    "description": row.get("Description", ""),
                    "amount": float(row.get("Amount", 0))
                }
                transactions.append(transaction)
            
            return {
                "filename": file.filename,
                "total_transactions": len(transactions),
                "parsed_transactions": transactions
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "message": "Failed to parse CSV file"
            }
    
    async def parse_excel(self, file: UploadFile):
        """
        Parse an Excel file (bank statement) and extract transactions.
        """
        try:
            contents = await file.read()
            
            # For now, placeholder for Excel parsing
            # Will use openpyxl or pandas in production
            return {
                "filename": file.filename,
                "total_transactions": 0,
                "parsed_transactions": [],
                "message": "Excel parsing coming soon"
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "message": "Failed to parse Excel file"
            }
