import sys
import os

# Ensure app modules are importable
sys.path.insert(0, os.getcwd())

from app.domain.banking.csb43 import CSB43Parser

def create_sample_n43():
    # Construct a valid N43 mock content (ISO-8859-1 / Latin-1)
    # 11: Header
    # 22: Transaction
    # 33: Footer
    
    # 11: Bank 0049, Office 1234, Account 1234567890, Dates 250101-250131, Start Bal +1000.00 EUR
    line_11 = "11004912341234567890250101250131200000001000009782Sample Account             "
    
    # 22: Date 250102, Value 250102, Concept 01, Own 000, Debit (1), 50.00, Doc 123 (10 chars), Ref "Payment Invoice"
    # Amount: 00000000005000 (14 chars) -> 50.00
    # Doc: 0000000123 (10 chars)
    line_22_1 = "2200491234250102250102010001000000000050000000000123Payment Invoice 001                      "
    
    # 22: Date 250105, Value 250105, Concept 02, Own 000, Credit (2), 200.00, Doc 124 (10 chars), Ref "Client Transfer"
    # Amount: 00000000020000 (14 chars) -> 200.00
    line_22_2 = "2200491234250105250105020002000000000200000000000124Client Transfer ABC                      "
    
    # 33: Summary (Start + Credits - Debits) = 1000 - 50 + 200 = 1150.00
    line_33 = "330049123412345678900001000000000500000001000000002000020000000115000978"
    
    content = f"{line_11}\n{line_22_1}\n{line_22_2}\n{line_33}"
    return content.encode('latin-1')

def verify_parser():
    print("[INFO] Creating Sample CSB43 file...")
    content = create_sample_n43()
    
    print("[INFO] Parsing...")
    parser = CSB43Parser()
    try:
        statements = parser.parse("sample.n43", content)
    except Exception as e:
        print(f"[ERROR] Parsing failed: {e}")
        return

    if not statements:
        print("[ERROR] No statements parsed")
        return

    stmt = statements[0]
    print(f"[SUCCESS] Statement parsed for account: {stmt.account_id}")
    print(f"  - Initial Balance Line: (implied)")
    
    print(f"  - Transactions Found: {len(stmt.lines)}")
    for line in stmt.lines:
        print(f"    * {line.date} | {line.amount} | {line.concept}")
        
    # Check expected values
    if len(stmt.lines) != 2:
        print("[FAILURE] Expected 2 lines")
        return
        
    line1 = stmt.lines[0]
    if line1.amount != -50.00:
        print(f"[FAILURE] Line 1 amount mismatch: {line1.amount} != -50.00")
        return

    line2 = stmt.lines[1]
    if line2.amount != 200.00:
        print(f"[FAILURE] Line 2 amount mismatch: {line2.amount} != 200.00")
        return

    print("\n[VERIFIED] CSB43 Parser works correctly!")

if __name__ == "__main__":
    verify_parser()
