def post_invoices(files):
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
        print("Missing journal file. Please upload file first.")
        return False

    journal_file = files[journal_file_key]
    journal_extraction = journal_file['df']

    # Remove any non invoice transactions
    import re
    from support.linetypes import invoice_patterns
    invoice_extraction = journal_extraction.copy()
    for key in list(invoice_extraction.keys()):
        transaction_type = invoice_extraction[key]['Type']
        is_invoice = any(re.search(pattern, transaction_type, re.IGNORECASE) for pattern in invoice_patterns)
        if not is_invoice:
            invoice_extraction.pop(key)

    print(f"Found {len(list(invoice_extraction.keys()))} invoices to post.")

    # Clean customer names to best match
    from api.customers import clean_customers
    invoice_extraction = clean_customers(invoice_extraction)

    # Concurrently post all invoices
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        list(tqdm(executor.map(invoice_threadsafe, list(invoice_extraction.values())), total=len(list(invoice_extraction.keys()))))
    
    print("##############################_POSTI_END_##############################")
    return True

def invoice_threadsafe(one_invoice):
    single_invoice(one_invoice)

def single_invoice(one_invoice):
    import os, requests
    from api.customers import get_customers
        
    # Get OAuth tokens from environment or stored session
    access_token = os.environ.get('QBO_ACCESS_TOKEN')
    realm_id = os.environ.get('QBO_REALM_ID')
        
    if not access_token or not realm_id:
        print("Missing OAuth tokens. Please complete OAuth flow first.")
        return False
            
    # Extract invoice data
    invoice_date = one_invoice['Date']
    invoice_number = one_invoice['Num']
    memo = one_invoice['Memo']
    amount = one_invoice['Debit'][0]
        
    # Create invoice object according to QBO API specification
    invoice = {
        "CustomerRef": {
            "value": one_invoice['Id']
        },
        "Line": [{
            "DetailType": "DescriptionOnly",
            "Amount": amount,
            "Description": memo if memo else "Invoice line item"
        }]
    }
        
    # Add optional fields if available
    if invoice_date:
        invoice["TxnDate"] = invoice_date
        
    if invoice_number:
        invoice["DocNumber"] = invoice_number
        
    if memo:
        invoice["PrivateNote"] = memo

    # QBO API endpoint for creating invoices
    base_url = 'https://sandbox-quickbooks.api.intuit.com'
    url = f'{base_url}/v3/company/{realm_id}/invoice?minorversion=75'
        
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
        
    response = requests.post(url, json=invoice, headers=headers)
        
    if response.status_code >= 300:
        print(f"Failed to create invoice for {one_invoice['Name']} because {response.message}")
        return False
        
    print(f"Posting invoice for {one_invoice['Name']}, Amount: ${amount}")

    return True
