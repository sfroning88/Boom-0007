def is_first_row(row):
    import pandas as pd
    if pd.notna(row.iloc[1]) and str(row.iloc[1]).strip() != "":
        return True
    return False

def is_last_row(row, next_row=None):
    import pandas as pd
    if next_row is None:
        return True  # Last row in dataset
    if pd.notna(next_row.iloc[1]) and str(next_row.iloc[1]).strip() != "":
        return True  # Next row starts a new transaction
    return False

def extract_journals(file, exte):
    print("##############################_EXTRJ_BEGIN_##############################")

    # Generic dictionary to store transactions
    extracted = {}

    # Convert file into pandas dataframe
    import pandas as pd
    if exte == 'csv':
        df = pd.read_csv(file)
    elif exte == 'xlsx' or exte == 'xls':
        df = pd.read_excel(file)
    else:
        print("##############################_EXTRJ_END_##############################")
        return {}
    
    num_rows, num_cols = df.shape

    # Extract transactions
    transaction_counter = 0
    current_transaction_header = None
    
    for i in range(len(df)):
        row = df.iloc[i]
        next_row = df.iloc[i + 1] if i + 1 < len(df) else None
        
        # Check if this is the first row of a new transaction
        if is_first_row(row):
            # Start new transaction header
            from support.stripping import strip_timestamp
            current_transaction_header = {
                'Trans #': str(int(row.iloc[1])).strip() if pd.notna(row.iloc[1]) else None,
                'Type': str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else None,
                'Date': strip_timestamp(str(row.iloc[5])) if pd.notna(row.iloc[5]) else "2025-01-01",
                'Num': str(row.iloc[7]).strip() if pd.notna(row.iloc[7]) else None,
                'Name': str(str(row.iloc[9])) if pd.notna(row.iloc[9]) else "UNDEFINED NAME",
                'Memo': str(row.iloc[11]).strip() if pd.notna(row.iloc[11]) else None,
                'Bill Customer': None,
                'Bill Customer Id': None,
                'Id': None,
                'Exp Id': None
            }
        
        # Process line items for current transaction (skip first row, only process rows 2 onwards)
        if current_transaction_header is not None and not is_first_row(row):
            # Check if this row has account information (not a total/summary row)
            account_name = str(row.iloc[13]).strip() if pd.notna(row.iloc[13]) else ""
            
            # Only process line items if there's an account name and type is valid
            if account_name and account_name != "" and current_transaction_header['Type'] in ["Bill", "Invoice", "Check"]:
                # Calculate amount as max of Debit/Credit
                debit_value = 0.0
                credit_value = 0.0
                
                if pd.notna(row.iloc[15]) and str(row.iloc[15]).strip() != "":
                    debit_value = float(row.iloc[15])
                
                if pd.notna(row.iloc[17]) and str(row.iloc[17]).strip() != "":
                    credit_value = float(row.iloc[17])
                
                amount = max(debit_value, credit_value)

                if pd.notna(row.iloc[9]) and str(row.iloc[9]).strip() != "":
                    bill_customer_name = str(row.iloc[9]) if str(row.iloc[9]) != current_transaction_header['Name'] else None

                if pd.notna(row.iloc[11]) and str(row.iloc[11]).strip() != "":
                    updated_memo = str(row.iloc[11]) if current_transaction_header['Memo'] is None else current_transaction_header['Memo']
                
                # Create transaction object for this line item
                transaction = {
                    'Trans #': current_transaction_header['Trans #'],
                    'Type': current_transaction_header['Type'],
                    'Date': current_transaction_header['Date'],
                    'Num': current_transaction_header['Num'],
                    'Name': current_transaction_header['Name'],
                    'Memo': updated_memo,
                    'Account': account_name,
                    'Amount': round(amount, 2),
                    'Bill Customer': bill_customer_name,
                    'Bill Customer Id': None,
                    'Id': None,
                    'Exp Id': None
                }
                
                extracted[transaction_counter] = transaction
                transaction_counter += 1
        
        # Check if this is the last row of the current transaction
        if is_last_row(row, next_row):
            current_transaction_header = None
    
    first_transaction = extracted[0] if extracted else None
    if first_transaction is None:
        print(f"WARNING: No transactions were found from the journal file or data validation error")
        return None
    
    print(f"CHECKPOINT: First key accesses {first_transaction['Type']} for {first_transaction['Name']}")
    print("##############################_EXTRJ_END_##############################")
    return extracted
