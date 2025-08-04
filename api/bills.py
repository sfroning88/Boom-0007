def post_bills(files):
    print("##############################_POSTB_BEGIN_##############################")

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

    # Remove any non bill transactions
    import re
    from support.linetypes import bill_patterns
    bill_extraction = journal_extraction.copy()
    for key in list(bill_extraction.keys()):
        transaction_type = bill_extraction[key]['Type']
        is_bill = any(re.search(pattern, transaction_type, re.IGNORECASE) for pattern in bill_patterns)
        if not is_bill:
            bill_extraction.pop(key)

    print(f"Found {len(list(bill_extraction.keys()))} bills to post.")

    # Clean vendor names to best match
    from api.resolve import resolve_vendors
    bill_extraction = resolve_vendors(bill_extraction)

    # Assign ids pulled from QBO
    from api.resolve import resolve_vend_ids
    try:
        bill_extraction = resolve_vend_ids(bill_extraction)
    except Exception as e:
        print(e)

    # Concurrently post all bills
    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
        list(tqdm(executor.map(bill_threadsafe, list(bill_extraction.values())), total=len(list(bill_extraction.keys()))))
    
    print("##############################_POSTB_END_##############################")
    return True

def bill_threadsafe(one_bill):
    try:
        single_bill(one_bill)
    except Exception as e:
        print(e)

def single_bill(one_bill):
    import os, requests
        
    # Get OAuth tokens from environment or stored session
    access_token = os.environ.get('QBO_ACCESS_TOKEN')
    realm_id = os.environ.get('QBO_REALM_ID')
        
    if not access_token or not realm_id:
        print("Missing OAuth tokens. Please complete OAuth flow first.")
        return False
            
    # Extract bill data
    bill_date = one_bill['Date']
    bill_number = one_bill['Num']
    memo = one_bill['Memo']
    amount = one_bill['Credit']
        
    # Create bill object according to QBO API specification
    bill = {
        "VendorRef": {
            "value": one_bill['Id']
        },
        "Line": [{
            "DetailType": "AccountBasedExpenseLineDetail",
            "Amount": amount,
            "Id": "1", 
            "AccountBasedExpenseLineDetail": {
                "AccountRef": {
                "value": "1"
                }
            }
        }]
    }
        
    # Add optional fields if available
    if bill_date:
        bill["TxnDate"] = bill_date
        
    if bill_number:
        bill["DocNumber"] = bill_number
        
    if memo:
        bill["PrivateNote"] = memo

    # QBO API endpoint for creating bills
    base_url = 'https://sandbox-quickbooks.api.intuit.com'
    url = f'{base_url}/v3/company/{realm_id}/bill?minorversion=75'
        
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
        
    response = requests.post(url, json=bill, headers=headers)
        
    if response.status_code >= 300:
        print(f"Failed to create bill for {one_bill['Name']} because {response.text}")
        return False
        
    print(f"Posting bill for {one_bill['Name']}, Amount: ${amount}")
    return True
