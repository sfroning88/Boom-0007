def extract_accounts(file, exte):
    print("##############################_EXTRA_BEGIN_##############################")

    # Generic dictionary to store accounts
    extracted = {}

    # Convert file into pandas dataframe
    import pandas as pd
    if exte == 'csv':
        df = pd.read_csv(file)
    elif exte == 'xlsx' or exte == 'xls':
        df = pd.read_excel(file)
    else:
        print("##############################_EXTRA_END_##############################")
        return {}

    # Extract vendors
    account_counter = 0

    from support.stripping import strip_nonabc
    for i in range(len(df)):
        row = df.iloc[i]
        
        current_account = {
            'Old': strip_nonabc(row.iloc[0]) if pd.notna(row.iloc[0]) else None,
            'Num': int(row.iloc[1]) if pd.notna(row.iloc[1]) else None,
            'Account': str(row.iloc[2]) if pd.notna(row.iloc[2]) else None,
        }

        # BUGFIX(prod): Check values, not literal keys.
        current_account['Full'] = str(current_account['Num']) + " " + current_account['Account'] if 'Num' is not None and 'Account' is not None else None

        # TODO(prod): Switch to header-based parsing; validate schema and types with clear error messages.

        extracted[account_counter] = current_account
        account_counter += 1

    first_account_key = list(extracted.keys())[0]
    first_account = extracted[first_account_key]
    print(f"CHECKPOINT: {first_account_key} accesses {first_account['Full']}")

    print("##############################_EXTRA_END_##############################")
    return extracted
