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
    # Generic dictionary to store transactions
    extracted = {}

    # Convert file into pandas dataframe
    import pandas as pd
    if exte == 'csv':
        df = pd.read_csv(file)
    elif exte == 'xlsx' or exte == 'xls':
        df = pd.read_excel(file)
    else:
        return {}
    
    num_rows, num_cols = df.shape

    print(f"\n{num_rows} Rows, {num_cols} Cols were ingested\n")

    # Extract transactions
    transaction_counter = 0
    current_transaction = None
    
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
                    'Trans #': str(row.iloc[1]) if pd.notna(row.iloc[1]) else None,
                    'Type': str(row.iloc[3]) if pd.notna(row.iloc[3]) else None,
                    'Date': strip_timestamp(str(row.iloc[5])) if pd.notna(row.iloc[5]) else None,
                    'Num': str(row.iloc[7]) if pd.notna(row.iloc[7]) else None,
                    'Name': [],
                    'Memo': [],
                    'Account': [],
                    'Debit': [],
                    'Credit': []
                }

            except Exception as e:
                print(e)
        
        # Add data to current transaction
        if current_transaction is not None:
            try:
                # Add Name (column J, index 9)
                if pd.notna(row.iloc[9]) and str(row.iloc[9]).strip() != "":
                    current_transaction['Name'].append(str(row.iloc[9]))
            
                # Add Memo (column L, index 11)
                if pd.notna(row.iloc[11]) and str(row.iloc[11]).strip() != "":
                    current_transaction['Memo'].append(str(row.iloc[11]))
            
                # Add Account (column N, index 13)
                if pd.notna(row.iloc[13]) and str(row.iloc[13]).strip() != "":
                    current_transaction['Account'].append(str(row.iloc[13]))
            

                # Add Debit (column P, index 15) - use 0 for empty cells
                if pd.notna(row.iloc[15]) and str(row.iloc[15]).strip() != "":
                    # Convert numpy.float64 to regular float and format to 2 decimal places
                    debit_value = float(row.iloc[15])
                    current_transaction['Debit'].append(round(debit_value, 2))
                else:
                    current_transaction['Debit'].append(0.0)
            
                # Add Credit (column R, index 17) - use 0 for empty cells
                if pd.notna(row.iloc[17]) and str(row.iloc[17]).strip() != "":
                    # Convert numpy.float64 to regular float and format to 2 decimal places
                    credit_value = float(row.iloc[17])
                    current_transaction['Credit'].append(round(credit_value, 2))
                else:
                    current_transaction['Credit'].append(0.0)
        
            except Exception as e:
                print(e)
        
        # Check if this is the last row of the current transaction
        if is_last_row(row, next_row):
            # Remove the final balancing row (last row) from Debit and Credit arrays
            if current_transaction is not None and len(current_transaction['Debit']) > 0:
                current_transaction['Debit'] = current_transaction['Debit'][:-1]
            if current_transaction is not None and len(current_transaction['Credit']) > 0:
                current_transaction['Credit'] = current_transaction['Credit'][:-1]
            
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
    
    return extracted
