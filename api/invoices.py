def post_invoices(files, begin_date="2025-01-01", end_date="2025-01-31"):
    print("##############################_POSTI_BEGIN_##############################")

    import concurrent.futures
    from tqdm import tqdm

    # Determine journal file
    journal_file_key = None
    for single_file_key in files.keys():
        if files[single_file_key]['type'] == "journal" and files[single_file_key]['uploaded'] == False:
            journal_file_key = single_file_key
            break

    if journal_file_key is None:
        print("WARNING: Missing journal file, please upload file first")
        return False

    journal_file = files[journal_file_key]
    journal_extraction = journal_file['df']

    # Remove any non invoice transactions or older transactions
    invoice_extraction = journal_extraction.copy()
    for key in list(invoice_extraction.keys()):
        transaction_type = invoice_extraction[key]['Type']
        transaction_date = invoice_extraction[key]['Date']
        transaction_amount = invoice_extraction[key]['Amount']

        if transaction_type.lower() not in ["invoice"]:
            invoice_extraction.pop(key)
            continue

        if transaction_date < begin_date or transaction_date > end_date:
            invoice_extraction.pop(key)
            continue

        if transaction_amount == 0.0:
            invoice_extraction.pop(key)
            continue

    print(f"CHECKPOINT: Found {len(list(invoice_extraction.keys()))} invoices to post from {begin_date} to {end_date}")

    # Post all new customers from invoices
    from api.resolve import resolve_customers
    invoice_extraction = resolve_customers(invoice_extraction)

    if invoice_extraction is None:
        return False

    # Assign ids pulled from QBO
    from api.resolve import resolve_cust_ids
    invoice_extraction = resolve_cust_ids(invoice_extraction)
    
    # Concurrently post all invoices
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        list(tqdm(executor.map(invoice_threadsafe, list(invoice_extraction.values())), total=len(list(invoice_extraction.keys()))))
    
    print("##############################_POSTI_END_##############################")
    return True

def invoice_threadsafe(one_invoice):
    single_invoice(one_invoice)

def single_invoice(one_invoice):
    import os, requests, time, random

    # Respectful delay to the server
    time.sleep(random.uniform(0.8, 1.2))
        
    # Get OAuth tokens from environment or stored session
    access_token = os.environ.get('QBO_ACCESS_TOKEN')
    realm_id = os.environ.get('QBO_REALM_ID')
        
    if not access_token or not realm_id:
        print("WARNING: Missing OAuth tokens. Please complete OAuth flow first.")
        return False

    if one_invoice['Id'] is None:
        print(f"WARNING: Could not post invoice for {one_invoice['Name']}, Amount: ${one_invoice['Amount']}")
        return False
            
    # Extract invoice data
    invoice_name = one_invoice['Name']
    invoice_id = one_invoice['Id']
    invoice_date = one_invoice['Date']
    invoice_number = one_invoice['Num']
    invoice_memo = one_invoice['Memo']
    invoice_amount = one_invoice['Amount']

    # net 30 terms default
    from functions.stripping import days_timestamp
    due_date = days_timestamp(invoice_date, 30)
        
    # Create invoice object according to QBO API specification
    invoice = {
        "CustomerRef": {
            "value": invoice_id
        },
        "Line": [{
            "DetailType": "SalesItemLineDetail",
            "SalesItemLineDetail": {
                "ServiceDate": invoice_date
            },
            "Amount": invoice_amount,
            "Description": invoice_memo if invoice_memo else "Invoice line item"
        }],
        "TotalAmt": invoice_amount,
        "TxnDate": invoice_date,
        "DueDate": due_date if due_date else invoice_date,
        "DocNumber": invoice_number,
        "PrivateNote": invoice_memo if invoice_memo else "Uncategorized Income"
    }

    # QBO API endpoint for creating invoices
    from support.config import env_mode
    base_url = 'https://quickbooks.api.intuit.com' if env_mode == "production" else 'https://sandbox-quickbooks.api.intuit.com'
    url = f'{base_url}/v3/company/{realm_id}/invoice?minorversion=75'
        
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
        
    response = requests.post(url, json=invoice, headers=headers)
        
    if response.status_code >= 300:
        print(f"ERROR: Failed to create invoice for {invoice_name}, Amount: ${invoice_amount}")
        return False
        
    #print(f"INVOICE: Posting invoice for {invoice_name}, Amount: ${invoice_amount}")
    return True
