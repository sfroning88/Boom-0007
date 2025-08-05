def extract_vendors(file, exte):
    print("##############################_EXTRV_BEGIN_##############################")

    # Generic dictionary to store vendors
    extracted = {}

    # Convert file into pandas dataframe
    import pandas as pd
    if exte == 'csv':
        df = pd.read_csv(file)
    elif exte == 'xlsx' or exte == 'xls':
        df = pd.read_excel(file)
    else:
        print("##############################_EXTRV_END_##############################")
        return {}
    
    num_rows, num_cols = df.shape

    print(f"{num_rows} Rows, {num_cols} Cols were ingested")

    # Extract vendors
    vendor_counter = 0

    from functions.stripping import strip_nonabc
    for i in range(len(df)):
        row = df.iloc[i]
        
        current_vendor = {
            'Vendor': str(row.iloc[2]) if pd.notna(row.iloc[2]) else None,
            'Account #': str(row.iloc[4]) if pd.notna(row.iloc[4]) else None,
            'Bill From': str(row.iloc[6]) if pd.notna(row.iloc[6]) else None,
            'Primary Contact': str(row.iloc[8]) if pd.notna(row.iloc[8]) else None,
            'Main Phone': str(row.iloc[10]) if pd.notna(row.iloc[10]) else None,
            'Balance Total': round(float(row.iloc[14]), 2) if pd.notna(row.iloc[14]) else None
        }

        extracted[vendor_counter] = current_vendor
        vendor_counter += 1

    first_vendor_key = list(extracted.keys())[0]
    first_vendor = extracted[first_vendor_key]
    print(f"CHECKPOINT: {first_vendor_key} accesses {first_vendor['Vendor']}")

    print("##############################_EXTRV_END_##############################")
    return extracted
