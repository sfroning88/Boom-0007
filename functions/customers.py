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
    
    num_rows, num_cols = df.shape

    print(f"{num_rows} Rows, {num_cols} Cols were ingested")

    # Extract customer
    customer_counter = 0

    from functions.stripping import strip_nonabc
    for i in range(len(df)):
        row = df.iloc[i]
        
        try:
            current_customer = {
                'Customer': strip_nonabc(row.iloc[2]) if pd.notna(row.iloc[2]) else None,
                'Bill To': str(row.iloc[4]) if pd.notna(row.iloc[4]) else None,
                'Primary Contact': str(row.iloc[6]) if pd.notna(row.iloc[6]) else None,
                'Main Phone': str(row.iloc[8]) if pd.notna(row.iloc[8]) else None,
                'Fax': str(row.iloc[10]) if pd.notna(row.iloc[10]) else None,
                'Balance Total': round(float(row.iloc[12]), 2) if pd.notna(row.iloc[12]) else None
            }

            extracted[customer_counter] = current_customer
            customer_counter += 1

        except Exception as e:
            print(e)

    first_customer_key = list(extracted.keys())[0]
    first_customer = extracted[first_customer_key]
    print(f"Customer Key: {first_customer_key}")
    print(f"Customer Structure:")
    for key, value in first_customer.items():
        print(f"  {key}: {value}")

    print("##############################_EXTRC_END_##############################")
    return extracted
