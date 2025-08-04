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

    print(f"{num_rows} Rows, {num_cols} Cols were ingested")

    # Extract transactions
    transaction_counter = 0
    current_transaction = None
    
    from functions.stripping import strip_nonabc
    for i in range(len(df)):
        row = df.iloc[i]
        next_row = df.iloc[i + 1] if i + 1 < len(df) else None
        
        # Check if this is the first row of a new transaction
        if is_first_row(row):
            # If we have a current transaction, save it
            if current_transaction is not None:
                extracted[transaction_counter] = current_transaction
                transaction_counter += 1
            
            # Start new transaction
            from functions.extension import strip_timestamp
            try:
                current_transaction = {
                    'Trans #': str(int(row.iloc[1])).strip() if pd.notna(row.iloc[1]) else None,
                    'Type': str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else None,
                    'Date': strip_timestamp(str(row.iloc[5])) if pd.notna(row.iloc[5]) else None,
                    'Num': str(row.iloc[7]).strip() if pd.notna(row.iloc[7]) else None,
                    'Name': strip_nonabc(str(row.iloc[9])) if pd.notna(row.iloc[9]) else None,
                    'Memo': str(row.iloc[11]).strip() if pd.notna(row.iloc[11]) else None,
                    'Account': str(row.iloc[13]).strip() if pd.notna(row.iloc[13]) else None,
                    'Debit': 0.0,
                    'Credit': 0.0,
                    'Id': None
                }

            except Exception as e:
                print(e)
        
        # Update current transaction with sum row values
        if current_transaction is not None:
            # Update Debit (column P, index 15) - use 0 for empty cells
            if pd.notna(row.iloc[15]) and str(row.iloc[15]).strip() != "":
                # Convert numpy.float64 to regular float and format to 2 decimal places
                debit_value = float(row.iloc[15])
                current_transaction['Debit'] = round(debit_value, 2)
            
            # Update Credit (column R, index 17) - use 0 for empty cells
            if pd.notna(row.iloc[17]) and str(row.iloc[17]).strip() != "":
                # Convert numpy.float64 to regular float and format to 2 decimal places
                credit_value = float(row.iloc[17])
                current_transaction['Credit'] = round(credit_value, 2)
        
        # Check if this is the last row of the current transaction
        if is_last_row(row, next_row):
            # Save the current transaction
            if current_transaction is not None:
                extracted[transaction_counter] = current_transaction
                transaction_counter += 1
                current_transaction = None
    
    # Handle the last transaction if it wasn't saved
    if current_transaction is not None:
        extracted[transaction_counter] = current_transaction
    
    first_transaction_key = list(extracted.keys())[0]
    first_transaction = extracted[first_transaction_key]
    print(f"Transaction Key: {first_transaction_key}")
    print(f"Transaction Structure:")
    for key, value in first_transaction.items():
        print(f"  {key}: {value}")

    print("##############################_EXTRJ_END_##############################")
    return extracted
