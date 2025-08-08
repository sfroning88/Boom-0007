def extract_customers(file, exte):
    print("##############################_EXTRC_BEGIN_##############################")

    # Generic dictionary to store customers
    extracted = {}

    # Convert file into pandas dataframe
    import pandas as pd
    if exte == 'csv':
        df = pd.read_csv(file)
    elif exte == 'xlsx' or exte == 'xls':
        df = pd.read_excel(file)
    else:
        print("##############################_EXTRC_END_##############################")
        return {}

    # Extract customer
    customer_counter = 0

    for i in range(len(df)):
        row = df.iloc[i]
        
        current_customer = {
            'Customer': str(row.iloc[2]) if pd.notna(row.iloc[2]) else None,
            'Bill To': str(row.iloc[4]) if pd.notna(row.iloc[4]) else None,
            'Primary Contact': str(row.iloc[6]) if pd.notna(row.iloc[6]) else None,
            'Main Phone': str(row.iloc[8]) if pd.notna(row.iloc[8]) else None,
            'Balance Total': round(float(row.iloc[12]), 2) if pd.notna(row.iloc[12]) else 0.0
        }

        extracted[customer_counter] = current_customer
        customer_counter += 1

    first_customer_key = list(extracted.keys())[0]
    first_customer = extracted[first_customer_key]
    print(f"CHECKPOINT: First key accesses {first_customer['Customer']}")

    print("##############################_EXTRC_END_##############################")
    return extracted
