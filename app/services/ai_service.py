import json
import asyncio
from app.config import settings
from typing import List, Dict, Optional


class AIService:
    """
    Generates validated double-entry journal entries from transaction descriptions.

    Contract: Every response MUST have:
    - entries: list with 2+ items
    - Each entry: {account, code, type: debit|credit, amount}
    - Debit total == Credit total
    - Accounts exist in provided COA
    """

    def __init__(self):
        # Lazy import - only import openai when first used
        import openai
        openai.api_key = settings.OPENAI_API_KEY
        self.model = 'gpt-3.5-turbo'
        self.max_retries = 2
        self.timeout = 15
        self.openai = openai

    async def generate_journal(
        self,
        description: str,
        amount: float,
        industry: str,
        available_accounts: List[Dict[str, str]],
        date: Optional[str] = None
    ) -> Dict:
        '''
        Generate double-entry journal from user input.
        
        Input:
            description: 'Bought feed R3000'
            amount: 3000
            industry: 'poultry'
            available_accounts: [{'code': '5000', 'name': 'Feed Expense', 'account_type': 'expense'}, ...]
        
        Output (contract):
        {
            'entries': [
                {'account': 'Feed Expense', 'code': '5000', 'type': 'debit', 'amount': 3000},
                {'account': 'Bank', 'code': '1010', 'type': 'credit', 'amount': 3000}
            ],
            'confidence': 0.92,
            'reasoning': 'Feed purchase debits expense, credits cash',
            'source': 'ai'
        }
        '''
        
        # Try AI first
        for attempt in range(self.max_retries):
            try:
                result = await asyncio.wait_for(
                    self._call_openai(description, amount, industry, available_accounts, date),
                    timeout=self.timeout
                )
                
                # Validate response
                if self._is_valid_journal(result, available_accounts):
                    result['source'] = 'ai'
                    return result
                else:
                    print(f'Invalid AI response: {result}')
                    
            except Exception as e:
                print(f'AI error on attempt {attempt + 1}: {e}')
                continue
        
        # Fallback
        return self._fallback_journal(description, amount, available_accounts)

    async def _call_openai(
        self,
        description: str,
        amount: float,
        industry: str,
        available_accounts: List[Dict[str, str]],
        date: Optional[str]
    ) -> Dict:
        '''Call OpenAI with strict double-entry prompt'''
        
        # Build account reference for AI
        account_text = '\n'.join([
            f"- {acc['name']} ({acc['code']})"
            for acc in available_accounts[:40]
        ])
        
        prompt = f'''You are an accounting system for {industry} businesses.

USER INPUT: {description} | Amount: {amount}

AVAILABLE ACCOUNTS:
{account_text}

RULES:
1. Use ONLY accounts above
2. Every transaction must balance (debit total = credit total)
3. Return ONLY valid JSON (no other text)
4. Typical patterns:
   - Purchase: Debit expense, Credit cash
   - Sale: Debit cash, Credit revenue
   - Payment: Debit payable, Credit cash

RESPOND WITH JSON ONLY:
{{
  "entries": [
    {{"account": "Account Name", "code": "1000", "type": "debit", "amount": 1000}},
    {{"account": "Account Name", "code": "1010", "type": "credit", "amount": 1000}}
  ],
  "confidence": 0.95,
  "reasoning": "Brief explanation"
}}'''

        response = await asyncio.to_thread(
            self.openai.ChatCompletion.create,
            model=self.model,
            messages=[
                {'role': 'system', 'content': 'You are an accounting system. Respond with ONLY valid JSON. No markdown, no explanations.'},
                {'role': 'user', 'content': prompt}
            ],
            temperature=0,
            max_tokens=400
        )

        content = response.choices[0].message.content.strip()
        
        # Clean potential markdown
        if content.startswith('`json'):
            content = content.replace('`json', '').replace('`', '').strip()
        elif content.startswith('```'):
            content = content.replace('```', '').strip()
        
        return json.loads(content)

    def _is_valid_journal(self, result: Dict, available_accounts: List[Dict[str, str]]) -> bool:
        '''Validate AI response against contract'''
        
        # Check structure
        if not result or not isinstance(result.get('entries'), list):
            return False
        
        entries = result['entries']
        
        # Must have 2+ entries
        if len(entries) < 2:
            print(f'Invalid: only {len(entries)} entries')
            return False
        
        # Validate each entry
        for entry in entries:
            if not all(k in entry for k in ['account', 'code', 'type', 'amount']):
                print(f'Invalid entry: missing required fields {entry}')
                return False
            
            if entry['type'] not in ['debit', 'credit']:
                print(f'Invalid entry type: {entry["type"]}')
                return False
            
            if not isinstance(entry['amount'], (int, float)) or entry['amount'] <= 0:
                print(f'Invalid amount: {entry["amount"]}')
                return False
        
        # Check account codes exist in COA
        account_codes = {acc['code'] for acc in available_accounts}
        for entry in entries:
            if entry['code'] not in account_codes:
                print(f'Invalid account code: {entry["code"]} not in COA')
                return False
        
        # Check balance
        total_debit = sum(e['amount'] for e in entries if e['type'] == 'debit')
        total_credit = sum(e['amount'] for e in entries if e['type'] == 'credit')
        
        if abs(total_debit - total_credit) > 0.01:
            print(f'Unbalanced: debit={total_debit}, credit={total_credit}')
            return False
        
        return True

    def _fallback_journal(self, description: str, amount: float, available_accounts: List[Dict[str, str]]) -> Dict:
        '''Simple rule-based fallback'''
        
        desc_lower = description.lower()
        
        # Find key accounts
        cash = next(
            (a for a in available_accounts if 'cash' in a['name'].lower() or 'bank' in a['name'].lower()),
            {'name': 'Cash', 'code': '1000', 'account_type': 'asset'}
        )
        
        # Detect transaction type and find appropriate account
        if any(word in desc_lower for word in ['bought', 'purchase', 'paid', 'expense', 'feed']):
            expense = next(
                (a for a in available_accounts if a['account_type'] == 'expense'),
                {'name': 'Operating Expense', 'code': '5000', 'account_type': 'expense'}
            )
            return {
                'entries': [
                    {'account': expense['name'], 'code': expense['code'], 'type': 'debit', 'amount': amount},
                    {'account': cash['name'], 'code': cash['code'], 'type': 'credit', 'amount': amount}
                ],
                'confidence': 0.60,
                'reasoning': 'Expense transaction (fallback rule)',
                'source': 'fallback'
            }
        
        elif any(word in desc_lower for word in ['sale', 'sold', 'revenue', 'income']):
            revenue = next(
                (a for a in available_accounts if a['account_type'] == 'revenue'),
                {'name': 'Sales Revenue', 'code': '4000', 'account_type': 'revenue'}
            )
            return {
                'entries': [
                    {'account': cash['name'], 'code': cash['code'], 'type': 'debit', 'amount': amount},
                    {'account': revenue['name'], 'code': revenue['code'], 'type': 'credit', 'amount': amount}
                ],
                'confidence': 0.60,
                'reasoning': 'Revenue transaction (fallback rule)',
                'source': 'fallback'
            }
        
        else:
            expense = next(
                (a for a in available_accounts if a['account_type'] == 'expense'),
                {'name': 'Operating Expense', 'code': '5000', 'account_type': 'expense'}
            )
            return {
                'entries': [
                    {'account': expense['name'], 'code': expense['code'], 'type': 'debit', 'amount': amount},
                    {'account': cash['name'], 'code': cash['code'], 'type': 'credit', 'amount': amount}
                ],
                'confidence': 0.50,
                'reasoning': 'Unknown type - assumed expense (REQUIRES REVIEW)',
                'source': 'fallback'
            }
